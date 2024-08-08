from Socket_Server import * 
from Socket_Client_Keyboard import * 
from Socket_Client_Sensors import * 
from Socket_Client_UI import * 
import time



MyServer = Socket_Server()
MyServer.Run_Threads()


UIObj = Socket_Client_UI()
UIObj.Run_Threads()


#Last Command
UIObj.OpenWindow()

