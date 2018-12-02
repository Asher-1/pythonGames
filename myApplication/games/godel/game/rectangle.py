"""An actor showing a filled rectangle"""

import pygame
from pgzero import actor


class Rectangle(actor.Actor):
    """An actor that shows a filled rectangle"""

    def __init__(self, colour, size, *args, **kw):
        """Initialise the rectangle"""
        surface = pygame.Surface(size)
        surface.fill(colour)
        #
        self.colour = colour
        #
        super(Rectangle, self).__init__(surface, *args, **kw)
        #
        self._pos = self.pos

    def resize(self, size):
        """Set the new width"""
        self.size = size
        surface = pygame.Surface(size)
        surface.fill(self.colour)
        self.image = surface
        self.pos = self._pos

    @property
    def newsize(self):
        return self.size

    @newsize.setter
    def newsize(self, size):
        self.resize(size)