import socket
import threading
import time
from Lib_Utils_MyQ import * 
from Robot_Envs import * 
from Socket_Json import * 


        

class Robot_Socket_Server_Brain(Robot_Socket_BaseClass): 


    client_objects = []
    
        
    # SensorMessage List 
    MyListOfSensors = []
    
    def __init__(self,ServiceName = 'Server', ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort, True)
           
        self.Connect()    


    def SendToClient(self,TargetClient:socket, Obj:SocketContent_STANDARD): 
        try:
            SerializedObj = self.Pack_StardardEnvelope_And_Serialize(Obj)
            TargetClient.send(SerializedObj)
        except Exception as e:
            self.TraceLog("Server Error in SendToClient  " + str(e))
                  
    def GetFromClient(self,TargetClient:socket):
        try:
            ser_obj = TargetClient.recv(self.buffer)
            myobj = self.UnPack_StardardEnvelope_And_Deserialize(ser_obj)
            return myobj
        
        except Exception as e:
            if (str(e).find("connection was forcibly closed")==0):
                self.TraceLog("Server Error in GetFromClient " + str(e))
            return None    
    
    
       
    # List all servicenames
    def ListActiveservicenames(self):
        self.TraceLog("Active servicenames")
        c:client_object
        for c in self.client_objects:
            print(c.servicename)   


    def GetClientObject(self,client:socket)->client_object:
        
        c:client_object
        for c in self.client_objects:
            if (c.client == client):
                return c

    def Quit(self, client): 
        c:client_object = self.GetClientObject(client)
        ServiceName = c.servicename
        self.client_objects.remove(c)
        client.close()
        msg = '{} left!'.format(ServiceName)
        self.TraceLog(msg)
        ObjToSend:SocketContent_STANDARD = SocketContent_STANDARD(ClassType=SocketContent_STANDARD_Type.MESSAGE, SubClassType = '', UID = '',Message =msg,Value="",RefreshInterval=5,LastRefresh = 0, IsAlert=False, Error ="")
        self.broadcastObj(ObjToSend)
                     

    def broadcastObj(self,ObjToSend:SocketContent_STANDARD):
        c:client_object
        for c in self.client_objects:
            self.SendToClient (c.client, ObjToSend)
            
    def SensorUpdate(self,MySensorObject:SensorObject):
        print("Received Type SENSOR:" + MySensorObject.Key)
        found = False
        x:SensorObject
        for x in self.MyListOfSensors:
            if (x.key == MySensorObject.key):
                found = True
                x.Copy(MySensorObject)
                print(MySensorObject.Key + " copied")
                break
        if (not found):
            self.MyListOfSensors.put(MySensorObject)
            print(MySensorObject.Key + " added")
 
    # Handling Messages From Clients
    def handle(self,client:socket):
        ## Read Client Info from 
        CurrClientObject = self.GetClientObject(client)
        while True:
            try:
                ## Receive Message
                print("Server Handle ["+ CurrClientObject.servicename + "]  wait for message")
                MySocketMessageEnv:SocketMessageEnvelope = self.GetFromClient(client)
                print("Server Handle ["+ CurrClientObject.servicename + "] received of MsgType " + MySocketMessageEnv.ContentType)
                
                ##SocketObjectClassType.MESSAGE      
                if (MySocketMessageEnv.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                    
                                            
                    MySocketObject = SocketContent_STANDARD(**SocketDecoder.get(MySocketMessageEnv.EncodedJson))
                    print("Server Handle ["+ CurrClientObject.servicename + "] received  Message " + MySocketObject.Message)
                    
                    ## SEZIONE MESSAGGI
                    if (MySocketObject.ClassType== SocketContent_STANDARD_Type.MESSAGE):
                                            
                        if (MySocketObject.Message == self.SOCKET_QUIT_MSG):
                            self.TraceLog("Server Handle ["+ CurrClientObject.servicename + "]  Message Got: " + MySocketObject.Message + " from Unknown")
                            self.Quit(client)
                            break
                    
                        ##SocketObjectClassType.SENSOR      
                        if (MySocketObject.ClassType== SocketContent_STANDARD_Type.SENSOR):
                            
                            MySensorObject = SensorObject(**SocketDecoder.get(MySocketMessageEnv.EncodedJson))
                            self.TraceLog("Server Handle ["+ CurrClientObject.servicename + "]  Type " + MySensorObject.SubClassType + " Value " + str(MySensorObject.Value))
                            ##self.SensorUpdate(MySensorObject)
                            print("self.SensorUpdate(MySensorObject)")
                        
                        
                    else:    
                        
                        #Try as MESSAGE and resent to sender
                        MySocketObject = SocketContent_STANDARD(**SocketDecoder.get(MySocketMessageEnv.EncodedJson))
                        self.TraceLog("Server Handle ["+ CurrClientObject.servicename + "] Message Got: " + MySocketObject.Message + " [" + MySocketObject.Key + "]  from " + str(CurrClientObject.servicename))               
                        # confirm message
                        ObjToSend:SocketContent_STANDARD = SocketContent_STANDARD(SocketContent_STANDARD_Type.MESSAGE,"",MySocketObject.Message,0,"Message not recognized")
                        self.SendToClient(client,ObjToSend)
                    
            
                
            except Exception as e:
                self.TraceLog("Server Handle ["+ CurrClientObject.servicename + "] Error in handle() "  + str(e))
                
                self.Quit(client)
                break
           
    # Receiving / Listening Function
    def receive(self):
        
        self.TraceLog("Waiting for Clients...")
        
        
        try:
            
            while True:
                # Accept Connection
                client, address = self.ServerConnection.accept()
                self.TraceLog("Connected with {}".format(str(address)))
                ObjToSend:SocketContent_STANDARD = SocketContent_STANDARD(SocketContent_STANDARD_Type.MESSAGE,"","",self.SOCKET_LOGIN_MSG)
                self.SendToClient(client,ObjToSend)
                
                # Request And Store servicename
            
                MySocketMessageEnv:SocketMessageEnvelope = self.GetFromClient(client)
                if (MySocketMessageEnv.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                    
                    MySocketObject = SocketContent_STANDARD(**SocketDecoder.get(MySocketMessageEnv.EncodedJson))
                    
                    if (MySocketObject.ClassType ==SocketContent_STANDARD_Type.MESSAGE):
                        
                        servicename = MySocketObject.Message
                        self.TraceLog("Server Message Got: " + servicename)
                                    
                        myclient_object = client_object(client,servicename,address)
                        self.client_objects.append(myclient_object)
                        
                        self.TraceLog("servicename is {}".format(servicename))

                        # Start Handling Thread For Client
                        thread = threading.Thread(target=self.handle, args=(client,))
                        thread.start()
            
        except Exception as e:
            self.TraceLog("Server Error in receive() "  + str(e))
        
            
    def simul(self):
        count = 0
        self.TraceLog("Simul Enabled")
        while True:
            time.sleep(20)
            message = "Server Broad cast tick: " + str(count)
            ObjToSend:SocketContent_STANDARD = SocketContent_STANDARD(SocketMessageEnvelopeContentType.STANDARD,"","",message)
            self.broadcastObj(ObjToSend)
            
            count = count + 1
        
    def Run(self,SimulOn = False):
        self.receive()
        
        if (SimulOn):
            simul_thread = threading.Thread(target=self.simul)
            simul_thread.start()
        
if (__name__== "__main__"):
    
    MyRobot_Socket_Server_Brain = Robot_Socket_Server_Brain()
    
    MyRobot_Socket_Server_Brain.Run(True)