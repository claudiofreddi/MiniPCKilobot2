

from Socket_Utils_ConsoleLog import * 
from Socket_Struct_Messages import *
from Socket_Utils_Text import PaddingTuples
from Socket_Logic_Topics import *  
from Socket_Struct_ListOfCommandAndParamBase import *  

class ServiceCommand(ServiceCommandAndParamBase):
    def __init__(self, ServiceName:str="", Name:str="",ArgDescr="",GiveFeedback=True, AltCommand="", IsLocal=True):
        super().__init__( ServiceName=ServiceName, Name=Name,ArgDescr=ArgDescr,GiveFeedback=GiveFeedback, AltCommand=AltCommand, IsLocal=IsLocal,Type ="C")
        
        
class ServiceCommandList(ServiceCommandAndParamListBase, Common_LogConsoleClass):
   
    def __init__(self, ServiceName):
        super().__init__(ServiceName)
    
    def CreateCommand(self,ServiceName:str="",Name:str="",ArgDescr="",GiveFeedback=True, AltCommand="" , IsLocal=True):
        pCmd:ServiceCommand
        pCmd, retval = self.GetByGlobalName(ServiceName + "_" + Name)
        if (not retval):
            pObj:ServiceCommand = ServiceCommand(ServiceName=ServiceName,Name=Name,ArgDescr=ArgDescr, GiveFeedback=GiveFeedback, AltCommand=AltCommand , IsLocal=IsLocal)
            self.List.append(pObj)
    
    
    def Util_Command_ConfimationMsg(self,Name,CommandRetVal:str,AlsoReplyToTopic=False,ReplyToTopic:str="")->Socket_Default_Message:
        ObjToServer:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_CLIENT_PARAM_SERVER_REGISTER
                                                                            #Suffix to service name
                                                                            ,Message = Name
                                                                            )
        if (AlsoReplyToTopic and ReplyToTopic!=""):
            ObjToReplyTopic:Socket_Default_Message = Socket_Default_Message(Topic = ReplyToTopic
                                                                            #Suffix to service name
                                                                            ,Message = f"Command  {Name} succesfully Executed: {CommandRetVal}"
                                                                            )
        else:
            ObjToReplyTopic = None
            
        return ObjToServer,ObjToReplyTopic