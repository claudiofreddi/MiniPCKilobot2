from Socket_Client_Joystick import SocketClient_Joystick_Commands

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
  
    
    _Joy_Fw = SocketClient_Joystick_Commands.FW
    _Joy_Bw = SocketClient_Joystick_Commands.BW
    _Joy_Left = SocketClient_Joystick_Commands.RIGHT
    _Joy_Right = SocketClient_Joystick_Commands.LEFT
    _Joy_Stop = SocketClient_Joystick_Commands.BUTTON_6
        
    def PrintUsageCommands(self):
        print("Keyboard:")
        print('Forward key {0} '.format(self._Mov_Fw))
        print('Backward key {0} '.format(self._Mov_Bw))
        print('Left key {0} '.format(self._Mov_Left))
        print('Right key {0} '.format(self._Mov_Right))
        print('Stop key {0} '.format(self._Mov_Stop))
        
    def convert(self,KeyString:str):
           
        if (KeyString == self._Mov_Stop     or KeyString == self._Joy_Stop):
            ArdCmd = RobotArduinoCommands.STOP
        elif (KeyString == self._Mov_Fw     or KeyString == self._Joy_Fw):
            ArdCmd = RobotArduinoCommands.MOVE_FW
        elif (KeyString == self._Mov_Bw     or KeyString == self._Joy_Bw):
            ArdCmd = RobotArduinoCommands.MOVE_BW
        elif (KeyString == self._Mov_Right  or KeyString == self._Joy_Right):
            ArdCmd =  RobotArduinoCommands.TURN
        elif (KeyString == self._Mov_Left   or KeyString == self._Joy_Left):
            ArdCmd = RobotArduinoCommands.TURN_B
        else:
            ArdCmd = ""
            print(f"command {KeyString} not found") 
        
        return ArdCmd