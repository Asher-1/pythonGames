'''renderer.py - base class for renderers'''

import pygame
from pygame.locals import *
from pygame.constants import *


class Renderer(object):

    def __init__(self, state, interface):
        self.state = state
        self.interface = interface

    def setup_pygame(self):
        pygame.init()
    
    def draw(self):
        pass

    def scroll_left(self):
        pass

    def scroll_right(self):
        pass

    def scroll_up(self):
        pass

    def scroll_down(self):
        pass

    def zoom_in(self):
        pass

    def zoom_out(self):
        pass

    def report(self):
        pass
