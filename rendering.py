# Dependencies 
import pygame as Flav

# Used for loading pieces 
chessPieceFiles = (
    "r",
    "q",
    "k",
    "n",
    "p",
    "b"
)

# Main Class

class Rendering():
    ChessPieceImages = {} 

    Screen = None
    Centre = (250,250) # Alternate way of handling class instances getting properties from classes 
    DecScr = 1 # What decimal (like percentage) of Screen is used
    DecPiece = 1 # What decimal of the square is used for the piece image 

    TopLeft = (0,0)
    BottomRight = (0,0)

    SquareSize = (1,1)
    SquareLightColour = (245,241,228)
    SquareDarkColour = (149,55,55) 

    MarkerColour = (127,127,127)
    MarkerRadius = 8

    RenderingChange = True # if RenderingChange then render (again)

    Markers = [] #for rendering

    def LoadPiece(self,index,key):
        self.ChessPieceImages[index] = Flav.image.load(key)
        self.ChessPieceImages[index] = Flav.transform.scale(self.ChessPieceImages[index],(self.DecPiece * self.SquareSize[0], self.DecPiece * self.SquareSize[1]))

        return self.ChessPieceImages[index]

    
    def DrawPiece(self,positionX,positionY,pieceName):
        if self.ChessPieceImages[pieceName]:
            self.Screen.blit(self.ChessPieceImages[pieceName],(positionX,positionY))

    def DrawImageAtCoords(self,coords,imageID):
        self.DrawPiece(self.TopLeft[0] + (coords[0] *self.SquareSize[0]) + ((1-self.DecPiece)/2 * self.SquareSize[0]), self.TopLeft[1] + ((7 - coords[1]) * self.SquareSize[1])  + ((1-self.DecPiece)/2 * self.SquareSize[1]),imageID)

    def DrawMarker(self,coords):
        Flav.draw.circle(self.Screen,self.MarkerColour,(self.TopLeft[0] + ((coords[0] + 0.5) * self.SquareSize[0]), self.TopLeft[1] + ((7.5 - coords[1]) * self.SquareSize[1])),self.MarkerRadius)
        
    def FullRenderBoard(self,boardState):
        self.Screen.fill((115,147,179))

        for x in range(8):
            for y in range(8):
                colour = (x + y + 1) % 2
                colourTuple = (colour and self.SquareLightColour) or self.SquareDarkColour
            
                Flav.draw.rect(self.Screen,colourTuple,(self.TopLeft[0] + (x *self.SquareSize[0]),self.TopLeft[1] + (y *self.SquareSize[1]),self.SquareSize[0],self.SquareSize[1]))

        for piece in boardState:
            if not (piece == None):
                self.DrawImageAtCoords((piece.PositionX,piece.PositionY),piece.ID)

        for move in self.Markers:
            self.DrawMarker((move[0],move[1]))

    def initialise(self):
        for thing in chessPieceFiles: # just preparing image assets
            self.LoadPiece(thing + "l","ChessPieces\chess_" + thing + "l.png")
            self.LoadPiece(thing + "d","ChessPieces\chess_" + thing + "d.png")    

    def __init__(self,screen=None,screenSize=[800, 800], centreOfChessBoard = None,decimalScreen = None,decimalPieceFromSquare = None):
        self.Screen = screen or Flav.display.set_mode(screenSize)
        self.Centre = centreOfChessBoard or (screenSize[0]/2,screenSize[1]/2)
        self.DecScr = decimalScreen
        self.DecPiece = decimalPieceFromSquare

        self.TopLeft = (self.Centre[0] - (self.DecScr * screenSize[0]/2), self.Centre[1] - (self.DecScr * screenSize[1]/2)) # Use DecScr, Centre, screenSize to calculate where we should put TopLeft
        self.BottomRight = (self.Centre[0] + (self.DecScr * screenSize[0]/2), self.Centre[1] + (self.DecScr * screenSize[1]/2))
        self.SquareSize = (self.DecScr * screenSize[0]/8,self.DecScr * screenSize[1]/8)
