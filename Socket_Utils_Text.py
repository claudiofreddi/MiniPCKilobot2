
def Padding(txt,num=20):
    F = "{: <"+ str(num) + "}"
    return (F.format(txt))

#print(PaddingTuples(("ciao",10),("pippo",8)))
def PaddingTuples(*args):
    r = ""
    for t in args:
        r += Padding(txt=t[0],num=t[1])
    return r

