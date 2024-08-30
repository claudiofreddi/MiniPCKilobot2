# https://www.simplilearn.com/tutorials/python-tutorial/speech-recognition-in-python
# pip install SpeechRecognition 
# pip install pyaudio

# https://medium.com/john-snow-labs/the-complete-guide-to-information-extraction-from-texts-with-spark-nlp-and-python-c862dd33995f

from Socket_Struct_Client_BaseClass import * 
from Socket_Utils_Timer import * 
from  Socket_Logic_Topics import * 

import speech_recognition as sr
from Lib_SpeakToMe import *
from thefuzz import process, fuzz
from Socket_Server import ServerLocalCommands

class SocketClient_VoiceCommands(Socket_Client_BaseClass):

    ACTIVATION_KEYWORD = "robot"
    ACTIVATION_KEYWORD_WELCOME_MSG = "Ciao, dimmi"
    
    WAIT_TIMEOUT_AFTER_ASK = 15
    
        
    
    def __init__(self, ServiceName = Socket_Services_List.VOICE_COMMANDS, ForceServerIP = '',ForcePort='',LogOptimized = False):
        super().__init__(ServiceName,ForceServerIP,ForcePort,LogOptimized)
        try:
            
            self.collectionForKeyword = ["robot", "robots", "robi"]
            
            print("speak recognityion version:" + sr.__version__)
            
            MyServerLocalCommands = ServerLocalCommands()
            
            self.collection = ["come stai", "io sono", "spegni la luce"]
            for t in MyServerLocalCommands.__dict__.values():
                print(t)
                self.collection.append(t)
                    
            self.recognizer_instance = sr.Recognizer() # Crea una istanza del recognizer
            self.MySpeak = Service_SpeakToMe("",True)
            self.MyTimer = Socket_Timer()
            

            self.AskSomething = False
        
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in __init__()  " + str(e),ConsoleLogLevel.Error)
                    
       
    def OnClient_Connect(self):
        
        self.AskSomething = False
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
    
    def On_ClientAfterLogin(self):
        
        self.RegisterTopics(Socket_Default_Message_Topics.INPUT_VOICE_COMMAND)
        #self.SubscribeTopics(Socket_Default_Message_Topics.INPUT_KEYBOARD)
        #self.SubscribeTopics(Socket_Default_Message_Topics.INPUT_JOYSTICK)
              

        
        pass
    
    #Define here this client commands
    def After_Execute_Service_SpecificCommands(self,Command:str,Args:str, ReceivedMessage:Socket_Default_Message,AdditionaByteData=b''):
        
        try:
            CommandExecuted = False
            CommandRetval=  ""
            bAlsoReplyToTopic = True
            
            # if (Command == self.LOCAL_COMMAND_PRINT_THIS):
            #     print("THIS")
            #     CommandRetval=  "Printed"
            #     CommandExecuted = True
                
                

                
            
            self.LogConsole("*After_Execute_Service_SpecificCommands" + Command,ConsoleLogLevel.CurrentTest)
            
            
            return CommandExecuted, CommandRetval, bAlsoReplyToTopic
        
        
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return False, self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e), True
        
        
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreadyManaged=False):
        try:
            # if (self.IsConnected):
            #     if (not IsMessageAlreadyManaged):
            #         if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
            #             ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
            #             LocalTopicTest = TopicManager(ReceivedMessage.Topic)
            #             if (LocalTopicTest.IsValid):
            #                 pass #here speific topic commands
            #             else:
            #                 if (ReceivedMessage.Topic == Socket_Default_Message_Topics.MESSAGE):
            #                     pass #here others topic
            pass    
                            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
 
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 

    def GetBestUnderstoodCommand(self,UnderstoodText, BasedOnThisCollection):
        ListOfSimilarCommands = process.extract(UnderstoodText, BasedOnThisCollection, scorer=fuzz.ratio)
        BestListenedCommand = ""
        BestListenedCommandConfidence = 0

        #if any similarity found
        if (len(ListOfSimilarCommands)>0):
            self.LogConsole(str(ListOfSimilarCommands) ,ConsoleLogLevel.CurrentTest)
            BestListenedCommand, BestListenedCommandConfidence = ListOfSimilarCommands[0]
            
        return BestListenedCommand, BestListenedCommandConfidence
            
    def Client_Core_Task(self):
        try:
            
            with  sr.Microphone() as source:  
                self.recognizer_instance.adjust_for_ambient_noise(source,3)
                self.LogConsole(f"recognizer_instance.energy_threshold:  {self.recognizer_instance.energy_threshold}",ConsoleLogLevel.System)
                self.LogConsole(f"recognizer_instance.pause_threshold:  {self.recognizer_instance.pause_threshold}",ConsoleLogLevel.System)
                
                while not self.IsQuitCalled and self.IsConnected:
                   
                    #Basic Management of Service Idle 
                    pParam, retval  = self.LocalListOfStatusParams.GetByLocalName(self.ServiceParamStdBy)
                    if (retval):
                        if (pParam.Value==StatusParamListOfValues.ON): 
                            time.sleep(self.SLEEP_TIME)
                            continue

                        try:
                            if (not self.AskSomething):
                                self.LogConsole("Waiting keyword..." ,ConsoleLogLevel.System)
                            else:
                                self.LogConsole("Waiting request..." ,ConsoleLogLevel.System)
                                
                            audio = self.recognizer_instance.listen(source)
                            self.LogConsole("..." ,ConsoleLogLevel.System)
                            #print(len(audio.frame_data))
                            try:
                                UnderstoodText = self.recognizer_instance.recognize_google(audio, language="it-IT")
                                print(UnderstoodText)
                                self.LogConsole("Waiting request..." ,ConsoleLogLevel.System)
                                if (not self.AskSomething):
                                    BestListenedCommand, BestListenedCommandConfidence = self.GetBestUnderstoodCommand(UnderstoodText, self.collectionForKeyword)
                                    if (BestListenedCommandConfidence>70):
                                        self.LogConsole("Tell me...",ConsoleLogLevel.System)
                                                                                
                                        self.MySpeak.Speak(self.ACTIVATION_KEYWORD_WELCOME_MSG)
                                        self.MyTimer.start(self.WAIT_TIMEOUT_AFTER_ASK)
                                        self.AskSomething = True
                                else:
                                    BestListenedCommand, BestListenedCommandConfidence = self.GetBestUnderstoodCommand(UnderstoodText,self.collection)
                                    if (BestListenedCommand !="" and BestListenedCommandConfidence >60):
                                        CommandExecuted, CommandRetVal = self.LocalCommandManagement(BestListenedCommand, BestListenedCommandConfidence)
                                        if (not CommandExecuted):
                                            #Send TO Server
                                            self.LogConsole("#Send TO Server" ,ConsoleLogLevel.CurrentTest)
                                            ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.INPUT_VOICE_COMMAND,
                                                                                        Message =BestListenedCommand
                                                                                        ,Value= BestListenedCommandConfidence #Confidence
                                                                                        ,ReplyToTopic= self.Standard_Topics_For_Service.ServiceReplyToTopic  
                                                                                                    #self.Standard_Topics_For_Service.ServiceReplyToTopic  
                                                                                        )
                                            if (ObjToSend):
                                                self.SendToServer( ObjToSend)                                       
                                                    
                                if (self.MyTimer.IsTimeout()):
                                    self.LogConsole("Timed out",ConsoleLogLevel.System)
                                    self.AskSomething = False
                                
                                self.MyTimer.Reset()
                                    
                            except Exception as e:
                                self.AskSomething = False
                                print(e)
                                    
                        except Exception as e:
                            print(e)


                       
                    #self.SleepTime(Multiply=1,CalledBy="OnClient_Core_Task_Cycle",Trace=False)
                    
                    #NOT USED
                    #retval = self.OnClient_Core_Task_Cycle() 
                    
                    # if (retval == self.OnClient_Core_Task_RETVAL_QUIT):
                    #     self.Quit()
                    
                    # if (retval == self.OnClient_Core_Task_RETVAL_ERROR):
                    #     self.LogConsole(self.ThisServiceName() + " Error in Inner - Client_Core_Task () Break " + str(e),ConsoleLogLevel.System)
                    #     break
                    
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in Inner - OnClient_Core_Task()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR

    
    # NOT USED
    # def OnClient_Core_Task_Cycle(self):
        
        
    #     try:
            
    #         if (self.IsConnected):
                             
    #             if (self.IsQuitCalled):
    #                 return self.OnClient_Core_Task_RETVAL_QUIT
        
    #         return self.OnClient_Core_Task_RETVAL_OK
                      
    #     except Exception as e:
    #         self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
    #         return self.OnClient_Core_Task_RETVAL_ERROR
    
    
    def LocalCommandManagement(self, ListenedCommand,BestListenedCommandConfidence):
        try:
            
            CommandExecuted = False
            CommandRetVal = ""

            
            self.LogConsole(f"Got: {ListenedCommand} {BestListenedCommandConfidence} " ,ConsoleLogLevel.CurrentTest)
            
            
            
            return CommandExecuted, CommandRetVal
        
        except Exception as e:
            t = self.ThisServiceName() + "Error in Inner - OnClient_Core_Task()  " + str(e)
            self.LogConsole(t,ConsoleLogLevel.Error)
            return False, t
                
if (__name__== "__main__"):
    
    MySocketClient = SocketClient_VoiceCommands()
    
    MySocketClient.Run_Threads()