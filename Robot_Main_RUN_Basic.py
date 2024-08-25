import time
import subprocess

PYTHON_EXEC_PATH = 'C:/Users/user/AppData/Local/Programs/Python/Python311/python.exe'
PYTHON_CLIENT_DIR = "c:/Dati/MiniPCKilobot2/"

#Mode 0 = Disabled
#Mode 1 = subprocess.CREATE_NEW_CONSOLE 
#     2 = Run without Console

FilesToRun = [('Socket_Server.py', 1),
             ('Socket_Client_Keyboard.py', 1),
            ('Socket_Client_Sensors.py',0),
            ('Socket_Client_Lidar.py',  0),
            ('Socket_Client_Actuators.py', 0),
            ('Socket_Client_Speaker.py', 0),
            ('Socket_Client_Telegram.py',0),
            ('Socket_Client_UI.py', 0),
            ('Socket_Client_WebCam.py', 0),
            ('Socket_Client_Remote.py',0),
            ("Socket_Client_Sample.py",1),
            ("Socket_Client_ArduinoReadWrite_Sample.py", 0),
            ("Socket_Client_Console.py", 1),    
            ("Socket_Client_Joystick.py", 0),
            ]


           
for file in FilesToRun:      
    x_filename = PYTHON_CLIENT_DIR + file[0]
    if (file[1] == 0): pass
    elif (file[1] == 1): p = subprocess.Popen([PYTHON_EXEC_PATH ,x_filename],shell = False,creationflags=subprocess.CREATE_NEW_CONSOLE )
    elif (file[1] == 2): p = subprocess.Popen([PYTHON_EXEC_PATH ,x_filename],shell = False)
    time.sleep(2)





    
