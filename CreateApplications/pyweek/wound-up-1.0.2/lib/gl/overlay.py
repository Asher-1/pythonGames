from OpenGL.GL import *
from globject import *
from pygame.locals import *
import pygame
import data
from glstate import GLState

class Overlay(Object):
    n_polys = 1
    def __init__(self, texsize, position=(0,0), size = None):
        if not size:
            size = texsize
        Object.__init__(self)
        if texsize not in [4, 8, 16, 32, 64, 128, 256, 512]:
            raise NotAPowerOfTwoException
        self.texsize = texsize
        self.size = size 
        self.surf = pygame.Surface((texsize, texsize), SRCALPHA, 32)
        self.texid = glGenTextures(1)
        self.updateTexture()
        self.setPosition(position)
        

    def updateTexture(self):
        image = pygame.image.tostring(self.surf, 'RGBA', 1)
        glBindTexture(GL_TEXTURE_2D, self.texid)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.texsize, self.texsize, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

    def draw(self):
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, GLState.width, 0, GLState.height, -10, 10)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        self.setupView()
        glColor3f(1,1,1)
        glBindTexture(GL_TEXTURE_2D, self.texid)
        glNormal3f(0,0,-1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex3f(0, 0, 0)
        glTexCoord2f(0, 1)
        glVertex3f(0, self.size, 0)
        glTexCoord2f(1, 1)
        glVertex3f(self.size, self.size, 0)
        glTexCoord2f(1, 0)
        glVertex3f(self.size, 0, 0)
        glEnd()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
class NotAPowerOfTwoException(Exception):
    pass
