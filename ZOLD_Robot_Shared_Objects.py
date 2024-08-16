    
import multiprocessing as mp 
from ZOLD_Lib_Commands_Interfaces import *
from ZOLD_Lib_Utils_MyQ import *


class SpeakerCommandInterface:
    TextToSpeech = ''
    
    def __init__(self,Text):
       self.TextToSpeech = Text  
       
       
class TelegramMsgInterface:
    TextToSend = '' 
    
    def __init__(self,Text):
       self.TextToSend = Text     

class RobotLidar_Info:
    FrontDistance = 200
    LastUpdate:time = None
    

    
class VisionRequestTypes:
    IDLE  = "IDLE"
    TRACK_OBJECT = "TRACK_OBJECT"  #track a single object
    FIND_OBJECT = "FIND_OBJECT"    #find oject unitl it appears 
    FOLLOW_OBJECT = "FOLLOW_OBJECT"  #fing obj and give movement direction
    STOP_TRACKING = "STOP_TRACKING" #stop tracking

class VisionRequestInterface:
    TargetObjectsName = []
    TargetObjectsConfidence:float = 70.0
    RequestType = VisionRequestTypes.IDLE
    UpdateRateInSeconds = 1
    AllowAddQueue = False
    AllowUpdateTargetObjectTracked = True
    
    def __init__(self):
       pass

class VisionObjectTrackingInterface:
    ObjectId = 0
    ObjectName = 0
    Confidence = 0
    IsMovingLR = 0
    IsMovingUD = 0
    AreaLR = 0
    AreaUD = 0
    PrevBox = [0,0,0,0]
    CurrBox = [0,0,0,0]
    #[650 355 164 211]
   
    def __init__(self):
       pass
   
    def CurrBaricenter(self):
        return [int((self.CurrBox[0]+self.CurrBox[2])/2),int((self.CurrBox[1]+self.CurrBox[3])/2)]


#Shared Objects Between Processes
class SharedObjs:
    
    #Settings Params 
    Init_ARDUINO_A_COM_PORT = "COM5"
    Init_ARDUINO_B_COM_PORT = "COM3"
    Init_LIDAR_COM_PORT = "COM10"
    
    GLB_KEY_KeyPressed = "KeyPressed"
    
    _ReadFromDatabase = True
    _WriteOnDatabase = True
    _EnableLog = True

    
    def __init__(self):
        
        self.manager = mp.Manager()
        self.GlobalMem = self.manager.dict()
                        
        self.BrainCommandQ = MyQ[RobotCommandInterface]("Brain Command Q")
        self.ArduinoCommandQ = MyQ[RobotCommandInterface]("Arduino Command Q")
        self.SpeakerCommandQ = MyQ[SpeakerCommandInterface]("Speaker Command Q")
        self.TelegramMsgQ = MyQ[TelegramMsgInterface]("Telegram Command Q")
        self.VisionRequestQ = MyQ[VisionRequestInterface]("Vision Request Q")
        self.VisionResponseQ = MyQ[VisionObjectTrackingInterface]("Vision Response Q")
        self.VisionTargetObjectTracked:VisionObjectTrackingInterface = VisionObjectTrackingInterface()
        self.Compass:int = 0
        self.Battery:int = 0
        self.LidarInfo = RobotLidar_Info()

        #default
        self.SpeakerOn = False
        self.MailOn = True
        self.TelegramOn = True
        self.VideoOn = True
        self.GraphOn = True
             
        #ShowStatus      
        self.Show(True)
        
        return
    
    def _LogConsole(self,Text):
        if (self._EnableLog):
            print(Text)
            
    def SetProcessStatus(self,ProcessName, ProcessStatus):
        self.GlobalMem[ProcessName] = ProcessStatus
        
    def GetProcessStatus(self,ProcessName):
        return self.GlobalMem[ProcessName] 

   
    def Show(self, ShowAll = False):
        try:      
            #Variable params
            print("RobotSharedParamsMonitor:")
            print("GlobalMem:")
            print(self.GlobalMem.keys())
            print(list(self.GlobalMem.values()))

            self.BrainCommandQ.Show()
            self.TelegramMsgQ.Show()
            self.SpeakerCommandQ.Show()
            self.ArduinoCommandQ.Show()
            self.VisionRequestQ.Show()
            self.VisionResponseQ.Show()
            print("Compass: " + str(self.Compass))
            print("Front Distance: " + str(self.LidarInfo.FrontDistance))

            
            if (ShowAll):
                #Static params
                print("Speaker" + (" on" if self.SpeakerOn else " off"))
                print("MailOn" + (" on" if self.MailOn else " off"))
                print("TelegramOn" + (" on" if self.TelegramOn else " off"))
                print("VideoOn" + (" on" if self.VideoOn else " off"))
                
                
                
                print("Arduino A Com Port: " + self.Init_ARDUINO_A_COM_PORT)
                print("Arduino B Com Port: " + self.Init_ARDUINO_B_COM_PORT)
                print("Lidar Com Port: " + self.Init_LIDAR_COM_PORT)

                print("_ReadFromDatabase" + (" on" if self._ReadFromDatabase else " off"))
                print("_WriteOnDatabase" + (" on" if self._WriteOnDatabase else " off"))
                print("_EnableLog" + (" on" if self._EnableLog else " off"))
            
            
        except BaseException:
            super().LogConsole("Shared Mem Printing Error !")    
