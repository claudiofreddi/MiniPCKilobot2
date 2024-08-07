import socket
import threading
import time
from Lib_Utils_MyQ import * 
from Robot_Envs import * 
from Socket_Json import * 

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
        

class Robot_Socket_Server_Brain(Robot_Socket_BaseClass): 


    client_objects = []
    
        
    # SensorMessage List 
    MyListOfSensors = []
    
    def __init__(self,ServiceName = 'Server', ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort, True)
           
        self.Connect()    


    def SendToClient(self,TargetClient, Obj:SocketMessage_Type_STANDARD,From=''): 
        try:
            c:client_object = self.GetClientObject(TargetClient)
            To2 = c.servicename if (c != None) else ''
            
            SerializedObj = self.Pack_StandardEnvelope_And_Serialize(Obj,From = From,To=To2)
            
            TargetClient.send(SerializedObj)
        except Exception as e:
            
            print("Server Error in SendToClient " + str(e))
            
                  
    def GetFromClient(self,TargetClient):
        try:
                       
            ser_obj = TargetClient.recv(self.buffer)
            myobj = self.UnPack_StandardEnvelope_And_Deserialize(ser_obj)
            self.TraceLog(self.LogPrefix() + " received " + myobj.ContentType + " from " + myobj.From)
            return myobj
         
        except Exception as e:
            self.TraceLog("Server Error in GetFromClient " + str(e))
            return None    
    
    
       
    # List all servicenames
    def ListActiveservicenames(self):
        self.TraceLog("Active servicenames")
        c:client_object
        for c in self.client_objects:
            self.TraceLog(c.servicename)   


    def GetClientObject(self,client:socket)->client_object:
        
        c:client_object
        for c in self.client_objects:
            if (c.client == client):
                return c
        return None

    def QuitClient(self, TargetClient:socket, Broadcast = True): 
        c:client_object = self.GetClientObject(TargetClient)
        ServiceName = c.servicename
        self.client_objects.remove(c)
        TargetClient.close()
        msg = '{} left!'.format(ServiceName)
        self.TraceLog(msg)
        ObjToSend:SocketMessage_Type_STANDARD = SocketMessage_Type_STANDARD(ClassType=SocketMessage_Type_STANDARD_Type.MESSAGE, SubClassType = '', UID = '',Message =msg,Value="",RefreshInterval=5,LastRefresh = 0, IsAlert=False, Error ="")
        if (Broadcast):
            self.broadcastObj(ObjToSend)
                     

    def broadcastObj(self,ObjToSend:SocketMessage_Type_STANDARD, ExcludeServiceName = ""):
        c:client_object
        count = 0
        for c in self.client_objects:
          
            if (c.servicename != ExcludeServiceName):
                self.TraceLog("Broad Cast to: " + c.servicename)
                self.SendToClient (c.client, ObjToSend)
                count = count + 1
                
        return count
            
            
    def SensorUpdate(self,ReceivedSensorObject:SocketMessage_Type_STANDARD):
        self.TraceLog("Received Type SENSOR:" + ReceivedSensorObject.SubClassType)
        found = False
        if (ReceivedSensorObject.ClassType == SocketMessage_Type_STANDARD_Type.SENSOR ):
            pSensor:SocketMessage_Type_STANDARD
            for pSensor in self.MyListOfSensors:
                print(pSensor.SubClassType + " - curr val: " + str(pSensor.Value))
                if (pSensor.SubClassType == ReceivedSensorObject.SubClassType):
                    found = True
                    pSensor.Copy(ReceivedSensorObject)
                    print(pSensor.SubClassType + " - New val: " + str(pSensor.Value))
                    self.TraceLog(ReceivedSensorObject.SubClassType + " copied")
                    break
            if (not found):
                self.MyListOfSensors.append(ReceivedSensorObject)
                self.TraceLog(ReceivedSensorObject.SubClassType + " added")
                
                
                
    def GetSensor(self,SubClassType):
        pSensor:SocketMessage_Type_STANDARD
        for pSensor in self.MyListOfSensors:
            if (pSensor.SubClassType == SubClassType):
                    return True, pSensor
        return False, None   
    
        

 
    # Handling Messages From Clients
    def handle(self,client:socket):
        
        
        ## Read Client Info from 
        CurrClientObject = self.GetClientObject(client)
        
        LocalMsgPrefix = self.LogPrefix() + " from [" + CurrClientObject.servicename + "]"
        while True:
            try:
                ## Receive Message
                
                ReceivedEnvelope:SocketMessageEnvelope = self.GetFromClient(client)
                self.TraceLog(LocalMsgPrefix + " received  Envelope  From " + ReceivedEnvelope.From + " To: " + ReceivedEnvelope.To)
                
                ##SocketObjectClassType.MESSAGE      
                if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                    
                                            
                    ReceivedMessage = SocketMessage_Type_STANDARD(**SocketDecoder.get(ReceivedEnvelope.EncodedJson))
                    self.TraceLog(LocalMsgPrefix + " received  Message " + ReceivedMessage.Message + " Value: " + str(ReceivedMessage.Value)
                                   + "  Class: " + ReceivedMessage.ClassType
                                   + "  SubClass: " + ReceivedMessage.SubClassType)
                    
                    ## SEZIONE MESSAGGI
                    if (ReceivedMessage.ClassType== SocketMessage_Type_STANDARD_Type.MESSAGE):
                                            
                        if (ReceivedMessage.Message == self.SOCKET_QUIT_MSG):
                     
                            self.QuitClient(client)
                            break
                    
                    ##SocketObjectClassType.SENSOR      
                    if (ReceivedMessage.ClassType== SocketMessage_Type_STANDARD_Type.SENSOR):
                        
                        
                        self.SensorUpdate(ReceivedMessage)
                        
                    if (ReceivedMessage.ClassType== SocketMessage_Type_STANDARD_Type.INPUT):
                        
                        
                        if (ReceivedEnvelope.To == SocketMessageEnvelopeTargetType.BROADCAST):   
                            self.broadcastObj(ReceivedMessage, ReceivedEnvelope.From)
                            
                else:    
                    
                    #Try as MESSAGE and resent to sender
                    ReceivedMessage = SocketMessage_Type_STANDARD(**SocketDecoder.get(ReceivedEnvelope.EncodedJson))
                    self.TraceLog(LocalMsgPrefix + " Message Unnkown: " + ReceivedMessage.Message + " [" + ReceivedMessage.ClassType + "." + ReceivedMessage.SubClassType + "] from " + str(CurrClientObject.servicename))               
                    # confirm message
                    ObjToSend:SocketMessage_Type_STANDARD = SocketMessage_Type_STANDARD(SocketMessage_Type_STANDARD_Type.MESSAGE,"",ReceivedMessage.Message,0,"Message not recognized")
                    self.SendToClient(client,ObjToSend)
                    
            
                
            except Exception as e:
                self.TraceLog(LocalMsgPrefix + " Error in handle() "  + str(e))
          
                self.QuitClient(client)
                break
           
    # Receiving / Listening Function
    def WaitingForNewClient(self):
        
        self.TraceLog("Waiting for Clients...")
        
        
        try:
            
            while True:
                # Accept Connection
                client, address = self.ServerConnection.accept()
                self.TraceLog("Connected with {}".format(str(address)))
                ObjToSend:SocketMessage_Type_STANDARD = SocketMessage_Type_STANDARD(SocketMessage_Type_STANDARD_Type.MESSAGE,"","",self.SOCKET_LOGIN_MSG)
                self.SendToClient(client,ObjToSend,From=str(address))
                
                # Request And Store servicename
                ReceivedEnvelope = self.GetFromClient(client)
                
                if (ReceivedEnvelope != None):
                    
                    if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                        
                        ReceivedMessage = SocketMessage_Type_STANDARD(**SocketDecoder.get(ReceivedEnvelope.EncodedJson))
                        
                        if (ReceivedMessage.ClassType ==SocketMessage_Type_STANDARD_Type.MESSAGE):
                            
                            servicename = ReceivedMessage.Message
                            self.TraceLog(" New Service Name is {}".format(servicename))
                                                                
                            myclient_object = client_object(client,servicename,address)
                            self.client_objects.append(myclient_object)
                            #self.TraceLog(self.LogPrefix() + " New Client Added")                      

                            # Start Handling Thread For Client
                            thread = threading.Thread(target=self.handle, args=(client,))
                            thread.start()
            
        except Exception as e:
            self.TraceLog(self.LogPrefix() + " Error in WaitingForNewClient() "  + str(e))
        
            
    def Server_BroadCast_Simulation(self):
        tick = 0
        self.TraceLog(self.LogPrefix() +  " Server_BroadCast_Simulation Enabled")
        while True:
            time.sleep(3)
            
            message = self.LogPrefix() +  "SIMULATED Broadcast tick: " + str(tick)            
            ObjToSend:SocketMessage_Type_STANDARD = SocketMessage_Type_STANDARD(SocketMessageEnvelopeContentType.STANDARD,"Test","",message)
            count = self.broadcastObj(ObjToSend)
            if (count>0):
                print(message)
            
            
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
    
    MyServer = Robot_Socket_Server_Brain()
    MyServer.Run_Threads(False)
    
   