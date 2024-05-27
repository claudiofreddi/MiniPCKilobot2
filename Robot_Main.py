#################################################
# Moduo principale che inizializza il robot 
# e lancia i task paralleli necessari
#################################################


#Env
from Robot_Envs import *

from Lib_SpeakToMe import Service_SpeakToMe
from Lib_MailSender import MailSender
from Lib_Processes import * 


#Concurrent Tasks Management
from concurrent.futures import ThreadPoolExecutor


#Concurrent Tasks
from Robot_Arduino_B_ReadSensors import ArduinoReadSensors_Run
from Robot_Arduino_A_DoActions import Arduino_A_DoActions_Run
from Robot_Telegram import RobotTelegram_Run
from Robot_ShowCam import RobotShowCam_Run
from Robot_SharedParamsMonitor import RobotSharedParamsMonitor_Run
from Robot_Lidar import RobotLidar_Run
from Robot_Brain import RobotBrain_Run
from Robot_Speaker import RobotSpeaker_Run
          

if (__name__== "__main__"):

    print ()
    _EnableOutputs = False  ## MailOn, SpeakerOn, TelegramOn
    
    
    _StartSpeakerMessage = "Ciao, eccomi. Sono Kilobot"
    _StartMailMessage_Subject = "Robot Starting..."
    _StartMailMessage_Body = "Someone started the robot !"
    
    MySharedObjs = SharedObjs() 
    
    #Settings Params 
    MySharedObjs.Init_ARDUINO_A_COM_PORT = "COM5"
    MySharedObjs.Init_ARDUINO_B_COM_PORT = "COM3"
    MySharedObjs.Init_LIDAR_COM_PORT = "COM10"
    
    #Enabling Params 
    MySharedObjs.MailOn = _EnableOutputs
    MySharedObjs.SpeakerOn = _EnableOutputs 
    MySharedObjs.TelegramOn = _EnableOutputs
    
        
    #Speaker
    MySpeak = Service_SpeakToMe("",MySharedObjs.SpeakerOn)
    MySpeak.Speak(_StartSpeakerMessage)
    
    
    MyMailSender = MailSender(ADMIN_MAIL)
    MyMailSender.send_email(_StartMailMessage_Subject,_StartMailMessage_Body)
  
 

    run_io_tasks_in_parallel([
         ArduinoReadSensors_Run
        ,Arduino_A_DoActions_Run
        ,RobotTelegram_Run
        ,RobotSharedParamsMonitor_Run
        ,RobotShowCam_Run
        ,RobotLidar_Run
        ,RobotBrain_Run
        ,RobotSpeaker_Run
    ], MySharedObjs)    

