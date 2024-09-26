# Dependencies

import pygame as flav

# Variables

Path = "Sounds/"

Sources = {
    "Move":"Move.mp3"
}

Sounds = {}

# Functions

def init():
    for Name, Source in Sources.items():
        Sounds[Name] = flav.mixer.Sound(Path + Source)
    
def PlaySound(Name):
    if Name in Sounds:
        Sounds[Name].play()