import numpy as np
import cv2
import datetime
from ZOLD_Lib_Processes import *
from multiprocessing import Process, Manager


class RobotShowCam_Obj(ProcessSuperClass):
    
    VideoStatusOpened = False
    
    def __init__(self,processName):
        super().__init__(processName)

   
    def Run(self,SharedMem):
        super().Run_Pre(SharedMem)
        
       # self.OpenVideo()
        
       # return
        #while super().Run_CanContinueRunnig(): 
            # if (self.SharedMem.VideoOn and not self.VideoStatusOpened):
            #     self.VideoStatusOpened = True
            #     print("Camera On")
            #     self.OpenVideo()
            #     print("Camera Off")
            
            
    #def OpenVideo(self):
        
        #self.VideoStatusOpened = True
        
        # create display window
        cv2.namedWindow("webcam", cv2.WINDOW_NORMAL)
        

        # initialize webcam capture object
        self.cap = cv2.VideoCapture(0)

        # retrieve properties of the capture object
        cap_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        cap_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        cap_fps = self.cap.get(cv2.CAP_PROP_FPS) 
        fps_sleep = int(1000 / cap_fps)
        super().LogConsole('* Capture width:' + str(cap_width))
        super().LogConsole('* Capture height:' + str(cap_height))
        super().LogConsole('* Capture FPS: ' + str(cap_fps) + ' ideal wait time between frames: ' + str(fps_sleep) + ' ms')

        # initialize time and frame count variables
        self.last_time = datetime.datetime.now()
        self.frames = 0
        self.Continue = True
        
        # main loop: retrieves and displays a frame from the camera
        while (self.Continue):
            # blocks until the entire frame is read
            try:
                self.success, self.img = self.cap.read()
                self.frames += 1
            except Exception as inst:
                super().LogConsole('Error cap.read()') 
                continue
            
            # compute fps: current_time - last_time
            delta_time = datetime.datetime.now() - self.last_time
            elapsed_time = delta_time.total_seconds()
            cur_fps = np.around(self.frames / elapsed_time, 1)
            # draw FPS text and display image
            try:
                cv2.putText(self.img, 'FPS: ' + str(cur_fps), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.imshow("webcam", self.img)
            except Exception as inst:
                super().LogConsole('Error cv2.putText') 
                continue
            
            # wait 1ms for ESC to be pressed
            if (False):
                key = cv2.waitKey(1)
                if (key == 27):
                    super().Run_Kill() 
                    break
            
            self.Continue = super().Run_CanContinueRunnig() and self.SharedMem.VideoOn
        
        self.VideoStatusOpened = False
            
        # release resources
        try:
            cv2.destroyAllWindows()
            self.cap.release()
        except Exception as inst:
            super().LogConsole('Error cv2.destroyAllWindows()') 
            

def RobotShowCam_Run(SharedMem):
    MyRobotShowCam_Obj = RobotShowCam_Obj(ProcessList.Robot_ShowCam)
    MyRobotShowCam_Obj.Run(SharedMem)
   

if (__name__== "__main__"):
    
    MySharedObjs = SharedObjs() 
    
    RobotShowCam_Run(MySharedObjs)    