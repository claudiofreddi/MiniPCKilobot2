SOCKET_QUIT_MSG = "Exit"
SOCKET_LOGIN_MSG = "ServiceName"

        
class SensorsId:
    COMPASS = "COMPASS"
    BATTERY = "BATTERY"        

class SocketServices:
    SENSORS = "Sensors"

class BaseMsgClassTypes:
    BASE = "BASE"
    SIMPLE = "SIMPLE"
    SENSOR = "SENSOR"
    
    
        
class BaseMsgClass:
    Type:str = BaseMsgClassTypes.BASE
    IsError = False
    IsExit = False
    Message:str = ""
    IntValue:int = 0
    DecValue:float = 0.0
    RefObj:any = None
    
    def __init__(self,MsgType):
        self.Type = MsgType 
        
        
 
class SimpleMessage(BaseMsgClass):
    def __init__(self,Message):
        super().__init__(BaseMsgClassTypes.SIMPLE)
        self.Message = Message
        

class SensorMessage(BaseMsgClass):
    def __init__(self,SensorID,Value):
        super().__init__(BaseMsgClassTypes.SENSOR)
        self.Message = SensorID
        self.IntValue = Value 
        self.DecValue = Value 
