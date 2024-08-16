
import time


class Robot_CommandSource:
    NONE = "NONE"
    TELEGRAM = "TELEGRAM"
    
   

class RobotListOfAvailableCommands:   
    STOP = "stop"
    GOTOCOMPASS = "rot"
    MOVE_FW = "fw"
    MOVE_BW = "bw"
    SPEAK = "speak"
    MAIN_POWER_ON_OFF = "mainpower"
    MOTOR_POWER_ON_OFF = "motorpower"
    SWITCH_ON_OFF = "switch"
    SPEAKER_ON_OFF = 'speaker'
    RUN_AROUND = 'runaround'
    HIGH_SPEED = 'hspeed'
    LOW_SPEED = 'lspeed'
    ROT_CW = "rot"
    ROT_ACW = "rota"
    
    def __init__(self):
        
        self.AllowedCommandList = list(
                    {self.STOP
                    ,self.GOTOCOMPASS
                    ,self.MOVE_FW
                    ,self.MOVE_BW
                    ,self.SPEAK
                    ,self.MAIN_POWER_ON_OFF
                    ,self.MOTOR_POWER_ON_OFF
                    ,self.SWITCH_ON_OFF
                    ,self.SPEAKER_ON_OFF
                    ,self.RUN_AROUND
                    ,self.HIGH_SPEED
                    ,self.LOW_SPEED
                    ,self.ROT_CW
                    ,self.ROT_ACW
                    }
                    )
        
        self.PassThroughToArduinoCommandList = list(
                    {self.STOP
                    ,self.GOTOCOMPASS
                    ,self.MOVE_FW
                    ,self.MOVE_BW
                    ,self.SPEAK
                    ,self.MAIN_POWER_ON_OFF
                    ,self.MOTOR_POWER_ON_OFF
                    ,self.SWITCH_ON_OFF
                    ,self.HIGH_SPEED
                    ,self.LOW_SPEED
                    ,self.ROT_CW
                    ,self.ROT_ACW
                    }
                    )
        
        self.ComplexCommandList = list(
                    {self.RUN_AROUND
                    }
                    )

        return

    
    def IsValidCommand(self,CommandToCheck:str):
        return (CommandToCheck in self.AllowedCommandList)
  
    def IsPassThroughToArduinoCommand(self,CommandToCheck:str):
        return (CommandToCheck in self.PassThroughToArduinoCommandList)
    
    def IsComplexCommand(self,CommandToCheck:str):
        return (CommandToCheck in self.ComplexCommandList)

    def GetList():
       
        Prefix = ''
        Cmds =  ""
        Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.SPEAK + " [text] " 
        Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.GOTOCOMPASS + " [degrees] " 
        Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.MOVE_FW + " [millis] " 
        Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.MOVE_BW + " [millis] " 
        Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.MAIN_POWER_ON_OFF  + " [on off]" 
        Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.MOTOR_POWER_ON_OFF + " [on off]" 
        Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.SWITCH_ON_OFF  + " [on off]" 
        Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.SPEAKER_ON_OFF  + " [on off]" 
        Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.HIGH_SPEED  + " " 
        Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.LOW_SPEED  + " " 

        return Cmds



class RobotCommandExecutionStatus:
    NOT_SET = 0
    TO_RUN = 1
    RUNNING = 2
    ENDED = 3
    TIMEDOUT = 4
    
class RobotCommandInterface:
    CommandSource = Robot_CommandSource.NONE
    CmdToExecute = ''
    CommandStatus = RobotCommandExecutionStatus.NOT_SET
    CommandTimeout = 0
        
    _EnableTrace = True
    _RobotListOfAvailableCommands = RobotListOfAvailableCommands()
    
    def __init__(self):
        return
    
              
    def _parseText(self,InputCmd, pos, tail = False)->str:
        ValSplitted = str(InputCmd).split()
        if (pos<len(ValSplitted)):
            if (not tail):
                return str(ValSplitted[pos])
            else:
                return ' '.join(ValSplitted[pos:])
        return ''    
        
  
    def GetSpecificCommand(self):
        return self._parseText(self.CmdToExecute,0)
    
    def GetSpecificCommandParam(self, paramPos, tail = False)-> str:
        return self._parseText(self.CmdToExecute,paramPos,tail)


    def IsValidCommand(self):
        return self._RobotListOfAvailableCommands.IsValidCommand(self.GetSpecificCommand())
    
    def IsPassThroughToArduinoCommand(self):
        return self._RobotListOfAvailableCommands.IsPassThroughToArduinoCommand(self.GetSpecificCommand())
    
    def _Trace_(self, sType = ''):
        if (self._EnableTrace):
            if (sType != ''):
                sType = sType + " => "
            print(sType + "CmdToExecute = " + str(self.CmdToExecute)
            + "; CommandStatus = " + str(self.CommandStatus)
            + "; CommandTimeout = " + str(self.CommandTimeout))     
    
    # Accessi To Arduino Command Variables
    def SetCommand(self,CmdToExecute = None,CommandStatus = None,CommandTimeout = None, CommandSource = None):
        if (CmdToExecute != None):
            self.CmdToExecute = CmdToExecute
        if (CommandTimeout != None):
            self.CommandTimeout = CommandTimeout
        if (CommandSource != None):
            self.CommandSource = CommandSource
        #Keep as Last beacusae is a semaphore
        if (CommandStatus != None):
            self.CommandStatus = CommandStatus
        self._Trace_("Set")
            
    def NewCommand(self,CmdToExecute,CommandTimeout = None):
        self.SetCommand(CmdToExecute,RobotCommandExecutionStatus.TO_RUN,CommandTimeout)

    def IsRunning(self):
        return (self.CommandStatus == RobotCommandExecutionStatus.RUNNING)
        
    def IsIdle(self):
        return (self.CmdToExecute == '' or self.CommandStatus == RobotCommandExecutionStatus.NOT_SET
                or self.CommandStatus == RobotCommandExecutionStatus.ENDED
                or self.CommandStatus == RobotCommandExecutionStatus.TIMEDOUT)

    def IsNewCommandAvailable(self):
        return (self.CommandStatus == RobotCommandExecutionStatus.TO_RUN)

    def StartExecution(self):
        self.CommandStatus = RobotCommandExecutionStatus.RUNNING
        self._Trace_("Start")
        
    def EndExecution(self, IsTimeout = False):
        self.CommandStatus = RobotCommandExecutionStatus.ENDED
        if (IsTimeout):
            self.CommandStatus = RobotCommandExecutionStatus.TIMEDOUT
        self._Trace_("End")
    
                      
 
if (__name__== "__main__"):
    
    print('Test')
    
    
    
    
    