from Socket_Client_BaseClass import * 
from pynput import keyboard
import datetime

class SocketClient_Keyboard(Socket_Client_BaseClass):
    
    ACCEPTED_CHARS = "adesw"
        
    _AllowEscape = True
    _StopOnReleaseEvent   = True
    _presstime = 0
    _LastCmd = ""
    IsValidChar = False
    
   
    def __init__(self, ServiceName = Socket_Services_List.KEYBOARD, ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort)
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()
        self.LogConsole("Keyboard Listener Started",ConsoleLogLevel.System)
        
    def On_ClientAfterLogin(self):
        
        self.RegisterTopics(Socket_Default_Message_Topics.INPUT_KEYBOARD)
        
    
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreayManaged=False):
        #ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
        
        pass
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 

    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
            if (self.IsQuitCalled):
                self.listener.stop()
                return self.OnClient_Core_Task_RETVAL_QUIT
            
            return self.OnClient_Core_Task_RETVAL_OK
            
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
    def on_press(self,key):
        try:
            self.IsValidChar = True if ((self.ACCEPTED_CHARS.find(str(key)[1])>=0) and len(str(key)) == 3) or self.ACCEPTED_CHARS == "" else False
            if (self.IsValidChar):
                if (self._LastCmd !=  str(key)):
                    self._LastCmd = str(key)
                    self.LogConsole(str(key),ConsoleLogLevel.System)
                    self._presstime = datetime.datetime.now()
                    #self.LogConsole('alphanumeric key {0} pressed'.format(key),,ConsoleLogLevel.Test)
                    ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.INPUT, 
                                                                    SubClassType = Socket_Default_Message_SubClassType.KEYBOARD, 
                                                                    Topic = Socket_Default_Message_Topics.INPUT_KEYBOARD,
                                                                    Message = self._LastCmd,Value=0)
        
                    self.SendToServer(ObjToSend)
                    #self.SendToServer(ObjToSend,SocketMessageEnvelopeTargetType.BROADCAST) 

                    
                    ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.MESSAGE, 
                                                                                SubClassType = Socket_Default_Message_SubClassType.MESSAGE,
                                                                                Topic = Socket_Default_Message_Topics.OUTPUT_SPEAKER, 
                                                                                Message = str(key), Value = 0)                


                    self.SendToServer(ObjToSend) 
                
                    
                   
        except AttributeError:
            self.LogConsole('special key {0} pressed'.format(key),ConsoleLogLevel.System)

    def on_release(self,key):
        
        if (self.IsValidChar and self._LastCmd != ""):
            #self.LogConsole('{0} released'.format(key))
                         
            time_pressed = int((datetime.datetime.now() - self._presstime).total_seconds() * 1000)
            self.LogConsole(str(key) + " " + str(time_pressed) + " ms ",ConsoleLogLevel.System)
            
            ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.INPUT, 
                                                                                SubClassType = Socket_Default_Message_SubClassType.KEYBOARD,
                                                                                Topic = Socket_Default_Message_Topics.INPUT_KEYBOARD,
                                                                                Message = self._LastCmd,Value=time_pressed)
                    
            self.SendToServer(ObjToSend) 
            
        self._LastCmd = ""
            
        if (self._AllowEscape and key == keyboard.Key.esc) or self.IsQuitCalled:
            # Stop listener
            return False    
        
if (__name__== "__main__"):
    
    MySocketClient_Keyboard = SocketClient_Keyboard()
    
    MySocketClient_Keyboard.Run_Threads()