from Socket_Client_BaseClass import * 
from Socket_Utils_Timer import * 
from Socket_Client_Actuators_Helpers import * 
import time
import telepot  
from telepot.loop import MessageLoop
from Socket_Server_Robot_Commands import *
from Socket_Utils_Q import * 
from Socket_Utils_Timer import *
import cv2
from PIL import Image
import numpy as np

class RobotTelegramCommands:
    
    TELEGRAM_START = "start"
    TELEGRAM_GETSTATUS = "status"
    TELEGRAM_SURVEILLANCE_ON_OFF = "cam"
    TELEGRAM_EXIT = "exit"
    TELEGRAM_HELP = "help"

    def __init__(self):
        return
    
    def GetList():
       
        Prefix = ''
        Cmds =  ""
        Cmds = Cmds + '\n' + Prefix + RobotTelegramCommands.TELEGRAM_START  + " "
        Cmds = Cmds + '\n' + Prefix + RobotTelegramCommands.TELEGRAM_GETSTATUS  + " "
        Cmds = Cmds + '\n' + Prefix + RobotTelegramCommands.TELEGRAM_SURVEILLANCE_ON_OFF  + " (switch on-off)"
        Cmds = Cmds + '\n' + Prefix + RobotTelegramCommands.TELEGRAM_EXIT  + " " 

        return Cmds
    
    
class SocketClient_Telegram(Socket_Client_BaseClass):

    bot = telepot.Bot(TELEGRAM_TOKEN)
    MyTimer = Socket_Timer()
    PHOTO_SEND_MIN_INTERVAL_SEC = 10
    LOCAL_TEMP_IMAGE = "c:/dati/Snapshot/LocalTempPhoto.png"
    SurveillanceMode = True
    
    def __init__(self, ServiceName = Socket_Services_List.TELEGRAM, ForceServerIP = '',ForcePort='',LogOptimized = False):
        super().__init__(ServiceName,ForceServerIP,ForcePort,LogOptimized)
        
        self.Telegram_Enabled = True
        self.GlbFlagProcessKilled = False
        self.TelegramMsgQ = Socket_Q[str]("Telegram Msgs")
        self.MyTimer.start(self.PHOTO_SEND_MIN_INTERVAL_SEC)
        
        self.on_chat_send_master_message(self.bot, 'Listening..')
        self.on_chat_send_master_message(self.bot, "SurveillanceMode: cam is " + "on" if self.SurveillanceMode else "off")
        self.on_chat_send_master_message(self.bot, self.GetListOfCommands())
        MessageLoop(self.bot, self.on_chat_message).run_as_thread()
        
        super().LogConsole('Telegram Listening ...')
        
        
    def GetListOfCommands(self) -> str:
        return 'Ecco i comandi che capisco:\n' + RobotTelegramCommands.GetList() + '\n' + RobotListOfAvailableCommands.GetList()
    
    def on_chat_message(self,msg):
        contents_type, chat_type, chat_id = telepot.glance(msg)
        IsToSendToServer = True   
        if contents_type == 'text':
            name = msg["from"]["first_name"]
            txt = msg['text']
            MyCmd = txt.lower()
            #super().LogConsole(msg)
            super().LogConsole('Comando: ' + MyCmd,ConsoleLogLevel.Test)
            super().LogConsole('from: '  + name,ConsoleLogLevel.Test)
                    
       
            if (MyCmd == RobotTelegramCommands.TELEGRAM_START):
                self.bot.sendMessage(chat_id, 'ciao {}, sono kilobot'.format(name))
                IsToSendToServer = False
            
            elif (MyCmd == RobotTelegramCommands.TELEGRAM_HELP):
                self.bot.sendMessage(chat_id, self.GetListOfCommands())
                IsToSendToServer = False
       
            elif (MyCmd == RobotTelegramCommands.TELEGRAM_SURVEILLANCE_ON_OFF):
                self.SurveillanceMode = not self.SurveillanceMode
                Text = "SurveillanceMode: cam is " + "on" if self.SurveillanceMode else "off"
                self.bot.sendMessage(chat_id, Text)
                IsToSendToServer = False
                            
            elif (MyCmd == RobotTelegramCommands.TELEGRAM_EXIT):
                self.bot.sendMessage(chat_id, "Bot kill")
                super().LogConsole("Bot killed")
                #self MyProcessesStatus.SetStatus(self.THIS_PROCESS_NAME,ProcessesStatus.KILLED)
                time.sleep(1)
                self.GlbFlagProcessKilled = True
            
                   
            # else:
            #     self.bot.sendMessage(chat_id, f'Mi spiace {name}, non capisco {MyCmd}\nUsa /help per sapere cosa posso fare!')
            if (IsToSendToServer):
                print("k->:" +MyCmd)
                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.INPUT_TELEGRAM,
                                                                                Message = MyCmd, Value = 0)
                                
                self.SendToServer(ObjToSend) 


    def on_chat_send_master_message(self,bot, text_msg):
        print("z->: " + text_msg)
        bot.sendMessage(TELEGRAM_MASTER_TARGET,text_msg)
        
            
    def OnClient_Connect(self):
        
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
    
    def On_ClientAfterLogin(self):
        self.RegisterTopics(Socket_Default_Message_Topics.INPUT_TELEGRAM,Socket_Default_Message_Topics.OUTPUT_TELEGRAM)
        self.SubscribeTopics(Socket_Default_Message_Topics.INPUT_IMAGE )
        
        
        

    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreayManaged=False):
        #ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
        
        try:
            if (IsMessageAlreayManaged == False):
                if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                    ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                    
                    # if (ReceivedMessage.Topic == Socket_Default_Message_Topics.INPUT_KEYBOARD):
                    #     self.TelegramMsgQ.put(ReceivedMessage.Message)   
                        
                    if (ReceivedMessage.Topic == Socket_Default_Message_Topics.OUTPUT_TELEGRAM):
                        print("->x: " + ReceivedMessage.Message)
                        self.TelegramMsgQ.put(ReceivedMessage.Message)     
                        
                    if (ReceivedMessage.Topic== Socket_Default_Message_Topics.INPUT_IMAGE):
                        self.LogConsole("Receiving Image Data " + str(len(AdditionaByteData)),ConsoleLogLevel.Test)
                        if (self.SurveillanceMode):
                            if (len(AdditionaByteData)>0):
                                #Wait some time before resend an image
                                if (self.MyTimer.IsTimeout()):
                                    frame= pickle.loads(AdditionaByteData, fix_imports=True, encoding="bytes")
                                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR) 
                                    
                                    cv2.imwrite(self.LOCAL_TEMP_IMAGE , frame) 
                                    self.LogConsole(f"Sending Image Data To Telegram {str(len(AdditionaByteData))} {ReceivedMessage.Value}%",ConsoleLogLevel.CurrentTest)
                                    self.bot.sendPhoto(TELEGRAM_MASTER_TARGET,open(self.LOCAL_TEMP_IMAGE , 'rb'))
                                    self.MyTimer.Reset(self.PHOTO_SEND_MIN_INTERVAL_SEC)     
                        
                                               
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 

    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
            
            if (self.GlbFlagProcessKilled):
               return self.OnClient_Core_Task_RETVAL_QUIT
            
            if (self.TelegramMsgQ.HasItems()): 
                
                TextToSend = self.TelegramMsgQ.get()
                print("y->: " + TextToSend)
                if (TextToSend != ''):
                    if (self.Telegram_Enabled):
                        self.bot.sendMessage(TELEGRAM_MASTER_TARGET,TextToSend)
            
            # ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.TELEGRAM, 
            #                                                         Message = "Test", Value = self.MyTimer.GetElapsed())                
                
            
            # self.SendToServer(ObjToSend) 
            # self.LogConsole(self.ThisServiceName() + " " + ObjToSend.GetMessageDescription(),ConsoleLogLevel.Always)
        
                    
            if (self.IsQuitCalled):
                return self.OnClient_Core_Task_RETVAL_QUIT
        
            return self.OnClient_Core_Task_RETVAL_OK
            
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
     
        
if (__name__== "__main__"):
    
    MySocketClient = SocketClient_Telegram()
    
    MySocketClient.Run_Threads()