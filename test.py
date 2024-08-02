import tkinter

import numpy as np

# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
import cv2 
from PIL import Image, ImageTk 

Label2L =  []
Label2R = []

root = tkinter.Tk()
root.wm_title("Embedding in Tk")



# Define a video capture object 
vid = cv2.VideoCapture(0) 

# Declare the width and height in variables 
width, height = 800, 600

# Set the width and height 
vid.set(cv2.CAP_PROP_FRAME_WIDTH, width) 
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height) 


# Bind the app with Escape keyboard to 
# quit app whenever pressed 
root.bind('<Escape>', lambda e: root.quit()) 

# Create a label and display it on app 
label_widget = tkinter.Label(root) 
#label_widget.pack() 

# Create a function to open camera and 
# display it in the label_widget on app 

def open_camera(): 

	# Capture the video frame by frame 
	_, frame = vid.read() 

	# Convert image from one color space to other 
	opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA) 

	# Capture the latest frame and transform to image 
	captured_image = Image.fromarray(opencv_image) 

	# Convert captured image to photoimage 
	photo_image = ImageTk.PhotoImage(image=captured_image) 

	# Displaying photoimage in the label 
	label_widget.photo_image = photo_image 

	# Configure image in the label 
	label_widget.configure(image=photo_image) 

	# Repeat the same process after every 10 seconds 
	label_widget.after(10, open_camera) 

def AddLabel_Pair(container,index, Label, Value, Row, Sector): 
    j:int = (Sector*2)

    CurrL =  tkinter.Label(container, text=Label, padx=10, pady=5)
    CurrL.grid(row=Row, column=j,  sticky=tkinter.W, padx=5, pady=5)
    Label2L.insert(index, CurrL)
    CurrR =  tkinter.Label(container, text=Value, padx=10, pady=5)
    CurrR.grid(row=Row,column=(j+1),  sticky=tkinter.E, padx=5, pady=5)
    Label2R.insert(index, CurrR)


fig = Figure(figsize=(5, 4), dpi=100)
t = np.arange(0, 3, .01)
ax = fig.add_subplot()
line, = ax.plot(t, 2 * np.sin(2 * np.pi * t))
ax.set_xlabel("time [s]")
ax.set_ylabel("f(t)")

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()

# pack_toolbar=False will make it easier to use a layout manager later on.
toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()

canvas.mpl_connect(
    "key_press_event", lambda event: print(f"you pressed {event.key}"))
canvas.mpl_connect("key_press_event", key_press_handler)

button_quit = tkinter.Button(master=root, text="Quit", command=root.destroy)


container = tkinter.Frame(root, padx=20, pady=10)
container.grid()

AddLabel_Pair(container,0,"Compass:","",0,0)
AddLabel_Pair(container,0,"keyPressed:","",0,1)



def update_frequency(new_val):
    # retrieve frequency
    f = float(new_val)

    # update data
    y = 2 * np.sin(2 * np.pi * f * t)
    line.set_data(t, y)

    # required to update canvas and attached toolbar!
    canvas.draw()


slider_update = tkinter.Scale(root, from_=1, to=5, orient=tkinter.HORIZONTAL,
                              command=update_frequency, label="Frequency [Hz]")


open_camera()

# Packing order is important. Widgets are processed sequentially and if there
# is no space left, because the window is too small, they are not displayed.
# The canvas is rather flexible in its size, so we pack it last which makes
# sure the UI controls are displayed as long as possible.
label_widget.pack(side=tkinter.LEFT)
container.pack(side=tkinter.LEFT)
button_quit.pack(side=tkinter.BOTTOM)
slider_update.pack(side=tkinter.BOTTOM)
toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)




tkinter.mainloop()