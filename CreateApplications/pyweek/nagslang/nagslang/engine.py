"""Top-level event dispatching and area transition."""

import pygame
import pygame.locals as pgl

from nagslang import constants
from nagslang.options import options
from nagslang.screens.area import AreaScreen
from nagslang.events import ScreenChange
from nagslang.world import World
from nagslang.level import Level


class Engine(object):
    def __init__(self, surface):
        self._surface = surface
        self._clock = pygame.time.Clock()
        self._fps = constants.FPS
        self._dt = 1. / self._fps
        self._world = World()
        self._current_screen = None

        self._screens = {}
        for area_name in AreaScreen.list_areas():
            self._screens[area_name] = AreaScreen
        starting_area = Level.game_starting_point()[0]

        if options.point:
            x, y = options.point.split(',')
            point = (int(x), int(y))
            self._world.protagonist.set_position(point)
        if options.area:
            self.change_screen(options.area)
        else:
            self.change_screen(starting_area)
        # Dummy resize event, to force us to realise our real size
        # http://stackoverflow.com/q/16442573/8629
        pygame.event.post(pygame.event.Event(pgl.VIDEORESIZE,
                                             size=(0, 0), w=0, h=0))
        self._current_screen.splash()

    def change_screen(self, new_screen):
        if self._current_screen is not None:
            self._current_screen.teardown()
        screen_cls = self._screens[new_screen]
        self._current_screen = screen_cls(new_screen, self._world)
        self._current_screen.setup()

    def run(self):
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pgl.QUIT:
                    running = False
                elif ev.type == pgl.VIDEORESIZE:
                    pygame.display.set_mode(ev.size,
                                            pgl.SWSURFACE | pgl.RESIZABLE)
                    self._surface = pygame.display.get_surface()
                elif ScreenChange.matches(ev):
                    self._surface.fill(pygame.color.Color(0, 0, 0))
                    self.change_screen(ev.screen)
                else:
                    self._current_screen.handle_event(ev)
            self._current_screen.tick(self._dt)
            self._current_screen.render(self._surface)
            pygame.display.flip()
            self._clock.tick(self._fps)
