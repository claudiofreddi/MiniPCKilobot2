from __future__ import annotations
import json
import socket
from json import JSONEncoder
from Robot_Envs import * 
import uuid


class SocketObjectClassType:
    MESSAGE = "MESSAGE"    
    SENSOR = "SENSOR"

class SocketEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__  

class SocketObject(object):
    def __init__(self,ClassType, Key,Message,Value=0,Error=""):
        self.ClassType = ClassType
        self.Key = Key
        self.Message = Message
        self.Value = Value
        self.Error = Error
        
        

    def json(self):
        return json.dumps(self,cls=SocketEncoder,indent=4)
    
    def Copy(self,Source:SocketObject):
        self.ClassType = Source.ClassType
        self.Key = Source.Key
        self.Message = Source.Message
        self.Value = Source.Value
        self.Error = Source.Error
    
class SocketDecoder:
    def get(CodedJson):
        return  json.loads(CodedJson)


class SensorObject(SocketObject):
    def __init__(self,ClassType, Key,Message,Value,Error="",IsAlert=False):
        super().__init__(ClassType, Key,Message,Value,Error)
        self.IsAlert  = IsAlert
        
    def Copy(self,Source:SocketObject):
        super().Copy()
        self.IsAlert  = Source.IsAlert
        

class SocketMessageEnvelope:
    def  __init__(self,ClassType,EncodedJson): 
        self.ClassType = ClassType
        self.EncodedJson = EncodedJson


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
        self.TraceLog("Quit Command..")
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
            
        
if (__name__== "__main__"):
    
    
    x = SocketObject("10","1","3",4).json()
    
    print(type(x))
    print(x)
    
    FinalObj = SocketObject(**SocketDecoder.get(x))
    
    print(type(FinalObj))
    
    
    
    y = SensorObject("10","1","3",4,3).json()
    print(y)
    print(type(y))
    
    FinalObj = SensorObject(**SocketDecoder.get(y))
    
    exit

    
