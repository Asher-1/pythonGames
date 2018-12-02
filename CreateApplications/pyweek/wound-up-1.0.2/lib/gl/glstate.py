from OpenGL.GL import *

class GLState(object):
    lights = True
    camera = None
    inited = False
    @classmethod
    def setParticles(self, flag):
        self.particles = flag
    @classmethod
    def setResolution(cls, width, height):
        cls.width = width
        cls.height = height

    @classmethod
    def toggleLighting(cls):
        if cls.lights:
            glDisable(GL_LIGHTING)
        else:
            glEnable(GL_LIGHTING)
        cls.lights = not cls.lights

    @classmethod
    def currentCamera(cls):
        return cls.camera
