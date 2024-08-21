
from __future__ import annotations
import json
import socket
import uuid
from Socket_Utils_ConsoleLog import * 
from json import JSONEncoder
import time
from Socket_Struct_Services_List import Socket_Services_List

### ***************************************************************************
### Message FORMAT
### ***************************************************************************

class Socket_Default_Message_Topics:
    NONE = ""                                           #Not subscrible 
    LOGIN = "LOGIN"                                     #Not subscrible 
    MESSAGE = "/MESSAGE"                                #Not subscrible 
    SERVER_LOCAL = "/TOPIC/SERVER_LOCAL"                #Not subscrible 
    TOPIC_REGISTER = "/TOPIC/ADD"                            #Not subscrible 
    TOPIC_SUBSCRIBE = "/TOPIC/SUBSCRIBE"                #Not subscrible 
    TOPIC_UNSUBSCRIBE = "/TOPIC/UNSUBSCRIBE"            #Not subscrible 
    TOPIC_CLIENT_STANDBY_CMD = "/TOPIC/CLIENT_STANDBY_CMD"    #Not subscrible    to remove
    TOPIC_CLIENT_STANDBY_ACK = "/TOPIC/CLIENT_STANDBY_ACK"    #Not subscrible    to remove
    TOPIC_CLIENT_DIRECT_CMD = "/TOPIC/CLIENT_DIRECT"    #Not subscrible    
    TOPIC_CLIENT_PARAM_UPDATED = "/TOPIC/CLIENT_PARAM_UPDATED"    #Not subscrible    
    
    INPUT_KEYBOARD = "/INPUT/KEYBOARD"    
    INPUT_IMAGE = "/INPUT/IMAGE"
    INPUT_TELEGRAM = "/INPUT/TELEGRAM"
    INPUT_LIDAR = "/INPUT/LIDAR"
    INPUT_TEXT_COMMANDS = "/INPUT/TEXT_COMMANDS"
    INPUT_JOYSTICK = "/INPUT/JOYSTICK"
    
    SENSOR_BATTERY = "/SENSOR/BATTERY"
    SENSOR_COMPASS = "/SENSOR/COMPASS"
    OUTPUT_SPEAKER = "/OUTPUT/SPEAKER"
    OUTPUT_TELEGRAM = "/OUTPUT/TELEGRAM"
    OUTPUT_TEXT_COMMANDS = "/OUTPUT/TEXT_COMMANDS"
    
    #Arduino Sample Class
    INPUT_OBJ00 = "INPUT/OBJ00"
    INPUT_OBJ01 = "INPUT/OBJ01"
    
    def IsTopicReserved(self,NewTopic):
        if (NewTopic == Socket_Default_Message_Topics.NONE
            or 
            NewTopic == Socket_Default_Message_Topics.TOPIC_REGISTER
            or 
            NewTopic == Socket_Default_Message_Topics.TOPIC_SUBSCRIBE
            or
            NewTopic == Socket_Default_Message_Topics.TOPIC_UNSUBSCRIBE
            or
            NewTopic == Socket_Default_Message_Topics.MESSAGE
            or
            NewTopic == Socket_Default_Message_Topics.LOGIN
            or
            NewTopic == Socket_Default_Message_Topics.SERVER_LOCAL
            or
            NewTopic == Socket_Default_Message_Topics.TOPIC_CLIENT_STANDBY_CMD
            or
            NewTopic == Socket_Default_Message_Topics.TOPIC_CLIENT_STANDBY_ACK
            or
            NewTopic == Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD
            ):
            return True
        
        return False
    
### ***************************************************************************
### Ecoder e Decoder (JSON <-> Class)
### ***************************************************************************
class SocketEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__  

class SocketDecoder:
    def get(CodedJson):
        return  json.loads(CodedJson)
   

class Socket_Default_Message(Common_LogConsoleClass):
    def __init__(self,Topic=Socket_Default_Message_Topics.NONE,Message ="",
                 Value=0, ValueStr="",ByteData='', ResultList= []
                 , ReplyToTopic=Socket_Default_Message_Topics.NONE 
                 , TargetClientName = Socket_Services_List.NONE
                 ):
        self.Message = Message
        self.Value = Value
        self.ValueStr = ValueStr
        self.ByteData = ByteData
        self.Topic = Topic
        self.ResultList = ResultList
        self.ReplyToTopic = ReplyToTopic
        self.TargetClientName = TargetClientName
       

    def json(self):
        return json.dumps(self,cls=SocketEncoder,indent=4)
    
    def Copy(self,Source:Socket_Default_Message):
        self.Topic = Source.Topic
        self.Message = Source.Message
        self.Value = Source.Value
        self.ValueStr = Source.ValueStr
        self.ByteData = Source.ByteData       
        self.ResultList = Source.ResultList
        self.ReplyToTopic = Source.ReplyToTopic
        self.TargetClientName = Source.TargetClientName
        
    def GetMessageDescription(self):
        Txt =  " Message " + self.Message + " Value: " + str(self.Value) + " Topic: " + self.Topic+ " ValueStr: " + str(self.ValueStr) 
        Txt += " Reply To Topic: " + str(self.ReplyToTopic)
        Txt += " Target Client Name: " + str(self.TargetClientName)
        return Txt
    
    def _ShowStdMessageJsonForma(self):
        self.LogConsole(self.json(),ConsoleLogLevel.Control)
        
class SocketMessageEnvelopeContentType:
    STANDARD = "STANDARD"
    
    
class SocketMessageEnvelopeTargetType:
    SERVER = "SERVER"
    BROADCAST = "BROADCAST"
    
class SocketMessageEnvelope:
    def  __init__(self,Uid = "",ContentType=SocketMessageEnvelopeContentType.STANDARD,EncodedJson='',
                  From='',To='',
                  NeedResponse=False,Response='',ShowContentinLog = False,SendTime=0): 
        self.Uid = uuid.uuid4
        self.ContentType = ContentType
        self.EncodedJson = EncodedJson
        self.NeedResponse = NeedResponse
        self.Response = Response
        self.ShowContentinLog = ShowContentinLog
        self.From=From
        self.To=To
        self.SendTime = time.time()
            
    def GetReceivedMessage(self)->Socket_Default_Message:
                  
        ReceivedMsg:Socket_Default_Message = Socket_Default_Message(**SocketDecoder.get(self.EncodedJson))    
        
        return ReceivedMsg

    def GetEnvelopeDescription(self) -> str:
        return "Envelope [" + self.ContentType + "] From " + self.From + " To: " + self.To 