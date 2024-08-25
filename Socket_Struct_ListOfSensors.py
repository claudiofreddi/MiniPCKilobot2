from Socket_Utils_ConsoleLog import * 
from Socket_Utils_Text import PaddingTuples
from datetime import datetime 

class SensorsListOfValues:
     ON = "ON"
     OFF = "OFF"

class SensorRangeAlertType:
    GREEN = 1
    YELLOW = 2
    RED = 3

class SensorRelativeRangePosition:
    LOWER = -1
    IN = 0
    HIGER = +1

class SensorRange():
    def __init__(self, Name, LowVal:float, HighVal:float, RangeAlertType:SensorRangeAlertType):
        self.Name = Name
        if (Name == ""): self.Name = "[" + str(LowVal) + "-" + str(HighVal) + "]"
        self.LowVal = LowVal
        self.HighVal = HighVal
        self.RangeAlertType = RangeAlertType
        
    def GetRelativePosition(self,Value):
        if (Value < self.LowVal): return SensorRelativeRangePosition.LOWER
        if (self.LowVal<=Value and Value<=self.HighVal)  : return SensorRelativeRangePosition.IN
        if (Value > self.HighVal): return SensorRelativeRangePosition.HIGER
    
    def GetDescription(self):
        retval = PaddingTuples((f"{self.Name}:",30),(f"{self.LowVal}",10),(f"...{self.HighVal}",10),(f"{self.RangeAlertType}\n",1)) + "\n"          
        return retval
     
class Sensor():
    
    def __init__(self, SensorTopic="", Value:float=0):
        self.SensorTopic = SensorTopic
        self.Value = Value
        self.LastUpdate = datetime.now()
        self.IsOnOff =  (Value==SensorsListOfValues.OFF or Value==SensorsListOfValues.ON)
        self.RangeSet = []

    def Update(self,NewValue):
        self.Value = NewValue
        self.LastUpdate = datetime.now()
        
    def GetAlertType(self):
        r:SensorRange
        for r in self.RangeSet:
            #Get the IN range
            if (r.GetRelativePosition(self.Value) == SensorRelativeRangePosition.IN):
                return r.RangeAlertType, True
        return None, False
        
    def GetDescription(self):
        r:SensorRange
        retval = PaddingTuples((f"{self.SensorTopic}:",40),(f"{self.Value }",10),(f"{self.LastUpdate}\n",1)) + "\n" 
        for r in self.RangeSet:
            retval += "  " + r.GetDescription()  
        return retval
    
class SensorList(Common_LogConsoleClass):
   
    def __init__(self,ThisServiceName=""):
        self.List = []
        self.ThisServiceName = ThisServiceName
        
    def Get(self,SensorTopic:str):
        pObj:Sensor
        for pObj in self.List:
            if (pObj.SensorTopic.lower() == SensorTopic.lower()):
                    return pObj, True
        return None, False    
    
    def Append(self, SensorTopic="", Value:float=0):
        pNew = Sensor(SensorTopic, Value)
        self.List.append(pNew)
        
    def GetDescription(self):
        retval = ""
        sns:Sensor
        for sns in self.List:
            retval+= sns.GetDescription() + "\n"
        return retval
            
    def GetSensorsInSpecificAlertType(self,Status:SensorRangeAlertType):
        sns:Sensor
        retList = []
        for sns in self.List:
            if (sns.GetAlertType() == Status):
                retList.append(sns) 
        return retList