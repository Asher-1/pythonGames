import pyglet
from pyglet.window import key
from pyglet.gl import *

from gamelib import app
from gamelib.constants import *


class Scene(object):

    def __init__(self):
        self.x = app.window.width / 2
        self.y = app.window.height / 2

    def tick(self):
        if app.keys[key.LEFT]:
            self.x -= 2
        if app.keys[key.RIGHT]:
            self.x += 2
        if app.keys[key.DOWN]:
            self.y -= 2
        if app.keys[key.UP]:
            self.y += 2

    def on_draw(self):
        app.window.clear()
        glBegin(GL_QUADS)
        glColor3f(1, 1, 0)
        glVertex2f(self.x - 5, self.y - 5)
        glVertex2f(self.x + 5, self.y - 5)
        glVertex2f(self.x + 5, self.y + 5)
        glVertex2f(self.x - 5, self.y + 5)
        glEnd()
