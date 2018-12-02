'''sound.py - sound manager'''

import random

import pygame
from pygame.locals import *
from pygame.constants import *

import data
from constants import *


def post_sound(code):
    pygame.event.post(pygame.event.Event(SOUND_EVENT, code=code))


class SoundMan(object):
    sounds = {}
    channels = {}
        
    def load(self, soundfile):
        if soundfile in self.sounds:
            return self.sounds[soundfile]
        sound = pygame.mixer.Sound(data.filepath(soundfile))
        self.sounds[soundfile] = sound
        return sound

    def play(self, soundfile):
        chan = pygame.mixer.find_channel()
        if chan is None: return False
        sound = self.load(soundfile)
        chan.play(sound)
        return chan

    def handle_sound_event(self, evt):
        for code, chan in self.channels.items():
            if not chan.get_busy():
                del self.channels[code]

        if self.is_playing(evt.code):
            return
        elif isinstance(evt.code, tuple):
            chan = self.play(random.choice(evt.code))
        else:
            chan = self.play(evt.code)

        self.channels[evt.code] = chan

    def is_playing(self, sound_code):
        return sound_code in self.channels
