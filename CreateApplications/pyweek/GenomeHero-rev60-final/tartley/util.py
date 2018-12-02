from euclid import *
import collections

VCPGDict = collections.namedtuple(
    'vcpgdict',
    ['vertices', 'colors', 'prim_types', 'drawgroups', 'parents']
)


def split_list(L, n):
    #assert type(L) is list, "L is not a list"
    for i in range(0, len(L), n):
        yield L[i:i+n]

def translate_vertex_list(vertex_list, vector, value= 1.0):
    v = vector
    tm = Matrix4.new_translate(v.x, v.y, v.z)
    new_verts = []
    for vert in split_list(vertex_list.vertices, 3):
        p = tm*Point3(vert[0], vert[1], vert[2])
        new_verts+= [p.x,p.y,p.z]
    vertex_list.vertices = new_verts
    
def rotate_vertex_listY(vertex_list, angle):
    r = Matrix4.new_rotatez(angle)
    new_verts = []
    for vert in split_list(vertex_list.vertices, 3):
        p = r*Point3(vert[0], vert[1], vert[2])
        new_verts+= [p.x,p.y,p.z]
    vertex_list.vertices = new_verts


def scale_vertex_list(vertex_list, amt):
    s = Matrix4.new_scale(amt, amt, amt)
    new_verts = []
    #print "scale - >", vertex_list.vertices[:]
    for vert in split_list(vertex_list.vertices, 3):
        #print vert
        p = s*Point3(vert[0], vert[1], vert[2])
        new_verts+= [p.x,p.y,p.z]
    #print new_verts
    vertex_list.vertices = new_verts


