import math
import pygame as flav
import game 
import rendering
import ai
import sound
import music 

selectedPiece = None

def init():
    global newGame, newRendering, CurrentAI # module-level globals (scope NOT shared among all files in program)
    
    newGame = None
    newRendering = None

def VisualisePossibleMoves(piece):
    possibleMoves = piece.GeneratePossibleMoves(newGame.Turn, True)
    newRendering.Markers = []

    for move in possibleMoves:
        newRendering.Markers.append(move)

    newRendering.RenderingChange = True

def ResetSelection():
    global selectedPiece 
    selectedPiece = None

    newRendering.Markers = []
    newRendering.RenderingChange = True

def MakeMove(piece,move):
    global newGame

    ResetSelection()
    Valuation = newGame.MakeMove(piece, move)

    if Valuation:
        if Valuation == "s":
            newGame.CompletedFlag = "Victory"
        elif Valuation == 9999:
            newGame.CompletedFlag = "Victory"
        else:
            newGame.CompletedFlag = "Defeat"

def UndoMove():
    ResetSelection()
    return newGame.UndoMove()

def AIMove():
    print("generating AI move")
    AIMove = CurrentAI.GenerateMove()
    print("post AI generation")

    if AIMove:
        MakeMove(AIMove[0], AIMove[1])
    else:
        print("CHECKMATE")

def selectPiece(mousePos):
    if (mousePos[0] < newRendering.BottomRight[0]) and (mousePos[0] > newRendering.TopLeft[0]) and ((mousePos[1] > newRendering.TopLeft[1]) and (mousePos[1] < newRendering.BottomRight[1])):
        squarePos = (math.floor((mousePos[0] - newRendering.TopLeft[0])/newRendering.SquareSize[0]), 7 - math.floor((mousePos[1] - newRendering.TopLeft[0])/newRendering.SquareSize[1]))
        global selectedPiece

        MoveMade = False

        if selectedPiece: # moving to a square
            for move in newRendering.Markers:
                if (move[0] == squarePos[0]) and (move[1] == squarePos[1]):
                    MakeMove(selectedPiece,move)

                    MoveMade = True

        # selecting a piece 
        if MoveMade:
            newRendering.FullRenderBoard(newGame.BoardState)
            flav.display.flip()

            sound.PlaySound("Move")

            if CurrentAI:   
                AIMove()
        else:
            for piece in newGame.BoardState:
                if (piece.PositionX == squarePos[0]) and (piece.PositionY == squarePos[1]) and (piece.Side == newGame.Side):
                    if piece == selectedPiece:
                        break
                    
                    selectedPiece = piece
                    VisualisePossibleMoves(piece)

                    break

#nl = newGame.GeneratePiece("n", "d", 4, 4)

def DeselectPiece():
    global selectedPiece

    selectedPiece = None
    newRendering.Markers = []
    newRendering.RenderingChange = True

running = True 

# Input Pre-Loop Setup

InputRegister = { # stores a record of CanRegisterInput 
    "RightClick":True,
    "LeftClick":True
}

def RegisterInput(State, InputName):
    if State: # right click
        if InputRegister[InputName]:
            InputRegister[InputName] = False
            return True
    else:
        InputRegister[InputName] = True

# Music Pre-Loop Setup

def History():
    n = 2
    strn = "1"

    for move in newGame.History:
        if ((n % 2) == 0) and strn != "1":
            print(strn)
            strn = str(int(n/2))
        
        strn += " " + move
        n += 1 

    if (n % 2) == 1:
        print(strn)

def Start(Opponent, Screen, ScreenSize):
    # Need to load playlists first (songs already preloaded)
    global CurrentAI, newGame, newRendering
    
    newGame = game.Game()
    newGame.ResetBoard()   
    
    newRendering = rendering.Rendering(screen=Screen, screenSize=ScreenSize, decimalScreen = 0.8, decimalPieceFromSquare = 0.9)
    newRendering.initialise()   

    # Choosing AI
    if Opponent and Opponent in ai.AIMappings:
        CurrentAI = ai.AIMappings[Opponent]
        CurrentAI.GameInstance = newGame
    else:
        CurrentAI = None

def ProcessEvents(self, Events):
    if newGame.CompletedFlag:
        History()
        return newGame.CompletedFlag
    
    for event in Events:     
        if event.type == flav.KEYDOWN: 
            if event.key == flav.K_u:
                UndoMove()

        states = flav.mouse.get_pressed()
        
        if RegisterInput(states[2], "RightClick"):
            DeselectPiece()

        if RegisterInput(states[0], "LeftClick"): 
            selectPiece(flav.mouse.get_pos())
            
def Render(self, Screen):
    if newRendering.RenderingChange: # Rendering
        newRendering.RenderingChange = False

        newRendering.FullRenderBoard(newGame.BoardState)