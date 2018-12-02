from pyglet.gl import *

def draw_bounding_box(target):
        glColor4f(0, 0, 1, 1) 
        glBegin(GL_LINE_STRIP)
        glVertex2f(target.x,target.y)
        glVertex2f(target.x+target.width,target.y)
        glVertex2f(target.x+target.width,target.y+target.height)
        glVertex2f(target.x, target.y+target.height)
        glVertex2f(target.x,target.y)
        glEnd()
        glColor4f(1, 1, 1, 1) 

