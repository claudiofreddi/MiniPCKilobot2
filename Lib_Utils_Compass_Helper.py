# ----------------------------------------------------------------
#   UTILITA'
# ----------------------------------------------------------------
                

class CompassHelper:
    
    def IsAngleReached(CompassAngle,CompassToReach):
        print(str(CompassAngle) + ' -> ' + str(CompassToReach))
        SliceHalfSize = 5
        Anglefrom = CompassToReach - SliceHalfSize
        Angleto = CompassToReach + SliceHalfSize
        if (Anglefrom<0):
            #0
            #-10  +10
            #350  10
            Anglefrom = 360 - Anglefrom
            print(str(Anglefrom) + ' <-> ' + str(Angleto))
            return (CompassAngle>=Anglefrom or CompassAngle<=Angleto)

        elif (Angleto>360):
            #360
            #350  370
            #350  10 
            Angleto = Angleto - 360
            print(str(Anglefrom) + ' <-> ' + str(Angleto))
            return (CompassAngle>=Anglefrom or CompassAngle<=Angleto)
        else:
            #40
            #20 50
            print(str(Anglefrom) + ' <-> ' + str(Angleto))
            return (CompassAngle>=Anglefrom and CompassAngle<=Angleto)
        
    def BestRotationDir(CompassAngle,CompassToReach):
        #ang01 = CompassAngle - CompassAngle
        ang02 = CompassToReach - CompassAngle
        if (ang02 < 0):
            ang02 = ang02 + 360
        if (ang02 <= 180):
            return 1
        else:
            return -1
        
    def GetRotationDistance(CompassAngle,CompassToReach):
        ang02 = CompassToReach - CompassAngle
        if (ang02 < 0):
            ang02 = ang02 + 360
        return abs(ang02)

