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

if (MyConfig.IsToRun(Socket_Services_List.SERVER)):
    MyServer = Socket_Server()
    MyServer.Run_Threads()
    
Obj =SocketClient_Keyboard()    
Obj.Run_Threads()  

Obj = SocketClient_Sensors()    
Obj.Run_Threads()  

# Obj = SocketClient_Remote()    
# Obj.Run_Threads()  

# Obj = SocketClient_Sample()    
# Obj.Run_Threads() 
    
Obj = SocketClient_Speaker()    
Obj.Run_Threads() 

# Obj = SocketClient_Webcam()    
# Obj.Run_Threads() 

Obj = Socket_Client_UI()    
Obj.Run_Threads() 
Obj.OpenWindow()





