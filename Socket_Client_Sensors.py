from Socket_Client_BaseClass import * 
from Lib_ArduinoConnection import *
from Robot_Envs import * 

class Robot_Arduino_Sensor_Params:
     SENSOR_COMPASS = "SENSORS_COMPASS"
     SENSORS_BATTERY = "SENSORS_BATTERY"
     
class SocketClient_Sensors(Socket_Client_BaseClass):
    
    MyArduino_Connection = Arduino_Connection()
    
    
    def __init__(self, ServiceName = Socket_Services_List.SENSORS, ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort)
        self.MyArduino_Connection.OpenConnection(ARDUINO_B_COM_PORT)
            
    def OnClient_Connect(self):
        
        self.LogConsole("OnClient_Connect")
    
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,IsMessageAlreayManaged=False):
        #obj:Socket_Default_Message = ReceivedEnvelope.GetDecodedMessageObject()
        #self.LogConsole("OnClient_Receive: " + obj.Message + " [" + self.ServiceName + "]")
        pass
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect")
        
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit") 

    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
            if (self.MyArduino_Connection.IsStarted):
                retData = self.MyArduino_Connection.ReadSerial()
                #self.LogConsole("RETDATA: " + retData)
                if (retData != ""):
                    #Compass
                    bFound, val = self._ParseParamValue(retData,Robot_Arduino_Sensor_Params.SENSOR_COMPASS)
                    if (bFound):
                        LocalSubClassType  = Socket_Default_Message_SubClassType.COMPASS
                        LocalSensorValue = int(val)
                        LocalMessage = str(ARDUINO_B_COM_PORT + ": " + Socket_Default_Message_SubClassType.COMPASS)
                    
                        ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.SENSOR, 
                                                                        SubClassType = LocalSubClassType, 
                                                                        Message = LocalMessage, Value = LocalSensorValue)
                        
                        self.SendToServer(ObjToSend) 
        
                #Battery
                    bFound, val = self._ParseParamValue(retData,Robot_Arduino_Sensor_Params.SENSORS_BATTERY)
                    if (bFound):
                        LocalSubClassType  = Socket_Default_Message_SubClassType.BATTERY
                        LocalSensorValue = int(val)
                        LocalMessage = str(ARDUINO_B_COM_PORT + ": " + Socket_Default_Message_SubClassType.BATTERY)
                    
                        ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.SENSOR, 
                                                                        SubClassType = LocalSubClassType, 
                                                                        Message = LocalMessage, Value = LocalSensorValue)                
                
               
                        self.SendToServer(ObjToSend) 
                
            return self.OnClient_Core_Task_RETVAL_OK

        except Exception as e:
            self.LogConsole(self.LogPrefix() + "Error in OnClient_Core_Task_Cycle()  " + str(e))
            return self.OnClient_Core_Task_RETVAL_ERROR
    
    
    #########################################################################
    #SPECIFIC FOR ARDUINO
    #########################################################################
    def _ParseParamValue(self,retData,ParamName):
        if (retData[:len(ParamName)] == ParamName):
            return True, retData[len(ParamName)+1:]
        else:
            return False, ''
     
        
           
   
        
if (__name__== "__main__"):
    
    MySocketClient_Sensors = SocketClient_Sensors(Socket_Services_List.SENSORS)
    
    MySocketClient_Sensors.Run_Threads(True)