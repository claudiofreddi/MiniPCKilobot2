from Socket_Client_BaseClass import * 
from pynput import keyboard
import datetime

class SocketClient_Remote(Socket_Client_BaseClass):

       
    def __init__(self, ServiceName = Socket_Services_List.REMOTE, ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort)

        
    def OnClient_Connect(self):
        self.NumOfCycles = 0
        self.LogConsole("OnClient_Connect")
    
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,IsMessageAlreayManaged=False):
        
        try:
            if (IsMessageAlreayManaged == False):
                if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
               
                    ReceivedMessage =  Socket_Default_Message(**SocketDecoder.get(ReceivedEnvelope.EncodedJson))
                    #ReceivedMessage = SuperDecoder.GetReceivedMessage(ReceivedEnvelope)
                                             
                            
                            
        except Exception as e:
            self.LogConsole(self.LogPrefix() + "Error in OnClient_Receive()  " + str(e))
            return self.OnClient_Core_Task_RETVAL_ERROR
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect")
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit") 

    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
            
            
            time.sleep(3)
                        
            self.NumOfCycles = self.NumOfCycles + 1
            
            ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.MESSAGE, 
                                                                    SubClassType = Socket_Default_Message_SubClassType.MESSAGE, 
                                                                    Message = "Test", Value = self.NumOfCycles)                
                
            
            self.SendToServer(ObjToSend) 
            
            
            
            
            
            if (self.IsQuitCalled):
                return self.OnClient_Core_Task_RETVAL_QUIT
        
            return self.OnClient_Core_Task_RETVAL_OK
            
            
        except Exception as e:
            self.LogConsole(self.LogPrefix() + "Error in OnClient_Core_Task_Cycle()  " + str(e))
            return self.OnClient_Core_Task_RETVAL_ERROR
    
     
        
if (__name__== "__main__"):
    
    MySocketClient = SocketClient_Remote()
    
    MySocketClient.Run_Threads()