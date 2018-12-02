import math
import random

import pymunk

import pyglet

import cocos
from cocos.scenes.transitions import FadeTRTransition

from gamelib.atom import Atom
from gamelib.collision import (C_WALL, C_ATOM, C_ENEMY, C_STRONGHOLD,
                               C_ELECTRON, C_PROTON)
from gamelib.enemy import Enemy, RADIUS as E_RADIUS
from gamelib.stronghold import Stronghold
from gamelib.subparticle import Electron, Proton
from gamelib.subparticle_counter import SubparticleCounter
from gamelib.wall import Wall, StrongholdWall
from gamelib.score import Score
from gamelib.data import SoundFxHolder


DAMPING = 0.3
UPDATE_INTERVAL = 1.0 / 60.0
ATOM_INIT_POS = (400, 70)
ENEMY_DISSAPIER_TIME = 0.5
INIT_ELECTRONS = 11
INIT_PROTONS = 11
ELECTRON_TIMEOUT = 0.7
PROTON_TIMEOUT = 1.0

ENEMY_TIMEOUT_MIN = 0.3
ENEMY_TIMEOUT_START = 2.0
ENEMY_TIMEOUT_REDUCER = 0.85

TIMEOUT_BEFORE_END = 1.0

SUBPARTICLE_VOLUME = 0.5


class GameLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, end_game_class):
        super(GameLayer, self).__init__()
        self.end_game_class = end_game_class

        self.soundfx = SoundFxHolder(['damaged', 'enemy',
                                      'subparticle', 'shoot'])
        self.init_space()

        self.dispose_list = set()
        self.spaceobjects = []

        self.init_counter()
        self.atom = None
        self.init_atom()
        self.init_walls()
        self.init_stronghold()
        self.init_score()

        self.init_collision_callbacks()

        self.set_timers()

    def set_timers(self):
        self.enemy_timeout = ENEMY_TIMEOUT_START
        pyglet.clock.schedule_once(self.create_enemy, 2.0)
        pyglet.clock.schedule_once(self.create_proton, 2.0)
        pyglet.clock.schedule_once(self.create_electron, 2.0)

    def init_score(self):
        self.score = Score(self.score_checkpoint)
        self.add(self.score, z=4)

    def score_checkpoint(self):
        self.enemy_timeout = max(ENEMY_TIMEOUT_MIN,
                                 self.enemy_timeout * ENEMY_TIMEOUT_REDUCER)

    def init_counter(self):
        self.counter = SubparticleCounter(ATOM_INIT_POS, INIT_ELECTRONS,
                                          INIT_PROTONS)
        self.add(self.counter)

    def init_collision_callbacks(self):
        self.space.add_collision_handler(C_ATOM, C_WALL,
                                         self.on_atom_hit_wall)
        self.space.add_collision_handler(C_ATOM, C_ENEMY,
                                         self.on_atom_hit_enemy)
        self.space.add_collision_handler(C_ATOM, C_PROTON,
                                         self.on_atom_hit_proton)
        self.space.add_collision_handler(C_ATOM, C_ELECTRON,
                                         self.on_atom_hit_electron)

        self.space.add_collision_handler(C_ENEMY, C_STRONGHOLD,
                                         self.on_enemy_hit_stronghold)
        self.space.add_collision_handler(C_ENEMY, C_WALL,
                                         self.on_enemy_hit_wall)
        self.space.add_collision_handler(C_ENEMY, C_PROTON,
                                         self.on_enemy_hit_proton)
        self.space.add_collision_handler(C_ENEMY, C_ELECTRON,
                                         self.on_enemy_hit_electron)

        self.space.add_collision_handler(C_PROTON, C_STRONGHOLD,
                                         self.on_proton_hit_stronghold)
        self.space.add_collision_handler(C_ELECTRON, C_STRONGHOLD,
                                         self.on_electron_hit_stronghold)

        self.space.add_collision_handler(C_PROTON, C_WALL,
                                         self.on_proton_hit_wall)
        self.space.add_collision_handler(C_ELECTRON, C_WALL,
                                         self.on_electron_hit_wall)

    def get_enemy_timeout(self):
        return self.enemy_timeout

    def get_proton_timeout(self):
		return PROTON_TIMEOUT

    def get_electron_timeout(self):
		return ELECTRON_TIMEOUT

    def create_enemy(self, dt):
        w, h = cocos.director.director.get_window_size()

        enemy = Enemy((E_RADIUS + random.random() * (w - E_RADIUS), h + E_RADIUS))
        self.add(enemy, z=1)
        self.add_spaceobject(enemy)
        pyglet.clock.schedule_once(self.create_enemy,
                                   self.get_enemy_timeout())

    def create_proton(self, dt):
        self.create_subparticle(Proton)
        pyglet.clock.schedule_once(self.create_proton,
                                   self.get_proton_timeout())

    def create_electron(self, dt):
        self.create_subparticle(Electron)
        pyglet.clock.schedule_once(self.create_electron,
                                   self.get_electron_timeout())

    def create_subparticle(self, subparticle_class):
        w, h = cocos.director.director.get_window_size()
        subparticle = subparticle_class((random.random() * w,
                                         random.random() * (h - 200) + 200))
        self.add(subparticle, z=1)
        self.add_spaceobject(subparticle)

    def init_atom(self):
        if self.atom is None and self.counter.is_enough_for_atom():
            self.atom = Atom(ATOM_INIT_POS)
            self.counter.on_new_atom()
            self.add(self.atom, z=2)

    def init_stronghold(self):
        self.stronghold = Stronghold()
        self.add(self.stronghold, z=0)

        # Generes part of ellipse that looks like contour of stronghold
        # Stupid spagetti with magic numbers...
        angle = 1.06
        wall_points = []
        while angle < 2.17:
            wall_points.append((math.cos(angle) * 800 + 400,
                                math.sin(angle) * 500 - 350))
            angle += 0.17
        for a, b in zip(wall_points[:-1], wall_points[1:]):
            self.space.add_static(StrongholdWall(a, b).shape)

    def init_walls(self):
        w, h = cocos.director.director.get_window_size()

        wall = Wall((-w, h * 2), (w*2, h*2))
        self.space.add_static(wall.shape)
        wall = Wall((-w, h*2), (-w, -h))
        self.space.add_static(wall.shape)
        wall = Wall((w*2, h*2), (w*2, -h))
        self.space.add_static(wall.shape)

    def add_spaceobject(self, spaceobject):
        self.spaceobjects.append(spaceobject)
        self.space.add(spaceobject.body, spaceobject.shape)

    def remove_spaceobject(self, spaceobject):
        self.spaceobjects.remove(spaceobject)
        self.space.remove(spaceobject.body, spaceobject.shape)

    def init_space(self):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, 0.0)
        self.space.damping = DAMPING
        pyglet.clock.schedule_interval(self.space_step, UPDATE_INTERVAL)

    def proccess_dispose_list(self):
        for spaceobject in self.dispose_list:
            self.remove_spaceobject(spaceobject)
            spaceobject.kill()
        self.dispose_list.clear()

    def space_step(self, dt):
        if self.dispose_list:
            self.proccess_dispose_list()

        self.space.step(dt)
        for spaceobject in self.spaceobjects:
            spaceobject.update_position()

    def end_game(self, dt):
        scene = self.end_game_class(self.score.score)
        cocos.director.director.replace(FadeTRTransition(scene))

    def on_key_press (self, key, modifiers):
        if self.atom is None:
            return

        if key == pyglet.window.key.LEFT and self.counter.has_electrons():
            self.counter.dec_electrons()
            self.atom.add_electron()
        elif key == pyglet.window.key.RIGHT and self.counter.has_protons():
            self.counter.dec_protons()
            self.atom.add_proton()
        elif key == pyglet.window.key.SPACE and self.atom is not None:
            self.atom.shoot()
            self.add_spaceobject(self.atom)
            self.atom = None
            self.init_atom()
            self.soundfx.play('shoot')
        elif key == pyglet.window.key.SPACE and self.atom is None:
            self.soundfx.play('shoot-empty')

    def on_atom_hit_wall(self, space, arbiter):
        atom = arbiter.shapes[0].spaceobject
        self.dispose_list.add(atom)
        return True

    def on_atom_hit_enemy(self, space, arbiter):
        enemy = arbiter.shapes[1].spaceobject
        if enemy.was_hit:
            return False
        enemy.dissapear(ENEMY_DISSAPIER_TIME)
        enemy.was_hit = True
        self.score.on_enemy_kill()
        pyglet.clock.schedule_once(lambda dt: self.dispose_list.add(enemy),
                                   ENEMY_DISSAPIER_TIME)
        self.soundfx.play('enemy')
        return True

    def on_enemy_hit_stronghold(self, space, arbiter):
        enemy = arbiter.shapes[0].spaceobject
        if not enemy.was_hit:
            self.atom = None # prevents input
            self.stronghold.to_damaged()
            pyglet.clock.unschedule(self.space_step)
            pyglet.clock.unschedule(self.create_enemy)
            pyglet.clock.unschedule(self.create_proton)
            pyglet.clock.unschedule(self.create_electron)
            self.pause()
            pyglet.clock.schedule_once(self.end_game, TIMEOUT_BEFORE_END)
            self.soundfx.play('damaged')
            return True
        return False

    def on_enemy_hit_wall(self, space, arbiter):
        enemy = arbiter.shapes[0].spaceobject
        if not enemy.was_hit:
            self.dispose_list.add(enemy)
            return True
        return False

    def on_atom_hit_proton(self, space, arbiter):
        self.counter.inc_protons()
        self.init_atom()
        self.dispose_list.add(arbiter.shapes[1].spaceobject)
        self.soundfx.play('subparticle', SUBPARTICLE_VOLUME)
        return True

    def on_atom_hit_electron(self, space, arbiter):
        self.counter.inc_electrons()
        self.init_atom()
        self.dispose_list.add(arbiter.shapes[1].spaceobject)
        self.soundfx.play('subparticle', SUBPARTICLE_VOLUME)
        return True

    def on_enemy_hit_proton(self, space, arbiter):
        self.dispose_list.add(arbiter.shapes[1].spaceobject)
        return True

    def on_enemy_hit_electron(self, space, arbiter):
        self.dispose_list.add(arbiter.shapes[1].spaceobject)
        return True

    def on_proton_hit_stronghold(self, space, arbiter):
        self.counter.inc_protons()
        self.init_atom()
        self.dispose_list.add(arbiter.shapes[0].spaceobject)
        self.soundfx.play('subparticle', SUBPARTICLE_VOLUME)
        return True

    def on_electron_hit_stronghold(self, space, arbiter):
        self.counter.inc_electrons()
        self.init_atom()
        self.dispose_list.add(arbiter.shapes[0].spaceobject)
        self.soundfx.play('subparticle', SUBPARTICLE_VOLUME)
        return True

    def on_proton_hit_wall(self, space, arbiter):
        self.dispose_list.add(arbiter.shapes[0].spaceobject)
        return True

    def on_electron_hit_wall(self, space, arbiter):
        self.dispose_list.add(arbiter.shapes[0].spaceobject)
        return True
