# Dependencies
import pieces
import timeit
from vectors import FindDirectionVector, VectorsEqual, RayComponentMagnitude, CheckOnRayFromFixedPosition

# Variables
PiecesThatPin = ("r","q","b")
Ranks = [chr(i) for i in range(97, 97+8)]

MappingCastlingToSquares = {
    "q":(0,7), # black queen-side castling
    "k":(7,7),
    "Q":(0,0),
    "K":(7,0)
}

# Functions 
def ConvertSquareToNotation(Square):
    Position = (Ranks[Square[0]], Square[1]+1)
    return Position[0] + str(int(Position[1]))

def ConvertNotationToSquare(Notation):
    Rank = ord(Notation[0]) - 97
    File = int(Notation[1]) - 1
    return (Rank, File)
    

# Object Classes

class Game():
    def __init__(self):
        self.Completed = False
        self.CompletedFlag = None

    def ClearBoard(self):
        self.Turn = 1
        self.Side = "l"
        self.BoardState = [] # list of pieces, pretty slow v squares 
    
        self.InCheck = False
        self.CheckRays = None
        self.nCheckRays = None
        self.PiecesChecking = None

        self.EnPassantPiece = None
        self.EnPassantTurn = -1

    def DuplicateBoardState(self): # creating new table without manipulation of elements (no messups)
        NewBoardState = []

        for Piece in self.BoardState:
            NewBoardState.append(Piece)

        return NewBoardState

    def CountPermutations(self, depth):
        if (depth == 0):
            return 1

        PermutationCount = 0
        IterateThrough = self.DuplicateBoardState()

        for Piece in IterateThrough:
            #print(Piece)
            if Piece.Side == self.Side:
                for Move in Piece.GeneratePossibleMoves(self.Turn, False):
                    self.MakeMove(Piece, Move)
                    PermutationCount += self.CountPermutations(depth - 1)
                    self.UndoMove()
                    
        return PermutationCount
            
    def ClearState(self):
        self.ClearBoard()

        self.History = []
        self.StateCache = []
        self.Completed = False

    def SaveAsFEN(self):
        FENString = ""
        ChessSquareArray = [False] * 64

        # Loading Piece Positions
        for Piece in self.BoardState:
            SquareIndex = (Piece.PositionY * 8) + Piece.PositionX
            ChessSquareArray[SquareIndex] = Piece.ID[0]

            if Piece.Side == "l":
                ChessSquareArray[SquareIndex] = ChessSquareArray[SquareIndex].upper() # White pieces are capital letters 
        
        nSpaces = 0

        for PotentialPiece in ChessSquareArray: # turn square array into FEN String
            if PotentialPiece != False: # is holding a piece
                if nSpaces > 0:
                    FENString += str(int(nSpaces))
                    nSpaces = 0

                FENString += PotentialPiece

            elif FENString != "": # is not the start
                nSpaces += 1 

        FENString += " "

        # Recording whose side it is
        
        if self.Side == "l":
            FENString += "w"
        else:
            FENString += "b"

        # Castling
        CanCastle = {
            "l":None,
            "d":None
        }

        CastlingString = ""

        for Piece in self.BoardState: # checking whether Kings can castle first 
            if Piece.ID[0] == "k":
                if Piece.CanCastle:
                    CanCastle[Piece.ID[1]] = [] # else remains as None
                else:
                    del CanCastle[Piece.ID[1]]

        for Piece in self.BoardState: # Assigning Symbols 
            if (Piece.ID[0] == "r") and (self.Side in CanCastle) and Piece.CanCastle:
                for Symbol, PotentialPosition in MappingCastlingToSquares.items():
                    if VectorsEqual(PotentialPosition, (Piece.PositionX, Piece.PositionY)):
                        CastlingString += Symbol
                        break
        
        if CastlingString == "":
            FENString += "- "
        else:
            FENString += CastlingString + " "

        # En Passant

        if self.EnPassantTurn == self.Turn:
            UnitToAdd = ((self.EnPassantPiece.Side == "l") and -1) or 1 # for white, target square is one square behind the pawn 
            TargetSquare = (self.EnPassantPiece.PositionX, self.EnPassantPiece.PositionY + UnitToAdd)
            FENString += ConvertSquareToNotation(TargetSquare)
        else:
            FENString += "- "

        # Half-Move Clock

        FENString += " 0 "

        # Turn Number

        FENString += F"{str(self.Turn)}"
        print("FENString: ", FENString)

        return FENString
    
    def LoadFromFEN(self, FENString):
        self.ClearBoard()

        iBoard = 0 # board iterator
        SavedIndex = None

        # Loading board state
        for StringIndex in range(0, len(FENString)):
            if iBoard >= 64: # 63 is last square
                SavedIndex = StringIndex + 1
                break

            Character = FENString[StringIndex]
            lCharacter = Character.lower()

            if lCharacter in pieces.PieceMappings:
                IsWhite = Character.isupper()
                
                x = iBoard % 8
                y = 7 - ((iBoard - x)/8)
                
                self.GeneratePiece(lCharacter, (IsWhite and "l") or "d", int(x), int(y))
            elif (lCharacter == "/") or (lCharacter == " "): # ignore these characters; they don't really mean anything
                continue
            elif int(lCharacter): 
                iBoard += int(lCharacter)
                continue

            iBoard += 1 
           
        if not SavedIndex:
            return # no more data
        
        print("got to loading side", SavedIndex, len(FENString))

        # Loading Side
        NextSavedIndex = None

        for StringIndex in range(SavedIndex, len(FENString)):
            Character = FENString[StringIndex]
            lCharacter = FENString[StringIndex].lower()

            if lCharacter == "w": # Side (White)
                self.Side = "l"
                NextSavedIndex = StringIndex + 2
                break
            elif lCharacter == "b": # Side (Black)
                self.Side = "d"
                NextSavedIndex = StringIndex + 2
                break
            elif lCharacter == "-":
                NextSavedIndex = StringIndex + 2
                break

        if not NextSavedIndex: 
            return
        
        SavedIndex = NextSavedIndex
        NextSavedIndex = None

        CanCastle = {
            "l":[],
            "d":[],
        }

        # Loading castling 
        for StringIndex in range(SavedIndex, len(FENString)):
            Character = FENString[StringIndex]
            lCharacter = FENString[StringIndex].lower()

            if lCharacter == " ": # If no  more info
                NextSavedIndex = StringIndex + 1
                break
            elif (lCharacter == "q") or (lCharacter == "k"): # Castling 
                CanCastle[(Character.isupper() and "l") or "d"].append(Character)

        DeletableSides = [] # removing redundant data 
        for Side in CanCastle.keys():
            if len(CanCastle[Side]) == 0:
                DeletableSides.append(Side)

        for Side in DeletableSides:
            del CanCastle[Side]

        RegisteredRooks = []

        for Piece in self.BoardState: # identifying non-disabling rooks 
            if (Piece.ID[0] == "r") and (Piece.Side in CanCastle):
                for PossibleCastles in CanCastle[Piece.Side]:
                    if VectorsEqual((Piece.PositionX, Piece.PositionY), MappingCastlingToSquares[PossibleCastles]):
                        RegisteredRooks.append(Piece)

        for Piece in self.BoardState: # disabling the rest
            if (Piece.ID[0] == "r") and not (Piece in RegisteredRooks):
                Piece.CanCastle = False

        if not NextSavedIndex:
            return 
        
        SavedIndex = NextSavedIndex
        NextSavedIndex = None

        # En Passant

        for StringIndex in range(SavedIndex, len(FENString)):
            Character = FENString[StringIndex]

            if Character == "-":
                NextSavedIndex = StringIndex + 2
            else:
                TargetSquareString = FENString[StringIndex:StringIndex+2]
                TargetSquare = ConvertNotationToSquare(TargetSquareString)

                for PotentialPiece in self.BoardState:
                    if (PotentialPiece.ID[0] == "p") and (PotentialPiece.PositionX == TargetSquare[0]) and ((PotentialPiece.PositionY == (TargetSquare[1] + 1)) or (PotentialPiece.PositionY == (TargetSquare[1] - 1))):
                        self.EnPassantPiece = PotentialPiece
                        self.EnPassantTurn = self.Turn

                NextSavedIndex = StringIndex + 3
                break

        if not NextSavedIndex:
            return 
        
        SavedIndex = NextSavedIndex
        NextSavedIndex = None

        # Half-Move Clock
        for StringIndex in range(SavedIndex, len(FENString)):
            Character = FENString[StringIndex]

            if Character == "-":
                NextSavedIndex = StringIndex + 2 
                break
            elif Character == " ":
                NextSavedIndex = StringIndex + 1
                break

        if not NextSavedIndex:
            return 
        
        SavedIndex = NextSavedIndex

        # Turn No 
        LeftOverString = FENString[SavedIndex:len(FENString)]
        LeftOverString = LeftOverString.lstrip()
        LeftOverString = LeftOverString.rstrip()
        
        if LeftOverString.isdigit():
            self.Turn = int(LeftOverString)
            self.EnPassantTurn = self.Turn

    def GeneratePiece(self,pieceType,side,positionX,positionY):
        if pieceType in pieces.PieceMappings:
            newPiece = pieces.PieceMappings[pieceType](self,side,(positionX,positionY))
            self.BoardState.append(newPiece)

            return newPiece

    def CapturePiece(self, piece):
        self.BoardState.remove(piece)
    
    def PromotePawn(self, piece, selection):
        NewPiece = self.GeneratePiece(selection, piece.Side, piece.PositionX, piece.PositionY)
        self.BoardState.remove(piece)
    
        return NewPiece
    
    def UndoMove(self):
        if len(self.StateCache) == 0:
            return

        LatestCachedState = self.StateCache[len(self.StateCache) - 1]
        
        self.Side = ((self.Side == "l") and "d") or "l"

        if self.Side == "d":
            self.Turn -= 1 

        if LatestCachedState[0]: # check state
            self.InCheck = True
            self.CheckRays = LatestCachedState[0][0]
            self.nCheckRays = LatestCachedState[0][1]
            self.PiecesChecking = LatestCachedState[0][2]
        else:
            self.InCheck = False

        if LatestCachedState[1]: # en passant OR Castling Disabled
            if LatestCachedState[1][0] == False: # Castling Disabled
                LatestCachedState[1][1].CanCastle = True
            else: # en passant 
                self.EnPassantPiece = LatestCachedState[1][0]
                self.EnPassantTurn = LatestCachedState[1][1]
        
        if LatestCachedState[2]: # captures
            self.BoardState.append(LatestCachedState[2])

        if LatestCachedState[3]: # castling
            LatestCachedState[3][0].PositionX = LatestCachedState[3][1] # Restoring rook position
            LatestCachedState[3][0].PositionY = LatestCachedState[3][2]
            LatestCachedState[3][3].CanCastle = True # Setting King castling rights back

        MovedPiece = LatestCachedState[4][0] # previous move 
        MovedPiece.PositionX = LatestCachedState[4][1]
        MovedPiece.PositionY = LatestCachedState[4][2]

        if LatestCachedState[5]: # replacing piece bc state (remove new piece!!)
            self.BoardState.append(LatestCachedState[5][0])
            self.BoardState.remove(LatestCachedState[5][1])

        for Piece in self.BoardState:
            if Piece.CachedTurn > self.Turn:
                Piece.PossibleMoves = None
                Piece.CachedTurn = -1
        
        self.Completed = False

        self.StateCache.pop()
        self.History.pop()

    def Graphical(self):
        Graphic = []

        for i in range(0, 64):
            Graphic.append(None)

        for piece in self.BoardState:
            Numerical = piece.PositionX + (piece.PositionY*8)
            Representation = ((piece.Side == "l") and piece.ID[0].upper()) or piece.ID[0]
            Graphic[Numerical] = Representation
        
        for y in range(0, 8):
            XString = ""
            for x in range(0, 8):
                XString = XString + " " + (Graphic[(y * 8) + x] or "-")
            
            print(XString)

    def CheckForMate(self, OldPositionData, Aggregates=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0]):
        t1 = timeit.default_timer()

        InCheck = self.KingInCheck(OldPositionData[0], (OldPositionData[1], OldPositionData[2]))
        
        Aggregates[10] += timeit.default_timer() - t1
        t1 = timeit.default_timer()

        ThereAreMoves = False

        for OtherPiece in self.BoardState:
            if OtherPiece.Side == self.Side:
                PossibleMoves = OtherPiece.GeneratePossibleMoves(self.Turn, True)

                if PossibleMoves and len(PossibleMoves) >= 1:
                    ThereAreMoves = True
                    break
        
        Aggregates[11] += timeit.default_timer() - t1

        if not InCheck:
            if not ThereAreMoves:
                #print("STALEMATE")
                self.Completed = True
                return "s"
        elif not ThereAreMoves:
            #print("CHECKMATE")
            self.Completed = True
            return ((self.Side == "l") and -9999) or 9999
        
        if len(self.BoardState) == 2:
            #print("STALEMATE")
            self.Completed = True
            return "s"

    def MakeMove(self, piece, move, Aggregates=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 0]):
        t1 = timeit.default_timer()
        TurnN = ((self.Turn-1)*2 + (((self.Side == "d") and 1) or 0)) # pre-move turn count for removing unneeded state caches 

        if not (len(self.StateCache) == TurnN): # cutting off old future states 
            Mismatch = len(self.StateCache) - TurnN

            for i in range(0, Mismatch):
                self.StateCache.pop()

        Aggregates[5] += timeit.default_timer() - t1
        t1 = timeit.default_timer()

        StateToSave = [] # check states, en passant, captured pieces,  previous move, previous piece (if previously pawn)

        if self.InCheck:
            StateToSave.append((self.CheckRays, self.nCheckRays, self.PiecesChecking)) # check states
        else:
            StateToSave.append(None)

        if piece.ID[0] == "p" and abs(piece.PositionY - move[1]) == 2:
            StateToSave.append((self.EnPassantPiece, self.EnPassantTurn)) # en passant
            piece.TriggerEnPassant(self.Turn)
        else:
            if (piece.ID[0] == "k") or (piece.ID[0] == "r"):
                if piece.CanCastle:
                    piece.CanCastle = False
                    StateToSave.append((False, piece))
                else:
                    StateToSave.append(None)
            else:
                StateToSave.append(None)

        self.Side = ((self.Side == "l") and "d") or "l" # Side state change 

        if self.Side == "l":
            self.Turn += 1 

        Aggregates[6] += timeit.default_timer() - t1
        t1 = timeit.default_timer()
        
        #check for captures
        Capture = None

        if piece.ID[0] == "p" and (not (piece.PositionX == move[0])) and not (piece.CheckForEnemyPiece(move[0],move[1])): #en-passant
            for otherPiece in self.BoardState:
                if (otherPiece.PositionX == move[0]) and (otherPiece.PositionY == (move[1] + (((piece.Side == "l") and -1) or 1))):
                    self.CapturePiece(otherPiece)
                    Capture = otherPiece
        else:
            for otherPiece in self.BoardState:
                if (otherPiece.PositionX == move[0]) and (otherPiece.PositionY == move[1]):
                    self.CapturePiece(otherPiece)
                    Capture = otherPiece

        StateToSave.append(Capture) # captured pieces

        Aggregates[7] += timeit.default_timer() - t1
        t1 = timeit.default_timer()

        #Castling Check
        KingDiff = move[0] - piece.PositionX

        if (piece.ID[0] == "k") and (abs(KingDiff) == 2):
            self.History.append("O-O")
            piece.CanCastle = False

            for Rook in piece.FindPieceOfType("r"): # Castling
                if (Rook.Side == piece.Side) and Rook.CanCastle and (Rook.PositionY == piece.PositionY): 
                    if (((KingDiff > 0) and (Rook.PositionX > piece.PositionX)) or ((KingDiff < 0) and (Rook.PositionX < piece.PositionX))):
                        StateToSave.append((Rook, Rook.PositionX, Rook.PositionY, piece))
                        Rook.PositionX = move[0] + (((KingDiff > 0) and -1) or 1)
                        break
        else:
            StateToSave.append(None)

            if piece.ID[0] == "p":
                self.History.append(ConvertSquareToNotation(move))
            else:
                self.History.append(piece.ID[0] + ConvertSquareToNotation(move))

        PreviousMoveData = (piece, piece.PositionX, piece.PositionY)
        StateToSave.append((PreviousMoveData)) # previous move 
                           
        piece.PositionX = move[0]
        piece.PositionY = move[1]
        
        Aggregates[8] += timeit.default_timer() - t1
        t1 = timeit.default_timer()

        if (piece.ID[0] == "p") and ((move[1] == 7) or (move[1] == 0)):
            OldPiece = piece
            piece = self.PromotePawn(piece, "q")
            PreviousMoveData = (piece, PreviousMoveData[1], PreviousMoveData[2]) # Update piece
            StateToSave.append((OldPiece, piece)) # for undo, remove new piece; add old piece to board
        else:
            StateToSave.append(None)

        Aggregates[9] += timeit.default_timer() - t1
        t1 = timeit.default_timer()

        self.StateCache.append(StateToSave)

        return self.CheckForMate(PreviousMoveData, Aggregates)

    def ResetBoard(self):
        self.ClearState()

        # Generate pawns (light + dark)
        for x in range(8):
            self.GeneratePiece("p","l",x,1)
            self.GeneratePiece("p","d",x,6)

        order = ["r","n","b"]
        
        # Generate rooks, knights, bishops (light + dark)
        for x in range(3):
            pieceType = order[x]

            self.GeneratePiece(pieceType,"l",x,0)
            self.GeneratePiece(pieceType,"l",7 - x,0)
            self.GeneratePiece(pieceType,"d",x,7)
            self.GeneratePiece(pieceType,"d",7 - x,7)
            
        order = ["q","k"]

        # Generate queens, kings (light + dark)
        for x in range(2):
            self.GeneratePiece(order[x],"l",3 + x,0)
            self.GeneratePiece(order[x],"d",3 + x,7)

        
    def AddPieceToCheckList(self, Piece, KingPiece):
        self.PiecesChecking.append(Piece)

        if Piece.ID[0] in PiecesThatPin:
            Ray = (KingPiece.PositionX - Piece.PositionX, KingPiece.PositionY - Piece.PositionY)

            self.CheckRays.append(Ray)
            self.nCheckRays.append(FindDirectionVector(Ray))
        else:
            self.CheckRays.append(0)
            self.nCheckRays.append(0)

    #KingInCheck is called after the enemy's move; set turn to the being checked's side
    def OldKingInCheck(self): # this should trigger once per move OPTIMISATION: over triggering per piece
        kingPiece = None

        for piece in self.BoardState: 
            if (piece.ID[0] == "k") and (piece.Side == self.Side):
                kingPiece = piece
                break
        
        AnyCheckedChecks = False

        for piece in self.BoardState:
            if (not (piece.Side == self.Side)) and not (piece.ID[0] == "k"): #piece that can check
                possibleMoves = piece.GeneratePossibleMoves(self.Turn+1, False, KingPrune=True) # generating moves from the future with same board state

                for possibleMove in possibleMoves:
                    if (possibleMove[0] == kingPiece.PositionX) and (possibleMove[1] == kingPiece.PositionY):
                        if not (AnyCheckedChecks):
                            self.PiecesChecking = []
                            self.CheckRays = []
                            self.nCheckRays = []

                            AnyCheckedChecks = True
                            self.InCheck = True

                        self.AddPieceToCheckList(piece, kingPiece)
        
        if not AnyCheckedChecks:
            self.InCheck = False
            
        return self.InCheck

    def CheckForDiscoveredCheck(self, Piece, EnemyKingPiece, RayType, DiscoveryRay): # NOTE it is currently the enemy's move
        LeastMagnitude = 99
        LeastMagnitudePiece = None

        NormalisedRay = FindDirectionVector(DiscoveryRay)
        DiscoveryRayMagnitude = RayComponentMagnitude(DiscoveryRay)

        for AlliedPiece in self.BoardState:
            if not ((AlliedPiece.Side == Piece.Side) and (AlliedPiece != Piece) and ((AlliedPiece.ID[0] == RayType) or (AlliedPiece.ID[0] == "q"))): # must be allied, correct type
                continue
                
            AllyRay = (EnemyKingPiece.PositionX - AlliedPiece.PositionX, EnemyKingPiece.PositionY - AlliedPiece.PositionY)
            AllyMagnitude = RayComponentMagnitude(AllyRay)

            if not ((NormalisedRay == FindDirectionVector(AllyRay)) and (AllyMagnitude > DiscoveryRayMagnitude)):
                continue 
                
            # check for inbetween pieces
            # could use generate moves but we already have AllyRay, and we know that it's a ray piece can move on

            if AllyMagnitude < LeastMagnitude: 
                LeastMagnitude = AllyMagnitude
                LeastMagnitudePiece = AlliedPiece

        if LeastMagnitudePiece: # the closest piece on the ray to the King 
            NoneInbetween = True

            DiscoveryRay = (EnemyKingPiece.PositionX - LeastMagnitudePiece.PositionX, EnemyKingPiece.PositionY - LeastMagnitudePiece.PositionY)
            Origin = (LeastMagnitudePiece.PositionX, LeastMagnitudePiece.PositionY)

            for InbetweenPiece in self.BoardState:
                if (InbetweenPiece != LeastMagnitudePiece) and (InbetweenPiece != EnemyKingPiece) and CheckOnRayFromFixedPosition(Origin, InbetweenPiece.PositionX, InbetweenPiece.PositionY, DiscoveryRay, NormalisedRay):
                    NoneInbetween = False
                    break

            if NoneInbetween:
                self.InCheck = True
                self.AddPieceToCheckList(LeastMagnitudePiece, EnemyKingPiece)

    def KingInCheck(self, Piece, OldPosition): # Note that this function is called in MakeMove after the turn swaps to the other side: it is the enemy's move
        EnemyKingPiece = None
        self.InCheck = False # Check is assumed to be False since moves MUST stop check (go from InCheck to not InCheck) 

        for EnemyPiece in self.BoardState: # finding the King 
            if (EnemyPiece.Side != Piece.Side) and (EnemyPiece.ID[0] == "k"):
                EnemyKingPiece = EnemyPiece

        self.PiecesChecking = []
        self.CheckRays = []
        self.nCheckRays = []

        if not (Piece.ID[0] == "k"):
            Found = Piece.LookForPossibleMove((EnemyKingPiece.PositionX, EnemyKingPiece.PositionY)) # simple check 

            if Found:
                self.InCheck = True 
                self.AddPieceToCheckList(Piece, EnemyKingPiece)

        # possible discovered check

        DiscoveryRay = (EnemyKingPiece.PositionX - OldPosition[0], EnemyKingPiece.PositionY - OldPosition[1])

        RayType = None

        if (abs(DiscoveryRay[0]) == abs(DiscoveryRay[1])):
            RayType = "b" # bishop
        elif (DiscoveryRay[0] == 0) or (DiscoveryRay[1] == 0):
            RayType = "r" # rook

        if RayType:
            self.CheckForDiscoveredCheck(Piece, EnemyKingPiece, RayType, DiscoveryRay)

        return self.InCheck
            