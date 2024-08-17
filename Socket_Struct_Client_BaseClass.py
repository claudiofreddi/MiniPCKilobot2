from socket import *
import threading
import time
from typing import cast
from Robot_Envs import *
#from Lib_Sockets import * 
from Socket_Struct_ClientServer_BaseClass import * 
import struct

class Socket_Client_BaseClass(Socket_ClientServer_BaseClass):

    OnClient_Core_Task_RETVAL_OK = 0
    OnClient_Core_Task_RETVAL_QUIT= 1
    OnClient_Core_Task_RETVAL_ERROR = -1

    def __init__(self, ServiceName = "", ForceServerIP = '',ForcePort='',LogOptimized=False):
        super().__init__(ServiceName,ForceServerIP,ForcePort, False,LogOptimized)    
        self.DisconnectCount = 0
        
    
    def SendToServer(self,MyMsg:Socket_Default_Message, 
                        Target=SocketMessageEnvelopeTargetType.SERVER,AdditionaByteData=b''):
        
        try:
            
            MyEnvelope:SocketMessageEnvelope = self.Prepare_StandardEnvelope(MsgToSend=MyMsg,To=Target,From=self.ServiceName)
            
            self.LogConsole("Client ["+ self.ServiceName + "] SendToServer: " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
            
            self.LogConsole("Client ["+ self.ServiceName + "] SendToServer: " + MyMsg.GetMessageDescription(),ConsoleLogLevel.Socket_Flow)
            
            SerializedObj = self.Pack_Envelope_And_Serialize(MyEnvelope)
           
            self.MySocket_SendReceive.send_msg(self.client,SerializedObj,AdditionaByteData)

            
        except Exception as e:
            self.LogConsole("Client Error in SendToServer  " + str(e))
    
    def ReceiveFromServer(self):
        try:
            MyEnvelope:SocketMessageEnvelope  = None
            
            ser_obj,AdditionaByteData,retval = self.MySocket_SendReceive.recv_msg(self.client)
            
            
            if (len(ser_obj)>0):
                MyEnvelope = self.UnPack_StandardEnvelope_And_Deserialize(ser_obj)
                
                self.LogConsole("Client ["+ self.ServiceName + "] ReceiveFromServer: " + MyEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
                
            return MyEnvelope,AdditionaByteData 

        
        except Exception as e:
            self.LogConsole("Client Error in ReceiveFromServer " + str(e),ConsoleLogLevel.Error)
            return None, b''
         
    def OnClient_Connect(self):
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
        
    def On_ClientAfterLogin(self):
        self.LogConsole("On_ClientAfterLogin()",ConsoleLogLevel.Override_Call)
    
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreayManaged=False):
        #ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
        pass
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
        
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call)
        
    # Listening to Server and Sending ServiceName
    def Client_Listening_Task(self):
        self.IsConnected = False
        
        while True:
            try:
                self.SleepTime(Multiply=3,CalledBy="Client_Listening_Task",Trace=False)
                
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
                    
                    ReceivedEnvelope, AdditionaByteData = self.ReceiveFromServer()
                    if (ReceivedEnvelope != None):
                        self.LogConsole("Client ["+ self.ServiceName + "] ReceiveFromServer: " + ReceivedEnvelope.GetEnvelopeDescription(),ConsoleLogLevel.Socket_Flow)
                    
                    IsMessageAlreayManaged = False                   
                    if (ReceivedEnvelope != None):
                        
                        
                        ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                                                 
                        if (ReceivedMessage.Message == self.SOCKET_LOGIN_MSG):                
                            
                            self.LogConsole("Client send Login Name: " + str(self.ServiceName))   
                            ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.LOGIN
                                                                                        ,UID = ''
                                                                                        ,Message =str(self.ServiceName),Value="",RefreshInterval=5
                                                                                        ,LastRefresh = 0, IsAlert=False, Error ="")
                            
                            self.SendToServer(ObjToSend)    
                            
                            self.On_ClientAfterLogin()
                            
                            IsMessageAlreayManaged = True   
                        
                        elif (ReceivedMessage.Message == self.SOCKET_QUIT_MSG): 
                            self.LogConsole("Quit Message Received",ConsoleLogLevel.System)
                            self.OnClient_Quit()
                            self.Quit()
                            IsMessageAlreayManaged = True

                        #Send To Inherited Objcts
                        self.OnClient_Receive(ReceivedEnvelope=ReceivedEnvelope,AdditionaByteData=AdditionaByteData,IsMessageAlreayManaged=IsMessageAlreayManaged)   
                        
                    else: 
                        if (self.ForceDisconnect()):               
                            break      
                else:
                    #Connection Failed    
                    if (self.ForceDisconnect()):               
                        break   
                    
            except Exception as e:
                
                self.LogConsole("Error in Client_Listening_Task()  " + str(e),ConsoleLogLevel.Error)
                
                if (self.ForceDisconnect()):               
                     break
                 
    
    def ForceDisconnect(self):
        self.DisconnectCount += 1
        self.LogConsole(f"Client disconnecting [{self.DisconnectCount}] ...",ConsoleLogLevel.System)  
        self.OnClient_Disconnect()
        self.Disconnect()
        
        if (self.IsQuitCalled == False):
            self.LogConsole("An error occured! Retry in " + str(self.RETRY_TIME) + " sec..",ConsoleLogLevel.System)
            time.sleep(self.RETRY_TIME) #Wait 30 sec and retry
            return False
        else:
            self.LogConsole("Service Quitted",ConsoleLogLevel.System)
            return True

        
        
    
    def RegisterTopics(self, *ClientTopics):
        for t in ClientTopics:
            try:
                
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_ADD
                                                                        , UID = '',Message = t)
                self.SendToServer( ObjToSend)   
            
            except Exception as e:
                self.LogConsole(self.ThisServiceName() + "Error in RegisterTopics()  " + str(e),ConsoleLogLevel.Error)
                
    def SubscribeTopics(self, *TopicsToSubscribe):
        for t in TopicsToSubscribe:
            try:
                
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_SUBSCRIBE
                                                                        , UID = '',Message = t)
                self.SendToServer( ObjToSend)   
            
            except Exception as e:
                self.LogConsole(self.ThisServiceName() + "Error in RegisterTopics()  " + str(e),ConsoleLogLevel.Error)
                

    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
            
            
            # #Default
            # self.LogConsole(self.ThisServiceName() + "Waiting for input...",ConsoleLogLevel.Test)
            # message = '{}'.format(input(''))
            # ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.MESSAGE
            #                                                             , UID = '',Message =message)
            # self.SendToServer( ObjToSend)   
        
            # if (message == self.SOCKET_QUIT_MSG):
            #     self.OnClient_Quit()
            #     self.Quit()
            #     self.LogConsole("OnClient_Core_Task_Cycle terminated for " + self.ServiceName,ConsoleLogLevel.System)
            #     return self.OnClient_Core_Task_RETVAL_QUIT

            return self.OnClient_Core_Task_RETVAL_OK
        
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
    def Client_Core_Task(self):
        try:
            while True:
                self.SleepTime(Multiply=1,CalledBy="OnClient_Core_Task_Cycle",Trace=False)
                retval = self.OnClient_Core_Task_Cycle(self.IsQuitCalled) 
                if (self.IsQuitCalled or  retval == self.OnClient_Core_Task_RETVAL_QUIT):
                    
                    self.Disconnect()
                    self.Quit()
                    
                    break
                
                if (retval == self.OnClient_Core_Task_RETVAL_ERROR):
                    self.LogConsole(self.ThisServiceName() + " Error in Inner - Client_Core_Task () Break " + str(e),ConsoleLogLevel.System)
                    break
                
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in Inner - OnClient_Core_Task()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
  
      
    def ClientSimulateSend(self):
        try:
            count = 0
            self.LogConsole("Simul Enabled",ConsoleLogLevel.Test)
            while True:
                time.sleep(5)
                message = self.ServiceName + " tick: " + str(count) + " SIMULATED !"
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.MESSAGE
                                                                                          , UID = '',Message =message, 
                                                                                          Value="",RefreshInterval=5,
                                                                                          LastRefresh = 0, IsAlert=False, Error ="")
                self.SendToServer(ObjToSend)  
                count = count + 1
                if (self.IsQuitCalled):
                    self.LogConsole("Simul Quit",ConsoleLogLevel.System)
                    break
        except Exception as e:
            self.LogConsole("Error in simul()  " + str(e),ConsoleLogLevel.Error)
        
    def Run_Threads(self,SimulOn = False):
        # Starting Threads For Listening And Writing
        receive_thread = threading.Thread(target=self.Client_Listening_Task)
        receive_thread.start()
        
        receive_thread = threading.Thread(target=self.Client_Core_Task)
        receive_thread.start()
        
        if (SimulOn):
            simul_thread = threading.Thread(target=self.ClientSimulateSend)
            simul_thread.start()
        
  
        
if (__name__== "__main__"):
    
    for i in range(1):
        MySocket_Client_BaseClass =  Socket_Client_BaseClass("Servizio " + str(i))
        MySocket_Client_BaseClass.Run_Threads(False)      
 