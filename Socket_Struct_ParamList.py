from datetime import datetime 
from Socket_Utils_ConsoleLog import * 
from Socket_Struct_Messages import *
from Socket_Utils_Text import Padding, PaddingTuples
from Socket_Logic_Topics import *  


class StatusParamListOfValues:
    ON = "ON"
    OFF = "OFF"

class StatusParam():
    def __init__(self,ServiceName:str="",ParamName="",Value="",ArgDescr=""):
        self.ServiceName = ServiceName
        self.ParamName = ParamName
        self.GlobalParamName = ServiceName + "_" + ParamName
        self.Value:str = Value
        self.ArgDescr = ArgDescr
        self.LastUpdate = datetime.now()
        self.URL = ""
        self.URL += TopicReserved.ReservedTopic_Starts_With_Slash + TopicReserved.ReservedTopic_Starts_With_At + ServiceName
        self.URL += TopicReserved.ReservedTopic_Starts_With_Slash + TopicReserved.ReservedTopic_For_Param
        self.URL += TopicReserved.ReservedTopic_Starts_With_Slash + ParamName
        if (ArgDescr !=""):
            self.URL += TopicReserved.ReservedTopic_Starts_With_Slash + "[" + ArgDescr + "]"
        
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
        
    def GetDescription(self):
        retval = ""
        
        A = f"{self.GlobalParamName}: {self.Value}"
        B=  f"{self.ParamName}"
        C = f"{self.URL}\n"
        
        retval += PaddingTuples((A,40), (B,40),(C,1))
        return retval

class StatusParamList(Common_LogConsoleClass):
   
    def __init__(self):
        self.List = []
    
    def GetParam(self,ParamName):
        pParam:StatusParam
        for pParam in self.List:
            if (pParam.ParamName == ParamName):
                    return pParam, True
        return None, False
    
    # def GetParamByUserCmd(self,UserCmd):
    #     pParam:StatusParam
    #     for pParam in self.List:
    #         if (pParam.ParamName == UserCmd):
    #                 return pParam,True
    #     return None,False
    
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
         
    def CreateOrUpdateParam(self,ServiceName="",ParamName="",Value="",ArgDescr=""):
        pParam:StatusParam
        pParam, retval = self.GetParam(ParamName)
        if (retval):
            pParam.Update(Value)
        else:
            pObj:StatusParam = StatusParam(ServiceName=ServiceName,ParamName=ParamName,Value=Value,ArgDescr=ArgDescr)
            self.List.append(pObj)
        return Value
    
    
    def GetDescription(self):
        pParam:StatusParam
        
        retval = "------------------------------------------------------------------------------" + "\n"
        retval += "Param Status:\n\n" 
        
        for pParam in self.List:
            retval += pParam.GetDescription()
            
        retval += "------------------------------------------------------------------------------" + "\n"
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
                NewVal = self.CreateOrUpdateParam(ParamName=pPar.ParamName,Value=StatusParamListOfValues.ON)
            elif (NewValue=="off"):
                NewVal = self.CreateOrUpdateParam(ParamName=pPar.ParamName,Value=StatusParamListOfValues.OFF)
            elif (NewValue=="switch"):
                NewVal = self.SwitchParam(pPar.ParamName)
        elif (pPar.IsInt) or (pPar.IsFloat):
            NewVal = self.CreateOrUpdateParam(ParamName=pPar.ParamName,Value=str(NewValue))
        return NewVal        
    
    def Util_Params_ConfimationMsg(self,ParamName,NewVal,AlsoReplyToTopic=False,ReplyToTopic:str="")->Socket_Default_Message:
        ObjToServer:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_CLIENT_PARAM_SERVER_REGISTER
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