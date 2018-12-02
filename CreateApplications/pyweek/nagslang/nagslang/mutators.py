'''Mutations to apply to images'''

import pygame
from pygame.transform import rotate, flip, scale


class Mutator(object):
    def __init__(self, func, *args):
        self._func = func
        self._args = tuple(args)

    def __call__(self, image):
        return self._func(image, *self._args)

    def __hash__(self):
        return hash((self._func, self._args))

    def __eq__(self, other):
        if not isinstance(other, Mutator):
            return NotImplemented
        return (self._func == other._func) and (self._args == other._args)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self._args)


class Colour(Mutator):
    '''Overlay a colour onto an image'''
    def __init__(self, colour, blend=pygame.locals.BLEND_RGBA_MULT):
        super(Colour, self).__init__(Colour.colour, colour, blend)

    @classmethod
    def colour(self, image, colour, blend):
        image = image.copy()
        overlay = pygame.surface.Surface(image.get_size(),
                                         pygame.locals.SRCALPHA, image)
        overlay.fill(colour)
        image.blit(overlay, (0, 0), None, blend)
        return image


class ImageOverlay(Mutator):
    '''Overlay another image onto an image'''
    def __init__(self, image, offset=(0, 0), halfsize=True, blend=0):
        super(ImageOverlay, self).__init__(
            ImageOverlay.overlay, image, offset, halfsize, blend)

    @classmethod
    def overlay(self, image, overlay, offset, halfsize, blend):
        image = image.copy()
        if halfsize:
            new_size = (overlay.get_width() / 2, overlay.get_height() / 2)
            overlay = scale(overlay, new_size)
        offset_x = image.get_width() / 2 - overlay.get_width() / 2 + offset[0]
        offset_y = image.get_width() / 2 - overlay.get_width() / 2 + offset[1]
        image.blit(overlay, (offset_x, offset_y), None, blend)
        return image


class ImageCentre(Mutator):
    def __init__(self, size):
        super(ImageCentre, self).__init__(ImageCentre.centre, size)

    @classmethod
    def centre(cls, image, size):
        if image.get_size() == size:
            return image
        surf = pygame.surface.Surface(size, pygame.locals.SRCALPHA, image)
        surf.blit(image, ((size[0] - image.get_width()) / 2,
                          (size[1] - image.get_height()) / 2))
        return surf


def rotator(angle):
    return Mutator(rotate, angle)


def scaler(size):
    return Mutator(scale, size)


# Identity mutator
NULL = Mutator(lambda x: x)

# Rotation
R90 = rotator(90)
R180 = rotator(180)
R270 = rotator(-90)

FLIP_H = Mutator(flip, True, False)
FLIP_V = Mutator(flip, False, True)

# Colour
RED = Colour((255, 0, 0))
GREEN = Colour((0, 255, 0))
BLUE = Colour((0, 0, 255))
