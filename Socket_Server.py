import socket

import threading
import time
from Lib_Utils_MyQ import * 
from Robot_Envs import * 
from Socket_ClientServer_BaseClass import * 
from Socket_Messages import * 

import cv2

class client_object:
    client:socket = None
    servicename:str = ''
    address = ('',0)
    Topics = []
    TopicSubscriptions = []
    ErrCount = 0
    
    def __init__(self):
        pass
    
    def __init__(self,Client:socket, ServiceName:str, Address):
        self.client = Client
        self.servicename = ServiceName
        self.address = Address    
    
    
   
    def RegisterTopic(self,NewTopic):
              
        if (Socket_Default_Message_Topics().IsTopicReserved(NewTopic)):
            return False
        try:
            i = self.Topics.index(NewTopic)
        except Exception as e:
            self.Topics.append(NewTopic)  
            return True
        
        return False        
        
    def SubscribeTopic(self,SubscribeTopic):
        
        if (Socket_Default_Message_Topics().IsTopicReserved(SubscribeTopic)):
            return False
        
        try:
            i = self.TopicSubscriptions.index(SubscribeTopic)
            
                           
        except Exception as e:
            self.TopicSubscriptions.append(SubscribeTopic)  
            return True
        
        return False          

    def UnSubscribeTopic(self,UnSubscribeTopic):
      
        try:
            i = self.TopicSubscriptions.index(UnSubscribeTopic)
            self.TopicSubscriptions.remove(UnSubscribeTopic)
            
            return True           
            
        except Exception as e:
           pass 
       
        return False 

    def IsSubscribedToThisTopic(self, TopicToCheck):
        for t in self.TopicSubscriptions:
            if (t == TopicToCheck):
               return True 
        return False
        
        
class Socket_Server(Socket_ClientServer_BaseClass): 


    client_objects = []
    SHOW_FRAME = True
        
    # SensorMessage List 
    MyListOfSensors = []
    
    def __init__(self,ServiceName = Socket_Services_List.SERVER, ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort, True)
           
        self.Connect()    


    def SendToClient(self,TargetClient, MyMsg:Socket_Default_Message,From='',AdditionaByteData=b''): 
        try:
            c:client_object = self.GetClientObject(TargetClient)
            ToServiceName = c.servicename if (c != None) else ''
            
            MyEnvelope:SocketMessageEnvelope = self.Prepare_StandardEnvelope(MsgToSend=MyMsg,To=ToServiceName,From=self.ServiceName)
            SerializedObj = self.Pack_Envelope_And_Serialize(MyEnvelope)
            
            
            
            self.MySocket_SendReceive.send_msg(TargetClient,SerializedObj,AdditionaByteData)
            
            
            self.LogConsole("Server SendToClient [" + ToServiceName + "]: " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
            self.LogConsole("Server SendToClient [" + ToServiceName + "]: " + MyMsg.GetMessageDescription(),ConsoleLogLevel.Socket_Flow)
            
        except Exception as e:
            
            self.LogConsole("Server Error in SendToClient " + str(e),ConsoleLogLevel.Error)
            
                  
    def GetFromClient(self,TargetClient:socket):
        try:
            c:client_object = self.GetClientObject(TargetClient)
            FromServiceName = c.servicename if (c != None) else ''
            
            ser_obj,AdditionaByteData = self.MySocket_SendReceive.recv_msg(TargetClient)
                
            MyEnvelope = self.UnPack_StandardEnvelope_And_Deserialize(ser_obj)
            self.LogConsole("Server GetFromClient [" + FromServiceName + "] " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
            
            return MyEnvelope,AdditionaByteData 

         
        except Exception as e:
            c.ErrCount += 1
            if (c.ErrCount >= 5 ):
                c.ErrCount = 0
                self.QuitClient(TargetClient,True)
             
            else:
                self.LogConsole("Server Error in GetFromClient " + str(e),ConsoleLogLevel.Error)
            return None, b''   
    
    
       
    # List all servicenames
    def ListActiveservicenames(self):
        self.LogConsole("Active servicenames",ConsoleLogLevel.Test)
        c:client_object
        for c in self.client_objects:
            self.LogConsole(c.servicename,ConsoleLogLevel.Show)   


    def GetClientObject(self,client:socket)->client_object:
        
        c:client_object
        for c in self.client_objects:
            if (c.client == client):
                return c
        return None

    def GetClientObjectByServiceName(self,ServiceNameToFind)->client_object:
        
        c:client_object
        for c in self.client_objects:
            if (c.servicename == ServiceNameToFind):
                return c
        return None
    
    
    def CheckIfServiceNameExists(self,ServiceNameToFind)->bool:
        
        c:client_object
        for c in self.client_objects:
            if (c.servicename == ServiceNameToFind):
                return True
        return False
    
    def QuitClient(self, TargetClient:socket, Broadcast = True):
        try: 
            c:client_object = self.GetClientObject(TargetClient)
            ServiceName = c.servicename
            self.client_objects.remove(c)
            TargetClient.close()
            msg = '{} left!'.format(ServiceName)
            self.LogConsole(msg,ConsoleLogLevel.Socket_Flow)
            ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.MESSAGE, 
                                                                    SubClassType = '', 
                                                                    Topic = Socket_Default_Message_Topics.MESSAGE,
                                                                    UID = '',
                                                                    Message =msg,
                                                                    Value=0,
                                                                    RefreshInterval=5,
                                                                    LastRefresh = 0,
                                                                    IsAlert=False, 
                                                                    Error ="")
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
    
            
    def SensorUpdate(self,ReceivedSensorObject:Socket_Default_Message):
        Log = False
        if (Log): self.LogConsole("Received Type SENSOR:" + ReceivedSensorObject.SubClassType,ConsoleLogLevel.Socket_Flow)
        found = False
        if (ReceivedSensorObject.ClassType == Socket_Default_Message_ClassType.SENSOR ):
            pSensor:Socket_Default_Message
            for pSensor in self.MyListOfSensors:
                if (Log): self.LogConsole(pSensor.SubClassType + " - curr val: " + str(pSensor.Value),ConsoleLogLevel.Socket_Flow)
                if (pSensor.SubClassType == ReceivedSensorObject.SubClassType):
                    found = True
                    pSensor.Copy(ReceivedSensorObject)
                    if (Log): self.LogConsole(pSensor.SubClassType + " - New val: " + str(pSensor.Value),ConsoleLogLevel.Socket_Flow)
                    if (Log): self.LogConsole(ReceivedSensorObject.SubClassType + " copied",ConsoleLogLevel.Socket_Flow)
                    break
            if (not found):
                self.MyListOfSensors.append(ReceivedSensorObject)
                if (Log): self.LogConsole(ReceivedSensorObject.SubClassType + " added",ConsoleLogLevel.Socket_Flow)
                
                
                
    def GetSensor(self,SubClassType):
        pSensor:Socket_Default_Message
        for pSensor in self.MyListOfSensors:
            if (pSensor.SubClassType == SubClassType):
                    return True, pSensor
        return False, None   
    
        

 
    # Handling Messages From Clients
    def handle(self,client:socket):
        
        
        ## Read Client Info from 
        CurrClientObject = self.GetClientObject(client)
        
        LocalMsgPrefix = self.ThisServiceName() + " from [" + CurrClientObject.servicename + "]"
        while True:
            try:
                ## Receive Message
                ReceivedEnvelope:SocketMessageEnvelope
                ReceivedMessage:Socket_Default_Message
                
                ReceivedEnvelope, AdditionaByteData = self.GetFromClient(client)
                
                if (ReceivedEnvelope != None):
                              
                    ########################################################################################                        
                    ##Gestione Messaggi Conosciuti dal server   
                    ########################################################################################   
                    if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                                        
                        ReceivedMessage = ReceivedEnvelope.GetReceivedMessage()
                        self.LogConsole("Server GetFromClient [" + CurrClientObject.servicename + "] " + ReceivedMessage.GetMessageDescription(),ConsoleLogLevel.Socket_Flow )                
                                    
                        
                        ## SEZIONE MESSAGGI SPECIALI
                        if (ReceivedMessage.ClassType== Socket_Default_Message_ClassType.MESSAGE):
                                                
                            if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_ADD):
                                if (CurrClientObject.RegisterTopic(ReceivedMessage.Message)):
                                    self.LogConsole("[" + CurrClientObject.servicename +  "]  Added Topic [" + ReceivedMessage.Message + "]",ConsoleLogLevel.System)
                            
                            if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_SUBSCRIBE):
                                if (CurrClientObject.SubscribeTopic(ReceivedMessage.Message)):
                                    self.LogConsole("[" + CurrClientObject.servicename +  "] Subscribed to Topic [" + ReceivedMessage.Message + "]",ConsoleLogLevel.System)
                                    
                            if (ReceivedMessage.Message == self.SOCKET_QUIT_MSG):
                                self.LogConsole("[" + CurrClientObject.servicename +  "] Quitted ",ConsoleLogLevel.System)
                                self.QuitClient(client)
                                break
                        
                        ##SocketObjectClassType.SENSOR : value update      
                        if (ReceivedMessage.ClassType== Socket_Default_Message_ClassType.SENSOR):
                                        
                            self.SensorUpdate(ReceivedMessage)
                            
                        if (ReceivedMessage.ClassType== Socket_Default_Message_ClassType.INPUT):
                            
                            if (ReceivedMessage.SubClassType== Socket_Default_Message_SubClassType.IMAGE):
                                self.LogConsole("Receiving Image Data " + str(len(AdditionaByteData)),ConsoleLogLevel.Test)
                                if (len(AdditionaByteData)>0):
                                    if (self.SHOW_FRAME):
                                        frame= pickle.loads(AdditionaByteData, fix_imports=True, encoding="bytes")
                                        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)  
                                        cv2.imshow('server',frame)
                                        cv2.waitKey(1)
                                
                        ########################################################################################                        
                        ##FINE Gestione Messaggi Conosciuti dal server   
                        ########################################################################################   
                        
                        ########################################################################################                        
                        ##Gestione Inoltro Messaggi  
                        ########################################################################################                                        
                        if (ReceivedEnvelope.To == SocketMessageEnvelopeTargetType.BROADCAST):   
                            #Broadcast requested by client
                            self.broadcastObj(ReceivedMessage, ReceivedEnvelope.From)
                        else:
                            #By Topic
                            c:client_object
                            if (not Socket_Default_Message_Topics().IsTopicReserved(ReceivedMessage.Topic)):
                                for c in self.client_objects:
                                    #if (c.servicename != CurrClientObject.servicename):
                                    if (c.IsSubscribedToThisTopic(ReceivedMessage.Topic)):
                                        self.SendToClient(TargetClient=c.client,MyMsg=ReceivedMessage,From= Socket_Services_List.SERVER,AdditionaByteData=AdditionaByteData)
                    
                        # c:client_object = self.GetClientObjectByServiceName(Socket_Services_List.USERINTERFACE)
                        # if (c != None):
                        #     self.SendToClient(c.client,ReceivedMessage)
                                
                    else:    
                        
                        #Try as MESSAGE and resent to sender
                        
                        ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                        # confirm message
                        ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.MESSAGE,
                                                                                SubClassType="",
                                                                                Topic = Socket_Default_Message_Topics.MESSAGE,
                                                                                Message=ReceivedMessage.Message,
                                                                                Value=0,
                                                                                Error="Message not recognized")
                        self.SendToClient(client,ObjToSend)
                        
            
                
            except Exception as e:
                self.LogConsole(LocalMsgPrefix + " Error in handle() "  + str(e),ConsoleLogLevel.Error)
                try:
                    self.QuitClient(client)
                except:
                    continue
                break
           
    # Receiving / Listening Function
    def WaitingForNewClient(self):
        
        self.LogConsole("Waiting for Clients...",ConsoleLogLevel.Socket_Flow)
        i = 0
        
        try:
            
            while True:
                # Accept Connection
                i = 0
                client, address = self.ServerConnection.accept()
                i +=1 
                self.LogConsole("Connected with {}".format(str(address)),ConsoleLogLevel.Socket_Flow)
                i +=1
                ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.MESSAGE,
                                                                          SubClassType="",
                                                                          Topic = Socket_Default_Message_Topics.MESSAGE,
                                                                          Message=self.SOCKET_LOGIN_MSG)
                i +=1
                self.SendToClient(TargetClient=client,MyMsg=ObjToSend,From=str(address))
                i +=1
                
                # Request And Store servicename
                ReceivedEnvelope:SocketMessageEnvelope
                ReceivedEnvelope, AdditionaByteData = self.GetFromClient(client)
                i +=1
                
                #self.LogConsole("Server GetFromClient " + ReceivedEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
                
                if (ReceivedEnvelope != None):
                    
                    if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                        
                        
                        ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                        
                        if (ReceivedMessage.ClassType ==Socket_Default_Message_ClassType.MESSAGE):
                            
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
            ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.MESSAGE,
                                                                      SubClassType="",
                                                                      Topic = Socket_Default_Message_Topics.MESSAGE,
                                                                      Message=message)
            
            # s = self.GetClientObjectByServiceName(Socket_Services_List.REMOTE)
            # if (s != None):
            #     self.SendToClient(s,ObjToSend)

            count = self.broadcastObj(ObjToSend)
            if (count>0):                
                self.LogConsole(message,ConsoleLogLevel.Socket_Flow)
            
            
            tick = tick + 1
        
    def Run_Threads(self,SimulOn = False):
        simul_thread = threading.Thread(target=self.WaitingForNewClient)
        simul_thread.start()
        #self.WaitingForNewClient()
        
        if (SimulOn):
            simul_thread = threading.Thread(target=self.Server_BroadCast_Simulation)
            simul_thread.start()
        
if (__name__== "__main__"):
    
    MyClients = []
    
    MyServer = Socket_Server()
    MyServer.Run_Threads(False)
    
   