'''globjects.py - GL state for the model'''

import random
import math

from OpenGL.GL import *
from OpenGL.GLUT import *

import gl
import model

class Firework(gl.Particle):
    def __init__(self, position, colour = (1,1,0)):
        gl.Particle.__init__(self, position)
        self.colour = colour
        self.velocity = (0, .15+ random.gauss(0,.05), random.gauss(0, .05))
    def draw(self):
        glDisable(GL_LIGHTING)
        glColor3f(*self.colour)
        glBegin(GL_POINTS)
        glVertex3f(0,0,0)
        glEnd()
        glEnable(GL_LIGHTING)
    def tick(self):
        self.move(self.velocity)
        self.velocity = (self.velocity[0], self.velocity[1] - .005, self.velocity[2])
        return random.random() < 0.97
class SnappedBelt(gl.ParticleSystem):
    def __init__(self, end1, end2, nparts = 100):
        gl.ParticleSystem.__init__(self, (0,0,0), nparts=0)
        if not gl.GLState.particles:
            return
        for x in range(nparts):
            alpha = (x + .5) / nparts
            self.particles.append(BeltPiece(([x[0] * alpha + x[1] * (1 - alpha) for x in zip(end1, end2)])))


class BeltPiece(gl.Particle):
    def draw(self):
        glDisable(GL_LIGHTING)
        glColor3f(.45, .25, .1)
        glBegin(GL_POINTS)
        glVertex3f(0,0,0)
        glEnd()
        glEnable(GL_LIGHTING)
    def tick(self):
        self.move((0, -random.random() * .02, 0))
        return random.random() < .95


class SmokePuff(gl.Particle):
    n_polys = 1
    teximages = ["smoke_puff.tga", "smoke_puff2.tga"]
    texs = []    
    def __init__(self, position):
        if not self.texs:
            for img in self.teximages:
                self.texs.append(gl.Texture(img))
        self.tex = random.choice(self.texs)
        gl.Particle.__init__(self, position)
        self.velocity = (0,0,0)
        self.setAngle(random.random() * 360)
        self.size = random.random() * .3 + .3
    def draw(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.tex.enable()
        glNormal3f(0, 0, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0,0)
        glVertex3f(-self.size, -self.size, 0)
        glTexCoord2f(0,1)
        glVertex3f(-self.size, self.size, 0)
        glTexCoord2f(1,1)
        glVertex3f(self.size, self.size, 0)
        glTexCoord2f(1,0)
        glVertex3f(self.size, -self.size, 0)
        glEnd()
        self.tex.disable()
        glDisable(GL_BLEND)

    def tick(self):
        self.velocity = (self.velocity[0] + random.gauss(0, .005), self.velocity[1] + random.gauss(0, .005), 0)
        self.move(self.velocity)
        return random.random() < 0.95


class Belt(gl.Object):
    n_polys = 4
    
    def __init__(self, belt, bag):
        gl.Object.__init__(self)
        self.end1 = belt.part1.pos
        self.end2 = belt.part2.pos
        b_angle = math.atan2(self.end1[1] - self.end2[1], self.end1[0] - self.end2[0])
        self.offset = (.2 * -math.sin(b_angle), .2 * math.cos(b_angle))
        self.normal = (math.cos(b_angle), math.sin(b_angle), 0)
        
    def draw(self):
        glColor(.45,.25,.1)
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)

        glVertex3f(self.end1[0] + self.offset[0], self.end1[1] + self.offset[1], 0)
        glVertex3f(self.end2[0] + self.offset[0], self.end2[1] + self.offset[1], 0)
        glVertex3f(self.end2[0] + self.offset[0], self.end2[1] + self.offset[1], -.1)
        glVertex3f(self.end1[0] + self.offset[0], self.end1[1] + self.offset[1], -.1)

        glVertex3f(self.end1[0] + self.offset[0] * .9, self.end1[1] + self.offset[1] * .9, 0)
        glVertex3f(self.end1[0] + self.offset[0] * 1.1, self.end1[1] + self.offset[1] * 1.1, 0)
        glVertex3f(self.end2[0] + self.offset[0] * 1.1, self.end2[1] + self.offset[1] * 1.1, 0)
        glVertex3f(self.end2[0] + self.offset[0] * .9, self.end2[1] + self.offset[1] * .9, 0)

        glVertex3f(self.end1[0] - self.offset[0], self.end1[1] - self.offset[1], 0)
        glVertex3f(self.end2[0] - self.offset[0], self.end2[1] - self.offset[1], 0)
        glVertex3f(self.end2[0] - self.offset[0], self.end2[1] - self.offset[1], -.1)
        glVertex3f(self.end1[0] - self.offset[0], self.end1[1] - self.offset[1], -.1)

        glVertex3f(self.end1[0] - self.offset[0] * .9, self.end1[1] - self.offset[1] * .9, 0)
        glVertex3f(self.end1[0] - self.offset[0] * 1.1, self.end1[1] - self.offset[1] * 1.1, 0)
        glVertex3f(self.end2[0] - self.offset[0] * 1.1, self.end2[1] - self.offset[1] * 1.1, 0)
        glVertex3f(self.end2[0] - self.offset[0] * .9, self.end2[1] - self.offset[1] * .9, 0)
        
        glEnd()


class Boundary(gl.Object):
    n_polys = 8
    
    def __init__(self, width, height):
        gl.Object.__init__(self)
        self.groundtex = gl.Texture("boiler_plate.jpg")
        self.boundtex = gl.Texture("ground.jpg")   
        self.walltex = gl.Texture("iron_wrought.jpg")
        self.width = width
        self.height = height
    
    def setSize(self, size):
        self.width, self.height = size
        self.modeldirty = True
 
    def draw(self):
        glPushMatrix()
        glTranslated(-.5, -.5, 0)
        self.boundtex.enable()
        
        glBegin(GL_QUAD_STRIP)
        glNormal3f(1, 0, 0)
        glTexCoord2f(0, 0)
        glVertex3f(0, 0, 0)
        glTexCoord2f(.5, 0)
        glVertex3f(0, 0, 2)
        glTexCoord2f(0, .25 * self.height)
        glVertex3f(0, self.height, 0)
        glTexCoord2f(.5, .25 * self.height)
        glVertex3f(0, self.height, 2)
        glTexCoord2f(0, .25 * (self.height + self.width))
        glNormal3f(-1, 0, 0)
        glVertex3f(self.width, self.height, 0)
        glTexCoord2f(.5, .25 * (self.height + self.width))
        glVertex3f(self.width, self.height, 2)
        glTexCoord2f(0, self.height * .5 + .25 * self.width)
        glVertex3f(self.width, 0, 0)
        glTexCoord2f(.5, self.height * .5 + .25 * self.width)
        glVertex3f(self.width, 0, 2)
        glEnd()
        
        glNormal3f(0,0,1)
        glBegin(GL_QUAD_STRIP)
        glTexCoord2f(0,0)
        glVertex3f(0,0,2)
        glTexCoord2f(-2.5, -2.5)
        glVertex3f(-10,-10,2)
        glTexCoord2f(0, self.height * .25)
        glVertex3f(0, self.height, 2)
        glTexCoord2f(-2.5, self.height * .25 + 2.5)
        glVertex3f(-10, self.height + 10, 2)
        glTexCoord2f(self.width * .25, self.height * .25)
        glVertex3f(self.width, self.height, 2)
        glTexCoord2f(self.width * .25 + 2.5, self.height * .25 + 2.5)
        glVertex3f(self.width + 10, self.height + 10, 2)
        glTexCoord2f(self.width * .25, 0)
        glVertex3f(self.width, 0, 2)
        glTexCoord2f(self.width * .25 + 2.5, -2.5)
        glVertex3f(self.width + 10, -10, 2)
        glTexCoord2f(0,0)
        glVertex3f(0,0,2)
        glTexCoord2f(-2.5, -2.5)
        glVertex3f(-10,-10,2)
        glEnd() 
        self.boundtex.disable()
        self.walltex.enable()
        glBegin(GL_QUADS)
        for u in range(-8, self.width + 8, 8):
            for v in range(-8, self.height + 8, 8):
                glTexCoord2f(0,0)   
                glVertex3f(u, v, -2.5)
                glTexCoord2f(0,1)   
                glVertex3f(u, v + 8, -2.5)
                glTexCoord2f(1,1)   
                glVertex3f(u+8, v+8, -2.5)
                glTexCoord2f(1,0)   
                glVertex3f(u+8, v, -2.5)
        glEnd()
        self.walltex.disable()
        self.groundtex.enable()
        glBegin(GL_QUAD_STRIP)
        glNormal3f(0, 1, 0)
        glTexCoord2f(.5 * self.width , 0)
        glVertex3f(self.width, 0, -0)
        glTexCoord2f(.5 * self.width, 1)
        glVertex3f(self.width, 0, 2)
        glTexCoord2f(0, 0)
        glVertex3f(0, 0, -0)
        glTexCoord2f(0, 1)
        glVertex3f(0, 0, 2)
        glEnd()
        self.groundtex.disable()
        glPopMatrix()


class Cog(gl.ModelObject):
    _cogModels = dict({1: ["simple-1.obj", "scuzzy-1.obj", "round-1.obj"], 
                       3: ["simple-3.obj", "cycle-3.obj"], 
                       5: ["simple-5.obj", "hypno-5.obj"], 
                       7: ["scuzzy-7.obj"],
                      25: ["mighty-25.obj"]
                      })
    _defaultModel = "plane.obj"

    def __init__(self, cog, bag):
        if cog.diam in self._cogModels:
            model = random.choice(self._cogModels[cog.diam])
        else:
            model = _defaultModel
        gl.ModelObject.__init__(self, model)
        self.setPosition(cog.pos + (0,))


class Elf(gl.ModelObject):

    def __init__(self, elf, bag):
        gl.ModelObject.__init__(self, ["elf.obj", "girlelf.obj"][elf.female])
        self.axis = (0,1,0)
        self.setPosition(elf.path[0] + (.5,))


class Ladder(gl.ModelObject):
    
    def __init__(self, position, bag):
        gl.ModelObject.__init__(self, "ladder.obj")
        self.setPosition(position + (0,))


class Plat(gl.ModelObject):
    _platObjs = {1: "plat.obj", 3: "plat3.obj", 5: "plat5.obj"}
    _defaultObj = "bucket.obj"

    def __init__(self, plat, bag):
        position, size = plat
        gl.ModelObject.__init__(self, self._platObjs.get(size, self._defaultObj))
        self.setPosition(position + (0,))

class Wheel(gl.ModelObject):
    
    def __init__(self, parent):
        gl.ModelObject.__init__(self, "wheel.obj")
        self.setPosition(parent.pos + (0,))
        self.parent = parent

class Device(gl.ModelObject):
    deviceModel = "bucket.obj"
    
    def __init__(self, device, bag):
        gl.ModelObject.__init__(self, self.deviceModel)
        self.wheelObj = Wheel(device)
        self.setPosition(device.pos + (0,))
    
    def setAngle(self, angle):
        self.wheelObj.setAngle(angle)

    def prerender(self):
        gl.ModelObject.prerender(self)
        self.wheelObj.prerender()

    def render(self):
        gl.ModelObject.render(self)
        self.wheelObj.render()
    def numPolys(self):
        return gl.ModelObject.numPolys(self) + self.wheelObj.numPolys()


class Spring(Device):
    deviceModel = "spring.obj"

    def __init__(self, spring, bag):
        Device.__init__(self, spring, bag)
        self.light = gl.Light((spring.pos[0], spring.pos[1] + 3, 5))


class GumballMachine(Device):
    deviceModel = "gumball-machine.obj"


class MetalFactory(Device):
    deviceModel = "metal-factory.obj"

class HeavyMetalFactory(Device):
    deviceModel = "heavy-metal.obj"

class RubberFactory(Device):
    deviceModel = "rubber-factory.obj"

class HeavyRubberFactory(Device):
    deviceModel = "heavy-rubber.obj"

class DeviceFactory(object):
    glClasses = {
        model.part.Spring: Spring, 
        model.device.GumballMachine: GumballMachine,
        model.device.MetalFactory: MetalFactory,
        model.device.HeavyMetalFactory: HeavyMetalFactory,
        model.device.RubberFactory: RubberFactory,
        model.device.HeavyRubberFactory: HeavyRubberFactory
    }
    defaultClass = Device
    
    def __new__(cls, device, bag):
        self = cls.glClasses.get(type(device), cls.defaultClass)(device, bag)
        return self


class InvisibleTask(gl.Object):
    
    def __init__(self, task, bag):
        gl.Object.__init__(self)
    
    def render(self):
        pass 
    
    def update(self):
        pass


class CogTask(gl.Object):
    
    def __init__(self, task, bag):
        gl.Object.__init__(self)
        self.setPosition(task.pos + (-.2,))
        self.diam = task.diam

    def draw(self):
        glDisable(GL_LIGHTING)
        glColor3f(.5,.5,.5)
        glutWireTorus(.1, self.diam * .5, 6, 12)
        glEnable(GL_LIGHTING)

    def update(self):
        pass

class RemoveCogTask(gl.Object):
    def __init__(self, task, bag):
        gl.Object.__init__(self)
        self.setPosition(task.cog.pos + (-.1,))
        self.diam = task.cog.diam

    def draw(self):
        glDisable(GL_LIGHTING)
        glColor3f(1,0,0)
        glPushMatrix()
        glRotated(45, 0, 0, 1)
        glPushMatrix()
        glScaled(self.diam, .5, .1)
        glutWireCube(1)
        glPopMatrix()
        glRotated(90, 0, 0, 1)
        glScaled(self.diam, .5, .1)
        glutWireCube(1)
        glPopMatrix()
        glEnable(GL_LIGHTING)
    def update(self):
        pass

class DisconnectTask(gl.Object):
    def __init__(self, task, bag):
        gl.Object.__init__(self)
        self.belt = task.belt
        self.position = (0,0,0)

    def draw(self):
        glDisable(GL_LIGHTING)
        glColor3f(1,0,0)
        glPushMatrix()
        glTranslated(*([.5 * sum(x) for x in zip(self.belt.part1.pos, self.belt.part2.pos)] + [0]))
        glRotated(45, 0, 0, 1)
        glPushMatrix()
        glScaled(.7, .2, .1)
        glutWireCube(1)
        glPopMatrix()
        glRotated(90, 0, 0, 1)
        glScaled(.7, .2, .1)
        glutWireCube(1)
        glPopMatrix() 
        glEnable(GL_LIGHTING)

    def update(self):
        pass
class ConnectTask(gl.Object):
    
    def __init__(self, task, bag):
        gl.Object.__init__(self)
        self.elfbag = bag.elfbag
        self.task = task

    def update(self):
        if self.task.phase == 2:
            self.modeldirty = True

    def draw(self):
        glDisable(GL_LIGHTING)
        glColor3f(.5,.5,.5)
        glBegin(GL_LINES)
        glVertex3fv(self.task.part1.pos + (0,))
        glVertex3fv(self.task.part2.pos + (0,))
        glEnd()
        glEnable(GL_LIGHTING)
        if self.task.phase == 2:
            glColor3f(.45,.25,.1)
            glBegin(GL_LINES)
            glVertex3fv(self.elfbag.objs[self.task.elf1].position)
            glVertex3fv(self.elfbag.objs[self.task.elf2].position)
            glEnd()


class PlatformTask(gl.Object):
    
    def __init__(self, task, bag):
        gl.Object.__init__(self)
        self.setPosition((task.pos[0], task.pos[1] + .4, .5,))

    def draw(self):
        glDisable(GL_LIGHTING)
        glColor3f(.5,.5,.5)
        glPushMatrix()
        glScaled(1, .2, 1)
        glutWireCube(1)
        glPopMatrix()
        glEnable(GL_LIGHTING)
    
    def update(self):
        pass


class LadderTask(gl.Object):
    
    def __init__(self, task, bag):
        gl.Object.__init__(self)
        self.setPosition((task.pos[0], task.pos[1], 1.05))

    def draw(self):
        glDisable(GL_LIGHTING)
        glColor3f(.5,.5,.5)
        glPushMatrix()
        glScaled(.6, 1, .1)
        glutWireCube(1)
        glPopMatrix()
        glEnable(GL_LIGHTING)
    
    def update(self):
        pass


class TaskFactory(object):
    taskClasses = {
        model.task.CreateCogTask: CogTask,
        model.task.ConnectTask: ConnectTask,
        model.task.BuildPlatformTask: PlatformTask,
        model.task.BuildLadderTask: LadderTask,
        model.task.RemoveCogTask: RemoveCogTask,
        model.task.DisconnectTask: DisconnectTask
    }
    defaultClass = InvisibleTask
    
    def __new__(cls, task, bag):
        self = cls.taskClasses.get(type(task), cls.defaultClass)(task, bag)
        return self

class Cursor(gl.Object):
    dynamicmodes = ["platform task", "ladder task", "belt task"] 
    def __init__(self, state):
        gl.Object.__init__(self)
        self.light = gl.Light((0,0,3))
        self.mode = None 
        self.mode_param = None
        self.is_valid = True
        self.state = state
        self.setPosition((0,0,0))

    def setMode(self, mode, mode_param, is_valid):
        self.mode = mode
        self.mode_param = mode_param
        self.is_valid = is_valid
        self.modeldirty = True
        
    def setPosition(self, position):
        gl.Object.setPosition(self, position)
        self.light.position = (position[0], position[1], 5)
        if self.mode in self.dynamicmodes:
            self.modeldirty = True 
    def draw(self):
        glDisable(GL_LIGHTING)
        glColor3f(1,1,1)
        glPushMatrix()
        selected = self.state.mgrid[self.position[0], self.position[1]]
        if not self.is_valid:
            glColor3f(.5,0,0)
        if self.mode == "cog task":
            glTranslated(0,0,-.2)
            glutWireTorus(.1, self.mode_param * .5 - .1, 6, 12)
        elif self.mode == "platform task":
            if self.mode_param:
                y = self.mode_param[1]
                minx = min(self.position[0], self.mode_param[0])
                maxx = max(self.position[0], self.mode_param[0])
                for x in range(minx, maxx + 1):
                    if self.state.pgrid[x, y][0]:
                        glColor3f(.5, 0, 0)
                    else:
                        glColor3f(1, 1, 1)
                    glPushMatrix()
                    glTranslated(x - self.position[0], y - self.position[1] + .4, .5)
                    glScaled(1,.2,1)
                    glutWireCube(1)
                    glPopMatrix()
            else:
                glColor3f(1, 1, 1)
                glTranslated(0, .4, .5)
                glScaled(1,.2,1)
                glutWireCube(1)
        elif self.mode == "ladder task":
            if self.mode_param:
                x = self.mode_param[0]
                miny = min(self.position[1], self.mode_param[1])
                maxy = max(self.position[1], self.mode_param[1])
                for y in range(miny, maxy + 1):
                    if self.state.pgrid[x, y][1]:
                        glColor3f(.5, 0, 0)
                    else:
                        glColor3f(1, 1, 1)
                    glPushMatrix()
                    glTranslated(x - self.position[0], y - self.position[1], 1.05)
                    glScaled(.6,1,.1)
                    glutWireCube(1)
                    glPopMatrix()
            glColor3f(1, 1, 1)
            glTranslated(0, 0, 1.05)
            glScaled(.6,1,.1)
            glutWireCube(1)
            glColor3f(.3, .3, .3)
            glTranslated(0, 0, -5.5)
            glScaled(1,1,10)
            glutWireCube(1)
            
        elif self.mode == "belt task":
            if self.mode_param:
                if selected:
                    offset = (selected.pos[0] - self.position[0], selected.pos[1] - self.position[1], 0)
                else:
                    offset = (0,0,0)
                glBegin(GL_LINES)
                glVertex3f(*offset)
                glVertex3f(self.mode_param.pos[0] - self.position[0], self.mode_param.pos[1] - self.position[1], 0)
                glEnd()
        elif self.mode == "remove cog task":
            if selected and isinstance(selected, model.part.Cog):
                size = selected.diam
                offset = (selected.pos[0] - self.position[0], selected.pos[1] - self.position[1], 0)
            else:
                size = 1
                offset = (0,0,0)
            glTranslated(*offset)
            glRotated(45, 0, 0, 1)
            glPushMatrix()
            glScaled(size, .3, .1)
            glutWireCube(1)
            glPopMatrix()
            glRotated(90, 0, 0, 1)
            glScaled(size, .3, .1)
            glutWireCube(1)
        elif self.mode == "unhook task":
            belts = []
            if selected:
                offset = (selected.pos[0] - self.position[0], selected.pos[1] - self.position[1], 0)
                belts = self.state.connected_belts(selected)
                glTranslated(*[-x for x in self.position])
                for belt in belts:
                    glPushMatrix()
                    glTranslated(*([.5 * sum(x) for x in zip(belt.part1.pos, belt.part2.pos)] + [0]))
                    glRotated(45, 0, 0, 1)
                    glPushMatrix()
                    glScaled(.7, .2, .1)
                    glutWireCube(1)
                    glPopMatrix()
                    glRotated(90, 0, 0, 1)
                    glScaled(.7, .2, .1)
                    glutWireCube(1)
                    glPopMatrix() 
        glPopMatrix()
        glEnable(GL_LIGHTING)
