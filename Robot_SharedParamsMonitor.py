from multiprocessing import Manager
from Lib_Processes import *
import multiprocessing as mp 

class RobotSharedParamsMonitor_Obj(ProcessSuperClass):
    
    _ShowInterval_ = 5 #sec
    
    def __init__(self,processName):
        super().__init__(processName)
   
    def Run(self,SharedMem):
        super().Run_Pre(SharedMem)
        Continue = True
        while Continue:
            super().GetSharedMemObj().Show()
            Continue = super().Run_CanContinueRunnig()
            time.sleep(self._ShowInterval_)

        super().Run_Kill()
        



def RobotSharedParamsMonitor_Run(SharedMem):
    MyRobotSharedParamsMonitor_Obj = RobotSharedParamsMonitor_Obj(ProcessList.Robot_SharedParamsMonitor)
    MyRobotSharedParamsMonitor_Obj.Run(SharedMem)
   

if (__name__== "__main__"):
    
    MySharedObjs = SharedObjs() 
        
    RobotSharedParamsMonitor_Run(MySharedObjs)            