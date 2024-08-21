from Socket_Struct_Client_BaseClass import * 
from Socket_Utils_Timer import * 
from Socket_Logic_GlobalTextCmdMng import *

class SocketClient_Console(Socket_Client_BaseClass):

   
    def __init__(self, ServiceName = Socket_Services_List.CONSOLE, ForceServerIP = '',ForcePort='',LogOptimized = False):
        super().__init__(ServiceName,ForceServerIP,ForcePort,LogOptimized)
        
        
    def OnClient_Connect(self):
        
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
    
    def On_ClientAfterLogin(self):
        self.RegisterTopics(Socket_Default_Message_Topics.INPUT_TEXT_COMMANDS)
        self.SubscribeTopics(Socket_Default_Message_Topics.OUTPUT_TEXT_COMMANDS)     #receive feedback
        pass
        
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreadyManaged=False):
        # if (self.IsConnected):
        #     if (not IsMessageAlreadyManaged):
        #         if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
        #             ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
        #             if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD):
        #                 MySpecificCommand = ReceivedMessage.Message
        self.LogConsole("OnClient_Receive " +  ReceivedEnvelope.From, ConsoleLogLevel.Test)
        try:
            if (IsMessageAlreadyManaged == False):
                if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                    ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                    if (ReceivedMessage.Topic == Socket_Default_Message_Topics.OUTPUT_TEXT_COMMANDS):
                        if (ReceivedMessage.Message != ""):
                            print(ReceivedMessage.Message)
                        if (len(ReceivedMessage.ResultList)>0):
                            print(ReceivedMessage.ResultList)
                            
                            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 

    def OnClient_Core_Task_Cycle(self):
        try:
            
            if (self.IsConnected):

                #Default
                self.LogConsole(self.ThisServiceName() + "Waiting for your command...",ConsoleLogLevel.Test)
                FullTextCommand = '{}'.format(input(''))
                
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.INPUT_TEXT_COMMANDS,
                                                                Message =FullTextCommand
                                                                ,ReplyToTopic=Socket_Default_Message_Topics.OUTPUT_TEXT_COMMANDS
                                                                )
                    
                self.SendToServer( ObjToSend)   
                        
                if (self.IsQuitCalled):
                    return self.OnClient_Core_Task_RETVAL_QUIT
            
            return self.OnClient_Core_Task_RETVAL_OK
          
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
    
     
        
if (__name__== "__main__"):
    
    MySocketClient = SocketClient_Console()
    
    MySocketClient.Run_Threads()