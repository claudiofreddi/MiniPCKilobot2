from Socket_Struct_Messages import * 
from Socket_Utils_ConsoleLog import * 
from Socket_Struct_Server_Robot_Commands import * 
from Socket_Utils_Text import Padding, PaddingTuples
from Socket_Utils_TextCommand_Parser import * 
from Socket_Struct_ListOfCommands import * 

class ServerLocalCommands:

    GET_HELP = "?"
    GET_TOPICS = "get topics"
    GET_STATUS = "get status"
    GET_CLIENTS = "get clients"
    GET_SENSORS = "get sensors"
    GET_COMMANDS = "get commands"
    SHOW_SERVER_MSGS = "togglemsgs"
    SHOW_SERVER_IMAGE = "toggleimage"


# #Main Class    
# class ServerLocalCommands_Executor(Common_LogConsoleClass):

#     def __init__(self):
#         pass
        
#     def  Execute_Listed_Command(self,ReceivedMessage:Socket_Default_Message,pCmd:ServiceCommand):
#         try:
           
            
#             RetValMsgs = []
#             MyCmdParser = Socket_TextCommandParser(InputCmd)
#             CmdLowered = MyCmdParser.GetSpecificCommand().lower()
#             FullInputCmdLowered = InputCmd.lower()
            
#             if (ServerLocalCommands)
            
#             ## ***************************************************
#             ## remapping di Keyboard commands
#             ## ***************************************************
#             if (FullInputCmdLowered==self.GET_STATUS):
#                 CmdLowered = RobotListOfAvailableCommands.CTRL_S

#             if (FullInputCmdLowered==self.GET_TOPICS):
#                 CmdLowered = RobotListOfAvailableCommands.CTRL_T
                
#             if (FullInputCmdLowered==self.SHOW_SERVER_MSGS):
#                 CmdLowered = RobotListOfAvailableCommands.CTRL_M
                
#             if (FullInputCmdLowered==self.SHOW_SERVER_IMAGE):
#                 CmdLowered = RobotListOfAvailableCommands.CTRL_I

#             ## ***************************************************
#             ## Server Local Msgs
#             ## ***************************************************
#             if (FullInputCmdLowered==self.GET_CLIENTS):
#                 ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.SERVER_LOCAL,
#                                                                 Message =FullInputCmdLowered
#                                                                 ,ReplyToTopic=ReceivedMessage.ReplyToTopic
#                                                                 )
#                 RetValMsgs.append(ObjToSend)    
               
#             #Server Side
#             if (CmdLowered==RobotListOfAvailableCommands.CTRL_T
#                 or CmdLowered==RobotListOfAvailableCommands.CTRL_S
#                 or CmdLowered==Socket_Logic_GlobalTextCmdMng.GET_COMMANDS
#                 or CmdLowered==RobotListOfAvailableCommands.CTRL_I
#                 or CmdLowered==RobotListOfAvailableCommands.CTRL_M
#                 or CmdLowered==Socket_Logic_GlobalTextCmdMng.GET_HELP1 
#                 or CmdLowered==Socket_Logic_GlobalTextCmdMng.GET_HELP2):
#                 ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.SERVER_LOCAL,
#                                                             Message = CmdLowered
#                                                             ,ReplyToTopic=ReceivedMessage.ReplyToTopic
#                                                             )
#                 RetValMsgs.append(ObjToSend)
            
#             ## ***************************************************
#             ## OTHER CLIENT MSGS
#             ## ***************************************************
#             if (CmdLowered==RobotListOfAvailableCommands.SPEAK):
#                 TextToSpeech = MyCmdParser.GetSpecificCommandParam(1,True)

#                 ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.OUTPUT_SPEAKER,
#                                                             Message =TextToSpeech
#                                                             ,ReplyToTopic=ReceivedMessage.ReplyToTopic
#                                                             )
#                 RetValMsgs.append(ObjToSend)

#             if (FullInputCmdLowered.startswith(self.TARGET_CLIENT_PREFIX)):
#                 MyCmdParser2 = Socket_TextCommandParser(InputCmd[1:])
#                 GetClientName = MyCmdParser2.GetSpecificCommand()
#                 GetAllParams = MyCmdParser2.GetSpecificCommandParam(1,True)
#                 ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD,
#                                                             Message =GetAllParams
#                                                             ,ReplyToTopic=ReceivedMessage.ReplyToTopic
#                                                             ,TargetClientName=GetClientName
#                                                             )
#                 RetValMsgs.append(ObjToSend) 
                
            
                    
#             if (len(RetValMsgs)==0):
#                 #print(f"Command {InputCmd} Not Found")
#                 if (ReceivedMessage.ReplyToTopic!=""):
#                     ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.SERVER_LOCAL,
#                                                                 Message =InputCmd
#                                                                 ,ReplyToTopic=ReceivedMessage.ReplyToTopic
#                                                                 )
#                     RetValMsgs.append(ObjToSend)
                
#             return (len(RetValMsgs)>0), RetValMsgs
        
#             return CommandExecuted, CommandRetval
        
    
#         except Exception as e:
#             self.LogConsole("Error in Socket_Logic_TextCommands.Parse()  " + str(e),ConsoleLogLevel.Error)
#             return False,[]