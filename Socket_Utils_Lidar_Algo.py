
import numpy as np


class Socket_Utils_Lidar_Algorithm():
    
    def __init__(self):
        pass
    
    def CircularIndex(self,CurrIndex,MaxIndex=359):
        if (CurrIndex>=0 and CurrIndex<=MaxIndex):  
            return CurrIndex
        
        if (CurrIndex<0):
            while CurrIndex<0:
                CurrIndex = CurrIndex + MaxIndex + 1
        
        if (CurrIndex>MaxIndex):
            while CurrIndex>MaxIndex:
                CurrIndex = CurrIndex - MaxIndex - 1

        return CurrIndex
        
    def GetBestAngleToMove(self,Arr, Test=False):

        numitems = len(Arr)
        #FClass = [0] * numitems
        Degrees = [0] * numitems
        TotalWeight = [0] * numitems
        
        Pos = 0
        Step = int(360/numitems)
        for i in range(0,len(Degrees)): 
            Degrees[i] = Pos
            Pos += Step
            #FClass[i] = int(Arr[i]/100)*100
            
        if (Test): print(numitems)    
        MAX_HALF_WINDOW = 6
        for i in range(0,numitems):
            TotalWeight[i] = 0
            for j in range(-MAX_HALF_WINDOW,MAX_HALF_WINDOW+1):
                TotalWeight[i] += Arr[self.CircularIndex(i+j,numitems-1)]
            TotalWeight[i] = int(TotalWeight[i] )
            
        MaxIndex = -1
        LastMaxTotal = 0
        for i in range(0,numitems):
            if (TotalWeight[i] >= LastMaxTotal): 
                MaxIndex = i
                LastMaxTotal = TotalWeight[i] 
        
        if (Test):print("MaxIndex: ", MaxIndex)

        if (Test):
            print(Arr)    
            print(Degrees)
            #print(FClass)
            print(TotalWeight)
            print(MaxIndex)
            print(LastMaxTotal)
            print(Degrees[MaxIndex])
        
        print(TotalWeight)
        
        if (MaxIndex!=-1):
            return Degrees[MaxIndex]
        
        return -1
        
    
if (__name__== "__main__"):   
    

    Arr =[311.8, 313.3, 316.4, 322.6, 173.6, 136.4, 120.9, 106.9, 96.0, 88.3, 82.1, 79.0, 72.8, 77.4, 92.9, 94.5, 86.7, 86.7, 92.9, 97.6, 89.8, 75.8, 68.1, 60.3, 57.2, 54.1, 51.0, 49.4, 47.1, 47.1, 47.1, 47.5, 47.9, 18.8, 18.8, 19.1, 20.5, 22.8, 26.1, 30.3, 35.9, 46.0, 61.8, 262.1, 273.0, 274.5, 276.1, 280.7, 290.1, 300.9, 313.3, 46.4, 41.9, 40.6, 40.6, 45.2, 325.8, 318.0, 313.3, 311.8]
    Obj = Socket_Utils_Lidar_Algorithm()
    retval =  Obj.GetBestAngleToMove(Arr,True)
    print(retval) #12
    
    # maxVal = 3
    # for i in range(-10,10):
    #     print(str(Obj.CircularIndex(i,maxVal)), i)
    