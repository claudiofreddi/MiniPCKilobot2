import tkinter as tk
from ZOLD_Lib_Processes import *
from ZOLD_Robot_Arduino_A_DoActions import *
from ZOLD_Robot_Keyboard import RobotKeyboard_Run
import threading
import datetime
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk) 




class LabelIndex:
    Compass = 0
    FrontDistance = 1
    keyPressed = 2
    SpeakerStatus = 3
    ArduinoActionReady =4
    
class Robot_UI(threading.Thread):              


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
        print("************************************** Robot_UI init") 
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
            
            CURR_ROW = CURR_ROW + 1
            self.AddLabel_Pair(self.container,LabelIndex.ArduinoActionReady,"Arduino Action Ready:","",CURR_ROW,0)
            


            self.start_updates()
            
            self.plot()
            
            return
        except Exception as error:
            print("**************************************  Robot_UI init Error:  ",error) 
            
            
    

    def update_label(self): 
 
        self.root.title('Kilobot ' + str(datetime.datetime.now().time())[:8])
            
        if not (self._SharedMem is None):
            self.SetLabel_Pair(LabelIndex.Compass,str(self._SharedMem.Compass))
            self.SetLabel_Pair(LabelIndex.FrontDistance,str(self._SharedMem.LidarInfo.FrontDistance))
            self.SetLabel_Pair(LabelIndex.SpeakerStatus,str(self._SharedMem.SpeakerOn))
            
            self.SetLabel_Pair(LabelIndex.ArduinoActionReady,str(self._SharedMem.ArduinoCommandQ.IsReady()))
            
        
        if (SharedObjs.GLB_KEY_KeyPressed in self._SharedMem.GlobalMem.keys()):
            self.SetLabel_Pair(LabelIndex.keyPressed, self._SharedMem.GlobalMem[SharedObjs.GLB_KEY_KeyPressed])
        
        self.root.after(1000, self.update_label)
        
        


    def start_updates(self):
        self.root.after(1000, self.update_label)
        
        
    # plot function is created for 
    # plotting the graph in 
    # tkinter window 
    def plot(self): 
        try:
            # the figure that will contain the plot 
            fig = Figure(figsize = (5, 5),                 dpi = 100) 

            # list of squares 
            y = [i**2 for i in range(101)] 

            # adding the subplot 
            plot1 = fig.add_subplot(111) 

            # plotting the graph 
            plot1.plot(y) 

            # creating the Tkinter canvas 
            # containing the Matplotlib figure 
            canvas = FigureCanvasTkAgg(fig, 
                                    master = self.root) 

            canvas.draw() 
            
            

            # placing the canvas on the Tkinter window 
            #canvas.get_tk_widget().pack() 

            # creating the Matplotlib toolbar 
            toolbar = NavigationToolbar2Tk(canvas, 
                                        self.root) 
            
            toolbar.grid(row=9, column=0,  sticky=tk.W, padx=5, pady=5)
            toolbar.update() 

            # placing the toolbar on the Tkinter window 
            #canvas.get_tk_widget().pack()     
            
            return
        except Exception as error:
            print("**************************************  Robot_UI init Error:  ",error) 
            

    def Run(self, SharedMem:SharedObjs):
        self._SharedMem = SharedMem 
 
        try:
          
            


            self.root.mainloop()
            return    
        except Exception as error:
            print("**************************************  Robot_UI Run ",error) 
 
    
def RobotUI_Run(SharedMem):
    MyRobot_UI_Obj = Robot_UI()
    MyRobot_UI_Obj.Run(SharedMem)    
        
if (__name__== "__main__"):

    MySharedObjs = SharedObjs()
    
    
    if (True) :
        RobotUI_Run(MySharedObjs)
    else:
        run_io_tasks_in_parallel([
            RobotUI_Run
            ,Arduino_A_DoActions_Run
            ,RobotKeyboard_Run
            
        ], MySharedObjs)    