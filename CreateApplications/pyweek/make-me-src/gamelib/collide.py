#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import sys

from pyglet.gl import *

class BBox(object):
    # Validity of edges
    left = True
    top = True
    right = True
    bottom = True

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __repr__(self):
        def t(v):
            if v:
                return 'T'
            return 'F'

        return 'BBox(%d, %d, %d, %d [%s%s%s%s])' % (
            self.x1, self.y1, self.x2, self.y2,
            t(self.left), t(self.top), t(self.right), t(self.bottom))

    def draw(self):
        glPushAttrib(GL_CURRENT_BIT | GL_POLYGON_BIT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(0, 0, 1)
        glRectf(self.x1, self.y1, self.x2, self.y2)
        glPopAttrib()

    @classmethod
    def for_sprite(cls, sprite):
        return cls(sprite.x, sprite.y, 
                   sprite.x + sprite.width, sprite.y + sprite.height)

    def resolve_edges(self, other):
        '''Return dx, dy to move self so that it doesn't intersect other.'''
        # See http://www.ziggyware.com/readarticle.php?article_id=134
        dx = 0
        dy = 0

        axis = 'none'
        min_dist = sys.maxint

        # left
        diff = self.x2 - other.x1
        if diff < 0:
            return 0, 0

        min_dist = diff
        axis = 'x'
        side = -1

        # right
        diff = other.x2 - self.x1
        if diff < 0:
            return 0, 0

        if diff < min_dist and other.right:
            min_dist = diff
            axis = 'x'
            side = 1

        # down
        diff = other.y2 - self.y1
        if diff < 0:
            return 0, 0

        if diff < min_dist and other.top:
            min_dist = diff
            axis = 'y'
            side = 1

        # up
        diff = self.y2 - other.y1
        if diff < 0:
            return 0, 0

        if diff < min_dist and other.bottom:
            min_dist = diff
            axis = 'y'
            side = -1

        if axis == 'x':
            return side * min_dist, 0
        elif axis == 'y':
            return 0, side * min_dist
        else:
            return 0, 0

    def intersects(self, other):
        return (self.x2 > other.x1 and other.x2 > self.x1 and
                self.y2 > other.y1 and other.y2 > self.y1)

    def has_point(self, x, y):
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def normalize(self):
        x1, y1, x2, y2 = self.x1, self.y1, self.x2, self.y2
        self.x1 = min(x1, x2)
        self.x2 = max(x1, x2)
        self.y1 = min(y1, y2)
        self.y2 = max(y1, y2)

    def get_translated(self, x, y):
        return BBox(self.x1 + x, self.y1 + y, self.x2 + x, self.y2 + y)

    def get_ground_check(self):
        return BBox(self.x1 + 5, self.y1 - 5, self.x2 - 5, self.y1 + 20)

    def get_flipped(self):
        return BBox(-self.x2, self.y1, -self.x1, self.y2)
