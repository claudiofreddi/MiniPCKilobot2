from Socket_Client_BaseClass import * 
from Lib_ArduinoConnection import *
from Robot_Envs import * 

class Robot_Arduino_Sensor_Params:
     SENSOR_COMPASS = "SENSORS_COMPASS"
     SENSORS_BATTERY = "SENSORS_BATTERY"
     
class SocketClient_Sensors(Socket_Client_BaseClass):
    
    MyArduino_Connection = Arduino_Connection()
    SensorLastValue = {}
    SensorAbsSensitiveRange = {}
    
    
    def __init__(self, ServiceName = Socket_Services_List.SENSORS, ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort)
        self.MyArduino_Connection.OpenConnection(ARDUINO_B_COM_PORT)
        self.SensorLastValue[Robot_Arduino_Sensor_Params.SENSOR_COMPASS] = -1
        self.SensorAbsSensitiveRange[Robot_Arduino_Sensor_Params.SENSOR_COMPASS] = 3
        
        self.SensorLastValue[Robot_Arduino_Sensor_Params.SENSORS_BATTERY] = -1
        self.SensorAbsSensitiveRange[Robot_Arduino_Sensor_Params.SENSORS_BATTERY] = 3
        
        
    def OnClient_Connect(self):
        
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
    
    def On_ClientAfterLogin(self):
        
        self.RegisterTopics(Socket_Default_Message_Topics.SENSOR_COMPASS)
        self.RegisterTopics(Socket_Default_Message_Topics.SENSOR_BATTERY)
        
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreayManaged=False):
        #ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
        #self.LogConsole("OnClient_Receive: " + obj.Message + " [" + self.ServiceName + "]")
        pass
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
        
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 
        
    def Sensor_Check_SendCondition(self,ThisSensor, val=0):
        #Check send condistions
        IsToSend = False
        if (self.SensorLastValue[ThisSensor] == -1):  # First Time
            IsToSend = True
        else:
            if (abs(self.SensorLastValue[ThisSensor] - int(val)) > self.SensorAbsSensitiveRange[ThisSensor]):
                IsToSend = True    
        
        return IsToSend

    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
            if (self.MyArduino_Connection.IsStarted):
                retData = self.MyArduino_Connection.ReadSerial()
                
                if (retData != ""):
                    #Compass
                    ThisSensor = Robot_Arduino_Sensor_Params.SENSOR_COMPASS
                    bFound, val = self._ParseParamValue(retData,ThisSensor)
                   
                    if (bFound):
                        #Check send condition
                        if (self.Sensor_Check_SendCondition(ThisSensor,val)):
                            self.LogConsole(self.ThisServiceName() + "Send  (" + str(val) + ") "+ ThisSensor,ConsoleLogLevel.Test)
                            LocalSensorValue = int(val)
                            LocalMessage = str(ARDUINO_B_COM_PORT + ": " + ThisSensor)
                        
                            ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.SENSOR, 
                                                                            SubClassType = Socket_Default_Message_SubClassType.COMPASS, 
                                                                            Topic = Socket_Default_Message_Topics.SENSOR_COMPASS,
                                                                            Message = LocalMessage, Value = LocalSensorValue)
                            
                            self.SendToServer(ObjToSend) 
                            
                            self.SensorLastValue[ThisSensor] = int(val)
                        else:
                            self.LogConsole(self.ThisServiceName() + "Not Send  (" + str(val) + ") "+ ThisSensor,ConsoleLogLevel.Test)
                                    
                    #Battery
                    ThisSensor = Robot_Arduino_Sensor_Params.SENSORS_BATTERY
                    bFound, val = self._ParseParamValue(retData,ThisSensor)
                    
                    if (bFound):
                        #Check send condition
                        if (self.Sensor_Check_SendCondition(ThisSensor,val)):
                            self.LogConsole(self.ThisServiceName() + "Send  (" + str(val) + ") "+ ThisSensor,ConsoleLogLevel.Test)
                            
                            LocalSensorValue = int(val)
                            LocalMessage = str(ARDUINO_B_COM_PORT + ": " + Socket_Default_Message_SubClassType.BATTERY)
                        
                            ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.SENSOR, 
                                                                            SubClassType = Socket_Default_Message_SubClassType.BATTERY, 
                                                                            Topic = Socket_Default_Message_Topics.SENSOR_BATTERY,
                                                                            Message = LocalMessage, Value = LocalSensorValue)                
                    

                            self.SendToServer(ObjToSend)
                            
                            self.SensorLastValue[ThisSensor] = int(val) 
                        else:
                            self.LogConsole(self.ThisServiceName() + "Not Send (" + str(val) + ") "+ ThisSensor,ConsoleLogLevel.Test)
                            
            return self.OnClient_Core_Task_RETVAL_OK

        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
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