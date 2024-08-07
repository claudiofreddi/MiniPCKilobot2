from Socket_Client_JSON import * 
from pynput import keyboard
import datetime

class Input_SubClass_Types:
    KEYBOARD = "KEYBOARD"

class SocketClient_Keyboard(Robot_Socket_Client_Service):
    
    ACCEPTED_CHARS = "adesw"
        
    _AllowEscape = True
    _StopOnReleaseEvent   = True
    _presstime = 0
    _LastCmd = ""
    IsValidChar = False
    
   
    def __init__(self, ServiceName = Socket_Services_Types.KEYBOARD, ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort)
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        listener.start()
        print("Listener Started")
        
    def OnClient_Connect(self):
        self.NumOfCycles = 0
        print("OnClient_Connect")
    
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,IsMessageAlreayManaged=False):
        #obj:SocketMessage_Type_STANDARD = ReceivedEnvelope.GetDecodedMessageObject()
        #print("OnClient_Receive: " + obj.Message + " [" + self.ServiceName + "]")
        pass
        
    def OnClient_Disconnect(self):
        print("OnClient_Disconnect")
    
    def OnClient_Quit(self):
        print("OnClient_Quit") 

    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
   
            return self.OnClient_Core_Task_RETVAL_OK
            #self.OnClient_Core_Task_RETVAL_QUIT
            
        except Exception as e:
            self.TraceLog(self.LogPrefix() + "Error in OnClient_Core_Task_Cycle()  " + str(e))
            return self.OnClient_Core_Task_RETVAL_ERROR
    
    def on_press(self,key):
        try:
            self.IsValidChar = True if ((self.ACCEPTED_CHARS.find(str(key)[1])>=0) and len(str(key)) == 3) or self.ACCEPTED_CHARS == "" else False
            if (self.IsValidChar):
                if (self._LastCmd !=  str(key)):
                    self._LastCmd = str(key)
                    print(str(key))
                    self._presstime = datetime.datetime.now()
                    #print('alphanumeric key {0} pressed'.format(key))
                    ObjToSend:SocketMessage_Type_STANDARD = SocketMessage_Type_STANDARD(ClassType=SocketMessage_Type_STANDARD_Type.INPUT, 
                                                                    SubClassType = Input_SubClass_Types.KEYBOARD, 
                                                                    Message = self._LastCmd,Value=0)
        
                    self.SendToServer(ObjToSend,SocketMessageEnvelopeTargetType.BROADCAST) 
                
                    
                   
        except AttributeError:
            print('special key {0} pressed'.format(key))

    def on_release(self,key):
        
        if (self.IsValidChar and self._LastCmd != ""):
            #print('{0} released'.format(key))
                         
            time_pressed = int((datetime.datetime.now() - self._presstime).total_seconds() * 1000)
            print(str(key) + " " + str(time_pressed) + " ms ")
            
            ObjToSend:SocketMessage_Type_STANDARD = SocketMessage_Type_STANDARD(ClassType=SocketMessage_Type_STANDARD_Type.INPUT, 
                                                                                SubClassType = Input_SubClass_Types.KEYBOARD,
                                                                                Message = self._LastCmd,Value=time_pressed)
                    
            self.SendToServer(ObjToSend) 
            
        self._LastCmd = ""
            
        if (self._AllowEscape and key == keyboard.Key.esc) or self.IsQuitCalled:
            # Stop listener
            return False    
        
if (__name__== "__main__"):
    
    MySocketClient_Keyboard = SocketClient_Keyboard(Socket_Services_Types.KEYBOARD)
    
    MySocketClient_Keyboard.Run_Threads()