#pip install -U deep-translator
from deep_translator import GoogleTranslator

def Padding(txt,num=20):
    F = "{: <"+ str(num) + "}"
    return (F.format(txt))

#print(PaddingTuples(("ciao",10),("pippo",8)))
def PaddingTuples(*args):
    r = ""
    for t in args:
        r += Padding(txt=t[0],num=t[1])
    return r



# Use any translator you like, in this example GoogleTranslator
#translated = GoogleTranslator(source='auto', target='de').translate("keep it up, you are awesome")  # output -> Weiter so, du bist großartig

def Translate(Text):
    return GoogleTranslator(source='auto', target='it').translate(Text)  # output -> Weiter so, du bist großartig