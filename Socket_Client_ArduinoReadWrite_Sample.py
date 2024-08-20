from Socket_Struct_Client_BaseClass import * 
from Lib_ArduinoConnection import *
from Robot_Envs import * 
from Socket_Utils_Timer import * 
from Socket_Utils_Q import *

class Robot_Arduino_Sensor_Params:
     OBJ00 = "OBJ00"
     OBJ01 = "OBJ01"

ARDUINO_TEST = "COM3"  #To define in Env variables
     
class SocketClient_ArduinoReadWrite_Sample(Socket_Client_BaseClass):
    
    MyArduino_Connection = Arduino_Connection()
    ObjectLastValue = {}
    ObjectAbsSensitiveRange = {}
    MyTimer = Socket_Timer()
    
    def __init__(self, ServiceName = Socket_Services_List.ARDUINO_READ_WRITE, ForceServerIP = '',ForcePort='',LogOptimized = False):
        super().__init__(ServiceName,ForceServerIP,ForcePort,LogOptimized)
        self.MyArduino_Connection.OpenConnection(ARDUINO_TEST)
        self.ObjectLastValue[Robot_Arduino_Sensor_Params.OBJ00] = -1
        self.ObjectAbsSensitiveRange[Robot_Arduino_Sensor_Params.OBJ00] = 3
        
        self.ObjectLastValue[Robot_Arduino_Sensor_Params.OBJ01] = -1
        self.ObjectAbsSensitiveRange[Robot_Arduino_Sensor_Params.OBJ01] = 3
        self.MyTimer.start(30,"Forced Sensor Refresh")
        
        self.ArduinoCommandsQ = Socket_Q[str]("Arduino Commands")
        
    def OnClient_Connect(self):
        
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
    
    def On_ClientAfterLogin(self):
        
        self.RegisterTopics(Socket_Default_Message_Topics.INPUT_OBJ00)
        self.RegisterTopics(Socket_Default_Message_Topics.INPUT_OBJ01)
        self.SubscribeTopics(Socket_Default_Message_Topics.INPUT_KEYBOARD)
        
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
                    
                    if (ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_KEYBOARD):
                            
                            self.ArduinoCommandsQ.put(ReceivedMessage.Message)
                            self.ArduinoCommandsQ.Show()
        
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
        
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 
        
    def Sensor_Check_SendCondition(self,ThisObject, val=0):
        #Check send condistions
        IsToSend = False
        if (self.ObjectLastValue[ThisObject] == -1):  # First Time
            IsToSend = True
        else:
            if (abs(self.ObjectLastValue[ThisObject] - int(val)) > self.ObjectAbsSensitiveRange[ThisObject]):
                IsToSend = True    
        
        return IsToSend

    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
            if (self.MyArduino_Connection.IsStarted):
                
                #Send Queued Messages
                if (self.ArduinoCommandsQ.HasItems()): # and self.CurrNUmOfMsgs<self.MSG_BLOCK):
                    self.MyArduino_Connection.sendData(self.ArduinoCommandsQ.get()) 
                
                #Get incoming Mesage
                retData = self.MyArduino_Connection.ReadSerial()
                
                if (retData != ""):
                    ForceRefresh = self.MyTimer.IsTimeout(RestartIfTimeout=True)
                    
                    #Compass
                    ThisObject = Robot_Arduino_Sensor_Params.OBJ00
                    bFound, val = self._ParseParamValue(retData,ThisObject)
                   
                    if (bFound):
                        #Check send condition
                        if (self.Sensor_Check_SendCondition(ThisObject,val) or ForceRefresh):
                            self.LogConsole(self.ThisServiceName() + "Send  (" + str(val) + ") "+ ThisObject,ConsoleLogLevel.Test)
                            LocalObjectValue = int(val)
                            LocalMessage = str(ARDUINO_TEST + ": " + ThisObject)
                        
                            ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.INPUT_OBJ00,
                                                                            Message = LocalMessage, Value = LocalObjectValue)
                            
                            self.SendToServer(ObjToSend) 
                            
                            self.ObjectLastValue[ThisObject] = int(val)
                        else:
                            self.LogConsole(self.ThisServiceName() + "Not Send  (" + str(val) + ") "+ ThisObject,ConsoleLogLevel.Test)
                                    
                    #Battery
                    ThisObject = Robot_Arduino_Sensor_Params.OBJ01
                    bFound, val = self._ParseParamValue(retData,ThisObject)
                    
                    if (bFound):
                        #Check send condition
                        if (self.Sensor_Check_SendCondition(ThisObject,val) or ForceRefresh):
                            self.LogConsole(self.ThisServiceName() + "Send  (" + str(val) + ") "+ ThisObject,ConsoleLogLevel.Test)
                            
                            LocalObjectValue = int(val)
                            LocalMessage = str(ARDUINO_TEST + ": " + ThisObject)
                        
                            ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.INPUT_OBJ01,
                                                                            Message = LocalMessage, Value = LocalObjectValue)                
                    

                            self.SendToServer(ObjToSend)
                            
                            self.ObjectLastValue[ThisObject] = int(val) 
                        else:
                            self.LogConsole(self.ThisServiceName() + "Not Send (" + str(val) + ") "+ ThisObject,ConsoleLogLevel.Test)
                            
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
    
    MySocketClient_Sensors = SocketClient_ArduinoReadWrite_Sample(Socket_Services_List.SENSORS)
    
    MySocketClient_Sensors.Run_Threads(False)