# timer.py

import time

class Timer:
    def __init__(self):
        self._start_time = None
        self._TimeoutSecond = 0
        

    def start(self,TimeoutSecond,Name = ""):
        
        self._Name = Name
        
        """Start a new timer"""
        if self._start_time is not None:
            print(f"Timer is running. Use .stop() to stop it")
        self._TimeoutSecond = TimeoutSecond
        self._start_time = time.perf_counter()


    def IsTimeout(self):
        if self._start_time is None:
            return False
        if (self._TimeoutSecond==0):return False
        elapsed_time = self.GetElapsed()
        if (elapsed_time > self._TimeoutSecond):
            return True

    def Reset(self,NewTimeoutSecond = 0):
        if (NewTimeoutSecond >0):
            self._TimeoutSecond = NewTimeoutSecond
        self._start_time = time.perf_counter()
        
    def GetElapsed(self):
        if self._start_time is None:
            return 0
        return  time.perf_counter() - self._start_time

    def stop(self):
        
        if self._start_time is None:
            raise print(f"Timer is not running. Use .start() to start it")

        elapsed_time = self.GetElapsed()
        self._start_time = None
        print(f"{ self._Name}: Elapsed time: {elapsed_time:0.4f} seconds")
        return elapsed_time
    
MyTimer =Timer ()
MyTimer.start(5,"pippo")
while True:
    if MyTimer.IsTimeout():
        break

MyTimer.Reset(2)
    
while True:
    if MyTimer.IsTimeout():
        break
        
MyTimer.stop()