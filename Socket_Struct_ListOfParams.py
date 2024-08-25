from datetime import datetime 
from Socket_Utils_ConsoleLog import * 
from Socket_Struct_Messages import *
from Socket_Utils_Text import Padding, PaddingTuples
from Socket_Logic_Topics import *  
from Socket_Struct_ListOfCommandAndParamBase import *  

class StatusParamListOfValues:
    ON = "ON"
    OFF = "OFF"

class ServiceParam(ServiceCommandAndParamBase):
    def __init__(self,ServiceName:str="",Name="",Value="",ArgDescr="", IsLocal=True):
        super().__init__( ServiceName=ServiceName, Name=Name,ArgDescr=ArgDescr,GiveFeedback=False, AltCommand="", IsLocal=IsLocal,Type ="P")
        
        self.Value = Value
        self.LastUpdate = datetime.now()
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
        

class ServiceParamList(ServiceCommandAndParamListBase,Common_LogConsoleClass):
   
    def __init__(self, ServiceName):
        super().__init__(ServiceName)
    
        
    def CheckParam(self,Name="",ValueToCheck = ""):
        pParam:ServiceParam
        pParam, retval = self.GetByLocalName(Name)
        if (retval):
            if (pParam.Value == ValueToCheck):
                return True
        return False
            
    def SwitchParam(self,Name=""):
        pParam:ServiceParam
        pParam, retval = self.GetByLocalName(Name)
        if (retval):
            if (pParam.Value == StatusParamListOfValues.ON):
                pParam.Update(StatusParamListOfValues.OFF)
            elif (pParam.Value == StatusParamListOfValues.OFF):
                pParam.Update(StatusParamListOfValues.ON)
            return pParam.Value
        
        self.LogConsole("Null Retval in SwitchParam()",ConsoleLogLevel.System)
        return ""
         
    def CreateOrUpdateParam(self,ServiceName="",Name="",Value="",ArgDescr="",IsLocal=True):
        pParam:ServiceParam
        pParam, retval = self.GetByGlobalName(ServiceName + "_" + Name)
        
        if (retval):
            pParam.Update(Value)
        else:
            pObj:ServiceParam = ServiceParam(ServiceName=ServiceName,Name=Name,Value=Value,ArgDescr=ArgDescr,IsLocal=IsLocal)
            self.List.append(pObj)
        return Value
    
    
    def Util_IsParamOn(self,ServiceName, Name=""):
        pParam:ServiceParam
        pParam, retval = self.GetByGlobalName(ServiceName + "_" + Name)
        if (retval):
            if (pParam.IsOnOff):
                if (pParam.Value == StatusParamListOfValues.ON):
                    return True
        return False
    
    def Util_IsParamOff(self,ServiceName,Name=""):
        pParam:ServiceParam
        pParam, retval = self.GetByGlobalName(ServiceName + "_" + Name)
        if (retval):
            if (pParam.IsOnOff):
                if (pParam.Value == StatusParamListOfValues.OFF):
                    return True
        return False
        
    def Util_Params_SetValue(self,pPar:ServiceParam,NewValue):
        NewVal = pPar.Value
        if (pPar.IsOnOff):
            if (NewValue=="on"):
                NewVal = self.CreateOrUpdateParam(ServiceName=pPar.ServiceName,Name=pPar.Name,Value=StatusParamListOfValues.ON)
            elif (NewValue=="off"):
                NewVal = self.CreateOrUpdateParam(ServiceName=pPar.ServiceName,Name=pPar.Name,Value=StatusParamListOfValues.OFF)
            elif (NewValue=="switch"):
                NewVal = self.SwitchParam(pPar.Name)
        elif (pPar.IsInt) or (pPar.IsFloat):
            NewVal = self.CreateOrUpdateParam(ServiceName=pPar.ServiceName,Name=pPar.Name,Value=str(NewValue))
        return NewVal        
    
    def Util_Params_ConfimationMsg(self,Name,NewVal,AlsoReplyToTopic=False,ReplyToTopic:str="")->Socket_Default_Message:
        #print(f"*** TOPIC_CLIENT_PARAM_SERVER_REGISTER")
        ObjToServer:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_CLIENT_PARAM_SERVER_REGISTER
                                                                            #Suffix to service name
                                                                            ,Message = Name
                                                                            ,ValueStr2= self.ThisServiceName
                                                                            ,ValueStr= NewVal)
        
        if (AlsoReplyToTopic and ReplyToTopic!=""):
            #print(f"*** OK")
            ObjToReplyTopic:Socket_Default_Message = Socket_Default_Message(Topic = ReplyToTopic
                                                                            #Suffix to service name
                                                                            ,Message = f"Command Succesfully Executed: {Name} New Status:{ NewVal }"
                                                                            ,ValueStr2= self.ThisServiceName
                                                                            )
        else:
            ObjToReplyTopic = None
            
        return ObjToServer,ObjToReplyTopic