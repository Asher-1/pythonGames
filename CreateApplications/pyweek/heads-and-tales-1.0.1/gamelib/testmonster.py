import pyglet
from pyglet.gl import *

from vector import v, zero

from monsterparts import *

body = BearBody(None)
body.add_part(BearHead, 0)
seg2 = body.add_part(SnakeSegment, 1)
seg1 = body.add_part(SnakeSegment, 2)
ant = seg1.add_part(CrocodileAnterior, 1)
ant.add_part(CrocodileHead, 1)
seg3 = seg2.add_part(SnakeSegment, 1, root_idx=1)
seg3.add_part(CrocodileTail, 0)

class TestMonsterScene(object):

    def draw(self):

        for p in body.all_parts():
            p.sprite.draw()

        glPointSize(8)
        for p in body.all_parts():
            for a in p.anchors:
                glBegin(GL_LINES)
                glVertex2f(*(p.pos + a[0].rotated(p.rotation)))
                glVertex2f(*(p.pos + a[0].rotated(p.rotation) + v((10,0)).rotated(a[1] + p.rotation)))
                glEnd()
            
    def tick(self):
        pass
