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
    
    def Utils_Split_Cmd_Param(self, CmdToParse="",Lowered=True):
        if (CmdToParse!=""):
            self.CmdToParse = CmdToParse
        if (Lowered):self.CmdToParse =self.CmdToParse.lower()
        return self.GetSpecificCommand(), self.GetSpecificCommandParam(1,True)
     
    def Utils_Split_Cmd_Param_Param(self, CmdToParse="",Lowered=True):
        if (CmdToParse!=""):
            self.CmdToParse = CmdToParse
        if (Lowered):self.CmdToParse =self.CmdToParse.lower()
        return self.GetSpecificCommand(), self.GetSpecificCommandParam(1,False), self.GetSpecificCommandParam(2,True)
        
#Sample
# MyTP = Socket_TextCommandParser("pippo pluto e paparino")
# print(MyTP.Utils_Split_Cmd_Param())
# print(MyTP.Utils_Split_Cmd_Param_Param())
# print(MyTP.Utils_Split_Cmd_Param("Testo 1"))
# print(MyTP.Utils_Split_Cmd_Param_Param("Testo 1"))

#Main Class    
class Socket_Logic_GlobalTextCmdMng(Common_LogConsoleClass):

    GET_HELP1 = "-help"
    GET_HELP2 = "?"
    GET_TOPICS = "get topics"
    GET_STATUS = "get status"
    GET_CLIENTS = "get clients"
    SHOW_SERVER_MSGS = "show messages"
    SHOW_SERVER_IMAGE = "show image"
    TARGET_CLIENT_PREFIX = "@"    
    
    def __init__(self):
        pass
    def Padding(self,txt):
        return ('{: <20}'.format(txt))
        
    def ListOfCommands(self):
        cmds = []
        cmds.append(self.Padding(self.GET_STATUS)             + "      ->get params status (Ctrl+S with Keyboard)")
        cmds.append(self.Padding(self.GET_TOPICS)             + "      ->get Topics (Ctrl+T with Keyboard)")
        cmds.append(self.Padding(self.SHOW_SERVER_MSGS)       + "      ->show Messages on/off (Ctrl+M with Keyboard)")
        cmds.append(self.Padding(self.SHOW_SERVER_IMAGE)      + "      ->show Image (Ctrl+I with Keyboard)")
        cmds.append(self.Padding(self.GET_CLIENTS)            + "      ->get Clients")
        cmds.append(self.Padding(self.TARGET_CLIENT_PREFIX)   + "      ->TargetPrefix  sample: [@KEYBOARD_Client idle on] ")
        cmds.append(self.Padding("speak [Text]")              + "      ->Speak a Text")
        return cmds
    
    def ShowCommands(self):
        cmds = self.ListOfCommands()
        Txt = ""
        Txt += "---------------------------------" + "\n"
        Txt += "AVAILABLE COMMANDS:" + "\n"

        for c in cmds:
            Txt += c + "\n"
        
        Txt += "---------------------------------" + "\n"
        return Txt
        
    def ParseCommandAndGetMsgs(self,ReceivedMessage:Socket_Default_Message):
        try:
            RetValMsgs = []
            InputCmd = ReceivedMessage.Message
            MyCmdParser = Socket_TextCommandParser(InputCmd)
            CmdLowered = MyCmdParser.GetSpecificCommand().lower()
            FullInputCmdLowered = InputCmd.lower()
            
            ## ***************************************************
            ## remapping di Keyboard commands
            ## ***************************************************
            if (FullInputCmdLowered==self.GET_STATUS):
                CmdLowered = RobotListOfAvailableCommands.CTRL_S

            if (FullInputCmdLowered==self.GET_TOPICS):
                CmdLowered = RobotListOfAvailableCommands.CTRL_T
                
            if (FullInputCmdLowered==self.SHOW_SERVER_MSGS):
                CmdLowered = RobotListOfAvailableCommands.CTRL_M
                
            if (FullInputCmdLowered==self.SHOW_SERVER_IMAGE):
                CmdLowered = RobotListOfAvailableCommands.CTRL_I

            ## ***************************************************
            ## Server Local Msgs
            ## ***************************************************
            if (FullInputCmdLowered==self.GET_CLIENTS):
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.SERVER_LOCAL,
                                                                Message =FullInputCmdLowered
                                                                ,ReplyToTopic=ReceivedMessage.ReplyToTopic
                                                                )
                RetValMsgs.append(ObjToSend)    
               
            #Server Side
            if (CmdLowered==RobotListOfAvailableCommands.CTRL_T
                or CmdLowered==RobotListOfAvailableCommands.CTRL_S
                or CmdLowered==RobotListOfAvailableCommands.CTRL_I
                or CmdLowered==RobotListOfAvailableCommands.CTRL_M
                or CmdLowered==Socket_Logic_GlobalTextCmdMng.GET_HELP1 
                or CmdLowered==Socket_Logic_GlobalTextCmdMng.GET_HELP2):
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.SERVER_LOCAL,
                                                            Message = CmdLowered
                                                            ,ReplyToTopic=ReceivedMessage.ReplyToTopic
                                                            )
                RetValMsgs.append(ObjToSend)
            
            ## ***************************************************
            ## OTHER CLIENT MSGS
            ## ***************************************************
            if (CmdLowered==RobotListOfAvailableCommands.SPEAK):
                TextToSpeech = MyCmdParser.GetSpecificCommandParam(1,True)

                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.OUTPUT_SPEAKER,
                                                            Message =TextToSpeech
                                                            ,ReplyToTopic=ReceivedMessage.ReplyToTopic
                                                            )
                RetValMsgs.append(ObjToSend)

            if (FullInputCmdLowered.startswith(self.TARGET_CLIENT_PREFIX)):
                MyCmdParser2 = Socket_TextCommandParser(InputCmd[1:])
                GetClientName = MyCmdParser2.GetSpecificCommand()
                GetAllParams = MyCmdParser2.GetSpecificCommandParam(1,True)
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD,
                                                            Message =GetAllParams
                                                            ,ReplyToTopic=ReceivedMessage.ReplyToTopic
                                                            ,TargetClientName=GetClientName
                                                            )
                RetValMsgs.append(ObjToSend) 
                
            
                    
            if (len(RetValMsgs)==0):
                #print(f"Command {InputCmd} Not Found")
                if (ReceivedMessage.ReplyToTopic!=""):
                    ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.SERVER_LOCAL,
                                                                Message =InputCmd
                                                                ,ReplyToTopic=ReceivedMessage.ReplyToTopic
                                                                )
                    RetValMsgs.append(ObjToSend)
                
            return (len(RetValMsgs)>0), RetValMsgs
    
        except Exception as e:
            self.LogConsole("Error in Socket_Logic_TextCommands.Parse()  " + str(e),ConsoleLogLevel.Error)
            return False,[]