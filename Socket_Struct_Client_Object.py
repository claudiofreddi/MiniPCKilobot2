import socket
from Socket_Struct_Messages import * 
import os

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

        Text = "******************************************"+ "\n"
        Text += self.servicename + " " + str(self.address) + "\n"
        Text += "registered topics:        NONE\n" if len(self.Topics)==0 else f"registered topics:        {self.Topics}" + "\n"
        Text += "registered subscriptions: NONE\n" if len(self.TopicSubscriptions)==0 else f"registered subscriptions: {self.TopicSubscriptions}" + "\n"
        Text += "\n"
        #print(Text)
        return Text
    
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

    def IsSubscribedToThisTopic(self, PartialTopic):
        for t in self.TopicSubscriptions:
            if (self.SingleTopicMatched(t,PartialTopic)):
               return True 
        
        return False
    
    
    def splitall(self,path):
        allparts = []
        while 1:
            parts = os.path.split(path)
            if parts[0] == path:  # sentinel for absolute paths
                if (parts[0] != "*"):
                    allparts.insert(0, parts[0])
                break
            elif parts[1] == path: # sentinel for relative paths
                if (parts[1] != "*"):
                    allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                if (parts[1] != "*"):
                    allparts.insert(0, parts[1])
        return allparts

    def SingleTopicMatched(self,FullTopic, PartialTopic) -> bool:
        pt = self.splitall(PartialTopic)
        ft = self.splitall(FullTopic)
        
        IsMatchOK = True
        minlen = len(pt) 
        if len(ft)<len(pt): minlen = len(ft)  
        
        for i in range(minlen):
            if (pt[i] != ft[i]):
                IsMatchOK = False
        # if (IsMatchOK):
        #     print(pt)
        #     print(ft)
        return IsMatchOK
        
    def TopicMatched(self,FullTopicList, PartialTopic):
        RetList = []
        
        for ft in FullTopicList:
            if self.SingleTopicMatched(ft,PartialTopic):
                RetList.append(ft)
            
        return RetList
            