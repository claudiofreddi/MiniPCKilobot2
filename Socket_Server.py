import socket
import threading
import time
from Lib_Utils_MyQ import * 
from Robot_Envs import * 
from Socket_ClientServer_Common import * 

class client_object:
    client:socket = None
    servicename:str = ''
    address = ('',0)
    
    def __init__(self):
        pass
    
    def __init__(self,Client:socket, ServiceName:str, Address):
        self.client = Client
        self.servicename = ServiceName
        self.address = Address    
        

class Socket_Server(Socket_ClientServer_BaseClass): 


    client_objects = []
    
        
    # SensorMessage List 
    MyListOfSensors = []
    
    def __init__(self,ServiceName = Socket_Services_List.SERVER, ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort, True)
           
        self.Connect()    


    def SendToClient(self,TargetClient, MyMsg:Socket_Default_Message,From=''): 
        try:
            c:client_object = self.GetClientObject(TargetClient)
            ToServiceName = c.servicename if (c != None) else ''
            
            MyEnvelope:SocketMessageEnvelope = self.Prepare_StandardEnvelope(MsgToSend=MyMsg,To=ToServiceName,From=self.ServiceName)
            SerializedObj = self.Pack_Envelope_And_Serialize(MyEnvelope)
                        
            TargetClient.send(SerializedObj)
            
            self.LogConsole("Server SendToClient [" + ToServiceName + "]: " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
            self.LogConsole("Server SendToClient [" + ToServiceName + "]: " + MyMsg.GetMessageDescription(),ConsoleLogLevel.Socket_Flow)
            
        except Exception as e:
            
            self.LogConsole("Server Error in SendToClient " + str(e),ConsoleLogLevel.Error)
            
                  
    def GetFromClient(self,TargetClient):
        try:
            c:client_object = self.GetClientObject(TargetClient)
            FromServiceName = c.servicename if (c != None) else ''
            
            ser_obj = TargetClient.recv(self.buffer)
            MyEnvelope = self.UnPack_StandardEnvelope_And_Deserialize(ser_obj)
            self.LogConsole("Server GetFromClient [" + FromServiceName + "] " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
            
            return MyEnvelope
         
        except Exception as e:
            self.LogConsole("Server Error in GetFromClient " + str(e),ConsoleLogLevel.Error)
            return None    
    
    
       
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
        c:client_object = self.GetClientObject(TargetClient)
        ServiceName = c.servicename
        self.client_objects.remove(c)
        TargetClient.close()
        msg = '{} left!'.format(ServiceName)
        self.LogConsole(msg,ConsoleLogLevel.Socket_Flow)
        ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.MESSAGE, SubClassType = '', UID = '',Message =msg,Value="",RefreshInterval=5,LastRefresh = 0, IsAlert=False, Error ="")
        if (Broadcast):
            self.broadcastObj(ObjToSend)
                     

    def broadcastObj(self,ObjToSend:Socket_Default_Message, ExcludeServiceName = ""):
        c:client_object
        count = 0
        for c in self.client_objects:
          
            if (c.servicename != ExcludeServiceName):
                self.LogConsole("Server Broadcast to: " + c.servicename,ConsoleLogLevel.Socket_Flow)
                self.SendToClient (c.client, ObjToSend)
                count = count + 1
                
        return count
            
            
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
                
                ReceivedEnvelope:SocketMessageEnvelope = self.GetFromClient(client)
                  
                           
                ##SocketObjectClassType.MESSAGE      
                if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                                       
                    ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                    self.LogConsole("Server GetFromClient [" + CurrClientObject.servicename + "] " + ReceivedMessage.GetMessageDescription(),ConsoleLogLevel.Socket_Flow )                
                    
                    ## SEZIONE MESSAGGI
                    if (ReceivedMessage.ClassType== Socket_Default_Message_ClassType.MESSAGE):
                                            
                        if (ReceivedMessage.Message == self.SOCKET_QUIT_MSG):
                     
                            self.QuitClient(client)
                            break
                    
                    ##SocketObjectClassType.SENSOR      
                    if (ReceivedMessage.ClassType== Socket_Default_Message_ClassType.SENSOR):
                        
                        
                        self.SensorUpdate(ReceivedMessage)
                        
                    if (ReceivedMessage.ClassType== Socket_Default_Message_ClassType.INPUT):
                        
                        
                        if (ReceivedEnvelope.To == SocketMessageEnvelopeTargetType.BROADCAST):   
                            self.broadcastObj(ReceivedMessage, ReceivedEnvelope.From)
                    
                    
                    c:client_object = self.GetClientObjectByServiceName(Socket_Services_List.USERINTERFACE)
                    if (c != None):
                        self.SendToClient(c.client,ReceivedMessage)
                            
                else:    
                    
                    #Try as MESSAGE and resent to sender
                    
                    ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                    # confirm message
                    ObjToSend:Socket_Default_Message = Socket_Default_Message(Socket_Default_Message_ClassType.MESSAGE,"",ReceivedMessage.Message,0,"Message not recognized")
                    self.SendToClient(client,ObjToSend)
                    
            
                
            except Exception as e:
                self.LogConsole(LocalMsgPrefix + " Error in handle() "  + str(e),ConsoleLogLevel.Error)
          
                self.QuitClient(client)
                break
           
    # Receiving / Listening Function
    def WaitingForNewClient(self):
        
        self.LogConsole("Waiting for Clients...",ConsoleLogLevel.Socket_Flow)
        
        
        try:
            
            while True:
                # Accept Connection
                client, address = self.ServerConnection.accept()
                self.LogConsole("Connected with {}".format(str(address)),ConsoleLogLevel.Socket_Flow)
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Socket_Default_Message_ClassType.MESSAGE,"","",self.SOCKET_LOGIN_MSG)
                self.SendToClient(client,ObjToSend,From=str(address))
                
                # Request And Store servicename
                ReceivedEnvelope = self.GetFromClient(client)
                self.LogConsole("Server GetFromClient " + ReceivedEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
                
                if (ReceivedEnvelope != None):
                    
                    if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                        
                        
                        ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                        
                        if (ReceivedMessage.ClassType ==Socket_Default_Message_ClassType.MESSAGE):
                            
                            servicename = ReceivedMessage.Message
                            self.LogConsole(" New Service Name is {}".format(servicename),ConsoleLogLevel.Socket_Flow,ConsoleLogLevel.Show)
                            
                            if (not self.CheckIfServiceNameExists(servicename)):
                                                    
                                myclient_object = client_object(client,servicename,address)
                                self.client_objects.append(myclient_object)
                                                

                                # Start Handling Thread For Client
                                thread = threading.Thread(target=self.handle, args=(client,))
                                thread.start()
                            else:
                                client.close()
                                self.LogConsole(" Service Name {} Already Exists. Connection Refused".format(servicename),ConsoleLogLevel.Socket_Flow,ConsoleLogLevel.Show)
                                
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + " Error in WaitingForNewClient() "  + str(e),ConsoleLogLevel.Error)
        
            
    def Server_BroadCast_Simulation(self):
        tick = 0
        self.LogConsole(self.ThisServiceName() +  " Server_BroadCast_Simulation Enabled",ConsoleLogLevel.Socket_Flow)
        while True:
            time.sleep(3)
            
            message = self.ThisServiceName() +  "SIMULATED Broadcast tick: " + str(tick)            
            ObjToSend:Socket_Default_Message = Socket_Default_Message(SocketMessageEnvelopeContentType.STANDARD,"Test","",message)
            
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
    
   