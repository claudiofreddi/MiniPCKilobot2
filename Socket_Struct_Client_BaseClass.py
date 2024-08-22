from socket import *
import threading
import time
from typing import cast
from Robot_Envs import *
from Socket_Struct_ClientServer_BaseClass import * 
from Socket_Struct_Server_StatusParamList import * 
from Socket_Logic_GlobalTextCmdMng import Socket_TextCommandParser

class Local_Params_Suffix:
    #Common suffix and local param name
    _IS_IDLE = "_IS_IDLE"   #The Service do nothing during Main Cycle or Cyling Functions (for eavy duty clients)
                                        #Receve Messages (to allow re-enable)
    _SLEEP_TIME = "_SLEEP_TIME"
    
    
class Local_Params_User_Command:
    QUIT = "quit"
    _IS_IDLE ="idle"
    _SLEEP_TIME = "sleeptime" 
                                          
class Socket_Client_BaseClass(Socket_ClientServer_BaseClass):

    OnClient_Core_Task_RETVAL_OK = 0
    OnClient_Core_Task_RETVAL_QUIT= 1
    OnClient_Core_Task_RETVAL_ERROR = -1

    

    def __init__(self, ServiceName = "", ForceServerIP = '',ForcePort='',LogOptimized=False):
        super().__init__(ServiceName,ForceServerIP,ForcePort, False,LogOptimized)    
        
        self.DisconnectCount = 0
        self.LOCAL_PARAMS_SLEEP_TIME = self.ServiceName + Local_Params_Suffix._SLEEP_TIME
        self.LOCAL_PARAMS_IS_IDLE = self.ServiceName + Local_Params_Suffix._IS_IDLE
        
        
        self.LocalListOfStatusParams = StatusParamList()
        self.LocalListOfStatusParams.CreateOrUpdateParam(ParamName=self.LOCAL_PARAMS_IS_IDLE,Value=StatusParamListOfValues.OFF
                                                             ,UserCmd=Local_Params_User_Command._IS_IDLE
                                                             ,ServiceName=ServiceName
                                                             ,UserCmdDescription=Local_Params_User_Command._IS_IDLE + " [on/off/switch]")
        self.LocalListOfStatusParams.CreateOrUpdateParam( ParamName=self.LOCAL_PARAMS_SLEEP_TIME,Value="2"
                                                             ,UserCmd=Local_Params_User_Command._SLEEP_TIME
                                                             ,ServiceName=ServiceName
                                                             ,UserCmdDescription=Local_Params_User_Command._SLEEP_TIME + " [val]")
        
        
        
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
        
    def On_ClientAfterLogin(self):
        self.LogConsole("On_ClientAfterLogin()",ConsoleLogLevel.Override_Call)
    
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreadyManaged=False):
        # if (self.IsConnected):
        #     if (not IsMessageAlreadyManaged):
        #         if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
        #             ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
        #             if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD):
        #                 pass
        pass


    #######################################################
    # Common Commands Management (To call in Client)
    #######################################################
   
    def Common_Client_Command_Management(self,ReceivedMessage:Socket_Default_Message, AdditionalData = b''):
        
        try:
            self.LogConsole("Parent Specific_Client_Command_Management",ConsoleLogLevel.Override_Call)
            MySpecificCommand = ReceivedMessage.Message
                        
            #Extract Command and Params
            MyTP = Socket_TextCommandParser(MySpecificCommand)
            Cmd, P1, P2 = MyTP.Utils_Split_Cmd_Param_Param()
            self.LogConsole(f"Cmd:{Cmd},{P1},{P2}",ConsoleLogLevel.CurrentTest)   
            
            #Change Variable
            VarChanged = False
            bAlsoReplyToTopic=True
            MyParamName = ""
            pPar:StatusParam
            pPar, retval = self.LocalListOfStatusParams.GetParamByUserCmd(Cmd)
            if (retval):
                MyParamName = pPar.ParamName
                if (pPar.Util_Params_IsValid(P1)):
                    NewVal = self.LocalListOfStatusParams.Util_Params_SetValue(pPar,P1)
                    VarChanged = True
             
            
            if (Cmd == Local_Params_User_Command.QUIT):
                self.OnClient_Quit()
                self.LogConsole("Quit Message Received",ConsoleLogLevel.System)
                self.Quit()  
                VarChanged = False
                bAlsoReplyToTopic = False
               
            #Notify Changes Change Variable
            if (VarChanged and MyParamName !=""):
                    ObjToServer,ObjToReplyTopic = self.LocalListOfStatusParams.Util_Params_ConfimationMsg(ParamName=MyParamName,NewVal=NewVal
                                                                           ,AlsoReplyToTopic=bAlsoReplyToTopic
                                                                           ,ReplyToTopic=ReceivedMessage.ReplyToTopic)
                    if (ObjToServer): self.SendToServer(ObjToServer)                        
                    if (ObjToReplyTopic): self.SendToServer(ObjToReplyTopic)
                

            return VarChanged 
        
        except Exception as e:
            self.LogConsole("Client Error in Specific_Client_Command_Management " + str(e),ConsoleLogLevel.Error)
            return False
    
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
                        IsMessageAlreadyManaged = True                         
                        
                        if (ReceivedMessage.Message == Socket_ClientServer_Local_Commands.SOCKET_LOGIN_MSG):                
                            
                            #######################################################
                            # Login Requested
                            #######################################################
                            self.LogConsole("Client send Login Name: " + str(self.ServiceName))   
                            ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.LOGIN
                                                                                        ,Message =str(self.ServiceName)
                                                                                       )
                            
                            self.SendToServer(ObjToSend)    
                            
                            self.On_ClientAfterLogin()
                            
                            
                            #######################################################
                            # Send First Param Status of all parameters to server 
                            #######################################################
                            pParam:StatusParam
                            for pParam in self.LocalListOfStatusParams.List:
                                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_CLIENT_PARAM_UPDATED
                                                                #Suffix to service name
                                                                ,Message = pParam.ParamName
                                                                ,ValueStr= pParam.Value
                                                                ,ValueStr2= pParam.UserCmd
                                                                ,ValueStr3= pParam.UserCmdDescription)

                                self.SendToServer( ObjToSend)    
                                
                                               
                        #######################################################
                        # TOPIC_CLIENT_DIRECT_CMD
                        #######################################################                         
                        if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD):
                            IsMessageAlreadyManaged = self.Common_Client_Command_Management(ReceivedMessage,AdditionaByteData)
                        
                        
                        else:
                            IsMessageAlreadyManaged = False
                        
                        #Send To Inherited Objcts
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
            pParam, retval = self.LocalListOfStatusParams.GetParam(self.LOCAL_PARAMS_IS_IDLE)
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
                pParam, retval  = self.LocalListOfStatusParams.GetParam(self.LOCAL_PARAMS_IS_IDLE)
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
 