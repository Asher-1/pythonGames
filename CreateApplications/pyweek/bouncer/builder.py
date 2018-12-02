#!/usr/bin/python

# Panda Engine imports
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletHingeConstraint, BulletPlaneShape
from panda3d.bullet import BulletTriangleMesh, BulletTriangleMeshShape, BulletGhostNode
from panda3d.core import Vec3, BitMask32, Point3, VBase3, Mat3

# Game imports

#----------------------------------------------------------------------#

class Builder():

    def __init__(self, _parent=None):
        self.parent = _parent

        self.objectTypes = {"background": self.setupBackground,
            "door": self.setupDoor,
            "wall": self.setupWalls,
            "counter": self.setupSensor,
            "spawn": self.setupSpawnPoints,
            "collector": self.setupCollector,}

        self.hingeLeft = None
        self.hingeRight = None
        self.isHingeLeftSet = False
        self.isHingeRightSet = False

        self.spawnPoints = []

        self.rootNode = render.attachNewNode("builder_root")

    def cleanup(self):
        self.rootNode.removeNode()

    def parseEggFile(self, _filename):

        eggFile = loader.loadModel(_filename)

        # Get the contained objects
        objects = eggFile.findAllMatches('**')
        self.hingeLeft = eggFile.find("**/hinge_left")
        self.hingeRight = eggFile.find("**/hinge_right")

        for obj in objects:
            for types in self.objectTypes:
                if obj.hasTag(types):
                    self.objectTypes[types](obj, eggFile)


    def setupBackground(self, _obj, _eggFile):
        _obj.reparentTo(self.rootNode)
        _obj.setPos(0, 0, 0)

    def setupWalls(self, _obj, _eggFile):
        tmpMesh = BulletTriangleMesh()
        node = _obj.node()

        if node.isGeomNode():
            tmpMesh.addGeom(node.getGeom(0))
        else:
            return

        body = BulletRigidBodyNode("wall")
        body.addShape(BulletTriangleMeshShape(tmpMesh, dynamic=False))
        body.setMass(0)

        np = self.rootNode.attachNewNode(body)
        np.setCollideMask(BitMask32.bit(1))

        self.parent.physics_world.attachRigidBody(body)

    def setupDoor(self, _obj, _eggFile):
        shape = BulletBoxShape(Vec3(1.7/2, 0.6/2, 0.2/2))
        node = BulletRigidBodyNode(_obj.getTag("door"))
        node.addShape(shape)
        node.setMass(1)
        node.setDeactivationEnabled(False)

        np = self.rootNode.attachNewNode(node)
        np.setCollideMask(BitMask32.bit(2))
        np.setPos(_obj.getPos())
        np.setHpr(_obj.getHpr())

        self.parent.physics_world.attachRigidBody(node)

        _obj.reparentTo(np)
        _obj.setPos(np.getPos() - _obj.getPos())

        # Setup hinge
        if _obj.getTag("door") == "left" and self.isHingeLeftSet != True:
            pos = Point3(-2.0, 0, 0)#hingeLeft.getPos()
            axisA = Vec3(0, 1, 0)
            hinge = BulletHingeConstraint(node, pos, axisA, True)
            hinge.setDebugDrawSize(0.3)
            hinge.setLimit(-10, 58, softness=0.9, bias=0.3, relaxation=1.0)
            self.parent.physics_world.attachConstraint(hinge)
            self.isHingeLeftSet = True

            self.parent.game_doors["left"] = np
            self.parent.game_doors["left_hinge"] = hinge

        if _obj.getTag("door") == "right" and self.isHingeRightSet != True:
            pos = Point3(2.0, 0, 0)#hingeLeft.getPos()
            axisA = Vec3(0, -1, 0)
            hinge = BulletHingeConstraint(node, pos, axisA, True)
            hinge.setDebugDrawSize(0.3)
            hinge.setLimit(-10, 58, softness=0.9, bias=0.3, relaxation=1.0)
            self.parent.physics_world.attachConstraint(hinge)
            self.isHingeRightSet = True

            self.parent.game_doors["right"] = np
            self.parent.game_doors["right_hinge"] = hinge

    def setupSensor(self, _obj, _eggFile):
        shape = BulletBoxShape(Vec3(_obj.getScale()))

        ghost = BulletGhostNode("Counter_Ghost_Node")
        ghost.addShape(shape)

        np = self.rootNode.attachNewNode(ghost)
        np.setPos(_obj.getPos())
        np.setCollideMask(BitMask32(0x0f))

        self.parent.physics_world.attachGhost(ghost)

        self.parent.game_counter_node = np

    def setupCollector(self, _obj, _eggFile):
        tb = _obj.getTightBounds()
        boxSize = VBase3(tb[1] - tb[0])
        # TODO: istn't there a better way to multiply those two vectors?
        s = _obj.getTransform().getScale()
        boxSize[0] *=  s[0]
        boxSize[1] *=  s[1]
        boxSize[2] *=  s[2]
        shape = BulletBoxShape(boxSize*0.5)

        ghost = BulletGhostNode("Collector_Ghost_Node")
        ghost.addShape(shape)

        np = self.rootNode.attachNewNode(ghost)
        np.setPos(_obj.getPos())
        np.setHpr(_obj.getHpr())
        np.setCollideMask(BitMask32(0x0f))

        self.parent.physics_world.attachGhost(ghost)

        self.parent.game_collector_nodes.append(np)

    def setupSpawnPoints(self, _obj, _eggFile):
        point = (_obj.getPos())
        self.spawnPoints.append(point)
