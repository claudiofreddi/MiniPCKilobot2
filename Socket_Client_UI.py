from Socket_Client_BaseClass import * 
import tkinter as tk
import threading

class LabelIndex:
    Compass = 0
    Battery = 1
    keyPressed = 2
    SpeakerStatus = 3
    ArduinoActionReady =4
    
class Socket_Client_UI(Socket_Client_BaseClass,threading.Thread):
    
    Label2Count = 0
    Label2L =  []
    Label2R = []
    IsWindowOn =False
    IsTimeout = False
    TimeoutVal = 10
    LastRead = datetime.now()
   
    def __init__(self, ServiceName = Socket_Services_List.USERINTERFACE, ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort)
        threading.Thread.__init__(self)
        self.CreateUI()
        
    def OnClient_Connect(self):
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)

    def On_ClientAfterLogin(self):
        #self.RegisterTopics(Socket_Default_Message_Topics.NONE)
        self.SubscribeTopics(Socket_Default_Message_Topics.INPUT_KEYBOARD,
                             Socket_Default_Message_Topics.SENSOR_BATTERY,
                             Socket_Default_Message_Topics.SENSOR_COMPASS                                                       
                             )
        pass
            
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreayManaged=False):
        #ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
        
        if (self.IsWindowOn == False):
            return
        try:
            
            if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                   
                    ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                    
                    self.LastRead = datetime.now()
                    self.IsTimeout = False
                    if (ReceivedMessage.ClassType == Socket_Default_Message_ClassType.SENSOR):
                        if (ReceivedMessage.SubClassType == Socket_Default_Message_SubClassType.COMPASS):
                            self.SetLabel_Pair(LabelIndex.Compass,str(ReceivedMessage.Value))
                        if (ReceivedMessage.SubClassType == Socket_Default_Message_SubClassType.BATTERY):
                            self.SetLabel_Pair(LabelIndex.Battery,str(ReceivedMessage.Value))
                    if (ReceivedMessage.ClassType == Socket_Default_Message_ClassType.INPUT):
                        if (ReceivedMessage.SubClassType == Socket_Default_Message_SubClassType.KEYBOARD and ReceivedMessage.Value == 0):
                            self.SetLabel_Pair(LabelIndex.keyPressed,str(ReceivedMessage.Message))
                    
         
            
       
                    
                    

            # self.root.update_idletasks()
            # self.root.update()
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 

    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
            
            if ((datetime.now() - self.LastRead).seconds > self.TimeoutVal):
                self.IsTimeout = True
                self.root.title('Kilobot TIMEOUT')
                    
                  
                #self.root.quit() 
            
            
            if (self.IsWindowOn and (self.IsTimeout == False)):
                self.root.title('Kilobot ' + str(datetime.now().time())[:8])
            
            if (self.IsQuitCalled):
                self.listener.stop()
                return self.OnClient_Core_Task_RETVAL_QUIT
            
            return self.OnClient_Core_Task_RETVAL_OK
            
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
  
    def AddLabel_Pair(self,container,index, Label, Value, Row, Sector): 
        j:int = (Sector*2)

        CurrL =  tk.Label(container, text=Label, padx=10, pady=5)
        CurrL.grid(row=Row, column=j,  sticky=tk.W, padx=5, pady=5)
        self.Label2L.insert(index, CurrL)
        CurrR =  tk.Label(container, text=Value, padx=10, pady=5)
        CurrR.grid(row=Row,column=(j+1),  sticky=tk.E, padx=5, pady=5)
        self.Label2R.insert(index, CurrR)
            
    def SetLabel_Pair(self, index,Value):
        self.Label2R[index].config(text=Value)     
   
  
    def CreateUI(self):
        try:
            self.root = tk.Tk()
            self.root.geometry("500x600")
            #self.root.resizable(0, 0)
            self.root.title('Kilobot')
            
             # Create a frame container
            self.container = tk.Frame(self.root, padx=20, pady=10)
            self.container.grid()
            
            
            CURR_ROW = 0
            self.AddLabel_Pair(self.container,LabelIndex.Compass,"Compass:","",CURR_ROW,0)
            self.AddLabel_Pair(self.container,LabelIndex.keyPressed,"keyPressed:","",CURR_ROW,1)
            
            CURR_ROW = CURR_ROW + 1
            self.AddLabel_Pair(self.container,LabelIndex.Battery,"Battery:","",CURR_ROW,0)
            self.AddLabel_Pair(self.container,LabelIndex.SpeakerStatus,"Speaker:","",CURR_ROW,1)
            
            CURR_ROW = CURR_ROW + 1
            self.AddLabel_Pair(self.container,LabelIndex.ArduinoActionReady,"Arduino Action Ready:","",CURR_ROW,0)
        
        except Exception as error:
            self.LogConsole("Error in CreateUI" + str(error),ConsoleLogLevel.Error)     

    def OpenWindow(self):
        self.IsWindowOn = True
        self.root.mainloop()
        
        
    def Run_Threads(self, SimulOn=False):
        super().Run_Threads(SimulOn)
        
        return 
  
  
  
  
if (__name__== "__main__"):
    
    MySocket_Client_UI = Socket_Client_UI()
    
    MySocket_Client_UI.Run_Threads()