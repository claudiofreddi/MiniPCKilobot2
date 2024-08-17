
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


    
class Arduino_Keyboard_To_Actions:
    
    _Mov_Fw = 'w'
    _Mov_Bw = 's'
    _Mov_Left = 'd'
    _Mov_Right = 'a'
    _Mov_Stop = 'e'
  
        
    def PrintUsageCommands(self):
        print('Forward key {0} '.format(self._Mov_Fw))
        print('Backward key {0} '.format(self._Mov_Bw))
        print('Left key {0} '.format(self._Mov_Left))
        print('Right key {0} '.format(self._Mov_Right))
        print('Stop key {0} '.format(self._Mov_Stop))
        
    def convert(self,KeyString:str):
            
        if (KeyString == self._Mov_Stop):
            ArdCmd = RobotArduinoCommands.STOP
        elif (KeyString == self._Mov_Fw):
            ArdCmd = RobotArduinoCommands.MOVE_FW
        elif (KeyString == self._Mov_Bw):
            ArdCmd = RobotArduinoCommands.MOVE_BW
        elif (KeyString == self._Mov_Right):
            ArdCmd =  RobotArduinoCommands.TURN
        elif (KeyString == self._Mov_Left):
            ArdCmd = RobotArduinoCommands.TURN_B
        else:
            ArdCmd = ""
            print(f"command {KeyString} not found") 
        
        return ArdCmd