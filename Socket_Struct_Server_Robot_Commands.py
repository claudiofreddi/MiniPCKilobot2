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
    
    #Server Local
    CTRL_T = "ctrl+t"  #Ctrl + T Topic List
    CTRL_M = "ctrl+m"  #Ctrl + M (Alle Messages about send and receive)
    CTRL_S = "ctrl+s"  #Ctrl + S Param Status
    CTRL_I = "ctrl+i"  #Ctrl + I (Image On Off)
    
    
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
        # Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.GOTOCOMPASS + " [degrees] " 
        # Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.MOVE_FW + " [millis] " 
        # Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.MOVE_BW + " [millis] " 
        # Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.MAIN_POWER_ON_OFF  + " [on off]" 
        # Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.MOTOR_POWER_ON_OFF + " [on off]" 
        # Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.SWITCH_ON_OFF  + " [on off]" 
        # Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.SPEAKER_ON_OFF  + " [on off]" 
        # Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.HIGH_SPEED  + " " 
        # Cmds = Cmds + '\n' + Prefix + RobotListOfAvailableCommands.LOW_SPEED  + " " 

        return Cmds

