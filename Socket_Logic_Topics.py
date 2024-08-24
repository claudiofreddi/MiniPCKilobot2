from Socket_Struct_Messages import *

class TopicReserved:
    ReservedTopic_Starts_With_Slash = "/"
    ReservedTopic_Starts_With_At = "@" 
    ReservedTopic_For_Command = "#CMD#"
    ReservedTopic_For_Param = "#PARAM#"
    ReservedTopic_For_Param_Bool = "#B#"
    ReservedTopic_For_Param_Int = "#I#"
    ReservedTopic_For_Param_Float = "#F#"
    ReservedTopic_For_Param_Str = "#S#"
    ReservedTopic_For_ReplyTo = "#REPLYTO#"
    
class TopicType:
    Specific = "S"
    Generic = "G"
    
class TopicParamType:
    Int = "int"
    Bool = "bool"
    String = "str"
    Float = "float"
    
class Topics_Standard_For_Service():
          
    def __init__(self,ServiceName:str):
        self.ServiceName = ServiceName
        
        #Std Topics
        self.ServiceTopic = TopicReserved.ReservedTopic_Starts_With_Slash + TopicReserved.ReservedTopic_Starts_With_At + self.ServiceName
        self.ServiceCommandTopic = self.ServiceTopic  + "/" + TopicReserved.ReservedTopic_For_Command
        self.ServiceParamsTopic = self.ServiceTopic  + "/" + TopicReserved.ReservedTopic_For_Param
        self.ServiceReplyToTopic = self.ServiceTopic + "/" + TopicReserved.ReservedTopic_For_ReplyTo
    
    def GetInfoForStatusParam(self,ParamName, ArgsDescription):
        LocalParamName = self.ServiceName + "_" + ParamName
        UserCmd=self.ServiceParamsTopic + "/" + ParamName
        if (ArgsDescription!=""):
            UserCmdDescription = UserCmd + "/[" + ArgsDescription + "]"
        else:
            UserCmdDescription = UserCmd  
        return  LocalParamName, UserCmd, UserCmdDescription
    
    def GetInfoForCommands(self,CommandName, ArgsDescription):
        LocalParamName = self.ServiceName + "_" + CommandName
        if (self.ServiceName == Socket_Services_List.SERVER):
            UserCmd=CommandName
        else:
            UserCmd=self.ServiceCommandTopic + "/" + CommandName
        if (ArgsDescription!=""):
            UserCmdDescription = UserCmd + "/[" + ArgsDescription + "]"
        else:   
            UserCmdDescription = UserCmd
        return  LocalParamName, UserCmd, UserCmdDescription
    
class TopicManager():
    
    def __init__(self,Topic:str):
       
        self.Topic = Topic
        self.IsValid = False
        self.TopicType = ""
        self.TargetService = ""
        self.IsCommand = False
        self.IsParam = False
        self.IsReplyTo = False
        self.Command = ""
        self.Args = ""
        self.Param = ""
        self.ParamVal = ""

        IsOK = False
        shift = 0
        self.IsValid = Topic.startswith(TopicReserved.ReservedTopic_Starts_With_Slash)
        if (self.IsValid):
            SubTopics = self.Topic.split(TopicReserved.ReservedTopic_Starts_With_Slash)
            #Check Target : first is ''
            if (len(SubTopics)>1):
                if (SubTopics[1].startswith(TopicReserved.ReservedTopic_Starts_With_At)):
                    self.TargetService = SubTopics[1][1:]
                    self.TopicType = TopicType.Specific
                else:
                    self.TopicType = TopicType.Generic
                    IsOK = True 
                    shift = -1
            if (len(SubTopics)>2+shift):
                Token = SubTopics[2+shift]
                if (Token == TopicReserved.ReservedTopic_For_Command):
                    self.IsCommand = True
                    if (len(SubTopics)>3+shift):
                        self.Command = SubTopics[3+shift]
                        IsOK = True #OK at Command Name
                        if (len(SubTopics)>4+shift):
                            self.Args = SubTopics[4+shift]
                elif (Token == TopicReserved.ReservedTopic_For_Param):
                    self.IsParam = True
                   
                    if (len(SubTopics)>3):
                        self.Param = SubTopics[3+shift]     
                        IsOK = True #OK at Param Name                        
                        if (len(SubTopics)>4+shift):
                            self.ParamVal = SubTopics[4+shift]   
                        
                elif (Token == TopicReserved.ReservedTopic_For_ReplyTo):
                    self.IsReplyTo = True
                    IsOK = True 
                
        self.IsValid =  self.IsValid and IsOK
                
    def Describe(self):
        Txt = ""
        Txt += f"Topic:  { self.Topic}\n"
        Txt += f"IsValid:  {self.IsValid}\n"
        Txt += f"Topic Type:  { self.TopicType}\n"
        Txt += f"TargetService:  {self.TargetService}\n"
        Txt += f"IsCommand:  {self.IsCommand }\n"
        Txt += f"IsParam:  {self.IsParam}\n"
        Txt += f"IsReplyTo:  {self.IsReplyTo}\n"
        Txt += f"Command:  { self.Command}\n"
        Txt += f"Command Args:  { self.Args}\n"
        Txt += f"Param:  {self.Param}\n"
        Txt += f"Param Val:  {self.ParamVal}\n"
        return Txt

    

if (__name__== "__main__"):
    # #Server
    
    # #subscribe:
    #     "/#CMD#"
    #     "/#PARAM#"
    #     "/#REPLYTO#"
        
    # #Clients:
    #     #subscribe:
    #     "/@SAMPLE_Client/#CMD#"
    #     "/@SAMPLE_Client/#PARAM#"
    #     "/@SAMPLE_Client/#REPLYTO#"
    
    MyTopicTest = TopicManager("/#CMD#/PIPPO")
    print(MyTopicTest.Describe()) 
    MyTopicTest = TopicManager("/#PARAM#/PLUTO")
    print(MyTopicTest.Describe()) 
    MyTopicTest = TopicManager("/#REPLYTO#")
    print(MyTopicTest.Describe()) 
    
    #Client Specific Command   
    MyTopicTest = TopicManager("/@SAMPLE_Client/#CMD#/SPEAK/PIPPO ciao")
    print(MyTopicTest.Describe()) 
    
    #Client Specific: Set Param Value
    MyTopicTest = TopicManager("/@SAMPLE_Client/#PARAM#/STANDBY/1")
    print(MyTopicTest.Describe()) 
    
    #Client Specific: Not Valid
    MyTopicTest = TopicManager("/@SAMPLE_Client/#PARAM_B#/STANDBY/ON")
    print(MyTopicTest.Describe())  
    
    #Client Specific: ReplyTo
    MyTopicTest = TopicManager("/@SAMPLE_Client/#REPLYTO#")
    print(MyTopicTest.Describe()) 
    
    #Client Specific: Command
    MyTopicTest = TopicManager("/@SAMPLE_Client/#CMD#/MOV/FW")
    print(MyTopicTest.Describe()) 

    #Generic
    MyTopicTest = TopicManager("/INPUT/SENSOR/COMPASS")
    print(MyTopicTest.Describe()) 
