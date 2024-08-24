#Utils
class Socket_TextCommandParser():
    
    def __init__(self,CmdToParse):
        self.CmdToParse = str.lower(CmdToParse)
        
    
    def _parseText(self,InputCmd, pos, GetAllTailParams = False)->str:
        ValSplitted = str(InputCmd).split()
        if (pos<len(ValSplitted)):
            if (not GetAllTailParams):
                return str(ValSplitted[pos])
            else:
                return ' '.join(ValSplitted[pos:])
        return ''    
        
  
    def GetSpecificCommand(self):
        return self._parseText(self.CmdToParse,0)
    
    def GetSpecificCommandParam(self, paramPos, GetAllTailParams = False)-> str:
        return self._parseText(self.CmdToParse,paramPos,GetAllTailParams)
    
    def Utils_Split_Cmd_Param(self, CmdToParse="",Lowered=True):
        if (CmdToParse!=""):
            self.CmdToParse = CmdToParse
        if (Lowered):self.CmdToParse =self.CmdToParse.lower()
        return self.GetSpecificCommand(), self.GetSpecificCommandParam(1,True)
     
    def Utils_Split_Cmd_Param_Param(self, CmdToParse="",Lowered=True):
        if (CmdToParse!=""):
            self.CmdToParse = CmdToParse
        if (Lowered):self.CmdToParse =self.CmdToParse.lower()
        return self.GetSpecificCommand(), self.GetSpecificCommandParam(1,False), self.GetSpecificCommandParam(2,True)

if (__name__== "__main__"):
    #Sample
    MyTP = Socket_TextCommandParser("pippo pluto e paparino")
    print(MyTP.Utils_Split_Cmd_Param())
    print(MyTP.Utils_Split_Cmd_Param_Param())
    print(MyTP.Utils_Split_Cmd_Param("Testo 1"))
    print(MyTP.Utils_Split_Cmd_Param_Param("Testo 1"))
