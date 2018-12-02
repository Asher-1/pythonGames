from math import atan2, degrees
from random import random
from util import Vector
from models import models

class AI(object):
    def __init__(self, racer):
        self.racer = racer
        self.track = racer.track
        difficulty = self.racer.model.game.currentLevel.difficulty
        if 'easy' in difficulty.lower():
            models[0].morph(self.racer)
        elif 'medium' in difficulty.lower():
            models[1].morph(self.racer)
        elif 'hard' in difficulty.lower():
            models[-1].morph(self.racer)
        handicap = int(self.racer.model.game.currentLevel.levelId) / 100.0 + 1
        self.racer.power *= handicap

    def move(self):
        """ Redefine this to implement different AIs"""
        pass

class BasicAI(AI):
    def __init__(self, racer):
        super(BasicAI, self).__init__(racer)
        self.getOutOfTheWay = 0
    def move(self):
#        return
        if self.racer.hasWon:
            if self.getOutOfTheWay > 200:
                self.racer.engine_off()
            else:
                self.getOutOfTheWay += 1
                self.racer.stop_right()
                self.racer.stop_left()
        else:
            self.racer.engine_on()
            headingCheckpoint = self.track.checkpoints[self.racer.next]
            diff = headingCheckpoint.pos - Vector(*self.racer.position)
            heading = degrees(atan2(-diff.imag, diff.real))
            heading = (heading - self.racer.rotation) % 360
            if 15 < heading <= 180:
                self.racer.stop_left()
                self.racer.start_right()
            elif 180 < heading < 345:
                self.racer.stop_right()
                self.racer.start_left()
            else:
                self.racer.stop_right()
                self.racer.stop_left()
            if self.racer.ropes[0] is None:
                if random() > 0.99:
                    self.racer.throw_rope (0, 90)
            else:
                if self.racer.ropes[0].line.length < 15:
                    self.racer.detach_rope (0)

class FishAI():
    def __init__ (self, fish):
        self.fish = fish
        self.goingTo = 0
    def move(self):
        self.fish.engine_on()
        headingPoint = self.fish.points[self.goingTo]
        if abs(headingPoint - Vector(*self.fish.position)) < 30: # Close enough
            self.goingTo = (self.goingTo + 1) % len(self.fish.points)
        diff = headingPoint - Vector(*self.fish.position)
        heading = degrees(atan2(-diff.imag, diff.real))
        heading = (heading - self.fish.rotation) % 360
        if 15 < heading <= 180:
            self.fish.stop_left()
            self.fish.start_right()
        elif 180 < heading < 345:
            self.fish.stop_right()
            self.fish.start_left()
        else:
            self.fish.stop_right()
            self.fish.stop_left()

