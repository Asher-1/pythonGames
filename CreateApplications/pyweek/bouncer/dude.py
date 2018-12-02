#!/usr/bin/python

from datetime import datetime
from random import randint, choice
# Panda Engine imports
from panda3d.bullet import BulletSphereShape, BulletRigidBodyNode
from panda3d.core import Vec3, BitMask32, Point3, CardMaker, NodePath
from direct.task.Task import Task

# Game imports


### TODO: Convert this to a object class rather, to support easier spawning
#----------------------------------------------------------------------#

class Dude():

    def __init__(self, _parent=None):
        self.parent = _parent

        self.dudes = {}
        self.dudesToSpawn = 10

        # Spawner
        self.secondsTime = 0
        self.count = 0
        self.maxDudesAllowed = 20

    def start(self):
        #taskMgr.add(self.timer, "Dude_Spawn_Timer", 0)
        taskMgr.add(self.update, "Dude_Spawner_Task", 0)

        # Start
        for x in range(0, 5):
            self.dudeSpawn()

    def stop(self):
        #taskMgr.remove("Dude_Spawn_Timer")
        taskMgr.remove("Dude_Spawner_Task")
        for name in self.dudes.keys():
            self.dudes[name].removeNode()
            #self.parent.physics_world.removeRigidBody(self.dudes[name].node())
        self.dudes = {}

    def update(self, task):
        ### TODO:
        # starts with 3.0
        # moves to 1.5 in 2 min
        # moves to 0.8 in 2.5 mins
        # moves to 0.3 in 1min
        # 0.1? doable

        spawnTime = 1.8
        if base.difficulty == 0:
            spawnTime = 1.8
        if base.difficulty == 1:
            spawnTime = 0.8
        if base.difficulty == 2:
            spawnTime = 0.3

        if task.time > spawnTime:
            if self.getDudesCount() < self.maxDudesAllowed:
                self.dudeSpawn()
                return Task.again

            return Task.again

        return Task.cont

    def timer(self, task):
        self.secondsTime = int(task.time)
        return Task.cont

    def getDudesCount(self):
        return len(self.dudes)

    def dudeSpawn(self):
        choices = ["blue", "red", "blue"]
        if base.difficulty == 0:
            choices = ["blue", "red", "blue"]
        if base.difficulty == 1:
            choices = ["blue", "red", "red"]
        if base.difficulty == 1:
            choices = ["blue", "red", "red", "red"]

        _type = choice(choices)
        _pos = choice(self.parent.spawnPoints)#Point3(randint(-5, 5), 0, 8)

        self.count += 1

        if _type == "blue":
            # make blue dudes they are good
            body = self.createBody(self.count, _type, _pos)

        if _type == "red":
            body = self.createBodyBad(self.count, _type, _pos)

        self.dudes[body[0]] = body[1]
        #print (self.dudes)


    def createBody(self, _count, _type, _pos=(0, 0, 0)):
        radius = 0.4
        shape = BulletSphereShape(radius)

        name = _type+"Dude"+str(_count)

        node = BulletRigidBodyNode(name)
        node.setMass(2.0)
        node.addShape(shape)
        #node.setDeactivationEnabled(False)
        np = render.attachNewNode(node)
        np.setCollideMask(BitMask32.allOn())

        self.parent.physics_world.attachRigidBody(node)

        np.setPos(_pos)

        #model = loader.loadModel("assets/dude")
        #model.reparentTo(np)
        #model.setScale(0.4)

        dudeID = [1, 2, 3]
        tex = loader.loadTexture("dudes/dude{}_good.png".format(choice(dudeID)))
        cm = CardMaker('spritesMaker')
        sprite = NodePath(cm.generate())
        sprite.setTexture(tex)
        sprite.reparentTo(np)
        sprite.setPos(-0.4, 0, -0.4)
        sprite.setCompass(render)
        sprite.setTransparency(1)
        sprite.setScale(0.8)

        return name, np

    def createBodyBad(self, _count, _type, _pos=(0, 0, 0)):
        radius = 0.4
        shape = BulletSphereShape(radius)

        name = _type+"Dude"+str(_count)

        node = BulletRigidBodyNode(name)
        node.setMass(2.0)
        node.addShape(shape)
        #node.setDeactivationEnabled(False)
        np = render.attachNewNode(node)
        np.setCollideMask(BitMask32.allOn())

        self.parent.physics_world.attachRigidBody(node)

        np.setPos(_pos)

        #model = loader.loadModel("assets/badDude")
        #model.reparentTo(np)
        #model.setScale(0.4)

        dudeID = [1, 2, 3]
        tex = loader.loadTexture("dudes/dude{}_bad.png".format(choice(dudeID)))
        cm = CardMaker('spritesMaker')
        sprite = NodePath(cm.generate())
        sprite.setTexture(tex)
        sprite.reparentTo(np)
        sprite.setPos(-0.4, 0, -0.4)
        sprite.setCompass(render)
        sprite.setTransparency(1)
        sprite.setScale(0.8)

        return name, np
