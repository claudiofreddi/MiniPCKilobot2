import pyodbc
from Robot_Envs import connectionString

class QManager_Def_Target:
    TELEGRAM = "TELEGRAM"
    MOTOR = "MOTOR"
    SPEAKER = "SPEAKER"
    POWER = "POWER"
   
class QManager_Def_Source:
    TELEGRAM = "TELEGRAM"
    EMAIL = "EMAIL"
    BRAIN = "BRAIN"
    

class QManager:

    def __init__(self):
        self.conn = pyodbc.connect(connectionString)
        self.conn.autocommit = True
        self.PrintLogEnabled = False
        
        if (self.PrintLogEnabled == True):
            print ('__init__')

    def PushData(self, Target, Source,Data1='',Data2='',Data3='',Data4='',Int1=0,Int2=0,decimal1=0.0,decimal2=0.0, Grp = '', GrpParent= ''):
       
        sql = f"exec [queue_manager].[PushData] '{Target}','{Source}','{Data1}','{Data2}','{Data3}','{Data4}',{Int1},{Int2},{decimal1},{decimal2},'{Grp}','{GrpParent}'"
        
        print(sql)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except pyodbc.ProgrammingError as e:
            raise Exception("Cannot execute " + sql)
              
        if (self.PrintLogEnabled == True):
            print ('Queue Item Addes')
            
    def ReadData(self, Target):
        sql = f"SET NOCOUNT ON DECLARE @token INT EXEC @token =[queue_manager].[PopDataId] '{Target}' SELECT @token"

        if (self.PrintLogEnabled == True):
            print (sql)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)

            while True:
                try:
                    record = cursor.fetchone() 
                    break
                except pyodbc.ProgrammingError as e:
                    if "Previous SQL was not a query." in str(e):
                        if not cursor.nextset():
                             raise Exception("Cannot execute " + sql)
            
        except pyodbc.ProgrammingError as e:
             raise Exception("Cannot execute " + sql)

        for token in record:
            if (self.PrintLogEnabled == True):
                print(token)
        
        T = []
        
        if (token != 0):
            sql = f"select * from queue_manager.ReadData('{token}')"
            cursor = self.conn.cursor()
            if (self.PrintLogEnabled == True):
                print (sql)
            cursor.execute(sql)
            records = cursor.fetchall()
            index = 0
            
            if (len(records) == 1):
                r = records[0]
                T = [r.Data1,r.Data2,r.Data3,r.Data4,r.Int1,r.Int2,r.Decimal1,r.Decimal2,r.Grp,r.GrpParent,r.Target,r.Source]
        
           
        return  T     


    def ClearData(self, Target, clearall=1):
        if (clearall == 1):
            sql = f"delete from [queue_manager].[QData] where [Target] = '{Target}'"
        else:
            sql = f"delete from [queue_manager].[QData] where [Target] = '{Target}' and StatusId > 0 "

        if (self.PrintLogEnabled == True):
            print (sql)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)

        except pyodbc.ProgrammingError as e:
            raise Exception("Cannot execute " + sql)          
        
        
if (__name__== "__main__"):
   
    MyQManager = QManager()
    MyQManager.ClearData(QManager_Def_Target.MOTOR)
    MyQManager.PushData(QManager_Def_Target.MOTOR,QManager_Def_Source.BRAIN ,'Test')
    record = MyQManager.ReadData(QManager_Def_Target.MOTOR)
    print(record)
    
    
    