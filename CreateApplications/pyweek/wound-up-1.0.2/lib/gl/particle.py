from globject import *
from glstate import *

import random

class Particle(Object):
    def __init__(self, position):
        Object.__init__(self)
        if not GLState.particles:
            return
        self.setPosition((position[0], position[1], position[2] + random.gauss(0, .1)))

    def draw(self):
        if not GLState.particles:
            return
        glColor3f(0, 1, 0)
        glBegin(GL_POINTS)
        glVertex3f(0,0,0)
        glEnd()

    def tick(self):
        if not GLState.particles:
            return
        self.move((random.gauss(0, .1), random.gauss(0, .1), 0))
        return random.random() < 0.9

class ParticleSystem(Object):
    def __init__(self, position, pclass = Particle, nparts = 100, radius=0):
        Object.__init__(self)
        if not GLState.particles:
            return
        self.particles = [pclass([x + random.gauss(0, radius) for x in position]) for x in range(nparts)]
     
    def prerender(self):
        if not GLState.particles:
            return
        for p in self.particles:
            self.prerender()
    def render(self):
        if not GLState.particles:
            return
        for p in self.particles:
            p.render()

    def tick(self):
        if not GLState.particles:
            return
        dead = []
        for p in self.particles:
            if not p.tick():
                dead.append(p)
        for p in dead:
            self.modeldirty = True
            self.particles.remove(p)
        self.particles = sorted(self.particles, key= lambda x: x.position[2])
        return len(self.particles) > 0

    def numPolys(self):
        if not GLState.particles:
            return
        return sum([p.numPolys() for p in self.particles])

class ParticleManager(ParticleSystem):
    def __init__(self):
        Object.__init__(self)
        if not GLState.particles:
            return
        self.particles = []
        
    def addSystem(self, psystem):
        if not GLState.particles:
            return
        self.particles += psystem.particles
        self.particles = sorted(self.particles, key= lambda x: x.position[2])
