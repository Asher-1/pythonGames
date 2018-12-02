import random

from pymunk import Body, moment_for_circle, Circle

import cocos
from cocos.actions import Repeat, RotateBy

import gamelib.data as d
from gamelib.collision import C_ATOM, G_STRONGHOLD
from gamelib.spaceobject import SpaceObject


MASS = 10
RADIUS = 57
FONT_SIZE=20
RADIUS_INC_FACTOR = 0.2


class Atom(cocos.cocosnode.CocosNode, SpaceObject):

    def __init__(self, pos):
        super(Atom, self).__init__()
        self.position = pos

        self.limit = cocos.sprite.Sprite(d.img('ball'))
        self.limit.charge = 0
        self.add(self.limit, z=2)

        self.electrons = []
        self.protons = []

        self.label = cocos.text.Label('0', font_size=FONT_SIZE, bold=True,
                                      anchor_x='center', anchor_y='center')
        self.add(self.label, z=1)

        self.add_electron()
        self.add_proton()

    def add_electron(self):
        for electron in self.electrons:
            electron.stop()

        new_e = cocos.sprite.Sprite(d.img('atom_electron'),
                                    anchor=self.get_electron_anchor())
        self.add(new_e, z=0)
        self.electrons.append(new_e)

        len_e = float(len(self.electrons))
        for i, electron in enumerate(self.electrons):
            electron.rotation = 360.0 / len_e * i
            electron.do(Repeat(RotateBy(90.0, 2.0)))
        self.update_label()

    def update_label(self):
        self.label.element.text = '{0:+}'.format(self.charge)

    def get_electron_anchor(self):
        return (0, 50 * self.limit.scale)

    def get_proton_position(self):
        total = 20 * self.limit.scale
        x = random.random() * total - total / 2.0
        y = random.random() * total - total / 2.0
        return x, y

    def add_proton(self):
        proton = cocos.sprite.Sprite(d.img('atom_proton'),
                                     position=self.get_proton_position())
        self.add(proton, z=0)

        self.limit.scale = 1.0 + self.positive_charge * RADIUS_INC_FACTOR
        for electron in self.electrons:
            electron.image_anchor = self.get_electron_anchor()
        self.protons.append(proton)
        self.update_label()

    @property
    def charge(self):
        return self.positive_charge + self.negative_charge

    @property
    def negative_charge(self):
        return -len(self.electrons)

    @property
    def positive_charge(self):
        return len(self.protons)

    def init_physics(self):
        radius = RADIUS * self.limit.scale
        self.body = Body(MASS, moment_for_circle(MASS, 0, radius))
        self.body.position = self.position
        self.shape = Circle(self.body, radius)
        self.shape.collision_type = C_ATOM
        self.shape.group = G_STRONGHOLD
        self.shape.spaceobject = self

    def shoot(self):
        self.init_physics()

        self.body.apply_force((1000 * self.negative_charge, 0))
        self.body.apply_force((1000 * self.positive_charge, 0))
        self.body.apply_force((0, 1000))
        self.body.apply_impulse((0, 3000))
