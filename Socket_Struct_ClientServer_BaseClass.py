from __future__ import annotations

from  socket import * 

from Robot_Envs import * 
import uuid
import pickle

from Socket_Utils_Send_Receive import *
from Socket_Utils_ConsoleLog import * 
from Socket_Struct_Messages import * 

class Socket_Services_List:
    SERVER = "SERVER"
    SENSORS = "SENSORS_Client"
    KEYBOARD = "KEYBOARD_Client"
    USERINTERFACE = "UI_Client"
    REMOTE = "REMOTE_Client"
    SAMPLE = "SAMPLE_Client"
    WEBCAM = "WEBCAM_Client" 
    SPEAKER = "SPEAKER_Client"
    ACTUATORS = "ACTUATORS_Client"
    TELEGRAM = "TELEGRAM_Client"
    ARDUINO_READ_WRITE = "ARDUINO_READ_WRITE_TEST_Client"
    LIDAR = "LIDAR_Client"



class Socket_ClientServer_BaseClass(Common_LogConsoleClass):
     # Connection Data
    ServerIP = ''
    ServerPort = SOCKET_SERVER_PORT
    buffer = SOCKET_BUFFER
    ServiceName:str = ""
    IsServer:bool = False
    ServerConnection:socket
    client:socket
    IsConnected = False
    IsQuitCalled = False
    
    
    SOCKET_QUIT_MSG = "Quit"
    SOCKET_LOGIN_MSG = "AskForServiceName"
    RETRY_TIME = 8
    
    SLEEP_TIME:float = 0.0 #time.sleep(self.SLEEP_TIME)
    
    MySocket_SendReceive = Socket_SendReceive()
    
    def SleepTime(self, Multiply:float=1.0,CalledBy="",Trace=False):
        sec:float= self.SLEEP_TIME*Multiply
        time.sleep(sec)
        if (Trace): self.LogConsole("SLEEP_TIME Called By: " + CalledBy,ConsoleLogLevel.SleepTime)
    
    def ServerIPToUse(self)-> str:
        if (SOCKET_USE_LOCALHOST == 1):
            self.LogConsole(self.ServiceName + " Using Localhost  IP: "+ SOCKET_SERVER_LOCALHOST_IP,ConsoleLogLevel.Always)
            return SOCKET_SERVER_LOCALHOST_IP, True
        else:
            if (SOCKET_SERVER_IP_REMOTE !="" ):
                self.LogConsole(self.ServiceName + " Using Forced IP: "+ SOCKET_SERVER_IP_REMOTE,ConsoleLogLevel.Always)
                return SOCKET_SERVER_IP_REMOTE, True
            else:
                if (SOCKET_THIS_IS_SERVER_MACHINE == 1):
                    #GetThis Machine IP
                    ThisMachineIP = socket.gethostbyname(socket.gethostname())
                    self.LogConsole(self.ServiceName + " Using Local Machine IP: "+ ThisMachineIP,ConsoleLogLevel.Always)
                    return ThisMachineIP, True
                else:
                    Err = self.ServiceName + " This May be a Remote Client. Please configure SOCKET_SERVER_IP_REMOTE"
                    self.LogConsole(Err,ConsoleLogLevel.Always)
                    return Err, False

    
    def __init__(self,ServiceName = '', ForceServerIP = '',ForcePort='', IsServer=False,LogOptimized=False):
            
            self.RunOptimized = LogOptimized
            
            self.IsServer = IsServer
            
            if (ServiceName != ''):
                self.ServiceName = ServiceName
            
            # Starting Server
            if (ForceServerIP!= ''):
                self.ServerIP = ForceServerIP
            else:
                IPToUse , isValid =self.ServerIPToUse()
                if (isValid):
                    self.ServerIP = IPToUse
                else:
                    self.LogConsole("Can't find IP. Quitting",ConsoleLogLevel.Always)
                    self.Quit()
                
            if (ForcePort!= ''):
                self.ServerPort = ForcePort  
                
            if (ServiceName == ''):
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
            
            self.LogConsole(self.ServiceName + " Connected!",ConsoleLogLevel.System)
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
               
        self.LogConsole(self.ThisServiceName() + "  Disconnected",ConsoleLogLevel.System)   
    
    def Quit(self):
        
        try:
            self.LogConsole(self.ThisServiceName() + "  Quitted",ConsoleLogLevel.System) 
            self.Disconnect()
            if (self.IsServer):
                self.ServerConnection.close()
                
            else:
                self.client.close()
                         
            self.IsConnected = False
            self.IsQuitCalled = True
         
            
        except Exception as e:
            self.IsQuitCalled = True
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
        

    

    
