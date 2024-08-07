import socket
import threading
import time
import pickle

from Robot_Envs import * 
from Lib_Sockets import * 

from Lib_Commands_Interfaces import *
from Lib_Utils_MyQ import *



class client_object:
    client:socket = None
    servicename:str = ''
    address = ('',0)
    
    def __init__(self):
        pass
    
    def __init__(self,Client:socket, ServiceName:str, Address):
        self.client = Client
        self.servicename = ServiceName
        self.address = Address

        

class Robot_Socket_Server_Brain: 


    # Connection Data
    ServerIP = SOCKET_SERVER_IP
    ServerPort = SOCKET_SERVER_PORT
    buffer = SOCKET_BUFFER
    SOCKET_QUIT_MSG = "Exit"
    server:socket = None
    client_objects = []
    ShowNormalTrace = True
    
    # SensorMessage List 
    #MyListOfSensors:ListOfSensors = ListOfSensors()
    MyListOfSensors = MyQ[SensorMessage2]("MyListOfSensors")
    
    def __init__(self,ForceServerIP = '',ForcePort=''):
        # Starting Server
        if (ForceServerIP!= ''):
            self.ServerIP = ForceServerIP
            
        if (ForcePort!= ''):
            self.ServerPort = ForcePort  
              
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ServerIP, self.ServerPort))
        self.server.listen()
        t = "Brain Server Listening on " + SOCKET_SERVER_IP + ":" + str(SOCKET_SERVER_PORT) + " buffer:" +  str(SOCKET_BUFFER)
        self.TraceLog(t)
        
    
    def SerializeObj_And_Send(self,client:socket, myobj):
        try:
            ser_obj = pickle.dumps(myobj,protocol=5) 
            client.send(ser_obj)
        except Exception as e:
            self.TraceLog("Server Error in Receive_And_DeserializedObj  " + str(e))
            
    def Receive_And_DeserializedObj(self,client:socket):
        try:
            ser_obj = client.recv(self.buffer)
            myobj = pickle.loads(ser_obj)
            return myobj
        except Exception as e:
            self.TraceLog("Server Error in Receive_And_DeserializedObj " + str(e))
   
        
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
        ObjToSend:SimpleMessage = SimpleMessage(msg)
        self.broadcastObj(ObjToSend)
                     

    def broadcastObj(self,MyMessageObj):
        c:client_object
        for c in self.client_objects:
            self.SerializeObj_And_Send (c.client, MyMessageObj)
 
    # Handling Messages From Clients
    def handle(self,client:socket):

        while True:
            try:
            
                myObject = self.Receive_And_DeserializedObj(client)
                message = myObject.Message
                            
                if (message == SOCKET_QUIT_MSG):
                    self.TraceLog("Server Message Got: " + message + " from Unknown")
                    self.Quit(client)
                    break
                
                elif (myObject.Type == BaseMsgClassTypes.SENSOR):
                    
                    print("Received Type SENSOR:" + myObject.Key)
                    found = False
                    for x in self.MyListOfSensors:
                        if (x.key == myObject.key):
                            found = True
                    if (not found):
                        self.MyListOfSensors.put(myObject)
                        print(myObject.Key + " added")
                
                else:    
                    c:client_object = self.GetClientObject(client)
                    self.TraceLog("Server Message Got: " + message + " from " + str(c.servicename))               
                    # confirm message
                    ObjToSend:SimpleMessage = SimpleMessage(message)
                    self.SerializeObj_And_Send(client,ObjToSend)
                    
            except:
                self.Quit(client)
                break
        
    # Sending Messages To Server
    def ServerTimer(self):
        while True:
            time.sleep(30)
            #ListActiveservicenames()

        
            
    # Receiving / Listening Function
    def receive(self):
        
        self.TraceLog("Waiting for Clients...")
        
        while True:
            # Accept Connection
            client, address = self.server.accept()
            self.TraceLog("Connected with {}".format(str(address)))
            ObjToSend:SimpleMessage = SimpleMessage(SOCKET_LOGIN_MSG)
            self.SerializeObj_And_Send(client,ObjToSend)
            
            # Request And Store servicename
        
            MyObj = self.Receive_And_DeserializedObj(client)
            servicename = MyObj.Message
            self.TraceLog("Server Message Got: " + servicename)
                        
            myclient_object = client_object(client,servicename,address)
            self.client_objects.append(myclient_object)
            
            self.TraceLog("servicename is {}".format(servicename))

            # Start Handling Thread For Client
            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()
            
            thread = threading.Thread(target=self.ServerTimer, args=())
            thread.start()
            
    def IsTraceLogEnabled(self) -> bool:
        return self.ShowNormalTrace
    
    def TraceLog(self, Text):
        if (self.IsTraceLogEnabled()):
            print(Text)        
            
    def simul(self):
        count = 0
        self.TraceLog("Simul Enabled")
        while True:
            time.sleep(20)
            message = "Server Broad cast tick: " + str(count)
            ObjToSend:SimpleMessage = SimpleMessage(message)
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