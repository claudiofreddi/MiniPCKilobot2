import socket
import threading
import time
import pickle
import uuid
from typing import cast
from Robot_Envs import *
from Lib_Sockets import * 
from Socket_Json import * 

class Robot_Socket_Client_Service(Robot_Socket_BaseClass):
    
    SimulOn = False
    
    EnableStdInText = True

    def __init__(self, ServiceName = "", ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort, False)    

    
    def SerializeObj_And_Send(self,Targetclient:socket, Obj:SocketObject):
        try:
                print(Obj.json())
                print(Obj.ClassType)
                myobj = SocketMessageEnvelope(Obj.ClassType,Obj.json()) 
                ser_obj = pickle.dumps(myobj,protocol=5) 
                print(len(ser_obj))
                self.client.send(ser_obj)
        except Exception as e:
            self.TraceLog("Client Error in SerializeObj_And_Send " + str(e))
    
    def Receive_And_DeserializedObj(self,Targetclient:socket):
        try:
            ser_obj = self.client.recv(self.buffer)
            print(ser_obj)
            print(len(ser_obj))
            myobj:SocketMessageEnvelope = pickle.loads(ser_obj)
            return myobj

        except Exception as e:
            self.TraceLog("Client Error in Receive_And_DeserializedObj " + str(e))
            
      
    
    def OnClient_Receive(self, client:socket, ObjToSend:SocketObject):
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
                    MySocketMessageEnv = self.Receive_And_DeserializedObj(self.client)
                    
                    if (MySocketMessageEnv != None):
                        
                        if (MySocketMessageEnv.ClassType == SocketObjectClassType.MESSAGE):
                            
                            MySocketObject = SocketObject(**SocketDecoder.get(MySocketMessageEnv.EncodedJson))
                            self.TraceLog("Client receive: " + str(MySocketObject.Message))
                                                    
                            if (MySocketObject.Message == self.SOCKET_LOGIN_MSG):                
                    
                                self.TraceLog("Client send: " + str(self.ServiceName))   
                                ObjToSend:SocketObject = SocketObject(SocketObjectClassType.MESSAGE,"",str(self.ServiceName),0,)
                                self.SerializeObj_And_Send(self.client, ObjToSend)         
                            
                            elif (MySocketObject.Message == self.SOCKET_QUIT_MSG): 
                                self.Quit()
                                
                            else:
                                #Other SocketObjectClassType.MESSAGE NOT MANAGED
                                #Pass Throught Child
                                self.OnClient_Receive(self.client,MySocketMessageEnv)
                        else:
                                #Other messages NOT MANAGED
                                self.TraceLog("OnClient_Receive -> " + MySocketMessageEnv.Message + " Type [" + MySocketMessageEnv.ClassType + "]")
                                self.OnClient_Receive(self.client,MySocketMessageEnv)   
                    else: 
                        #NoneType
                        self.TraceLog("None Type Message")  
                        self.Disconnect()
                        print("An error occured! Retry in 15 sec..")
                        time.sleep(15) #Wait 30 sec and retry        
                else:
                    #Connection Failed    
                    self.TraceLog("Client disconnected")  
                #NoneType
                    self.TraceLog("None Type Message")  
                    self.Disconnect()
                    print("An error occured! Retry in 15 sec..")
                    time.sleep(15) #Wait 30 sec and retry  
                        
                if(self.IsQuitCalled):
                    break #Exit While
                    
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
            print("got message " + message)
            ObjToSend:SocketObject = SocketObject(SocketObjectClassType.MESSAGE,"",str(self.ServiceName) + message)
            print("got message in  SocketObject " + ObjToSend.Message)
            self.SerializeObj_And_Send(self.client, ObjToSend)   
            print("end SerializeObj_And_Send")
                
            if (message == self.SOCKET_QUIT_MSG):
                self.TraceLog("write task terminated for " + self.ServiceName)
                break
        
    def simul(self):
        try:
            count = 0
            self.TraceLog("Simul Enabled")
            while True:
                time.sleep(5)
                message = self.ServiceName + " tick: " + str(count)
                ObjToSend:SocketObject = SocketObject(SocketObjectClassType.MESSAGE,"",message,0)
                self.SerializeObj_And_Send(self.client, ObjToSend)  
                count = count + 1
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
 