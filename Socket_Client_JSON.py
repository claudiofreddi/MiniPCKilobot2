import socket
import threading
import time
from typing import cast
from Robot_Envs import *
from Lib_Sockets import * 
from Socket_Json import * 

class Robot_Socket_Client_Service(Robot_Socket_BaseClass):
    
    SimulOn = False
    
    EnableStdInText = True

    def __init__(self, ServiceName = "", ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort, False)    

    
    def SendToServer(self,Obj:SocketContent_STANDARD):
        try:
            SerializedObj = self.Pack_StardardEnvelope_And_Serialize(Obj)
            self.client.send(SerializedObj)
        except Exception as e:
            if (str(e).find("something that is not a socket")==0):
                self.TraceLog("Client Error in SendToServer  " + str(e))
    
    def ReceiveFromServer(self):
        try:
            ser_obj = self.client.recv(self.buffer)
            myobj = self.UnPack_StardardEnvelope_And_Deserialize(ser_obj)
            return myobj
        
        except Exception as e:
            if (str(e).find("connection was forcibly closed")==0):
                self.TraceLog("Client Error in ReceiveFromServer " + str(e))
            return None
         

    
    def OnClient_Receive(self, client:socket, ObjToSend:SocketContent_STANDARD):
        print("OnClient_Receive")
        
    
        
    # Listening to Server and Sending ServiceName
    def receive(self):
        self.IsConnected = False

        while True:
            try:
                #Retry conncetion if needed
                if (not self.IsConnected):
                    self.Connect()
                
                #If OK talk
                if (self.IsConnected):

                    # Receive Message From Server
                    # If 'NICK' Send ServiceName
                    MySocketMessageEnv = self.ReceiveFromServer()
                    
                    if (MySocketMessageEnv != None):
                        
                        if (MySocketMessageEnv.ContentType  == SocketMessageEnvelopeContentType.STANDARD):
                            
                            MySocketObject = SocketContent_STANDARD(**SocketDecoder.get(MySocketMessageEnv.EncodedJson))
                            self.TraceLog("Client receive: " + str(MySocketObject.Message))
                                                    
                            if (MySocketObject.Message == self.SOCKET_LOGIN_MSG):                
                                
                                self.TraceLog("Client send: " + str(self.ServiceName))   
                                ObjToSend:SocketContent_STANDARD = SocketContent_STANDARD(ClassType=SocketContent_STANDARD_Type.MESSAGE, 
                                                                                          SubClassType = '', UID = '',Message =str(self.ServiceName),Value="",RefreshInterval=5,LastRefresh = 0, IsAlert=False, Error ="")
                                self.SendToServer(ObjToSend)         
                            
                            elif (MySocketObject.Message == self.SOCKET_QUIT_MSG): 
                                print("Quit Message Received")
                                self.Quit()
                                
                            else:
                                #Other SocketObjectClassType.MESSAGE NOT MANAGED
                                #Pass Throught Child
                                self.OnClient_Receive(self.client,MySocketMessageEnv)
                        else:
                                #Other messages NOT MANAGED
                                self.TraceLog("OnClient_Receive -> " + MySocketMessageEnv.Message + " Type [" + MySocketMessageEnv.ContentType + "]")
                                self.OnClient_Receive(self.client,MySocketMessageEnv)   
                    else: 
                     
                        self.Disconnect()
                        if (self.IsQuitCalled == False):
                            print("An error occured! Retry in 15 sec..")
                            time.sleep(15) #Wait 30 sec and retry 
                        else:
                            break       
                else:
                    #Connection Failed    
                    self.TraceLog("Client disconnected")  
                    self.Disconnect()
                    if (self.IsQuitCalled == False):
                        print("An error occured! Retry in 15 sec..")
                        time.sleep(15) #Wait 30 sec and retry  
                    else:
                        print("Service Quitted")
                        break      
                    
            except Exception as e:
                
                self.TraceLog("Error in receive()  " + str(e))
                
                self.Disconnect()
               
                if (self.IsQuitCalled == False):
                    print("An error occured! Retry in 15 sec..")
                    time.sleep(15) #Wait 30 sec and retry
                else:
                    break
    

                                
    # Sending Messages To Server
    def write(self):
        while True:
            
          
            #Default
            message = '{}'.format(input(''))
            
          
            ObjToSend:SocketContent_STANDARD = SocketContent_STANDARD(ClassType=SocketContent_STANDARD_Type.MESSAGE, 
                                                                                          SubClassType = '', UID = '',Message =str(self.ServiceName) + message, Value="",RefreshInterval=5,LastRefresh = 0, IsAlert=False, Error ="")
            
            self.SendToServer( ObjToSend)   
            
                
            if (message == self.SOCKET_QUIT_MSG):
                self.Quit()
                self.TraceLog("write task terminated for " + self.ServiceName)
                break
        
    def simul(self):
        try:
            count = 0
            self.TraceLog("Simul Enabled")
            while True:
                time.sleep(5)
                message = self.ServiceName + " tick: " + str(count)
                ObjToSend:SocketContent_STANDARD = SocketContent_STANDARD(ClassType=SocketContent_STANDARD_Type.MESSAGE, 
                                                                                          SubClassType = '', UID = '',Message =message, Value="",RefreshInterval=5,LastRefresh = 0, IsAlert=False, Error ="")
                self.SendToServer(ObjToSend)  
                count = count + 1
                if (self.IsQuitCalled):
                    print("Simul Quit")
                    break
        except Exception as e:
            self.TraceLog("Error in simul()  " + str(e))
        
    def Run(self):
        # Starting Threads For Listening And Writing
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        
        if (self.EnableStdInText):
            self.TraceLog("Write Thread Enabled")
            write_thread = threading.Thread(target=self.write)
            write_thread.start()
        else:
            self.TraceLog("Write Thread Disabled")
        
        if (self.SimulOn):
            simul_thread = threading.Thread(target=self.simul)
            simul_thread.start()
        
  
        
if (__name__== "__main__"):
    
    for i in range(1):
        MyRobot_Socket_Client_Service =  Robot_Socket_Client_Service("Servizio " + str(i))
        MyRobot_Socket_Client_Service.SimulOn = True
        MyRobot_Socket_Client_Service.Run()      
 