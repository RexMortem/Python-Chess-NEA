# Dependencies
import random
import game
import rendering
import pygame as flav 

import timeit

# Object Classes

class BaseAI(): # should be able to GenerateMove, given boardstate 
    def __init__(self, GameInstance=None, Side="d"):
        self.Side = Side
        self.GameInstance = GameInstance
    
    def PlayItself(self):
        NewRendering = rendering.Rendering(flav, decimalScreen = 0.8, decimalPieceFromSquare = 0.9)
        self.GameInstance = game.Game()
        
        NewRendering.initialise()

        while True:
            self.GameInstance.ResetBoard()

            while self.GameInstance.Completed != True:
                OurMove = self.GenerateMove()
                self.GameInstance.MakeMove(OurMove[0], OurMove[1])
                print("turn no:", self.GameInstance.Turn)
                NewRendering.FullRenderBoard(self.GameInstance.BoardState)

                flav.display.flip()
                flav.time.delay(50)

            print("turn no [COMPLETE]:", self.GameInstance.Turn)
            flav.time.delay(500)

class RandomMoves(BaseAI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def GenerateMove(self):
        PossiblePieces = self.GameInstance.BoardState
        PossibleMoveBigTable = []

        for Piece in PossiblePieces:
            if Piece.Side == self.GameInstance.Side:
                PossibleMoves = Piece.GeneratePossibleMoves(self.GameInstance.Turn, True)
                
                for Move in PossibleMoves:
                    PossibleMoveBigTable.append((Piece, Move))
        
        if len(PossibleMoveBigTable) == 0:
            print("ai recognises win/defeat/draw")
            return

        OurSelection = PossibleMoveBigTable[random.randint(0, len(PossibleMoveBigTable)-1)]
        return OurSelection[0], OurSelection[1]

class MinMax(BaseAI):
    def __init__(self, Depth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.MaxDepth = Depth 
    
    def StaticEvaluation(self, GameInstance):
        Valuations = {
            "p":1,
            "n":3,
            "b":3,
            "r":5,
            "q":9
        }
        PossiblePieces = GameInstance.BoardState

        Valuation = 0

        for Piece in PossiblePieces:
            if Piece.ID[0] in Valuations:
                if Piece.Side == "l":
                    Valuation += Valuations[Piece.ID[0]]
                else:
                    Valuation -= Valuations[Piece.ID[0]]
        
        return Valuation

    def GoDeeper(self, Depth, Maxing, Aggregates, Alpha= -9999, Beta= 9999):
        if Depth == self.MaxDepth:
            t1 = timeit.default_timer()
            returns = self.StaticEvaluation(self.GameInstance)

            Aggregates[0] += timeit.default_timer() - t1
            return returns

        CurrentSide = (Maxing and "l") or "d"
        BestEvaluation = (Maxing and -9999) or 9999
        BestMoves = []

        t1 = timeit.default_timer()
        IterateThrough = self.GameInstance.DuplicateBoardState()

        Aggregates[1] += timeit.default_timer() - t1

        for Piece in IterateThrough:
            if Piece.Side == CurrentSide:
                t1 = timeit.default_timer()
                PossibleMoves = Piece.GeneratePossibleMoves(self.GameInstance.Turn, False)

                Aggregates[2] += timeit.default_timer() - t1

                for PossibleMove in PossibleMoves:
                    #print("Considering Move: ",Piece.ID," to ", game.ConvertSquareToNotation(PossibleMove), " at ", Depth)
                    
                    t1 = timeit.default_timer()
                    Valuation = self.GameInstance.MakeMove(Piece, PossibleMove, Aggregates)

                    Aggregates[3] += timeit.default_timer() - t1

                    if Valuation:
                        if Valuation == "s":
                            Valuation = 0
                    else:
                        Valuation = self.GoDeeper(Depth + 1, not Maxing, Aggregates)

                    t1 = timeit.default_timer()
                    self.GameInstance.UndoMove()

                    Aggregates[4] += timeit.default_timer() - t1
                    
                    if (Maxing and (Valuation > BestEvaluation)) or ((not Maxing) and (Valuation < BestEvaluation)):
                        BestEvaluation = Valuation
                        BestMoves = [(Piece, PossibleMove)]

                        #if (Maxing):
                          #  Alpha = max(Alpha, BestEvaluation)
                        #else:
                         #   Beta = min(Beta, BestEvaluation)

                        #if (Beta <= Alpha):
                         #   print("pruning")
                         #   break
                    elif Valuation == BestEvaluation:
                        BestMoves.append((Piece, PossibleMove))

        if Depth == 1:
            return BestEvaluation, BestMoves[random.randint(0, len(BestMoves)-1)]
        else:
            return BestEvaluation
            
        
    def GenerateMove(self):
        t1 = timeit.default_timer()

        Benchmark = [0,0,0,0,0,0,0,0,0,0,0,0]

        if self.GameInstance.Completed: 
            return None
        
        Return = self.GoDeeper(1, self.GameInstance.Side == "l", Benchmark)

        t2 = timeit.default_timer()

        print("Static: ", Benchmark[0])
        print("Duplication: ", Benchmark[1])
        print("Generate Possible Moves: ", Benchmark[2])
        print("MakeMove: ", Benchmark[3])
        print("UndoMove: ", Benchmark[4])

        for i in range(5, 12):
            print(F"MakeMove {i} : {Benchmark[i]}")

        print("Ev: ", Return[0], "time: ", t2 - t1)
        return Return[1]

# Mapping since only one object is needed (singleton) at a time in our code (only one game is played at once)
AIMappings = {
    "Geg":RandomMoves(),
    "MrFlav":MinMax(4)
}