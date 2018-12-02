import cocos
from cocos.scene import Scene

from world import World
from util import Vector, to_tuple, cargar
from physics import Physics, SimulatedBody, Shaped, Rope
from endrace import EndOfRaceScreen
from soga import Soga
import tabla
from controls import ControlLayer
from math import radians, sin, cos, degrees
from random import randint
from ais import BasicAI, FishAI
from models import currentModel
import os.path

DEGREE = Vector (cos(radians(-1)), sin(radians(-1)))
OCTANT = Vector (cos(radians(-45)), sin(radians(-45)))

class Mover(cocos.sprite.Sprite, Shaped):

    power = 100.0 # Acceleration force
    rotspeed = 1.0 # Max angular velocity (radians/s)
    rotpower = 400.0 # Max momentum applied by maneuver jets

    def __init__ (self, model, initialPosition, filename):
        super(Mover, self).__init__(filename)
        self.model = model
        self.game = model.game
        self.track = model.world
        self.ph = model.ph
        self.position = initialPosition.position
        self.rotation = initialPosition.rotation
        self.engine = False
        self.turningLeft = self.turningRight = False
        self.desired_w = 0.0 # Desired angular velocity

    def update(self, delta):
        pass
    # Movement:
    def engine_on(self):
        self.engine = True

    def engine_off(self):
        self.engine = False

    def start_left(self):
        if not self.turningLeft:
            self.turningLeft = True
            self.desired_w += self.rotspeed

    def stop_left(self):
        if self.turningLeft:
            self.turningLeft = False
            self.desired_w -= self.rotspeed

    def start_right(self):
        if not self.turningRight:
            self.turningRight = True
            self.desired_w -= self.rotspeed

    def stop_right(self):
        if self.turningRight:
            self.turningRight = False
            self.desired_w += self.rotspeed

    def set_forces(self):
        force = Vector (0.0, 0.0)
        # thrust
        if self.engine:
            force += (DEGREE ** self.rotation)*self.power
        else:
            pass
        # rotation
        rotate_to = (self.desired_w - self.shape.angular_v)
        if rotate_to < -0.05:
            mom = -self.rotpower
        elif rotate_to > 0.05:
            mom = self.rotpower
        else:
            mom = self.rotpower*rotate_to
        # TODO: ropes!
        
        self.shape.add_forces (force, mom)

class FishMover(Mover):
    def __init__(self, model, fish):
        super(FishMover, self).__init__(model, fish, cargar(os.path.join('items','ballena 001.png')))
        self.power = 600
        self.points = fish.points
        self.load (os.path.join('shapes','ballena01.shape'))

class Racer(Mover):
    RANGE = 200.0 # rope range
    power = 100.0 # Acceleration force
    rotspeed = 1.0 # Max angular velocity (radians/s)
    rotpower = 400.0 # Max momentum applied by maneuver jets

    def __init__ (self, model, initialPosition, filename):
        super(Racer, self).__init__(model, initialPosition, filename)
        self.next = 0         # 0 <= self.next < len(self.track.checkpoints)
        self.laps = -1
        self.load (os.path.join('shapes','sub.shape'))
        self.hasWon = False
        self.ropes = [None]*8

    def update(self, delta):
        if self.engine and hasattr(self, 'bubbles'):
            self.bubbles.replenish()
        # Race progress logic
        if self.laps == self.track.maxlaps: return
        c = self.track.checkpoints[self.next]
        if c.has_inside(Vector(*self.position)):
            self.leave_checkpoint (c)
            if self.next==0:
                self.laps += 1
                if self.laps == self.track.maxlaps:
                    self.onVictory()
            self.next += 1
            if self.next == len(self.track.checkpoints):
                self.next = 0
            self.enter_checkpoint (self.track.checkpoints[self.next])

    def leave_checkpoint (self, checkpoint):
        pass
        
    def enter_checkpoint (self, checkpoint):
        pass

    def throw_rope (self, index, direction):
        if self.ropes[index] is None:
            angle = DEGREE**self.rotation * OCTANT**index
            
            # FIXME: calcular direccion
            src, psrc, dist = self.ph.find (self.shape.pos, angle, self.RANGE)
            if src is not None:
                dst, pdst, dist = self.ph.find (self.shape.pos+angle*0.1, angle, self.RANGE)
                if dst is not None:
                    self.ropes[index] = self.model.new_rope (src.body, psrc, dst.body, pdst)
            else:
                print "No source!?"

    def detach_rope (self, index):
        if self.ropes[index] is not None:
            self.ropes[index].broken = True
            self.ropes[index] = None

    def onVictory(self):
        """ Do your victory dance """
        self.hasWon = True

class Hero(Racer):

    def leave_checkpoint (self, checkpoint):
        checkpoint.highlight(False)

    def enter_checkpoint (self, checkpoint):
        checkpoint.highlight(True)

    def onVictory(self):
        self.track.stopTime()
        level = self.game.currentLevel

        if tabla.tabla.es_mejor (self.track.getElapsedTime(), level.name):
            hiscores = tabla.CapaTabla (self.track.getElapsedTime(), nombre=None, levelName=level.name, color0=(255,255,255,255))
            hiscores.onFinished = self.endRace
            self.parent.control.add (hiscores, z=100)
            
        else:
            self.endRace()

    def endRace(self):
        level = self.game.currentLevel
        finishingPosition = 1 + len([x for x in self.model.ships if x.laps == x.track.maxlaps])
        self.game.completeCurrentLevel(finishingPosition)
        eor = EndOfRaceScreen(level, self.track.getElapsedTime(),
                              finishingPosition, self.game.score)
        cocos.director.director.push(eor)

class pseudorope(cocos.draw.Line):
    def remove(self):
        self.parent.remove(self)
        self.model.ropes.remove (self)

class DummyModel():
    def __init__ (self, theGame, filename):
        self.game = theGame
        self.ph = Physics()
        self.world = World(os.path.join('levels', filename))
        self.world.checkpoints[0].highlight(True)
        self.ships = []
        self.ais = []
        self.ropes = []
        self.hero = Hero (self, self.world.initialposs[0], 'sub.png')
        currentModel().morph(self.hero) # En forma de submarino!
        for i, oponent in enumerate(self.world.initialposs):
            if i==0: continue # Hero position
            r = Racer(self, oponent, 'bot%d.png' % min(i,3))
            self.ships.append (r)
            self.ais.append(BasicAI(r))
            self.ph.add (r.shape)
        self.fish = []
        for fish in self.world.fish:
            f = FishMover(self, fish)
            self.fish.append (f)
            self.ais.append(FishAI(f))
            self.ph.add (f.shape)
        self.ph.add (self.hero.shape)
        self.world.add_shapes (self.ph)
        

    def update(self, delta):
        self.ph.step (delta)
        for ship in self.ships:
            ship.update(delta)
        for fish in self.fish:
            fish.update(delta)
        self.hero.update(delta)
        for oponent in self.ais:
            oponent.move()

    def new_rope (self, src, srcp, dst, dstp):
        pic = Soga(srcp, dstp, self)
        self.ropes.append(pic)
        length = abs(srcp-dstp)
        srcp -= src.shape.pos
        srcp /= DEGREE**src.rotation
        dstp -= dst.shape.pos
        dstp /= DEGREE**dst.rotation
        r = Rope(pic, src.shape, srcp, dst.shape, dstp,
            length, 10, 15, 999999, 100000, self.ph.time, 2) # Tunable arguments
        self.ph.ropes.append(r)
        return r

