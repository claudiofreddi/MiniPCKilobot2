from __future__ import annotations
import json
import socket
from json import JSONEncoder
from Robot_Envs import * 
import uuid
import pickle
import time

### ***************************************************************************
### LOG DEF
### ***************************************************************************

class  ConsoleLogLevel:
    
    Test = 0
    CurrentTest = 1
    
    System = 2
    Control = 3
    Always = 4
    Override_Call = 6
    Socket_Flow = 5 
    Show = 7
    
    Error = 90

class Common_LogConsoleClass(object):
    EnableConsoleLog = True
    EnableAll = False
    EnableConsoleLogLevels = [
                              ConsoleLogLevel.Error   #keep always on
                              #,ConsoleLogLevel.Test
                              ,ConsoleLogLevel.CurrentTest #keep on temporary
                              ,ConsoleLogLevel.System
                              ,ConsoleLogLevel.Control
                              ,ConsoleLogLevel.Always
                              #,ConsoleLogLevel.Override_Call
                              #,ConsoleLogLevel.Socket_Flow
                              ,ConsoleLogLevel.Show    #keep on
                              
                              ]
    

    
    def LogConsole(self,Text,*LogLevels):
        
        if (self.EnableConsoleLog):
            
            if (self.EnableAll):
                print(Text) 
                
            else:
                if (len(LogLevels) == 0):
                    #Test is Default
                    LogLevel = ConsoleLogLevel.Test
                  
                    for v in self.EnableConsoleLogLevels:
                        if (v == LogLevel):
                            print(Text)
                            break
                            
                else:
                    for LogLevel in LogLevels:
                        for v in self.EnableConsoleLogLevels:
                            if (v == LogLevel):
                                print(Text)
                                break
        
### ***************************************************************************
### Ecoder e Decoder (JSON <-> Class)
### ***************************************************************************
class SocketEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__  

class SocketDecoder:
    def get(CodedJson):
        return  json.loads(CodedJson)

  
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
    SAMPLE = "Client_Sample"


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
    
    def _ShowStdMessageJsonForma(self):
        self.LogConsole(self.json(),ConsoleLogLevel.Control)
        
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
            
    def GetReceivedMessage(self)->Socket_Default_Message:
                  
        ReceivedMsg:Socket_Default_Message = Socket_Default_Message(**SocketDecoder.get(self.EncodedJson))    
        
        return ReceivedMsg

    def GetEnvelopeDescription(self) -> str:
        return "Envelope [" + self.ContentType + "] From " + self.From + " To: " + self.To 

class Socket_ClientServer_BaseClass(Common_LogConsoleClass):
     # Connection Data
    ServerIP = ''
    ServerPort = SOCKET_SERVER_PORT
    buffer = SOCKET_BUFFER
    ServiceName:str = ""
    IsServer:bool = False
    ServerConnection:socket = None
    client:socket
    IsConnected = False
    IsQuitCalled = False
    
    
    SOCKET_QUIT_MSG = "Quit"
    SOCKET_LOGIN_MSG = "AskForServiceName"
    RETRY_TIME = 3
    
    def ServerIPToUse(self)-> str:
        if (SOCKET_USE_LOCALHOST == 1):
            self.LogConsole("Using Localhost  IP: "+ SOCKET_SERVER_LOCALHOST_IP,ConsoleLogLevel.Always)
            return SOCKET_SERVER_LOCALHOST_IP, True
        else:
            if (SOCKET_SERVER_IP_REMOTE !="" ):
                self.LogConsole("Using Forced IP: "+ SOCKET_SERVER_IP_REMOTE,ConsoleLogLevel.Always)
                return SOCKET_SERVER_IP_REMOTE, True
            else:
                if (SOCKET_THIS_IS_SERVER_MACHINE == 1):
                    #GetThis Machine IP
                    ThisMachineIP = socket.gethostbyname(socket.gethostname())
                    self.LogConsole("Using Local Machine IP: "+ ThisMachineIP,ConsoleLogLevel.Always)
                    return ThisMachineIP, True
                else:
                    Err = "This May be a Remote Client. Please configure SOCKET_SERVER_IP_REMOTE"
                    self.LogConsole(Err,ConsoleLogLevel.Always)
                    return Err, False

    
    def __init__(self,ServiceName = '', ForceServerIP = '',ForcePort='', IsServer=False):
            
            self.IsServer = IsServer
            
            # Starting Server
            if (ForceServerIP!= ''):
                self.ServerIP = ForceServerIP
            else:
                IPToUse , isValid =self. ServerIPToUse()
                if (isValid):
                    self.ServerIP = IPToUse
                else:
                    self.LogConsole("Can't find IP. Quitting",ConsoleLogLevel.Always)
                    self.Quit()
                
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
                self.LogConsole(self.ServiceName + " started on " + self.ServerIP + ":" + str(self.ServerIP) + " buffer:" +  str(self.buffer),ConsoleLogLevel.Socket_Flow) 
            else:
                self.LogConsole("init Service: " + str(self.ServiceName),ConsoleLogLevel.Socket_Flow)         
            
    
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
                self.LogConsole("Error in Connect()  " + str(e),ConsoleLogLevel.Error)
            self.IsConnected = False
            return False
    
    def Disconnect(self):
        
        self.IsConnected = False
        if (self.IsServer):
            self.ServerConnection.close()
        else:
            self.client.close()     
               
        self.LogConsole(self.ThisServiceName() + "  Disconnected",ConsoleLogLevel.Socket_Flow)   
    
    def Quit(self):
        
        try:
            self.LogConsole(self.ThisServiceName() + "  Quitted",ConsoleLogLevel.Socket_Flow) 
            self.Disconnect()
            if (self.IsServer):
                self.ServerConnection.close()
                
            else:
                self.client.close()
              
            
               
            self.IsConnected = False
            self.IsQuitCalled = True
         
            
        except Exception as e:
            self.LogConsole("Error in Quit()  " + str(e),ConsoleLogLevel.Socket_Flow)
                                    
 

    
    
    def ThisServiceName(self)->str:
        return " [" + self.ServiceName + "] "
        
    

    
    
    def Prepare_StandardEnvelope(self,MsgToSend:Socket_Default_Message,From="",To=""):
        try:
            
            MyEnvelope =  SocketMessageEnvelope("",SocketMessageEnvelopeContentType.STANDARD,MsgToSend.json(),From=From if (From!='') else self.ServiceName,To=To) 
            
            return MyEnvelope

        except Exception as e:
            self.LogConsole(self.ThisServiceName() + " Error in Pack_StardardEnvelope_And_Serialize " + str(e),ConsoleLogLevel.Error)

           
    def Pack_Envelope_And_Serialize(self,MyEnv:SocketMessageEnvelope):
        try:
            
            ser_obj = pickle.dumps(MyEnv,protocol=5) 
            
            #Alert if Buffer too little
            if (len(ser_obj) > self.buffer):
                self.LogConsole(self.ThisServiceName() + " Increment Buffer Size [" + str(self.buffer) + "]. Curr Envelope Size is " + str(len(ser_obj)),ConsoleLogLevel.Error )
              
                
            return ser_obj
        
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + " Error in Pack_StardardEnvelope_And_Serialize " + str(e),ConsoleLogLevel.Error)
     
    def UnPack_StandardEnvelope_And_Deserialize(self,ser_obj):
        try:
            myobj:SocketMessageEnvelope = pickle.loads(ser_obj)
            
            return myobj
        
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + " Error in UnPack_StandardEnvelope_And_Deserialize " + str(e),ConsoleLogLevel.Error)
            return None
        
# if (__name__== "__main__"):
    

    
