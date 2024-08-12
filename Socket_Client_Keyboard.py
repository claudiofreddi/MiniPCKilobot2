from Socket_Client_BaseClass import * 
from pynput import keyboard
from  datetime import datetime
import enum

class SocketClient_Keyboard(Socket_Client_BaseClass):
    
    ACCEPTED_CHARS = "adesw"
        
    _AllowEscape = False
    _StopOnReleaseEvent   = True
    _presstime = 0
    _LastCmd = ""
    IsValidChar = False
    SendAllChars = True
    Ctrl_Pressed = False
    Alt_Pressed = False
    
       
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
    
        
    def IsCtrl_Char(self, key, letter):
        try:
            if type(key) != enum:
                return ((ord(letter.upper())-64) == ord(key.char))
            else:
                False
        except:
            print("error")
            return False
        
    def GetCtrl_Char(self, key, Prefix):
        try:
            if type(key) != enum:
                if (Prefix !=""):
                    if (Prefix == "Ctrl"):
                        return Prefix + "+" + chr(ord(key.char)+64)
                    if (Prefix == "Alt"):
                        return Prefix + "+" + chr(ord(key.char)-32)
                else:
                    return str(key).replace("'","")
            else:
                return str(key).replace("'","")
        except:
            return ""

    def on_press(self,key):
        
        
        try:
            self.IsValidChar = True if ((self.ACCEPTED_CHARS.find(str(key)[1])>=0) and len(str(key)) == 3) or self.ACCEPTED_CHARS == "" else False
            if (self.IsValidChar or self.SendAllChars):
                
                KeyString = ""

                if not self.Ctrl_Pressed and (key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or key == keyboard.Key.ctrl):
                    self.Ctrl_Pressed = True
                    #return
                
                if not self.Alt_Pressed and (key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r or key == keyboard.Key.alt_gr):
                    self.Alt_Pressed = True
                    #return               
                
                if (self.Ctrl_Pressed and not (key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or key == keyboard.Key.ctrl)):
                    KeyString = self.GetCtrl_Char(key,"Ctrl")
                    #self.Ctrl_Pressed = False
                elif (self.Alt_Pressed and not (key == keyboard.Key.alt_l or key == keyboard.Key.alt_r or key == keyboard.Key.alt_gr)):
                    KeyString = self.GetCtrl_Char(key,"Alt")
                    #self.Alt_Pressed = False
                else:
                    KeyString = self.GetCtrl_Char(key,"")

                    ###filtrare Key "key..." "\x0"
                    


                
                
                if (self._LastCmd !=  KeyString):
                    self._LastCmd = KeyString
                
                    if (KeyString != ""):     
                        self.LogConsole(KeyString,ConsoleLogLevel.System)
                        self._presstime = datetime.now()
                        #self.LogConsole('alphanumeric key {0} pressed'.format(key),,ConsoleLogLevel.Test)
                        ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.INPUT, 
                                                                        SubClassType = Socket_Default_Message_SubClassType.KEYBOARD, 
                                                                        Topic = Socket_Default_Message_Topics.INPUT_KEYBOARD,
                                                                        Message = self._LastCmd,Value=0)
            
                        # self.SendToServer(ObjToSend)
                        # #self.SendToServer(ObjToSend,SocketMessageEnvelopeTargetType.BROADCAST) 

                        
                        # ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.MESSAGE, 
                        #                                                             SubClassType = Socket_Default_Message_SubClassType.MESSAGE,
                        #                                                             Topic = Socket_Default_Message_Topics.OUTPUT_SPEAKER, 
                        #                                                             Message = KeyString, Value = 0)                


                        self.SendToServer(ObjToSend) 
                
                    
                   
        except AttributeError:
            self.LogConsole('special key {0} pressed'.format(key),ConsoleLogLevel.System)

    def on_release(self,key):
        
        
        if ((self.IsValidChar or  self.SendAllChars) and self._LastCmd != ""):
            
           
            self.Alt_Pressed = False
            self.Ctrl_Pressed = False
            
            #self.LogConsole('{0} released'.format(key))
                         
            time_pressed = int((datetime.now() - self._presstime).total_seconds() * 1000)
            print(str(time_pressed) + " ms")
            self.LogConsole(str(key) + " " + str(time_pressed) + " ms ",ConsoleLogLevel.Test)
            
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