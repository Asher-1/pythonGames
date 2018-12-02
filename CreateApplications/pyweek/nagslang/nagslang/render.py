import math
import textwrap

import pygame
import pygame.locals as pgl
import pymunk

from nagslang.options import options
from nagslang.utils import (
    tile_surface, vec_from_angle, points_to_pygame, extend_line)
from nagslang.widgets.text import LabelWidget, MultiLineWidget


class Renderer(object):
    def set_game_object(self, game_object):
        self.game_object = game_object

    def _render_shape(self, surface):
        shape = self.game_object.get_shape()
        # Less general that pymunk.pygame_util.draw, but also a lot less noisy.
        color = getattr(shape, 'color', pygame.color.THECOLORS['lightblue'])
        # We only explicitly draw Circle and Poly shapes. Everything else we
        # forward to pymunk.
        if isinstance(shape, pymunk.Circle):
            centre = pymunk.pygame_util.to_pygame(shape.body.position, surface)
            radius = int(shape.radius)
            pygame.draw.circle(surface, color, centre, radius, 2)
        elif isinstance(shape, pymunk.Poly):
            # polygon bounding box
            points = [pymunk.pygame_util.to_pygame(p, surface)
                      for p in shape.get_vertices()]
            pygame.draw.lines(surface, color, True, points, 2)
        else:
            pymunk.pygame_util.draw(surface, shape)

    def render(self, surface):
        if options.shapes:
            self._render_shape(surface)

    def update(self, seconds):
        # Used by time animatations to advance the clock
        pass


class NullRenderer(Renderer):
    def render(self, surface):
        pass


class HatchRendererMixin(object):
    def draw_hatch_line(self, surface, a, b):
        ai, bi = extend_line(a, b, -2)
        a, b, ai, bi = points_to_pygame(surface, (a, b, ai, bi))
        pygame.draw.line(
            surface, pygame.color.THECOLORS['black'], a, b, 7)
        pygame.draw.line(
            surface, pygame.color.THECOLORS['lightblue'], ai, bi, 5)

    def render_hatch(self, surface):
        shape = self.game_object.get_shape()
        a = shape.body.local_to_world(shape.a)
        b = shape.body.local_to_world(shape.b)
        if self.game_object.puzzler.get_state():
            offset = vec_from_angle((b - a).angle, 10)
            ai = a + offset
            bi = b - offset
            self.draw_hatch_line(surface, a, ai)
            self.draw_hatch_line(surface, bi, b)
        else:
            mid = a + (b - a) / 2
            self.draw_hatch_line(surface, a, mid)
            self.draw_hatch_line(surface, mid, b)


class HatchRenderer(Renderer, HatchRendererMixin):
    def render(self, surface):
        self.render_hatch(surface)


def image_pos(image, pos):
    return (pos[0] - image.get_width() / 2,
            pos[1] - image.get_height() / 2)


class ImageRenderer(Renderer):
    def __init__(self, image):
        self._image = image

    def get_image(self):
        return self._image

    def rotate_image(self, image):
        angle = self.game_object.get_render_angle() * 180 / math.pi
        return pygame.transform.rotate(image, angle)

    def render_image(self, surface, image):
        image = self.rotate_image(image)
        pos = self.game_object.get_render_position(surface)
        surface.blit(image, image_pos(image, pos))

    def render(self, surface):
        self.render_image(surface, self.get_image())
        super(ImageRenderer, self).render(surface)


class KeyedHatchRenderer(ImageRenderer, HatchRendererMixin):
    def render(self, surface):
        self.render_hatch(surface)
        if not self.game_object.puzzler.get_state():
            self.render_image(surface, self.get_image())


class ImageStateRenderer(ImageRenderer):
    def __init__(self, state_images):
        self._state_images = state_images

    def get_image(self):
        return self._state_images[self.game_object.puzzler.get_state()]


class TimedAnimatedRenderer(ImageRenderer):
    def __init__(self, images, frame_ticks=1):
        self._images = images
        self._frame_ticks = frame_ticks
        self._frame_tick = 0
        self._frame = 0

    def advance_tick(self):
        self._frame_tick += 1
        if self._frame_tick > self._frame_ticks:
            self._frame_tick = 0
            self._frame += 1
        if self._frame >= len(self._images):
            self._frame = 0

    def reset(self):
        self._frame_tick = 0
        self._frame = 0

    def get_image(self):
        return self._images[self._frame]

    def update(self, seconds):
        self.advance_tick()


class MovementAnimatedRenderer(TimedAnimatedRenderer):
    def update(self, seconds):
        if self.game_object.is_moving:
            self.advance_tick()
        else:
            self.reset()


class RendererSelectionRenderer(Renderer):
    def __init__(self, renderers):
        self._renderers = renderers

    def set_game_object(self, game_object):
        self.game_object = game_object
        for renderer in self._renderers.values():
            renderer.set_game_object(game_object)

    @property
    def renderer(self):
        return self._renderers[self.select_renderer()]

    def render(self, surface):
        return self.renderer.render(surface)

    def update(self, seconds):
        return self.renderer.update(seconds)

    def select_renderer(self):
        raise NotImplementedError()


class FacingSelectionRenderer(RendererSelectionRenderer):
    def select_renderer(self):
        return self.game_object.get_facing_direction()


class ShapeRenderer(Renderer):
    def render(self, surface):
        self._render_shape(surface)
        super(ShapeRenderer, self).render(surface)


class ShapeStateRenderer(ShapeRenderer):
    """Renders the shape in a different colour depending on the state.

    Requires the game object it's attached to to have a puzzler.
    """
    def render(self, surface):
        if self.game_object.puzzler.get_state():
            color = pygame.color.THECOLORS['green']
        else:
            color = pygame.color.THECOLORS['red']

        self.game_object.get_shape().color = color
        super(ShapeStateRenderer, self).render(surface)


class Overlay(object):
    def set_game_object(self, game_object):
        self.game_object = game_object

    def render(self, surface, display_offset, max_width):
        pass

    def is_visible(self):
        return self.game_object.puzzler.get_state()


class TextOverlay(Overlay):
    def __init__(self, text, **kwargs):
        self.text = text
        self.widget = LabelWidget((20, 20), self.text, **kwargs)

    def render(self, surface, display_offset, max_width):
        x, y = 20, 20
        if display_offset[0] < 0:
            x += abs(display_offset[0])
        if display_offset[1] < 0:
            y += abs(display_offset[1])
        if self.widget.rect.width > max_width - 40:
            # Need to relayout the widget
            factor = 2
            while self.widget.rect.width > max_width - 40:
                wrapped = '\n'.join(textwrap.wrap(self.text,
                                                  len(self.text) // factor))
                factor *= 2
                self.widget = MultiLineWidget((20, 20), wrapped)
                if self.widget.rect.width < 100:
                    # safety valve
                    break
            self.widget.rect.topleft = (x, y)
            self.widget.draw(surface)
            # TODO: undo the mad folding
        else:
            self.widget.rect.topleft = (x, y)
            self.widget.draw(surface)


class ImageOverlay(Overlay):
    def __init__(self, image):
        self.image = image

    def render(self, surface, display_offset, max_width):
        x = (surface.get_width() - self.image.get_width()) / 2
        y = (surface.get_height() - self.image.get_height()) / 2
        surface.blit(self.image, (x, y))


class TiledRenderer(Renderer):
    """Tile the given image to fit the given outline

       Outline is assumed to be in pymunk coordinates"""

    def __init__(self, outline, tile_image, alpha=255):
        self._tile_image = tile_image
        self.outline = outline
        self._tiled = None
        self._offset = None
        self._alpha = alpha

    def _make_surface(self, surface, image):
        size = surface.get_size()
        mask = pygame.surface.Surface(size, pgl.SRCALPHA)
        pointlist = [pymunk.pygame_util.to_pygame(p, surface)
                     for p in self.outline]
        rect = pygame.draw.polygon(mask,
                                   pygame.color.Color(
                                       255, 255, 255, self._alpha),
                                   pointlist, 0)
        self._offset = (rect.x, rect.y)
        tiled = tile_surface((rect.w, rect.h), image)
        tiled.blit(mask, (0, 0), rect,
                   special_flags=pgl.BLEND_RGBA_MULT)
        return tiled

    def render(self, surface):
        if not self._tiled:
            self._tiled = self._make_surface(surface, self._tile_image)
        surface.blit(self._tiled, self._offset)
        super(TiledRenderer, self).render(surface)


class TimedTiledRenderer(TiledRenderer):
    """Animate tiles"""

    # Should make this a mixin with TimeAnimate, but not right now

    def __init__(self, outline, images, frame_ticks=1, alpha=255):
        self._images = images
        self._frame_ticks = frame_ticks
        self.outline = outline
        self._frames = [None] * len(images)
        self._offset = None
        self._alpha = alpha
        self._frame = 0
        self._frame_tick = 0

    def advance_tick(self):
        self._frame_tick += 1
        if self._frame_tick > self._frame_ticks:
            self._frame_tick = 0
            self._frame += 1
        if self._frame >= len(self._images):
            self._frame = 0

    def reset(self):
        self._frame_tick = 0
        self._frame = 0

    def update(self, seconds):
        self.advance_tick()

    def render(self, surface):
        if not self._frames[self._frame]:
            self._frames[self._frame] = self._make_surface(
                surface, self._images[self._frame])
        self._tiled = self._frames[self._frame]
        super(TimedTiledRenderer, self).render(surface)
