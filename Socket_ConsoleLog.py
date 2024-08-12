### ***************************************************************************
### LOG DEF
### ***************************************************************************

class  ConsoleLogLevel:
    
    Test = 0
    CurrentTest = 1
    
    System = 2
    Control = 3
    Always = 4
    Override_Call = 6
    Socket_Flow = 5 
    Show = 7
    
    Error = 90

class Common_LogConsoleClass(object):   
    EnableConsoleLog = True
    EnableAll = False
    EnableConsoleLogLevels = [
                              ConsoleLogLevel.Error   #keep always on
                              #,ConsoleLogLevel.Test
                              ,ConsoleLogLevel.CurrentTest #keep on temporary
                              ,ConsoleLogLevel.System
                              ,ConsoleLogLevel.Control
                              ,ConsoleLogLevel.Always
                              #,ConsoleLogLevel.Override_Call
                              #,ConsoleLogLevel.Socket_Flow
                              ,ConsoleLogLevel.Show    #keep on
                              
                              ]
    

    
    def LogConsole(self,Text,*LogLevels):
        
        if (self.EnableConsoleLog):
            
            if (self.EnableAll):
                print(Text) 
                
            else:
                if (len(LogLevels) == 0):
                    #Test is Default
                    LogLevel = ConsoleLogLevel.Test
                  
                    for v in self.EnableConsoleLogLevels:
                        if (v == LogLevel):
                            print(Text)
                            break
                            
                else:
                    for LogLevel in LogLevels:
                        for v in self.EnableConsoleLogLevels:
                            if (v == LogLevel):
                                print(Text)
                                break