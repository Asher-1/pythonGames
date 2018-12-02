import pygame
import pygame.locals as pgl

import pymunk
import pymunk.pygame_util


def convert_colour(colour):
    if isinstance(colour, pygame.Color):
        return colour
    if isinstance(colour, tuple):
        return pygame.Color(*colour)
    if isinstance(colour, basestring):
        return pygame.Color(colour)
    raise ValueError()


def vec_from_angle(angle, length=1):
    vec = pymunk.Vec2d(length, 0)
    vec.angle = angle
    return vec


def vec_with_length(coords, length=1):
    vec = pymunk.Vec2d(coords)
    # Don't crash if we've created a zero length vector
    if vec.length != 0:
        vec.length = length
    return vec


def points_to_lines(points):
    if len(points) < 2:
        return
    last_point = points[0]
    for point in points[1:]:
        yield (last_point, point)
        last_point = point


def extend_line(a, b, length):
    offset = vec_from_angle((a - b).angle, abs(length))
    if length < 0:
        offset = -offset
    return (a + offset, b - offset)


def points_to_pygame(surface, points):
    return [pymunk.pygame_util.to_pygame(p, surface) for p in points]


def tile_surface(size, tile_image):
    # create a surface, approriately tiled
    surface = pygame.surface.Surface(size, pgl.SRCALPHA)
    x_step = tile_image.get_rect().width
    y_step = tile_image.get_rect().height
    x_count = size[0] // x_step + 1
    y_count = size[1] / y_step + 1
    tile_rect = pygame.rect.Rect(0, 0, x_step, y_step)
    for x in range(x_count):
        tile_rect.x = x * x_step
        for y in range(y_count):
            tile_rect.y = y * y_step
            surface.blit(tile_image, tile_rect)
    return surface
