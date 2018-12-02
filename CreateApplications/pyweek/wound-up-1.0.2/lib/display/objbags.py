'''objbags.py - globject collections to facilitate management and rendering'''

import random

from OpenGL.GL import *

from globjects import *


class ObjBag(object):

    def __init__(self):
        self.objs = dict()
        self.dirty = True
        self.displist = glGenLists(1)

    def update(self, objlist):
        dicty = isinstance(objlist, dict)
        removals = []
        for obj in self.objs:
            if obj not in objlist:
                removals.append(obj)
                self.dirty = True
        for obj in removals:
            del self.objs[obj]
        for obj in objlist:
            if obj not in self.objs:
                if dicty:
                    self.objs[obj] = self.objClass(obj, self, objlist[obj])
                else:
                    self.objs[obj] = self.objClass(obj, self)
                self.dirty = True
            self.updateObj(obj)

    def updateObj(self, obj):
        pass

    def render(self):
        if not self.objs:
            return
        for obj in self.objs.values():
            obj.prerender()
        if self.dirty:
            glNewList(self.displist, GL_COMPILE)
            for obj in self.objs.values():
                obj.render()
            glEndList()
            self.dirty = False
        glCallList(self.displist)
    
    def numPolys(self):
        return sum([obj.numPolys() for obj in self.objs.values()])


class CogBag(ObjBag):
    objClass = Cog

    def updateObj(self, cog):
        parity = (cog.pos[0] + cog.pos[1] + (cog.diam // 2)) % 2
        self.objs[cog].setAngle(cog.angle + ([90.0/cog.diam, 0][parity]))


class DeviceBag(ObjBag):
    objClass = DeviceFactory

    def updateObj(self, device):
        self.objs[device].setAngle(device.angle)


class ElfBag(ObjBag):
    objClass = Elf
    
    def updateObj(self, elf):
        angle = math.cos(sum(self.objs[elf].position) * math.pi) * 30
        offset = 0.5
        if len(elf.path) == 1:
            if not elf.is_falling:
                self.objs[elf].axis = (0,1,0)
                self.objs[elf].setPosition(elf.path[0])
            else:
                self.objs[elf].axis = (0,0,1)
                self.objs[elf].setPosition((elf.path[0][0], elf.path[0][1] - offset))
                self.objs[elf].setAngle((elf.path[0][0] + elf.path[0][1] - offset) * 90)
        else:
            self.objs[elf].axis = (0,1,0)
            if elf.path[0][0] < elf.path[1][0]:
                angle += 180
            elif elf.path[0][1] != elf.path[1][1]:
                angle += 270
                offset = 1.2
            e0x = elf.path[0][0]; e0y = elf.path[0][1]
            e1x = elf.path[1][0]; e1y = elf.path[1][1]
            self.objs[elf].setPosition(((1 - elf.offset) * e0x + elf.offset * e1x, (1 - elf.offset) * e0y + elf.offset * e1y, offset))
            self.objs[elf].setAngle(angle)


class BeltBag(ObjBag):
    objClass = Belt


class PlatBag(ObjBag):
    objClass = Plat
    def __init__(self):
        ObjBag.__init__(self)
        self.rng = random.Random()
    def update(self, platlist):
        pstarts = sorted(platlist.keys(), key = reversed)
        psizes = Plat._platObjs.keys()
        
        y = 0
        for plat in pstarts:
            if plat[1] != y:
                self.rng.seed(plat[1])
                y = plat[1]
            while platlist[plat] not in psizes:
                newsize = None
                while not newsize or newsize > platlist[plat]:
                    newsize = self.rng.choice(psizes)
                
                platlist[(plat[0] + newsize, plat[1])] = platlist[plat] - newsize
                platlist[plat] = newsize
                plat = (plat[0] + newsize, plat[1])
        ObjBag.update(self, zip(platlist.keys(), platlist.values()))


class LadderBag(ObjBag):
    objClass = Ladder


class TaskBag(ObjBag):
    objClass = TaskFactory

    def __init__(self, elfbag):
        self.elfbag = elfbag
        ObjBag.__init__(self)
    
    def updateObj(self, task):
        self.objs[task].update()
