from Socket_Logic_Topics import *  
from Socket_Utils_Text import PaddingTuples

class ServiceCommandAndParamBase():
    
    def __init__(self, ServiceName:str="", Name:str="",ArgDescr="",GiveFeedback=True, AltCommand="", IsLocal=True, Type =""):
        self.Type =Type
        self.ServiceName = ServiceName
        self.Name = Name.lower()
        self.GlobalName = ServiceName + "_" + Name
        self.ArgDescr = ArgDescr
        self.URL = TopicReserved.Compose_URL(Type=Type,ServiceName=ServiceName,Name=Name,ArgDescr=ArgDescr )
        self.GiveFeedback = GiveFeedback
        self.AltCommand = AltCommand.lower()
        self.IsLocal = IsLocal
        self.Value = "" #for Param
        
    def GetDescription(self):
        retval = ""
        
        if (self.Type=="C"):
            A = f"{self.GlobalName}"
        if (self.Type=="P"):
            A = f"{self.GlobalName}:{self.Value}"
        
        B=  f"{self.Name}"
        C = f"{self.URL}\n"
        
        retval += PaddingTuples((A,40), (B,40),(C,1))
        return retval


class ServiceCommandAndParamListBase(Common_LogConsoleClass):
   
    def __init__(self,ThisServiceName=""):
        self.List = []
        self.ThisServiceName = ThisServiceName
        
    def GetByGlobalName(self,GlobalName:str):
        pObj:ServiceCommandAndParamBase
        for pObj in self.List:
            if (pObj.GlobalName.lower() == GlobalName.lower()):
                    return pObj, True
        return None, False    
    
    def GetByLocalName(self,Name:str):
        pObj:ServiceCommandAndParamBase
        for pObj in self.List:
            
            if (pObj.ServiceName.lower() == self.ThisServiceName.lower()):
            
                if (pObj.Name.lower() == Name.lower()):
                    return pObj, True    
                elif (pObj.AltCommand!="" and pObj.AltCommand==Name.lower()):
                    return pObj, True
        return None, False    
    
    def GetDescription(self):
        pObj:ServiceCommandAndParamBase
        retval = "No items found!"
        for pObj in self.List:
            retval = "------------------------------------------------------------------------------" + "\n"
            if (pObj.Type == "C"):
                retval += "Commands:\n\n" 
            elif (pObj.Type == "P"):
                retval += "Params:\n\n" 
            
            for pObj in self.List:
                retval += pObj.GetDescription()
            retval += "------------------------------------------------------------------------------" + "\n"
        
        return retval