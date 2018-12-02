'''device.py - things for doing things'''

import part
from constants import *


class Device(part.Part):
    region = [ ( 0,  0) ]
    load = 1.0

    def __init__(self, pos):
        part.Part.__init__(self, pos)
        self.energy = 0.0

    def tick(self, gs):
        self.rotate(gs)
    
    def add_energy(self, e):
        self.energy += e


class GumballMachine(Device):
    region = [ (-1,  2), ( 0,  2), ( 1,  2),
               (-1,  1), ( 0,  1), ( 1,  1),
               (-1,  0), ( 0,  0), ( 1,  0),
               (-1, -1), ( 0, -1), ( 1, -1) ]
    
    def __init__(self, pos, gumballs=3):
        Device.__init__(self, pos)
        self.gumballs = gumballs

    def tick(self, gs):
        Device.tick(self, gs)
        if self.energy > ENERGY_COST_GUMBALL and self.gumballs > 0:
            self.energy -= ENERGY_COST_GUMBALL
            self.gumballs -= 1
            gs.add_elf((self.pos[0], self.pos[1] - 1))

    def get_description(self, gs):
        if self.gumballs > 0:
            return "Gumball machine (elves: %d, power share: %d%%)." % (self.gumballs, gs.get_power_share(self) * 100)
        return "Gumball machine (empty)."


class Factory(Device):
    initialefficiency = 100.0
    minefficiency = 5.0
    name = "Unsubclassed Factory"
    def __init__(self, pos):
        Device.__init__(self, pos)
        self.efficiency = self.initialefficiency

    def tick(self, gs):
        Device.tick(self, gs)
        self.efficiency -= self.energy * EFFICIENCY_DECAY_RATE
        self.efficiency = max(self.efficiency, self.minefficiency)
        self.output(gs, self.energy * self.efficiency * 0.01)
        self.energy = 0
    
    def get_description(self, gs):
        return "%s (efficiency: %d%%, power share: %d%%)." % (self.name, self.efficiency, gs.get_power_share(self) * 100)


class RubberFactory(Factory):
    region = [ (-1,  3), ( 0,  3), ( 1,  3),
               (-1,  2), ( 0,  2),
               (-1,  1), ( 0,  1), ( 1,  1),
               (-1,  0), ( 0,  0), ( 1,  0) ]
    name = "Rubber Factory"
    def output(self, gs, amt):
        gs.rubber += amt



class MetalFactory(Factory):
    region = [ (-1,  3), ( 0,  3),
               (-1,  2), ( 0,  2), ( 1,  2),
               (-1,  1), ( 0,  1), ( 1,  1),
               (-1,  0), ( 0,  0), ( 1,  0) ]
    name = "Metal Factory"    
    def output(self, gs, amt):
        gs.metal += amt
  
class HeavyRubberFactory(RubberFactory):
    region = [                               ( 2,  4), ( 3,  4),
               (-1,  3), ( 0,  3), ( 1,  3), ( 2,  3), ( 3,  3),
               (-1,  2), ( 0,  2), ( 1,  2), ( 2,  2), ( 3,  2),
               (-1,  1), ( 0,  1), ( 1,  1), ( 2,  1), ( 3,  1),
               (-1,  0), ( 0,  0), ( 1,  0), ( 2,  0), ( 3,  0) ]
    name = "Heavy Rubber Factory"
    initialefficiency = 200.0
    minefficiency = 10.0  

class HeavyMetalFactory(MetalFactory):
    region = [           (-4,  5),                     (-1,  5),
                         (-4,  4), (-3,  4), (-2,  4), (-1,  4),
                         (-4,  3), (-3,  3), (-2,  3),
                         (-4,  2), (-3,  2), (-2,  2),
                         (-4,  1), (-3,  1), (-2,  1),
               (-5,  0), (-4,  0), (-3,  0), (-2,  0), (-1,  0), (0,  0) ]
    name = "Heavy Metal Factory"
    initialefficiency = 200.0
    minefficiency = 10.0  
