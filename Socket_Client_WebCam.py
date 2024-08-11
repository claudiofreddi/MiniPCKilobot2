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
    IsFirstImage = True
    CvIsOpen = False
    
    def __init__(self, ServiceName = Socket_Services_List.WEBCAM, ForceServerIP = '',ForcePort=''):
        super().__init__(ServiceName,ForceServerIP,ForcePort)
        self.CvIsOpen = False
        
    def OnClient_Connect(self):
        self.IsFirstImage  = True #Set for reload image also in case of no detection
        #self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)
        #self.MyTimer.start(1,"WebCamTimer")

    def On_ClientAfterLogin(self):
        self.RegisterTopics(Socket_Default_Message_Topics.INPUT_IMAGE)
        

                
    def OnClient_Receive(self,ReceivedEnvelope:SocketMessageEnvelope,AdditionaByteData=b'',IsMessageAlreayManaged=False):
        #ReceivedMessage:Socket_Default_Message = ReceivedEnvelope.GetReceivedMessage()
        
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
           
            if (self.IsFirstImage and not self.CvIsOpen):
                self.LogConsole("Opening Webcam... please wait",ConsoleLogLevel.System)
                #self.cap = cv.VideoCapture(0,cv.CAP_DSHOW)
                self.cap = cv.VideoCapture(0,cv.CAP_MSMF)

                self.cap.set(cv.CAP_PROP_FPS,self.FRAME_PER_SECOND)  

                #encode to jpeg format
                #encode param image quality 0 to 100. default:95
                #if you want to shrink data size, choose low image quality.
                self.encode_param=[int(cv.IMWRITE_JPEG_QUALITY),90]
                self.IsFirstImage = True
                self.CvIsOpen = True
                
                
            if (self.IsConnected):     
                if (self.CvIsOpen):
                
                    if not self.cap.isOpened():
                        print("Cannot open camera")
            
                    else:      
                        #if (self.MyTimer.IsTimeout()): 
                        # Capture frame-by-frame
                        #print("read")
                        ret, frame = self.cap.read()

                        
                        # if frame is read correctly ret is True
                        if not ret:
                            print("Can't receive frame (stream end?). Exiting ...")
                        else:
                            
                            
                            time.sleep(0.4)
                            frame = imutils.resize(frame, width=320)

                            frame = cv.flip(frame,180)
                            
                            diff_percent = -1
                            
                            try:
                                
                                                                
                                ## compare
                                imgToCompareChg = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                                imgToCompareChg = cv.GaussianBlur(imgToCompareChg, (21, 21), 0)
                                
                                                                
                                if (self.IsFirstImage):
                                    self.LastFrameToCompareChg = imgToCompareChg
                                    #self.IsFirstImage = False
                                
                                diff_percent = self.calculate_difference_measure(self.LastFrameToCompareChg , imgToCompareChg) *100
                                diff_percent = int(diff_percent)                                
                                self.LastFrameToCompareChg = imgToCompareChg
                                                                                                
                                                                
                            except Exception as e:
                                self.LogConsole(self.ThisServiceName() + "Error in Comparing Images:  " + str(e),ConsoleLogLevel.Error)
                            
                            if (diff_percent == -1 or diff_percent > 30 or self.IsFirstImage):
                                self.IsFirstImage = False
                                
                                print("Image Score" + str(diff_percent))  
                                result, image = cv.imencode('.jpg', frame, self.encode_param)
                                AdditionaByteData = pickle.dumps(image, 0) 
                                
                                #AdditionaByteData = b''
                                                    
                                #send
                            
                                ObjToSend:Socket_Default_Message = Socket_Default_Message(ClassType=Socket_Default_Message_ClassType.INPUT, 
                                                                                        SubClassType = Socket_Default_Message_SubClassType.IMAGE, 
                                                                                        Topic=Socket_Default_Message_Topics.INPUT_IMAGE,
                                                                                        Message = "Test", 
                                                                                        Value = diff_percent)                


                                self.SendToServer(MyMsg=ObjToSend,AdditionaByteData=AdditionaByteData) 
                            
                            
                                                            
                            if (self.SHOW_FRAME):
                                # Display the resulting frame
                                cv.imshow('frame', frame)
                               
                        
                                                
                        cv.waitKey(1)
                        #self.MyTimer.Reset()
                            
                        
            
            
            
            if (self.IsQuitCalled):
                return self.OnClient_Core_Task_RETVAL_QUIT
        
            return self.OnClient_Core_Task_RETVAL_OK
            
            
        except Exception as e:
            self.LogConsole(self.ThisServiceName() + "Error in OnClient_Core_Task_Cycle()  " + str(e),ConsoleLogLevel.Error)
            return self.OnClient_Core_Task_RETVAL_ERROR
    
    
    def calculate_difference_measure(self,img1: np.array, img2: np.array) -> float:
        diff = cv.absdiff(img1, img2)
        thresh_diff = cv.threshold(diff, 15, 255, cv.THRESH_BINARY)[1]

        # Calculate the difference between the 2 images
        total_pixels = img1.shape[0] * img1.shape[1] * 1.0
        diff_on_pixels = cv.countNonZero(thresh_diff) * 1.0
        difference_measure = diff_on_pixels / total_pixels
        #print('difference_measure: {}'.format(difference_measure))
        return difference_measure
    
    def calculate_difference_measure2(self,img1: np.array, img2: np.array) -> float:

        #--- take the absolute difference of the images ---
        res = cv.absdiff(img1, img2)

        #--- convert the result to integer type ---
        res = res.astype(np.uint8)

        #--- find percentage difference based on the number of pixels that are not zero ---
        percentage = (np.count_nonzero(res) * 100)/ res.size
        
        return percentage
        
    def Run_Threads(self, SimulOn=False):
        super().Run_Threads(SimulOn)
        

    
        

                      
    
        
if (__name__== "__main__"):
    
    MySocketClient = SocketClient_Webcam()
    
    MySocketClient.Run_Threads()