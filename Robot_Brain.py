from multiprocessing import Manager
from Lib_Processes import *
import multiprocessing as mp 

import time
from Lib_Commands_Interfaces import * 
from ZOLD_Robot_Speaker import SpeakerCommandInterface
from Robot_Telegram import TelegramMsgInterface

class RobotBrain_Obj(ProcessSuperClass):
    
    _EnableLiveMessage = False
     
    def __init__(self,processName):
        super().__init__(processName)
        self.MyRobotTimeout = RobotTimeout()

   
    def Run(self,SharedMem):
        super().Run_Pre(SharedMem)
        if (self._EnableLiveMessage):
            self.MyRobotTimeout.StartNewTimeout(30)
            
            
        self.SharedMem.BrainCommandQ.SetReady()
      
        Continue = True
        while Continue:
            
            #Read Commands Queue
            if (self.SharedMem.BrainCommandQ.HasItems()):
                NewRobotCommand:RobotCommandInterface = self.SharedMem.BrainCommandQ.get()
                if (NewRobotCommand.IsValidCommand()):
                    if (NewRobotCommand.CommandStatus == RobotCommandExecutionStatus.TO_RUN):
                        #Speaker Commands
                        if (NewRobotCommand.GetSpecificCommand() == RobotListOfAvailableCommands.SPEAKER_ON_OFF):
                            if (NewRobotCommand.GetSpecificCommandParam(1) == 'on'):
                                self.SharedMem.SpeakerOn =True
                            else:
                                self.SharedMem.SpeakerOn =False
                       
                        elif (NewRobotCommand.GetSpecificCommand() == RobotListOfAvailableCommands.SPEAK):
                            NewSpeakerCommand = SpeakerCommandInterface(NewRobotCommand.GetSpecificCommandParam(1,True))
                            self.SharedMem.SpeakerCommandQ.put(NewSpeakerCommand) 
                        
                        #Direct Arduino Commands
                        elif (NewRobotCommand.IsPassThroughToArduinoCommand()):
                            if (NewRobotCommand.GetSpecificCommand() == RobotListOfAvailableCommands.STOP):
                                 self.SharedMem.ArduinoCommandQ.Clear() #clear before send stop
                            self.SharedMem.ArduinoCommandQ.put(NewRobotCommand)
                        
            if (self._EnableLiveMessage):
                if (self.MyRobotTimeout.IsTimeout()):
                    NewTelegramMsg = TelegramMsgInterface("sono qui..")                
                    self.SharedMem.TelegramMsgQ.put(NewTelegramMsg)
                    self.MyRobotTimeout.StartNewTimeout(30)
                            

           
            Continue = super().Run_CanContinueRunnig()
        super().Run_Kill()
        
   
    

     
def RobotBrain_Run(SharedMem):
    MyRobotBrain_Obj = RobotBrain_Obj(ProcessList.Robot_Brain)
    MyRobotBrain_Obj.Run(SharedMem)
   

if (__name__== "__main__"):
    
    MySharedObjs = SharedObjs()
    
    RobotBrain_Run(MySharedObjs)            