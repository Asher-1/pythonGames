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

color = [0.0,0.5,0.0,1.0]

class Axis (object):

    def __init__(self, pos=Vector3(0,0,0), size=2.0):
        self.pos = pos
        self.size = size
        vcpgdict = VCPGDict(
            vertices=[self.get_vertices()],
            colors=[self.get_colors()],
            prim_types=[self.get_prim_type()],
            drawgroups=[self.get_drawgroup()],
            parents=[self],
        )
        batch.add(vcpgdict)
        
    def get_vertices(self):
        vertices_format = 'v3f'
        length = self.size
        vertices = [0.0, 0.0, 0.0, 
                    0.0, 0.0, length, 
                    0.0, 0.0, 0.0, 
                    0.0, length, 0.0, 
                    0.0, 0.0, 0.0, 
                    length, 0.0, 0.0]
        return (vertices_format,vertices)
        
    def get_colors(self):
        colors = [0.0, 0.3, 1.0,0.0,  0.0, 0.3, 1.0,0.0,
                  1.0, 0.0, 0.0,0.0,   1.0, 0.0, 0.0,0.0,
                  0.0, 1.0, 0.0,0.0,  0.0, 1.0, 0.0,0.0]
        colors = ('c4f', color*6)
        return colors
        
    def get_prim_type(self):
        return GL_LINE
        
    def get_drawgroup(self):
        return GRP_BLEND_ONE
        
    def get_parent(self):
        return self
        

if __name__ == '__main__':
    v = VectorChar()
    print v.vertices
