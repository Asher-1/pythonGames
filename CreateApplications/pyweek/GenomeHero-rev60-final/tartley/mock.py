
import pyglet
from pyglet.gl import *

from euclid import *

def get_mock_helix():
    colors = [1.0, 0.0, 0.0]*4
    verts = [1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0]
    tex = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0]
    vertex_list = pyglet.graphics.vertex_list(len(verts)/3,
        ('v3f', verts),
        ('c3f', colors),
        ('t2f', tex)
    )
    return vertex_list
