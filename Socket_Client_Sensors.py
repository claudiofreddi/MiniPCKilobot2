import time
from Socket_Client import *


class SocketClientSensor(Robot_Socket_Client_Service):
    
    CompassVal = 0
    Interval = 10
    
    
    def __init__(self,ForceServerIP = '',ForcePort = ''):
        super().__init__(SocketServices.SENSORS,ForceServerIP,ForcePort)
        
       
        
    def OnClient_Receive(self, DeserializedMsgObj:any):
        super().OnClient_Receive(DeserializedMsgObj)
        
        
            
    def OnClient_WriteToServer(self):
        return None              
                
                
    def Run(self):
        # Starting Threads For Listening And Writing
        super().Run()
        
        while True:
            time.sleep(self.Interval)
            self.CompassVal = self.CompassVal + self.Interval
            if (self.CompassVal>=360):  
                self.CompassVal = 0
            
            MySensorMessage = SensorMessage(SensorsId.COMPASS,self.CompassVal)
                
            if (self.IsConnected == True):
                message = "Set_Sensor_Compass" + ":" + str(self.CompassVal)
                self.TraceLog(message)
                self.Client_Send(MySensorMessage)
            
            
        
if (__name__== "__main__"):
    
    MySocketClientSensor = SocketClientSensor()
    MySocketClientSensor.Run()