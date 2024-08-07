import time
import random2
from ZZZ_Socket_Client import *

class SensorsId:
    COMPASS = "COMPASS"
    BATTERY = "BATTERY"      
    
class SocketClientSensor(Robot_Socket_Client_Service):
    
    CompassVal:SensorMessage2
    BatteryVal:SensorMessage
        
    
    def __init__(self,ForceServerIP = '',ForcePort = ''):
        super().__init__(SocketServices.SENSORS,ForceServerIP,ForcePort)
        self.CompassVal = SensorMessage2(SensorsId.COMPASS,0,"Orientamento bussola")
        self.BatteryVal = SensorMessage(SensorsId.BATTERY,0,"Carica Batteria")
        #self.CompassVal.SetParams(0,360,3)
        self.BatteryVal.SetParams(700,1024,30)
               
            
         
                
                
    def Run(self):
        # Starting Threads For Listening And Writing
        super().Run()
        lastRead = datetime.now()
        while True:
            if ((datetime.now() - lastRead).total_seconds() > self.CompassVal.UpdateFrequency_InSec):
                print("NeedUpdate")  
                lastRead = datetime.now()
                self.CompassVal.IntValue = random2.randint(0,360)
                ObjToSend = self.CompassVal
                self.SerializeObj_And_Send(self.client,ObjToSend)
            else:
                print("No Need Update") 
                
                
                   
            # if (self.CompassVal.NeedUpdate()):
            #     print("NeedUpdate")              
            #     self.TraceLog("Sending Compass")
            #     self.CompassVal.UpdateValue(random2.randint(0,360))
            #     ObjToSend = self.CompassVal
            #     # ObjToSend:SimpleMessage = SimpleMessage("Simple: " + str(self.CompassVal.IntValue))
            #     # ObjToSend.IntValue = self.CompassVal.IntValue
            #     self.SerializeObj_And_Send(self.client,ObjToSend)
            #     #self.Client_Send(self.client,ObjToSend)
            # else:
            #     print("No Need Update")              

            # if (self.BatteryVal.NeedUpdate()):
                
            #     self.TraceLog("Sending Battery")
            #     self.BatteryVal.UpdateValue(random.randint(800,900))
            #     self.Client_Send(self.BatteryVal)
            
            print("sleep")              
            time.sleep(2)
        
if (__name__== "__main__"):
    
    MySocketClientSensor = SocketClientSensor()
    MySocketClientSensor.SimulOn = False
    MySocketClientSensor.Run()