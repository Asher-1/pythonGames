from OpenGL.GL import *
from OpenGL.GLU import *
from glstate import GLState
from light import Light

from constants import *

class Camera(object):
    def __init__(self, center = (0, 0), distance=10):
        self.center = center
        self.distance = distance
        self.mindistance = ZOOM_MIN_DISTANCE
        self.maxdistance = ZOOM_MAX_DISTANCE
        self.bottomleft = (-1,-1)
        self.topright = (10,10)
    def setPosition(self, center):
        self.center = center
        self.setCurrent()

    def setZoom(self, zoom):
        self.distance = zoom
        self.setCurrent()

    def move(self, offset):
        c0, c1 = self.center
        if (self.center[0] + offset[0] - self.distance * .5 >= self.bottomleft[0] or offset[0] >= 0) and \
           (self.center[0] + offset[0] + self.distance * .5 <= self.topright[0] or offset[0] <= 0):
            c0 += offset[0]
        if (self.center[1] + offset[1] - self.distance * .5 >= self.bottomleft[1] or offset[1] >= 0) and \
           (self.center[1] + offset[1] + self.distance * .5 <= self.topright[1] or offset[1] <= 0):
            c1 += offset[1]
        self.center = (c0, c1)
        self.setCurrent()

    def zoom(self, offset):
        if self.distance + offset >= self.mindistance and self.distance + offset <= self.maxdistance:
            self.distance += offset
        self.setCurrent()

    def setCurrent(self):
        glLoadIdentity()
        gluLookAt(self.center[0], self.center[1], self.distance, 
                  self.center[0], self.center[1], 0, 
                  0, 1, 0)
        GLState.camera = self
        Light.updateLights()
        
    def getPos(self, screenPos):
        sx, sy = screenPos
        vx = (sx - .5 * GLState.width) / GLState.height
        vy = (.5 * GLState.height - sy) / GLState.height
        cx = self.center[0] + (1 + self.distance) * vx
        cy = self.center[1] + (1 + self.distance) * vy
        return (cx, cy)

    def getIntPos(self, screenPos):
        cx, cy = self.getPos(screenPos)
        return (int(cx + .5), int(cy + .5))
