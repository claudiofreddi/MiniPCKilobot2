
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
        FClass = [0] * numitems
        Weight = [0] * numitems
        Degrees = [0] * numitems
        TotalWeight = [0] * numitems
        
        Pos = 0
        Step = int(356/numitems)
        for i in range(0,len(Degrees)): 
            Degrees[i] = Pos
            Pos += Step
            FClass[i] = int(Arr[i]/100)*100
            Weight[i] = 0
        if (Test): print(numitems)    
        for i in range(0,numitems):
            TotalWeight[i] = 0
            for j in range(-8,9):
                TotalWeight[i] += Arr[self.CircularIndex(i+j,numitems-1)]
                #if (FClass[i] == FClass[self.CircularIndex(i+j,numitems-1)]): Weight[i] +=1 #abs(j)
            TotalWeight[i] = int(TotalWeight[i] )
            
        MaxIndex = -1
        LastMaxTotal = 0
        for i in range(0,numitems):
            if (TotalWeight[i] >= LastMaxTotal): 
                MaxIndex = i
                LastMaxTotal = TotalWeight[i] 
        
        # MaxIndex = -1
        # LastMaxTotal = 0
        # CountMaxVal = 0
        # for non_circular in range(0,numitems):  
        #     i = self.CircularIndex(non_circular,numitems-1)  
        #     TotalWeight[i] = FClass[i] * Weight[i] 
        #     if (TotalWeight[i] >= LastMaxTotal): 
        #         MaxIndex = i
                
        #         if (TotalWeight[i] == LastMaxTotal): 
        #             CountMaxVal += 1
        #         else:
        #             CountMaxVal =1
        #        LastMaxTotal = TotalWeight[i]
         
        # StepBack = int(CountMaxVal/2)
        
        print("MaxIndex: ", MaxIndex)
        # print("StepBack: ", StepBack)
        
        # if (MaxIndex - StepBack<0):
        #     MaxIndex = MaxIndex - StepBack  + numitems
        # else:
        #     MaxIndex = MaxIndex - StepBack
            
        if (Test):
            print(Arr)    
            print(Degrees)
            print(FClass)
            print(Weight)
            print(TotalWeight)
            print(MaxIndex)
            print(LastMaxTotal)
            print(Degrees[MaxIndex])
        
        if (MaxIndex!=-1):
            if (Test):return Degrees[MaxIndex] ,MaxIndex
            return Degrees[MaxIndex]
        
        return -1
        
    
if (__name__== "__main__"):   
    

    Arr =[311.8, 313.3, 316.4, 322.6, 173.6, 136.4, 120.9, 106.9, 96.0, 88.3, 82.1, 79.0, 72.8, 77.4, 92.9, 94.5, 86.7, 86.7, 92.9, 97.6, 89.8, 75.8, 68.1, 60.3, 57.2, 54.1, 51.0, 49.4, 47.1, 47.1, 47.1, 47.5, 47.9, 18.8, 18.8, 19.1, 20.5, 22.8, 26.1, 30.3, 35.9, 46.0, 61.8, 262.1, 273.0, 274.5, 276.1, 280.7, 290.1, 300.9, 313.3, 46.4, 41.9, 40.6, 40.6, 45.2, 325.8, 318.0, 313.3, 311.8]
    Obj = Socket_Utils_Lidar_Algorithm()
    retval =  Obj.GetBestAngleToMove(Arr,True)
    print(retval)
    
    # maxVal = 3
    # for i in range(-10,10):
    #     print(str(Obj.CircularIndex(i,maxVal)), i)
    