from Socket_Client_BaseClass import * 
from Socket_Timer import * 
import numpy as np
import imutils
import cv2 as cv

class SocketClient_Webcam(Socket_Client_BaseClass):

    MyTimer:Timer=Timer()
    FRAME_PER_SECOND = 10
    USE_GRAY = 0
    SHOW_FRAME = False
    img_counter = 0
    
    
    def __init__(self, ServiceName = Socket_Services_List.WEBCAM, ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort)

        #self.cap = cv.VideoCapture(0,cv.CAP_DSHOW)
        self.cap = cv.VideoCapture(0,cv.CAP_MSMF)
        self.cap.set(cv.CAP_PROP_FPS,self.FRAME_PER_SECOND)  
        
        #encode to jpeg format
        #encode param image quality 0 to 100. default:95
        #if you want to shrink data size, choose low image quality.
        self.encode_param=[int(cv.IMWRITE_JPEG_QUALITY),90]
                
        
    def OnClient_Connect(self):
        
        self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
        self.MyTimer.start(1,"WebCamTimer")

        
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,IsMessageAlreayManaged=False):
        
        try:
            if (IsMessageAlreayManaged == False):
                if (ReceivedEnvelope.ContentType == SocketMessageEnvelopeContentType.STANDARD):
                    ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
                            
                            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Receive()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
        
    def OnClient_Disconnect(self):
        self.LogConsole("OnClient_Disconnect",ConsoleLogLevel.Override_Call)
    
    def OnClient_Quit(self):
        self.LogConsole("OnClient_Quit",ConsoleLogLevel.Override_Call) 

    def OnClient_Core_Task_Cycle(self, QuitCalled):
        try:
            
            
            if (self.IsConnected):
            
                if not self.cap.isOpened():
                    print("Cannot open camera")
          
                else:      
                    if (self.MyTimer.IsTimeout()): 
                        # Capture frame-by-frame
                        #print("read")
                        ret, frame = self.cap.read()
                    
                        # if frame is read correctly ret is True
                        if not ret:
                            print("Can't receive frame (stream end?). Exiting ...")
                        else:
                            frame = imutils.resize(frame, width=320)

                            frame = cv.flip(frame,180)
                            result, image = cv.imencode('.jpg', frame, self.encode_param)
                            AdditionaByteData = pickle.dumps(image, 0) 
                            
                            #AdditionaByteData = b''
                                                
                            #send
                        
                            ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.INPUT, 
                                                                                    SubClassType = Socket_Default_Message_SubClassType.IMAGE, 
                                                                                    Topic=Socket_Default_Message_Topics.INPUT_IMAGE,
                                                                                    Message = "Test", 
                                                                                    Value = self.img_counter)                


                            self.SendToServer(ObjToSend,AdditionaByteData=AdditionaByteData) 
                        
                        
                            self.img_counter = self.img_counter + 1
                            
                            if (self.SHOW_FRAME):
                                # Display the resulting frame
                                cv.imshow('frame', frame)
                        
                                                
                        cv.waitKey(1)
                        self.MyTimer.Reset()
                        
                        
            
            
            
            if (self.IsQuitCalled):
                return self.OnClient_Core_Task_RETVAL_QUIT
        
            return self.OnClient_Core_Task_RETVAL_OK
            
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
    def Run_Threads(self, SimulOn=False):
        super().Run_Threads(SimulOn)
        

    
        

                      
    
        
if (__name__== "__main__"):
    
    MySocketClient = SocketClient_Webcam()
    
    MySocketClient.Run_Threads()