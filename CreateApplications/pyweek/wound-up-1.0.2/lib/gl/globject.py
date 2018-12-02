from OpenGL.GL import *
from OpenGL.GLUT import *
import objloader
from glstate import GLState


class Object(object):
    '''Base class for a displayable GL object'''

    def __init__(self):
        self.viewdirty = True
        self.modeldirty = True
        self.angle = 0
        self.position = (0, 0, 0)
        self.axis = (0, 0, 1)
        self.viewdisplist = glGenLists(1)
        self.modeldisplist = glGenLists(1)

    def __del__(self):
        glDeleteLists(self.viewdisplist, 1)
        glDeleteLists(self.modeldisplist, 1)


    def render(self):
        self.prerender()
        glCallList(self.viewdisplist)
    def prerender(self):
        if self.modeldirty:
            self.updateModelDisplayList()
        if self.viewdirty:
            self.updateViewDisplayList()

    def rotate(self, angle):
        self.angle += angle
        self.viewdirty = True

    def setAngle(self, angle):
        self.angle = angle
        self.viewdirty = True

    def move(self, offset):
        self.position = tuple([sum(x) for x in zip(self.position, offset)])
        self.viewdirty = True

    def setPosition(self, position):
        if len(position) == 2:
            self.position = tuple(position) + (self.position[2],)
        else:
            self.position = tuple(position)
        self.viewdirty = True

    def updateViewDisplayList(self):
        glNewList(self.viewdisplist, GL_COMPILE)
        glPushMatrix()
        self.setupView()
        glCallList(self.modeldisplist)
        glPopMatrix()
        glEndList()
        self.viewdirty = False
 
    def setupView(self):
        glTranslated(*self.position)
        glRotated(self.angle, *self.axis)
       
    def updateModelDisplayList(self):
        self.modeldirty = False
        glNewList(self.modeldisplist, GL_COMPILE)
        self.draw()
        glEndList()
    
    def numPolys(self):
        if hasattr(self, "n_polys"): return self.n_polys
        return 0

    def draw(self):
        glColor3f(1, .3, .5)
        glutWireIcosahedron()
    def __del__(self):
        glDeleteLists(self.modeldisplist, 1)
        glDeleteLists(self.viewdisplist, 1)

class ModelObject(Object):
    _OBJs = dict()
    def __init__(self, objfile):
        Object.__init__(self)
        glDeleteLists(self.modeldisplist, 1)
        if objfile not in self._OBJs:
            self._OBJs[objfile] = objloader.OBJ(objfile)
        self.OBJ = self._OBJs[objfile]
    
    def __del__(self):
        glDeleteLists(self.viewdisplist, 1)

    def updateModelDisplayList(self):
        self.modeldisplist = self.OBJ.gl_list
        self.modeldirty = False

    def numPolys(self):
        return len(self.OBJ.faces)
    
    def __del__(self):
        glDeleteLists(self.viewdisplist, 1)
