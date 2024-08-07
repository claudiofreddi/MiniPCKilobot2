from Socket_Client_JSON import * 

class Sensors_SubClass_Types:
    BATTERY = "BATTERY"
    COMPASS = "COMPASS"

class SocketClient_Sensors(Robot_Socket_Client_Service):
    
    
    
    def __init__(self, ServiceName = Socket_Services_Types.SENSORS, ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort)
        
    def OnClient_Connect(self):
        self.NumOfCycles = 0
        print("OnClient_Connect")
    
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,IsMessageAlreayManaged=False):
        #obj:SocketMessage_Type_STANDARD = ReceivedEnvelope.GetDecodedMessageObject()
        #print("OnClient_Receive: " + obj.Message + " [" + self.ServiceName + "]")
        pass
        
    def OnClient_Disconnect(self):
        print("OnClient_Disconnect")
        
    def OnClient_Quit(self):
        print("OnClient_Quit") 

    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
            
            time.sleep(3)
            
            message = 'Numero di Cicli attuali {}'.format(self.NumOfCycles)
            SubClass = Sensors_SubClass_Types.BATTERY
            SensorValue = self.NumOfCycles 
            
            
            ObjToSend:SocketMessage_Type_STANDARD = SocketMessage_Type_STANDARD(ClassType=SocketMessage_Type_STANDARD_Type.SENSOR, 
                                                                                SubClassType = SubClass, Message = message, Value = SensorValue)
            
            self.TraceLog(self.LogPrefix() + " " + SubClass  + " Sending Value: " + str(SensorValue))
            self.SendToServer(ObjToSend)  
            self.NumOfCycles = self.NumOfCycles + 1
        
        
    
            return self.OnClient_Core_Task_RETVAL_OK
            #self.OnClient_Core_Task_RETVAL_QUIT
            
        except Exception as e:
            self.TraceLog(self.LogPrefix() + "Error in OnClient_Core_Task_Cycle()  " + str(e))
            return self.OnClient_Core_Task_RETVAL_ERROR
        
        
if (__name__== "__main__"):
    
    MySocketClient_Sensors = SocketClient_Sensors(Socket_Services_Types.SENSORS)
    
    MySocketClient_Sensors.Run_Threads(True)