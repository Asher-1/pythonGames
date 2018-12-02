import random

import cocos

from pymunk import Body, moment_for_circle, Circle

from gamelib.spaceobject import SpaceObject
from gamelib.collision import C_ELECTRON, C_PROTON
import gamelib.data as d


MASS = 1


class Subparticle(cocos.sprite.Sprite, SpaceObject):
    def __init__(self, position):
        super(Subparticle, self).__init__(self.get_img())
        self.position = position
        self.init_physics()

        self.opacity = 0
        self.do(cocos.actions.FadeIn(0.3))

    def init_physics(self):
        radius = self.get_radius()
        self.body = Body(MASS, moment_for_circle(MASS, 0, radius))
        self.body.position = self.position
        self.shape = Circle(self.body, radius)
        self.shape.collision_type = self.get_collision_type()
        self.shape.spaceobject = self
        self.apply_forces()

    def get_img(self):
        return d.img(self.get_img_name())


class Electron(Subparticle):
    def get_img_name(self):
        return 'electron'

    def get_radius(self):
        return 15

    def get_collision_type(self):
        return C_ELECTRON

    def apply_forces(self):
        self.body.apply_force((-20, random.random() * 20 - 10))
        self.body.apply_impulse((60, random.random() * 60 - 30))


class Proton(Subparticle):
    def get_img_name(self):
        return 'proton'

    def get_radius(self):
        return 21

    def get_collision_type(self):
        return C_PROTON

    def apply_forces(self):
        self.body.apply_force((20, random.random() * 20 - 10))
        self.body.apply_impulse((-60, random.random() * 60 - 30))
