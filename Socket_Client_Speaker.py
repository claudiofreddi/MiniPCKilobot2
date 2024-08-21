from Socket_Struct_Client_BaseClass import * 
from Socket_Utils_Timer import * 
from Lib_SpeakToMe import *
import queue

class SocketClient_Speaker(Socket_Client_BaseClass):


    
    def __init__(self, ServiceName = Socket_Services_List.SPEAKER, ForceServerIP = '',ForcePort='',LogOptimized = False):
        super().__init__(ServiceName,ForceServerIP,ForcePort,LogOptimized)
        self.SpeakerOn = True
        self.MySpeak = Service_SpeakToMe("",self.SpeakerOn)
        self.MySpeak.Speak("Speaker On")      
        self.MessageQ = queue.Queue()
    
    def OnClient_Connect(self):
        
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
        
    
    def On_ClientAfterLogin(self):
        self.RegisterTopics(Socket_Default_Message_Topics.OUTPUT_SPEAKER)  
        self.SubscribeTopics(Socket_Default_Message_Topics.OUTPUT_SPEAKER)
        pass
        
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreadyManaged=False):
        # if (self.IsConnected):
        #     if (not IsMessageAlreadyManaged):
        #         if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
        #             ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
        #             if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD):
        #                 MySpecificCommand = ReceivedMessage.Message
        
        try:
            if (self.IsConnected):
                if (IsMessageAlreadyManaged == False):
                    if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                        ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                        
                        if (ReceivedMessage.Topic == Socket_Default_Message_Topics.OUTPUT_SPEAKER):
                            if (self.SpeakerOn):
                                if (ReceivedMessage.Value == 0): ## queue
                                    self.MessageQ.put(ReceivedMessage.Message)  
                                else:  ## speak immediatly
                                    self.MySpeak.Speak(ReceivedMessage.Message)
                    
                            
                            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 

    def OnClient_Core_Task_Cycle(self):
        try:
            
            if (not self.MessageQ.empty()):
                M = self.MessageQ.get()
                self.MySpeak.Speak(M)
            

            
            # if (self.IsQuitCalled):
            #     return self.OnClient_Core_Task_RETVAL_QUIT
        
            return self.OnClient_Core_Task_RETVAL_OK
            
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
     
        
if (__name__== "__main__"):
    
    MySocketClient = SocketClient_Speaker()
    
    MySocketClient.Run_Threads()