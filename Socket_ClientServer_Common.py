from __future__ import annotations
import json
import socket
from json import JSONEncoder
from Robot_Envs import * 
import uuid
import pickle
import time

### ***************************************************************************
### Ecoder e Decoder (JSON <-> Class)
### ***************************************************************************
class SocketEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__  

class SocketDecoder:
    def get(CodedJson):
        return  json.loads(CodedJson)
    
class SuperDecoder:
    def GetReceivedMessage(ReceivedEnvelope:SocketMessageEnvelope):
        return Socket_Default_Message(**SocketDecoder.get(ReceivedEnvelope.EncodedJson))    

### ***************************************************************************
### LOG DEF
### ***************************************************************************

class  ConsoleLogLevel:
    Test = 0
    System = 1
    Control = 2
    Always = 2

class Common_LogConsoleClass(object):
    EnableConsoleLog = True
    EnableConsoleLogLevel = ConsoleLogLevel.Test
    
### ***************************************************************************
### Message FORMAT
### ***************************************************************************
class Socket_Default_Message_ClassType:
    MESSAGE = "MESSAGE"    
    SENSOR = "SENSOR"
    INPUT = "INPUT"

class Socket_Default_Message_SubClassType:
    MESSAGE = "MESSAGE"  
    KEYBOARD = "KEYBOARD"    
    BATTERY = "BATTERY"
    COMPASS = "COMPASS"

class Socket_Services_List:
    SERVER = "Server"
    SENSORS = "SENSORS_Client"
    KEYBOARD = "KEYBOARD_Client"
    USERINTERFACE = "UI_Client"
    REMOTE = "REMOTE_Client"


class Socket_Default_Message(Common_LogConsoleClass):
    def __init__(self,ClassType=Socket_Default_Message_ClassType.MESSAGE, SubClassType = '', UID = '',Message ="",
                 Value=0,RefreshInterval=5,LastRefresh = 0, IsAlert=False, Error =""):
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
    
    def Copy(self,Source:Socket_Default_Message):
        self.ClassType = Source.ClassType
        self.SubClassType = Source.SubClassType
        self.Message = Source.Message
        self.Value = Source.Value
        self.Error = Source.Error
        self.IsAlert = Source.IsAlert 
        self.RefreshInterval = Source.RefreshInterval
        self.LastRefresh = Source.LastRefresh
        
    def GetMessageDescription(self):
        Txt =  " Message " + self.Message + " Value: " + str(self.Value) + "  Class: " + self.ClassType + "  SubClass: " + self.SubClassType
        if (self.Error != ""):
            Txt = Txt + self.Error 
        if (self.IsAlert == True):
            Txt = Txt + self.IsAlert
        return Txt
        
class SocketMessageEnvelopeContentType:
    STANDARD = "STANDARD"
    
    
class SocketMessageEnvelopeTargetType:
    SERVER = "SERVER"
    BROADCAST = "BROADCAST"
    
class SocketMessageEnvelope:
    def  __init__(self,Uid = "",ContentType=SocketMessageEnvelopeContentType.STANDARD,EncodedJson='',
                  From='',To='',
                  NeedResponse=False,Response='',ShowContentinLog = False,SendTime=0): 
        self.Uid = uuid.uuid4
        self.ContentType = ContentType
        self.EncodedJson = EncodedJson
        self.NeedResponse = NeedResponse
        self.Response = Response
        self.ShowContentinLog = ShowContentinLog
        self.From=From
        self.To=To
        self.SendTime = time.time()
            
    def GetEnvelopeDescription(self) -> str:
        return "Envelope [" + self.ContentType + "] From " + self.From + " To: " + self.To 

class Socket_ClientServer_BaseClass(Common_LogConsoleClass):
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
    SOCKET_LOGIN_MSG = "AskForServiceName"
    RETRY_TIME = 3
    
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
                self.LogConsole(self.ServiceName + " started on " + self.ServerIP + ":" + str(self.ServerIP) + " buffer:" +  str(self.buffer)) 
            else:
                self.LogConsole("init Service: " + str(self.ServiceName))         
            
    
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
                self.LogConsole("Error in Connect()  " + str(e))
            self.IsConnected = False
            return False
    
    def Disconnect(self):
        
        self.IsConnected = False
        if (self.IsServer):
            self.ServerConnection.close()
        else:
            self.client.close()     
               
        self.LogConsole(self.LogPrefix() + "  Disconnected")   
    
    def Quit(self):
        
        try:
            self.LogConsole(self.LogPrefix() + "  Quitted") 
            self.Disconnect()
            if (self.IsServer):
                self.ServerConnection.close()
                
            else:
                self.client.close()
              
            
               
            self.IsConnected = False
            self.IsQuitCalled = True
         
            
        except Exception as e:
            self.LogConsole("Error in Quit()  " + str(e))
                                    
 

    
    def LogConsole(self,Text,LogLevel = ConsoleLogLevel.Test):
        if (self.EnableConsoleLog):
            if (LogLevel >= self.EnableConsoleLogLevel):
                print(Text)
    
    def LogPrefix(self)->str:
        return " [" + self.ServiceName + "] "
        
    
    def _ShowStdMessageContent(self,Obj:Socket_Default_Message):
        self.LogConsole(Obj.ClassType)
        self.LogConsole(Obj.json())
    
    def _ShowEnvelope_Content(self,Obj:SocketMessageEnvelope):
        self.LogConsole(Obj.ContentType)
        self.LogConsole("From:", Obj.From)
        self.LogConsole("To:", Obj.To)
           
    def Pack_StandardEnvelope_And_Serialize(self,Obj:Socket_Default_Message,From="",To=""):
        try:
            
            if (self.ShowJsonData):
                 self._ShowStdMessageContent(Obj)
              
            myobj =  SocketMessageEnvelope("",SocketMessageEnvelopeContentType.STANDARD,Obj.json(),From=From if (From!='') else self.ServiceName,To=To) 
            if (myobj.ShowContentinLog or self.ShowJsonData):
                self._ShowEnvelope_Content(myobj)
            ser_obj = pickle.dumps(myobj,protocol=5) 
            
            #Alert if Buffer too little
            if (len(ser_obj) > self.buffer):
                self.LogConsole(self.LogPrefix() + " Increment Buffer Size [" + str(self.buffer) + "]. Curr Envelope Size is " + str(len(ser_obj)) )
              
                
            return ser_obj
        
        except Exception as e:
            self.LogConsole(self.LogPrefix() + " Error in Pack_StardardEnvelope_And_Serialize " + str(e))
     
    def UnPack_StandardEnvelope_And_Deserialize(self,ser_obj):
        try:
            myobj:SocketMessageEnvelope = pickle.loads(ser_obj)
            #self._ShowContent(myobj)
            if (myobj.ShowContentinLog or self.ShowJsonData):
                self._ShowEnvelope_Content(myobj)
            return myobj
        
        except Exception as e:
            self.LogConsole(self.LogPrefix() + " Error in UnPack_StandardEnvelope_And_Deserialize " + str(e))
            return None
        
# if (__name__== "__main__"):
    

    
