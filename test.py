
def Padding(txt,num=40):
    F = "{: <"+ str(num) + "}"
    return (F.format(txt))

print(Padding("Ciao",10) + "pippo")