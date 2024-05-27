import cv2
import numpy as np
from Robot_Envs import *

class RobotVision_Object_Tracker():
    
    
    TrackerMode = (['KFC','GOTURN'])[0]
    TrackStarted = False
    
    def __init__(self):
        if (self.TrackerMode ==  'KFC'):
            self.tracker = cv2.TrackerKCF.create()
        
        if (self.TrackerMode ==  'GOTURN'):
            # For GOTURN:
            #     goturn.prototxt and goturn.caffemodel: https://github.com/opencv/opencv_extra/tree/c4219d5eb3105ed8e634278fad312a1a8d2c182d/testdata/tracking
            self.tracker = cv2.TrackerGOTURN.create()
            
        self.TrackStarted = False
        pass
            
    
    def SetFirstTrackerFrame(self,frame, roi):
        ret = self.tracker.init(frame, roi)
        self.TrackStarted = True
        return ret
    
    def _Map_roi(self,roi): 
        x,y,w,h = tuple(map(int,roi))
        return x,y,w,h
        
    def AskROI(self, frame):
        roi = cv2.selectROI(frame, False)
        return roi
    
    def UpdateTrackerFrame(self, frame, bDrawRect = True):
        roi = [0,0,0,0]
        success = False
        
        if (self.TrackStarted):
            # Update tracker
            success, roi = self.tracker.update(frame)
            if (success):        
                # roi variable is a tuple of 4 floats
                # We need each value and we need them as integers
                (x,y,w,h) = tuple(map(int,roi))
                if (bDrawRect):                              
                    # Tracking success
                    p1 = (x, y)
                    p2 = (x+w, y+h)
                    cv2.rectangle(frame, p1, p2, (255,0,0), 3)   #Blue                            
            else:
                if (bDrawRect): 
                    # Tracking failure
                    cv2.putText(frame, "Failure to Detect Tracking!!", (100,200), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),3)
                    self.TrackStarted = False
                    
        return success, roi
    
if (__name__== "__main__"):
        
    _GetFromCam = False
    
    MyRobotVision_Object_Tracker = RobotVision_Object_Tracker()
    AskROI = True
      
    # Read video
    if (_GetFromCam):
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(PATH_TEST_VIDEO)

    # Read first frame.
    ret, frame = cap.read()
    
    if (AskROI):
        # Special function allows us to draw on the very first frame our desired ROI
        roi = cv2.selectROI(frame, False)
        print(roi)
    else:
        roi = [200,300,100,100]
    
    if (ret):
        ret = MyRobotVision_Object_Tracker.SetFirstTrackerFrame(frame, roi)
       
    isErrorWritten = False
    while True:
        # Read a new frame
        ret, frame = cap.read()
        
        if (ret):
            success, roi = MyRobotVision_Object_Tracker.UpdateTrackerFrame(frame)
            
            if (not success and not isErrorWritten):
                isErrorWritten = True
                print("Error")
            
            # Display result
            cv2.imshow("Output",frame)
            cv2.setWindowProperty("Output", cv2.WND_PROP_TOPMOST, 1)
            cv2.waitKey(1)

            # Exit if ESC pressed
            k = cv2.waitKey(1) & 0xff
            if k == 27 : 
                break
        
        else:
            break
        
    cap.release()
    cv2.destroyAllWindows()