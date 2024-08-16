import pyodbc
from Robot_Envs import connectionString

class LogManager:

    def __init__(self):
        self.conn = pyodbc.connect(connectionString)
        self.conn.autocommit = True
        self.PrintLogEnabled = False
        
        if (self.PrintLogEnabled == True):
            print ('__init__')

    def Trace(self, Source, Info, IsError):
       
        sql = f"exec [logger].[SetLog] '{Source}','{Info}','{IsError}'"
        #print(sql)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except pyodbc.ProgrammingError as e:
            raise Exception("Cannot execute " + sql)
              
        if (self.PrintLogEnabled == True):
            print ('Param Saved')
            
    def TraceSimple(self, Info):
            self.Trace("", Info, 0)
            
           
if (__name__== "__main__"):
   
    MyLog = LogManager()
    MyLog.Trace("Freddi","My Log",0)
    