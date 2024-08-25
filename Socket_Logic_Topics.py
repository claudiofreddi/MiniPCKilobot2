from Socket_Struct_Messages import *

class TopicReserved:
    ReservedTopic_Starts_With_Slash = "/"
    ReservedTopic_Starts_With_At = "@" 
    ReservedTopic_For_Command = "#cmd#"
    ReservedTopic_For_Param = "#param#"
    ReservedTopic_For_Param_Bool = "#b#"
    ReservedTopic_For_Param_Int = "#i#"
    ReservedTopic_For_Param_Float = "#f#"
    ReservedTopic_For_Param_Str = "#s#"
    ReservedTopic_For_ReplyTo = "#replyto#"
 
    def Compose_URL(Type,ServiceName, Name,ArgDescr):
        URL = TopicReserved.ReservedTopic_Starts_With_Slash + TopicReserved.ReservedTopic_Starts_With_At + ServiceName
        if (Type == "P"):
            URL += TopicReserved.ReservedTopic_Starts_With_Slash + TopicReserved.ReservedTopic_For_Param
        if (Type == "C"):
            URL += TopicReserved.ReservedTopic_Starts_With_Slash + TopicReserved.ReservedTopic_For_Command
        URL += TopicReserved.ReservedTopic_Starts_With_Slash + Name
        if (ArgDescr !=""):
            URL += TopicReserved.ReservedTopic_Starts_With_Slash + "[" + ArgDescr + "]"
        return URL   

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
        "/@ServiceName"
        self.ServiceTopic = TopicReserved.ReservedTopic_Starts_With_Slash + TopicReserved.ReservedTopic_Starts_With_At + self.ServiceName
        
        "/@ServiceName/#CMD#"
        self.ServiceCommandTopic = self.ServiceTopic  + "/" + TopicReserved.ReservedTopic_For_Command
        "/@ServiceName/#PARAM#"
        self.ServiceParamsTopic = self.ServiceTopic  + "/" + TopicReserved.ReservedTopic_For_Param
        "/@ServiceName/#REPLYTO#"
        self.ServiceReplyToTopic = self.ServiceTopic + "/" + TopicReserved.ReservedTopic_For_ReplyTo
    

        
                    
    
class TopicManager():
    
    def __init__(self,Topic:str):
       
        self.Topic = Topic.lower()
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
    
    MyTopicTest = TopicManager("/@keyboard_client/#cmd#/quit")
    print(MyTopicTest.Describe()) 
    # MyTopicTest = TopicManager("/#PARAM#/PLUTO")
    # print(MyTopicTest.Describe()) 
    # MyTopicTest = TopicManager("/#REPLYTO#")
    # print(MyTopicTest.Describe()) 
    
    # #Client Specific Command   
    # MyTopicTest = TopicManager("/@SAMPLE_Client/#CMD#/SPEAK/PIPPO ciao")
    # print(MyTopicTest.Describe()) 
    
    # #Client Specific: Set Param Value
    # MyTopicTest = TopicManager("/@SAMPLE_Client/#PARAM#/STANDBY/1")
    # print(MyTopicTest.Describe()) 
    
    # #Client Specific: Not Valid
    # MyTopicTest = TopicManager("/@SAMPLE_Client/#PARAM_B#/STANDBY/ON")
    # print(MyTopicTest.Describe())  
    
    # #Client Specific: ReplyTo
    # MyTopicTest = TopicManager("/@SAMPLE_Client/#REPLYTO#")
    # print(MyTopicTest.Describe()) 
    
    # #Client Specific: Command
    # MyTopicTest = TopicManager("/@SAMPLE_Client/#CMD#/MOV/FW")
    # print(MyTopicTest.Describe()) 

    # #Generic
    # MyTopicTest = TopicManager("/INPUT/SENSOR/COMPASS")
    # print(MyTopicTest.Describe()) 
