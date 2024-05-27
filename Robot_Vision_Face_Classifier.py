import cv2
import face_recognition as fr
from os.path import exists, os
import numpy as np
from Robot_Envs import *

class RobotVision_Face_Classifier():
    
    
    listofknown_images = []
    listofknown_encoded_images = []
    known_face_names = []
    Peoplepath = PATH_FACE_REC_PEOPLE
    PeopleLoaded = False
    _EnableSavingNewFaces = True
    
    
    # Object
    face_classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    ) 

    def __init__(self):
         self.PeopleLoaded = False
         pass

    def Load(self):
        self._LoadPeopleDatabase()
        

    def ApplyToFrame(self, frame):   
        if (self.PeopleLoaded):
            self.faces = self._detect_bounding_box(
                frame, self.Peoplepath
            )  # apply the function we created to the video frame

    def _LoadPeopleDatabase(self):

        self.PeopleLoaded = False
        #Load People
        self._load_images_of_known_People(self.Peoplepath)

        if (len(self.known_face_names) == 0):
            print("No Files Found")
        else:
            self.PeopleLoaded = True
          
    
    
    def _load_images_of_known_People(self,MyPath):
        # Known Images 
        print (MyPath)
        dir_list = os.listdir(MyPath)
        print(dir_list)
        #Add Known Images 
        FilesCount = 0
        for imagename in dir_list:
            if (imagename[-3:] == "jpg"):
                file_exists = exists(MyPath + "//" + imagename)
                if (file_exists):
                    print("Loading " + imagename + "...")
                    known_image = fr.load_image_file(MyPath + "//" + imagename)
                    self.listofknown_images.insert(FilesCount, known_image)
                    self.known_face_names.insert(FilesCount,imagename[:-4])
                    small_frame = cv2.resize(known_image, (0, 0), fx=0.25, fy=0.25)
                    rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
                    face_locations1 = fr.face_locations(rgb_small_frame)
                    face_encodings1 = fr.face_encodings(rgb_small_frame, face_locations1)
                    known_encoding = np.array(face_encodings1).tolist()  
                    known_encoding = face_encodings1
                    if (len(known_encoding)>0):
                        known_encoding = known_encoding[0]
                        self.listofknown_encoded_images.insert(FilesCount, known_encoding)
                        #print(listofknown_encoded_images[FilesCount])
                    FilesCount = FilesCount + 1
                else:
                    break
            
            if (FilesCount == 0):
                print("No Files Found")
            
            
    def _detect_bounding_box(self,vid, MyPath):
        gray_image = cv2.cvtColor(vid, cv2.COLOR_BGR2GRAY)
        faces = self.face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
        for (x, y, w, h) in faces:
            cv2.rectangle(vid, (x, y), (x + w, y + h), (0, 0, 255), 4)
            my_image = vid[y:y+h, x:x+w]
            small_frame = cv2.resize(my_image, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
            face_locations1 = fr.face_locations(rgb_small_frame)
            face_encodings1 = fr.face_encodings(rgb_small_frame, face_locations1)
            unknown_encoding = np.array(face_encodings1).tolist()
            unknown_encoding = face_encodings1
            if (len(unknown_encoding)>0):
                unknown_encoding = unknown_encoding[0]
            
            if (len(unknown_encoding) > 0): 
                matches = fr.compare_faces(self.listofknown_encoded_images, unknown_encoding)
                print("matches")
                print(matches)
                
                isMatch = False
                if (matches.count(True) >0):
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                    isMatch = True
                else:
                    first_match_index = -1
                    name = ""
                    
                print(first_match_index)    
                print(name)   
                
                        
                # describe the type of font 
                # to be used. 
                font = cv2.FONT_HERSHEY_SIMPLEX 
            
                # Use putText() method for 
                # inserting text on video 
                cv2.putText(vid,  
                            name,  
                            (50, 50),  
                            font, 1,  
                            (0, 255, 255),  
                            2,  
                            cv2.LINE_4) 
            
                
                
                if (not isMatch and self._EnableSavingNewFaces):
                    nextid = len(self.listofknown_images)
                    imagename = "newimage" +  str(nextid) 
                    fullpath =  MyPath + "//" + imagename + ".jpg"
                    print("Salvo Immagine: " + imagename)
                    cv2.imwrite(fullpath, my_image)
                    
                    self.known_face_names.insert(nextid, imagename)
                    self.listofknown_images.insert(nextid, my_image)
                    self.listofknown_encoded_images.insert(nextid, unknown_encoding)
            
        if (first_match_index >= 0 and name != ""):
            FirstMatchName = name
         
        return FirstMatchName
    
    
if (__name__== "__main__"):
        
    _GetFromCam = True
    
    MyRobotVision_Face_Classifier = RobotVision_Face_Classifier()
    MyRobotVision_Face_Classifier.Load()
       
       
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
        
        
        MyRobotVision_Face_Classifier.ApplyToFrame(frame)
        
        # Display result
        cv2.imshow("Output",frame)
        cv2.setWindowProperty("Output", cv2.WND_PROP_TOPMOST, 1)
        cv2.waitKey(1)

        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27 : 
            break
        
    cap.release()
    cv2.destroyAllWindows()