#!/usr/bin/python

# Panda Engine imports
from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import Vec3, OrthographicLens
from direct.task.Task import Task
from direct.showbase.InputStateGlobal import inputState

# Game imports

#----------------------------------------------------------------------#

class GameBase():

    def __init__(self, _parent=None):
        self.parent = _parent

        # Physics
        self.gravity = Vec3(0, 0, -9)
        self.physics_world = None

        # Camera
        self.cam_position = Vec3(0, -47, 2.5)
        self.cam_rotation = (0.0, 0.0, 0.0)
        self.cam_filmSize = (40, 20)

    def start(self):
    	# Physics
    	self.setupPhysics(self.gravity)

    	# Camera
    	self.setupCamera(self.cam_position, self.cam_rotation, self.cam_filmSize)

    	# Input
    	self.setupInput()

    	# Start Tasks
    	taskMgr.add(self.updatePhysics, 'update-physics-task', 0)

    def stop(self):
    	# Stop Tasks
    	taskMgr.remove("update-physics-task")

    	# reset objects
    	self.physics_world = None

    ##### SETUPS #####
    def setupPhysics(self, _gravity):
    	self.physics_world = BulletWorld()
    	self.physics_world.setGravity(_gravity)


    def setupCamera(self, _pos, _rot, _filmsize):
    	# Setup lens, position and rotation
    	lens = OrthographicLens()
    	lens.setFilmSize(_filmsize[0], _filmsize[1])
    	#base.cam.node().setLens(lens)
    	base.cam.setPos(_pos)
    	base.cam.setHpr(_rot)

    def setupInput(self):
        # Disable the mouse
        #base.disableMouse()

        # Setup Keyboard Input
        inputState.watchWithModifiers('left', "arrow_left")
        inputState.watchWithModifiers('right', "arrow_right")
        inputState.watchWithModifiers('left', "z")
        inputState.watchWithModifiers('right', "/")
        inputState.watchWithModifiers('left', "lcontrol")
        inputState.watchWithModifiers('right', "rcontrol")
        inputState.watchWithModifiers('left', "lalt")
        inputState.watchWithModifiers('right', "ralt")
        inputState.watchWithModifiers('left', "lshift")
        inputState.watchWithModifiers('right', "rshift")

        # Ingame escape for menu
        #self.accept('escape', func)


    ##### UPDATES #####
    def updatePhysics(self, task):
        dt = globalClock.getDt()
        self.physics_world.doPhysics(dt, 5, 1.0/240.0)
        #print(camera.getPos())

        return task.cont

    ##### DEBUG #####
    def enablePhysicsDebug(self):
    	debugnode = BulletDebugNode('Physics-Debug')
    	debugnode.showWireframe(True)
    	debugnode.showConstraints(True)

    	debugNP = render.attachNewNode(debugnode)
    	if self.physics_world != None:
    		self.physics_world.setDebugNode(debugNP.node())
    		debugNP.show()

