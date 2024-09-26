# Dependencies
from vectors import * 

# Useful Variables
BishopGains = (
    (1,1),
    (1,-1),
    (-1,1),
    (-1,-1)
) # there are offsets for bishops and rooks as well

PiecesThatPin = ("r","q","b")

# Functions

def GeneratePossibleMovesWrapper(GeneratePossibleMoves):
        # Add an argument for no-check generate moves for king 
        def Wrapping(self,Turn, Caching, KingPrune=False, **kwargs):
            if (self.CachedTurn == Turn) and (self.PossibleMoves) and not KingPrune: # caching is ONLY for KingPrune=False
                return self.PossibleMoves
            
            PossibleMoves = GeneratePossibleMoves(self, Turn, KingPrune, **kwargs) # we don't have any kwargs, but just in case

            if KingPrune:
                return PossibleMoves # we ignore checks/caching for kingprune moves (and rest of function is checks/caching)

            # prune King moves in class King
            # prune King Moves: we only want king moves that are NOT on either ray 
            # allow moves which have the piece intercept the ray between King and Enemy (if pinning enemy e.g. K, Q, R and only one attacker)
            # allow moves which take the attacker (if there is only one attacker)

            if (self.GameObject.InCheck): 
                PrunedPossibleMoves = []
                
                if (self.ID[0] == "k"): # prune King moves for only moves that aren't on enemy rays 
                    for PossibleMove in PossibleMoves:
                        ProblemFound = False
                        
                        for EnemyIndex in range(0, len(self.GameObject.PiecesChecking)): # currently checking enemy rays 
                            EnemyPiece = self.GameObject.PiecesChecking[EnemyIndex]
                            nCheckRay = self.GameObject.nCheckRays[EnemyIndex]

                            if (EnemyPiece.ID[0] in PiecesThatPin):
                                if EnemyPiece.CheckOnRay(PossibleMove[0], PossibleMove[1], None, nCheckRay):
                                    ProblemFound = True
                                    break

                        if not ProblemFound:
                            PrunedPossibleMoves.append(PossibleMove)

                elif len(self.GameObject.PiecesChecking) == 1:
                    for PossibleMove in PossibleMoves:
                        EnemyPiece = self.GameObject.PiecesChecking[0]
                        if (PossibleMove[0] == EnemyPiece.PositionX) and (PossibleMove[1] == EnemyPiece.PositionY):
                            PrunedPossibleMoves.append(PossibleMove)

                        if (EnemyPiece.ID[0] in PiecesThatPin) and CheckOnRayFromFixedPosition((EnemyPiece.PositionX, EnemyPiece.PositionY), PossibleMove[0], PossibleMove[1], self.GameObject.CheckRays[0], self.GameObject.nCheckRays[0]):
                            PrunedPossibleMoves.append(PossibleMove)

                PossibleMoves = PrunedPossibleMoves
            
            if Caching:
                self.CachedTurn = Turn
                self.PossibleMoves = PossibleMoves 
            
            return PossibleMoves

        return Wrapping

# Object Classes

class BasePiece():
    def __init__(self,GameObject,side,position): #treat white as false, black as true 
        self.Side = side 
        self.PositionX = position[0]
        self.PositionY = position[1]
        self.GameState = GameObject.BoardState
        self.GameObject = GameObject 
        self.CachedTurn = 0
        self.PossibleMoves = None
        self.ID = ""

    def CheckPosition(self, OtherPiece):
        if (self.PositionX == OtherPiece.PositionX) and (self.PositionY == OtherPiece.PositionY):
            return True

    # Checks whether a piece is on self's Direction ray 
    def CheckOnRay(self, PositionX, PositionY, Direction, NormalisedDirection):
        DirectionBetweenPieces = (PositionX - self.PositionX, PositionY - self.PositionY)
        NormalisedDirectionBetweenPieces = FindDirectionVector(DirectionBetweenPieces)

        if VectorsEqual(NormalisedDirection, NormalisedDirectionBetweenPieces): # same direction
            if Direction:
                if SquaredMagnitude(DirectionBetweenPieces) <= SquaredMagnitude(Direction):
                    return True
            else:
                return True

    def FindPieceOfType(self, PieceTypes):
        PieceList = []

        for piece in self.GameState:
            if piece.ID[0] in PieceTypes:
                PieceList.append(piece)

        return PieceList

    def CheckForPin(self): #rooks, queens, bishops can pin 
        if (self.ID[0] == "k"):
            return None, None

        possiblePinningPiece = None # an optimisation since you cannot both be rook-pinned and bishop-pinned 
        differenceVector = None

        OurKing = None

        for king in self.FindPieceOfType(("k")): # Locating our side's King 
            # OPTIMISATION: Cache the King object to reduce computation time
            if (king.Side == self.Side):
                OurKing = king

                differenceVector = (king.PositionX - self.PositionX, king.PositionY - self.PositionY)

                if abs(differenceVector[0]) == abs(differenceVector[1]): #can be pinned by bishop (or queen)
                    possiblePinningPiece = "b" 
                elif (differenceVector[0] == 0) or (differenceVector[1] == 0): #can be pinned by rook (or queen)
                    possiblePinningPiece = "r"

                break
         
        if not possiblePinningPiece:
            return None, None
        
        normalisedDifferenceVector = FindDirectionVector(differenceVector)

        #let's check for pieces inbetween the king, this piece AND attacking piece, piece
        if possiblePinningPiece == "b":
            #note difference vec is from piece (self) to King 

            nDV = Negative(differenceVector)
            nNDV = Negative(normalisedDifferenceVector)

            #technically not "normalised" since mag is not 1
            # must look for an enemy bishop (or queen)

            EnemyBishop = False

            EBDV = None # Enemy Bishop Difference Vector
    
            # OPTIMISATION: With the number of times we call SquaredMagnitude, we should've used a vector class and cached magnitudes

            for PossibleBishop in self.FindPieceOfType(("q","b")):
                if (self.Side != PossibleBishop.Side) and self.CheckOnRay(PossibleBishop.PositionX, PossibleBishop.PositionY, None, nNDV):
                    if EnemyBishop: # we must find the enemy bishop (queen) which is closer; only one possible direction ray 
                        PEBDV = (PossibleBishop.PositionX - self.PositionX, PossibleBishop.PositionY - self.PositionY)

                        if SquaredMagnitude(PEBDV) < SquaredMagnitude(EBDV):
                            EnemyBishop = PossibleBishop
                            EBDV = PEBDV
                    else: 
                        EnemyBishop = PossibleBishop
                        EBDV = (PossibleBishop.PositionX - self.PositionX, PossibleBishop.PositionY - self.PositionY)
                    
                

            if not EnemyBishop:
                return None, None
                
            #We don't need to calculate normalised enemy bishop vector as this is = nNDV

            # Once we have an enemy piece, we now check whether a piece is between (self, king) or (self, bishop)
            # We need to check whether it is on the ray AND is less by providing proper arguments 

            for PossibleInbetweenPiece in self.GameState:
                if (PossibleInbetweenPiece == self) or (PossibleInbetweenPiece == OurKing) or (PossibleInbetweenPiece == EnemyBishop):
                    continue
                    
                # (self, king)
                if self.CheckOnRay(PossibleInbetweenPiece.PositionX, PossibleInbetweenPiece.PositionY, differenceVector, normalisedDifferenceVector):
                    possiblePinningPiece = None
                    break

                # (self, enemybishop)
                if self.CheckOnRay(PossibleInbetweenPiece.PositionX, PossibleInbetweenPiece.PositionY, EBDV, nNDV):
                    possiblePinningPiece = None
                    break

            if possiblePinningPiece: 
                return EBDV, nNDV

        else: # rook pin 
            nDV = Negative(differenceVector)
            nNDV = Negative(normalisedDifferenceVector)

            EnemyRook = False
            ERDV = None 

            for PossibleRook in self.FindPieceOfType(("q","r")):
                if (self.Side != PossibleRook.Side) and self.CheckOnRay(PossibleRook.PositionX, PossibleRook.PositionY, None, nNDV):
                    if EnemyRook:
                        PERDV = (PossibleRook.PositionX - self.PositionX, PossibleRook.PositionY - self.PositionY)

                        if SquaredMagnitude(PERDV) < SquaredMagnitude(ERDV):
                            EnemyRook = PossibleRook
                            ERDV = PERDV
                    else: 
                        EnemyRook = PossibleRook
                        ERDV = (PossibleRook.PositionX - self.PositionX, PossibleRook.PositionY - self.PositionY)
                    
                

            if not EnemyRook:
                return None, None
    
            for PossibleInbetweenPiece in self.GameState:
                if (PossibleInbetweenPiece == self) or (PossibleInbetweenPiece == OurKing) or (PossibleInbetweenPiece == EnemyRook):
                    continue

                if self.CheckOnRay(PossibleInbetweenPiece.PositionX, PossibleInbetweenPiece.PositionY, differenceVector, normalisedDifferenceVector):
                    possiblePinningPiece = None
                    break

                if self.CheckOnRay(PossibleInbetweenPiece.PositionX, PossibleInbetweenPiece.PositionY, ERDV, nNDV):
                    possiblePinningPiece = None
                    break

            if possiblePinningPiece: 
                return ERDV, nNDV

        return None, None

    def CheckPosOnBoard(self,PosX,PosY):
        return (PosX < 8 and PosX > -1) and (PosY < 8 and PosY > -1)
        
    def CheckForAlliedPiece(self,PosX,PosY):
        for piece in self.GameState:
            if (piece.PositionX == PosX) and (piece.PositionY == PosY) and (piece.Side == self.Side):
                return True

    def CheckForEnemyPiece(self,PosX,PosY):
        for piece in self.GameState:
            if (piece.PositionX == PosX) and (piece.PositionY == PosY) and not (piece.Side == self.Side):
                return piece

    def BaseChecks(self,PosX,PosY, Ray, nRay, KingPrune): # add one pin check later
        return self.CheckPosOnBoard(PosX, PosY) and ( (KingPrune and not (self.ID[0] in PiecesThatPin)) or (not self.CheckForAlliedPiece(PosX, PosY)) ) and (KingPrune or ((Ray and (self.CheckOnRay(PosX, PosY, Ray, nRay) or self.CheckOnRay(PosX, PosY, Negative(Ray), Negative(nRay)))) or (not Ray)))

class Knight(BasePiece):
    def __init__(self,gameState,side,position): 
        super().__init__(gameState,side,position)
        self.ID = "n" + side

    @GeneratePossibleMovesWrapper
    def GeneratePossibleMoves(self,turn, KingPrune):
        PossibleMoves = []
        Ray, nRay = None, None

        if not KingPrune:
            Ray, nRay = self.CheckForPin()

        for x in range(-2,3): 
            if not (x == 0):
                y = (abs(x) % 2) + 1

                if self.BaseChecks(self.PositionX + x,self.PositionY + y, Ray, nRay, KingPrune):
                    PossibleMoves.append((self.PositionX + x,self.PositionY + y))

                if self.BaseChecks(self.PositionX + x,self.PositionY - y, Ray, nRay, KingPrune):
                    PossibleMoves.append((self.PositionX + x,self.PositionY - y))

        return PossibleMoves

    def LookForPossibleMove(self, Position):
        for x in range(-2,3): 
            if not (x == 0):
                y = (abs(x) % 2) + 1

                if ((self.PositionX + x) == Position[0]) and (((self.PositionY + y) == Position[1]) or ((self.PositionY - y) == Position[1])):
                    return True

class Bishop(BasePiece):
    def __init__(self,gameState,side,position): 
        super().__init__(gameState,side,position)
        self.ID = "b" + side

    @GeneratePossibleMovesWrapper
    def GeneratePossibleMoves(self,turn, KingPrune):
        PossibleMoves = []
        Ray, nRay = None, None

        if not KingPrune:
            Ray, nRay = self.CheckForPin()

        for gains in BishopGains:
            x,y = self.PositionX, self.PositionY

            while True:
                x = x + gains[0]
                y = y + gains[1]
                
                if self.BaseChecks(x,y, Ray, nRay, KingPrune):
                    PossibleMoves.append((x,y))

                    if self.CheckForEnemyPiece(x,y):
                        break
                else:
                    if KingPrune and self.CheckPosOnBoard(x, y):
                        PossibleMoves.append((x, y))
                        
                    break
        
        return PossibleMoves

    def LookForPossibleMove(self, Position):
        for gains in BishopGains:
            x,y = self.PositionX, self.PositionY

            while True:
                x = x + gains[0]
                y = y + gains[1]
                
                if self.BaseChecks(x,y, None, None, True):
                    if (x == Position[0]) and (y == Position[1]):
                            return True

                    if self.CheckForEnemyPiece(x,y):
                        break
                else:
                    break
            
class Queen(BasePiece):
    def __init__(self,gameState,side,position): 
        super().__init__(gameState,side,position)
        self.ID = "q" + side

    @GeneratePossibleMovesWrapper
    def GeneratePossibleMoves(self,turn, KingPrune):
        PossibleMoves = []
        Ray, nRay = None, None

        if not KingPrune:
            Ray, nRay = self.CheckForPin()

        for xGain in range(-1, 2):
            for yGain in range(-1, 2):
                if (xGain == 0) and (yGain == 0):
                    continue

                x, y = self.PositionX, self.PositionY

                while True:
                    x = x + xGain
                    y = y + yGain

                    if self.BaseChecks(x,y, Ray, nRay, KingPrune):
                        PossibleMoves.append((x,y))

                        if self.CheckForEnemyPiece(x,y):
                            break
                    else:
                        if KingPrune and self.CheckPosOnBoard(x, y):
                            PossibleMoves.append((x, y))
                            
                        break 

        return PossibleMoves

    def LookForPossibleMove(self, Position): # Used solely for checking for checks i.e. don't care about pins
        for xGain in range(-1, 2):
            for yGain in range(-1, 2):
                if (xGain == 0) and (yGain == 0):
                    continue

                x, y = self.PositionX, self.PositionY

                while True:
                    x = x + xGain
                    y = y + yGain

                    if self.BaseChecks(x,y, None, None, True):
                        if (x == Position[0]) and (y == Position[1]):
                            return True
                        
                        if self.CheckForEnemyPiece(x,y):
                            break
                    else:     
                        break 

class King(BasePiece):
    def __init__(self,gameState,side,position): 
        super().__init__(gameState,side,position)
        self.ID = "k" + side
        self.CanCastle = True

    @GeneratePossibleMovesWrapper
    def GeneratePossibleMoves(self,turn, KingPrune):
        # SPECIAL FOR KING: Must purge all moves that put you into the path of an enemy 
        # SPECIAL: Castling | CanCastle, Free path inbetween (rays), no enemy moves, no check, no kingprune, O-O vs O-O-O
        PossibleMoves = []

        Ray, nRay = None, None # the king can't be pinned

        for x in range(-1,2):
            for y in range(-1,2):
                if (x == 0) and (y == 0): 
                    continue

                if self.BaseChecks(self.PositionX + x, self.PositionY + y, Ray, nRay, KingPrune):
                    PossibleMoves.append((self.PositionX + x, self.PositionY + y))
        
        if KingPrune:
            return PossibleMoves

        PrunedList = []
        EnemyMoves = []

        for EnemyPiece in self.GameState:
            if EnemyPiece.Side != self.Side:
                EnemyPossibleMoves = EnemyPiece.GeneratePossibleMoves(turn+1, False, KingPrune=True) 
                
                for EnemyMove in EnemyPossibleMoves:
                    for PossibleMove in PossibleMoves:
                        if VectorsEqual(PossibleMove, EnemyMove):
                            PossibleMoves.remove(PossibleMove)
                            break

        PrunedList = PossibleMoves
        
        # Castling
        if (not self.GameObject.InCheck) and self.CanCastle:
            for Rook in self.FindPieceOfType(("r")):
                if Rook.CanCastle and (self.PositionY == Rook.PositionY): # don't want newly promoted rook to be mistaken 
                    Difference = Rook.PositionX - self.PositionX
                    Polarity = (Difference > 0) # True is positive/lead-from-King, False is negative/lead-from-Rook
                    
                    PositiveUnit = (Polarity and 1) or -1 

                    StartX = self.PositionX + PositiveUnit
                    UpperLimitX = int(Rook.PositionX)
                    StepX = PositiveUnit

                    SquaresInbetween = [x for x in range(StartX, UpperLimitX, StepX)]
                    Cancelled = False

                    for OtherPiece in self.GameState:
                        if (not (OtherPiece == self)) and (not (OtherPiece == Rook)):
                            if (OtherPiece.PositionX in SquaresInbetween) and (OtherPiece.PositionY == self.PositionY): # could have used raycasting
                                Cancelled = True 
                                break

                    if Cancelled:
                        continue

                    for EnemyMove in EnemyMoves:
                        if (EnemyMove[1] == self.PositionY):
                            for Square in SquaresInbetween:
                                if (EnemyMove[0] == Square):
                                    Cancelled = True
                                    break

                            if Cancelled:
                                break

                    if not Cancelled:
                        PrunedList.append((self.PositionX + (2 * PositiveUnit), self.PositionY))
                            
        PossibleMoves = PrunedList

        return PossibleMoves

class Pawn(BasePiece):
    def __init__(self,gameState,side,position): 
        super().__init__(gameState,side,position)
        self.ID = "p" + side

        if self.Side == "l":
            self.PositiveUnit = 1 # PositiveUnit -> direction going forward for the pawn 
            self.InitialSquare = 1
        else:
            self.PositiveUnit = -1 
            self.InitialSquare = 6

    @GeneratePossibleMovesWrapper
    def GeneratePossibleMoves(self,turn, KingPrune):
        # Add pawn promotion functionality 
        PossibleMoves = []
        Ray, nRay = None, None

        if not KingPrune:
            Ray, nRay = self.CheckForPin()

        if self.BaseChecks(self.PositionX,self.PositionY + self.PositiveUnit, Ray, nRay, KingPrune) and not self.CheckForEnemyPiece(self.PositionX, self.PositionY + self.PositiveUnit): #check move forward
            if not KingPrune:
                PossibleMoves.append((self.PositionX, self.PositionY + self.PositiveUnit))

            if (self.PositionY == self.InitialSquare) and self.BaseChecks(self.PositionX, self.PositionY + (self.PositiveUnit*2), Ray, nRay, KingPrune) and not self.CheckForEnemyPiece(self.PositionX, self.PositionY + (self.PositiveUnit*2)): #check move 2 forward
                if not KingPrune:
                    PossibleMoves.append((self.PositionX, self.PositionY + (self.PositiveUnit*2)))
            
        EnPassantTurn = self.GameObject.EnPassantTurn
        EnPassantPiece = self.GameObject.EnPassantPiece

        for x in (-1,1):
            if self.BaseChecks(self.PositionX + x,self.PositionY + self.PositiveUnit, Ray, nRay, KingPrune): #check for captures and en passant
                if KingPrune:
                    PossibleMoves.append((self.PositionX + x, self.PositionY + self.PositiveUnit))
                else:
                    if (EnPassantTurn == turn) and (EnPassantPiece.Side != self.Side): #en-passant
                        if (EnPassantPiece.PositionY == self.PositionY) and ((EnPassantPiece.PositionX == (self.PositionX + x))):
                            PossibleMoves.append((self.PositionX + x, self.PositionY + self.PositiveUnit))

                    if self.CheckForEnemyPiece(self.PositionX + x, self.PositionY + self.PositiveUnit): #taking normally
                        PossibleMoves.append((self.PositionX + x, self.PositionY + self.PositiveUnit))

        return PossibleMoves

    def LookForPossibleMove(self, Position):
        for x in (-1, 1):
            if ((self.PositionX + x) == Position[0]) and ((self.PositionY + self.PositiveUnit) == Position[1]):
                return True

    def TriggerEnPassant(self,turn):
        if self.Side == "l":
            self.GameObject.EnPassantTurn = turn
        else:
            self.GameObject.EnPassantTurn = turn + 1

        self.GameObject.EnPassantPiece = self

class Rook(BasePiece):
    def __init__(self,gameState,side,position): 
        super().__init__(gameState,side,position)
        self.ID = "r" + side
        self.CanCastle = True

    @GeneratePossibleMovesWrapper
    def GeneratePossibleMoves(self,turn, KingPrune):
        PossibleMoves = []
        Ray, nRay = None, None

        if not KingPrune:
            Ray, nRay = self.CheckForPin()
            
        for xGain in (-1,1):
            x = self.PositionX

            while True:
                x = x + xGain
                if self.BaseChecks(x,self.PositionY, Ray, nRay, KingPrune):
                    PossibleMoves.append((x,self.PositionY))

                    if self.CheckForEnemyPiece(x,self.PositionY):
                        break
                else:
                    if KingPrune and self.CheckPosOnBoard(x, self.PositionY):
                        PossibleMoves.append((x, self.PositionY))

                    break
        
        for yGain in (-1,1):
            y = self.PositionY

            while True:
                y = y + yGain
                if self.BaseChecks(self.PositionX,y, Ray, nRay, KingPrune):
                    PossibleMoves.append((self.PositionX,y))

                    if self.CheckForEnemyPiece(self.PositionX,y):
                        break
                else:
                    if KingPrune and self.CheckPosOnBoard(self.PositionX, y):
                        PossibleMoves.append((self.PositionX, y))
                        
                    break

        return PossibleMoves

    def LookForPossibleMove(self, Position):
        for xGain in (-1,1):
            x = self.PositionX

            while True:
                x = x + xGain
                if self.BaseChecks(x,self.PositionY, None, None, True):
                    if (x == Position[0]) and (self.PositionY == Position[1]):
                        return True

                    if self.CheckForEnemyPiece(x,self.PositionY):
                        break
                else:
                    break
        
        for yGain in (-1,1):
            y = self.PositionY

            while True:
                y = y + yGain
                if self.BaseChecks(self.PositionX,y, None, None, True):
                    if (self.PositionX == Position[0]) and (y == Position[1]):
                        return True

                    if self.CheckForEnemyPiece(self.PositionX,y):
                        break
                else:
                    break
        
# References ObjectClasses for easy instancing w/ variables

PieceMappings = {
    "n":Knight,
    "p":Pawn,
    "r":Rook,
    "k":King,
    "q":Queen,
    "b":Bishop
}
