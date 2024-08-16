#cd c:\Users\user\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312
#python c:\dati\thisrobot\RunService_ExecMailCommands.py

from ZOLD_Lib_EventManager import *
import array 
import time
from Lib_SpeakToMe import Service_SpeakToMe

def Dispatch_Mail_Commands():
    MySubscriber = SubscriberEventManager('MyMailCommandListener')
    MySpeaker = Service_SpeakToMe()
    MySubscriber.SubscribeService('MailNotification')
    print ('subscribed')
    while True:
        T = MySubscriber.ReadService('MailNotification')
        for t in T:
            Data1 = t[0] #mail id
            Data2 = t[1] #subject
            Data3 = t[2] #sender
            print(t)
            commandInfo = Data2.split(":",1)
            print(commandInfo)
            if (len(commandInfo)==2):
                commandType = commandInfo[0].lower()    #tipo comando
                commandData = commandInfo[1]            #comando
                match commandType:
                    case "speak":
                        MySpeaker.Speak(commandData)

                    case "light":
                        MySpeaker.Speak("light")
                        
                        
                    case _:
                        MySpeaker.Speak("command not found")
                
                time.sleep(1)
            else:
                MySpeaker.Speak("command not found")
                
        time.sleep(3)



