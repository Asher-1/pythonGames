import pygame


class Widget(object):
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos, size if size else (0, 0))
        self.visible = True
        self.is_prepared = False

    def draw(self, surface):
        raise NotImplemented()

    def prepare(self):
        raise NotImplemented()

    def do_prepare(self):
        if not self.is_prepared:
            self.prepare()
            self.is_prepared = True
