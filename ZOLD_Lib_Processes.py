#Env


from ZOLD_Robot_Shared_Objects import SharedObjs
from ZOLD_Lib_Utils_Timeout import *
import threading
#Concurrent Tasks Management
from concurrent.futures import ThreadPoolExecutor


#Execution
def run_io_tasks_in_parallel(tasks,d):
    with ThreadPoolExecutor() as executor:
        running_tasks = [executor.submit(task,d) for task in tasks]
        for running_task in running_tasks:
            running_task.result()
        
class ProcessList:
    RobotProcessTemplate = "RobotProcessTemplate"
    Arduino_B_ReadSensors = "Arduino_B_ReadSensors"
    Arduino_A_DoActions = "Arduino_A_DoActions"
    Robot_Telegram =  "Robot_Telegram"
    Robot_ShowCam = "Robot_ShowCam"
    Robot_Lidar = "Robot_Lidar"
    Robot_SharedParamsMonitor = "Robot_SharedParamsMonitor"
    Robot_Brain = "Robot_Brain"
    Robot_Speaker = "RobotSpeaker"
    Robot_Vision = "Robot_Vision"
    Robot_Keyboard = "Robot_Keyboard"
    
    #Common user for all processes
    Robot_Simulate_Process = "Robot_Simulate_Process"


class ProcessesStatus:
    DISABLED = "DISABLED"
    OFF = "OFF"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    SUSPENDED = "SUSPENDED"
    KILLED = "KILLED"
    ISTOKILL = "ISTOKILL"
    
  
    def __init__(self):
        return
   
    

class  ProcessSuperClassLogLevel:
    Test = 0
    System = 1
    Control = 2
    Always = 2
    
        
#assert threading.current_thread() is threading.main_thread()       
        
class  ProcessSuperClass:
    
    
    THIS_PROCESS_NAME = ''
    THIS_PROCESS_ID = 0
    THIS_PROCESS_THREAD_NAME = ''
    EnableConsoleLog = True
    EnableConsoleLogLevel = ProcessSuperClassLogLevel.Test
    
    def __init__(self, processName):
        self.THIS_PROCESS_NAME = processName

    
    def Run_Pre(self,pSharedMem:SharedObjs):
        self.SharedMem = pSharedMem
        self.SharedMem.SetProcessStatus(self.THIS_PROCESS_NAME,ProcessesStatus.RUNNING)
        self.THIS_PROCESS_ID = threading.get_ident()
        self.THIS_PROCESS_THREAD_NAME = threading.current_thread().name
        self.LogConsole("Run Main " + self.THIS_PROCESS_NAME)

             
    def GetSharedMemObj(self):
        return self.SharedMem


    def Run_CanContinueRunnig(self):
        return (self.SharedMem.GetProcessStatus(self.THIS_PROCESS_NAME) != ProcessesStatus.ISTOKILL)
    
    def Run_Kill(self):
        self.LogConsole(self.THIS_PROCESS_NAME + " Killed")
        self.SharedMem.SetProcessStatus(self.THIS_PROCESS_NAME,ProcessesStatus.KILLED)
        
    def LogConsole(self,Text,LogLevel = ProcessSuperClassLogLevel.Test):
        if (self.EnableConsoleLog):
            if (LogLevel >= self.EnableConsoleLogLevel):
                print(Text)
            
                        
       
               
