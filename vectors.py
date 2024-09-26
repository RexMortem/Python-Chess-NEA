# Helper library for vectors because I use way too many vector functions in different files 

def VectorsEqual(a, b):
    if (a[0] == b[0]) and (a[1] == b[1]):
        return True


def SquaredMagnitude(a): # More performant to use this versus magnitude due to sqrt 
    return (a[0] * a[0]) + (a[1] * a[1])

def Negative(a):
    return (-1 * a[0], -1 * a[1])

def FindDirectionVector(a): # not completely normalised
    x = 0
    y = 0

    if a[0] != 0:
        x = a[0]/abs(a[0])
        y = a[1]/abs(a[0])
    elif a[1] != 0:
        x = a[0]/abs(a[1])
        y = a[1]/abs(a[1])

    return (x, y)
    #return (((a[0] == 0) and 0) or (a[0]/abs(a[0])), ((a[1] == 0) and 0) or (a[1]/abs(a[1])))

def RayComponentMagnitude(a): # for handling rays of form (0, a) or (a, 0)
    return ((a[0] == 0) and abs(a[1])) or abs(a[0])

def CheckOnRayFromFixedPosition(FixedPosition, PositionX, PositionY, Direction, NormalisedDirection):
    DirectionBetweenPieces = (PositionX - FixedPosition[0], PositionY - FixedPosition[1])
    NormalisedDirectionBetweenPieces = FindDirectionVector(DirectionBetweenPieces)

    if VectorsEqual(NormalisedDirection, NormalisedDirectionBetweenPieces): # same direction
        if Direction:
            if SquaredMagnitude(DirectionBetweenPieces) <= SquaredMagnitude(Direction):
                return True
        else:
            return True

def PointWithinRectangle(PointX, PointY, RectangleX, RectangleY, Width, Height):
    if (PointX >= RectangleX) and (PointX <= (RectangleX + Width)): # within the X part of rectangle
        if (PointY >= RectangleY) and (PointY <= (RectangleY + Height)):
            return True