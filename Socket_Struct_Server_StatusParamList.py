from datetime import datetime 
from Socket_Utils_ConsoleLog import * 

class StatusParamName:
    #Common suffix and local param name
    THIS_SERVICE_IS_IDLE = "_IS_IDLE"   #The Service do nothing during Main Cycle or Cyling Functions (for eavy duty clients)
                                        #Receve Messages (to allow re-enable)
    SERVER_CAMERA = "SERVER_CAMERA" 
    SERVER_SHOW_RECEIVED_MSGS = "SERVER_SHOW_RECEIVED_MSGS"
    SERVER_SHOW_SEND_MSGS = "SERVER_SHOW_SEND_MSGS"

class StatusParam():
    def __init__(self,ParamName="",Value=""):
        self.ParamName = ParamName
        self.Value:str = Value
        self.LastUpdate = datetime.now()
            
    def Update(self,Value=""):
        self.Value:str = Value
        self.LastUpdate = datetime.now()

class StatusParamListOfValues:
    ON = "ON"
    OFF = "OFF"
    
class StatusParamList(Common_LogConsoleClass):
   
    def __init__(self):
        self.List = []
    
    def GetParam(self,ParamName):
        pParam:StatusParam
        for pParam in self.List:
            if (pParam.ParamName == ParamName):
                    return True, pParam
        return False, None 
    
    def GetValue(self,ParamName=""):
        pParam:StatusParam
        retval , pParam = self.GetParam(ParamName)
        if (retval):
            return pParam.Value
        else:
            return ""
    
    def CheckParam(self,ParamName="",ValueToCheck = ""):
        pParam:StatusParam
        retval , pParam = self.GetParam(ParamName)
        if (retval):
            if (pParam.Value == ValueToCheck):
                return True
        return False
            
    def SwitchParam(self,ParamName=""):
        pParam:StatusParam
        retval , pParam = self.GetParam(ParamName)
        if (retval):
            if (pParam.Value == StatusParamListOfValues.ON):
                pParam.Update(StatusParamListOfValues.OFF)
            elif (pParam.Value == StatusParamListOfValues.OFF):
                pParam.Update(StatusParamListOfValues.ON)
            return pParam.Value
        
        self.LogConsole("Null Retval in SwitchParam()",ConsoleLogLevel.System)
        return ""
            
    def UpdateParam(self,ParamName="",Value=""):
        pParam:StatusParam
        retval , pParam = self.GetParam(ParamName)
        if (retval):
            pParam.Update(Value)
        else:
            pObj:StatusParam = StatusParam(ParamName=ParamName,Value=Value)
            self.List.append(pObj)
    
    def GetStatusDescription(self):
        pParam:StatusParam
        retval = "Param Status:\n\n" 
        for pParam in self.List:
            retval += pParam.ParamName + ": " + pParam.Value + "\n"

        return retval
    
        