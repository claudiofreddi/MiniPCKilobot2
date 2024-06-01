import cv2
import face_recognition as fr
from os.path import exists, os
import numpy as np
from Robot_Envs import *

class RobotVision_Object_Classifier():
    
    
    configPath = PATH_OBJ_CLASS_configPath
    weightsPath = PATH_OBJ_CLASS_weightsPath
    classFile = PATH_OBJ_CLASS_classFile
    thres = 0.45 # Threshold to detect object
    GreenColor = (0,255,0)
    RedColor = (255,0,0)
    BlueColor = (0,0,255)
    ConfidenceColorThres = 75
    LookForSpecificObjs = []
    LookForSpecificObjsConf = 70.0

        
        
    def _LoadObjectDatabase(self):
        with open(self.classFile,'rt') as f:
            self.classNames = f.read().rstrip('\n').split('\n')

        for i in range(0,len(self.classNames)):
            self.classNames[i] = self.classNames[i].upper()
        
        self.classNamesMatched = self.classNames
        
        print("Classes: " + str(list(self.classNames)))
        
        
    def __init__(self):
        self.DNNLoaded = False
        
        pass
    
    def Load(self):
        self._LoadObjectDatabase()
        
    def StartDNN(self):
        print("Starting DNN...")
        self.net = cv2.dnn_DetectionModel(self.weightsPath,self.configPath)
        self.net.setInputSize(320,320)
        self.net.setInputScale(1.0/ 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)
        print("Model ok") 
        
    def SetSpecificObjSearch(self,_LookForSpecificObjs, _LookForSpecificObjsConf:float):
        self.LookForSpecificObjs   = np.array(_LookForSpecificObjs).copy()
        self.LookForSpecificObjsConf = _LookForSpecificObjsConf
        #Set Uppercase
        for i in range(0,len(self.LookForSpecificObjs)):
            self.LookForSpecificObjs[i] = self.LookForSpecificObjs[i].upper()
            
        print("Look for: " + str(list(self.LookForSpecificObjs)))
        
    def TrackObjects(self,frame,Title = 'Title',ShowBoxes=True):
        success = False
        FoundIndex = -1
        BestConf = -1
        FoundBox = (0,0,0,0)
        
        if not (frame is None):
            if (len(frame) >0):
                
                classIds, confs, bbox = self.net.detect(frame,confThreshold=self.thres)   
                i = 0 
                for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
                    Match = (len(self.LookForSpecificObjs)==0) # se richiesti tutti 
                    if (len(self.LookForSpecificObjs)>0):
                        ret = np.where(np.array(self.LookForSpecificObjs) == np.array(self.classNames)[classId-1])[0]
                        Match = (len(ret) > 0 and confidence*100 > self.LookForSpecificObjsConf)
                        if (Match and BestConf < confidence*100): #get The best Confidence 
                            FoundIndex = i   #only if on LookForSpecificObjs
                            BestConf = confidence*100
                            FoundBox = bbox[i]
                             
                    if (Match):     
                        success = True
                        if (ShowBoxes):
                            color = self.GreenColor if (confidence*100 >= self.ConfidenceColorThres) else self.RedColor
                            #color = self.GreenColor
                            cv2.rectangle(frame,box,color=color,thickness=2)
                            cv2.putText(frame,self.classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                                        cv2.FONT_HERSHEY_COMPLEX,1,color,2)
                            cv2.putText(frame,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                                        cv2.FONT_HERSHEY_COMPLEX,1,color,2)
                        
                            cv2.putText(frame,Title,(10,30),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    
                    i = i + 1
        
        if (success):
            return success,  classIds, confs, bbox, FoundIndex, BestConf, FoundBox
        else:
            return success, [], [], [], -1, -1, (0,0,0,0)
                
    
if (__name__== "__main__"):
        
    _GetFromCam = True
    
    MyRobotVision_Obj_Classifier = RobotVision_Object_Classifier()
    MyRobotVision_Obj_Classifier.Load()
    MyRobotVision_Obj_Classifier.StartDNN()
    #MyRobotVision_Obj_Classifier.SetSpecificObjSearch(["Persona"],70)
       
       
    # Read video
    if (_GetFromCam):
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(PATH_TEST_VIDEO)

    # Read first frame.
    ret, frame = cap.read()
    
       
    while True:
        # Read a new frame
        ret, frame = cap.read()
        
        if (ret):
            success,  classIds, confs, bbox, FoundIndex, BestConf, FoundBox = MyRobotVision_Obj_Classifier.TrackObjects(frame)
            
            
            #print(len(classIds))
            print("Index " ,FoundIndex, " best conf: ",BestConf )
            print("Box " ,FoundBox)
            
            if (not success):
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