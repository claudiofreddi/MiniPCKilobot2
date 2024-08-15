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