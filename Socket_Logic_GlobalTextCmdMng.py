from Socket_Struct_Messages import * 
from Socket_Utils_ConsoleLog import * 
from Socket_Struct_Server_Robot_Commands import * 

#Utils
class Socket_TextCommandParser():
    
    def __init__(self,CmdToParse):
        self.CmdToParse = str.lower(CmdToParse)
        
    
    def _parseText(self,InputCmd, pos, GetAllTailParams = False)->str:
        ValSplitted = str(InputCmd).split()
        if (pos<len(ValSplitted)):
            if (not GetAllTailParams):
                return str(ValSplitted[pos])
            else:
                return ' '.join(ValSplitted[pos:])
        return ''    
        
  
    def GetSpecificCommand(self):
        return self._parseText(self.CmdToParse,0)
    
    def GetSpecificCommandParam(self, paramPos, GetAllTailParams = False)-> str:
        return self._parseText(self.CmdToParse,paramPos,GetAllTailParams)

#Main Class    
class Socket_Logic_GlobalTextCmdMng(Common_LogConsoleClass):

    GET_HELP1 = "-help"
    GET_HELP2 = "?"
    GET_TOPICS = "get topics"
    GET_STATUS = "get status"
    GET_CLIENTS = "get clients"
        
    def __init__(self):
        pass
    
    def ListOfCommands(self):
        cmds = []
        cmds.append(self.GET_HELP1   + "     #this list")
        cmds.append(self.GET_HELP2   + "     #this list")
        cmds.append("")
        cmds.append(self.GET_STATUS  + "     #get params status")
        cmds.append(self.GET_TOPICS  + "     #get Topics")
        cmds.append(self.GET_CLIENTS + "     #get Clients")
        cmds.append("speak [Text]")
        return cmds

    def ParseCommandAndGetMsgs(self,InputCmd:str):
        try:
            RetValMsgs = []
            MyCmdParser = Socket_TextCommandParser(InputCmd)
            CmdLowered = MyCmdParser.GetSpecificCommand().lower()
            FullInputCmdLowered = InputCmd.lower()
       
            ## remapping ti Keyboard commands
            if (FullInputCmdLowered==self.GET_STATUS):
                CmdLowered = RobotListOfAvailableCommands.CTRL_S
                

            if (FullInputCmdLowered==self.GET_TOPICS):
                CmdLowered = RobotListOfAvailableCommands.CTRL_T

            if (FullInputCmdLowered==self.GET_CLIENTS):
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.SERVER_LOCAL,
                                                                Message =FullInputCmdLowered
                                                                )
                RetValMsgs.append(ObjToSend)    

            if (CmdLowered==RobotListOfAvailableCommands.SPEAK):
                TextToSpeech = MyCmdParser.GetSpecificCommandParam(1,True)

                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.OUTPUT_SPEAKER,
                                                            Message =TextToSpeech
                                                            )
                RetValMsgs.append(ObjToSend)
                
            #Server Side
            if (CmdLowered==RobotListOfAvailableCommands.CTRL_T
                or CmdLowered==RobotListOfAvailableCommands.CTRL_S
                or CmdLowered==RobotListOfAvailableCommands.CTRL_I
                or CmdLowered==RobotListOfAvailableCommands.CTRL_M):
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.SERVER_LOCAL,
                                                            Message =CmdLowered
                                                            )
                RetValMsgs.append(ObjToSend)
                    
            if (len(RetValMsgs)==0):
                print(f"Command {InputCmd} Not Found")
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.SERVER_LOCAL,
                                                            Message =InputCmd
                                                            )
                RetValMsgs.append(ObjToSend)
                
            return (len(RetValMsgs)>0), RetValMsgs
    
        except Exception as e:
            self.LogConsole("Error in Socket_Logic_TextCommands.Parse()  " + str(e),ConsoleLogLevel.Error)
            return False,[]