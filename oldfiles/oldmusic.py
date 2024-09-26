import pygame as flav
import asyncio

Sources = ["File","YT"]
Path = "Tunes/"

class Song():
    SongLookup = {}

    def __init__(self, SongName, Query, Source=0, **kwargs): 
        self.Name = SongName
        self.SongInstance = None

        if Source == 0:
            self.SongInstance = self.ImportFromFile(Query)
        elif Source == 1:
            self.SongInstance = self.ImportFromYT(Query, **kwargs)

        Song.SongLookup[SongName] = self.SongInstance

    def ImportFromFile(self, FileName):
        return flav.mixer.Sound(Path + FileName)

    def ImportFromYT(self, SongName):
        pass

class Playlist():
    Playlists = []

    def __init__(self, SongList=None, SongInstances=None):
        self.Songs = []

        if SongList:
            for SongName in SongList:
                if Song.SongLookup[SongName]:
                    self.Songs.append(Song.SongLookup[SongName])

        if SongInstances:
            if SongList:
                for SongInstance in SongInstances:
                    self.Songs.append(SongInstance)
            else:
                self.Songs = SongInstances

    async def Play(self, Loops=1):
        LoopCount = 0

        while (LoopCount < Loops) or (Loops == -1):
            for SongInstance in self.Songs: 
                #SongInstance.set_volume(0)
                SongInstance.play()
                await asyncio.sleep(SongInstance.get_length())

            LoopCount += 1
    def AddSong(self):
        pass
    
    def Shuffle(self):
        pass

def MassPreloadSongs(SongList):
    return [Song(x[0],x[1]) for x in SongList]