from cocos.sprite import Sprite
from cocos.cocosnode import CocosNode
from util import cargar, Vector, to_tuple
import os.path

from physics import Shaped

import math
from time import time

class CheckPoint (CocosNode):
    """ These first few short classes probably should inherit a 'Object'
        class that I haven't implemented yet"""
    CHECKPOINT_WIDTH = 20.0

    def __init__ (self, left=Vector(), right=Vector()):
        super(CheckPoint, self).__init__()
        self.left = left
        self.right = right
        self.highlighted = False
        self.add(Sprite(cargar('checkpoint.png'), position=to_tuple(left)), name="left")
        self.add(Sprite(cargar('checkpoint.png'), position=to_tuple(right)), name="right")
        self.add(Sprite(cargar('highlight_checkpoint.png'), position=to_tuple(left)), name="leftHL")
        self.get("leftHL").visible = False
        self.add(Sprite(cargar('highlight_checkpoint.png'), position=to_tuple(right)), name="rightHL")
        self.get("rightHL").visible = False
        self.updateRad()

    def updateRad(self):
        x1, y1 = self.get("left").position
        x2, y2 = self.get("right").position
        self.left = Vector(x1, y1)
        self.right = Vector(x2, y2)
        self.pos = (self.left + self.right) / 2
        self.get("left").pos = Vector(x1, y1)
        self.get("right").pos= Vector(x2, y2)
        d = abs (self.right-self.left)
        self.rad = math.sqrt ((d/2)**2 + self.CHECKPOINT_WIDTH ** 2) * 2

    def unserialize(self, line):
        """ Builds the object from a line from the savefile"""
        x1, y1, x2, y2 = (float(x) for x in line[11:].strip().split())
        self.get("left").position = x1, y1
        self.get("right").position = x2, y2
        self.get("leftHL").position = x1, y1
        self.get("rightHL").position = x2, y2
        self.updateRad()

    def serialize(self):
        """ Returns a string for the savefile"""
        return "Checkpoint: %f %f %f %f\n" % (to_tuple(self.left) + to_tuple(self.right))

    def has_inside (self, point):
        # Checkpoints are elliptical. Easier math
        return abs(point-self.left) + abs (point-self.right) <= self.rad
    
    def highlight(self, state):
        self.get("left").visible = not state
        self.get("right").visible = not state
        self.get("leftHL").visible = state
        self.get("rightHL").visible = state

class HalfCheckPoint (Sprite):
    def __init__ (self, pos=Vector()):
        super(HalfCheckPoint, self).__init__(cargar('checkpoint.png'), position=to_tuple(pos))
        self.pos = pos

class Rock (Sprite, Shaped):
    def __init__ (self, pos=Vector(),line=None):
        if line is None:
            super(Rock, self).__init__(cargar(os.path.join('items', 'rock.png')), position=to_tuple(pos))
            self.pos = pos
            self.shapeName = 'rock'
        else:
            x, y, shapeName = line[5:].strip().split()
            super(Rock, self).__init__(cargar(os.path.join('items', shapeName+'.png')), position=to_tuple(pos))
            self.pos = pos
            self.unserialize(line)

    def unserialize(self, line):
        x, y, shapeName = line[5:].strip().split()
        x=float(x)
        y=float(y)
        self.position = x, y
        self.pos = Vector(x, y)
        self.load (os.path.join('shapes',shapeName+'.shape'))
        self.shapeName = shapeName
    def serialize(self):
        return "Rock: %f %f %s\n" % (self.x, self.y, self.shapeName)

class InitialPosition (Sprite):
    def __init__ (self, pos=Vector(), rot=0):
        super(InitialPosition, self).__init__(cargar('sub.png'),
              position=to_tuple(pos), rotation=rot)
        self.pos = pos
    def unserialize(self, line):
        x, y, rot = line[17:].strip().split()
        self.position = (float(x), float(y))
        self.pos = Vector(*self.position)
        self.rotation = int(rot)
    def serialize(self):
        return "Initial Position: %f %f %d\n" % (self.x, self.y, self.rotation)

class Fish (Sprite):
    def __init__ (self, pos=Vector(), rot=0):
        super(Fish, self).__init__(cargar('fish1.png'), position=to_tuple(pos), rotation=rot)
        self.points = [Vector(), Vector()]
        self.pos = pos
    def unserialize(self, line):
        x, y, rot, x0, y0, x1, y1 = line[5:].strip().split()
        self.position = (float(x), float(y))
        self.pos = Vector(*self.position)
        self.rotation = int(rot)
        self.points = [Vector(float(x0),float(y0)), Vector(float(x1),float(y1))]

    def serialize(self):
        return "Fish: %f %f %d %s %s %s %s\n" % (self.x, self.y, self.rotation, self.points[0].real, self.points[0].imag, self.points[1].real, self.points[1].imag)

class World():
    """ This is just a bag of obstacles and checkpoints for now """
    def __init__(self, filename=None, maxlaps=3):
        self.items = []
        self.checkpoints = []
        self.initialposs = []
        self.fish = []
        if not filename is None:
            self.load(filename)
        self.maxlaps = maxlaps
        self.startTime = None
        self.elapsedTime = None

    def load(self, filename):
        f = open(filename)
        self.items = []
        lNum = 0
        for line in f.readlines():
            lNum += 1
            if line.startswith('Rock:'):
                try:
                    rock = Rock(line=line)
                    self.items.append (rock)
                except:
                    print "Invalid rock definition in %s, line %s" % (filename, lNum)
            elif line.startswith('Checkpoint:'):
                try:
                    chkpt = CheckPoint()
                    chkpt.unserialize(line)
                    self.checkpoints.append (chkpt)
                except:
                    print "Invalid checkpoint definition in %s, line %s" % (filename, lNum)
            elif line.startswith('Initial Position:'):
                try:
                    initialpos = InitialPosition()
                    initialpos.unserialize(line)
                    self.initialposs.append (initialpos)
                except:
                    print "Invalid initial position definition in %s, line %s" % (filename, lNum)
            elif line.startswith('Fish:'):
                try:
                    fish = Fish()
                    fish.unserialize(line)
                    self.fish.append (fish)
                except:
                    print "Invalid fish definition in %s, line %s" % (filename, lNum)

    def setStartTime(self):
        self.startTime = time()
    def getElapsedTime(self):
        if self.startTime is None:
            return '00:00:00'
        elif self.elapsedTime is None:
            newtime = time() - self.startTime
            return '%02d:%02d:%02d' % (int(newtime) / 60, int(newtime) % 60, int(newtime*100)%100)
        else:
            return self.elapsedTime
    def stopTime(self):
        self.elapsedTime = self.getElapsedTime()

    def save(self, filename):
        f = open(filename, 'w')
        for item in self.items:
            f.write(item.serialize())
        for chkpt in self.checkpoints:
            f.write(chkpt.serialize())
        for initialpos in self.initialposs:
            f.write(initialpos.serialize())
        for fish in self.fish:
            f.write(fish.serialize())

    def add_shapes (self, ph):
        for i in self.items:
            ph.add (i.shape)

if __name__ == '__main__':
    # Tests?
    pass
