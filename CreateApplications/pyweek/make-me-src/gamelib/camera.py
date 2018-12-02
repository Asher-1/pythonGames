#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import pyglet
from pyglet.gl import *

import collide
import globals

_debug_maps = False

def sign(v):
    return v > 0 and 1 or -1

class Camera(object):
    SPRING_K = 10.
    SPRING_MASS = 1.
    SPRING_DAMP = 4.
    MAX_DX = 1000
    MAX_DY = 1000

    follow = True
    locked = False

    def __init__(self):
        self.x = None
        self.y = None
        self.dx = 0
        self.dy = 0
        
    def apply(self):
        glLoadIdentity()
        glTranslatef(-int(self.x), -int(self.y), 0)

    def window_to_world(self, x, y):
        return x + int(self.x), y + int(self.y)

    def update(self, dt):
        if self.locked:
            return

        if dt > 1/20.:
            dt = 1/20.

        player = globals.game.player
        window = globals.window
        if self.follow:
            self.goal_x = player.x
            self.goal_y = player.y - window.height // 3
            if player.facing == 'right':
                self.goal_x -= window.width // 4
            else:
                self.goal_x -= 3 * window.width // 4

        if self.x is None:
            self.x = self.goal_x
            self.y = self.goal_y
            self.dx = 0
            self.dy = 0
            return

        fx = (self.goal_x - self.x) * self.SPRING_K - self.dx * self.SPRING_DAMP
        fy = (self.goal_y - self.y) * self.SPRING_K - self.dy * self.SPRING_DAMP
        ax = fx * self.SPRING_MASS
        ay = fy * self.SPRING_MASS
        self.dx += ax * dt
        self.dy += ay * dt

        self.dx = min(self.MAX_DX, max(-self.MAX_DX, self.dx))
        self.dy = min(self.MAX_DY, max(-self.MAX_DY, self.dy))

        self.x += self.dx * dt
        self.y += self.dy * dt

    def update_visibility(self, dt=None):
        if self.x is None:
            return

        ww = globals.window.width
        wh = globals.window.height
        border = 100
        test_bbox = collide.BBox(self.x - border, 
                                 self.y - border,
                                 self.x + ww + border * 2, 
                                 self.y + wh + border * 2)

        for layer in globals.game.layers:
            layer.update_visibility_bbox(test_bbox)

        if not self.follow:
            # In editor, don't do progressive
            globals.game.wait_for_tasks()

