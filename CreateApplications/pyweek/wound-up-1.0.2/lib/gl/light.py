from OpenGL.GL import *
import globject
import gc
import weakref

class Light(object):
    _lights = range(GL_LIGHT0, GL_LIGHT0 + 3)
    _active = weakref.WeakValueDictionary()
    @classmethod
    def updateLights(cls):
        gc.disable()
        for l in cls._active.values():
            glLightfv(l.id, GL_POSITION, l.position)
        gc.enable()
    def __init__(self, position, point = True):
        try:
            self.id = self._lights.pop(0)
        except:
            raise RuntimeError('Too many lights')
        self._active[self.id] = self
        glEnable(self.id)
        self.position = position + ([(0,),(1,)][point])
        glLightfv(self.id, GL_POSITION, self.position)
        glLightfv(self.id, GL_AMBIENT, (0,0,0))
        self.setColour((1,1,1))
        glLightf(self.id, GL_QUADRATIC_ATTENUATION, 0.02)

    def setColour(self, colour):
        glLightfv(self.id, GL_DIFFUSE, colour)
        glLightfv(self.id, GL_SPECULAR, colour)
    
    def destroy(self):
        glDisable(self.id)
        self._lights.insert(0, self.id)

    def __del__(self):
        glDisable(self.id)
        self._lights.insert(0, self.id)
