# Dependencies
import pygame as Flav
import UI
import sound as Sound
import chessgame as ChessGame
import music as Music

# Initialisation of modules 
Flav.init()
Sound.init()
ChessGame.init()

# Main variables 
Screen = Flav.display.set_mode((500, 500))

Running = True
BotMusic, MenuPlaylist, SelfPlaylist = None, None, None # will be initialised at the bottom 

# Start Menu Form

StartForm = UI.Form("Startup")
StartForm.BackgroundColour=(99, 197, 218)

StartHeaderLabel = UI.TextLabel()
StartHeaderLabel.Text = "Chess"
StartHeaderLabel.Position= (180, 20)
StartHeaderLabel.BackgroundColour = (99, 197, 218)

VersionLabel = UI.TextLabel()
VersionLabel.Text = "Chess v1"
VersionLabel.TextSize = 12
VersionLabel.Position = (445, 480)
VersionLabel.Size = (45, 20)
VersionLabel.BackgroundColour = (99, 197, 218)

BotSelectionButton = UI.TextLabel()
BotSelectionButton.Text = "Choose Bot"
BotSelectionButton.Position = (135, 220)
BotSelectionButton.Size = (200, 70)
BotSelectionButton.OutlineColour = (239, 239, 239)
BotSelectionButton.OutlineSize = 4
BotSelectionButton.BackgroundColour = (124, 124, 124)

ExitButton = UI.TextLabel()
ExitButton.Text = "Exit"
ExitButton.Position = (135, 310)
ExitButton.Size = (200, 70)
ExitButton.OutlineColour = (239, 239, 239)
ExitButton.OutlineSize = 4
ExitButton.BackgroundColour = (124, 124, 124)

StartForm.AddEntity(StartHeaderLabel)
StartForm.AddEntity(BotSelectionButton)
StartForm.AddEntity(ExitButton)
StartForm.AddEntity(VersionLabel)

# Choose Bot Form

ChooseForm = UI.Form("Bot Selection")
ChooseForm.BackgroundColour = (99, 197, 218)

ChooseHeaderLabel = UI.TextLabel()
ChooseHeaderLabel.Text = "Bot Selection"
ChooseHeaderLabel.Position= (180, 20)
ChooseHeaderLabel.BackgroundColour = (99, 197, 218)

RandomMoverButton = UI.TextLabel()
RandomMoverButton.Text = "Random Mover"
RandomMoverButton.Position = (105, 150)
RandomMoverButton.Size = (250, 70)
RandomMoverButton.OutlineColour = (239, 239, 239)
RandomMoverButton.OutlineSize = 4
RandomMoverButton.BackgroundColour = (124, 124, 124)

MinMaxButton = UI.TextLabel()
MinMaxButton.Text = "Mr Flav"
MinMaxButton.Position = (105, 240)
MinMaxButton.Size = (250, 70)
MinMaxButton.OutlineColour = (239, 239, 239)
MinMaxButton.OutlineSize = 4
MinMaxButton.BackgroundColour = (124, 124, 124)

PlaySelfButton = UI.TextLabel()
PlaySelfButton.Text = "Play Yourself"
PlaySelfButton.Position = (105, 330)
PlaySelfButton.Size = (250, 70)
PlaySelfButton.OutlineColour = (239, 239, 239)
PlaySelfButton.OutlineSize = 4
PlaySelfButton.BackgroundColour = (124, 124, 124)

ChooseBackButton = UI.TextLabel()
ChooseBackButton.Text = "Back"
ChooseBackButton.TextSize = 25
ChooseBackButton.Position = (10, 445)
ChooseBackButton.Size = (60, 45)
ChooseBackButton.OutlineColour = (239, 239, 239)
ChooseBackButton.OutlineSize = 4
ChooseBackButton.BackgroundColour = (124, 124, 124)

ChooseForm.AddEntity(ChooseHeaderLabel)
ChooseForm.AddEntity(RandomMoverButton)
ChooseForm.AddEntity(MinMaxButton)
ChooseForm.AddEntity(ChooseBackButton)
ChooseForm.AddEntity(PlaySelfButton)
ChooseForm.AddEntity(VersionLabel) # Notice that we're able to re-use the VersionLabel from the StartForm

# Game Form

GameForm = UI.App("Game")

GameForm.RenderFunction = ChessGame.Render 
GameForm.EventFunction = ChessGame.ProcessEvents

GameBackButton = UI.TextLabel()
GameBackButton.Text = "Back"
GameBackButton.TextSize = 15
GameBackButton.Position = (10, 465)
GameBackButton.Size = (40, 25)
GameBackButton.OutlineColour = (239, 239, 239)
GameBackButton.OutlineSize = 4
GameBackButton.BackgroundColour = (124, 124, 124)

GameForm.AddEntity(GameBackButton)

# Victory Form

VictoryForm = UI.Form("Victory")
VictoryForm.BackgroundColour = (241, 241, 241)

VictoryHeaderLabel = UI.TextLabel()
VictoryHeaderLabel.Text = "Congratulations!"
VictoryHeaderLabel.TextColour = (241, 241, 241)
VictoryHeaderLabel.Position= (0,0)
VictoryHeaderLabel.Size = (500, 100)
VictoryHeaderLabel.BackgroundColour = (60, 176, 55)

GameBackToSelectionButton = UI.TextLabel()
GameBackToSelectionButton.Text = "Back To Selection"
GameBackToSelectionButton.TextColour = (241, 241, 241)
GameBackToSelectionButton.Position = (75, 220)
GameBackToSelectionButton.Size = (350, 70)
GameBackToSelectionButton.OutlineColour = (219, 219, 219)
GameBackToSelectionButton.OutlineSize = 4
GameBackToSelectionButton.BackgroundColour = (124, 124, 124)

VictoryForm.AddEntity(VictoryHeaderLabel)
VictoryForm.AddEntity(GameBackToSelectionButton)

# Defeat Form

DefeatForm = UI.Form("Defeat")
DefeatForm.BackgroundColour = (241, 241, 241)

DefeatHeaderLabel = UI.TextLabel()
DefeatHeaderLabel.Text = "Defeat"
DefeatHeaderLabel.TextColour = (241, 241, 241)
DefeatHeaderLabel.Position= (0,0)
DefeatHeaderLabel.Size = (500, 100)
DefeatHeaderLabel.BackgroundColour = (144, 13, 9)

DefeatForm.AddEntity(DefeatHeaderLabel)
DefeatForm.AddEntity(GameBackToSelectionButton)

# Connections - Start Menu

def OnBotSelectionClick(self, Event):
    UI.SetCurrentForm(ChooseForm)

def ExitClick(self, Event):
    global Running
    Running = False

def OnButtonMouseEnter(self): # Note this (and OnButtonMouseLeave) can be re-used for several events in several objects
    self.BackgroundColour = (159, 159, 159)

def OnButtonMouseLeave(self):
    self.BackgroundColour = (124, 124, 124)

BotSelectionButton.Connect("OnClick", OnBotSelectionClick)
BotSelectionButton.Connect("OnMouseEnter", OnButtonMouseEnter)
BotSelectionButton.Connect("OnMouseLeave", OnButtonMouseLeave)

ExitButton.Connect("OnClick", ExitClick)
ExitButton.Connect("OnMouseEnter", OnButtonMouseEnter)
ExitButton.Connect("OnMouseLeave", OnButtonMouseLeave)


# Connections - Bot-Selection Menu

def InitialiseChessGame(Opponent):
    ChessGame.Start(Opponent, Screen, (500, 500))
    UI.SetCurrentForm(GameForm)

def ExitChessGame():
    Music.SwitchPlaylist(MenuPlaylist)

def SwitchToRandomMover(self, Event):
    InitialiseChessGame("Geg")
    Music.SwitchPlaylist(BotMusic["Geg"])

def SwitchToMinMax(self, Event):
    InitialiseChessGame("MrFlav")
    Music.SwitchPlaylist(BotMusic["MrFlav"])

def SwitchToSelf(self, Event):
    InitialiseChessGame("")
    Music.SwitchPlaylist(SelfPlaylist)

def BackToStart(self, Event):
    UI.SetCurrentForm(StartForm)

RandomMoverButton.Connect("OnClick", SwitchToRandomMover)
RandomMoverButton.Connect("OnMouseEnter", OnButtonMouseEnter)
RandomMoverButton.Connect("OnMouseLeave", OnButtonMouseLeave)

MinMaxButton.Connect("OnClick", SwitchToMinMax)
MinMaxButton.Connect("OnMouseEnter", OnButtonMouseEnter)
MinMaxButton.Connect("OnMouseLeave", OnButtonMouseLeave)

PlaySelfButton.Connect("OnClick", SwitchToSelf)
PlaySelfButton.Connect("OnMouseEnter", OnButtonMouseEnter)
PlaySelfButton.Connect("OnMouseLeave", OnButtonMouseLeave)

ChooseBackButton.Connect("OnClick", BackToStart)
ChooseBackButton.Connect("OnMouseEnter", OnButtonMouseEnter)
ChooseBackButton.Connect("OnMouseLeave", OnButtonMouseLeave)

# Connections - Game Form
def Victory():
    UI.SetCurrentForm(VictoryForm)

def Defeat():
    UI.SetCurrentForm(DefeatForm)

def BackToSelection(self, Event):
    UI.SetCurrentForm(ChooseForm)
    ExitChessGame()

def EventProcess(self, ReturnArg):
    if ReturnArg == "Victory":
        Victory()
    elif ReturnArg == "Defeat":
        Defeat()

GameForm.Connect("EventProcessed", EventProcess)
GameBackButton.Connect("OnClick", BackToSelection)
GameBackButton.Connect("OnMouseEnter", OnButtonMouseEnter)
GameBackButton.Connect("OnMouseLeave", OnButtonMouseLeave)

# Connections - Victory Screen

GameBackToSelectionButton.Connect("OnClick", BackToSelection)
GameBackToSelectionButton.Connect("OnMouseEnter", OnButtonMouseEnter)
GameBackToSelectionButton.Connect("OnMouseLeave", OnButtonMouseLeave)

# Music Asset Load

Music.MassPreloadSongs((
    ("Happy", "CantinaBandSource.mp3"),
    ("Tunes", "tunes.mp3"),
    ("Lobby", "ElevatorMusic.mp3"),
    ("Death", "TheOnlyThingTheyFearIsYou.mp3"),
    ("Contemplative", "Nocturne.mp3")
))

MenuPlaylist = Music.Playlist(tuple(["Lobby"]))
SelfPlaylist = Music.Playlist(tuple(["Contemplative"]))
BotMusic = {
    "Geg":Music.Playlist(("Tunes","Happy")),
    "MrFlav":Music.Playlist(tuple(["Death"]))
}

# Run Loop

UI.SetCurrentForm(StartForm)
Music.SwitchPlaylist(MenuPlaylist)

while Running:
    
    Events = Flav.event.get()

    for Event in Events:
        if Event.type == Flav.QUIT:
            Running = False
    
    UI.Update(Events)
    UI.Render(Screen)

    Music.Update()
    
    Flav.display.flip()
    Flav.time.delay(50)
