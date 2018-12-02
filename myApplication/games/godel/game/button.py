"""A button"""

import pygame
from pgzero import actor


class Button(actor.Actor):
    """A button in the game"""

    all_buttons = []

    def __init__(self, name, image_name, callback=None, *args, **kw):
        """Initialise the button"""
        super(Button, self).__init__(image_name, *args, **kw)
        #
        self.name = name
        self.callback = callback
        #
        self.off_image = image_name
        self.on_image = '{0}_highlight'.format(image_name)
        self.all_buttons.append(self)

    def update(self, dt):
        """Update the button"""
        if self.collidepoint(pygame.mouse.get_pos()):
            self.image = self.on_image
        elif self.image == self.on_image:
            self.image = self.off_image

    def on_click(self, mouse_button):
        """Called when the button is clicked"""
        if self.callback and self.visible:
            self.callback(self, mouse_button)
