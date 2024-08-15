import multiprocessing as mp
from typing import Generic, TypeVar

T = TypeVar("T")

#MyTestQ = Socket_Utils_Q[Test]("Test Class")
class Socket_Q(Generic[T]):
    Name = ''
    TheQueue:mp.Queue = mp.Queue()
    TargetReadyToReceive = False
    Status:str = ''
    SemaphoreRed:bool = False
    
    def __init__(self,name) -> None:
        self.Name = name
        self.SemaphoreRed = False
        pass

    def put(self, element: T) -> None:
        while self.SemaphoreRed:
            pass
        self.SemaphoreRed = True
        self.TheQueue.put(element)
        self.SemaphoreRed = False

    def get(self) -> T:
        while self.SemaphoreRed:
            pass
        self.SemaphoreRed = True
        if(self.HasItems()):
            self.SemaphoreRed = False
            return self.TheQueue.get()  
        else:
            self.SemaphoreRed = False
            return None

    def Size(self) -> int:
        return (self.TheQueue.qsize())

    def HasItems(self) -> bool:
        return (self.TheQueue.qsize() >0)
    
    def Clear(self):
        while self.TheQueue.qsize()>0:
            self.TheQueue.get()
            
    def Show(self):
        print(self.Name + " size: " + str(self.TheQueue.qsize()))        
        
    def SetReady(self):
        self.TargetReadyToReceive = True
    
    def IsReady(self):
        return self.TargetReadyToReceive
    
  