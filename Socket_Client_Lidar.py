import serial
import math
import matplotlib.pyplot as plt
import numpy as np
import threading
from Robot_lidar_base import lidarfunc
from Socket_Struct_Client_BaseClass import * 
from Socket_Utils_Timer import * 
from Robot_Envs import *
from Socket_Utils_Lidar_Algo import *
from datetime import datetime

class SocketClient_Lidar(Socket_Client_BaseClass,threading.Thread):

    MyAlgo = Socket_Utils_Lidar_Algorithm()
    
    def __init__(self, ServiceName = Socket_Services_List.LIDAR, ForceServerIP = '',ForcePort='',LogOptimized = False):
        super().__init__(ServiceName,ForceServerIP,ForcePort,LogOptimized)
        self.IsLidarConnected = False
        self.RangingIdleInSeconds = 2
        self.SliceHalfSize = 3
        self.SliceFullSize = self.SliceHalfSize * 2
        self.NumOfAnglesInterval = int(360/self.SliceFullSize) #18    
        self.GraphOn = True
        #Params
        self.MaxScale = 200
        self.TraceAllLines = False
        self.TraceSafetyLine = True
        self.last_min_front = 0
        
        #Used to wati endo of caclulation
        self.SemaphoreReadyToSend = False
        
        # Make a figure for the LiDAR polar graph
        if (self.GraphOn):
            self.fig = plt.figure(figsize=(4, 4))
            self.ax = self.fig.add_subplot(111, projection='polar')
            self.ax.set_title(str(datetime.now().time())[:8] + ' Scanning environment..', fontsize=10)
        
        self.theta = np.linspace(0 ,2*np.pi,self.NumOfAnglesInterval) # [0, 30, 60 , 90, 120, 150, 180... 360]

        self.LogConsole(self.ThisServiceName() + f"theta: {self.theta}",ConsoleLogLevel.Test)
        
        self.theta360 =  np.array(self.theta) * 360/(2*np.pi )
        self.LogConsole(self.ThisServiceName() + f"theta360: {self.theta360}",ConsoleLogLevel.Test)
        
        try:
            self.MyLidar = serial.Serial(port=LIDAR_COM_PORT,baudrate=LIDAR_BOAD_RATE,timeout=5.0,bytesize=8,parity='N',stopbits=1)
            self.IsLidarConnected = True
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in __init__() LIDAR COnnection  " + str(e),ConsoleLogLevel.Error)
            self.IsLidarConnected = False
        
    def OnClient_Connect(self):
        
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
    
    def On_ClientAfterLogin(self):
        self.RegisterTopics(Socket_Default_Message_Topics.INPUT_LIDAR)
        #self.SubscribeTopics(Socket_Default_Message_Topics.NONE)
        
                
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreadyManaged=False):
        # if (self.IsConnected):
        #     if (not IsMessageAlreadyManaged):
        #         if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
        #             ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
        #             if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD):
        #                 MySpecificCommand = ReceivedMessage.Message
        
        try:
            if (IsMessageAlreadyManaged == False):
                if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                    ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                            
                            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 
    
    def OnClient_Core_Task_Cycle(self):
        try:
            
            if (self.SemaphoreReadyToSend):
                self.LogConsole("Send LIdar info" ,ConsoleLogLevel.Test)
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.INPUT_LIDAR, 
                                                                        Message = "Lidare", Value = self.last_min_front)                
                    
                
                self.SendToServer(ObjToSend) 
                self.SemaphoreReadyToSend = False
                    
            if (self.IsQuitCalled):
                return self.OnClient_Core_Task_RETVAL_QUIT
        
            return self.OnClient_Core_Task_RETVAL_OK
         
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
        
        
    def MainExecution(self):
        try:
            
            while True:
                if (self.IsQuitCalled): break
                
                
                pParam, retval  = self.LocalListOfStatusParams.GetParam(self.ServiceName + StatusParamName.THIS_SERVICE_IS_IDLE)
                if (pParam.Value==StatusParamListOfValues.ON):
                    time.sleep(self.SLEEP_TIME)
                    continue
                
                if (not self.SemaphoreReadyToSend):
                
                    if (self.IsLidarConnected):
                        
                        lidar_data = lidarfunc(10,self.MyLidar)
                        
                        # metto zero del grafico in alto: ruoto di +90°
                        lidar_data.angles = np.array(lidar_data.angles) + np.pi/2
                        idx = np.where(lidar_data.angles> 2* np.pi)
                        lidar_data.angles[idx] = np.array(lidar_data.angles[idx]) - 2* np.pi
                        
                        #idx = np.where(np.array(lidar_data.distances) < 15)
                        #np.array(lidar_data.distances)[idx] = 200

                    
                        if (self.GraphOn):
                            self.ax.set_title(str(datetime.now().time())[:8] + ' Scanning environment..', fontsize=10)
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
                        for i in self.theta360:
                            av, mi, ma = (self.GetDistanceAngle(i,AN,AD))
                            radiusAv.append(av)
                            radiusMax.append(ma)
                            radiusMin.append(mi)
                        
                        radiusSafe = radiusMin
                        
                        #print(radiusSafe)
                        
                        BestNewAngleToFollow = self.MyAlgo.GetBestAngleToMove(radiusSafe)
                        #print("Best Angle To Follow: " + str(BestNewAngleToFollow))
                        BestNewAngleToFollowRad = (BestNewAngleToFollow/360)*2*np.pi
                        if ('line_Path' in locals()):
                            line_Path.remove()
                        line_Path, = self.ax.plot([BestNewAngleToFollowRad]*3,[0,50, 200],  c="red")
                        
                        if (self.GraphOn):
                            
                            if (self.TraceAllLines):
                                
                                if ('lineav' in locals()):
                                    lineav.remove()
                                lineav = self.ax.scatter(self.theta, radiusAv, c="yellow", s=5)
                                
                                if ('linemi' in locals()):
                                    linemi.remove()
                                linemi = self.ax.scatter(self.theta, radiusMin, c="red", s=5)
                                
                                if ('linema' in locals()):
                                    linema.remove()
                                linema = self.ax.scatter(self.theta, radiusMax, c="green", s=5)

                            if (self.TraceSafetyLine):
                                if ('linesaf' in locals()):
                                    linesaf.remove()
                                linesaf, = self.ax.plot(self.theta, radiusSafe, c="green")
                            
                            
                        #Vedo quanto sono libero davatni
                        LookAngle = 20
                        OKMinDistance = 20
                        boolean_array = np.logical_or(self.theta360 <= LookAngle,self.theta360 >= 360-LookAngle)
                        idx = np.where(boolean_array)[0] 
                        min_front = 200
                        for i in idx:
                            if (min_front >radiusSafe[i]):
                                min_front = radiusSafe[i]
                        if (min_front <= OKMinDistance):
                            min_front = 200

                        if (min_front != self.last_min_front ):
                            
                            if (self.IsConnected):
                                print("Best Angle To Follow: " + str(BestNewAngleToFollow))
                                print("min_front: " + str(min_front))
                                
                                # self.SharedMem.LidarInfo.FrontDistance = min_front
                                # self.SharedMem.LidarInfo.LastUpdate = time.time()
                                self.SemaphoreReadyToSend = True
                                
                           
                            self.last_min_front = min_front
                        
                        if (self.GraphOn):
                            plt.pause(self.RangingIdleInSeconds)
                        else:
                            time.sleep(self.RangingIdleInSeconds)
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + " Error in MainExecution()  " + str(e),ConsoleLogLevel.Error)
            
    
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
        
        #return 0 if len(X) == 0 else self.find_average(X), 0 if len(X) == 0 else min(X), 0 if len(X) == 0 else max(X)
        return self.find_average(X), min(X),  max(X)
         


    def find_average(self,arr): 
        total = sum(arr) 
        return total / len(arr) 


    def GetBestAngleToMove(self,Arr):
        Test = False
        numitems = len(Arr)
        FClass = [0] * numitems
        Weight = [0] * numitems
        Degrees = [0] * numitems
        TotalWeight = [0] * numitems
        
        Pos = 0
        Step = int(356/numitems)
        for i in range(0,len(Degrees)): 
            Degrees[i] = Pos
            Pos += Step
            FClass[i] = int(Arr[i]/100)*100
            Weight[i] = 0
        if (Test): print(numitems)    
        for i in range(0,numitems):
            index_1 = numitems-1 if (i-1<0) else i-1
            index_2 = numitems-2 if (i-2<0) else i-2
            index_1b = 0 if (i+1>numitems) else i
            index_2b = 1 if (i+2>numitems) else i+1
            if (Test): print(index_1,index_2, index_1b, index_2b)
            if (FClass[i] == FClass[index_1]): Weight[i] +=1
            if (FClass[i] == FClass[index_2]): Weight[i] +=2
            if (FClass[i] == FClass[index_1b]): Weight[i] +=1
            if (FClass[i] == FClass[index_2b]): Weight[i] +=2
        
        MaxIndex = -1
        LastMaxTotal = 0
        CountMaxVal = 0
        for i in range(0,numitems):    
            TotalWeight[i] = FClass[i] * Weight[i] 
            if (TotalWeight[i] >= LastMaxTotal): 
                MaxIndex = i
                
                if (TotalWeight[i] == LastMaxTotal): 
                    CountMaxVal += 1
                else:
                    CountMaxVal =1
                LastMaxTotal = TotalWeight[i]
                
        StepBack = int(CountMaxVal/2)
        if (MaxIndex - StepBack<0):
            MaxIndex = MaxIndex - StepBack  + numitems
        else:
            MaxIndex = MaxIndex - StepBack
            
        if (Test):
            print(Arr)    
            print(Degrees)
            print(FClass)
            print(Weight)
            print(TotalWeight)
            print(MaxIndex)
            print(LastMaxTotal)
            print(Degrees[MaxIndex])
        
        if (MaxIndex!=-1):
            return Degrees[MaxIndex],CountMaxVal    
        
        return -1
        

    def OpenWindow(self):
        self.MainExecution()
        
            
if (__name__== "__main__"):
    
    MySocketClient = SocketClient_Lidar()
    
    MySocketClient.Run_Threads()
    MySocketClient.OpenWindow()