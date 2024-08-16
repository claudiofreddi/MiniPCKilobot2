from ZOLD_Lib_Processes import *
import time

class RobotProcessTemplate_Obj(ProcessSuperClass):
    
    def __init__(self,processName):
        super().__init__(processName)

   
    def Run(self,SharedMem):
        super().Run_Pre(SharedMem)
        
        #Insert here start  command
        super().LogConsole('Template Started')    
            
            
            
        #End start commands      
        #self.SharedMem.Template_ObjQ.SetReady()
        
        
        Continue = True
        while Continue:
            #Insert here loop command
            super().LogConsole('Template Running')    
            
            
            
            #End loop commands
            time.sleep(1)
            Continue = super().Run_CanContinueRunnig()
        super().Run_Kill()
        
        
def RobotProcessTemplate_Run(SharedMem):
    MyRobotProcessTemplate_Obj = RobotProcessTemplate_Obj(ProcessList.RobotProcessTemplate)
    MyRobotProcessTemplate_Obj.Run(SharedMem)
   

if (__name__== "__main__"):
    
    MySharedObjs = SharedObjs()
    
    RobotProcessTemplate_Run(MySharedObjs)            