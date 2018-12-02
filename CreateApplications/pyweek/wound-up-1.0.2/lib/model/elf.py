'''elf.py - simulating little people'''

import random

import path
from colour import elfname, elfbio


class Elf(object):

    def __init__(self, gs, pos=(0, 0)):
        self.gs = gs
        self.path = [pos]
        self.offset = 0.0
        self.speed = 0.1
        self.falling_speed = 0.3
        self.is_falling = False
        self.task = None
        self.female = random.random() < 0.5
        self.name = elfname.random_name(self.female)
        self.bio = elfbio.random_bio()

    def tick(self, gs):
        if len(self.path) == 1:
            self.is_falling = self.test_falling()
            if self.is_falling:
                self.offset += self.falling_speed
                while self.offset >= 1.0:
                    self.offset -= 1.0
                    self.path[0] = (self.path[0][0], self.path[0][1]-1)
            return

        self.offset += self.speed
        while self.offset >= 1.0:
            self.offset -= 1.0
            self.path.pop(0)
            if len(self.path) == 1:
                self.offset = 0.0
                break
    
    def set_path(self, path):
        if self.is_falling:
            raise ValueError("tried to set new path for elf in midair")
        if path[0] != self.path[0]:
            raise ValueError("tried to set new path for elf with illegal start")
        elif len(self.path) == 1:  # currently stopped, can do whatever
            self.path = path
        elif len(path) == 1: # move back to centre of cell and stop
            self.path = self.path[:2]
            self.path.reverse()
            self.offset = 1.0 - self.offset
        elif path[1] == self.path[1]: # current movement is ok already
            self.path = path
        else: # need to back up and start again from last cell
            self.path = [self.path[1]] + path
            self.offset = 1.0 - self.offset

    def stop(self):
        self.set_path([self.path[0]])

    def send_to(self, gs, pos):
        p = path.find_best_path(gs.pgrid, self.path[0], pos)
        if p is None:
            self.stop()
            return False
        else:
            self.set_path(p)
            return True
    
    def is_climbing(self):
        if len(self.path) == 1:
            return False
        return self.path[1][1] != self.path[0][1]

    def test_falling(self):
        if self.is_falling and not self.gs.pgrid.cell_has_floor(self.path[0]): return True
        return not self.gs.pgrid.cell_supported(self.path[0])
