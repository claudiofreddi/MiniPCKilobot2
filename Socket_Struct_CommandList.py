

from Socket_Utils_ConsoleLog import * 
from Socket_Struct_Messages import *
from Socket_Utils_Text import Padding, PaddingTuples

class ServiceCommand():
    def __init__(self,UserCmd:str="",UserCmdDescription:str="",ServiceName:str="", GiveFeedback=True, AltCommand="" ):
        self.UserCmd = UserCmd.lower()
        self.UserCmdDescription = UserCmdDescription.lower()
        self.ServiceName = ServiceName
        self.GiveFeedback = GiveFeedback
        self.AltCommand = AltCommand.lower()
        
    def GetDescription(self):
        retval = ""
        
        A = f"{self.UserCmd}"
            
        if (self.ServiceName == Socket_Services_List.SERVER):
            B = f">{self.UserCmdDescription}"
        else:
            B = f">@{self.ServiceName} {self.UserCmdDescription}"
        
        if (self.ServiceName == Socket_Services_List.SERVER):
            C = f"@{self.ServiceName}\n"
        else:
            C = "\n"

        retval += PaddingTuples((A,40), (B,40),(C,1))   
        
        return retval 
        
class ServiceCommandList(Common_LogConsoleClass):
   
    def __init__(self):
        self.List = []
    
    def Get(self,UserCmd:str):
        pObj:ServiceCommand
        for pObj in self.List:
            if (pObj.UserCmd.lower() == UserCmd.lower() or ((pObj.AltCommand!="") and pObj.AltCommand.lower()==UserCmd.lower()) ):
                    return pObj, True
        return None, False
        
    def CreateCommand(self,UserCmd:str="",UserCmdDescription:str="",ServiceName:str="", GiveFeedback=True, AltCommand="" ):
        pCmd:ServiceCommand
        pCmd, retval = self.Get(UserCmd)
        if (not retval):
            if (UserCmdDescription==""): UserCmdDescription = UserCmd
            pObj:ServiceCommand = ServiceCommand(UserCmd=UserCmd,UserCmdDescription=UserCmdDescription,ServiceName=ServiceName, GiveFeedback=GiveFeedback, AltCommand=AltCommand )
            self.List.append(pObj)
    
    def GetDescription(self):
        pCmd:ServiceCommand
        
        retval = "------------------------------------------------------------------------------" + "\n"
        retval += "Commands:\n\n" 
        
        for pCmd in self.List:
            retval += pCmd.GetDescription()
        retval += "------------------------------------------------------------------------------" + "\n"
        return retval
    
    
    def Util_Command_ConfimationMsg(self,CommandName,CommandRetVal:str,AlsoReplyToTopic=False,ReplyToTopic:str="")->Socket_Default_Message:
        ObjToServer:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_CLIENT_PARAM_SERVER_REGISTER
                                                                            #Suffix to service name
                                                                            ,Message = CommandName
                                                                            )
        if (AlsoReplyToTopic and ReplyToTopic!=""):
            ObjToReplyTopic:Socket_Default_Message = Socket_Default_Message(Topic = ReplyToTopic
                                                                            #Suffix to service name
                                                                            ,Message = f"Command  {CommandName} succesfully Executed: {CommandRetVal}"
                                                                            )
        else:
            ObjToReplyTopic = None
            
        return ObjToServer,ObjToReplyTopic