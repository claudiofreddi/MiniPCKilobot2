#Env
from ZOLD_Lib_Processes import *
from Lib_ArduinoConnection import *

class Robot_Arduino_Sensor_Params:
     SENSOR_COMPASS = "SENSORS_COMPASS"
     SENSORS_BATTERY = "SENSORS_BATTERY"


class ArduinoReadSensors_Obj(ProcessSuperClass):
    
  
    MyArduino_Connection = Arduino_Connection()
   
    
    def __init__(self,processName):
        super().__init__(processName)


    def _ParseParamValue(self,retData,ParamName):
        if (retData[:len(ParamName)] == ParamName):
            return True, retData[len(ParamName)+1:]
        else:
            return False, ''
       
        
           
    def receiveDataFromSensors(self)->bool:
        RetVal = False
        try:
            retData = self.MyArduino_Connection.ReadSerial()
            
            if (retData != ""):
                #Compass
                bFound, val = self._ParseParamValue(retData,Robot_Arduino_Sensor_Params.SENSOR_COMPASS)
                if (bFound):
                    intval = int(val)
                    if (intval != self.SharedMem.Compass):
                        super().LogConsole("Compass: " + str(self.SharedMem.Compass))
                    self.SharedMem.Compass = int(val)
                    RetVal = True
                    
               #Battery
                bFound, val = self._ParseParamValue(retData,Robot_Arduino_Sensor_Params.SENSORS_BATTERY)
                if (bFound):
                    intval = int(val)
                    if (intval != self.SharedMem.Battery):
                        super().LogConsole("Battery: " + str(self.SharedMem.Battery))
                    self.SharedMem.Battery = int(val)
                    RetVal = True
                 
                
                #Add Here Other Methods
                
                return RetVal
             
        except KeyboardInterrupt:
            super().LogConsole("Error in receiveDataFromSensors",ProcessSuperClassLogLevel.Control)
       
           
                
    def Run(self,SharedMem):
        super().Run_Pre(SharedMem)
                
        if (self.MyArduino_Connection.OpenConnection(self.SharedMem.Init_ARDUINO_B_COM_PORT)):
        
            Continue = True
            while Continue:
                #Internal method to read all params
                self.receiveDataFromSensors()    
                Continue = super().Run_CanContinueRunnig()
            super().Run_Kill()
    

def ArduinoReadSensors_Run(SharedMem):
    MyArduinoReadSensors_Obj = ArduinoReadSensors_Obj(ProcessList.Arduino_B_ReadSensors)
    MyArduinoReadSensors_Obj.Run(SharedMem)
   
if (__name__== "__main__"):

    MySharedObjs = SharedObjs()
    
    ArduinoReadSensors_Run(MySharedObjs)
