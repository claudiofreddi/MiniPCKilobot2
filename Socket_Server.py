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

from Socket_Struct_ListOfParams import * 
from Socket_Struct_ListOfCommands import *
from Socket_Struct_ListOfSensors import *
from Socket_Logic_Topics import * 
#from Socket_Server_Commands import * 
import subprocess

class ServerLocalCommands:

    GET_HELP = "?"
    GET_TOPICS = "get topics"
    GET_PARAMS = "get params"
    GET_CLIENTS = "get clients"
    GET_SENSORS = "get sensors"
    GET_COMMANDS = "get commands"
    SHOW_SERVER_MSGS = "togglemsgs"
    SHOW_SERVER_IMAGE = "toggleimage"
    RUN_CLIENT = "run client"
    QUIT_ALL_CLIENTS = "quit all"
    GET_IPADDRESS = "get ip"
    SPEAK_TEXT = "speak"
        

class ServerLocalParamNames:
    SERVER_CAMERA = "SERVER_CAMERA" 
    SERVER_SHOW_RECEIVED_MSGS = "SERVER_SHOW_RECEIVED_MSGS"
    SERVER_SHOW_SEND_MSGS = "SERVER_SHOW_SEND_MSGS"

import cv2

class Socket_Server(Socket_ClientServer_BaseClass): 

    #Keep Global for handle() 
    client_objects = []

    #NEW MNG
    ServerListOfStatusParams = ServiceParamList(Socket_Services_List.SERVER)
    ServerListOfCommands = ServiceCommandList(Socket_Services_List.SERVER)   
    ServerSensorList = SensorList(Socket_Services_List.SERVER)
    
    def __init__(self,ServiceName = Socket_Services_List.SERVER, ForceServerIP = '',ForcePort='',LogOptimized=False):
        super().__init__(ServiceName,ForceServerIP,ForcePort, True,LogOptimized)
        
        self.RunOptimized = LogOptimized
        self.FrameName = 'server'
        self.SERVER_MAIN_CYCLE_SLEEP = 5 #sec
        #self.ServerSensorList = SensorList(ThisServiceName=ServiceName)
        self.MyFramesName = []
        

        
        #NEW MNG
        # define for Server
        self.Standard_Topics_For_Server = Topics_Standard_For_Service(self.ServiceName)
       
        #XYZ
        #Command Definition
        self.ServerListOfCommands.CreateCommand(ServiceName=ServiceName,Name=ServerLocalCommands.GET_HELP)
        self.ServerListOfCommands.CreateCommand(ServiceName=ServiceName,Name=ServerLocalCommands.GET_CLIENTS)
        self.ServerListOfCommands.CreateCommand(ServiceName=ServiceName,Name=ServerLocalCommands.GET_TOPICS,AltCommand="ctrl+T")
        self.ServerListOfCommands.CreateCommand(ServiceName=ServiceName,Name=ServerLocalCommands.GET_PARAMS,AltCommand="ctrl+T")
        self.ServerListOfCommands.CreateCommand(ServiceName=ServiceName,Name=ServerLocalCommands.GET_COMMANDS)
        self.ServerListOfCommands.CreateCommand(ServiceName=ServiceName,Name=ServerLocalCommands.GET_SENSORS)
        self.ServerListOfCommands.CreateCommand(ServiceName=ServiceName,Name=ServerLocalCommands.SHOW_SERVER_MSGS,AltCommand="ctrl+M")
        self.ServerListOfCommands.CreateCommand(ServiceName=ServiceName,Name=ServerLocalCommands.SHOW_SERVER_IMAGE,AltCommand="ctrl+I")
        self.ServerListOfCommands.CreateCommand(ServiceName=ServiceName,Name=ServerLocalCommands.RUN_CLIENT, ArgDescr="servicecommandkey")
        self.ServerListOfCommands.CreateCommand(ServiceName=ServiceName,Name=ServerLocalCommands.GET_IPADDRESS, ArgDescr="")
        self.ServerListOfCommands.CreateCommand(ServiceName=ServiceName,Name=ServerLocalCommands.SPEAK_TEXT,ArgDescr="Text to speak")
        
        self.ServerListOfStatusParams.CreateOrUpdateParam(ServiceName=ServiceName
                                                          ,Name=ServerLocalParamNames.SERVER_CAMERA
                                                          ,Value=StatusParamListOfValues.ON
                                                          ,ArgDescr="on|off")
         
        self.ServerListOfStatusParams.CreateOrUpdateParam(ServiceName=ServiceName
                                                        ,Name=ServerLocalParamNames.SERVER_SHOW_RECEIVED_MSGS
                                                        ,Value=StatusParamListOfValues.OFF
                                                        ,ArgDescr="on|off")
        
        self.ServerListOfStatusParams.CreateOrUpdateParam(ServiceName=ServiceName
                                                          ,Name=ServerLocalParamNames.SERVER_SHOW_SEND_MSGS
                                                          ,Value=StatusParamListOfValues.OFF
                                                          ,ArgDescr="on|off")

        self.Connect()    


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

            #self.LogConsole("Server SendToClient [" + ToServiceName + "]: " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow,LogParam)
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
                #self.LogConsole("Server GetFromClient [" + FromServiceName + "] " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow,LogParam)
                
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
                return c, True
        return None, False
    
    
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
                        self.client_objects.remove(CurrClientObject)
                        self.LogConsole(LocalMsgPrefix + " handle() Evelope Not Correct. Assume Break Connection. Quit.",ConsoleLogLevel.System)
                        break
                    else:
                        if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                            
                            
                            ReceivedMessage = ReceivedEnvelope.GetReceivedMessage()
                            NeedReply = False
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
                                #self.LogConsole("SN:" + CurrClientObject.servicename +  " Name:" + ReceivedMessage.Message + " VAL:" + ReceivedMessage.ValueStr + " Args:" + ReceivedMessage.ValueStr3,ConsoleLogLevel.CurrentTest)
                                self.ServerListOfStatusParams.CreateOrUpdateParam(ServiceName=ReceivedMessage.ValueStr2
                                                                                  ,Name=ReceivedMessage.Message
                                                                                  ,Value=ReceivedMessage.ValueStr
                                                                                  ,ArgDescr=ReceivedMessage.ValueStr3)
                            
                            elif (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_COMMAND_SERVER_REGISTER):   
                                self.ServerListOfCommands.CreateCommand(ServiceName=ReceivedMessage.ValueStr2
                                                                        ,Name=ReceivedMessage.Message
                                                                        ,ArgDescr=ReceivedMessage.ValueStr3
                                                                        ,AltCommand=ReceivedMessage.ValueStr
                                                                        ,GiveFeedback=ReceivedMessage.Value)
                                

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
                                CommandExecuted, CommandRetval = self.Execute_Listed_Command(ReceivedMessage=ReceivedMessage
                                                                                             ,CommandName=ReceivedMessage.Message
                                                                                             ,Args=""
                                                                                             ,CommandFromServiceName=ReceivedEnvelope.From)
                                NeedReply = True
                                
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

                                
                                #self.LogConsole("*" + LocalTopicTest.Describe(),ConsoleLogLevel.CurrentTest)
                                
                                if (LocalTopicTest.IsValid):
                                    if (LocalTopicTest.TargetService == "" or LocalTopicTest.TargetService == Socket_Services_List.SERVER):
                                        if (LocalTopicTest.IsParam):
                                            pPar:ServiceParam
                                            pPar, retval = self.ServerListOfStatusParams.GetByGlobalName(LocalTopicTest.TargetService + "_" + LocalTopicTest.Param)
                                            if (retval):
                                                self.LogConsole(pPar.Name,ConsoleLogLevel.Test)    
                                                if (pPar.Util_Params_IsValid(LocalTopicTest.ParamVal)):
                                                    NewVal = self.ServerListOfStatusParams.Util_Params_SetValue(pPar,LocalTopicTest.ParamVal)
                                                    CommandRetval = f"{LocalTopicTest.Param} new value: {NewVal}"
                                                    self.LogConsole(NewVal,ConsoleLogLevel.Test)    
                                                    
                                        elif (LocalTopicTest.IsCommand):
                                            pCmd:ServiceCommand
                                            print( LocalTopicTest.Command)
                                            pCmd, retval = self.ServerListOfCommands.GetByGlobalName(LocalTopicTest.TargetService + "_" + LocalTopicTest.Command)
                                            print(retval, " ", LocalTopicTest.Command)
                                            if (retval):
                                                CommandExecuted, CommandRetval = self.Execute_Listed_Command(ReceivedMessage=ReceivedMessage
                                                                                                             ,CommandName=pCmd.Name
                                                                                                             ,Args=LocalTopicTest.Args
                                                                                                             ,CommandFromServiceName=ReceivedEnvelope.From)
                                                if (not CommandExecuted): CommandRetval = f"Command {pCmd.Name} failed: {CommandRetval} !"
                                            
                                        elif (LocalTopicTest.IsReplyTo):
                                            print(ReceivedMessage.Message)

                                        if (LocalTopicTest.TargetService == Socket_Services_List.SERVER):
                                        #if (False):
                                            ReplyTopicTest = TopicManager(ReceivedMessage.ReplyToTopic)
                                            
                                            #self.LogConsole("*" + ReplyTopicTest.Describe(),ConsoleLogLevel.CurrentTest)
                                            
                                            if (ReplyTopicTest.IsValid):
                                                c:client_object
                                                c, retval = self.GetClientObjectByServiceName(ReplyTopicTest.TargetService)
                                                if (retval):  #do not send to SERVER itself
                                                    ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic=ReceivedMessage.ReplyToTopic
                                                                                                              ,Message=CommandRetval)
                                                    self.LogConsole("*SendToClient " +  ReplyTopicTest.TargetService, ConsoleLogLevel.CurrentTest)
                                                    self.SendToClient(c.client,ObjToSend)  
                                                
                            if (NeedReply): #For Text Commands
                                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = ReceivedMessage.ReplyToTopic ,Message=CommandRetval)
                                #self.LogConsole("SendToClient " +  ReceivedMessage.ReplyToTopic, ConsoleLogLevel.Test)
                                self.SendToClient(CurrClientObject.client, ObjToSend)
                        

                            cv2.waitKey(1)        
                            ########################################################################################                        
                            ##FINE Gestione Messaggi Conosciuti dal server   
                            ########################################################################################   
                            
 
                    
                except Exception as e:
                    self.LogConsole(LocalMsgPrefix + " Error in handle() "  + str(e),ConsoleLogLevel.Error)
                    break
    

        
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

           

    def Execute_Listed_Command(self,ReceivedMessage:Socket_Default_Message,CommandName="", Args="", CommandFromServiceName=""):
        self.LogConsole(f"Execute_Listed_Command Msg:{CommandName}", ConsoleLogLevel.CurrentTest)
        
        CheckCommand = CommandName.split('/')
        CommandName = CheckCommand[0]
        if (len(CheckCommand)>1): Args = CheckCommand[1]
            
        co:client_object
        
        if (CommandName == ""): return False,"Command not set"
        
        try:
            CommandExecuted = False
            CommandRetval = ""
            Msg = ReceivedMessage.Message.lower()
            #XYZ
            if (CommandName==ServerLocalCommands.GET_HELP): #like get commands
                CommandRetval = self.ServerListOfCommands.GetDescription() + "\n"              
                CommandExecuted = True

            elif (CommandName==ServerLocalCommands.GET_TOPICS):
                CommandRetval = ""
                for co in self.client_objects:
                    CommandRetval += co.ShowDetails()   
                CommandExecuted = True

            elif (CommandName==ServerLocalCommands.GET_COMMANDS):
                CommandRetval = self.ServerListOfCommands.GetDescription() + "\n"              
                CommandExecuted = True
            
            elif (CommandName==ServerLocalCommands.GET_PARAMS):
                CommandRetval = self.ServerListOfStatusParams.GetDescription() + "\n"           
                CommandExecuted = True
            
            elif (CommandName==ServerLocalCommands.GET_CLIENTS):
                CommandRetval = ""
                for co in self.client_objects:
                    CommandRetval += co.servicename + "\n"              
                CommandExecuted = (len(CommandRetval)>0)
                
            elif (CommandName==ServerLocalCommands.GET_SENSORS):
                CommandRetval = self.ServerSensorList.GetDescription() 
                CommandExecuted = (len(CommandRetval)>0)
                
            elif (CommandName==ServerLocalCommands.SHOW_SERVER_MSGS):
                NewVal = self.ServerListOfStatusParams.SwitchParam(ServerLocalParamNames.SERVER_SHOW_RECEIVED_MSGS)
                CommandRetval =f"SHOW_RECEIVED_MSGS is {NewVal}\n"
                NewVal = self.ServerListOfStatusParams.SwitchParam(ServerLocalParamNames.SERVER_SHOW_SEND_MSGS)
                CommandRetval += f"SERVER_SHOW_SEND_MSGS is {NewVal}\n"
                CommandExecuted = True
            
            elif (CommandName==ServerLocalCommands.SHOW_SERVER_IMAGE):
                NewVal = self.ServerListOfStatusParams.SwitchParam(ServerLocalParamNames.SERVER_CAMERA)
                CommandRetval = f"SERVER_CAMERA is {NewVal}\n"
                CommandExecuted = True
                
            elif (CommandName==ServerLocalCommands.GET_IPADDRESS): 
                CommandRetval = f"SERVER address:port is {self.ServerIP}:{self.ServerPort}\n"
                CommandExecuted = True 
                
            elif (CommandName == ServerLocalCommands.QUIT_ALL_CLIENTS):
                for co in self.client_objects:
                    if (co.servicename != CommandFromServiceName): #Do not quit the caller
                        Topic = f"/@{co.servicename}/#cmd#/quit"
                        ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Topic ,Message="quitted")
                        self.SendToClient(co.client, ObjToSend)
                        CommandRetval += co.servicename + " quitted\n"   
                
            elif (CommandName == ServerLocalCommands.SPEAK_TEXT):
                
                Topic = Socket_Default_Message_Topics.OUTPUT_SPEAKER
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Topic ,Message=Args)
                self.BroadCastMessageByTopic(ReceivedMessage=ObjToSend,AdditionaByteData=b'')
                CommandRetval = ""
                CommandExecuted = True
                
            elif (CommandName == ServerLocalCommands.RUN_CLIENT):
                print("Run  " + Args)
                for obj in RunnableClients:
                    #(commandkey, filename, servocename, mode)
                    if (obj[0] == Args and obj[3] != ExecMode.Disabled ):
                        c:client_object
                        c, retval  =  self.GetClientObjectByServiceName(obj[2])
                        if (not retval):
                            Thiscreationflags= 0 
                            if (obj[3] == ExecMode.OpenNewConsole): Thiscreationflags = subprocess.CREATE_NEW_CONSOLE 
                            subprocess.Popen(args=[PYTHON_EXEC_PATH ,obj[1]],shell = False, creationflags=Thiscreationflags)
                            CommandRetval=  f"{Args} launched !"
                            CommandExecuted = True
                        else:
                            CommandRetval=  f"{Args} already running !"
                            CommandExecuted = False
                
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
            
            
            pSens, retval = self.ServerSensorList.Get(ReceivedMessage.Topic)
            if (retval):
                pSens.Update(ReceivedMessage.Value)
            else:
                self.ServerSensorList.Append(SensorTopic=ReceivedMessage.Topic,Value=ReceivedMessage.Value)
            
  
    
    def Run_Threads(self):
        simul_thread = threading.Thread(target=self.WaitingForNewClient)
        simul_thread.start()
        
        Server_Main_Cycle_thread = threading.Thread(target=self.Server_Main_Cycle)
        Server_Main_Cycle_thread.start()
        
if (__name__== "__main__"):
    
        
    MyServer = Socket_Server()
    MyServer.Run_Threads()
    
   