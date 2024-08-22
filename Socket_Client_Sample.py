from Socket_Struct_Client_BaseClass import * 
from Socket_Utils_Timer import * 

class SocketClient_Sample(Socket_Client_BaseClass):

    LOCAL_PARAMS_ENABLE_Sample = "ENABLE_Sample"
    LOCAL_PARAMS_ENABLE_SampleUserCmd = "sample"
    LOCAL_PARAMS_ENABLE_SampleUserCmdDescr = "sample [on/off/switch]"
    
    def __init__(self, ServiceName = Socket_Services_List.SAMPLE, ForceServerIP = '',ForcePort='',LogOptimized = False):
        super().__init__(ServiceName,ForceServerIP,ForcePort,LogOptimized)

        #Params Definition:
        self.LocalListOfStatusParams.CreateOrUpdateParam(ParamName=self.LOCAL_PARAMS_ENABLE_Sample ,Value=StatusParamListOfValues.OFF
                                                             ,UserCmd=self.LOCAL_PARAMS_ENABLE_SampleUserCmd,ServiceName=ServiceName
                                                             ,UserCmdDescription=self.LOCAL_PARAMS_ENABLE_SampleUserCmdDescr)
        #Params Usage:
        #if (self.LocalListOfStatusParams.Util_IsParamOn(self.LOCAL_PARAMS_ENABLE_Sample)): 
        #
        
    def OnClient_Connect(self):
        
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
    
    def On_ClientAfterLogin(self):
        #self.RegisterTopics(Socket_Default_Message_Topics.NONE)
        #self.SubscribeTopics(Socket_Default_Message_Topics.NONE)
        pass
        
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreadyManaged=False):
        
        try:
            if (self.IsConnected):
                if (not IsMessageAlreadyManaged):
                    if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                        ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                        if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD):
                            #Add Sample for Change Params
                            pass
                            
    
                            
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
                #Sample To remove
                time.sleep(5)
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.MESSAGE, 
                                                                        Message = "Test", Value = 0)                
                    
                
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