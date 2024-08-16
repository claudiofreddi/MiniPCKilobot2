import multiprocessing as mp
from typing import Generic, TypeVar

T = TypeVar("T")

class MyQ(Generic[T]):
    Name = ''
    TheQueue:mp.Queue = mp.Queue()
    TargetReadyToReceive = False
    Status:str = ''
    
    def __init__(self,name) -> None:
        self.Name = name
        pass

    def put(self, element: T) -> None:
        self.TheQueue.put(element)

    def get(self) -> T:
        if(self.HasItems()):
            return self.TheQueue.get()  
        else:
            return None

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
    
class Test:
    P1 = "P1"
    P2 = 0
    
    def __init__(self) -> None:
        pass
    
    def Show(self):
        print(self.P1 + " " + str(self.P2))

    
if (__name__== "__main__"):

    MyTestQ = MyQ[Test]("Test Class")
    NewTest = Test()
    NewTest.P1 ="1"
    NewTest.P2 = 1
    
    MyTestQ.put(NewTest)

    NewTest = Test()
    NewTest.P1 ="2"
    NewTest.P2 = 2
    
    MyTestQ.put(NewTest)
    
    MyTestQ.Show()
    
    MyTestQ.Clear()
    
    MyTestQ.Show()
    
    if (MyTestQ.HasItems()):
        Ret:Test = MyTestQ.get()
        Ret.Show()
    
    if (MyTestQ.HasItems()):
        Ret:Test = MyTestQ.get()
        Ret.Show()
    
    #Missing Element
    Ret:Test = MyTestQ.get()
    if (not Ret == None):
        Ret.Show()
        
    
    
    
    
   
