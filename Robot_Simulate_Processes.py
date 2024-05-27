import time
from Lib_Commands_Interfaces import *
from Lib_Processes import *
from Robot_Shared_Objects import *

class Sparring_Process_Names:
    NOT_SET = ""
    ARDUINO_DO_COMMANDS = "ARDUINO_DO_COMMANDS"
    VISION = "VISION"

#Define for all parallel processes to run
class Robot_Simulate_Process_Obj(ProcessSuperClass):

    def __init__(self,processName, SparringProcess = ''):
        super().__init__(processName)
        self.THIS_PROCESS_NAME = processName
        self._SparringProcess = SparringProcess
        
    def AddQueueArduino(self,Cmd):
        print(str(Cmd))
        NewRobotCommand = RobotCommandInterface()
        NewRobotCommand.SetCommand(Cmd,RobotCommandExecutionStatus.TO_RUN)
        self.SharedMem.ArduinoCommandQ.put(NewRobotCommand)
        print(str(Cmd) + ' Added')
        
    def AddQueueVision(self,Cmd,ListObjs,ConfVal:float):
        print(Cmd)
        try:
            MyVisionCmd = VisionRequestInterface()
            MyVisionCmd.AllowAddQueue = True
            MyVisionCmd.RequestType = Cmd 
            MyVisionCmd.TargetObjectsName = ListObjs
            MyVisionCmd.TargetObjectsConfidence = ConfVal
            self.SharedMem.VisionRequestQ.put(MyVisionCmd)
            time.sleep(0.5)
        except Exception as ex:
            print(ex.message)
           
        print(str(Cmd) + ' Added')
            
    def Run(self,SharedMem,IsSingleRunning = False):
        super().Run_Pre(SharedMem)
        
        if (self._SparringProcess  == Sparring_Process_Names.NOT_SET):
            print("Define Sparring Process")
            return
        
        if (self._SparringProcess  == Sparring_Process_Names.ARDUINO_DO_COMMANDS):
            print('Check  Arduino Queue if Ready')
            print("Waiting Arduino Queue Reader be Ready...")
            while not self.SharedMem.ArduinoCommandQ.IsReady():
                time.sleep(0.5) 
            print('Arduino Queue Ready')
                
            #self.AddQueue(RobotListOfAvailableCommands.SWITCH_ON_OFF + ' on')
            self.AddQueueArduino(RobotListOfAvailableCommands.MOVE_FW)
            time.sleep(4)
            self.AddQueueArduino(RobotListOfAvailableCommands.STOP)
            #self.AddQueueArduino(RobotListOfAvailableCommands.SWITCH_ON_OFF + ' off')
            
            time.sleep(4)
            
            #self.AddQueueArduino(RobotListOfAvailableCommands.SWITCH_ON_OFF + ' on')
            self.AddQueueArduino(RobotListOfAvailableCommands.MOVE_FW)
            time.sleep(4)
            self.AddQueueArduino(RobotListOfAvailableCommands.STOP)
            #self.AddQueueArduino(RobotListOfAvailableCommands.SWITCH_ON_OFF + ' off')
            return
        
        if (self._SparringProcess  == Sparring_Process_Names.VISION):
            
            try:
                
                if not (IsSingleRunning):
                    while not self.SharedMem.VisionRequestQ.IsReady():
                        time.sleep(1) 
                print('Queue Ready')

                
                self.AddQueueVision( VisionRequestTypes.TRACK_OBJECT,['Persona'],70)

                                            
                print("Test Waiting..")     
                time.sleep(60)  
                print("Stop..")     
            
                self.AddQueueVision( VisionRequestTypes.STOP_TRACKING,[],70)
                
                print("Test Waiting..")     
                time.sleep(10)  
                print("Stop..")     
            
                self.AddQueueVision( VisionRequestTypes.FIND_OBJECT,['Persona'],70)
                
            except Exception as e:
                if hasattr(e, 'message'):
                    print(e.message)
                else:
                    print(e)

                      
            
            return
            
            
        
        return
                
       

   
def Robot_Simulate_Process_Obj_Run(SharedMem,SparringProcessName,IsSingleProcess = False):
    print("running Simul...")
    MySimul_Obj = Robot_Simulate_Process_Obj(ProcessList.Robot_Simulate_Process,SparringProcessName)
    MySimul_Obj.Run(SharedMem,IsSingleProcess)

def Simul_Run(SharedMem,IsSingleProcess = False):
    #Robot_Simulate_Process_Obj_Run(SharedMem,Sparring_Process_Names.ARDUINO_DO_COMMANDS)
    Robot_Simulate_Process_Obj_Run(SharedMem,Sparring_Process_Names.VISION,IsSingleProcess)
       
    
if (__name__== "__main__"):
   
  
    MySharedObjs = SharedObjs()
       
    
    Simul_Run(MySharedObjs,True)
    