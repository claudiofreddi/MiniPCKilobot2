from Socket_Struct_Client_BaseClass import * 
from Socket_Utils_Timer import * 
from  Socket_Logic_Topics import * 

class SocketClient_Sample(Socket_Client_BaseClass):

    LOCAL_PARAMS_ENABLE_Sample = "PARAM"
    LOCAL_COMMAND_PRINT_THIS = "print_this"
    
    
    def __init__(self, ServiceName = Socket_Services_List.SAMPLE, ForceServerIP = '',ForcePort='',LogOptimized = False):
        super().__init__(ServiceName,ForceServerIP,ForcePort,LogOptimized)
        
        #Sample generico topic of this service -> Counter
        self.GenerciTopic_Counter = "/COUNTER"
        self.MyCounter = 0
        
        
        #Params Definition:
        self.LocalListOfStatusParams.CreateOrUpdateParam(ServiceName=ServiceName
                                                         ,Name=self.LOCAL_PARAMS_ENABLE_Sample 
                                                         ,Value=StatusParamListOfValues.OFF
                                                         ,ArgDescr="on|off")
        
        #Command Definition (Common)
        self.LocalListOfCommands.CreateCommand(ServiceName=ServiceName
                                               ,Name=self.LOCAL_COMMAND_PRINT_THIS)
        

        
    def OnClient_Connect(self):
        
        
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
    
    def On_ClientAfterLogin(self):
        
        #self.RegisterTopics(Socket_Default_Message_Topics.NONE)
        #self.SubscribeTopics(Socket_Default_Message_Topics.INPUT_KEYBOARD)
        #self.SubscribeTopics(Socket_Default_Message_Topics.INPUT_JOYSTICK)
              

        
        pass
    
    #Define here this client commands
    def After_Execute_Service_SpecificCommands(self,Command:str,Args:str, ReceivedMessage:Socket_Default_Message,AdditionaByteData=b''):
        
        try:
            CommandExecuted = False
            CommandRetval=  ""
            bAlsoReplyToTopic = True
            
            if (Command == self.LOCAL_COMMAND_PRINT_THIS):
                print("THIS")
                CommandRetval=  "Printed"
                CommandExecuted = True
                
                

                
            
            self.LogConsole("*After_Execute_Service_SpecificCommands" + Command,ConsoleLogLevel.CurrentTest)
            
            
            return CommandExecuted, CommandRetval, bAlsoReplyToTopic
        
        
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return False, self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e), True
        
        
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreadyManaged=False):
        try:
            # if (self.IsConnected):
            #     if (not IsMessageAlreadyManaged):
            #         if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
            #             ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
            #             LocalTopicTest = TopicManager(ReceivedMessage.Topic)
            #             if (LocalTopicTest.IsValid):
            #                 pass #here speific topic commands
            #             else:
            #                 if (ReceivedMessage.Topic == Socket_Default_Message_Topics.MESSAGE):
            #                     pass #here others topic
            pass    
                            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
 
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 

    def OnClient_Core_Task_Cycle(self):
        
        IsEnabled = False
        try:
            
            if (self.IsConnected):
                #Sample To remove
                time.sleep(5)
                
                if (IsEnabled):
                    ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = self.GenerciTopic_Counter , 
                                                                            Message = "Counter", Value = self.MyCounter,
                                                                            ReplyToTopic=self.Standard_Topics_For_Service.ServiceReplyToTopic
                                                                            )
                    self.MyCounter += 1                
                        
                    
                    self.SendToServer(ObjToSend) 
                    self.LogConsole(self.ThisServiceName() + " " + ObjToSend.GetMessageDescription(),ConsoleLogLevel.Always)
                
                            
                    if (self.IsQuitCalled):
                        return self.OnClient_Core_Task_RETVAL_QUIT
            
            return self.OnClient_Core_Task_RETVAL_OK
          
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
    

          
                
if (__name__== "__main__"):
    
    MySocketClient = SocketClient_Sample()
    
    MySocketClient.Run_Threads()