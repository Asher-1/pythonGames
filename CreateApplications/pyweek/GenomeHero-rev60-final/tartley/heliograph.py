from batchmanager import batch
from drawgroups import *
import math
import collections
import random

#RADIUS = 1
SPINRATE = 1
#START_HGT = 11
CLIMBRATE = 0.5
#MAXHGT = START_HGT - (math.pi * CLIMBRATE / SPINRATE)*7
#ENDHGT = -9

### default colors
END_COLORS = [0.1,0.3,0.1,0.6]
LCON_COLORS = []
RCON_COLORS = []

BASE_COLORS = []
for c in range(2):
    BASE_COLORS+=[0.1, 0.0, 0.5, 0.5]
RBCOLORS = []
for c in range(2):
    RBCOLORS+=[0.5, 0.0, 0.1, 0.5]

_BASE_COLORS = {
    "A": [1, 1, 0, 0.4]*4,
    "T": [0, 1, 0, 0.4]*4,
    "C": [0, 0, 1, 0.4]*4, # red 0.30 green 0.30 blue 1.00
    "G": [1, 0, 0, 0.4]*4,
    None: [0,0,0,0]*4,
}

_COMPLETE_COLOR = [0, 1, 1, 1.0]*4

_OBS_BASE = [0, 1, 1, 0.2]*4

QUAD_WIDTH = 0.1

END_RADIUS = 0.12
END_ITERATIONS = 7
END_XY_STEP = 2 * math.pi / END_ITERATIONS
END_Z_STEP = math.pi / END_ITERATIONS
END_XY_ANGLES = [END_XY_STEP * i for i in range(END_ITERATIONS)]
END_Z_ANGLES = [END_Z_STEP * i * 4 for i in range(END_ITERATIONS)]
END_TRIWIDTH = 0.7
END_SPINRATE = 1.1

### SPHERE settings for ends of rungs
SP_RADIUS = 0.08
SP_RAD_MUTATION_AMT = 0.02
SP_ITERATIONS = 5
SP_XY_STEP = 2 * math.pi / SP_ITERATIONS
SP_Z_STEP = math.pi / SP_ITERATIONS
SP_XY_ANGLES = [SP_XY_STEP * i for i in range(SP_ITERATIONS)]
SP_Z_ANGLES = [SP_Z_STEP * i * 4 for i in range(SP_ITERATIONS)]
SP_SPINRATE = 0.5
SP_COLORS = [0.1, 0.4, 0.4, 0.75]
SP_TRISIZE = 0.02
SP_TRI_MUTATION_AMT = 0.016

VCPGDict = collections.namedtuple(
    'vcpgdict',
    ['vertices', 'colors', 'prim_types', 'drawgroups', 'parents']
)

### default pyglet vertex list formats
VFORMAT = 'v3f'
CFORMAT = 'c4f'

### drawgroups for rung graphics
GRP_RUNG_END = GRP_BLEND#PointGroup(16, GRP_SMOOTH_POINTS)
GRP_SPHEREPOINTS = GRP_BLEND#PointGroup(4, GRP_ROUGH_POINTS)
GRP_BASE = GRP_BLEND#LineWidthGroup(8)

class HelioGraph:
    def update(self, dt):
        self.vertex_list.vertices = self.get_vertices()
        self.vertex_list.colors = self.get_colors()

    def delete(self):
        self.vertex_list.delete()

    def get_vertices(self):
        pass

class RungEnds(HelioGraph):
    def __init__(self, rung, magic = math.pi, sign = 1):
        self.rung = rung
        self.magic = magic
        self.sign = sign
        vertices = (VFORMAT, self.get_vertices())
        colors = (CFORMAT, self.get_colors())
        prim_type = GL_TRIANGLES
        drawgroup = GRP_RUNG_END
        geometry = VCPGDict(
            vertices=[vertices],
            colors=[colors],
            prim_types=[prim_type],
            drawgroups=[drawgroup],
            parents=[self],
        )
        batch.add(geometry)

    def get_vertices(self):
        endvertices = []
        for a in END_XY_ANGLES:
            mut = self.rung.helix.mutation.amount * 0.05
            rad = END_RADIUS + random.random() * mut
            spin = self.rung.spin * END_SPINRATE
            xmod = math.sin(a+spin) * rad
            ymod = math.sin(a) * rad
            zmod = math.cos(a+spin) * rad
            xmod2 = math.sin(a+spin+END_XY_STEP*END_TRIWIDTH) * rad
            ymod2 = math.sin(a+END_XY_STEP) * rad
            zmod2 = math.cos(a+spin+END_XY_STEP*END_TRIWIDTH) * rad
            spin = self.rung.spin
            cos_spin = math.cos(spin+self.magic)
            sin_spin = math.sin(spin+self.magic)
            if self.rung._hgt > self.rung.maxhgt:
                midx = cos_spin * self.rung.radius
                midy = sin_spin * self.rung.radius
                midz = self.rung._hgt
            else:
                midx = -self.rung.radius * self.sign
                midy = 0
                midz = self.rung._hgt
            endvertices += [
                    midx,
                    midy,
                    midz,
                    midx + xmod,
                    midy,
                    midz + zmod,
                    midx + xmod2,
                    midy,
                    midz + zmod2,
                ]
        self.rung.endpoints+=endvertices[0:3]
        return endvertices

    def get_colors(self):
        return END_COLORS*3*END_ITERATIONS

class Base(HelioGraph):
    def __init__(self, rung, _type, magic=0, sign = 1):
        self.rung = rung
        self.magic = magic
        self.sign = -sign
        self._type = _type
        self.obscured = False
        self.complete = False
        vertices = (VFORMAT, self.get_vertices())
        colors = (CFORMAT, self.get_colors())
        prim_type = GL_QUADS
        drawgroup = GRP_BLEND_ONE_MINUS
        geometry = VCPGDict(
            vertices=[vertices],
            colors=[colors],
            prim_types=[prim_type],
            drawgroups=[drawgroup],
            parents=[self],
        )
        batch.add(geometry)

    def get_vertices(self):
        mut = self.rung.helix.mutation.amount*0.02
        basevertices = []
        end = []
        end += [
            self.rung.endpoints[0+self.magic],
            self.rung.endpoints[1+self.magic],
            self.rung.endpoints[2+self.magic],
        ]
        bothgt = self.rung._hgt - 0.05
        tophgt = self.rung._hgt + 0.05
        if self.rung._hgt > self.rung.maxhgt:
            basevertices += [
                end[0]+random.uniform(-mut,mut),
                end[1]+random.uniform(-mut,mut),
                bothgt+random.uniform(-mut,mut),
                0+random.uniform(-mut,mut),
                0+random.uniform(-mut,mut),
                bothgt+random.uniform(-mut,mut),
                0+random.uniform(-mut,mut),
                0+random.uniform(-mut,mut),
                tophgt+random.uniform(-mut,mut),
                end[0]+random.uniform(-mut,mut),
                end[1]+random.uniform(-mut,mut),
                tophgt+random.uniform(-mut,mut),
                #self.rung.cos_spin * self.rung.radius * self.sign,
                #self.rung.sin_spin * self.rung.radius * self.sign,
                #tophgt,

            ]
        else:
            basevertices += [
                0+random.uniform(-mut,mut),
                0+random.uniform(-mut,mut),
                bothgt+random.uniform(-mut,mut),
                -self.rung.radius * self.sign+random.uniform(-mut,mut),
                0+random.uniform(-mut,mut),
                bothgt+random.uniform(-mut,mut),
                ## ====================================
                -self.rung.radius * self.sign+random.uniform(-mut,mut),
                0+random.uniform(-mut,mut),
                tophgt+random.uniform(-mut,mut),
                0+random.uniform(-mut,mut),
                0+random.uniform(-mut,mut),
                tophgt+random.uniform(-mut,mut)
                ## =====================================
            ]
        #print len(basevertices)
        return basevertices

    def get_colors(self):
        #print self._type
        if self.obscured:
            return _OBS_BASE
        elif self.complete:
            return _COMPLETE_COLOR
        else:
            return _BASE_COLORS[self._type]

class Sphere(HelioGraph):
    def __init__(self, rung, magic=0):
        self.rung = rung
        self.magic = int(magic)
        vertices = (VFORMAT, self.get_vertices())
        colors = (CFORMAT, self.get_colors())
        prim_type = GL_TRIANGLES
        drawgroup = GRP_SPHEREPOINTS
        geometry = VCPGDict(
            vertices=[vertices],
            colors=[colors],
            prim_types=[prim_type],
            drawgroups=[drawgroup],
            parents=[self],
        )
        batch.add(geometry)

    def get_vertices(self):
        spvertices = []
        rad = SP_RADIUS+self.rung.helix.mutation.amount*SP_RAD_MUTATION_AMT
        for a in SP_XY_ANGLES:
            xmod = math.sin(a-self.rung.spin) * rad
            ymod = 0
            #ymod = math.sin(a) * rad
            zmod = math.cos(a-self.rung.spin) * rad
            spin = self.rung.spin * -2
            size = SP_TRISIZE+self.rung.helix.mutation.amount*SP_TRI_MUTATION_AMT
            x1 = math.sin(spin) * size
            z1 = math.cos(spin) * size
            x2 = math.sin(spin+math.radians(120)) * size
            z2 = math.cos(spin+math.radians(120)) * size
            x3 = math.sin(spin+math.radians(240)) * size
            z3 = math.cos(spin+math.radians(240)) * size
            spvertices += [
                self.rung.endpoints[0+self.magic] + xmod + x1,
                self.rung.endpoints[1+self.magic] + ymod,
                self.rung.endpoints[2+self.magic] + zmod + z1,
                self.rung.endpoints[0+self.magic] + xmod + x2,
                self.rung.endpoints[1+self.magic] + ymod,
                self.rung.endpoints[2+self.magic] + zmod + z2,
                self.rung.endpoints[0+self.magic] + xmod + x3,
                self.rung.endpoints[1+self.magic] + ymod,
                self.rung.endpoints[2+self.magic] + zmod + z3,
                #self.rung.endpoints[0+self.magic] + xmod - size,
                #self.rung.endpoints[1+self.magic] + ymod,
                #self.rung.endpoints[2+self.magic] + zmod + size,
            ]
        return spvertices
    def get_colors(self):
        colors = SP_COLORS*3*SP_ITERATIONS
        mut = self.rung.helix.mutation.amount*0.02
        for i in range(len(colors)):
            colors[i] += random.uniform(-mut,mut)
        return colors

class Connect(HelioGraph):
    def __init__(self, rung, magic=0):
        self.rung = rung
        self.magic = int(magic)
        vertices = (VFORMAT, self.get_vertices())
        colors = (CFORMAT, self.get_colors())
        prim_type = GL_QUADS
        drawgroup = GRP_BLEND_ONE_MINUS
        geometry = VCPGDict(
            vertices=[vertices],
            colors=[colors],
            prim_types=[prim_type],
            drawgroups=[drawgroup],
            parents=[self],
        )
        batch.add(geometry)

    def get_vertices(self):
        cvertices = []
        if self.rung._last_ends:
            verts = self.rung.endpoints
            lastverts = self.rung._last_ends.endpoints
            zmod = QUAD_WIDTH / 2
            cvertices += [

                lastverts[0+self.magic],
                lastverts[1+self.magic],
                lastverts[2+self.magic]-zmod,
                
                verts[0+self.magic],
                verts[1+self.magic],
                verts[2+self.magic]-zmod,
                
                verts[0+self.magic],
                verts[1+self.magic],
                verts[2+self.magic]+zmod,
                lastverts[0+self.magic],
                lastverts[1+self.magic],
                lastverts[2+self.magic]+zmod,
                
#                self.rung.graphics['rung_ends'].vertex_list.vertices[0+self.magic],
#                self.rung.graphics['rung_ends'].vertex_list.vertices[1+self.magic],
#                self.rung.graphics['rung_ends'].vertex_list.vertices[2+self.magic],
#                self.rung._last_ends.graphics['rung_ends'].vertex_list.vertices[0+self.magic],
#                self.rung._last_ends.graphics['rung_ends'].vertex_list.vertices[1+self.magic],
#                self.rung._last_ends.graphics['rung_ends'].vertex_list.vertices[2+self.magic],
            ]
        else:
            cvertices += [-5,-5,-5]*4
        return cvertices

    def get_colors(self):
        return END_COLORS*4

