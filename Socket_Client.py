import socket
import threading
import time
import pickle
import uuid
from typing import cast
from Robot_Envs import *
from Lib_Sockets import * 
from Socket_Json import * 

class Robot_Socket_Client_Service:
    # Choosing ServiceName
    ServiceName:str = ""
    ServerIP = SOCKET_SERVER_IP
    ServerPort = SOCKET_SERVER_PORT
    client = None
    buffer = SOCKET_BUFFER
    IsExitCalled = False
    IsConnected = False
    SimulOn = False
    ShowNormalTrace = True
    EnableStdInText = True

    def __init__(self, ServiceName = "", ForceServerIP = '',ForcePort=''):
        
        # Starting Server
        if (ForceServerIP!= ''):
            self.ServerIP = ForceServerIP
            
        if (ForcePort!= ''):
            self.ServerPort = ForcePort  
        
        if (ServiceName != ""):
            self.ServiceName = ServiceName
        else:
            #Assign Random
            self.ServiceName = str(uuid.uuid4())
        
            self.TraceLog("init Service: " + str(self.ServiceName))    
    
    
    def SerializeObj_And_Send(self,client:socket, myobj):
        try:
            ser_obj = pickle.dumps(myobj,protocol=5) 
            if (self.IsConnected):
                self.client.send(ser_obj)
            else:
                self.TraceLog("Not Connected") 
        except Exception as e:
            self.TraceLog("Client Error in SerializeObj_And_Send " + str(e))
    
    def Receive_And_DeserializedObj(self,client:socket):
        try:
            #if (self.IsConnected):
            ser_obj = self.client.recv(self.buffer)
            myobj = pickle.loads(ser_obj)
            return myobj
            # else:
            #     self.TraceLog("Not Connected")    
            #     return None
        except Exception as e:
            self.TraceLog("Client Error in Receive_And_DeserializedObj " + str(e))
            return None
      
    def OnClient_Receive(self, client:socket, DeserializedMsgObj:any):
        print("OnClient_Receive")
         
    
        
    # Listening to Server and Sending ServiceName
    def receive(self):
        self.IsConnected = False

        while True:
            if (self.IsExitCalled):
                self.TraceLog("receive task terminated")
                break
            try:
                if (self.IsConnected == False):
                    # Connecting To Server
                    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client.connect((self.ServerIP, self.ServerPort))
                    self.IsConnected = True
            
            
                # Receive Message From Server
                # If 'NICK' Send ServiceName
                MyReceivedObj = self.Receive_And_DeserializedObj(self.client)
                
                if (MyReceivedObj == None):
                    self.TraceLog("Client received None Msg")
                else:
                    message = MyReceivedObj.Message
                    
                    self.TraceLog("Client receive: " + str(message))
                    
                    if (message == SOCKET_LOGIN_MSG):            
                        self.TraceLog("Client send: " + str(self.ServiceName))   
                        ObjToSend:SimpleMessage = SimpleMessage(str(self.ServiceName))
                        self.SerializeObj_And_Send(self.client, ObjToSend)         
                    
                    elif (message == SOCKET_QUIT_MSG): 
                        self.Quit()
                    
                    else:
                        if (self.IsConnected):
                            if (MyReceivedObj.Message != ""):
                                
                                if (MyReceivedObj.Type == BaseMsgClassTypes.SENSOR):
                                
                                    MyReceivedObj = cast(SensorMessage,MyReceivedObj)     
                                
                                self.TraceLog("OnClient_Receive -> " + MyReceivedObj.Message + " " + str(MyReceivedObj.IntValue))
                                self.OnClient_Receive(self.client,MyReceivedObj)
                
                   
                    
            except Exception as e:
                
                print (e)
                
                self.Disconnect()
               
                if (self.IsExitCalled == False):
                    print("An error occured! Retry in 15 sec..")
                    time.sleep(15) #Wait 30 sec and retry
                else:
                    break
    
    def Quit(self):
        self.TraceLog("Quitting..")
        self.IsConnected = False
        self.client.close()
        self.IsExitCalled = True
        self.TraceLog("receive task terminated for " + self.ServiceName )
            
    def Disconnect(self):
        self.TraceLog("Disconnecting..")
        self.IsConnected = False
        self.client.close()
                                
    # Sending Messages To Server
    def write(self):
        while True:
            
          
            #Default
            message = '{}'.format(input(''))
            ObjToSend:SimpleMessage = SimpleMessage(message)
            self.SerializeObj_And_Send(self.client, ObjToSend)   

                
            if (message == SOCKET_QUIT_MSG):
                self.TraceLog("write task terminated for " + self.ServiceName)
                break
        
    def simul(self):
        count = 0
        self.TraceLog("Simul Enabled")
        while True:
            time.sleep(5)
            message = self.ServiceName + " tick: " + str(count)
            ObjToSend:SimpleMessage = SimpleMessage(message)
            self.SerializeObj_And_Send(self.client, ObjToSend)  
            count = count + 1
    
    
     
    def Client_Send(self, client:socket, DeserializedMsgObj:any):
        self.SerializeObj_And_Send(client, DeserializedMsgObj) 
         
    
    def IsTraceLogEnabled(self) -> bool:
        return self.ShowNormalTrace
    
    def TraceLog(self, Text):
        if (self.IsTraceLogEnabled()):
            print(Text)

        
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
    
    MyRobot_Socket_Client_Service =  Robot_Socket_Client_Service("")
    MyRobot_Socket_Client_Service.SimulOn = True
    MyRobot_Socket_Client_Service.Run()

           
    MyRobot_Socket_Client_Service =  Robot_Socket_Client_Service("Test")
    MyRobot_Socket_Client_Service.SimulOn = True
    MyRobot_Socket_Client_Service.Run()      
    
    