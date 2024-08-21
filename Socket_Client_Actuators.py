from Socket_Struct_Client_BaseClass import * 
from Socket_Utils_Timer import * 
from Lib_ArduinoConnection import *
from Socket_Struct_Client_Actuators_Helpers import * 
from Socket_Utils_Q import * 

class SocketClient_Actuators(Socket_Client_BaseClass):


    def __init__(self, ServiceName = Socket_Services_List.ACTUATORS, ForceServerIP = '',ForcePort='',LogOptimized = False):
        super().__init__(ServiceName,ForceServerIP,ForcePort,LogOptimized)

        self.MyArduino_Connection = Arduino_Connection()
        self.MyArduino_Connection.OpenConnection(ARDUINO_A_COM_PORT)
        self.ArduinoCommandsQ = Socket_Q[str]("Arduino Commands")


    def OnClient_Connect(self):
        
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
            
    def On_ClientAfterLogin(self):
        #self.RegisterTopics(Socket_Default_Message_Topics.NONE)
        self.SubscribeTopics(Socket_Default_Message_Topics.INPUT_KEYBOARD)
        self.SubscribeTopics(Socket_Default_Message_Topics.INPUT_JOYSTICK)
        pass
        
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
                    
                    if (ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_KEYBOARD
                        or ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_JOYSTICK):
                           
                        ArdCmd = Arduino_Keyboard_To_Actions().convert(ReceivedMessage.Message)
                        if (ArdCmd != ""):
                            if (ArdCmd == RobotArduinoCommands.STOP): 
                                #pulisco coda
                                self.ArduinoCommandsQ.Clear()
                                self.LogConsole(f"Q Cleared",ConsoleLogLevel.Test)
                            #Queue command
                            self.LogConsole(f"{self.ThisServiceName()} cmd {ArdCmd} received",ConsoleLogLevel.Test)
                           
                            self.ArduinoCommandsQ.put(ArdCmd)
                            self.ArduinoCommandsQ.Show()
                            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 

    def OnClient_Core_Task_Cycle(self):
        try:
            if (self.MyArduino_Connection.IsStarted):
                #if (self.ArduinoCommandsQ.HasItems()):
                if (self.ArduinoCommandsQ.HasItems()): # and self.CurrNUmOfMsgs<self.MSG_BLOCK):
                    self.MyArduino_Connection.sendData(self.ArduinoCommandsQ.get()) 
                    #self.CurrNUmOfMsgs +=1
                
                #self.CurrNUmOfMsgs = 0
            
            
            if (self.IsQuitCalled):
                return self.OnClient_Core_Task_RETVAL_QUIT
        
            return self.OnClient_Core_Task_RETVAL_OK
            
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
     
        
if (__name__== "__main__"):
    
    MySocketClient = SocketClient_Actuators()
    
    MySocketClient.Run_Threads()