import time
import serial.tools.list_ports  
import serial
from Socket_Utils_Timer import * 
class Arduino_Connection:

    _TraceLogOn = True
    IsStarted  = False
    
    
    USE_TERMINAL = '\n'
         
    def __init__(self):
         pass
    
    def _TraceLog(self,Text:str):
        if (self._TraceLogOn):
            print(Text)
            
            
    def ReadPorts(self, ComPort:str)->bool:

        ports = serial.tools.list_ports.comports()
        Found = False
        for onePort in ports:
            if (ComPort == str(onePort)[:len(ComPort)]):
                Found = True
                if (self._TraceLog):
                    print("[*] " + str(onePort))
            else:
                if (self._TraceLog):
                    print("[ ] " + str(onePort))
            
        return Found
    
    
  
                                 
    def OpenConnection(self, ComPort:str, BaudRate:int=115200, WaitForCommand:str="ArduinoReady", ContinueAnyway=False) -> bool:

        self.IsStarted  = False
        
        #CheckPort
        if not (self.ReadPorts(ComPort)):
            self._TraceLog("Port " + ComPort+" not Found")
            return False
                
        try:   
            self.arduino = serial.Serial(port=ComPort, baudrate=BaudRate, timeout=1) 
            time.sleep(0.5)
            if not (self.arduino.is_open):
                self._TraceLog("arduino not open")
                return False
            
            self.arduino.reset_input_buffer()
            #arduino.reset_output_buffer()
            
            if (WaitForCommand != ""):
                    
                ArduinoOK = False
                MyRobotTimeout = Socket_Timer()
                MaxTimeout = 20 #sec
                self._TraceLog("waiting for " + WaitForCommand + " for " + str(MaxTimeout) +  "sec(s) ...")    
                MyRobotTimeout.start(MaxTimeout)
                IsTimeout = MyRobotTimeout.IsTimeout()
                while not (ArduinoOK or IsTimeout):
                    data = self.ReadSerial()
                    self._TraceLog(data)
                    ArduinoOK = (data == WaitForCommand)
                    time.sleep(0.1)
                    IsTimeout = MyRobotTimeout.IsTimeout()
            
                #Uscita con Timeout
                if (IsTimeout):
                    self._TraceLog("Arduino Ready Command Not Received")
                    if (not ContinueAnyway):
                        return False
            
            #ok or ContinueAnyway
            self._TraceLog("Connected")
            self.IsStarted  = True
            return True
        
        except KeyboardInterrupt:
            self._TraceLog("error")
            self.IsStarted  = True
            return True
 
            
    def IsOpen(self) -> bool:
        return self.arduino.is_open 
    
    def ReadSerial(self)->str:
        return self.arduino.readline().decode().strip()
        
    def sendData(self,dataToTransmit):
        try:
            if (dataToTransmit != ""):
                self.arduino.write(bytes(dataToTransmit + self.USE_TERMINAL,'utf-8'))
                self._TraceLog("PC ->[" +  dataToTransmit + "]")
                #time.sleep(0.5)
                
        except KeyboardInterrupt:
            self._TraceLog("Error in sending Data")
         
            
    def CloseConnection(self):
        if (self.arduino.is_open):
            self._TraceLog("Arduino Closed")
            self.arduino.close()        
            
    def MainTest(self):
        try:
            self._TraceLog("Start")
            #self.arduino.write(bytes('switchon','utf-8'))
            #time.sleep(1)
            self.arduino.write(bytes('fw' + self.USE_TERMINAL,'utf-8'))
            time.sleep(1)
           # self.arduino.write(bytes('stop','utf-8'))
            time.sleep(1)
            #self.arduino.write(bytes('switchoff','utf-8'))
            #time.sleep(1)
            self._TraceLog("End Test")
        
        except KeyboardInterrupt:
            print("error")
        
    
if (__name__== "__main__"):

    MyArduino_Connection = Arduino_Connection()
    
    if (MyArduino_Connection.OpenConnection("COM5")):
        MyArduino_Connection.MainTest()
        MyArduino_Connection.CloseConnection()
        
    