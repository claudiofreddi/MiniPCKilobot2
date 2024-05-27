from Lib_Processes import *
import time
from Robot_Arduino_A_DoActions import *
from Lib_Utils_MyQ import *
from queue import *

# pip install pynput
from pynput import keyboard

class RobotKeyboard_Obj(ProcessSuperClass):
    
    
    _Mov_Fw = 'w'
    _Mov_Bw = 's'
    _Mov_Left = 'a'
    _Mov_Right = 'd'
    _Mov_Stop = 'e'

    
    _PrintCommand = False
    _AllowEscape = True
    
    _StopOnReleaseEvent   = True
    _LastCommand = ''
    LocalQ = Queue()
    
    _DirectQueue = True
    
    def __init__(self,processName):
        super().__init__(processName)
        #self.LocalQ = MyQ[str]("keyboard")
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        listener.start()
        
    def on_press(self,key):
        try:
            cmd = str(key.char)
            
            if self._PrintCommand: print('alphanumeric key {0} pressed'.format(cmd))
            # se diverso da ultimo accodo
            if (self._LastCommand != cmd or True):
                self._LastCommand = cmd
                if (not self._DirectQueue):
                    if (cmd == self._Mov_Stop):
                        while self.LocalQ.qsize()>0:
                            self.LocalQ.get()
                    self.LocalQ.put(cmd)
                else:   
                    if (cmd == self._Mov_Stop):
                        self.SharedMem.ArduinoCommandQ.Clear()
                        self.AddQueueArduino(RobotListOfAvailableCommands.STOP)
                    elif (cmd == self._Mov_Fw):
                        self.AddQueueArduino(RobotListOfAvailableCommands.MOVE_FW)
                    elif (cmd == self._Mov_Bw):
                        self.AddQueueArduino(RobotListOfAvailableCommands.MOVE_BW)
                    elif (cmd == self._Mov_Right):
                        self.AddQueueArduino(RobotListOfAvailableCommands.ROT_CW)
                    elif (cmd == self._Mov_Left):
                        self.AddQueueArduino(RobotListOfAvailableCommands.ROT_ACW)
                    else:
                        print("command not found")    
                
        except AttributeError:
            if self._PrintCommand: print('special key {0} pressed'.format(key))

    def on_release(self,key):
        if self._PrintCommand: print('{0} released'.format(key))
        
        if self._StopOnReleaseEvent and self._LastCommand in ('f','b','r','t'): 
            if (not self._DirectQueue):
                pass
                #self.LocalQ.put('s')
            else:
                pass
                #self.AddQueueArduino(RobotListOfAvailableCommands.STOP)
            
            self._LastCommand = ''
            
        if self._AllowEscape and key == keyboard.Key.esc:
            # Stop listener
            return False
        
    def AddQueueArduino(self,Cmd:str):
        sCmd = str(Cmd)
        print(sCmd)
        NewRobotCommand = RobotCommandInterface()
        NewRobotCommand.SetCommand(sCmd,RobotCommandExecutionStatus.TO_RUN)
        self.SharedMem.ArduinoCommandQ.put(NewRobotCommand)
        print(sCmd + ' Added')
    
    def Run(self,SharedMem):
        super().Run_Pre(SharedMem)
        
        #Insert here start  command
        super().LogConsole('RobotKeyboar Started')    
    
            
            
        #End start commands      
        while not self.SharedMem.ArduinoCommandQ.IsReady():
            print("Waiting Arduino...")
            time.sleep(1)
        
        super().LogConsole('RobotKeyboar Running')           
        

        self.cmd = ""
        Continue = True
        while Continue:
            #Insert here loop command
            #eefdsdprint(".")  

               
            if (not self._DirectQueue):
                if (self.LocalQ.qsize()>0):
                    self.cmd = self.LocalQ.get()
                    
                    if (self.cmd == self._Mov_Stop):
                        self.AddQueueArduino(RobotListOfAvailableCommands.STOP)
                    elif (self.cmd == self._Mov_Fw):
                        self.AddQueueArduino(RobotListOfAvailableCommands.MOVE_FW)
                    elif (self.cmd == self._Mov_Bw):
                        self.AddQueueArduino(RobotListOfAvailableCommands.MOVE_BW)
                    elif (self.cmd ==  self._Mov_Right):
                        self.AddQueueArduino(RobotListOfAvailableCommands.ROT_CW)
                    elif (self.cmd ==  self._Mov_Left):
                        self.AddQueueArduino(RobotListOfAvailableCommands.ROT_ACW)
                    else:
                        print("command not found")
                                        
                    print("kb cmd: ", self.cmd)
            
            #End loop commands
            time.sleep(.1)
            Continue = super().Run_CanContinueRunnig()
        super().Run_Kill()
        
        
def RobotKeyboard_Run(SharedMem):
    MyRobotKeyboard_Obj = RobotKeyboard_Obj(ProcessList.Robot_Keyboard)
    MyRobotKeyboard_Obj.Run(SharedMem)
   

if (__name__== "__main__"):
    
    MySharedObjs = SharedObjs()
    
    #RobotKeyboard_Run(MySharedObjs)  
   
    run_io_tasks_in_parallel([
        Arduino_A_DoActions_Run
        ,RobotKeyboard_Run
    ], MySharedObjs)            