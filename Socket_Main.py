from Socket_Server import * 
from Socket_Client_Keyboard import * 
from Socket_Client_Sensors import * 
from Socket_Client_UI import * 
from Socket_Client_Remote import * 
from Socket_Client_Sample import * 
import time


    
MyClients = []

EnableUI = False
DisableLog = False



MyServer = Socket_Server()
MyServer.EnableConsoleLog = True
MyServer.Run_Threads()

if (EnableUI):
    UIObj = Socket_Client_UI()
    UIObj.Run_Threads()
    MyClients.append(UIObj)

Obj = SocketClient_Keyboard()
Obj.Run_Threads()
MyClients.append(Obj)

Obj = SocketClient_Sensors()
Obj.EnableConsoleLog = True
Obj.Run_Threads()
MyClients.append(Obj)


Obj = SocketClient_Remote()
Obj.Run_Threads()
MyClients.append(Obj)

Obj = SocketClient_Sample()
Obj.Run_Threads()
MyClients.append(Obj)

if (DisableLog):
    pClient:Socket_Client_BaseClass
    for pClient in MyClients:
        pClient.EnableConsoleLog = False
        #pClient.Quit()

    MyServer.EnableConsoleLog = False


#Last Command
if (EnableUI):
    UIObj.OpenWindow()

