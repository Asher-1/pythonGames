import random

import cocos
from cocos.actions import FadeOut

from pymunk import Body, moment_for_box, Circle

MASS = 1

import gamelib.data as d
from gamelib.spaceobject import SpaceObject
from gamelib.collision import C_ENEMY


MASS = 0.1
RADIUS = 31
WIDTH = RADIUS * 2
HEIGHT = RADIUS * 2


class Enemy(cocos.sprite.Sprite, SpaceObject):
    def __init__(self, pos):
        super(Enemy, self).__init__(d.img('enemy'), position=pos)
        self.was_hit = False

        self.body = Body(MASS, moment_for_box(MASS, WIDTH, HEIGHT))
        self.body.position = pos
        self.shape = Circle(self.body, RADIUS)
        self.shape.collision_type = C_ENEMY
        self.shape.spaceobject = self

        self.body.apply_force((random.random() * 3 - 1.5, -4))

    def dissapear(self, duration):
        self.do(FadeOut(duration))
