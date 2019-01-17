"""A scrolling region holding a number of items"""

import pygame
from pgzero import actor
from game import group
from game import rectangle
from game.settings import SETTINGS as S


class ScrolledEntries(group.Group):
    """A scrolling region of entries"""

    def __init__(self, name, width, height, background, *args, **kw):
        """Initialise the scrolled group"""
        super(ScrolledEntries, self).__init__(name)
        #
        self.initial_offset = 0
        self.item_heights = S['text-entry-height']
        self.my_surface = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        self.region = actor.Actor(self.my_surface, *args, **kw)
        #
        self.background = None if background is None else actor.Actor(background)
        # self.scroll_grab = rectangle.Rectangle(
        #     S['scrolled-scroll-colour'], (S['scrolled-scroll-width'], S['scrolled-scroll-height'])
        # )

    def draw(self, surface):
        """Draw the scrolled entries"""
        #
        # Set the positions of all the items
        y = 0
        self.my_surface.fill((0, 0, 0, 0))
        for idx, item in enumerate(self):
            y += self.item_heights
            item.pos = (item.width / 2, y - self.initial_offset)
            #
            # Now draw item
            item.draw(self.my_surface)
        # #
        # # And the scrollbar
        # self.scroll_grab.pos = (self.my_surface.get_size()[0] - S['scrolled-scroll-width'], 0)
        # self.scroll_grab.draw(self.my_surface)
        #
        # Draw main surface
        if self.background:
            self.background.pos = self.pos
            self.background.draw(surface)
        self.region.pos = self.pos
        self.region.draw(surface)

    def page_down(self):
        """Page the display down"""
        self.set_initial_offset(self.initial_offset + self.my_surface.get_height())

    def page_up(self):
        """Page the display down"""
        self.set_initial_offset(self.initial_offset - self.my_surface.get_height())

    def down(self):
        """Move the display down"""
        self.set_initial_offset(self.initial_offset + self.item_heights)

    def up(self):
        """Move the display down"""
        self.set_initial_offset(self.initial_offset - self.item_heights)

    def home(self):
        """Return to the home"""
        self.initial_offset = 0

    def end(self):
        """Go to the end"""
        self.set_initial_offset(1e6)

    def set_initial_offset(self, offset):
        """Set the initial offset"""
        self.initial_offset = max(
            min(
                (len(self) + 0.5) * self.item_heights - self.my_surface.get_height(),
                offset
                ),
            0
        )