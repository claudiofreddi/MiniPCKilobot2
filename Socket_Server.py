import socket

import threading
import time
from Robot_Envs import * 
from Socket_Struct_ClientServer_BaseClass import * 
from Socket_Struct_Messages import * 
from Socket_Struct_Client_Object import *
from Socket_Logic_GlobalTextCmdMng import *
from Socket_Struct_Server_Robot_Commands import *
from PIL import Image

from Socket_Struct_Server_StatusParamList import * 

import cv2


class Socket_Server(Socket_ClientServer_BaseClass): 


    client_objects = []
        
    # SensorMessage List 
    MyListOfSensors = []
    
    
    def __init__(self,ServiceName = Socket_Services_List.SERVER, ForceServerIP = '',ForcePort='',LogOptimized=False):
        super().__init__(ServiceName,ForceServerIP,ForcePort, True,LogOptimized)
        self.RunOptimized = LogOptimized
        
        
        self.MyListOfStatusParams = StatusParamList()
        self.MyListOfStatusParams.UpdateParam(StatusParamName.SERVER_CAMERA,StatusParamListOfValues.ON) 
        self.MyListOfStatusParams.UpdateParam(StatusParamName.SERVER_SHOW_RECEIVED_MSGS,StatusParamListOfValues.OFF) 
        self.MyListOfStatusParams.UpdateParam(StatusParamName.SERVER_SHOW_SEND_MSGS,StatusParamListOfValues.OFF) 
          
        
        self.Connect()    


    def SendToClient(self,TargetClient, MyMsg:Socket_Default_Message,From='',AdditionaByteData=b''): 
        c:client_object
        try:
            c , retval = self.GetClientObject(TargetClient)
            ToServiceName = c.servicename if (retval) else ''
            
            MyEnvelope:SocketMessageEnvelope = self.Prepare_StandardEnvelope(MsgToSend=MyMsg,To=ToServiceName,From=self.ServiceName)
            SerializedObj = self.Pack_Envelope_And_Serialize(MyEnvelope)
            
            self.MySocket_SendReceive.send_msg(TargetClient,SerializedObj,AdditionaByteData)
            
            if (self.MyListOfStatusParams.CheckParam(StatusParamName.SERVER_SHOW_SEND_MSGS,StatusParamListOfValues.ON)):
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
          
            FromServiceName = c.servicename if (retval) else ''


            ser_obj,AdditionaByteData,retval = self.MySocket_SendReceive.recv_msg(TargetClient)
                
            MyEnvelope = self.UnPack_StandardEnvelope_And_Deserialize(ser_obj)
            
            if (self.MyListOfStatusParams.CheckParam(StatusParamName.SERVER_SHOW_RECEIVED_MSGS,StatusParamListOfValues.ON)):
                LogParam = ConsoleLogLevel.Show
            else:
                LogParam = 0
            self.LogConsole("Server GetFromClient [" + FromServiceName + "] " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow,LogParam)
            
            return MyEnvelope,AdditionaByteData ,True 

        except Exception as e:
            if (TargetClient):
                self.QuitClient(TargetClient,True)
            
            self.LogConsole("Server Error in GetFromClient " + str(e),ConsoleLogLevel.Error)
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
                    self.broadcastObj(ObjToSend)
        
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
                #if (c.servicename != CurrClientObject.servicename):
                if (c.IsSubscribedToThisTopic(ReceivedMessage.Topic)):
                    self.SendToClient(TargetClient=c.client,MyMsg=ReceivedMessage,From= Socket_Services_List.SERVER,AdditionaByteData=AdditionaByteData)
    
    #Direct Messages to Specific Client    
    def PassThroughtMsg(self, ReceivedMessage:Socket_Default_Message,AdditionaByteData=b''):
        try:
            c:client_object
            if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD):
                
                if (ReceivedMessage.TargetClientName != Socket_Default_Message_Topics.NONE 
                    and ReceivedMessage.TargetClientName != ""):
                    c = self.GetClientObjectByServiceName(ReceivedMessage.TargetClientName)
                    if (c):
                        self.SendToClient(TargetClient=c.client,MyMsg=ReceivedMessage,From=Socket_Services_List.SERVER,AdditionaByteData=AdditionaByteData)

        except Exception as e:
            self.LogConsole("Server Error in broadcastObj() " + str(e),ConsoleLogLevel.Error)                  
                
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
                            
                            if (self.MyListOfStatusParams.CheckParam(StatusParamName.SERVER_SHOW_RECEIVED_MSGS,StatusParamListOfValues.ON)):
                                LogParam = ConsoleLogLevel.Show
                            else:
                                LogParam = 0

                            self.LogConsole("Server GetFromClient [" + CurrClientObject.servicename + "] " + ReceivedMessage.GetMessageDescription(),ConsoleLogLevel.Socket_Flow,LogParam )                
                                        
                            ########################################################################################                        
                            ##Gestione Inoltro Messaggi  
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
                             
                            ## SEZIONE MESSAGGI SPECIALI
                       
                            if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_ADD):
                                if (CurrClientObject.RegisterTopic(ReceivedMessage.Message)):
                                    self.LogConsole("[" + CurrClientObject.servicename +  "]  Added Topic [" + ReceivedMessage.Message + "]",ConsoleLogLevel.System)
                            
                            elif (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_SUBSCRIBE):
                                if (CurrClientObject.SubscribeTopic(ReceivedMessage.Message)):
                                    self.LogConsole("[" + CurrClientObject.servicename +  "] Subscribed to Topic [" + ReceivedMessage.Message + "]",ConsoleLogLevel.System)
                                    
                            elif (ReceivedMessage.Message == self.SOCKET_QUIT_MSG):
                                self.LogConsole("[" + CurrClientObject.servicename +  "] Quitted ",ConsoleLogLevel.System)
                                self.QuitClient(client)
                                break
                            
                            elif (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_STANDBY_ACK):
                                ParamName = ReceivedMessage.Message #self.ServiceName + StatusParamName.THIS_SERVICE_IS_IDLE
                                ParamValueStr = ReceivedMessage.ValueStr
                                self.LogConsole("[" + ParamName +  "] Received ACK: [" + ParamValueStr + "]",ConsoleLogLevel.System)
                                self.MyListOfStatusParams.UpdateParam(ParamName,ParamValueStr) 
                            
                            elif (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD):
                                print("A")
                                self.PassThroughtMsg(ReceivedMessage,AdditionaByteData)
                                                                                           
                            ##SocketObjectClassType.SENSOR : value update      
                            elif (   ReceivedMessage.Topic== Socket_Default_Message_Topics.SENSOR_COMPASS
                                or ReceivedMessage.Topic== Socket_Default_Message_Topics.SENSOR_BATTERY):
                                self.Specific_Topic_Management_SENSOR(ReceivedMessage=ReceivedMessage)            
                                                           
                            elif ((ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_KEYBOARD and ReceivedMessage.Value==0)
                                 or ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_TELEGRAM
                                 or ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_TEXT_COMMANDS
                                 or ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_JOYSTICK
                                 ):
                                #self.Specific_Topic_Management_INPUT_KEYBOARD(ReceivedMessage=ReceivedMessage)    
                                self.Specific_Topic_Management_INPUT_TEXT_COMMAND(ReceivedMessage=ReceivedMessage,CurrClientObject=CurrClientObject,AdditionalData=AdditionaByteData)
        
                            elif (ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_IMAGE):
                                self.Specific_Topic_Management_INPUT_IMAGE(ReceivedMessage=ReceivedMessage,AdditionalData=AdditionaByteData)
     
                            cv2.waitKey(1)
                                    
                            ########################################################################################                        
                            ##FINE Gestione Messaggi Conosciuti dal server   
                            ########################################################################################   
                            
 
                    
                except Exception as e:
                    self.LogConsole(LocalMsgPrefix + " Error in handle() "  + str(e),ConsoleLogLevel.Error)
                    try:
                        self.QuitClient(client)
                    except:
                        self.LogConsole(LocalMsgPrefix + " handle() Error. Assume Break Connection. Quit.",ConsoleLogLevel.System)
                        break
                    self.LogConsole(LocalMsgPrefix + " handle() Error. Assume Break Connection. Quit.",ConsoleLogLevel.System)
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
                                                                          Message=self.SOCKET_LOGIN_MSG)
             
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
                            #else:
                            #    client.close()
                            #    self.LogConsole(" Service Name {} Already Exists. Connection Refused".format(servicename),ConsoleLogLevel.Socket_Flow,ConsoleLogLevel.Show)
                                
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + " Error in WaitingForNewClient() "  + str(e)+ " " + str(i),ConsoleLogLevel.Error) 
        
            
    def Server_BroadCast_Simulation(self):
        tick = 0
        self.LogConsole(self.ThisServiceName() +  " Server_BroadCast_Simulation Enabled",ConsoleLogLevel.Socket_Flow)
        while True:
            time.sleep(3)
            
            message = self.ThisServiceName() +  "SIMULATED Broadcast tick: " + str(tick)            
            ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.MESSAGE,
                                                                      Message=message)
            
            # s = self.GetClientObjectByServiceName(Socket_Services_List.REMOTE)
            # if (s != None):
            #     self.SendToClient(s,ObjToSend)

            count = self.broadcastObj(ObjToSend)
            if (count>0):                
                self.LogConsole(message,ConsoleLogLevel.Socket_Flow)
            
            
            tick = tick + 1
            
    ########################################################################################                        
    ##Gestione TOPICS
    ########################################################################################  
    def Specific_Topic_Management_INPUT_TEXT_COMMAND(self,ReceivedMessage:Socket_Default_Message,CurrClientObject:client_object, AdditionalData = b''):
        
        self.LogConsole("Receiving Command Text Data " +  ReceivedMessage.Message, ConsoleLogLevel.Test)
        
        GlobalTextCommandsManagement = Socket_Logic_GlobalTextCmdMng()
        AnyFound, MsgsToSend = GlobalTextCommandsManagement.ParseCommandAndGetMsgs(ReceivedMessage)
        
        if (AnyFound):
            ObjToSend:Socket_Default_Message
            for ObjToSend in MsgsToSend:
                if (ObjToSend.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD):
                    self.PassThroughtMsg(ObjToSend,AdditionalData)
                if (ObjToSend.Topic == Socket_Default_Message_Topics.SERVER_LOCAL):
                    self.LogConsole(self.ThisServiceName() + " " + ObjToSend.GetMessageDescription(),ConsoleLogLevel.Always)
                    self.Specific_Topic_Management_SERVER_LOCAL(ReceivedMessage=ObjToSend,CurrClientObject=CurrClientObject, AdditionalData=AdditionalData)
                else:                
                    self.LogConsole(self.ThisServiceName() + " " + ObjToSend.GetMessageDescription(),ConsoleLogLevel.Always)
                    self.BroadCastMessageByTopic(ObjToSend,AdditionaByteData=AdditionalData)

 

            
    def Specific_Topic_Management_INPUT_IMAGE(self,ReceivedMessage:Socket_Default_Message, AdditionalData = b''):
        self.LogConsole("Receiving Image Data " + str(len(AdditionalData)),ConsoleLogLevel.Test)
        self.LogConsole("Detection List " + str(ReceivedMessage.ResultList),ConsoleLogLevel.Test)
        if (len(AdditionalData)>0):
            if (self.MyListOfStatusParams.CheckParam(StatusParamName.SERVER_CAMERA,StatusParamListOfValues.ON)):
                frame= pickle.loads(AdditionalData, fix_imports=True, encoding="bytes")
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)  
                try:
                    cv2.imshow('server',frame)
                    cv2.setWindowProperty('server', cv2.WND_PROP_TOPMOST, 1)
                except:
                    cv2.destroyAllWindows()
            else:
                cv2.destroyAllWindows()
    
   
    def Specific_Topic_Management_SERVER_LOCAL(self,ReceivedMessage:Socket_Default_Message,CurrClientObject:client_object, AdditionalData = b''): 
        
        
        BackToClientMsg = ""
        co:client_object
        if (ReceivedMessage.Message == RobotListOfAvailableCommands.CTRL_M): #Ctrl + M (Alle Messages about send and receive)
            NewVal = self.MyListOfStatusParams.SwitchParam(StatusParamName.SERVER_SHOW_RECEIVED_MSGS)
            BackToClientMsg =f"SHOW_RECEIVED_MSGS is {NewVal}"
            self.LogConsole(BackToClientMsg,ConsoleLogLevel.System) 
            
            NewVal = self.MyListOfStatusParams.SwitchParam(StatusParamName.SERVER_SHOW_SEND_MSGS)
            BackToClientMsg =f"SHOW_SEND_MSGS is {NewVal}"
            self.LogConsole(BackToClientMsg,ConsoleLogLevel.System) 
            
        elif  (ReceivedMessage.Message == RobotListOfAvailableCommands.CTRL_T): 
            BackToClientMsg = ""
            for co in self.client_objects:
                BackToClientMsg += co.ShowDetails()
            
                    
        elif  (ReceivedMessage.Message == RobotListOfAvailableCommands.CTRL_I): #Ctrl + I (Image On Off)
            NewVal = self.MyListOfStatusParams.SwitchParam(StatusParamName.SERVER_CAMERA)
            BackToClientMsg = f"SERVER_CAMERA is {NewVal}"
            self.LogConsole(BackToClientMsg,ConsoleLogLevel.System) 
            

        elif  (ReceivedMessage.Message == RobotListOfAvailableCommands.CTRL_S): #Ctrl + S Param Status
            BackToClientMsg = self.MyListOfStatusParams.GetStatusDescription()
            self.LogConsole(BackToClientMsg,ConsoleLogLevel.Show)     

        elif  (ReceivedMessage.Message == Socket_Logic_GlobalTextCmdMng.GET_CLIENTS):
            BackToClientMsg = ""
            for co in self.client_objects:
                BackToClientMsg += co.servicename + "\n"
        
        elif  (ReceivedMessage.Message == Socket_Logic_GlobalTextCmdMng.GET_HELP1 or ReceivedMessage.Message == Socket_Logic_GlobalTextCmdMng.GET_HELP2):
            BackToClientMsg = ""
            Tmp = Socket_Logic_GlobalTextCmdMng()
            BackToClientMsg = Tmp.ShowCommands()
        
        else: ### ERROR
            BackToClientMsg = "Command not found: " +  ReceivedMessage.Message 
            self.LogConsole(BackToClientMsg , ConsoleLogLevel.System)           
                    
        #For TEST PORPOUSE
        if (BackToClientMsg!=""):
            if (ReceivedMessage.ReplyToTopic != Socket_Default_Message_Topics.NONE):
                TopicToUse = ReceivedMessage.ReplyToTopic 
            else:
                TopicToUse = Socket_Default_Message_Topics.OUTPUT_TEXT_COMMANDS
            
            ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = TopicToUse,Message=BackToClientMsg)
            
            self.LogConsole("SendToClient " +  BackToClientMsg, ConsoleLogLevel.Test)
            self.SendToClient(CurrClientObject.client,ObjToSend)  
    
    def Specific_Topic_Management_SENSOR(self,ReceivedMessage, AdditionalData = b''): 

        found = False
        if (    ReceivedMessage.Topic == Socket_Default_Message_Topics.SENSOR_BATTERY
            or  ReceivedMessage.Topic == Socket_Default_Message_Topics.SENSOR_COMPASS):
            pSensor:Socket_Default_Message
            for pSensor in self.MyListOfSensors:
                if (pSensor.Topic == ReceivedMessage.Topic):
                    found = True
                    pSensor.Copy(ReceivedMessage)
                    break
            if (not found):
                self.MyListOfSensors.append(ReceivedMessage)
    
    #######################################################################################                        
    ##Gestione TOPICS
    ########################################################################################  
    def SetClient_Status_Change_Idle(self,clientName:str):
         c:client_object = self.GetClientObjectByServiceName(ServiceNameToFind=clientName)
         if (c):
             self._SetClient_Status_Change_Idle(c.client)
    
    def _SetClient_Status_Change_Idle(self,client):
        ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_CLIENT_STANDBY_CMD,
                                                                          Message="", Value=0, ValueStr="")
             
        self.SendToClient(TargetClient=client,MyMsg=ObjToSend,From=Socket_Services_List.SERVER)
       
    
    
    def Run_Threads(self,SimulOn = False):
        simul_thread = threading.Thread(target=self.WaitingForNewClient)
        simul_thread.start()
        #self.WaitingForNewClient()
        
        if (SimulOn):
            simul_thread = threading.Thread(target=self.Server_BroadCast_Simulation)
            simul_thread.start()
        
if (__name__== "__main__"):
    
        
    MyServer = Socket_Server()
    MyServer.Run_Threads()
    
   