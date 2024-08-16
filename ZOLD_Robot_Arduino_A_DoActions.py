# Importing Libraries
import time

from ZOLD_Lib_Processes import *
from Lib_ArduinoConnection import *
from Lib_Utils_Compass_Helper import *                   
from ZOLD_Lib_Commands_Interfaces import * 


from ZOLD_Robot_SharedParamsMonitor import RobotSharedParamsMonitor_Run
from ZOLD_Robot_Simulate_Processes  import Robot_Simulate_Process_Obj_Run, Sparring_Process_Names

##Comandi Elaborabili da Arduino
class RobotArduinoCommands:
    IDLE = "idle"
    STOP = "stop"
    GOTOCOMPASS = "rot"
    TURN = "rot"
    TURN_B = "rotb"
    TURNFAST = "rotfast"
    TURNFAST_B = "rotfastb"
    MOVE_FW = "fw"
    MOVE_BW = "bw"
    MAIN_POWER_ON = "main_power_on"
    MAIN_POWER_OFF = "main_power_off"
    MOTOR_POWER_ON = "motor_power_on"
    MOTOR_POWER_OFF = "motor_power_off"
    SWITCH_ON = "switch_on"
    SWITCH_OFF = "switch_off"
    HIGH_SPEED = 'hspeed'
    LOW_SPEED = 'lspeed'



class RobotArduinoCommandStatus:
    NOT_SET = 0
    TO_RUN = 1
    RUNNING = 2
    ENDED = 3
    TIMEDOUT = 4
    
class RobotArduinoCommandInterface:
    CmdToExecute = RobotArduinoCommands.IDLE
    CommandStatus = RobotArduinoCommandStatus.NOT_SET
    CommandTimeout = 0
    

class RobotArduinoStatus:
    PowerON = False
    IsRunning = False
    IsError = False
    


#Define for all parallel processes to run
class Arduino_A_DoActions_Obj(ProcessSuperClass):
    
    MyArduino_Connection = Arduino_Connection()
    
    def __init__(self,processName):
        super().__init__(processName)
        
        self.THIS_PROCESS_NAME = processName


                
    def ConvertCommandToArduinoCommand(self, InCommand:RobotCommandInterface):
        Cmd = InCommand.GetSpecificCommand()
        Param1 = InCommand.GetSpecificCommandParam(1)
        ArdCmd = ''
        RetArdCmd = ''
        RetParam = ''
        RetValid = False
        RetIsSimple = True
        
        if (Cmd == RobotListOfAvailableCommands.STOP):
           ArdCmd = RobotArduinoCommands.STOP
           
        elif (Cmd == RobotListOfAvailableCommands.ROT_CW):
           ArdCmd = RobotArduinoCommands.TURN
        
        elif (Cmd == RobotListOfAvailableCommands.ROT_ACW):
           ArdCmd = RobotArduinoCommands.TURN_B

        elif (Cmd == RobotListOfAvailableCommands.GOTOCOMPASS):
            ArdCmd = RobotArduinoCommands.GOTOCOMPASS
            RetIsSimple = False
            RetParam = Param1
        
        elif (Cmd == RobotListOfAvailableCommands.MOVE_FW):
            ArdCmd = RobotArduinoCommands.MOVE_FW
            #RetIsSimple = False
            RetParam = Param1
        
        elif (Cmd == RobotListOfAvailableCommands.MOVE_BW):
            ArdCmd = RobotArduinoCommands.MOVE_BW
            #RetIsSimple = False
            RetParam = Param1
        
        elif (Cmd == RobotListOfAvailableCommands.HIGH_SPEED):
            ArdCmd = RobotArduinoCommands.HIGH_SPEED

        elif (Cmd == RobotListOfAvailableCommands.LOW_SPEED):
            ArdCmd = RobotArduinoCommands.LOW_SPEED

        elif (Cmd == RobotListOfAvailableCommands.MAIN_POWER_ON_OFF):
            if (Param1 == 'on'):
                ArdCmd = RobotArduinoCommands.MAIN_POWER_ON
            else:
                ArdCmd = RobotArduinoCommands.MAIN_POWER_OFF
        
        elif (Cmd == RobotListOfAvailableCommands.MOTOR_POWER_ON_OFF):
            if (Param1 == 'on'):
                ArdCmd = RobotArduinoCommands.MOTOR_POWER_ON
            else:
                ArdCmd = RobotArduinoCommands.MOTOR_POWER_OFF
        
        elif (Cmd == RobotListOfAvailableCommands.SWITCH_ON_OFF):
            if (Param1 == 'on'):
                ArdCmd = RobotArduinoCommands.SWITCH_ON
            else:
                ArdCmd = RobotArduinoCommands.SWITCH_OFF
        
        RetValid =  (ArdCmd !='') 
        RetArdCmd = ArdCmd  
        #return IsValid  , IsComplex, ArdCmd, Param 
        return RetValid, RetIsSimple, RetArdCmd, RetParam

            
            
    def Run(self,SharedMem):
        
        super().Run_Pre(SharedMem)
        
   
        if (self.MyArduino_Connection.OpenConnection(self.SharedMem.Init_ARDUINO_A_COM_PORT)):
        
            #SetQ Ready
            self.SharedMem.ArduinoCommandQ.SetReady()
            
            Continue = True
            while Continue:

                if (self.SharedMem.ArduinoCommandQ.HasItems()):
                    NewRobotCommand:RobotCommandInterface = self.SharedMem.ArduinoCommandQ.get()
                    self.SharedMem.ArduinoCommandQ.Status = "Running Command " + NewRobotCommand.CmdToExecute
                    RetValid, RetIsSimple, RetArdCmd, RetParam = self.ConvertCommandToArduinoCommand(NewRobotCommand)
                    if (RetValid):
                        
                        self.SharedMem.ArduinoCommandQ.Status = "Running Arduino Command " + RetArdCmd + ' ' + RetParam
                    
                        if (RetIsSimple):
                            self.MyArduino_Connection.sendData(RetArdCmd)
                        else:
                            RetVal = self.ExecuteComplexCommands(RetArdCmd, RetParam)
                            
                        self.SharedMem.ArduinoCommandQ.Status = "End Arduino Command " + RetArdCmd
                        
                    else:
                        self.SharedMem.ArduinoCommandQ.Status = "Command " + NewRobotCommand.CmdToExecute + " not found" 
                    
                time.sleep(0.1)  
                Continue = super().Run_CanContinueRunnig()
            
            super().Run_Kill()
        
    # ------------------------------------f----------------------------
    #   COMANDI COMPLESSI
    # ----------------------------------------------------------------

    def ExecuteComplexCommands(self,RetArdCmd, RetParam):
        CmdRetVal = 0
        
        if (RetArdCmd == RobotArduinoCommands.GOTOCOMPASS):
            CmdRetVal = self.ExecuteCommand_Rotate(int(RetParam))
        
        
        return CmdRetVal


    def ExecuteCommand_Rotate(self,CompassToReach:int):
        CmdRetVal = 0
        
        AngleReached = False
        CompassVal = self.SharedMem.GetCompass()
        
        dist = CompassHelper.GetRotationDistance(CompassVal,CompassToReach)
        print('ok')
        print('CompassToReach' , str(CompassToReach))
        print('CompassVal' , str(CompassVal))
        print('Dist' , str(dist))
        BestDir = CompassHelper.BestRotationDir(CompassVal,CompassToReach) 
        print('BestDir' , str(BestDir))
        if (BestDir == 1):
            if (dist > 100):
                Cmd = RobotArduinoCommands.GOTOCOMPASS
            else:
                Cmd = RobotArduinoCommands.GOTOCOMPASS
        else:
            if (dist > 100):
                Cmd = RobotArduinoCommands.TURN_B
            else:
                Cmd = RobotArduinoCommands.TURN_B
        
        print('Start Rotating' )
        
        MyRobotTimeout = RobotTimeout()
        MyRobotTimeout.StartNewTimeout(30)
        
        while not AngleReached and not MyRobotTimeout.IsTimeout():
            self.MyArduino_Connection.sendData(Cmd)
            time.sleep(1)
            self.MyArduino_Connection.sendData(RobotArduinoCommands.STOP)
            time.sleep(1)
            CompassVal = self.SharedMem.Compass
            print('Moving CompassVal' , str(CompassVal))
            AngleReached = CompassHelper.IsAngleReached(CompassVal,CompassToReach)
        
        self.MyArduino_Connection.sendData(RobotArduinoCommands.STOP)





def Arduino_A_DoActions_Run(SharedMem):
    print("running Actions...")
    MyArduino_A_DoActions_Obj = Arduino_A_DoActions_Obj(ProcessList.Arduino_A_DoActions)
    MyArduino_A_DoActions_Obj.Run(SharedMem)

def Simul_Run(SharedMem):
    Robot_Simulate_Process_Obj_Run(SharedMem,Sparring_Process_Names.ARDUINO_DO_COMMANDS )
                              
if (__name__== "__main__"):
    
    MySharedObjs = SharedObjs()
    
    run_io_tasks_in_parallel([
        Arduino_A_DoActions_Run
        ,Simul_Run
        ,RobotSharedParamsMonitor_Run
    ], MySharedObjs)    


    
    