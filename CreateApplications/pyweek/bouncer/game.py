#!/usr/bin/python

from random import choice

# Panda Engine imports
from panda3d.core import (
    CardMaker,
    NodePath,
    DirectionalLight,
    PointLight,
    VBase4)
from direct.task.Task import Task

# Game imports
from player import Player
from builder import Builder
from dude import Dude
from hud import Hud


# ----------------------------------------------------------------------#

class Game():

    def __init__(self, _parent=None):
        self.parent = _parent

        # Containers
        self.game_objects = {}
        self.game_doors = {}
        self.game_objects_np = render.attachNewNode("Game_Objects")
        self.game_doors_np = render.attachNewNode("Player_Doors")
        self.game_doors_np.setPos(0, 0, 0)
        self.game_counter_node = None
        self.game_collector_nodes = []

        self.redDudesCount = 0
        self.blueDudesCount = 0

        # Physics world
        self.physics_world = None
        self.builder = Builder(self)

        # level lights
        self.directLight = None

        # Dude class
        self.dude = None
        self.spawnPoints = self.builder.spawnPoints

        # HUD
        self.hud = Hud()

        # Lightshow
        self.elapsed = 0.0

    def start(self, levelID, winCondition=25):
        self.winCondition = winCondition

        self.loadLevel("assets/level{}".format(levelID))
        self.loadLights()

        # player
        self.loadPlayer("default")
        self.loadDude()

        # Timer
        taskMgr.add(self.update, "Game_Update_Task", 0)

        self.hud.show()

        # start the Lightshow
        taskMgr.add(self.discoLightTask, "the lightshow")

    def stop(self):
        self.player.stop()
        self.dude.stop()
        self.builder.cleanup()
        self.physics_world = None
        render.clearLight()
        self.directLight = None
        self.hud.hide()
        taskMgr.remove("the lightshow")

    def update(self, task):

        if self.game_counter_node is None:
            return

        ghost = self.game_counter_node.node()
        # for node in ghost.getOverlappingNodes():
        #
        #     if "red" in node.name:
        #         self.redDudesCount += 1
        #         self.physics_world.removeRigidBody(self.dude.dudes[node.name].node())
        #         self.dude.dudes[node.name].removeNode()
        #         self.hud.update(self.redDudesCount, self.blueDudesCount)
        #         del self.dude.dudes[node.name]
        #         break
        #
        #
        #     elif "blue" in node.name:
        #         self.blueDudesCount += 1
        #         self.physics_world.removeRigidBody(self.dude.dudes[node.name].node())
        #         self.dude.dudes[node.name].removeNode()
        #         self.hud.update(self.redDudesCount, self.blueDudesCount)
        #         del self.dude.dudes[node.name]
        #         break

        if self.redDudesCount > self.blueDudesCount:
            base.messenger.send("lostGame")
            return Task.done
        elif self.blueDudesCount >= self.winCondition:
            base.messenger.send("wonGame")
            return Task.done

        # for collectorGhostNP in self.game_collector_nodes:
        #     collectorGhost = collectorGhostNP.node()
        #     for node in collectorGhost.getOverlappingNodes():
        #         if "red" in node.name:
        #             self.physics_world.removeRigidBody(self.dude.dudes[node.name].node())
        #             self.dude.dudes[node.name].removeNode()
        #             self.hud.update(self.redDudesCount, self.blueDudesCount)
        #             del self.dude.dudes[node.name]

        return Task.cont

    def setPhysicsWorld(self, _physicsworld):
        self.physics_world = _physicsworld

    #### LOADERS ####
    def loadLevel(self, _filename):
        self.builder.parseEggFile(_filename)

    def loadLights(self):
        # Set a simple light
        dlight = DirectionalLight('DirectLight')
        dlnp = render.attachNewNode(dlight)
        dlnp.setHpr(-30, 0, 0)
        render.setLight(dlnp)
        self.directLight = dlnp

        self.discoLights = []

        p1 = PointLight("PointLight1")
        p1.setColor(VBase4(1, 0, 0, 1))
        p1.setAttenuation((0.08, 0, 0.05))
        p1np = render.attachNewNode(p1)
        p1np.setPos(0, -5, 0)
        render.setLight(p1np)
        self.discoLights.append(p1)

        p2 = PointLight("PointLight2")
        p2.setColor(VBase4(0, 1, 0, 1))
        p2.setAttenuation((0.08, 0, 0.05))
        p2np = render.attachNewNode(p2)
        p2np.setPos(5, -5, 0)
        render.setLight(p2np)
        self.discoLights.append(p2)

        p3 = PointLight("PointLight3")
        p3.setColor(VBase4(0, 0, 1, 1))
        p3.setAttenuation((0.08, 0, 0.05))
        p3np = render.attachNewNode(p3)
        p3np.setPos(-5, -5, 0)
        render.setLight(p3np)
        self.discoLights.append(p3)

        p4 = PointLight("PointLight4")
        p4.setColor(VBase4(0, 0, 1, 1))
        p4.setAttenuation((0.08, 0, 0.05))
        p4np = render.attachNewNode(p4)
        p4np.setPos(-5, -5, 5)
        render.setLight(p4np)
        self.discoLights.append(p4)

        p5 = PointLight("PointLight1")
        p5.setColor(VBase4(0, 0, 1, 1))
        p5.setAttenuation((0.08, 0, 0.05))
        p5np = render.attachNewNode(p5)
        p5np.setPos(0, -5, 5)
        render.setLight(p5np)
        self.discoLights.append(p5)

        p6 = PointLight("PointLight1")
        p6.setColor(VBase4(0, 0, 1, 1))
        p6.setAttenuation((0.08, 0, 0.05))
        p6np = render.attachNewNode(p6)
        p6np.setPos(5, -5, 5)
        render.setLight(p6np)
        self.discoLights.append(p6)

    def discoLightTask(self, task):
        self.elapsed += globalClock.getDt()

        if self.elapsed > 0.75:
            for light in self.discoLights:
                newcolor = choice(
                    [VBase4(0, 0, 1, 1),
                     VBase4(0, 1, 0, 1),
                     VBase4(1, 0, 0, 1),
                     VBase4(0, 1, 1, 1),
                     VBase4(1, 0, 1, 1),
                     VBase4(1, 1, 0, 1), ]
                )
                light.setColor(newcolor)
            self.elapsed = 0.0
        return task.cont

    def loadPlayer(self, _name):
        self.player = Player(self)
        self.player.start()

    def loadDude(self):
        self.dude = Dude(self)
        self.dude.start()
