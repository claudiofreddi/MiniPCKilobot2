from socket import *
import threading
import time
from typing import cast
from Robot_Envs import *
from Socket_Struct_ClientServer_BaseClass import * 
from Socket_Struct_ParamList import * 
from Socket_Struct_CommandList import * 
from  Socket_Logic_Topics import * 


   
class Local_Params_User_Command:
    QUIT = "quit"
                                          
class Socket_Client_BaseClass(Socket_ClientServer_BaseClass):

    OnClient_Core_Task_RETVAL_OK = 0
    OnClient_Core_Task_RETVAL_QUIT= 1
    OnClient_Core_Task_RETVAL_ERROR = -1

    

    def __init__(self, ServiceName = "", ForceServerIP = '',ForcePort='',LogOptimized=False):
        super().__init__(ServiceName,ForceServerIP,ForcePort, False,LogOptimized)    
        
        self.DisconnectCount = 0

        #NEW MNG
        self.LocalListOfStatusParams = StatusParamList()
        self.LocalListOfCommands = ServiceCommandList()
        
        #NEW MNG
        # define for all Clients
        self.Standard_Topics_For_Service = Topics_Standard_For_Service(self.ServiceName)
        
                        
        #NEW MNG
        #Param Definition (Common)
        self.ServiceParamStdBy =  "STANDBY"
        #LocalParamName, UserCmd, UserCmdDescription = self.Standard_Topics_For_Service.GetInfoForStatusParam(self.ServiceParamStdBy,"on/off/switch")
        self.LocalListOfStatusParams.CreateOrUpdateParam(ServiceName=self.ServiceName
                                                         , ParamName=self.ServiceParamStdBy
                                                         ,Value=StatusParamListOfValues.OFF
                                                         ,ArgDescr="on|off")
        
        #NEW MNG
        #Param Definition (Common)
        self.LocalParamSleepTime = "SLEEPTIME"
        #LocalParamName, UserCmd, UserCmdDescription = self.Standard_Topics_For_Service.GetInfoForStatusParam(self.LocalParamSleepTime,"value")
        self.LocalListOfStatusParams.CreateOrUpdateParam(ServiceName=self.ServiceName,
                                                         ParamName=self.LocalParamSleepTime
                                                         ,Value="10"
                                                        ,ArgDescr="on|off")
        
        #Command Definition (Common)
        self.LocalCommand_TESTCLIENT = "TESTCLIENT"
        LocalParamName, UserCmd, UserCmdDescription = self.Standard_Topics_For_Service.GetInfoForCommands(self.LocalCommand_TESTCLIENT,"")
        self.LocalListOfCommands.CreateCommand(UserCmd, UserCmdDescription)
        
        
        
    def SendToServer(self,MyMsg:Socket_Default_Message, 
                        Target=SocketMessageEnvelopeTargetType.SERVER,AdditionaByteData=b''):
        
        try:
            
            MyEnvelope:SocketMessageEnvelope = self.Prepare_StandardEnvelope(MsgToSend=MyMsg,To=Target,From=self.ServiceName)
            
            self.LogConsole("Client ["+ self.ServiceName + "] SendToServer: " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
            
            self.LogConsole("Client ["+ self.ServiceName + "] SendToServer: " + MyMsg.GetMessageDescription(),ConsoleLogLevel.Socket_Flow)
            
            SerializedObj = self.Pack_Envelope_And_Serialize(MyEnvelope)
           
            self.MySocket_SendReceive.send_msg(self.client,SerializedObj,AdditionaByteData)

            
        except Exception as e:
            self.LogConsole("Client Error in SendToServer  " + str(e))
    
    def ReceiveFromServer(self):
        try:
            MyEnvelope:SocketMessageEnvelope  = None
            
            ser_obj,AdditionaByteData,retval = self.MySocket_SendReceive.recv_msg(self.client)
            
            
            if (len(ser_obj)>0):
                MyEnvelope , retval = self.UnPack_StandardEnvelope_And_Deserialize(ser_obj)
                
                self.LogConsole("Client ["+ self.ServiceName + "] ReceiveFromServer: " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
                
            return MyEnvelope,AdditionaByteData 

        
        except Exception as e:
            self.LogConsole("Client Error in ReceiveFromServer " + str(e),ConsoleLogLevel.Error)
            return None, b''
         
    def OnClient_Connect(self):
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
    
    def _ClientAfterLoginLocal(self):
        
         #Listen to alla generic topic
         #'/@SAMPLE_Client/#CMD#' 
         #'/@SAMPLE_Client/#PARAM#'
         #'/@SAMPLE_Client/#REPLYTO#
        self.SubscribeTopics(self.Standard_Topics_For_Service.ServiceCommandTopic)
        self.SubscribeTopics(self.Standard_Topics_For_Service.ServiceParamsTopic)
        self.SubscribeTopics(self.Standard_Topics_For_Service.ServiceReplyToTopic)
        
        
    def On_ClientAfterLogin(self):
        self.LogConsole("On_ClientAfterLogin()",ConsoleLogLevel.Override_Call)
    
   
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
        
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call)

    
    # Listening to Server and Sending ServiceName
    # If Client CONNECTED
    # Perform LOGIN and send the fist status of all parameters to server
    def Client_Listening_Task(self):
        
        self.IsConnected = False
        
        while not self.IsQuitCalled:
            try:
                self.SleepTime(Multiply=3,CalledBy="Client_Listening_Task",Trace=False)
                
                #Retry conncetion if needed
                if (not self.IsConnected):
                    self.Connect()
                    self.OnClient_Connect()
                    
                #If OK talk
                if (self.IsConnected):

                    # Receive Message From Server
                    # If 'NICK' Send ServiceName
                    
                    ReceivedEnvelope, AdditionaByteData = self.ReceiveFromServer()
                    if (ReceivedEnvelope != None):
                        self.LogConsole(self.ThisServiceName() + " ReceiveFromServer: " + ReceivedEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
                    
                    IsMessageAlreadyManaged = False                   
                    if (ReceivedEnvelope != None):
                        
                        
                        ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                        IsMessageAlreadyManaged = False                         
                        
                        #######################################################
                        # LOGIN COMMAND AND PARAMS/COMMANDS REGISTRATION
                        #######################################################  
                        if (ReceivedMessage.Message == Socket_ClientServer_Local_Commands.SOCKET_LOGIN_MSG):                
                            
                            #######################################################
                            # Login Requested
                            #######################################################
                            self.LogConsole("Client send Login Name: " + str(self.ServiceName))   
                            ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.LOGIN
                                                                                        ,Message =str(self.ServiceName)
                                                                                       )
                            
                            self.SendToServer(ObjToSend)    
                            
                            self._ClientAfterLoginLocal()
                            
                            self.On_ClientAfterLogin()
                            
                            
                            #######################################################
                            # Send First Param Status of all parameters to server 
                            #######################################################
                            pParam:StatusParam
                            for pParam in self.LocalListOfStatusParams.List:
                                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_CLIENT_PARAM_SERVER_REGISTER
                                                                #Suffix to service name
                                                                ,Message = pParam.ParamName
                                                                ,ValueStr= pParam.Value
                                                                ,ValueStr2= pParam.ServiceName
                                                                ,ValueStr3= pParam.ArgDescr)

                                self.SendToServer( ObjToSend)    
                                
                            pCmd:ServiceCommand
                            
                            for pCmd in self.LocalListOfCommands.List:
                                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_CLIENT_COMMAND_SERVER_REGISTER
                                                                #Suffix to service name
                                                                ,Message = ""
                                                                ,ValueStr= ""
                                                                ,ValueStr2= pCmd.UserCmd
                                                                ,ValueStr3= pCmd.UserCmdDescription)

                                self.SendToServer( ObjToSend)    
                            
                            IsMessageAlreadyManaged = True  

                        #######################################################
                        # CLIENT SPECIFIC TOPIC (PARAMS UPDATE AND COMMANDS)
                        #######################################################                         
                        LocalTopicTest = TopicManager(ReceivedMessage.Topic)
                        
                        VarChanged = False
                        bAlsoReplyToTopic=True
                        MyParamName = ""
                        CommandExecuted = False
                        CommandRetval = ""
                        
                        
                        #self.LogConsole(LocalTopicTest.Describe(),ConsoleLogLevel.CurrentTest)
                        
                        if (LocalTopicTest.IsValid):
                            if (LocalTopicTest.IsParam):
                                pPar:StatusParam
                                pPar, retval = self.LocalListOfStatusParams.GetParam(LocalTopicTest.Param)
                                if (retval):
                                    MyParamName = pPar.ParamName
                                    if (pPar.Util_Params_IsValid(LocalTopicTest.ParamVal)):
                                        NewVal = self.LocalListOfStatusParams.Util_Params_SetValue(pPar,LocalTopicTest.ParamVal)
                                        VarChanged = True 
                                        IsMessageAlreadyManaged = True #PARAM SET
                                        
                            elif (LocalTopicTest.IsCommand):
                                pCmd:ServiceCommand
                                pCmd, retval = self.LocalListOfCommands.Get(LocalTopicTest.Param)
                                if (retval):
                                    CurrCmd = pCmd.UserCmd
                                    CurrArgs = LocalTopicTest.Args

                                    CommandExecuted, CommandRetval, bAlsoReplyToTopic = self.Execute_Service_SpecificCommand(Command=CurrCmd,Args=CurrArgs, 
                                                                                                                      ReceivedMessage=ReceivedMessage,
                                                                                                                      AdditionaByteData=AdditionaByteData)
                                    
                                    IsMessageAlreadyManaged = CommandExecuted
                                
                            elif (LocalTopicTest.IsReplyTo):
                                print(ReceivedMessage.Message)
                                IsMessageAlreadyManaged = True
                        
                            #Notify Changes Change Variable
                            if ((VarChanged and MyParamName !="") or CommandExecuted):
                                if (LocalTopicTest.IsParam):
                                    ObjToServer,ObjToReplyTopic = self.LocalListOfStatusParams.Util_Params_ConfimationMsg(ParamName=MyParamName,NewVal=NewVal
                                                                                        ,AlsoReplyToTopic=bAlsoReplyToTopic
                                                                                        ,ReplyToTopic=ReceivedMessage.ReplyToTopic)
                                if (LocalTopicTest.IsCommand):
                                    ObjToServer,ObjToReplyTopic = self.LocalListOfCommands.Util_Command_ConfimationMsg(CommandName=MyParamName,CommandRetval=CommandRetval
                                                                                        ,AlsoReplyToTopic=bAlsoReplyToTopic
                                                                                        ,ReplyToTopic=ReceivedMessage.ReplyToTopic)
                                    
                                if (ObjToServer): self.SendToServer(ObjToServer)                        
                                if (ObjToReplyTopic): self.SendToServer(ObjToReplyTopic)
                        #######################################################
                        # END CLIENT SPECIFIC TOPIC (PARAMS UPDATE AND COMMANDS)
                        #######################################################                         

                        #######################################################
                        # CLIENT OTHER MESSAGES
                        #######################################################                         
                        if (not self.IsQuitCalled):
                            self.OnClient_Receive(ReceivedEnvelope=ReceivedEnvelope,AdditionaByteData=AdditionaByteData,IsMessageAlreadyManaged=IsMessageAlreadyManaged)   

                                                                
                    else: 
                        if (self.ForceDisconnect()):               
                            break      
                else:
                    #Connection Failed    
                    if (self.ForceDisconnect()):               
                        break   
                    
            except Exception as e:
                
                self.LogConsole("Error in Client_Listening_Task()  " + str(e),ConsoleLogLevel.Error)
                
                if (self.ForceDisconnect()):               
                     break
                 
         
    def Execute_Service_SpecificCommand(self,Command:str,Args:str, ReceivedMessage:Socket_Default_Message,AdditionaByteData=b''):
        CommandExecuted = False
        CommandRetval=  ""
        bAlsoReplyToTopic = True
        
        ###################################################
        #Define Here Common Parent Commands
        ###################################################
        if (Command == self.LocalCommand_TESTCLIENT):
            CommandExecuted = True
            CommandRetval =  "text client Received"
            
    
        ###################################################
        #END OF LOCAL MANAGED COMMANDS
        ###################################################
        if (CommandExecuted):     
            return CommandExecuted, CommandRetval, bAlsoReplyToTopic
    
        ###################################################
        #FORWARD TO CHILD COMMANDS
        ###################################################
        return self.After_Execute_Service_SpecificCommands(Command=Command,Args=Args, ReceivedMessage= ReceivedMessage,AdditionaByteData=AdditionaByteData)
        
    
    #OVERRIDE
    def After_Execute_Service_SpecificCommands(self,Command:str,Args:str, ReceivedMessage:Socket_Default_Message,AdditionaByteData=b''):
        CommandExecuted = False
        CommandRetval=  ""
        bAlsoReplyToTopic = True
        
        
        return CommandExecuted, CommandRetval, bAlsoReplyToTopic
    
    #OVERRIDE   
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreadyManaged=False):
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


    def ForceDisconnect(self):
        self.DisconnectCount += 1
        self.LogConsole(f"Client disconnecting [{self.DisconnectCount}] ...",ConsoleLogLevel.System)  
        self.OnClient_Disconnect()
        self.Disconnect()
        
        if (self.IsQuitCalled == False):
            self.LogConsole("An error occured! Retry in " + str(self.RETRY_TIME) + " sec..",ConsoleLogLevel.System)
            time.sleep(self.RETRY_TIME) #Wait 30 sec and retry
            return False
        else:
            self.LogConsole("Service Quitted",ConsoleLogLevel.System)
            return True
     
    #UTILS: to register TOPICS
    def RegisterTopics(self, *ClientTopics):
        for t in ClientTopics:
            try:
                
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_REGISTER
                                                                        , Message = t)
                self.SendToServer( ObjToSend)   
            
            except Exception as e:
                self.LogConsole(self.ThisServiceName() + "Error in RegisterTopics()  " + str(e),ConsoleLogLevel.Error)
    
    #UTILS: to subscribe TOPICS
    def SubscribeTopics(self, *TopicsToSubscribe):
        for t in TopicsToSubscribe:
            try:
                
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_SUBSCRIBE
                                                                        ,Message = t)
                self.SendToServer( ObjToSend)   
            
            except Exception as e:
                self.LogConsole(self.ThisServiceName() + "Error in RegisterTopics()  " + str(e),ConsoleLogLevel.Error)
                
    #OVERRIDE: CORE TASK CYCLE: inner main cycle of Service
    def OnClient_Core_Task_Cycle(self):
        try:
            pParam, retval = self.LocalListOfStatusParams.GetParam(self.ServiceParamStdBy)
            if (pParam.Value==StatusParamListOfValues.ON):
                return self.OnClient_Core_Task_RETVAL_OK
            

            return self.OnClient_Core_Task_RETVAL_OK
        
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
    #CORE TASK: run as thread call self.OnClient_Core_Task_Cycle() to be override
    def Client_Core_Task(self):
        try:
            while not self.IsQuitCalled:
                
                #Basic Management of Service Idle 
                pParam, retval  = self.LocalListOfStatusParams.GetParam(self.ServiceParamStdBy)
                if (retval):
                    if (pParam.Value==StatusParamListOfValues.ON): 
                        time.sleep(self.SLEEP_TIME)
                        continue
                    
                self.SleepTime(Multiply=1,CalledBy="OnClient_Core_Task_Cycle",Trace=False)
                
                retval = self.OnClient_Core_Task_Cycle() 
                
                if (retval == self.OnClient_Core_Task_RETVAL_QUIT):
                    self.Quit()
                
                if (retval == self.OnClient_Core_Task_RETVAL_ERROR):
                    self.LogConsole(self.ThisServiceName() + " Error in Inner - Client_Core_Task () Break " + str(e),ConsoleLogLevel.System)
                    break
                
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in Inner - OnClient_Core_Task()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
  
    
    #MAIN TO CALL TO START CLIENT    
    def Run_Threads(self):
        # Starting Threads For Listening And Writing
        receive_thread = threading.Thread(target=self.Client_Listening_Task)
        receive_thread.start()
        
        receive_thread = threading.Thread(target=self.Client_Core_Task)
        receive_thread.start()
        
      
  
        
if (__name__== "__main__"):
    
    for i in range(1):
        MySocket_Client_BaseClass =  Socket_Client_BaseClass("Servizio" + str(i))
        MySocket_Client_BaseClass.Run_Threads()      
 