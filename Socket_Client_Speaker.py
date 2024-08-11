from Socket_Client_BaseClass import * 
from Socket_Timer import * 
from Lib_SpeakToMe import *

class SocketClient_Speaker(Socket_Client_BaseClass):

    MyTimer:Timer=Timer()
    SpeakerOn = True
    
    def __init__(self, ServiceName = Socket_Services_List.SPEAKER, ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort)
        self.MySpeak = Service_SpeakToMe("",self.SpeakerOn)
        self.MySpeak.Speak("Speaker On")      
        
    def OnClient_Connect(self):
        
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
        self.MyTimer.start(5,self.ServiceName)
    
    def On_ClientAfterLogin(self):
        self.SubscribeTopics(Socket_Default_Message_Topics.OUTPUT_SPEAKER)
        self.SubscribeTopics(Socket_Default_Message_Topics.OUTPUT_SPEAKER)
        pass
        
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreayManaged=False):
        #ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
        
        try:
            if (self.IsConnected):
                if (IsMessageAlreayManaged == False):
                    if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                        ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                        
                        if (ReceivedMessage.Topic == Socket_Default_Message_Topics.OUTPUT_SPEAKER):
                            if (self.SpeakerOn):
                                self.MySpeak.Speak(ReceivedMessage.Message)
                    
                            
                            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 

    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
            
            # if (self.MyTimer.IsTimeout()):
            
            #     #Sample To remove
                
            #     ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.MESSAGE, 
            #                                                             SubClassType = Socket_Default_Message_SubClassType.MESSAGE,
            #                                                             Topic = Socket_Default_Message_Topics.MESSAGE, 
            #                                                             Message = "Test", Value = self.MyTimer.GetElapsed())                
                    
                
            #     self.SendToServer(ObjToSend) 
            #     self.LogConsole(self.ThisServiceName() + " " + ObjToSend.GetMessageDescription(),ConsoleLogLevel.Always)
            #     self.MyTimer.Reset()
            
            
            
            # if (self.IsQuitCalled):
            #     return self.OnClient_Core_Task_RETVAL_QUIT
        
            return self.OnClient_Core_Task_RETVAL_OK
            
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
     
        
if (__name__== "__main__"):
    
    MySocketClient = SocketClient_Speaker()
    
    MySocketClient.Run_Threads()