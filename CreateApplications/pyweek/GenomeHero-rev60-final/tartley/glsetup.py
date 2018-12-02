
import pyglet
from pyglet.gl import *

###############################################################################
################################################################# gl_init #####
###############################################################################

def gl_init(width, height):
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40.0, float(width)/float(height), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


###############################################################################
################################################################ init #########
###############################################################################

def init(w, h, vsync):
    window = pyglet.window.Window(width=w, height=h, vsync=False)
    gl_init(w,h)
    return window


###############################################################################
################################################################ set2D ######## 
###############################################################################

def set2D(window):
    glDisable(GL_DEPTH_TEST) 
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, window.width, 0, window.height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


###############################################################################
################################################################ set3D ######## 
###############################################################################

def set3D(window):
    glEnable(GL_DEPTH_TEST) 
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40.0, float(window.width)/float(window.height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()



