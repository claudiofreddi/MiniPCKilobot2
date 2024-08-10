from Socket_Server import * 
from Socket_Client_Keyboard import * 
from Socket_Client_Sensors import * 
from Socket_Client_UI import * 
from Socket_Client_Remote import * 
from Socket_Client_WebCam import *
import time

RunUI = False
RunRemote = False
RunWebcam = True

if (RunRemote):
    Obj = SocketClient_Remote()
    Obj.Run_Threads()

if (RunUI):
    UIObj = Socket_Client_UI()
    UIObj.Run_Threads()

if (RunWebcam):
    UIObj = SocketClient_Webcam()
    UIObj.Run_Threads()


#Last Command
if (RunUI):
    UIObj.OpenWindow()

