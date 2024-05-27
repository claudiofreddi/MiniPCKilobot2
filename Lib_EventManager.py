import pyodbc
from array import *
from Robot_Envs import connectionString

class RaiseEventManager:

    def __init__(self, ServiceName):
        self.conn = pyodbc.connect(connectionString)
        self.conn.autocommit = True
        self.servicename = ServiceName
        self.PrintLogEnabled = False
        
        if (self.PrintLogEnabled == True):
            print ('__init__')

    def RegisterService(self):

        if (self.PrintLogEnabled == True):
            print ('RegisterService start')
        
        sql = f"exec [event_manager].RegisterService '{self.servicename}'"

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            if (self.PrintLogEnabled == True):
                print (sql)
        except pyodbc.ProgrammingError as e:
            raise Exception("Cannot execute " + sql)
              
        if (self.PrintLogEnabled == True):
            print ('RegisterService ok')


    def Notify(self, Data1, Data2, Data3, Data1_IsKey):
       
        sql = f"exec [event_manager].[notification_raise] '{self.servicename}','{Data1}','{Data2}','{Data3}',{Data1_IsKey}"
        print(sql)
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except pyodbc.ProgrammingError as e:
            raise Exception("Cannot execute " + sql)
              
        if (self.PrintLogEnabled == True):
            print ('Notification Sent')

class SubscriberEventManager:
    
    def __init__(self, SubscriberId):
        self.conn = pyodbc.connect(connectionString)
        self.conn.autocommit = True
        self.subscriberid = SubscriberId
        self.PrintLogEnabled = False

    def SubscribeService(self, ServiceName):
   
        sql = f"exec [event_manager].subscribe '{self.subscriberid}', '{ServiceName}'"

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except pyodbc.ProgrammingError as e:
            raise Exception("Cannot execute " + sql)
              
        if (self.PrintLogEnabled == True):
            print ('Subscription ok')

    def ReadService(self, ServiceName):
        sql = f"SET NOCOUNT ON DECLARE @token INT EXEC @token = [event_manager].notification_lock_for_read '{self.subscriberid}','{ServiceName}' SELECT @token"

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
            sql = f"select * from [event_manager].[notification_read_data]('{ServiceName}', {token})"
            cursor = self.conn.cursor()
            if (self.PrintLogEnabled == True):
                print (sql)
            cursor.execute(sql)
            records = cursor.fetchall()
            index = 0
            
            for r in records:
                if (self.PrintLogEnabled == True):
                    print(f"{r.id}\t{r.NotificationData1}")
                T.append([r.NotificationData1,r.NotificationData2,r.NotificationData3])
                index = index + 1  
            
            if (self.PrintLogEnabled == True):
                print(f'records found = {index}')
            
        else:
            if (self.PrintLogEnabled == True):
                print('no record found')    
    
        sql = f"exec [event_manager].[notification_set_read] '{ServiceName}', {token}"
        cursor = self.conn.cursor()
        if (self.PrintLogEnabled == True):
            print (sql)
        cursor.execute(sql)

        return T    

