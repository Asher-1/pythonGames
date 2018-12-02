import os

import pygame
import pygame.locals as pgl
import pymunk

from nagslang import collectable
from nagslang import game_object as go
from nagslang import enemies
from nagslang import puzzle
from nagslang.utils import (
    tile_surface, points_to_pygame, extend_line, points_to_lines)
from nagslang.resources import resources
from nagslang.yamlish import load, dump
from nagslang.constants import DEFAULT_MUSIC_VOLUME

POLY_COLORS = {
    1: pygame.color.THECOLORS['red'],
    2: pygame.color.THECOLORS['green'],
    3: pygame.color.THECOLORS['yellow'],
    4: pygame.color.THECOLORS['blue'],
    5: pygame.color.THECOLORS['lightblue'],
    6: pygame.color.THECOLORS['magenta'],
    7: pygame.color.THECOLORS['lightgreen'],
    8: pygame.color.THECOLORS['grey'],
}


LINE_COLOR = pygame.color.THECOLORS['orange']


class Level(object):
    _game_starting_point = None

    def __init__(self, name, world):
        self.name = name
        # defaults
        self.x = 800
        self.y = 600
        self.polygons = {}
        self.lines = []
        self.world = world
        self.world.level_state.setdefault(name, {})
        self.basetile = 'tiles/floor.png'
        self.music = None
        self.music_volume = None
        self._tile_image = None
        self._surface = None
        self._base_surface = None
        self._exterior = False
        self._glue = puzzle.PuzzleGlue()
        self.drawables = []
        self.overlay_drawables = []
        self._game_objects = []
        self._enemies = []

    def _get_data(self):
        # For overriding in tests.
        with resources.get_file('levels', self.name) as f:
            return load(f)

    def _dump_data(self, f):
        # For manipulation in tests.
        dump({
            'size': [self.x, self.y],
            'base_tile': self.basetile,
            'polygons': self.polygons,
            'lines': self.lines,
            'music': self.music,
            'music_volume': self.music_volume,
            'game_objects': self._game_objects,
            'enemies': self._enemies,
        }, f)

    @classmethod
    def list_levels(cls):
        dir_ = resources.get_resource_path('levels')
        for file_ in os.listdir(dir_):
            if file_ == 'meta':
                continue
            yield file_

    @classmethod
    def game_starting_point(cls):
        if not cls._game_starting_point:
            with resources.get_file('levels', 'meta') as f:
                data = load(f)
            cls._game_starting_point = (data['starting_level'],
                                        tuple(data['starting_position']))
        return cls._game_starting_point

    def is_starting_level(self):
        return self.name == self.game_starting_point()[0]

    def load(self, space):
        data = self._get_data()
        self.x, self.y = data['size']
        self.basetile = data['base_tile']
        self.music = data['music']
        self.music_volume = data.get('music_volume', DEFAULT_MUSIC_VOLUME)
        for i, points in data['polygons'].iteritems():
            self.polygons[i] = []
            for point in points:
                self.polygons[i].append(tuple(point))
        self.lines = data.get('lines', [])
        self._game_objects = data.get('game_objects', [])
        for game_object_dict in self._game_objects:
            self._create_game_object(space, **game_object_dict)
        self._enemies = data.get('enemies', [])
        for enemy_dict in self._enemies:
            self._create_enemy(space, **enemy_dict)

    def _create_game_object(self, space, classname, args, name=None):
        modules = {
            'collectable': collectable,
            'game_object': go,
            'puzzle': puzzle,
        }
        if '.' in classname:
            module, classname = classname.split('.')
        else:
            module = 'game_object'
        cls = getattr(modules[module], classname)

        if module == 'collectable' and name in self.world.inventory:
            return

        if issubclass(cls, puzzle.Puzzler):
            gobj = cls(*args)
        elif issubclass(cls, go.GameObject):
            gobj = cls(space, *args)
            level_state = self.world.level_state[self.name]
            stored_state = level_state.get(name, {})
            should_save = bool(gobj.set_stored_state_dict(stored_state))
            if should_save:
                if name is None:
                    raise Exception(
                        "Unnamed game object wants to save state:" % (gobj,))
                level_state[name] = stored_state
            self.drawables.append(gobj)
            if gobj.overlay:
                self.overlay_drawables.append(gobj.overlay)
        else:
            raise TypeError(
                "Expected a subclass of Puzzler or GameObject, got %s" % (
                    classname))
        if name is not None:
            self._glue.add_component(name, gobj)
        return gobj

    def _create_enemy(self, space, classname, args, name=None):
        cls = getattr(enemies, classname)
        if issubclass(cls, go.GameObject):
            gobj = cls(space, self.world, *args)
            self.drawables.append(gobj)
        else:
            raise TypeError(
                "Expected a subclass of GameObject, got %s" % (
                    classname))
        if name is not None:
            self._glue.add_component(name, gobj)
        return gobj

    def all_closed(self):
        """Check if all the polygons are closed"""
        closed = True
        messages = []
        for index, poly in self.polygons.items():
            if len(poly) == 0:
                # We ignore empty polygons
                continue
            elif len(poly) == 1:
                closed = False
                messages.append("Error: polygon %s too small" % index)
            elif poly[-1] != poly[0]:
                closed = False
                messages.append("Error: polygon %s not closed" % index)
        return closed, messages

    def save(self):
        closed, _ = self.all_closed()
        if not closed:
            return False
        with resources.get_file('levels', self.name, mode='w') as f:
            self._dump_data(f)
        return True

    def get_size(self):
        return self.x, self.y

    def set_base_tile(self, new_tile):
        self.basetile = new_tile
        self._tile_image = None

    def get_walls(self):
        walls = self.polygons.values()
        walls.extend(self.lines)
        return walls

    def _draw_wall_line(self, points, width, colour, extend):
        for line in points_to_lines(points):
            if extend:
                line = extend_line(
                    pymunk.Vec2d(line[0]), pymunk.Vec2d(line[1]), extend)
            line = points_to_pygame(self._surface, line)
            pygame.draw.line(self._surface, colour, line[0], line[1], width)

    def _draw_walls_lines(self, width, colour, extend):
        for index, polygon in self.polygons.items():
            self._draw_wall_line(polygon, width, colour, extend)
        for line in self.lines:
            self._draw_wall_line(line, width, colour, extend)

    def _draw_walls(self):
        inner_colour = pygame.color.THECOLORS['red']
        mid_colour = pygame.color.THECOLORS['orange']
        outer_colour = pygame.color.THECOLORS['yellow']
        self._draw_walls_lines(5, outer_colour, 0)
        self._draw_walls_lines(3, outer_colour, 1)
        self._draw_walls_lines(3, mid_colour, 0)
        self._draw_walls_lines(1, inner_colour, 0)

    def get_background(self):
        if self._surface is None:
            self._draw_background()
            self._draw_exterior()
            # Draw polygons
            self._draw_walls()
        return self._surface

    def _draw_exterior(self, force=False):
        """Fill the exterior of the level with black"""
        if self._exterior and not force:
            return
        white = pygame.color.THECOLORS['white']
        black = pygame.color.THECOLORS['black']
        surface = pygame.surface.Surface((self.x, self.y), pgl.SRCALPHA)
        surface.fill(black)
        for index, polygon in self.polygons.items():
            if len(polygon) > 1:
                pointlist = points_to_pygame(self._surface, polygon)
                # filled polygons
                color = white
                # If a polygon overlaps on of the existing polygons,
                # it is treated as negative
                # This is not a complete inversion, since any overlap
                # triggers this (inversion is easy enough, but the
                # behaviour doesn't seem useful)
                # We also only check the vertexes - not breaking this
                # assumption is left to the level designers
                surface.lock()
                for p in pointlist:
                    if surface.get_at(p) == white:
                        color = black
                surface.unlock()
                pygame.draw.polygon(surface, color, pointlist, 0)
        self._surface.blit(surface, (0, 0), special_flags=pgl.BLEND_RGBA_MULT)
        self._exterior = True

    def _draw_background(self, force=False):
        if self._tile_image is None:
            self._tile_image = resources.get_image(self.basetile)
        if self._surface is not None and not force:
            # We assume we don't change
            return self._surface
        if self._base_surface is None:
            self._base_surface = tile_surface((self.x, self.y),
                                              self._tile_image)
        self._surface = self._base_surface.copy()
        return self._surface
