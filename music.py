# Dependencies
import pygame as flav

# Variables 
Path = "Tunes/" # Folder where we store music (mp3)
CurrentPlaylist = None

# Classes

class Song(): # Song contains the internal pygame sound instance and handles easy importing + storage 
    SongLookup = {}

    def __init__(self, SongName, Query): 
        self.Name = SongName
        self.SongInstance = self.ImportFromFile(Query)

        Song.SongLookup[SongName] = self.SongInstance

    def ImportFromFile(self, FileName):
        return flav.mixer.Sound(Path + FileName)

class Playlist(): # Consists of a number of Songs 
    Playlists = []

    def __init__(self, SongList=None, SongInstances=None):
        self.Songs = []

        if SongList:
            for SongName in SongList:
                if Song.SongLookup[SongName]:
                    self.Songs.append(Song.SongLookup[SongName]) # utilises Song's Songlookup dictionary to make adding songs easier

        if SongInstances: # two ways of adding songs (names and SongInstances)
            if SongList:
                for SongInstance in SongInstances:
                    self.Songs.append(SongInstance)
            else:
                self.Songs = SongInstances

        self.Reset()

    def Reset(self): # sets back to Default state 
        self.LoopCount = 0
        self.NextSongIndex = 0
        self.NextUpdateTime = -1
        self.Playing = False
    
    def Play(self, Loops=1, Volume=1):
        self.Reset()

        self.Playing = True
        self.Loops = Loops
        self.Volume = Volume

        self.Update()

    def Stop(self):
        if (self.NextSongIndex >= 0) and (self.NextSongIndex < len(self.Songs)): # it shouldn't be in an invalid range anyway
            CurrentSongIndex = self.NextSongIndex - 1

            if CurrentSongIndex <= -1:
                CurrentSongIndex = len(self.Songs) - 1

            self.Songs[CurrentSongIndex].stop()

        self.Reset()

    def Update(self): # call this constantly; Playlist will check whether it's time 
        if not self.Playing: 
            return
        
        if (self.LoopCount > self.Loops) and not (self.Loops == -1): # don't play; playlist over
            self.Playing = False
            return

        if (flav.time.get_ticks() < self.NextUpdateTime): # not enough time until next song 
            return
        
        SongInstance = self.Songs[self.NextSongIndex] 
        SongInstance.set_volume(self.Volume)
        SongInstance.play()

        self.NextUpdateTime = flav.time.get_ticks() + (SongInstance.get_length() * 1000)

        self.NextSongIndex += 1 

        if self.NextSongIndex >= len(self.Songs): # loop back to start of playlist
            self.NextSongIndex = 0
            self.LoopCount += 1

# Functions
 
def MassPreloadSongs(SongList): # this will take a while but lets you not worry about loading songs later 
    return [Song(x[0],x[1]) for x in SongList]

def SwitchPlaylist(Playlist): # similar to form's CurrentForm behaviour 
    global CurrentPlaylist

    if CurrentPlaylist:
        CurrentPlaylist.Stop()

    CurrentPlaylist = Playlist
    CurrentPlaylist.Play(Loops=-1, Volume=0.4)

def Update():
    if CurrentPlaylist:
        CurrentPlaylist.Update() # Checks if individual song instance need to be stopped/played, move onto other songs etc. 