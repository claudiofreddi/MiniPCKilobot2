from Lib_EventManager import *
from array import *

#Sample
MyServiceName = RaiseEventManager('EventRaiserName')
MyServiceName.RegisterService()

MySubscriber = SubscriberEventManager('MySubscriberActuator')
MySubscriber.SubscribeService('EventRaiserName')

MyServiceName.Notify('A','B','C',1)
T = MySubscriber.ReadService('EventRaiserName')
print(T)

T = MySubscriber.ReadService('EventRaiserName')
print(T)
