
from Socket_ClientServer_BaseClass import *

    

class Socket_GLobal_Config:
    
    ServiceToRun = [
                    Socket_Services_List.SERVER,        #Never Disable
                    Socket_Services_List.SENSORS ,
                    Socket_Services_List.KEYBOARD ,
                    #Socket_Services_List.USERINTERFACE ,
                    #Socket_Services_List.REMOTE ,
                    #Socket_Services_List.SAMPLE, 
                    Socket_Services_List.WEBCAM ,
                    Socket_Services_List.SPEAKER
                   ]
    
    SPEAKER_On = True
 
    def IsToRun(self,ServiceName):
        try:
           i = self.ServiceToRun.index(ServiceName)
           return True
        except:
            return False