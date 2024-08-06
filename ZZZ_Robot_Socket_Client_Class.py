import socket
import threading
import time
from Robot_Envs import *

class Robot_Socket_Client_Object: 
    # Choosing Nickname
    ClientName = ""
    ServerIP = SOCKET_SERVER_IP
    ServerPort = SOCKET_SERVER_PORT
    client = None
    IsConnected = False
    buffer = SOCKET_BUFFER

    def __init__(self,ClientName):
       self.ClientName = ClientName 


    # Listening to Server and Sending Nickname
    def receive(self):
        self.IsConnected = False
        while True:
            
            try:
                if (self.IsConnected == False):
                    # Connecting To Server
                    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client.connect((self.ServerIP, self.ServerPort))
                    self.IsConnected = True
            
            
                # Receive Message From Server
                message = self.client.recv(self.buffer)
                
                self.Actions(message)
                
            except:
                self.IsConnected = False
                # Close Connection When Errorclaudio
                print("An error occured! Retry in 15 sec..")
                self.client.close()
                time.sleep(15) #Wait 30 sec and retry
                #break
        
    # Sending Messages To Server
    def write(self):
        
        while True:
            #message = '{}: {}'.format(nickname, input(''))
            message = '{}'.format(input(''))
            self.client.send(message.encode('ascii'))   

    def Actions(self,new_message):
        message = new_message.decode('ascii')
              
        if message == 'NICK':
            self.client.send(self.ClientName.encode('ascii'))
        else:
            print(message)
    
    def ThreadActions(self):    
        pass
        
    def Run(self):    
        # Starting Threads For Listening And Writing
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()
        
        write_thread = threading.Thread(target=self.ThreadActions)
        write_thread.start()
        
if (__name__== "__main__"):
    
    #Sample
    class Test(Robot_Socket_Client_Object):
        
        CompassVal = 0
        Interval = 10
        
        def __init__(self,ClientName,Interval):
            Robot_Socket_Client_Object.__init__(self,ClientName)
            self.Interval = Interval
            
        def Actions(self,new_message):
            super().Actions(new_message)
            
        def ThreadActions(self):
            super().ThreadActions()
            while True:
                time.sleep(self.Interval)
                self.CompassVal = self.CompassVal + self.Interval
                if (self.CompassVal>=360):  
                    self.CompassVal = 0
                    
                if (self.IsConnected == True):
                    message = "Set_Sensor_Compass" + ":" + str(self.CompassVal)
                    self.client.send(message.encode('ascii'))
                    print(message)
           
            
    
    S1 = Robot_Socket_Client_Object("S1")
    S2 = Robot_Socket_Client_Object("S2")
    S3 = Test("Sensors1",10)
    S4 = Test("Sensors2",15)
    
    
    S1.Run()
    S2.Run()
    S3.Run()
    S4.Run()
         