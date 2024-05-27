from Events_MailNotification import Event_MailReceiver 
import time

MyClass = Event_MailReceiver()
while True:
    print ('Start Reading and Notifying')
    MyClass.Run()
    time.sleep(3)

