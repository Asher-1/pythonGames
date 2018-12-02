'''
Created on 13.09.2011

'''

import csv
import data
from pyglet.media import Player

playEffects = True
playSound = True

_settings = None

def no_effects():
    global playEffects
    playEffects = False

def no_sound():
    global playSound
    playSound = False

def read_csv(filename):
    global _settings
    _settings = {}
    my_csv = data.load_csv_file(filename)
    my_file = csv.reader(open(my_csv, "r"), delimiter=";")
    
    for _line in my_file:
        name = ""
        volume = 1.0
        name = _line[0].replace("\"", "")
        try:
            volume = float(_line[2].replace("\"", ""))
            _settings[name] = volume 
        except:
            print "error reading volume", _line
            _settings[name] = volume

def read_setting(name):
    global _settings
    volume = _settings.get(name)
    if volume == None: return 1.0
    return volume

def play_sound(filename):
    global playSound
    if not playSound:
        return
    global playEffects
    if not playEffects:
        return
        
    sound, variation = data.load_sound(filename + ".wav")
    try:
        volume = read_setting(variation)
        sound.play(volume)
    except:
        playSound = False
        print "Error playing sound, sound deactivated"
        
class MusicPlayer:
    
    _Player = None
    
    _Music = None
    
    def __init__(self):
        self._Player = Player()
        self._Player.eos_action = Player.EOS_NEXT
        self._Player.push_handlers(self)
    
    def set_music(self, fileName):
        self._enqueue(fileName)
        self._Music = fileName
        
    def _enqueue(self, fileName):
        global playSound
        if not playSound:
            return
            
        sound, variation = data.load_sound(fileName + ".wav", True)
        try:
            volume = read_setting(variation)
            playing = self._Player.playing
            self._Player.queue(sound)
            self._Player.volume = volume
            if not self._Player.playing:
                self._Player.play()
            elif playing:
                self._Player.next()
        except:
            playSound = False
            print "Error playing sound, sound deactivated"
            
    # seeking fails on some hardware-> loop this way
    def on_eos(self):
        self.set_music(self._Music)
    