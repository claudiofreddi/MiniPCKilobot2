from Socket_Struct_Client_BaseClass import * 
from Socket_Utils_Timer import * 
from Socket_Logic_Joystick import *  #https://github.com/r4dian/Xbox-Controller-for-Python


class SocketClient_Joystick_Commands:
    FW = "fw"
    BW = "bw"
    LEFT = "left"
    RIGHT = "right"
    BUTTON_6 = "button_6"
    
class SocketClient_Joystick(Socket_Client_BaseClass):

    
   
    def __init__(self, ServiceName = Socket_Services_List.JOYSTICK, ForceServerIP = '',ForcePort='',LogOptimized = False):
        super().__init__(ServiceName,ForceServerIP,ForcePort,LogOptimized)
        ##Joy Object
        self.REFRESH_SECONDS = 0.5
        self.joysticks = XInputJoystick.enumerate_devices()
        self.MyTimer = Socket_Timer()
        self.MyTimer.start(TimeoutSecond=self.REFRESH_SECONDS)
        
    def OnClient_Connect(self):
        
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
    
    def On_ClientAfterLogin(self):
        self.RegisterTopics(Socket_Default_Message_Topics.INPUT_JOYSTICK)
        
        
        self.joysticks = XInputJoystick.enumerate_devices()
        device_numbers = list(map(attrgetter('device_number'), self.joysticks))

        print('found %d devices: %s' % (len(self.joysticks), device_numbers))

        if not self.joysticks:
            self.IsQuitCalled = True
            return

        pass
        
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreadyManaged=False):

        # if (self.IsConnected):
        #     if (not IsMessageAlreadyManaged):
        #         if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
        #             ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
        #             if (ReceivedMessage.Topic == Socket_Default_Message_Topics.TOPIC_CLIENT_DIRECT_CMD):
        #                 MySpecificCommand = ReceivedMessage.Message

        
        try:
            if (IsMessageAlreadyManaged == False):
                if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                    ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                            
                            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 

    def OnClient_Core_Task_Cycle(self):
        try:
            
            if (self.IsConnected):
                #Sample To remove
                time.sleep(2)
                # ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.MESSAGE, 
                #                                                         Message = "Test", Value = 0)                
                    
                
                # self.SendToServer(ObjToSend) 
                # self.LogConsole(self.ThisServiceName() + " " + ObjToSend.GetMessageDescription(),ConsoleLogLevel.Always)
            
                        
                if (self.IsQuitCalled):
                    return self.OnClient_Core_Task_RETVAL_QUIT
            
            return self.OnClient_Core_Task_RETVAL_OK
          
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
    def MainJoystick_Thread(self):
        """
        Grab 1st available gamepad, logging changes to the screen.
        L & R analogue triggers set the vibration motor speed.
        """
        print("Waiting for conttroller")
        while not self.joysticks:
            self.joysticks = XInputJoystick.enumerate_devices()
            device_numbers = list(map(attrgetter('device_number'), self.joysticks))

            print('found %d devices: %s' % (len(self.joysticks), device_numbers))
            time.sleep(3)

        # if not self.joysticks:
        #     sys.exit(0)7

        j = self.joysticks[0]
        print('using %d' % j.device_number)

        battery = j.get_battery_information()
        print(battery)

        @j.event
        def on_button(button, pressed):
            print('button', button, pressed)
            if (pressed == 1):
                Message = "button_" + str(button)
                if (Message != ""):              
                    if (self.MyTimer.IsTimeout()):
                        ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.INPUT_JOYSTICK, 
                                                                                Message = Message, Value = 0)                
                            
                        
                        self.SendToServer(ObjToSend) 
                        self.LogConsole(self.ThisServiceName() + " " + ObjToSend.GetMessageDescription(),ConsoleLogLevel.Test)
                        self.MyTimer.Reset()   
                        
        self.left_speed = 0
        self.right_speed = 0
        allData = False

        @j.event
        def on_axis(axis, value):
            self.left_speed = 0
            self.right_speed = 0
            Message = ""
            if (allData):
                print('axis', axis, value)
            else:
                
                if (axis=='l_thumb_y' and value>0.4):
                    Message = SocketClient_Joystick_Commands.FW
                
                if (axis=='l_thumb_y' and value<-0.4):
                    Message = SocketClient_Joystick_Commands.BW
                
                if (axis=='l_thumb_x' and value>0.4):
                    Message = SocketClient_Joystick_Commands.LEFT
                    
                if (axis=='l_thumb_x' and value<-0.4):
                    Message = SocketClient_Joystick_Commands.RIGHT
                

            
            if axis == "left_trigger":
                self.left_speed = value
            elif axis == "right_trigger":
                self.right_speed = value
            
            j.set_vibration(self.left_speed, self.right_speed)
            
            if (Message != ""):  
                print(Message)         
                if (self.MyTimer.IsTimeout()):
                    ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic = Socket_Default_Message_Topics.INPUT_JOYSTICK, 
                                                                            Message = Message, Value = 0)                
                        
                    
                    self.SendToServer(ObjToSend) 
                    self.LogConsole(self.ThisServiceName() + " " + ObjToSend.GetMessageDescription(),ConsoleLogLevel.Test)
                    self.MyTimer.Reset()     
            
            
            

        while True:
            j.dispatch_events()
            time.sleep(.01)
     
    def Run_Threads(self):
        super().Run_Threads()
        
        # Starting Threads For Listening And Writing
        receive_thread = threading.Thread(target=self.MainJoystick_Thread)
        receive_thread.start()
        
        
if (__name__== "__main__"):
    
    MySocketClient = SocketClient_Joystick()
    
    MySocketClient.Run_Threads()