#Env
from Robot_Envs import *
from ZOLD_Lib_Processes import *
from ZOLD_Lib_Commands_Interfaces import * 
from ZOLD_Robot_Shared_Objects import *

import time
import telepot  
from telepot.loop import MessageLoop


class RobotTelegramCommands:
    
    TELEGRAM_START = "start"
    TELEGRAM_GETSTATUS = "status"
    TELEGRAM_VIDEO_ON = "opencam"
    TELEGRAM_VIDEO_OFF = "closecam"
    TELEGRAM_EXIT = "exit"
    TELEGRAM_HELP = "help"

    def __init__(self):
        return
    
    def GetList():
       
        Prefix = ''
        Cmds =  ""
        Cmds = Cmds + '\n' + Prefix + RobotTelegramCommands.TELEGRAM_START  + " "
        Cmds = Cmds + '\n' + Prefix + RobotTelegramCommands.TELEGRAM_GETSTATUS  + " "
        Cmds = Cmds + '\n' + Prefix + RobotTelegramCommands.TELEGRAM_EXIT  + " " 

        return Cmds



class RobotTelegram_Obj(ProcessSuperClass):
    
    GlbFlagProcessKilled = False
    bot = telepot.Bot(TELEGRAM_TOKEN)
    
    def __init__(self,processName):
        super().__init__(processName)
        
    def GetListOfCommands(self) -> str:
        return 'Ecco i comandi che capisco:\n' + RobotTelegramCommands.GetList() + '\n' + RobotListOfAvailableCommands.GetList()
        
    def on_chat_message(self,msg):
        contents_type, chat_type, chat_id = telepot.glance(msg)
        if contents_type == 'text':
            name = msg["from"]["first_name"]
            txt = msg['text']
            MyCmd = txt.lower()
            #super().LogConsole(msg)
            super().LogConsole('Comando: ' + MyCmd)
            super().LogConsole('from: '  + name)
            
       
            if (MyCmd == RobotTelegramCommands.TELEGRAM_START):
                self.bot.sendMessage(chat_id, 'ciao {}, sono kilobot'.format(name))
            
            elif (MyCmd == RobotTelegramCommands.TELEGRAM_HELP):
                self.bot.sendMessage(chat_id, self.GetListOfCommands())
                        

            elif (MyCmd == RobotTelegramCommands.TELEGRAM_VIDEO_ON):
                self.SharedMem.VideoOn = True

            elif (MyCmd == RobotTelegramCommands.TELEGRAM_VIDEO_OFF):
                self.SharedMem.VideoOn = False

            elif (MyCmd == RobotTelegramCommands.TELEGRAM_GETSTATUS):
                self.bot.sendMessage(chat_id, 'Status')
                self.bot.sendMessage(chat_id, 'Compass: ' + str(self.SharedMem.Compass) + ' degrees')
                self.bot.sendMessage(chat_id, 'Speaker on: ' + ': ' + self.SharedMem.SpeakerOn)
                self.bot.sendMessage(chat_id, 'Mail on: ' + ': ' + self.SharedMem.MailOn)
                self.bot.sendMessage(chat_id, 'Telegram on: ' + ': ' + self.SharedMem.TelegramOn)
            
                        
            elif (MyCmd == RobotTelegramCommands.TELEGRAM_EXIT):
                self.bot.sendMessage(chat_id, "Bot kill")
                super().LogConsole("Bot killed")
                #self MyProcessesStatus.SetStatus(self.THIS_PROCESS_NAME,ProcessesStatus.KILLED)
                time.sleep(1)
                self.GlbFlagProcessKilled = True
            
                   
            else:
                NewRobotCommandInterface = RobotCommandInterface()
                NewRobotCommandInterface.SetCommand(MyCmd,RobotCommandExecutionStatus.TO_RUN)
                self.SharedMem.BrainCommandQ.put(NewRobotCommandInterface)
                #self.bot.sendMessage(chat_id, 'Mi spiace {}, non capisco\nUsa /help per sapere cosa posso fare!'.format(name))

    def on_chat_send_master_message(self,bot, text_msg):

        self.bot.sendMessage(TELEGRAM_MASTER_TARGET,text_msg)
        
    def Run(self,SharedMem:SharedObjs):
        super().Run_Pre(SharedMem)
 
        self.on_chat_send_master_message(self.bot, 'Listening..')
        self.on_chat_send_master_message(self.bot, self.GetListOfCommands())
        MessageLoop(self.bot, self.on_chat_message).run_as_thread()
        
        super().LogConsole('Listening ...')
        
        self.SharedMem.TelegramMsgQ.SetReady()
        
        Continue = True
        while (not self.GlbFlagProcessKilled) and Continue:

            #Insert here loop command
            if (self.SharedMem.TelegramMsgQ.HasItems()): 
                NewTelegramMsg:TelegramMsgInterface = self.SharedMem.TelegramMsgQ.get()
                if (NewTelegramMsg.TextToSend != ''):
                    if (self.SharedMem.TelegramOn):
                        self.bot.sendMessage(TELEGRAM_MASTER_TARGET,NewTelegramMsg.TextToSend)
            
            #End loop commands
            
            time.sleep(1)
            Continue = super().Run_CanContinueRunnig()
        super().Run_Kill()       
        exit
    

def RobotTelegram_Run(SharedMem:SharedObjs):
    MyRobotTelegram_Obj = RobotTelegram_Obj(ProcessList.Robot_Telegram)
    MyRobotTelegram_Obj.Run(SharedMem)
   

if (__name__== "__main__"):
    
    MySharedObjs = SharedObjs()     
    RobotTelegram_Run(MySharedObjs)    
