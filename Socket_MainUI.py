from Socket_Server import * 
from Socket_Client_Keyboard import * 
from Socket_Client_Sensors import * 
from Socket_Client_UI import * 
from Socket_Client_Remote import * 
import time




Obj = SocketClient_Remote()
Obj.Run_Threads()

UIObj = Socket_Client_UI()
UIObj.Run_Threads()


#Last Command
UIObj.OpenWindow()

