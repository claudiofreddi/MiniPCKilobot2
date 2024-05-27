#cd c:\Users\user\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312
#python c:\dati\thisrobot\Events_MailNotification_Run.py

#RUN MAIL READER AND QUEUE EVENTS TO SUBSCRIBER
from Events_MailNotification import Event_MailReceiver 
import time

def Service_Read_Brainbotmail():
    print ('MailReaderAndQueue started')
    MyClass = Event_MailReceiver()
    while True:
        print ('MailReaderAndQueue checking')
        MyClass.Run()
        time.sleep(3)

Service_Read_Brainbotmail()
