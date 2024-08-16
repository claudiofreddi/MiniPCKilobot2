
from __future__ import annotations
import json
import socket
import uuid
from Socket_ConsoleLog import * 
from json import JSONEncoder
import time

### ***************************************************************************
### Message FORMAT
### ***************************************************************************

class Socket_Default_Message_Topics:
    NONE = ""                                  #Not subscrible 
    LOGIN = "LOGIN"                             #Not subscrible 
    MESSAGE = "/MESSAGE"                       #Not subscrible 
    TOPIC_ADD = "/TOPIC/ADD"                    #Not subscrible 
    TOPIC_SUBSCRIBE = "/TOPIC/SUBSCRIBE"        #Not subscrible 
    TOPIC_UNSUBSCRIBE = "/TOPIC/UNSUBSCRIBE"    #Not subscrible 
    INPUT_KEYBOARD = "/INPUT/KEYBOARD"    
    INPUT_IMAGE = "/INPUT/IMAGE"
    INPUT_TELEGRAM = "/INPUT/TELEGRAM"
    SENSOR_BATTERY = "/SENSOR/BATTERY"
    SENSOR_COMPASS = "/SENSOR/COMPASS"
    OUTPUT_SPEAKER = "/OUTPUT/SPEAKER"
    OUTPUT_TELEGRAM = "/OUTPUT/TELEGRAM"
    #Arduino SAmple Class
    INPUT_OBJ00 = "INPUT/OBJ00"
    INPUT_OBJ01 = "INPUT/OBJ01"
    
    def IsTopicReserved(self,NewTopic):
        if (NewTopic == Socket_Default_Message_Topics.NONE
            or 
            NewTopic == Socket_Default_Message_Topics.TOPIC_ADD
            or 
            NewTopic == Socket_Default_Message_Topics.TOPIC_SUBSCRIBE
            or
            NewTopic == Socket_Default_Message_Topics.TOPIC_UNSUBSCRIBE
            or
            NewTopic == Socket_Default_Message_Topics.MESSAGE
            or
            NewTopic == Socket_Default_Message_Topics.LOGIN
            
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
    def __init__(self,Topic=Socket_Default_Message_Topics.NONE, UID = '',Message ="",
                 Value=0,RefreshInterval=5,LastRefresh = 0, IsAlert=False, Error ="",ByteData=''):
        self.Message = Message
        self.Value = Value
        self.Error = Error
        self.IsAlert = IsAlert
        if (UID==''):
            self.UID =  str(uuid.uuid4())
        self.RefreshInterval = RefreshInterval
        self.LastRefresh = LastRefresh
        self.ByteData = ByteData
        self.Topic = Topic
       

    def json(self):
        return json.dumps(self,cls=SocketEncoder,indent=4)
    
    def Copy(self,Source:Socket_Default_Message):
        self.Topic = Source.Topic
        self.Message = Source.Message
        self.Value = Source.Value
        self.Error = Source.Error
        self.IsAlert = Source.IsAlert 
        self.RefreshInterval = Source.RefreshInterval
        self.LastRefresh = Source.LastRefresh
        
    def GetMessageDescription(self):
        Txt =  " Message " + self.Message + " Value: " + str(self.Value) + " Topic: " + self.Topic
        if (self.Error != ""):
            Txt = Txt + self.Error 
        if (self.IsAlert == True):
            Txt = Txt + self.IsAlert
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