"""Tween between screens when changing worlds"""

import math
import pygame
from pygame.draw import circle

import serge.world
import serge.engine
import serge.sound


class TweenerEffect(object):
    """Tween between screens"""

    def __init__(self, last_frame, next_frame):
        """Initialise the effect"""
        self.last_frame = last_frame
        self.next_frame = next_frame

    def renderTo(self, surface, fraction):
        """Render to the main surface"""


class SplitScreen(TweenerEffect):
    """An effect to split a screen going from the last to the next world"""

    def renderTo(self, surface, fraction):
        """Render to the main surface"""
        fraction = 1.0 - math.cos(fraction * math.pi / 2.0)
        #
        # Back-plane
        surface.blit(self.next_frame, (0, 0))
        #
        # Left and right
        w, h = self.last_frame.get_size()
        dx = fraction * w / 2.0
        surface.blit(self.last_frame, (0, 0), (dx, 0, w / 2 - dx, h))
        surface.blit(self.last_frame, (w / 2 + dx, 0), (w / 2, 0, w / 2, h))


class ReverseSplitScreen(SplitScreen):
    """A split screen with a closing effect"""

    def __init__(self, last_frame, next_frame):
        """Initialise the split"""
        super(ReverseSplitScreen, self).__init__(next_frame, last_frame)

    def renderTo(self, surface, fraction):
        """Render the effect"""
        super(ReverseSplitScreen, self).renderTo(surface, 1.0 - fraction)


class IrisScreen(TweenerEffect):
    """Iris the screen from one to the other"""

    def __init__(self, last_frame, next_frame, pause_fraction=0):
        """Initialise the effect"""
        super(IrisScreen, self).__init__(last_frame, next_frame)
        self.pause_fraction = pause_fraction / 2
        #
        renderer = serge.engine.CurrentEngine().getRenderer()
        self.w, self.h = renderer.getScreenSize()
        self.radius = max(self.w, self.h)
        self.iris = renderer.getSurface().copy()

    def renderTo(self, surface, fraction):
        """Render the iris"""
        #
        # Get parameters to draw the iris
        if fraction < 0.5 - self.pause_fraction:
            circle_fraction = self.radius * (0.5 - self.pause_fraction - fraction) * 2
            frame = self.last_frame
        elif fraction > 0.5 + self.pause_fraction:
            circle_fraction = self.radius * (fraction - (0.5 + self.pause_fraction)) * 2
            frame = self.next_frame
        else:
            circle_fraction = 0
            frame = self.last_frame
        #
        # Do the drawing
        self.iris.fill((255, 255, 255, 255))
        if circle_fraction:
            pygame.draw.circle(self.iris, (0, 0, 0, 255), (int(self.w / 2), int(self.h / 2)), int(circle_fraction))
            surface.blit(frame, (0, 0))
        surface.blit(self.iris, (0, 0), special_flags=pygame.BLEND_RGB_SUB)


class ScreenTween(serge.world.World):
    """Visually tween between worlds"""

    def __init__(self, name, effect=SplitScreen):
        """Initialise the world"""
        super(ScreenTween, self).__init__(name)
        #
        self.renderer = self._from_world = self._to_world = None
        self._last_frame = self._next_frame = self.effect = None

    def setEngine(self, engine):
        """The engine is set"""
        super(ScreenTween, self).setEngine(engine)
        #
        self.renderer = self.engine.getRenderer()

    def tweenToWorld(self, to_world, duration, effect_class, sound=None, **kw):
        """Make the transition"""
        if sound:
            serge.sound.Sounds.play(sound)
        #
        # Store the last rendered frame
        self._from_world = self.engine.getCurrentWorld()
        self._last_frame = self.renderer.getSurface().copy()
        #
        # Get the next frame
        self._to_world = self.engine.setCurrentWorldByName(to_world)
        self.renderer.clearSurface()
        self._to_world.renderTo(self.renderer, 0)
        self._next_frame = self.renderer.getSurface().copy()
        #
        # Back to this world
        self.engine._current_world = self
        #
        self._elapsed_time = 0
        self.duration = duration
        self.effect = effect_class(self._last_frame, self._next_frame, **kw)

    def renderTo(self, renderer, interval):
        """Render to the screen"""
        self._elapsed_time += interval / 1000.0
        if self._elapsed_time > self.duration:
            self.engine._current_world = self._to_world
            self.effect.renderTo(renderer.getSurface(), 1.0)
        else:
            self.effect.renderTo(renderer.getSurface(), float(self._elapsed_time) / self.duration)


