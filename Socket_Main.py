from Socket_Server_JSON import * 
from Socket_Client_Keyboard import * 
from Socket_Client_Sensors import * 


    
MyClients = []

MyServer = Robot_Socket_Server_Brain()
MyServer.Run_Threads()

Obj = SocketClient_Keyboard()
Obj.Run_Threads()
MyClients.append(Obj)

Obj = SocketClient_Sensors()
Obj.Run_Threads()
MyClients.append(Obj)