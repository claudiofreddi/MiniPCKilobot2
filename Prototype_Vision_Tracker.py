import cv2


# For usage download models by following links
# For GOTURN:
#     goturn.prototxt and goturn.caffemodel: https://github.com/opencv/opencv_extra/tree/c4219d5eb3105ed8e634278fad312a1a8d2c182d/testdata/tracking
# For DaSiamRPN:
#     network:     https://www.dropbox.com/s/rr1lk9355vzolqv/dasiamrpn_model.onnx?dl=0
#     kernel_r1:   https://www.dropbox.com/s/999cqx5zrfi7w4p/dasiamrpn_kernel_r1.onnx?dl=0
#     kernel_cls1: https://www.dropbox.com/s/qvmtszx5h339a0w/dasiamrpn_kernel_cls1.onnx?dl=0
# For NanoTrack:
#     nanotrack_backbone: https://github.com/HonglinChu/SiamTrackers/blob/master/NanoTrack/models/nanotrackv2/nanotrack_backbone_sim.onnx
#     nanotrack_headneck: https://github.com/HonglinChu/SiamTrackers/blob/master/NanoTrack/models/nanotrackv2/nanotrack_head_sim.onnx

#pip install -U opencv-contrib-python

_GetFromCam = False
_TrackerChoice =5


def ask_for_tracker(Selected:int = -1):
    
    if (Selected == -1):
        print("Welcome! What Tracker API would you like to use?")
        print("Enter 0 for TrackerGOTURN: ")
        print("Enter 1 for TrackerMIL: ")
        print("Enter 2 for TrackerNano: ")
        print("Enter 3 for TrackerVit: ")
        print("Enter 4 for TrackerCSRT: ")
        print("Enter 5 for TrackerKCF: ")
        print("Enter 6 for TrackerDaSiamRPN: ")
        choice = input("Please select your tracker: ")
    else:
        choice = str(Selected)
    
    print(choice)
    
    tracker = None
    
    if choice == '0':
        tracker = cv2.TrackerGOTURN.create() #OK solo face
    if choice == '1':
        tracker = cv2.TrackerMIL.create()  #OK
    if choice == '2':
        tracker = cv2.TrackerNano.create()
    if choice == '3':
        tracker = cv2.TrackerVit.create()
    if choice == '4':
        tracker = cv2.TrackerCSRT.create() #OK
    if choice == '5':
        tracker = cv2.TrackerKCF.create()  #OK no libs
    if choice == '6':
        tracker = cv2.TrackerDaSiamRPN.create()   #OK
   
    
    return tracker

tracker = ask_for_tracker(_TrackerChoice)
tracker_name = str(tracker).split()[0][1:]

# Read video
if (_GetFromCam):
    cap = cv2.VideoCapture(0)
else:
    cap = cv2.VideoCapture('C:\Dati\MiniPCKilobot\Test_Videos\Test01.mp4')

# Read first frame.
ret, frame = cap.read()


# Special function allows us to draw on the very first frame our desired ROI
roi = cv2.selectROI(frame, False)

print(roi)

# Initialize tracker with first frame and bounding box
ret = tracker.init(frame, roi)

while True:
    # Read a new frame
    ret, frame = cap.read()
    
    
    # Update tracker
    success, roi = tracker.update(frame)
    
    # roi variable is a tuple of 4 floats
    # We need each value and we need them as integers
    (x,y,w,h) = tuple(map(int,roi))
    
    # Draw Rectangle as Tracker moves
    if success:
        # Tracking success
        p1 = (x, y)
        p2 = (x+w, y+h)
        cv2.rectangle(frame, p1, p2, (0,255,0), 3)
    else :
        # Tracking failure
        cv2.putText(frame, "Failure to Detect Tracking!!", (100,200), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),3)

    # Display tracker type on frame
    cv2.putText(frame, tracker_name, (20,400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),3);

    # Display result
    cv2.imshow(tracker_name, frame)

    # Exit if ESC pressed
    k = cv2.waitKey(1) & 0xff
    if k == 27 : 
        break
        
cap.release()
cv2.destroyAllWindows()