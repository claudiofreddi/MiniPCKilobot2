import socket
import threading
import time
from typing import cast
from Robot_Envs import *
from Lib_Sockets import * 
from Socket_Json import * 

class Robot_Socket_Client_Service(Robot_Socket_BaseClass):
    

    EnableStdInText = True
    OnClient_Core_Task_RETVAL_OK = 0
    OnClient_Core_Task_RETVAL_QUIT= 1
    OnClient_Core_Task_RETVAL_ERROR = -1

    def __init__(self, ServiceName = "", ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort, False)    

    
    def SendToServer(self,Obj:SocketMessage_Type_STANDARD, 
                        Target=SocketMessageEnvelopeTargetType.SERVER):
        try:
            SerializedObj = self.Pack_StandardEnvelope_And_Serialize(Obj=Obj,To=Target,From=self.ServiceName)
            self.client.send(SerializedObj)
            
        except Exception as e:
            self.TraceLog("Client Error in SendToServer  " + str(e))
    
    def ReceiveFromServer(self):
        try:
            ser_obj = self.client.recv(self.buffer)
            myobj = self.UnPack_StandardEnvelope_And_Deserialize(ser_obj)
            
            return myobj
        
        except Exception as e:
            self.TraceLog("Client Error in ReceiveFromServer " + str(e))
            return None
         
    def OnClient_Connect(self):
        print("OnClient_Connect")
    
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,IsMessageAlreayManaged=False):
        obj:SocketMessage_Type_STANDARD = ReceivedEnvelope.GetDecodedMessageObject()
        #print("OnClient_Receive: " + obj.Message + " [" + self.ServiceName + "]")
        
    def OnClient_Disconnect(self):
        print("OnClient_Disconnect")
        
    def OnClient_Quit(self):
        print("OnClient_Quit")
        
    # Listening to Server and Sending ServiceName
    def Client_Listening_Task(self):
        self.IsConnected = False
        LocalMsgPrefix = self.LogPrefix() + " from [Server]"
        while True:
            try:
                if (self.IsQuitCalled):
                    break
                
                #Retry conncetion if needed
                if (not self.IsConnected):
                    self.Connect()
                    self.OnClient_Connect()
                    
                #If OK talk
                if (self.IsConnected):

                    # Receive Message From Server
                    # If 'NICK' Send ServiceName
                    
                    ReceivedEnvelope = self.ReceiveFromServer()
                    self.TraceLog(LocalMsgPrefix + " received  Envelope  From " + ReceivedEnvelope.From + " To: " + ReceivedEnvelope.To)
                    
                    IsMessageAlreayManaged = False
                    
                    if (ReceivedEnvelope != None):
                        
                        
                        ReceivedMessage = ReceivedEnvelope.GetDecodedMessageObject()
                        self.TraceLog(LocalMsgPrefix + " received  Message " + ReceivedMessage.Message + " Value: " + str(ReceivedMessage.Value)
                                   + "  Class: " + ReceivedMessage.ClassType
                                   + "  SubClass: " + ReceivedMessage.SubClassType)
                                                  
                        if (ReceivedMessage.Message == self.SOCKET_LOGIN_MSG):                
                            
                            self.TraceLog("Client send Login Name: " + str(self.ServiceName))   
                            ObjToSend:SocketMessage_Type_STANDARD = SocketMessage_Type_STANDARD(ClassType=SocketMessage_Type_STANDARD_Type.MESSAGE, 
                                                                                        SubClassType = '', UID = '',Message =str(self.ServiceName),Value="",RefreshInterval=5,LastRefresh = 0, IsAlert=False, Error ="")
                            
                            self.SendToServer(ObjToSend)    
                            
                            IsMessageAlreayManaged = True   
                        
                        elif (ReceivedMessage.Message == self.SOCKET_QUIT_MSG): 
                            print("Quit Message Received")
                            self.OnClient_Quit()
                            self.Quit()
                            IsMessageAlreayManaged = True

                        #Send To Inherited Objcts
                        self.OnClient_Receive(ReceivedEnvelope,IsMessageAlreayManaged)   
                        
                    else: 
                        self.OnClient_Disconnect()
                        self.Disconnect()
                        if (self.IsQuitCalled == False):
                            print("An error occured! Retry in " + str(self.RETRY_TIME) + " sec..")
                            time.sleep(self.RETRY_TIME) #Wait 30 sec and retry 
                        else:
                            break       
                else:
                    #Connection Failed    
                 
                    self.OnClient_Disconnect()
                    self.Disconnect()
                    if (self.IsQuitCalled == False):
                        print("An error occured! Retry in " + str(self.RETRY_TIME) + " sec..")
                        time.sleep(self.RETRY_TIME) #Wait 30 sec and retry  
                    else:
                        print("Service Quitted")
                        break      
                    
            except Exception as e:
                
                self.TraceLog("Error in Client_Listening_Task()  " + str(e))
                                
                self.TraceLog("Client disconnected")  
                self.Disconnect()
               
                if (self.IsQuitCalled == False):
                    print("An error occured! Retry in " + str(self.RETRY_TIME) + " sec..")
                    time.sleep(self.RETRY_TIME) #Wait 30 sec and retry
                else:
                    break
    
    
    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
        
            #Default
            self.TraceLog(self.LogPrefix() + "Waiting for input...")
            message = '{}'.format(input(''))
            ObjToSend:SocketMessage_Type_STANDARD = SocketMessage_Type_STANDARD(ClassType=SocketMessage_Type_STANDARD_Type.MESSAGE, 
                                                                                            SubClassType = '', UID = '',Message =message)
            self.SendToServer( ObjToSend)   
        
            if (message == self.SOCKET_QUIT_MSG):
                self.OnClient_Quit()
                self.Quit()
                self.TraceLog("OnClient_Core_Task_Cycle terminated for " + self.ServiceName)
                return self.OnClient_Core_Task_RETVAL_QUIT

            return self.OnClient_Core_Task_RETVAL_OK
        
        except Exception as e:
            self.TraceLog(self.LogPrefix() + "Error in OnClient_Core_Task_Cycle()  " + str(e))
            return self.OnClient_Core_Task_RETVAL_ERROR
    
    def Client_Core_Task(self):
        try:
            while True:
                retval = self.OnClient_Core_Task_Cycle(self.IsQuitCalled) 
                if (self.IsQuitCalled or  retval == self.OnClient_Core_Task_RETVAL_QUIT):
                    self.Disconnect()
                    self.Quit()
        except Exception as e:
            self.TraceLog(self.LogPrefix() + "Error in OnClient_Core_Task()  " + str(e))
            return self.OnClient_Core_Task_RETVAL_ERROR
  
      
    def ClientSimulateSend(self):
        try:
            count = 0
            self.TraceLog("Simul Enabled")
            while True:
                time.sleep(5)
                message = self.ServiceName + " tick: " + str(count) + " SIMULATED !"
                ObjToSend:SocketMessage_Type_STANDARD = SocketMessage_Type_STANDARD(ClassType=SocketMessage_Type_STANDARD_Type.MESSAGE, 
                                                                                          SubClassType = '', UID = '',Message =message, Value="",RefreshInterval=5,LastRefresh = 0, IsAlert=False, Error ="")
                self.SendToServer(ObjToSend)  
                count = count + 1
                if (self.IsQuitCalled):
                    print("Simul Quit")
                    break
        except Exception as e:
            self.TraceLog("Error in simul()  " + str(e))
        
    def Run_Threads(self,SimulOn = False):
        # Starting Threads For Listening And Writing
        receive_thread = threading.Thread(target=self.Client_Listening_Task)
        receive_thread.start()
        
        if (self.EnableStdInText):
            self.TraceLog("Write Thread Enabled")
            write_thread = threading.Thread(target=self.Client_Core_Task)
            write_thread.start()
        else:
            self.TraceLog("Write Thread Disabled")
        
        if (SimulOn):
            simul_thread = threading.Thread(target=self.ClientSimulateSend)
            simul_thread.start()
        
  
        
if (__name__== "__main__"):
    
    for i in range(1):
        MyRobot_Socket_Client_Service =  Robot_Socket_Client_Service("Servizio " + str(i))
        MyRobot_Socket_Client_Service.Run_Threads(False)      
 