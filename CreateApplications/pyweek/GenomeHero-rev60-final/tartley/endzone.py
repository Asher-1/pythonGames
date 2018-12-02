import collections
from batchmanager import batch
from pyglet.gl import *
import pyglet
from util import *
from euclid import *
from drawgroups import *

VCPGDict = collections.namedtuple(
    'vcpgdict',
    ['vertices', 'colors', 'prim_types', 'drawgroups', 'parents']
)
import sys
if sys.platform == "darwin":
    color = [0.0,0.5,0.0,0.5]
else:
    color = [0.0,0.5,0.0,0.2]
color2 = [1.0,0.6,0.0,0.4]

class EndZone (object):

    def __init__(self, pos, w, h, size=0.1):
        self.pos = Vector3(pos[0],pos[1],pos[2])
        self.size = size
        self.w = w
        self.h = h
        vcpgdict = VCPGDict(
            vertices=self.get_vertices(),
            colors=self.get_colors(),
            prim_types=self.get_prim_type(),
            drawgroups=self.get_drawgroup(),
            parents=[self, self],
        )
        batch.add(vcpgdict)
        
    def get_vertices(self):
        vertices_format = 'v3f'
        x, y, z = self.pos[:]
        w, h = self.w, self.h
        vertices = [x,0,z,  x,0,z+h,  x+w,0,z+h,  x+w,0,z]
        self.vertices = vertices

        return [(vertices_format,vertices), (vertices_format,vertices)]
        
    def get_colors(self):
        colors = color * 4
        colors2 = color2 * 4
        colors = [('c4f', colors), ('c4f', colors2)]
        return colors
        
    def get_prim_type(self):
        return [GL_QUADS, GL_LINE_LOOP]
        
    def get_drawgroup(self):
        return [GRP_LINE_POLY, GRP_LINE_POLY]
        
    def get_parent(self):
        return self

    def inc_height(self, height):
        self.h += height
        self.vertex_list.vertices = self.get_vertices()[1]
        

if __name__ == '__main__':
    v = VectorChar()
    print v.vertices
