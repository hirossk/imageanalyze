from occvutil import changedH,changedS,changedV

#色相・彩度・明度変換
def convertframe(frame, var):
    #色相変換
    return changedH(frame, var)
    #彩度変換
    #return changedS(frame, 1.0, var)
    #明度変換
    #return changedV(frame, 2.0, var)

