
from datetime import datetime
import json
from json import JSONEncoder



SOCKET_QUIT_MSG = "Exit"
SOCKET_LOGIN_MSG = "ServiceName"
  

class SocketObjectClassType:
    BASE = "BASE"    
    SENSOR = "SENSOR"

class SocketServices:
    SENSORS = "Sensors"

class BaseMsgClassTypes:
    BASE = "BASE"
    SIMPLE = "SIMPLE"
    SENSOR = "SENSORS"
    
        
class BaseMsgClass:
    Type:str = BaseMsgClassTypes.BASE
    Message:str = ""
    Key:str = ""
    IntValue:int = 0
    DecValue:float = 0.0
        
    def __init__(self,MsgType):
        self.Type = MsgType 
        
        
 
class SimpleMessage(BaseMsgClass):
    def __init__(self,Message):
        super().__init__(BaseMsgClassTypes.SIMPLE)
        self.Message = Message
        


class SensorMessage2(BaseMsgClass):
    MinRange: int = 0
    MaxRange: int = 10000000
    IsAlert: bool = False
    UpdateFrequency_InSec:int = 10 
    
    def __init__(self,SensorID,Value, Description = ''):
        super().__init__(BaseMsgClassTypes.SENSOR)
        self.Key = SensorID
        self.Message = SensorID if Description =='' else SensorID
        self.IntValue = Value 
        self.DecValue = Value 

class SensorMessage(BaseMsgClass):
    MinRange: int = 0
    MaxRange: int = 10000000
    IsAlert: bool = False
    UpdateFrequency_InSec:int = 10 
    LastRead:datetime = None
    
    def __init__(self,SensorID,Value, Description = ''):
        super().__init__(BaseMsgClassTypes.SENSOR)
        self.Key = SensorID
        self.Message = SensorID if Description =='' else SensorID
        self.IntValue = Value 
        self.DecValue = Value 
        
    def SetParams(self,MinRange,MaxRange,UpdateFrequency):
        self.MinRange = MinRange
        self.MaxRange = MaxRange
        self.UpdateFrequency = UpdateFrequency
    
    def NeedUpdate(self):
        if (self.LastRead == None):
            return True
        elif ((datetime.now() - self.LastRead).total_seconds() > self.UpdateFrequency_InSec):
            return True
        else: 
            return False
    
    def UpdateValue(self,IntVal:int,DecVal:float = 0):
        self.LastRead = datetime.now()
        if ((self.IntValue < self.MinRange or self.IntValue > self.MaxRange)
            or
            (self.DecValue < self.MinRange or self.DecValue > self.MaxRange)):
            self.IsAlert = True
        else:
            self.IsAlert = False
        self.IntValue = IntVal
        self.DecValue = DecVal
    
              
        
class ListOfSensors:
    TheList = []
    
    def update(self, pObj:SensorMessage2, Minimal: True):
        found = False
        item:SensorMessage2
        for item in self.TheList:
            if (item.Key == pObj.Key):
                found = True
                self.copy(pObj,item,Minimal)
                return
        if (not found):
            self.TheList.append(pObj)     
            print("Added " + pObj.Key )   
                
    def copy(pObjSource:SensorMessage2,pObjTarget:SensorMessage2, Minimal: True):
        
        pObjTarget.IntValue = pObjSource.IntValue
        pObjTarget.DecValue = pObjSource.DecValue
        
        if (not Minimal):
            pObjTarget.MinRange = pObjSource.MinRange
            pObjTarget.MaxRange = pObjSource.MaxRange
            pObjTarget.IsAlert = pObjSource.IsAlert
            pObjTarget.UpdateFrequency_InSec = pObjSource.UpdateFrequency_InSec
            
            
           