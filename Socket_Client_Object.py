import socket
from Socket_Messages import * 
import queue

class client_object:
    client:socket = None
    servicename:str = ''
    address = ('',0)
    Topics = list()
    TopicSubscriptions = list()
    ErrCount = 0
    
    def __init__(self):
        pass
    
    def __init__(self,Client:socket, ServiceName:str, Address):
        self.client = Client
        self.servicename = ServiceName
        self.address = Address    
        self.Topics = list()
        self.TopicSubscriptions = list()
        self.ErrCount = 0
        
    def ShowDetails(self):

        print("******************************************") 
        print(self.servicename + " " + str(self.address))
        print("registered topics: NONE" if len(self.Topics)==0 else "registered topics: ") 
               
        for t in self.Topics:
            print("   " + t)
        
        print("")
        print("registered subscriptions: NONE" if len(self.TopicSubscriptions)==0 else "registered subscriptions:") 
        for s in self.TopicSubscriptions:
            print("   " + s)
        
        print("")

        
                                                    
    def ExistsTopic(self,Topic):
        for t in self.Topics:
            if (t==Topic):
                return True
        return False

    def ExistsTopicSubscription(self,TopicSubscription):
        for t in self.TopicSubscriptions:
            if (t==TopicSubscription):
                return True
        return False
            
    def RegisterTopic(self,NewTopic):
              
        if (Socket_Default_Message_Topics().IsTopicReserved(NewTopic)):
            return False
        if (not self.ExistsTopic(NewTopic)):
            self.Topics.append(NewTopic)  
            return True
        
        return False

    def SubscribeTopic(self,SubscribeTopic):
        
        if (Socket_Default_Message_Topics().IsTopicReserved(SubscribeTopic)):
            return False
        
        if (not self.ExistsTopicSubscription(SubscribeTopic)):
            self.TopicSubscriptions.append(SubscribeTopic)  
            return True
        
        return False         

    def UnSubscribeTopic(self,UnSubscribeTopic):
      
        try:
            i = self.TopicSubscriptions.index(UnSubscribeTopic)
            self.TopicSubscriptions.remove(UnSubscribeTopic)
            
            return True           
            
        except Exception as e:
           pass 
       
        return False 

    def IsSubscribedToThisTopic(self, TopicToCheck):
        for t in self.TopicSubscriptions:
            if (t == TopicToCheck):
               return True 
        return False