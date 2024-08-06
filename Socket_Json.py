from __future__ import annotations
import json
import socket
from json import JSONEncoder
from Robot_Envs import * 
import uuid
import pickle



class SocketEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__  

class SocketDecoder:
    def get(CodedJson):
        return  json.loads(CodedJson)

class SocketContent_STANDARD_Type:
    MESSAGE = "MESSAGE"    
    SENSOR = "SENSOR"


class SocketContent_STANDARD(object):
    def __init__(self,ClassType=SocketContent_STANDARD_Type.MESSAGE, SubClassType = '', UID = '',Message ="",Value="",RefreshInterval=5,LastRefresh = 0, IsAlert=False, Error =""):
        self.ClassType = ClassType
        self.SubClassType = SubClassType  #Compass, Battery, .. user defined
        self.Message = Message
        self.Value = Value
        self.Error = Error
        self.IsAlert = IsAlert
        if (UID==''):
            self.UID =  str(uuid.uuid4())
        self.RefreshInterval = RefreshInterval
        self.LastRefresh = LastRefresh
        
        

    def json(self):
        return json.dumps(self,cls=SocketEncoder,indent=4)
    
    def Copy(self,Source:SocketContent_STANDARD):
        self.ClassType = Source.ClassType
        self.Key = Source.Key
        self.Message = Source.Message
        self.Value = Source.Value
        self.Error = Source.Error

#A = SocketContent_STANDARD(ClassType=SocketContent_STANDARD_Type.MESSAGE, SubClassType = '', UID = '',Message ="",Value="",RefreshInterval=5,LastRefresh = 0, IsAlert=False, Error ="")
    


class SensorObject(SocketContent_STANDARD):
    def __init__(self,ClassType, Key,Message,Value,Error="",IsAlert=False):
        super().__init__(ClassType, Key,Message,Value,Error)
        self.IsAlert  = IsAlert
        
    def Copy(self,Source:SocketContent_STANDARD):
        super().Copy()
        self.IsAlert  = Source.IsAlert
        
class SocketMessageEnvelopeContentType:
    STANDARD = "STANDARD"
    
class SocketMessageEnvelope:
    def  __init__(self,Uid = "",ContentType=SocketMessageEnvelopeContentType.STANDARD,EncodedJson='',NeedResponse=False,Response=''): 
        self.Uid = uuid.uuid4
        self.ContentType = ContentType
        self.EncodedJson = EncodedJson
        self.NeedResponse = NeedResponse
        self.Response = Response

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

class Robot_Socket_BaseClass:
     # Connection Data
    ServerIP = SOCKET_SERVER_IP
    ServerPort = SOCKET_SERVER_PORT
    buffer = SOCKET_BUFFER
    ServiceName:str = ""
    IsServer:bool = False
    ServerConnection:socket = None
    client:socket
    IsConnected = False
    ShowNormalTrace = True
    IsQuitCalled = False
    ShowJsonData = False
    
    SOCKET_QUIT_MSG = "Quit"
    SOCKET_LOGIN_MSG = "ServiceName"
    
    def __init__(self,ServiceName = '', ForceServerIP = '',ForcePort='', IsServer=False):
            
            self.IsServer = IsServer
            
            # Starting Server
            if (ForceServerIP!= ''):
                self.ServerIP = ForceServerIP
                
            if (ForcePort!= ''):
                self.ServerPort = ForcePort  
                
            if (ServiceName != ''):
                self.ServiceName = ServiceName
            else:
                if (self.IsServer):
                    self.ServiceName = self.ServerIP
                else:
                    #Assign Random
                    self.ServiceName = str(uuid.uuid4())
            
            if (self.IsServer):
                self.TraceLog(self.ServiceName + " started on " + self.ServerIP + ":" + str(self.ServerIP) + " buffer:" +  str(self.buffer)) 
            else:
                self.TraceLog("init Service: " + str(self.ServiceName))         
            
    
    def Connect(self)->bool:
        try:
            if (self.IsServer):
                self.ServerConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.ServerConnection.bind((self.ServerIP, self.ServerPort))
                self.ServerConnection.listen() 
            else:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client.connect((self.ServerIP, self.ServerPort))
            
            self.IsConnected = True
            return True        
        
        except Exception as e:
            if (str(e).find("target machine actively refused it")==0):
                self.TraceLog("Error in Connect()  " + str(e))
            self.IsConnected = False
            return False
    
    def Disconnect(self):
        self.TraceLog("Disconnecting..")
        self.IsConnected = False
        if (self.IsServer):
            self.ServerConnection.close()
        else:
            self.client.close()        
    
    
    def Quit(self):
        
        try:
            if (self.IsServer):
                self.ServerConnection.close()
                self.TraceLog("Server Terminated")
            else:
                self.client.close()
                self.TraceLog("Client terminated for " + self.ServiceName )
                
            self.IsConnected = False
            self.IsQuitCalled = True
         
            
        except Exception as e:
            self.TraceLog("Error in Quit()  " + str(e))
                                    
    def IsTraceLogEnabled(self) -> bool:
        return self.ShowNormalTrace
    
    def TraceLog(self, Text):
        if (self.IsTraceLogEnabled()):
            print(Text)  
    
    def LogPrefix(self)->str:
        if (self.IsServer):
            Prefix = "Server"
        else:
            Prefix = "Client"
        return Prefix
    
    def Pack_StardardEnvelope_And_Serialize(self,Obj:SocketContent_STANDARD):
        try:
            if (self.ShowJsonData):
                print(Obj.json())
                print(Obj.ClassType)
            myobj =  SocketMessageEnvelope("",SocketMessageEnvelopeContentType.STANDARD,Obj.json())    
            ser_obj = pickle.dumps(myobj,protocol=5) 
            if (self.ShowJsonData):
                print(len(ser_obj))
            return ser_obj
        
        except Exception as e:
            self.TraceLog(self.LogPrefix + " Error in Pack_StardardEnvelope_And_Serialize " + str(e))
     
    def UnPack_StardardEnvelope_And_Deserialize(self,ser_obj):
        try:
            myobj:SocketMessageEnvelope = pickle.loads(ser_obj)
            return myobj
        
        except Exception as e:
            self.TraceLog(self.LogPrefix + " Error in UnPack_StardardEnvelope_And_Deserialize " + str(e))
            return None
        
if (__name__== "__main__"):
    
    
    x = SocketContent_STANDARD("10","1","109283293","4","").json()
    
    print(type(x))
    print(x)
    
    FinalObj = SocketContent_STANDARD(**SocketDecoder.get(x))
    
    print(type(FinalObj))
    

    exit

    
