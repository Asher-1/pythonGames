'''part.py - machine part definitions'''

import math

from constants import *


class Part(object):
    region = [ ]
    load = 0.0

    def __init__(self, pos):
        self.pos = pos
        self.angle = 0.0
        self.g_ratio = 0.0
        self.diam = 1

    def get_angular_speed(self, gs):
        return gs.spring.energy * self.g_ratio * gs.load_factor * SPEED_MULTIPLIER
        
    def rotate(self, gs):
        speed = self.get_angular_speed(gs)
        
        if speed != 0:
            stepsize = 60.0 / self.diam
            targetangle = speed / gs.spring_speed * gs.spring.angle
            targetoffset = targetangle % stepsize
            self.angle = (self.angle + speed)
            offset = self.angle % stepsize
            disp = (targetoffset - offset)
            if disp > stepsize / 2:
                disp -= stepsize
            self.angle += disp
            
    def get_load(self):
        return self.load

    def get_description(self, gs):
        return ""


class Cog(Part):

    number = {1: "I", 3: "II", 5: "III", 7: "IV"}

    @staticmethod
    def get_region(diam):
        region = []
        for i in xrange(0 - diam // 2, 1 + diam // 2):
            for j in xrange(0 - diam // 2, 1 + diam // 2):
                dx = [0, abs(i) - 0.5][i != 0]
                dy = [0, abs(j) - 0.5][j != 0]
                if math.sqrt(dx**2 + dy**2) <= diam / 2.0:
                    region.append((i, j))
        return region

    def __init__(self, pos, diam):
        Part.__init__(self, pos)
        self.diam = diam

        self.region = Cog.get_region(diam)

    def tick(self, gs):
        self.rotate(gs)
        
    def get_description(self, gs):
        if self.number.has_key(self.diam):
            return "Cog (number %s)." % self.number[self.diam]
        return "Cog (number ?)."


class Spring(Part):
    region = [ (-1,  1), ( 0,  1), ( 1,  1),
               (-1,  0), ( 0,  0), ( 1,  0),
               (-1, -1), ( 0, -1), ( 1, -1) ]
    load = 1.0    
    
    def __init__(self, pos):
        Part.__init__(self, pos)
        self.g_ratio = 1.0 # always
        self.diam = 1
        self.energy = 0.0

    def rotate(self, gs):
        speed = self.get_angular_speed(gs)
        self.angle += speed

    def tick(self, gs):
        self.rotate(gs)
        
    def get_description(self, gs):
        return "Spring (power: %d, elves: %d)." % (self.energy, len(gs.winding_elves))
        
    def get_door_pos(self):
        return self.pos[0] + 1, self.pos[1]


class Belt(object):
    
    def __init__(self, part1, part2):
        self.part1 = part1
        self.part2 = part2


class BrokenBeltException(Exception):
    pass
