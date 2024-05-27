#https://github.com/ankityddv/ObjectDetector-OpenCV

#python -m pip install --upgrade pip setuptools
#python -m pip install dlib-19.24.1-cp311-cp311-win_amd64.whl
#python -m pip install matplotlib
#python -m pip install Cmake
#python -m pip install face_recognition


from datetime import datetime
import cv2
import matplotlib.pyplot as plt
from Lib_Processes import * 

# Variabili
import numpy as np

from Robot_Shared_Objects import *
from Robot_SharedParamsMonitor import RobotSharedParamsMonitor_Run
from Robot_Simulate_Processes  import Robot_Simulate_Process_Obj_Run, Sparring_Process_Names

from Robot_Vision_Face_Classifier import RobotVision_Face_Classifier
from Robot_Vision_Object_Classifer import RobotVision_Object_Classifier
from Robot_Vision_Object_Tracker import RobotVision_Object_Tracker


class RobotVision_Obj(ProcessSuperClass):
        
    
    Enable_Obj_Tracking = True
    LookForSpecificObjs = []
    LookForSpecificObjsConf = 70.0

    Enable_Obj_Recog = True
    MyRobotVision_Obj_Classifier = RobotVision_Object_Classifier()

    Enable_Face_Recog = False
    MyRobotVision_Face_Classifier = RobotVision_Face_Classifier()
    NameOfFaceFound = ""
    
    MyRobotVision_Object_Tracker = RobotVision_Object_Tracker()
    
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720
   
    KeepWindowOnTop = True
    
    
    def __init__(self,processName,DefaultMode = "",_Enable_Face_Recog=False):
        super().__init__(processName)
        self._DefaultMode = DefaultMode
        self.Enable_Face_Recog = _Enable_Face_Recog
        if (self.Enable_Obj_Tracking):
            self.tracker = cv2.TrackerKCF.create() 

       
    
    def Run(self,SharedMem):
        super().Run_Pre(SharedMem)
        
        #Load Faces
        self.MyRobotVision_Face_Classifier.Load()
        
        #Load Obj Database        
        self.MyRobotVision_Obj_Classifier.Load()
        self.MyRobotVision_Obj_Classifier.StartDNN()
        
        print("Starting Video...")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,self.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,self.FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS,70)
   
                
        #Loop Param to enable or disable
        self.ShowBoxes = True
        self.TrackingEnabled = True
        self.OBJS = []
        self.CONF = 70.0
        #Default
        self.MyRobotVision_Obj_Classifier.SetSpecificObjSearch(self.OBJS,self.CONF)
                
        self.SharedMem.VisionRequestQ.SetReady()
        
        print("Default: " + self._DefaultMode)

        NewRequest = VisionRequestInterface()

        if (    self._DefaultMode==VisionRequestTypes.FIND_OBJECT 
            or  self._DefaultMode==VisionRequestTypes.FOLLOW_OBJECT):
            NewRequest.RequestType = self._DefaultMode
            NewRequest.TargetObjectsName = ['Persona']
            NewRequest.TargetObjectsConfidence = 70

        elif (self._DefaultMode==VisionRequestTypes.TRACK_OBJECT):
            NewRequest.RequestType = self._DefaultMode
            NewRequest.TargetObjectsName = []
            NewRequest.TargetObjectsConfidence = 70
            
        else:
            NewRequest.RequestType = VisionRequestTypes.IDLE
            NewRequest.TargetObjectsName = []
            NewRequest.TargetObjectsConfidence = 70
         
        self.SharedMem.VisionRequestQ.put(NewRequest)   
        
        Continue = True
        
        while Continue:
            
            print("..",end=" ")
            if (self.SharedMem.VisionRequestQ.HasItems()):
                
                NewRequest = self.SharedMem.VisionRequestQ.get()
                self.SharedMem.VisionRequestQ.Status = "Running Request " + str(NewRequest.RequestType)
                
                print("MESSAGE GOT")
              
                if (NewRequest.RequestType == VisionRequestTypes.IDLE):
                    self.ShowBoxes = False
                    self.TrackingEnabled = False
                    print("IDLE...........................")
                      
                if (NewRequest.RequestType == VisionRequestTypes.STOP_TRACKING):
                    self.ShowBoxes = False
                    self.TrackingEnabled = False
                    print("STOP  TRACKING...........................")
                
                elif (NewRequest.RequestType == VisionRequestTypes.TRACK_OBJECT):
                    self.ShowBoxes = False
                    self.TrackingEnabled = True
                    
                    print("START TRACKING...........................")
                    self.OBJS = NewRequest.TargetObjectsName
                    self.CONF = NewRequest.TargetObjectsConfidence
                    self.MyRobotVision_Obj_Classifier.SetSpecificObjSearch(self.OBJS,self.CONF)
            
                elif (NewRequest.RequestType == VisionRequestTypes.FIND_OBJECT):
                    self.ShowBoxes = True
                    self.TrackingEnabled = False
                    
                    print("FIND_OBJECT: " + NewRequest.TargetObjectsName[0])
                    self.OBJS = NewRequest.TargetObjectsName
                    self.CONF = NewRequest.TargetObjectsConfidence
                    self.MyRobotVision_Obj_Classifier.SetSpecificObjSearch(self.OBJS,self.CONF)

                elif (NewRequest.RequestType == VisionRequestTypes.FOLLOW_OBJECT):
                    self.ShowBoxes = False
                    self.TrackingEnabled = True

                    print("FOLLOW_OBJECT: " + NewRequest.TargetObjectsName[0])
                    self.OBJS = NewRequest.TargetObjectsName
                    self.CONF = NewRequest.TargetObjectsConfidence
                    self.MyRobotVision_Obj_Classifier.SetSpecificObjSearch(self.OBJS,self.CONF) 

            #Leggo Frame Video
            success,frame = self.cap.read()          
            
              
            if (success):
                TimeText = NewRequest.RequestType + " [" + str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")) + "]"
                if (not self.MyRobotVision_Object_Tracker.TrackStarted): ## Optimization: non traccio se ho avviato il tracking
                    success,  classIds, confs, bbox, FoundIndex, BestConf, FoundBox = self.MyRobotVision_Obj_Classifier.TrackObjects(frame,Title = TimeText, ShowBoxes=self.ShowBoxes)
                
                if (self.TrackingEnabled):
                    if (FoundIndex!=-1):
                        if (not self.MyRobotVision_Object_Tracker.TrackStarted):
                            roi = [FoundBox[0],FoundBox[1],FoundBox[2]-FoundBox[0],FoundBox[3]-FoundBox[1]]
                            ret = self.MyRobotVision_Object_Tracker.SetFirstTrackerFrame(frame, roi)
                            print("First ROI: ",roi)
                        else:
                            success, roi = self.MyRobotVision_Object_Tracker.UpdateTrackerFrame(frame)
                            print("Running: ",roi)
                            
            
                self.NameOfFaceFound = ""
                if (self.Enable_Face_Recog):
                    self.NameOfFaceFound = self.MyRobotVision_Face_Classifier.ApplyToFrame(frame)

 
                cv2.imshow("Output",frame)
                if (self.KeepWindowOnTop):
                    cv2.setWindowProperty("Output", cv2.WND_PROP_TOPMOST, 1)
                cv2.waitKey(1)       
                       
            
            time.sleep(0.001)
            Continue = super().Run_CanContinueRunnig()
        super().Run_Kill()
        
            
def RobotVision_Obj_Run(SharedMem, DefaultMode =  VisionRequestTypes.IDLE):
    MyRobotVision_Obj = RobotVision_Obj(ProcessList.Robot_Vision, DefaultMode)
    MyRobotVision_Obj.Run(SharedMem)
    
def Simul_Run(SharedMem):
    Robot_Simulate_Process_Obj_Run(SharedMem,Sparring_Process_Names.VISION )
   

if (__name__== "__main__"):
    
    RunSingleMode = True
  
    MySharedObjs = SharedObjs()
       
    if (RunSingleMode):
        RobotVision_Obj_Run(MySharedObjs,VisionRequestTypes.FOLLOW_OBJECT)
    else:
        run_io_tasks_in_parallel([
            RobotVision_Obj_Run
            ,Simul_Run
            #,RobotSharedParamsMonitor_Run
        ], MySharedObjs)    
