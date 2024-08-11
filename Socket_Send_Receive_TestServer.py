# Import the required modules
from IPython.display import clear_output
import socket
import sys
import cv2
import matplotlib.pyplot as plt
import pickle
import numpy as np
import struct ## new
import zlib
from PIL import Image, ImageOps
from  Socket_Send_Receive import * 



class SocketMessageEnvelope:
    def  __init__(self,Uid = "",ContentType="",EncodedJson='',
                  From='',To='',
                  NeedResponse=False,Response='',ShowContentinLog = False,SendTime=0): 
        self.Uid = Uid
        self.ContentType = ContentType
        self.EncodedJson = EncodedJson
        self.NeedResponse = NeedResponse
        self.Response = Response
        self.ShowContentinLog = ShowContentinLog
        self.From=From
        self.To=To
        self.SendTime = 0 
        
        
        

HOST='127.0.0.1'
PORT=8485

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
print('Socket created')

s.bind((HOST,PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn,addr=s.accept()
#*****************************************************************************
#*****************************************************************************
data = b""

SSR = Socket_SendReceive()

while True:
    
    
    msg1, msg2 ,retval = SSR.recv_msg(conn)
    if (len(msg1)>0): 
        frame= pickle.loads(msg1, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)         
        cv2.imshow('server',frame)
        cv2.waitKey(1)
          
    if (len(msg2)>0):
        myobj:SocketMessageEnvelope = pickle.loads(msg2)
    
        print(myobj.UID)
    
