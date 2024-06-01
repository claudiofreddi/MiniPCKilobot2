import tkinter as tk
from Lib_Processes import *
from Robot_Arduino_A_DoActions import *
from Robot_Keyboard import *
import threading
import datetime

class LabelIndex:
    Compass = 0
    FrontDistance = 1
    keyPressed = 2
    SpeakerStatus = 3
    
class TestClass(threading.Thread):              


    #root = tk.Tk()
    _SharedMem:SharedObjs
    Label2Count = 0
    Label2L =  []
    Label2R = []
    
    def AddLabel_Pair(self,container,index, Label, Value, Row, Sector): 
        j:int = (Sector*2)

        CurrL =  tk.Label(container, text=Label, padx=10, pady=5)
        CurrL.grid(row=Row, column=j,  sticky=tk.W, padx=5, pady=5)
        self.Label2L.insert(index, CurrL)
        CurrR =  tk.Label(container, text=Value, padx=10, pady=5)
        CurrR.grid(row=Row,column=(j+1),  sticky=tk.E, padx=5, pady=5)
        self.Label2R.insert(index, CurrR)
            
    def SetLabel_Pair(self, index,Value):
        self.Label2R[index].config(text=Value)     
   

    def __init__(self):
        threading.Thread.__init__(self)
        print("************************************** TestClass init") 
        try:
            self.root = tk.Tk()
            self.root.geometry("500x600")
            #self.root.resizable(0, 0)
            self.root.title('Kilobot')
            
             # Create a frame container
            self.container = tk.Frame(self.root, padx=20, pady=10)
            self.container.grid()
            
            
            CURR_ROW = 0
            self.AddLabel_Pair(self.container,LabelIndex.Compass,"Compass:","",CURR_ROW,0)
            self.AddLabel_Pair(self.container,LabelIndex.keyPressed,"keyPressed:","",CURR_ROW,1)
            
            CURR_ROW = CURR_ROW + 1
            self.AddLabel_Pair(self.container,LabelIndex.FrontDistance,"Front Distance:","",CURR_ROW,0)
            self.AddLabel_Pair(self.container,LabelIndex.SpeakerStatus,"Speaker:","",CURR_ROW,1)
            


           
            self.start_updates()
            
            return
        except Exception as error:
            print("**************************************  TestClass init  ",error) 
            
            
    

    def update_label(self):

        self.root.title('Kilobot ' + str(datetime.datetime.now().time())[:8])
            
        if not (self._SharedMem is None):
            self.SetLabel_Pair(LabelIndex.Compass,str(self._SharedMem.Compass))
            self.SetLabel_Pair(LabelIndex.FrontDistance,str(self._SharedMem.LidarInfo.FrontDistance))
            self.SetLabel_Pair(LabelIndex.SpeakerStatus,str(self._SharedMem.SpeakerOn))
            
        
        if ("Key" in self._SharedMem.GlobalMem.keys()):
            self.SetLabel_Pair(LabelIndex.keyPressed, self._SharedMem.GlobalMem["KeyPressed"])
        
        self.root.after(1000, self.update_label)
        
        


    def start_updates(self):
        self.root.after(1000, self.update_label)

    def Run(self, SharedMem:SharedObjs):
        self._SharedMem = SharedMem 
        print("************************************** TestClass Run")    
        try:
          


            print("************************************** main loop")
            self.root.mainloop()
            return    
        except Exception as error:
            print("**************************************  TestClass Run ",error) 
 
 
def RobotKeyboard_Run(SharedMem):
    MyRobotKeyboard_Obj = RobotKeyboard_Obj(ProcessList.Robot_Keyboard)
    MyRobotKeyboard_Obj.Run(SharedMem)
    
    
def UI_Run(SharedMem):
    MyTestClass_Obj = TestClass()
    MyTestClass_Obj.Run(SharedMem)    
        
if (__name__== "__main__"):

    MySharedObjs = SharedObjs()
    UI_Run(MySharedObjs)
    
    
    if (False) :

        run_io_tasks_in_parallel([
            UI_Run
            ,Arduino_A_DoActions_Run
            ,RobotKeyboard_Run
            
        ], MySharedObjs)    