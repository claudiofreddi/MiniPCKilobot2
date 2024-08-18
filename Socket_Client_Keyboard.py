from Socket_Struct_Client_BaseClass import * 
from pynput import keyboard
from  datetime import datetime
import enum
from Socket_Struct_Server_StatusParamList import * 

class SocketClient_Keyboard(Socket_Client_BaseClass):
    
    #Key Management and optimization
    SPECIAL_KEYS_ON_PRESS =  {'a',          #left
                              'd',          #right
                              'e',          #stop
                              's',          #backward
                              'w',          #forward
                              'Ctrl+M',     #Show Message Sent From Server_LastKey_Pressed
                              'Ctrl+T',      #Topic List
                              'Ctrl+I',      #Image Enable/Disable
                              'Ctrl+L',      #Lidar Enable/Disable
                              'Ctrl+S'      #Params Status
                              }
    
    SPECIAL_KEYS_ON_RELEASE =  {'a','d','e','s','w'}
    SPECIAL_KEYS_CONTINUE_SENDING =  {'a','d','e','s','w'}
    
    _AllowEscape = False
    _StopOnReleaseEvent   = True
    _AllowAllKeys = False
    
    #Key Press management
    _presstime = 0
    _LastKey_Pressed = ""
    _Ctrl_Pressed = False
    _Alt_Pressed = False
    _MaxKeyCount = 3
    _KeyCount = 0
    def IsKeyAllowed(self,Key:str):
        return (self._AllowAllKeys or self.SPECIAL_KEYS_ON_PRESS.__contains__(Key) or self.SPECIAL_KEYS_ON_RELEASE.__contains__(Key))
        
    def IsKeyToNotify(self,Key:str,OnRelease:False):
        if not OnRelease:
            return self.SPECIAL_KEYS_ON_PRESS.__contains__(Key)
        else:
            return self.SPECIAL_KEYS_ON_RELEASE.__contains__(Key)  and not self._StopOnReleaseEvent
        
    def IsContinueSending(self,Key:str):
        return (self.SPECIAL_KEYS_CONTINUE_SENDING.__contains__(Key))
    
       
    def __init__(self, ServiceName = Socket_Services_List.KEYBOARD, ForceServerIP = '',ForcePort='',LogOptimized = False):
        super().__init__(ServiceName,ForceServerIP,ForcePort,LogOptimized)
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
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in IsCtrl_Char()  " + str(e),ConsoleLogLevel.Error)
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
            
            KeyString = ""

            if not self._Ctrl_Pressed and (key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or key == keyboard.Key.ctrl):
                self._Ctrl_Pressed = True
            
            if not self._Alt_Pressed and (key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r or key == keyboard.Key.alt_gr):
                self._Alt_Pressed = True
            
            
            if (self._Ctrl_Pressed and not (key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or key == keyboard.Key.ctrl)):
                KeyString = self.GetCtrl_Char(key,"Ctrl")
            elif (self._Alt_Pressed and not (key == keyboard.Key.alt_l or key == keyboard.Key.alt_r or key == keyboard.Key.alt_gr)):
                KeyString = self.GetCtrl_Char(key,"Alt")
            else:
                KeyString = self.GetCtrl_Char(key,"")
                

                ###filtrare Key "key..." "\x0"
                    
            if (self.IsKeyAllowed(KeyString)
                and self.IsKeyToNotify(KeyString,OnRelease=False)
                and (self._LastKey_Pressed !=  KeyString or self.IsContinueSending(KeyString))):
   
                self._LastKey_Pressed = KeyString
                
                if (KeyString != ""):     
                    self.LogConsole(KeyString,ConsoleLogLevel.System)
                                         
                    self._presstime = datetime.now()
                    #self.LogConsole('alphanumeric key {0} pressed'.format(key),,ConsoleLogLevel.Test)
                    ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.INPUT_KEYBOARD,
                                                                    Message = self._LastKey_Pressed,Value=0)
        
          

                    self.LogConsole(f"Send Key {self._LastKey_Pressed}",ConsoleLogLevel.Test)
                    self.SendToServer(ObjToSend) 
                
                    
                   
        except AttributeError:
            self.LogConsole('special key {0} pressed'.format(key),ConsoleLogLevel.System)

    def on_release(self,key):
        
        if (key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or key == keyboard.Key.ctrl):
            self._Ctrl_Pressed = False 
            
        if (key == keyboard.Key.alt_l or key == keyboard.Key.alt_r or key == keyboard.Key.alt_gr):
            self._Alt_Pressed = False

        KeyString = self.GetCtrl_Char(key,"")
        
        if (    self.IsKeyAllowed(KeyString)
            and self.IsKeyToNotify(KeyString,OnRelease=True)
            and self._LastKey_Pressed != ""):

  
            time_pressed = int((datetime.now() - self._presstime).total_seconds() * 1000)
            self.LogConsole(str(key) + " " + str(time_pressed) + " ms ",ConsoleLogLevel.Test)
            
            ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.INPUT_KEYBOARD,
                                                                                Message = self._LastKey_Pressed,Value=time_pressed)
                    
            self.SendToServer(ObjToSend) 
            
        self._LastKey_Pressed = ""
            
        if (self._AllowEscape and key == keyboard.Key.esc) or self.IsQuitCalled:
            # Stop listener
            return False    
        
if (__name__== "__main__"):
    
    MySocketClient_Keyboard = SocketClient_Keyboard()
    
    MySocketClient_Keyboard.Run_Threads()