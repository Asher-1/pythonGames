'''music.py - music manage class, providing a simple, intuitive interface
to the more awkward pygame music management'''

import random

import pygame
from pygame.locals import *
from pygame.constants import *

import data
from constants import *


class MusicMan(object):
    '''I am the MusicMan and I come from far away...'''

    def __init__(self, vol=1.0):
        pygame.init()
        self.set_vol(vol)
        self.song = None
        self.loop = 0

        self.fading_out = False
        self.fadeout_startpos = None
        self.fadeout_startvol = None
        self.fadeout_time = None
    
    def change_song(self, song_file, fadeout=None):
        '''change the song, setting a fadeout if necessary'''
        if self.song is None or fadeout is None:
            pygame.mixer.music.load(song_file)
            pygame.mixer.music.play()
        else:
            self.start_fading(fadeout)

        self.song = song_file

    def random_new_song(self, fadeout=None, loop=0):
        '''pick a random song from those available'''
        new_song = None
        while new_song is None or new_song == self.song:
            new_song = data.filepath(random.choice(MUSIC_FILES))
        self.loop = loop
        self.change_song(new_song, fadeout=fadeout)

    def new_song(self, filename, loop=0, fadeout=None):
        '''pick a specific song'''
        self.loop = loop
        new_song = data.filepath(filename)
        self.change_song(new_song, fadeout=fadeout)

    def set_vol(self, vol):
        '''set the software volume'''
        self.vol = vol
        pygame.mixer.music.set_volume(vol)

    def change_vol(self, delta):
        '''change the software volume'''
        new_vol = min(1.0, max(0.0, self.vol + delta))
        self.set_vol(new_vol)

    def start_fading(self, fadeout):
        '''set the state to reflect the start of the fadeout'''
        self.fading_out = True
        self.fadeout_startpos = pygame.mixer.music.get_pos()
        self.fadeout_startvol = self.vol
        self.fadeout_time = fadeout

    def stop_fading(self):
        '''clear of the fadeout state'''
        pygame.mixer.music.fadeout(0)
        self.song = None
        self.set_vol(self.fadeout_startvol)
        self.fading_out = False
        self.fadeout_startpos = None
        self.fadeout_startvol = None
        self.fadeout_time = None

    def update(self):
        '''call once per update to keep the music in check'''
        cur_pos = pygame.mixer.music.get_pos()

        if self.fading_out:
            if cur_pos == -1 or self.vol == 0.0:
                new_song = self.song
                self.stop_fading()
                self.change_song(new_song)
            else:
                fade_end = self.fadeout_startpos + self.fadeout_time
                fade_level = max(0, float(fade_end - cur_pos)) / self.fadeout_time
                self.set_vol(self.fadeout_startvol * fade_level)
        
        if cur_pos == -1 and self.loop == 0:
            self.song = None 
        elif cur_pos == -1:
            self.change_song(self.song)
            if self.loop > 0:
                self.loop -= 1
        
        if self.song is None:
            self.random_new_song()

