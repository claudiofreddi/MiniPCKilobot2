import pyodbc
from array import *
from Robot_Envs import connectionString

class ParamManager:

    def __init__(self):
        self.conn = pyodbc.connect(connectionString)
        self.conn.autocommit = True
        
        self.PrintLogEnabled = False
        
        if (self.PrintLogEnabled == True):
            print ('__init__')


    def InitializeParam(self, ParamKey, ParamValue, Source):
       
        sql = f"exec [param_manager].[InitializeParam] '{ParamKey}','{ParamValue}','{Source}'"
        #print(sql)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except pyodbc.ProgrammingError as e:
            raise Exception("Cannot execute " + sql)
              
        if (self.PrintLogEnabled == True):
            print ('Param Initialized')


    def SetParam(self, ParamKey, ParamValue, Source):
       
        sql = f"exec [param_manager].[SetParam] '{ParamKey}','{ParamValue}','{Source}'"
        #print(sql)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except pyodbc.ProgrammingError as e:
            raise Exception("Cannot execute " + sql)
              
        if (self.PrintLogEnabled == True):
            print ('Param Saved')
            
    def GetParam(self, ParamKey, ParamDefault = ''):
        sql = f"select * from [param_manager].[GetParam]('{ParamKey}')"
        cursor = self.conn.cursor()
        if (self.PrintLogEnabled == True):
            print (sql)
        cursor.execute(sql)
        records = cursor.fetchall()
        
        
        if (len(records)>0):
            return records[0].ParamValue
        else:
            return ParamDefault
        
if (__name__== "__main__"):
   
    MyParam = ParamManager()
    ParamVal = MyParam.GetParam("Test")
    print (ParamVal)
    
    MyParam.SetParam("Freddi","Claudio","localhost")
    
    ParamVal = MyParam.GetParam("Freddi")
    print (ParamVal)