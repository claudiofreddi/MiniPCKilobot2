#Env
from Lib_Processes import *
from Lib_Commands_Interfaces import * 

import math
import matplotlib.pyplot as plt

import numpy as np
from multiprocessing import Manager
import time

from Robot_lidar_base import lidarfunc
from Robot_Keyboard import RobotKeyboard_Run
from Robot_UI import RobotUI_Run
from Robot_Arduino_B_ReadSensors import ArduinoReadSensors_Run
from Robot_Arduino_A_DoActions import Arduino_A_DoActions_Run



import serial
   

class RobotLidar_Obj(ProcessSuperClass,threading.Thread):
  
    RangingIdleInSeconds = 1
    SliceHalfSize = 10
    SliceFullSize = SliceHalfSize * 2
    NumOfAnglesInterval = 360/SliceFullSize #18    
    GraphOn = False
    
    
    def __init__(self,processName):
        threading.Thread.__init__(self)
        super().__init__(processName)
        self.EnableConsoleLogLevel = ProcessSuperClassLogLevel.Always
        
   
    def GetDistanceAngle(self,Angle,dataAN, dataD):
        Anglefrom = Angle - self.SliceHalfSize
        Angleto = Angle + self.SliceHalfSize
        if (Anglefrom<0):
            #0
            #-10  +10
            #350  10
            return self.GetDistance(360-Anglefrom,Angleto,dataAN, dataD)
        elif (Angleto>360):
            #360
            #350  370
            #350  10 
            return self.GetDistance(Anglefrom,Angleto-360,dataAN, dataD)
        else:
            #180
            #170  190
            return self.GetDistance(Anglefrom, Angleto,dataAN, dataD)
        
    def GetDistance(self, Anglefrom, Angleto,dataAN, dataD):
        if (Anglefrom > Angleto):
            #350  10 
            boolean_array = np.logical_or(dataAN >= Anglefrom, dataAN <= Angleto)
        else:
            #170  190
            boolean_array = np.logical_and(dataAN >= Anglefrom, dataAN <= Angleto)
        
        in_range_indices = np.where(boolean_array)[0]

        Y = [dataAN[index] for index in in_range_indices]
        super().LogConsole("Y:")
        super().LogConsole(Y)  
        X = [dataD[index] for index in in_range_indices]
        super().LogConsole("X:")
        super().LogConsole(X)
        if (len(X) == 0):
            return 0,0,0
        
        if (False):
            if (Anglefrom<=10 or Anglefrom>=350):
                #boolean_array = np.logical(dataD > 15)
                in_range_indices = np.where(np.array(dataD) < 15)[0]
                Z = [dataD[index] for index in in_range_indices]
                for index in in_range_indices:
                    dataD[index]= 200
                print(Z)
                print(len(X))
        
        #return 0 if len(X) == 0 else self.find_average(X), 0 if len(X) == 0 else min(X), 0 if len(X) == 0 else max(X)
        return self.find_average(X), min(X),  max(X)
        
        


    def find_average(self,arr): 
        total = sum(arr) 
        return total / len(arr) 

    def Run(self,SharedMem:SharedObjs):
        super().Run_Pre(SharedMem)
        self.GraphOn = MySharedObjs.GraphOn
        #Params
        self.MaxScale = 200
        self.TraceAllLines = False
        self.TraceSafetyLine = True
        last_min_front = 0

    
        # Make a figure for the LiDAR polar graph
        if (self.GraphOn):
            self.fig = plt.figure(figsize=(8, 8))
            self.ax = self.fig.add_subplot(111, projection='polar')
            self.ax.set_title('Scanning environment..', fontsize=18)
        
        theta = np.linspace(0 ,2*np.pi,self.SliceFullSize) # [0, 30, 60 , 90, 120, 150, 180... 360]

        #super().LogConsole("theta:")
        #super().LogConsole(theta)

        theta360 =  np.array(theta) * 360/(2*np.pi )
        #super().LogConsole("theta360:")
        #super().LogConsole(theta360)

        Myser = serial.Serial(port="COM10",baudrate=230400,timeout=5.0,bytesize=8,parity='N',stopbits=1)
        
        Continue = True
        while Continue:
            #Insert here loop command
            #super().LogConsole("Ranging...",ProcessSuperClassLogLevel.Control)
            lidar_data = lidarfunc(10,Myser)
            
            # metto zero del grafico in alto: ruoto di +90°
            lidar_data.angles = np.array(lidar_data.angles) + np.pi/2
            idx = np.where(lidar_data.angles> 2* np.pi)
            lidar_data.angles[idx] = np.array(lidar_data.angles[idx]) - 2* np.pi
            
            #idx = np.where(np.array(lidar_data.distances) < 15)
            #np.array(lidar_data.distances)[idx] = 200

           
            if (self.GraphOn):
                # Disegno confini
                if ('line' in locals()):
                    line.remove()
                line = self.ax.scatter(lidar_data.angles, lidar_data.distances, c="blue", s=5)
                #ax.set_theta_offset(0)
                self.ax.set_theta_offset(math.pi / 2)  # zero del grafico in alto
                self.ax.set_theta_direction(-1)
                #Settore di visibilità
                self.ax.set_thetamin(0)
                self.ax.set_thetamax(360)
                self.ax.set_ylim(0,self.MaxScale)  #1 = 0.01 m

            
            # Array di appoggio 0-360° e distanze cm
            AN = np.array(lidar_data.angles) * 360/(2*np.pi )
            AD = lidar_data.distances

            #theta = np.array(angles) 
        
            radiusAv = []
            radiusMax = []
            radiusMin = []
            radiusSafe = []
            for i in theta360:
                av, mi, ma = (self.GetDistanceAngle(i,AN,AD))
                radiusAv.append(av)
                radiusMax.append(ma)
                radiusMin.append(mi)
            
            radiusSafe = radiusMin
          
            #idx = np.where( np.array(radiusMin) < 10 )[0] 
            #for i in idx:
            #    radiusMin[i] = 10
            
                        
            
            if (self.GraphOn):
                
                if (self.TraceAllLines):
                    super().LogConsole("radius:")
                    if ('lineav' in locals()):
                        lineav.remove()
                    lineav = self.ax.scatter(theta, radiusAv, c="yellow", s=5)
                    
                    if ('linemi' in locals()):
                        linemi.remove()
                    linemi = self.ax.scatter(theta, radiusMin, c="red", s=5)
                    
                    if ('linema' in locals()):
                        linema.remove()
                    linema = self.ax.scatter(theta, radiusMax, c="green", s=5)

                if (self.TraceSafetyLine):
                    if ('linesaf' in locals()):
                        linesaf.remove()
                    linesaf, = self.ax.plot(theta, radiusSafe, c="green")
                
                
            #Vedo quanto sono libero davatni
            LookAngle = 20
            OKMinDistance = 20
            boolean_array = np.logical_or(theta360 <= LookAngle,theta360 >= 360-LookAngle)
            idx = np.where(boolean_array)[0] 
            min_front = 200
            for i in idx:
                if (min_front >radiusSafe[i]):
                    min_front = radiusSafe[i]
            if (min_front <= OKMinDistance):
                min_front = 200

            if (min_front != last_min_front ):
                
                self.SharedMem.LidarInfo.FrontDistance = min_front
                self.SharedMem.LidarInfo.LastUpdate = time.time()
                
                print("min_front: " + str(min_front))
                last_min_front = min_front
                
                
                
            

            if (self.GraphOn):
                plt.pause(self.RangingIdleInSeconds)
            else:
                time.sleep(self.RangingIdleInSeconds)
            
            #End loop commands
            #time.sleep(1)
            Continue = super().Run_CanContinueRunnig()
            
        super().Run_Kill()
        
        
def RobotLidar_Run(SharedMem, _GraphOn = True):
    MyRobotLidar_Obj = RobotLidar_Obj(ProcessList.Robot_Lidar)
    MyRobotLidar_Obj.GraphOn = _GraphOn
    MyRobotLidar_Obj.Run(SharedMem)

import logging 

if (__name__== "__main__"):
    
    useThreads = True
    
    MySharedObjs = SharedObjs()
    
    if not (useThreads):
        if (False):
            RobotLidar_Run(MySharedObjs)     
        else:        
            run_io_tasks_in_parallel([
                RobotLidar_Run
                ,ArduinoReadSensors_Run
                ,Arduino_A_DoActions_Run
                ,RobotKeyboard_Run
                ,RobotUI_Run
                
            ], MySharedObjs)    
    else: 
        
        
        
        print("Start Threading...")   
        
        #RobotLidar_Run(MySharedObjs)
        
        threads = list()
        x = threading.Thread(target=RobotLidar_Run, args=(MySharedObjs,False,))
        threads.append(x)
        x.start()        
        
        x = threading.Thread(target=RobotUI_Run, args=(MySharedObjs,))
        threads.append(x)
        x.start()        

        x = threading.Thread(target=RobotKeyboard_Run, args=(MySharedObjs,))
        threads.append(x)
        x.start()  

        
        x = threading.Thread(target=ArduinoReadSensors_Run, args=(MySharedObjs,))
        threads.append(x)
        x.start()  
        
        x = threading.Thread(target=Arduino_A_DoActions_Run, args=(MySharedObjs,))
        threads.append(x)
        x.start()  
        
        print("End Threading...", len(threads))
        
        for index, thread in enumerate(threads):
            logging.info("Main    : before joining thread %d.", index)
            thread.join()
            logging.info("Main    : thread %d done", index)    
        
        print("End Joining...", len(threads))
            