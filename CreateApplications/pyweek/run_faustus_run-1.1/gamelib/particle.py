from random import randint
from gamelib import vector
import pyglet
from pyglet.gl import *
from gamelib import app
from gamelib.constants import *

class PSGroup(pyglet.graphics.Group):
    def __init__(self, r):
        super(PSGroup, self).__init__()
        self.r = r * app.interface.content_size[1] / WORLD_HEIGHT
    def set_state(self):
        glEnable(GL_POINT_SMOOTH)
        glPointSize(self.r)

class ParticleSystem(object):

    def __init__(self,
            size=10,
            pos=(0,0),
            color=(0,0,0),
            alpha=255,
            radius=20,
            speed=15,
            time=210,
            autoadd=False
            ):

        self.size = size
        self.pos = tuple(pos)
        self.color = tuple(color) + (0,)
        self.alpha = alpha
        self.radius = radius
        self.speed = speed
        self.time = time
        self.autoadd = autoadd

        self.batch = pyglet.graphics.Batch()
        self.vlist = self.batch.add(size, GL_POINTS, PSGroup(radius),
                ('v2f', (0.0, 0.0) * size),
                ('c4B', self.color * size),
                )
        self.next_idx = 0
        self.particle_times = [None] * size

        if autoadd:
            for _ in xrange(size):
                self.add_particle(vector.zero)

    def add_particle(self, pos, color=None):
        idx = self.next_idx
        self.vlist.vertices[2*idx:2*(idx+1)] = tuple(pos + self.pos)
        self.vlist.colors[4*idx+3] = self.alpha
        if color is not None:
            self.vlist.colors[4*idx:4*idx+3] = [color]
        self.next_idx += 1
        self.particle_times[idx] = self.time

    def destroy_particle(self, idx):
        self.vlist.colors[4*idx+3] = 255
        self.particle_times[idx] = None

    def tick(self):
        pt = self.particle_times
        vs = self.vlist.vertices
        s = self.speed
        for idx in xrange(self.size):
            if pt[idx] > 1:
                pt[idx] -= 1
                vs[2*idx] += randint(-s, s)
                vs[2*idx+1] += randint(-s, s)
            elif pt[idx]:
                self.destroy_particle(idx)

    def is_dead(self):
        return self.particle_times == [None] * self.size
