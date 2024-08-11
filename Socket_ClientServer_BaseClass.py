from __future__ import annotations

import socket

from Robot_Envs import * 
import uuid
import pickle

from  Socket_Send_Receive import *
from Socket_ConsoleLog import * 
from Socket_Messages import * 

class Socket_Services_List:
    SERVER = "Server"
    SENSORS = "SENSORS_Client"
    KEYBOARD = "KEYBOARD_Client"
    USERINTERFACE = "UI_Client"
    REMOTE = "REMOTE_Client"
    SAMPLE = "Client_Sample"
    WEBCAM = "WEBCAM" 
        



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
    
    MySocket_SendReceive = Socket_SendReceive()
    UseMySocket_SendReceive = True
    
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
            
            ser_obj = pickle.dumps(MyEnv) 
                
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
    

    
