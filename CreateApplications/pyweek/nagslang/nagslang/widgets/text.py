from nagslang.constants import FONT, FONT_SIZE
from nagslang.widgets.base import Widget
import pygame

from nagslang.utils import convert_colour
from nagslang.resources import resources


class TextWidget(Widget):
    def __init__(self, pos, text, size=None, fontname=None, fontsize=None,
                 colour=None):
        super(TextWidget, self).__init__(pos, size)

        self.text = text
        self.fontname = fontname or FONT
        self.fontsize = fontsize or FONT_SIZE
        self.colour = convert_colour(colour or (0, 0, 0))

        self.prepare()

    def prepare(self):
        self.font = resources.get_font(self.fontname, self.fontsize)
        self.surface = self.font.render(self.text, True, self.colour)
        self.text_rect = self.surface.get_rect()
        if not self.size:
            self.rect.size = self.text_rect.size

    def draw(self, surface):
        if self.visible:
            self.do_prepare()
            surface.blit(self.surface, self.rect)


class LabelWidget(TextWidget):
    def __init__(self, *args, **kwargs):
        self.padding = kwargs.pop('padding', 5)
        self.border = kwargs.pop('border', 2)
        self.bg_colour = convert_colour(kwargs.pop('bg_colour',
                                                   (255, 255, 255, 192)))
        self.border_colour = convert_colour(kwargs.pop('border_colour',
                                                       (0, 0, 0)))
        super(LabelWidget, self).__init__(*args, **kwargs)

    def prepare(self):
        super(LabelWidget, self).prepare()
        if not self.size:
            self.rect.width += 2 * self.padding
            self.rect.height += 2 * self.padding
        surface = pygame.Surface(self.rect.size)
        surface = surface.convert_alpha()
        surface.fill(self.bg_colour)
        surface.blit(self.surface, self.surface.get_rect().move(
            (self.padding, self.padding)))
        pygame.draw.rect(surface, self.border_colour, surface.get_rect(),
                         self.border)
        self.surface = surface


class MultiLineWidget(LabelWidget):

    def prepare(self):
        self.font = resources.get_font(self.fontname, self.fontsize)
        surfaces = []
        height = 0
        width = 0
        for line in self.text.split('\n'):
            surface = self.font.render(line, True, self.colour)
            width = max(width, surface.get_rect().width)
            height += surface.get_rect().height
            surfaces.append(surface)
        width += 2 * self.padding
        height += 2 * self.padding
        self.surface = pygame.surface.Surface((width, height),
                                              pygame.locals.SRCALPHA)
        self.surface.fill(self.bg_colour)
        y = 0
        for surface in surfaces:
            self.surface.blit(surface, (self.padding, y + self.padding))
            y += surface.get_rect().height
        self.text_rect = self.surface.get_rect()
        if not self.size:
            self.rect.size = self.text_rect.size
