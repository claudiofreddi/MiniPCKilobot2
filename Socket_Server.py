import socket

import threading
import time
from Robot_Envs import * 
from Socket_Struct_ClientServer_BaseClass import * 
from Socket_Struct_Messages import * 
from Socket_Struct_Client_Object import *
from Socket_Struct_Server_Robot_Commands import *
from PIL import Image
from Socket_Utils_Text import * 

from Socket_Struct_ParamList import * 
from Socket_Struct_CommandList import *
from Socket_Logic_Topics import * 
#from Socket_Server_Commands import * 

class ServerLocalCommands:

    GET_HELP = "?"
    GET_TOPICS = "get topics"
    GET_STATUS = "get status"
    GET_CLIENTS = "get clients"
    GET_SENSORS = "get sensors"
    GET_COMMANDS = "get commands"
    SHOW_SERVER_MSGS = "togglemsgs"
    SHOW_SERVER_IMAGE = "toggleimage"
    

class ServerLocalParamNames:
    SERVER_CAMERA = "SERVER_CAMERA" 
    SERVER_SHOW_RECEIVED_MSGS = "SERVER_SHOW_RECEIVED_MSGS"
    SERVER_SHOW_SEND_MSGS = "SERVER_SHOW_SEND_MSGS"

import cv2

class Socket_Server(Socket_ClientServer_BaseClass): 

    
    client_objects = []
   
 
    def __init__(self,ServiceName = Socket_Services_List.SERVER, ForceServerIP = '',ForcePort='',LogOptimized=False):
        super().__init__(ServiceName,ForceServerIP,ForcePort, True,LogOptimized)
        
        self.RunOptimized = LogOptimized
        self.FrameName = 'server'
        self.SERVER_MAIN_CYCLE_SLEEP = 5 #sec
        self.MyListOfSensors = []
        self.MyFramesName = []
        
        #NEW MNG
        self.ServerListOfStatusParams = StatusParamList()
        self.ServerListOfCommands = ServiceCommandList()
        
        #NEW MNG
        # define for Server
        self.Standard_Topics_For_Server = Topics_Standard_For_Service(self.ServiceName)
       
        #Command Definition (Common)
        self.LocalCommand_TESTSERVER = "TESTSERVER"
        LocalParamName, UserCmd, UserCmdDescription = self.Standard_Topics_For_Server.GetInfoForCommands(CommandName=self.LocalCommand_TESTSERVER,ArgsDescription="")
        self.ServerListOfCommands.CreateCommand(UserCmd=UserCmd, UserCmdDescription=UserCmdDescription,GiveFeedback=True,AltCommand="")
        
        #XYZ
        #Command Definition
        self.AddCommand(Name=ServerLocalCommands.GET_HELP)
        self.AddCommand(Name=ServerLocalCommands.GET_CLIENTS)
        self.AddCommand(Name=ServerLocalCommands.GET_TOPICS,AltCommand="ctrl+T")
        self.AddCommand(Name=ServerLocalCommands.GET_STATUS,AltCommand="ctrl+T")
        self.AddCommand(Name=ServerLocalCommands.GET_COMMANDS)
        self.AddCommand(Name=ServerLocalCommands.GET_SENSORS)
        self.AddCommand(Name=ServerLocalCommands.SHOW_SERVER_MSGS,AltCommand="ctrl+M")
        self.AddCommand(Name=ServerLocalCommands.SHOW_SERVER_IMAGE,AltCommand="ctrl+I")
        
        
        self.ServerListOfStatusParams.CreateOrUpdateParam(ServiceName=ServiceName
                                                          ,ParamName=ServerLocalParamNames.SERVER_CAMERA
                                                          ,Value=StatusParamListOfValues.ON
                                                          ,ArgDescr="on|off")
         
        self.ServerListOfStatusParams.CreateOrUpdateParam(ServiceName=ServiceName
                                                        ,ParamName=ServerLocalParamNames.SERVER_SHOW_RECEIVED_MSGS
                                                        ,Value=StatusParamListOfValues.OFF
                                                        ,ArgDescr="on|off")
        
        self.ServerListOfStatusParams.CreateOrUpdateParam(ServiceName=ServiceName
                                                          ,ParamName=ServerLocalParamNames.SERVER_SHOW_SEND_MSGS
                                                          ,Value=StatusParamListOfValues.OFF
                                                          ,ArgDescr="on|off")
          
        
        self.Connect()    

    def AddCommand(self, Name:str,ArgsDescr="",GiveFeedback=True,AltCommand=""):
        LocalParamName, UserCmd, UserCmdDescription = self.Standard_Topics_For_Server.GetInfoForCommands(CommandName=Name,ArgsDescription=ArgsDescr)
        self.ServerListOfCommands.CreateCommand(UserCmd, UserCmdDescription,GiveFeedback=True,AltCommand=AltCommand)
    
    def SendToClient(self,TargetClient, MyMsg:Socket_Default_Message,From='',AdditionaByteData=b''): 
        c:client_object
        try:
            c , retval = self.GetClientObject(TargetClient)
            ToServiceName = c.servicename if (retval) else ''
            
            MyEnvelope:SocketMessageEnvelope = self.Prepare_StandardEnvelope(MsgToSend=MyMsg,To=ToServiceName,From=self.ServiceName)
            SerializedObj = self.Pack_Envelope_And_Serialize(MyEnvelope)
            
            self.MySocket_SendReceive.send_msg(TargetClient,SerializedObj,AdditionaByteData)
            
            if (self.ServerListOfStatusParams.CheckParam(ServerLocalParamNames.SERVER_SHOW_SEND_MSGS,StatusParamListOfValues.ON)):
                LogParam = ConsoleLogLevel.Show
            else:
                LogParam = 0

            self.LogConsole("Server SendToClient [" + ToServiceName + "]: " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow,LogParam)
            self.LogConsole("Server SendToClient [" + ToServiceName + "]: " + MyMsg.GetMessageDescription(),ConsoleLogLevel.Socket_Flow,LogParam)
            
        except Exception as e:
            
            self.LogConsole("Server Error in SendToClient " + str(e),ConsoleLogLevel.Error)
            
                  
    def GetFromClient(self,TargetClient:socket):
        c:client_object
        try:
                          
            c, retval = self.GetClientObject(TargetClient)
          
            #if (c):
                
            FromServiceName = c.servicename if (retval) else ''


            ser_obj,AdditionaByteData,retval = self.MySocket_SendReceive.recv_msg(TargetClient)
            
        
            MyEnvelope, retval = self.UnPack_StandardEnvelope_And_Deserialize(ser_obj)
 
            if (retval):
            
                if (self.ServerListOfStatusParams.CheckParam(ServerLocalParamNames.SERVER_SHOW_RECEIVED_MSGS,StatusParamListOfValues.ON)):
                    LogParam = ConsoleLogLevel.Show
                else:
                    LogParam = 0
                self.LogConsole("Server GetFromClient [" + FromServiceName + "] " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow,LogParam)
                
                return MyEnvelope,AdditionaByteData ,True 
            else:
                #self.LogConsole("MyEnvelope not Decoded in GetFromClient - May be Client disconncted ",ConsoleLogLevel.System)
                return None, b'',False   
        
        except Exception as e:
            # if (TargetClient):
            #     self.QuitClient(TargetClient,True)
            
            #self.LogConsole("Server Error in GetFromClient " + str(e),ConsoleLogLevel.Error)
            return None, b'',False   
    
    
       
    # List all servicenames
    def ListActiveservicenames(self):
        self.LogConsole("Active servicenames",ConsoleLogLevel.Test)
        c:client_object
        for c in self.client_objects:
            self.LogConsole(c.servicename,ConsoleLogLevel.Show)   


    def GetClientObject(self,client):
        found = False
        try:
            c:client_object
            for c in self.client_objects:
                if (c.client == client):
                    found = True
                    return c,found
            return None,found
        except Exception as e:
            self.LogConsole("Server Error in GetClientObject() " + str(e),ConsoleLogLevel.Error)  
            return None,found
            
    def GetClientObjectByServiceName(self,ServiceNameToFind:str)->client_object:
        
        c:client_object
        for c in self.client_objects:
            if (c.servicename.lower() == ServiceNameToFind.lower()):
                return c
        return None
    
    
    def CheckIfServiceNameExists(self,ServiceNameToFind)->bool:
        
        c:client_object
        for c in self.client_objects:
            if (c.servicename == ServiceNameToFind):
                return True
        return False
    
    def QuitClient(self, TargetClient:socket, Broadcast = True):
        c:client_object
        try: 
            c, retval = self.GetClientObject(TargetClient)
            if (retval):  
                ServiceName = c.servicename
                self.client_objects.remove(c)
                TargetClient.close()
                msg = '{} left!'.format(ServiceName)
                self.LogConsole(msg,ConsoleLogLevel.Socket_Flow)
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.MESSAGE,
                                                                        Message =msg
                                                                        )
                if (Broadcast):
                    self.broadcastObj(ObjToSend,ServiceName)
        
        except Exception as e:
            
            self.LogConsole("Server Error in QuitClient() " + str(e),ConsoleLogLevel.Error)                 

    def broadcastObj(self,ObjToSend:Socket_Default_Message, ExcludeServiceName = ""):
        try:
            c:client_object
            count = 0
            for c in self.client_objects:
                
                if (c.servicename != ExcludeServiceName):
                    self.LogConsole("Server Broadcast to: " + c.servicename,ConsoleLogLevel.Socket_Flow)
                    self.SendToClient (c.client, ObjToSend)
                    count = count + 1
                    
            return count
        except Exception as e:
        
            self.LogConsole("Server Error in broadcastObj() " + str(e),ConsoleLogLevel.Error)                 
    
    
    #Used to send Messages based on subscriptions
    def BroadCastMessageByTopic(self, ReceivedMessage:Socket_Default_Message,AdditionaByteData=b''):
        c:client_object
        
        if (not Socket_Default_Message_Topics().IsTopicReserved(ReceivedMessage.Topic)):
            for c in self.client_objects:
                if (c.IsSubscribedToThisTopic(ReceivedMessage.Topic)):
                    self.SendToClient(TargetClient=c.client,MyMsg=ReceivedMessage,From= Socket_Services_List.SERVER,AdditionaByteData=AdditionaByteData)
    
           
                
    def GetSensor(self,Topic):
        pSensor:Socket_Default_Message
        for pSensor in self.MyListOfSensors:
            if (pSensor.Topic == Topic):
                    return True, pSensor
        return False, None   
    


    # Handling Messages From Clients
    def handle(self,client:socket):
        
       
        ## Read Client Info from 
        CurrClientObject,retval = self.GetClientObject(client)
        
        if (retval):
            LocalMsgPrefix = self.ThisServiceName() + " from [" + CurrClientObject.servicename + "]"
            self.LogConsole(LocalMsgPrefix + " handle() started",ConsoleLogLevel.System)
            while True:
                try:
                    ## Receive Message
                    ReceivedEnvelope:SocketMessageEnvelope
                    ReceivedMessage:Socket_Default_Message
                    
                    ReceivedEnvelope, AdditionaByteData, retval = self.GetFromClient(client)
                    
                    
                    if (not retval): 
                        self.LogConsole(LocalMsgPrefix + " handle() Evelope Not Correct. Assume Break Connection. Quit.",ConsoleLogLevel.System)
                        break
                    else:
                        if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                            
                            
                            ReceivedMessage = ReceivedEnvelope.GetReceivedMessage()

                            ########################################################################################    
                            #ENABLE/DISABLE SHOW OF ALL MESSAGES FROM CLIENT
                            ########################################################################################    
                            if (self.ServerListOfStatusParams.CheckParam(ServerLocalParamNames.SERVER_SHOW_RECEIVED_MSGS,StatusParamListOfValues.ON)):
                                LogParam = ConsoleLogLevel.Show
                            else:
                                LogParam = 0

                            self.LogConsole("Server GetFromClient [" + CurrClientObject.servicename + "] " + ReceivedMessage.GetMessageDescription(),ConsoleLogLevel.Socket_Flow,LogParam )                
                                        
                            ########################################################################################                        
                            ##BROADCAST IF REQUIRED (to All client except this [sender])
                            ########################################################################################                                        
                            if (ReceivedEnvelope.To == SocketMessageEnvelopeTargetType.BROADCAST):   
                                #Broadcast requested by client
                                self.broadcastObj(ReceivedMessage, ReceivedEnvelope.From)
                            else:
                                #By Topic
                                self.BroadCastMessageByTopic(ReceivedMessage,AdditionaByteData)

                            ########################################################################################                        
                            ##Gestione Messaggi Conosciuti dal server   
                            ########################################################################################  
                             
                            ## SEZIONE TOPIC SPECIALI
                       
                            if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_REGISTER):
                                if (CurrClientObject.RegisterTopic(ReceivedMessage.Message)):
                                    self.LogConsole("[" + CurrClientObject.servicename +  "]  Added Topic [" + ReceivedMessage.Message + "]",ConsoleLogLevel.System)
                            
                            elif (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_SUBSCRIBE):
                                if (CurrClientObject.SubscribeTopic(ReceivedMessage.Message)):
                                    self.LogConsole("[" + CurrClientObject.servicename +  "] Subscribed to Topic [" + ReceivedMessage.Message + "]",ConsoleLogLevel.System)
                                    
                            elif (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_PARAM_SERVER_REGISTER):
                                self.ServerListOfStatusParams.CreateOrUpdateParam(ServiceName=ReceivedMessage.ValueStr2
                                                                                  ,ParamName=ReceivedMessage.Message
                                                                                  ,Value=ReceivedMessage.ValueStr
                                                                                  ,ArgDescr=ReceivedMessage.ValueStr3)
                            
                            elif (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_COMMAND_SERVER_REGISTER):   
                                self.ServerListOfCommands.CreateCommand(UserCmd=ReceivedMessage.ValueStr2
                                                                              ,UserCmdDescription=ReceivedMessage.ValueStr3
                                                                              ,ServiceName=CurrClientObject.servicename)
                                

                                                                                                                      
                            ########################################################################################                        
                            ## TOPIC TO BE MANAGED  
                            ########################################################################################  
                            ##SocketObjectClassType.SENSOR : value update      
                            elif (   ReceivedMessage.Topic== Socket_Default_Message_Topics.SENSOR_COMPASS
                                or ReceivedMessage.Topic== Socket_Default_Message_Topics.SENSOR_BATTERY
                                or ReceivedMessage.Topic== Socket_Default_Message_Topics.INPUT_LIDAR_MIN_DISTANCE
                                or ReceivedMessage.Topic== Socket_Default_Message_Topics.INPUT_LIDAR_BEST_WAYOUT_DIR
                                ):
                                self.Specific_Topic_Management_SENSOR(ReceivedMessage=ReceivedMessage)            
                                                           
                            elif ((ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_KEYBOARD and ReceivedMessage.Value==0)
                                 or ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_TELEGRAM
                                 or ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_TEXT_COMMANDS
                                 or ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_JOYSTICK
                                 ):
                                self.Specific_Topic_Management_INPUT_TEXT_COMMAND(ReceivedMessage=ReceivedMessage,CurrClientObject=CurrClientObject,AdditionalData=AdditionaByteData)
        
                            elif (ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_IMAGE):
                                self.Specific_Topic_Management_INPUT_IMAGE(ReceivedMessage=ReceivedMessage,AdditionalData=AdditionaByteData)
     
                            
                            else:
                                #######################################################
                                # CLIENT SPECIFIC TOPIC (PARAMS UPDATE AND COMMANDS)
                                #######################################################                         
                                LocalTopicTest = TopicManager(ReceivedMessage.Topic)
                                
                                VarChanged = False
                                bAlsoReplyToTopic=True
                                MyParamName = ""
                                CommandExecuted = False
                                CommandRetval = ""

                                
                                self.LogConsole(LocalTopicTest.Describe(),ConsoleLogLevel.Test)
                                
                                if (LocalTopicTest.IsValid):
                                    if (LocalTopicTest.IsParam):
                                        pPar:StatusParam
                                        pPar, retval = self.ServerListOfStatusParams.GetParam(LocalTopicTest.Param)
                                        if (retval):
                                            self.LogConsole(pPar.ParamName,ConsoleLogLevel.Test)    
                                            MyParamName = pPar.ParamName
                                            if (pPar.Util_Params_IsValid(LocalTopicTest.ParamVal)):
                                                
                                                NewVal = self.ServerListOfStatusParams.Util_Params_SetValue(pPar,LocalTopicTest.ParamVal)
                                                VarChanged = True 
                                                self.LogConsole(NewVal,ConsoleLogLevel.Test)    
                                                
                                    elif (LocalTopicTest.IsCommand):
                                        pCmd:ServiceCommand
                                        pCmd, retval = self.ServerListOfCommands.Get(LocalTopicTest.Param)
                                        if (retval):
                                            CurrCmd = pCmd.UserCmd
                                            CurrArgs = LocalTopicTest.Args

                                            CommandExecuted, CommandRetval, bAlsoReplyToTopic = self.Execute_Service_SpecificCommand(Command=CurrCmd,Args=CurrArgs, 
                                                                                                                                ReceivedMessage=ReceivedMessage,
                                                                                                                                AdditionaByteData=AdditionaByteData)
                                            
                                            LocalIsMessageAlreadyManaged = CommandExecuted
                                        
                                    elif (LocalTopicTest.IsReplyTo):
                                        print(ReceivedMessage.Message)
  
                                
                                    #Notify Changes Change Variable
                                    if (False):
                                        if ((VarChanged and MyParamName !="") or CommandExecuted):
                                            
                                            ObjToServer:Socket_Default_Message
                                            ObjToReplyTopic:Socket_Default_Message
                                            
                                            if (LocalTopicTest.IsParam):
                                                ObjToServer,ObjToReplyTopic = self.ServerListOfStatusParams.Util_Params_ConfimationMsg(ParamName=MyParamName,NewVal=NewVal
                                                                                                    ,AlsoReplyToTopic=bAlsoReplyToTopic
                                                                                                    ,ReplyToTopic=ReceivedMessage.ReplyToTopic)
                                            if (LocalTopicTest.IsCommand):
                                                ObjToServer,ObjToReplyTopic = self.ServerListOfCommands.Util_Command_ConfimationMsg(CommandName=MyParamName,CommandRetval=CommandRetval
                                                                                                    ,AlsoReplyToTopic=bAlsoReplyToTopic
                                                                                                    ,ReplyToTopic=ReceivedMessage.ReplyToTopic)
                                                
                                            
                                            if (ObjToServer): 
                                                self.LogConsole(ObjToServer.GetMessageDescription(),ConsoleLogLevel.CurrentTest)    
                                                #self.SendToServer(ObjToServer) 
                                            
                                            if (ObjToReplyTopic): 
                                                self.LogConsole(ObjToReplyTopic.GetMessageDescription(),ConsoleLogLevel.CurrentTest)    
                                                #self.SendToServer(ObjToReplyTopic) 
                                                
                                
                            

                            cv2.waitKey(1)        
                            ########################################################################################                        
                            ##FINE Gestione Messaggi Conosciuti dal server   
                            ########################################################################################   
                            
 
                    
                except Exception as e:
                    self.LogConsole(LocalMsgPrefix + " Error in handle() "  + str(e),ConsoleLogLevel.Error)
                    break
    

    def Execute_Service_SpecificCommand(self,Command:str,Args:str, ReceivedMessage:Socket_Default_Message,AdditionaByteData=b''):
        CommandExecuted = False
        CommandRetval=  ""
        bAlsoReplyToTopic = True
        
        ###################################################
        #Define Here Common Parent Commands
        ###################################################
        if (Command == self.LocalCommand_TESTSERVER):
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
    
        
    # Receiving / Listening Function
    def WaitingForNewClient(self):
        
        self.LogConsole("Waiting for Clients...",ConsoleLogLevel.Socket_Flow)
        i = 0
        
        try:
            
            while True:
                # Accept Connection
                try:
                    client, address = self.ServerConnection.accept()
                except Exception as e:
                    self.LogConsole(self.ThisServiceName() + " Error in ServerConnection.accept(): may be a server is already running "  + str(e)+ " " + str(i),ConsoleLogLevel.Error)     
                
            
                self.LogConsole("Connected with {}".format(str(address)),ConsoleLogLevel.Socket_Flow)
                
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.LOGIN,
                                                                          Message=Socket_ClientServer_Local_Commands.SOCKET_LOGIN_MSG)
             
                self.SendToClient(TargetClient=client,MyMsg=ObjToSend,From=str(address))
              
                
                # Request And Store servicename
                ReceivedEnvelope:SocketMessageEnvelope
                ReceivedEnvelope, AdditionaByteData, retval = self.GetFromClient(client)
             
                
                #self.LogConsole("Server GetFromClient " + ReceivedEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
                
                if (ReceivedEnvelope != None):
                    
                    if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                    
                        
                        ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                        
                        if (ReceivedMessage.Topic == Socket_Default_Message_Topics.LOGIN):
                            
                            servicename = ReceivedMessage.Message
                            self.LogConsole(" New Service Name is {}".format(servicename),ConsoleLogLevel.Socket_Flow,ConsoleLogLevel.Show)
                            
                            #if (not self.CheckIfServiceNameExists(servicename)):
                                                    
                            myclient_object = client_object(client,servicename,address)
                            self.client_objects.append(myclient_object)
                                            

                            # Start Handling Thread For Client
                            thread = threading.Thread(target=self.handle, args=(client,))
                            thread.start()
                              
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + " Error in WaitingForNewClient() "  + str(e)+ " " + str(i),ConsoleLogLevel.Error) 
        
    #Scheduled for paralell actions
    def Server_Main_Cycle(self):
        
        while True and not self.IsQuitCalled:
            time.sleep(self.SERVER_MAIN_CYCLE_SLEEP)
           
            self.LogConsole("Server_Main_Cycle",ConsoleLogLevel.Test)

           
    ########################################################################################                        
    ##Gestione TOPICS
    ########################################################################################  
    def Specific_Topic_Management_INPUT_TEXT_COMMAND(self,ReceivedMessage:Socket_Default_Message,CurrClientObject:client_object, AdditionalData = b''):
        
        self.LogConsole("Receiving Command Text Data " +  ReceivedMessage.Message, ConsoleLogLevel.CurrentTest)
        
        #NEW MNG
        #Check if local command
        pCmd:ServiceCommand
        CommandExecuted = False
        CommandRetval = ""
        pCmd, retval = self.ServerListOfCommands.Get(ReceivedMessage.Message)
        if (retval):
            #Is Known Message
            self.LogConsole("Execute command..." + pCmd.UserCmd, ConsoleLogLevel.Test)
            CommandExecuted, CommandRetval = self.Execute_Listed_Command(ReceivedMessage=ReceivedMessage,pCmd=pCmd)
            if (not CommandExecuted):
                self.LogConsole("Not Executed", ConsoleLogLevel.Test)
            else:
                self.LogConsole("......" + CommandRetval, ConsoleLogLevel.Test)
                if (CommandExecuted):
                    if (pCmd.GiveFeedback):
                        self.LogConsole("Give feedback...", ConsoleLogLevel.Test)
                        
                        ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = ReceivedMessage.ReplyToTopic ,Message=CommandRetval)
                        
                        self.LogConsole("SendToClient " +  ReceivedMessage.ReplyToTopic, ConsoleLogLevel.Test)
                        self.SendToClient(CurrClientObject.client,ObjToSend)  
    
    if (False):
        GlobalTextCommandsManagement = Socket_Logic_GlobalTextCmdMng()
        AnyFound, MsgsToSend = GlobalTextCommandsManagement.ParseCommandAndGetMsgs(ReceivedMessage)
        
        if (AnyFound):
            ObjToSend:Socket_Default_Message
            for ObjToSend in MsgsToSend:
                # if (ObjToSend.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD):
                #     self.PassThroughtMsg(ObjToSend,AdditionalData)
                if (ObjToSend.Topic == Socket_Default_Message_Topics.SERVER_LOCAL):
                    self.LogConsole(self.ThisServiceName() + " " + ObjToSend.GetMessageDescription(),ConsoleLogLevel.Always)
                    self.Specific_Topic_Management_SERVER_LOCAL(ReceivedMessage=ObjToSend,CurrClientObject=CurrClientObject, AdditionalData=AdditionalData)
                else:                
                    self.LogConsole(self.ThisServiceName() + " " + ObjToSend.GetMessageDescription(),ConsoleLogLevel.Always)
                    self.BroadCastMessageByTopic(ObjToSend,AdditionaByteData=AdditionalData)

 
    def Execute_Listed_Command(self,ReceivedMessage:Socket_Default_Message,pCmd:ServiceCommand):
        self.LogConsole(f"Execute_Listed_Command Msg:{ReceivedMessage.Message} Cmd:{pCmd.UserCmd} Alt:{pCmd.AltCommand.lower()}", ConsoleLogLevel.Test)
        co:client_object
        try:
            CommandExecuted = False
            CommandRetval = ""
            Msg = ReceivedMessage.Message.lower()
            #XYZ
            if (pCmd.UserCmd==ServerLocalCommands.GET_HELP): #like get commands
                CommandRetval = self.ServerListOfCommands.GetDescription() + "\n"              
                CommandExecuted = True

            elif (pCmd.UserCmd==ServerLocalCommands.GET_TOPICS):
                CommandRetval = ""
                for co in self.client_objects:
                    CommandRetval += co.ShowDetails()   
                CommandExecuted = True

            elif (pCmd.UserCmd==ServerLocalCommands.GET_COMMANDS):
                CommandRetval = self.ServerListOfCommands.GetDescription() + "\n"              
                CommandExecuted = True
            
            elif (pCmd.UserCmd==ServerLocalCommands.GET_STATUS):
                CommandRetval = self.ServerListOfStatusParams.GetDescription() + "\n"           
                CommandExecuted = True
            
            elif (pCmd.UserCmd==ServerLocalCommands.GET_CLIENTS):
                CommandRetval = ""
                for co in self.client_objects:
                    CommandRetval += co.servicename + "\n"              
                CommandExecuted = (len(CommandRetval)>0)
                
            elif (pCmd.UserCmd==ServerLocalCommands.GET_SENSORS):
                CommandRetval = ""
                sns:Socket_Default_Message
                for sns in self.MyListOfSensors:
                    CommandRetval += PaddingTuples((f"{sns.Topic}:",40),(f"{sns.Value}",10),(f"{sns.Message}\n",1))           
                CommandExecuted = (len(CommandRetval)>0)
                
            elif (pCmd.UserCmd==ServerLocalCommands.SHOW_SERVER_MSGS):
                NewVal = self.ServerListOfStatusParams.SwitchParam(ServerLocalParamNames.SERVER_SHOW_RECEIVED_MSGS)
                CommandRetval =f"SHOW_RECEIVED_MSGS is {NewVal}\n"
                NewVal = self.ServerListOfStatusParams.SwitchParam(ServerLocalParamNames.SERVER_SHOW_SEND_MSGS)
                CommandRetval += f"SERVER_SHOW_SEND_MSGS is {NewVal}\n"
                CommandExecuted = True
            
            elif (pCmd.UserCmd==ServerLocalCommands.SHOW_SERVER_IMAGE):
                NewVal = self.ServerListOfStatusParams.SwitchParam(ServerLocalParamNames.SERVER_CAMERA)
                CommandRetval = f"SERVER_CAMERA is {NewVal}\n"
                CommandExecuted = True
                
            return CommandExecuted, CommandRetval    
        
        except Exception as e:
            self.LogConsole("Error in Execute_Listed_Command()  " + str(e),ConsoleLogLevel.Error)
            return False,""
            
    def Specific_Topic_Management_INPUT_IMAGE(self,ReceivedMessage:Socket_Default_Message, AdditionalData = b''):
        self.LogConsole("Receiving Image Data " + str(len(AdditionalData)),ConsoleLogLevel.Test)
        self.LogConsole("Detection List " + str(ReceivedMessage.ResultList),ConsoleLogLevel.Test)
        if (len(AdditionalData)>0):
            if (self.ServerListOfStatusParams.CheckParam(ServerLocalParamNames.SERVER_CAMERA,StatusParamListOfValues.ON)):
                frame= pickle.loads(AdditionalData, fix_imports=True, encoding="bytes")
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)  
                self.FrameName = ReceivedMessage.Message
                self.MyFramesName.append(self.FrameName)
                try:
                    cv2.imshow(self.FrameName,frame)
                    cv2.setWindowProperty(self.FrameName, cv2.WND_PROP_TOPMOST, 1)
                except:
                    cv2.destroyAllWindows()
            else:
                cv2.destroyAllWindows()
        else:
            cv2.destroyAllWindows()
    
    def Specific_Topic_Management_SENSOR(self,ReceivedMessage:Socket_Default_Message, AdditionalData = b''): 

        found = False
        if (    ReceivedMessage.Topic == Socket_Default_Message_Topics.SENSOR_BATTERY
            or  ReceivedMessage.Topic == Socket_Default_Message_Topics.SENSOR_COMPASS
            or ReceivedMessage.Topic== Socket_Default_Message_Topics.INPUT_LIDAR_MIN_DISTANCE
            or ReceivedMessage.Topic== Socket_Default_Message_Topics.INPUT_LIDAR_BEST_WAYOUT_DIR):
            pSensor:Socket_Default_Message
            for pSensor in self.MyListOfSensors:
                if (pSensor.Topic == ReceivedMessage.Topic):
                    found = True
                    pSensor.Copy(ReceivedMessage)
                    break
            if (not found):
                self.MyListOfSensors.append(ReceivedMessage)

    
    
    def Run_Threads(self):
        simul_thread = threading.Thread(target=self.WaitingForNewClient)
        simul_thread.start()
        
        Server_Main_Cycle_thread = threading.Thread(target=self.Server_Main_Cycle)
        Server_Main_Cycle_thread.start()
        
if (__name__== "__main__"):
    
        
    MyServer = Socket_Server()
    MyServer.Run_Threads()
    
   