import time

class RobotTimeout:
          
    _next_timeout:float = 0 
    _timer_started:time = None
    
    def __init__(self):
        return
    
    def StartNewTimeout(self,timeout:float):
        self._timer_started = time.perf_counter()
        self._next_timeout = timeout
    
    def IsTimeout(self)->bool:
        if (self._timer_started == None or self._next_timeout == 0): 
            return False
        return((time.perf_counter()-self._timer_started) > self._next_timeout)

    def ResetTimeout(self):
        self._next_timeout = 0  