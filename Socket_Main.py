from Socket_Server import * 
from Socket_Client_Keyboard import * 
from Socket_Client_Sensors import * 
from Socket_Client_UI import * 
from Socket_Client_Remote import * 
from Socket_Client_Sample import * 
from Socket_Client_WebCam import * 
from Socket_Client_Speaker import * 
from Socket_Setting import *

import time


MyConfig = Socket_GLobal_Config()

AvailableClients = [
                
                SocketClient_Keyboard(),
                SocketClient_Sensors(),
                SocketClient_Speaker(),
                SocketClient_Remote(),
                SocketClient_Sample(),
                #SocketClient_Webcam(),
                Socket_Client_UI()  ## keep last
            ]

MyRunningClients = []

if (MyConfig.IsToRun(Socket_Services_List.SERVER)):
    MyServer = Socket_Server()
    MyServer.Run_Threads()

    time.sleep(2)
    
for Obj in AvailableClients:
    if (MyConfig.IsToRun(Obj.ServiceName)):
        print("Starting " + Obj.ServiceName)
        Obj.Run_Threads()
        MyRunningClients.append(Obj)
        if (Obj.ServiceName == Socket_Services_List.USERINTERFACE):
            Obj.OpenWindow()



