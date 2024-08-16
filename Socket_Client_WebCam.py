from Socket_Client_BaseClass import * 
from Socket_Utils_Timer import * 
import numpy as np
import imutils
import cv2 as cv
from Robot_Vision_Object_Classifer import *

class SocketClient_Webcam(Socket_Client_BaseClass):

          

    
    def __init__(self, ServiceName = Socket_Services_List.WEBCAM, ForceServerIP = '',ForcePort='',LogOptimized = False):
        super().__init__(ServiceName,ForceServerIP,ForcePort,LogOptimized)
        self.CvIsOpen = False
        self.IMAGE_CHANGE_SENSITIVITY_GR_THAN = 0
        self.FRAME_PER_SECOND = 35
        self.USE_GRAY = 0
        self.SHOW_FRAME = False
        self.img_counter = 0
        self.IsFirstImage = True
        self.CvIsOpen = False
        self.ContinuousSending_On = True
        self._Classifier_Enabled = True
        self._Classifier_Loaded = False
    
        
    def Classifier_Load(self):
        if (not self._Classifier_Loaded):
            self.LogConsole("Loaing Classifier... please wait",ConsoleLogLevel.System)
            self.MyRobotVision_Obj_Classifier = RobotVision_Object_Classifier()
            self.MyRobotVision_Obj_Classifier.Load()
            self.MyRobotVision_Obj_Classifier.StartDNN()
            self._Classifier_Loaded = True
            
            
    def Classifier_Enable(self, Enabled = True):
        self._Classifier_Enabled = Enabled and self._Classifier_Loaded
        self.LogConsole(f"Classifier { 'Enabled' if self._Classifier_Enabled else ' Disabled' }",ConsoleLogLevel.System)
        
    def Classifier_Apply(self, frame,ConfidenceLev=0.60):
        success,FoundNames,FoundConfidence,FoundBoxes = self.MyRobotVision_Obj_Classifier.TrackObjects(frame=frame,AddBoxes=True,ConfidenceLev=ConfidenceLev)
        self.LogConsole(str(FoundNames),ConsoleLogLevel.Test)
        return success,FoundNames,FoundConfidence,FoundBoxes
        
        
                    
    def OnClient_Connect(self):
        self.IsFirstImage  = True #Set for reload image also in case of no detection
        #self.LogConsole("OnClient_Connect",ConsoleLogLevel.Override_Call)


    def On_ClientAfterLogin(self):
        self.RegisterTopics(Socket_Default_Message_Topics.INPUT_IMAGE)
        self.Classifier_Load()
        self.Classifier_Enable(True)
        

                
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
           
            if (not self.CvIsOpen):
                self.LogConsole("Opening Webcam... please wait",ConsoleLogLevel.System)
                #self.cap = cv.VideoCapture(0,cv.CAP_DSHOW)
                self.cap = cv.VideoCapture(0,cv.CAP_MSMF)
                self.LogConsole("Webcam Opened",ConsoleLogLevel.System)
                self.cap.set(cv.CAP_PROP_FPS,self.FRAME_PER_SECOND)  

                #encode to jpeg format
                #encode param image quality 0 to 100. default:95
                #if you want to shrink data size, choose low image quality.
                self.encode_param=[int(cv.IMWRITE_JPEG_QUALITY),90]
                self.IsFirstCall = True
                self.CvIsOpen = True
                
                
            if (self.IsConnected):     
                if (self.CvIsOpen):
                
                    if not self.cap.isOpened():
                        print("Cannot open camera")
            
                    else:      

                        # Capture frame-by-frame
                        #print("read")
                        ret, frame = self.cap.read()

                        
                        # if frame is read correctly ret is True
                        if not ret:
                            print("Can't receive frame (stream end?). Exiting ...")
                        else:
                            
                            
                                
                            self.SleepTime(Multiply=1,CalledBy="OnClient_Core_Task_Cycle",Trace=False)
                            frame = imutils.resize(frame, width=320)

                            frame = cv.flip(frame,180)
                            
                                
                            diff_percent = -1
                            
                            try:
                                
                                if (self.IMAGE_CHANGE_SENSITIVITY_GR_THAN == 0): #non comparo
                                    time.sleep(0.3)
                                
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
                            
                            if (self._Classifier_Enabled):
                                #self.LogConsole("Classifier_Apply",ConsoleLogLevel.Test)
                                success,FoundNames,FoundConfidence,FoundBoxes = self.Classifier_Apply(frame)
                                #self.LogConsole(f"Classifier_Apply retval:{success}" ,ConsoleLogLevel.Test)
                            
                            if (    diff_percent == -1 
                                    or diff_percent > self.IMAGE_CHANGE_SENSITIVITY_GR_THAN 
                                    or self.IsFirstImage):
                                
                                self.IsFirstImage = False
                                
                                self.LogConsole(self.ThisServiceName() + "Image Score: " + str(diff_percent) + "%",ConsoleLogLevel.Test)  
                                result, image = cv.imencode('.jpg', frame, self.encode_param)
                                AdditionaByteData = pickle.dumps(image, 0) 
                                
                                #AdditionaByteData = b''
                                                    
                                #send
                            
                                ObjToSend:Socket_Default_Message = Socket_Default_Message(Topic=Socket_Default_Message_Topics.INPUT_IMAGE,
                                                                                        Message = "Test", 
                                                                                        Value = diff_percent,
                                                                                        ResultList=FoundNames)                


                                self.SendToServer(MyMsg=ObjToSend,AdditionaByteData=AdditionaByteData) 
                            
                            
                                                            
                            if (self.SHOW_FRAME):
                                # Display the resulting frame
                                try:
                                    cv.imshow('frame', frame)
                                    cv2.setWindowProperty('server', cv2.WND_PROP_TOPMOST, 1)
                                except:
                                    cv2.destroyAllWindows()
                        
                                                
                        cv.waitKey(1)

                            
                        
            
            
            
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