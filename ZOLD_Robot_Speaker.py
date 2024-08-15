from Lib_SpeakToMe import *
from Lib_Processes import *
from Lib_Utils_Timeout import *
from Robot_Shared_Objects import *
import time




class RobotSpeaker_Obj(ProcessSuperClass):
    
    MyRobotTimeout = RobotTimeout()
    
    def __init__(self,processName):
        super().__init__(processName)

   
    def Run(self,pSharedMem:SharedObjs):
        super().Run_Pre(pSharedMem)
        
        self.MySpeak = Service_SpeakToMe("",self.SharedMem.SpeakerOn)
        self.MySpeak.Speak("Speaker Running..")         
        self.MyRobotTimeout.StartNewTimeout(0)
        
        self.SharedMem.SpeakerCommandQ.SetReady()
        
        Continue = True
        while Continue:
            #Insert here loop command
            if (self.SharedMem.SpeakerCommandQ.HasItems()): 
                NewSpeakerCommand:SpeakerCommandInterface = self.SharedMem.SpeakerCommandQ.get()
                if (NewSpeakerCommand.TextToSpeech != ''):
                    if (self.SharedMem.SpeakerOn):
                        self.MySpeak.Speak(NewSpeakerCommand.TextToSpeech)
                            
            
            #End loop commands
            if (self.MyRobotTimeout.IsTimeout()):
                print('Speaker running..')
                self.MyRobotTimeout.StartNewTimeout(10)
                
            time.sleep(1)
            Continue = super().Run_CanContinueRunnig()
        super().Run_Kill()
        
        
def RobotSpeaker_Run(SharedMem):
    MyRobotSpeaker_Obj = RobotSpeaker_Obj(ProcessList.Robot_Speaker)
    MyRobotSpeaker_Obj.Run(SharedMem)
   

if (__name__== "__main__"):
    
    MySharedObjs = SharedObjs()
    
    RobotSpeaker_Run(MySharedObjs)            