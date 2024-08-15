from Socket_Server import * 
from Socket_Client_Keyboard import * 
from Socket_Client_Sensors import * 
from Socket_Client_UI import * 
from Socket_Client_Remote import * 
from Socket_Client_Sample import * 
from Socket_Client_WebCam import * 
from Socket_Client_Speaker import * 
from Socket_Client_Telegram import * 
from Socket_Client_Actuators import * 
from Socket_Setting___ import *

import time

_LogOptimized = True

MyServer = Socket_Server(LogOptimized=_LogOptimized)
MyServer.Run_Threads()
    
Obj =SocketClient_Keyboard(LogOptimized=_LogOptimized)    
Obj.Run_Threads()  

Obj = SocketClient_Sensors(LogOptimized=_LogOptimized)    
Obj.Run_Threads()  

# Obj = SocketClient_Speaker(LogOptimized=_LogOptimized)    
# Obj.Run_Threads() 

#Obj = SocketClient_Telegram(LogOptimized=_LogOptimized)    
#Obj.Run_Threads() 

#Obj = SocketClient_Webcam(LogOptimized=_LogOptimized)    
#Obj.Run_Threads() 

Obj = SocketClient_Actuators(LogOptimized=_LogOptimized)    
Obj.Run_Threads() 

# Obj = SocketClient_Remote()    
# Obj.Run_Threads()  

# Obj = SocketClient_Sample()    
# Obj.Run_Threads() s
    
Obj = Socket_Client_UI(LogOptimized=_LogOptimized)    
Obj.Run_Threads() 
Obj.OpenWindow()





