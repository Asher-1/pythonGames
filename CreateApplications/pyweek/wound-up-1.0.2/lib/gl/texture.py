from OpenGL.GL import *
import pygame, data

class Texture(object):
    _texids = dict()
    def __init__(self, filename):
        if filename in self._texids:
            self.id = self._texids[filename]
            return
        surf = pygame.image.load(data.filepath(filename))
        image = pygame.image.tostring(surf, 'RGBA', 1)
        x, y = surf.get_rect().size
        if x != y:
            raise NonSquareTextureException
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, x, y, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

    def enable(self):
        glColor3f(1,1,1)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.id)

    def disable(self):
        glDisable(GL_TEXTURE_2D)
class NonSquareTextureException(Exception):
    pass
