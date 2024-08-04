import socket
import threading
import time
from Lib_Commands_Interfaces import *
from Lib_Utils_MyQ import *


#GlobalVars
Sensor_Compass = 0
BrainCommandQ = MyQ[RobotCommandInterface]("Brain Command Q")

# Connection Data
host = '127.0.0.1'
port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
# clients = []
# nicknames = []

class client_object:
    client:socket = None
    nickname:str = ''
    address = ('',0)
    
client_objects = []

# Sending Messages To All Connected Clients
def broadcast(EncodedMessage):
    global client_objects
    c:client_object
    for c in client_objects:
        c.client.send(EncodedMessage)        
        

# List all nicknames
def ListActiveNickNames():
    global client_objects
    print("Active Nicknames")
    c:client_object
    for c in client_objects:
          print(c.nickname)
        
def GetClientObject(client:socket)->client_object:
    global client_objects
    c:client_object
    for c in client_objects:
          if (c.client == client):
              return c
   

# Handling Messages From Clients
def handle(client:socket):
    count = 0
    global Sensor_Compass 
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024).decode('ascii')
            
            c:client_object = GetClientObject(client)
            print(c.nickname + " called")
            #MessageFromClient
            messageCmd = ''
            messageVal = ''
            SubMsgs = message.split(':')
            messageCmd = SubMsgs[0]
            if (len(SubMsgs)>1):
                messageVal = SubMsgs[1]
            print(messageCmd, ' ', messageVal)
            
            if (messageCmd == "Get_Sensor_Compass"):
                client.send(str(Sensor_Compass).encode('ascii'))
            elif (messageCmd == "Set_Sensor_Compass"):
                Sensor_Compass = int(messageVal)
            else:
                broadcast(message.encode('ascii'))
        except:
            c:client_object = GetClientObject(client)
            client.close()
            broadcast('{} left!'.format(c.nickname).encode('ascii'))     
            client_objects.remove(c)
            
            break
    
# Sending Messages To Server
def ServerTimer():
    while True:
        time.sleep(30)
        ListActiveNickNames()

        
        
# Receiving / Listening Function
def receive():
    global client_objects
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        
        myclient_object = client_object()
        myclient_object.client = client
        myclient_object.nickname = nickname
        myclient_object.address = address
        
        client_objects.append(myclient_object)

        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        broadcast("{} joined!".format(nickname).encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
        
        thread = threading.Thread(target=ServerTimer, args=())
        thread.start()
        
receive()