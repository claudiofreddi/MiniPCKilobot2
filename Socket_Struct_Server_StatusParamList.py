from datetime import datetime 
from Socket_Utils_ConsoleLog import * 
from Socket_Struct_Messages import *

class StatusParamName:
    #Common suffix and local param name
    THIS_SERVICE_IS_IDLE = "_IS_IDLE"   #The Service do nothing during Main Cycle or Cyling Functions (for eavy duty clients)
                                        #Receve Messages (to allow re-enable)
    SERVER_CAMERA = "SERVER_CAMERA" 
    SERVER_SHOW_RECEIVED_MSGS = "SERVER_SHOW_RECEIVED_MSGS"
    SERVER_SHOW_SEND_MSGS = "SERVER_SHOW_SEND_MSGS"


class StatusParamListOfValues:
    ON = "ON"
    OFF = "OFF"

class StatusParam():
    def __init__(self,ParamName="",Value="",UserCmd:str="",ServiceName:str=""):
        self.ParamName = ParamName
        self.Value:str = Value
        self.LastUpdate = datetime.now()
        self.UserCmd = UserCmd
        self.ServiceName = ServiceName
        self.IsOnOff =  (Value==StatusParamListOfValues.OFF or Value==StatusParamListOfValues.ON)
        self.IsInt = Value.isnumeric() 
        self.IsFloat = Value.isdecimal() 
            
    def Update(self,Value=""):
        self.Value:str = Value
        self.LastUpdate = datetime.now()
    
    def Util_Params_IsValid(self,Value:str):
        if (self.IsOnOff):
            return (Value=="on" or Value=="off" or Value=="switch")
        elif (self.IsInt):
            return Value.isnumeric()
        elif (self.IsFloat):
            return Value.isdecimal() 
        
    
    
class StatusParamList(Common_LogConsoleClass):
   
    def __init__(self):
        self.List = []
    
    def GetParam(self,ParamName):
        pParam:StatusParam
        for pParam in self.List:
            if (pParam.ParamName == ParamName):
                    return pParam, True
        return None, False
    
    def GetParamByUserCmd(self,UserCmd):
        pParam:StatusParam
        for pParam in self.List:
            if (pParam.UserCmd == UserCmd):
                    return pParam,True
        return None,False
    
    def GetValue(self,ParamName=""):
        pParam:StatusParam
        pParam, retval = self.GetParam(ParamName)
        if (retval):
            return pParam.Value
        else:
            return ""
    
    def GetValueInt(self,ParamName="")->int:
        pParam:StatusParam
        pParam, retval = self.GetParam(ParamName)
        if (retval):
            try:
                return int(pParam.Value)
            except:
                self.LogConsole("Not valid in GetValueInt(), set 0",ConsoleLogLevel.Error) 
                return 0
        else:
            self.LogConsole("Not valid in GetValueInt(), set 0",ConsoleLogLevel.Error) 
            return 0
        
    def GetValueFloat(self,ParamName="")->float:
        pParam:StatusParam
        pParam, retval = self.GetParam(ParamName)
        if (retval):
            try:
                return float(pParam.Value)
            except:
                self.LogConsole("Not valid in GetValueFloat(), set 0",ConsoleLogLevel.Error) 
                return 0.0
        else:
            self.LogConsole("Not valid in GetValueFloat(), set 0",ConsoleLogLevel.Error) 
            return 0.0    
        
    def CheckParam(self,ParamName="",ValueToCheck = ""):
        pParam:StatusParam
        pParam, retval = self.GetParam(ParamName)
        if (retval):
            if (pParam.Value == ValueToCheck):
                return True
        return False
            
    def SwitchParam(self,ParamName=""):
        pParam:StatusParam
        pParam, retval = self.GetParam(ParamName)
        if (retval):
            if (pParam.Value == StatusParamListOfValues.ON):
                pParam.Update(StatusParamListOfValues.OFF)
            elif (pParam.Value == StatusParamListOfValues.OFF):
                pParam.Update(StatusParamListOfValues.ON)
            return pParam.Value
        
        self.LogConsole("Null Retval in SwitchParam()",ConsoleLogLevel.System)
        return ""
         
    def CreateOrUpdateParam(self,ParamName="",Value="",UserCmd:str="",ServiceName:str=""):
        pParam:StatusParam
        pParam, retval = self.GetParam(ParamName)
        if (retval):
            pParam.Update(Value)
        else:
            pObj:StatusParam = StatusParam(ParamName=ParamName,Value=Value,UserCmd=UserCmd,ServiceName=ServiceName)
            self.List.append(pObj)
        return Value
    
    def GetStatusDescription(self):
        pParam:StatusParam
        retval = "Param Status:\n\n" 
        for pParam in self.List:
            retval += pParam.ParamName + ": " + pParam.Value + "\n"

        return retval
    
    def Util_IsParamOn(self,ParamName=""):
        pParam:StatusParam
        pParam, retval = self.GetParam(ParamName)
        if (retval):
            if (pParam.IsOnOff):
                if (pParam.Value == StatusParamListOfValues.ON):
                    return True
        return False
    
    def Util_IsParamOff(self,ParamName=""):
        pParam:StatusParam
        pParam, retval = self.GetParam(ParamName)
        if (retval):
            if (pParam.IsOnOff):
                if (pParam.Value == StatusParamListOfValues.OFF):
                    return True
        return False
        
    def Util_Params_SetValue(self,pPar:StatusParam,NewValue):
        NewVal = pPar.Value
        if (pPar.IsOnOff):
            if (NewValue=="on"):
                NewVal = self.CreateOrUpdateParam(pPar.ParamName,StatusParamListOfValues.ON)
            elif (NewValue=="off"):
                NewVal = self.CreateOrUpdateParam(pPar.ParamName,StatusParamListOfValues.OFF)
            elif (NewValue=="switch"):
                NewVal = self.SwitchParam(pPar.ParamName)
        elif (pPar.IsInt) or (pPar.IsFloat):
            NewVal = self.CreateOrUpdateParam(pPar.ParamName,str(NewValue))
        return NewVal        
    
    def Util_Params_ConfimationMsg(self,ParamName,NewVal,AlsoReplyToTopic=False,ReplyToTopic:str="")->Socket_Default_Message:
        ObjToServer:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_CLIENT_PARAM_UPDATED
                                                                            #Suffix to service name
                                                                            ,Message = ParamName
                                                                            ,ValueStr= NewVal)
        if (AlsoReplyToTopic and ReplyToTopic!=""):
            ObjToReplyTopic:Socket_Default_Message = Socket_Default_Message(Topic = ReplyToTopic
                                                                            #Suffix to service name
                                                                            ,Message = f"Command Succesfully Executed: {ParamName} New Status:{ NewVal }"
                                                                            )
        else:
            ObjToReplyTopic = None
            
        return ObjToServer,ObjToReplyTopic