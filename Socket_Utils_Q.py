import multiprocessing as mp
from typing import Generic, TypeVar

T = TypeVar("T")

#MyTestQ = Socket_Utils_Q[Test]("Test Class")
class Socket_Q(Generic[T]):
    
    def __init__(self,name = '') -> None:
        self.Name = name
        self.TheQueue:mp.Queue = mp.Queue()
        pass

    def put(self, element: T) -> None:
        self.TheQueue.put(element)


    def get(self) -> T:

        if(self.HasItems()):
            return self.TheQueue.get()  
        else:
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
        
    
    
  