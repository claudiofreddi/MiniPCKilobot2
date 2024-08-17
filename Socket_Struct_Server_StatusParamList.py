from datetime import datetime 

class StatusParamName:
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
    
class StatusParamList():
   
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
        print("null")
        return ""
            
    def UpdateParam(self,ParamName="",Value=""):
        pParam:StatusParam
        retval , pParam = self.GetParam(ParamName)
        if (retval):
            pParam.Update(Value)
        else:
            pObj:StatusParam = StatusParam(ParamName=ParamName,Value=Value)
            self.List.append(pObj)
    

    
        