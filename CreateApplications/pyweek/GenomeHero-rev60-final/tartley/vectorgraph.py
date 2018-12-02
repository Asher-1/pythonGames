
from batchmanager import batch
from drawgroups import *
from letters import *
from euclid import *
from util import *



###############################################################################
############################################################### VectorChar ####
###############################################################################

class VectorString (object):

    def __init__(self, string, pos=(-1,0,0), size=0.08, 
        color=([0.0,0.7,0.0,1.0], [0.0,0.1,0.0,1.0])):
        self.string = string
        self.color = color
        pos = Vector3(0,0,0) + pos
        self.pos = pos
        self.char_list = []
        spacing = size + (size/1.5)
        for n in range(len(string)):
            new_pos = pos + (0+(spacing*n),0,0)
            self.char_list += [VectorChar(string[n], new_pos, size, color)]
        self.width = spacing * len(string)

    def set_string(self, string):
        if not len(self.char_list) >= len(string):
            print "string not the same size!"
            for n in self.char_list:
                n.set_char('blork')
        else:
            x = 0
            for n in (self.char_list):
                n.set_char(string[x])
                x += 1

    def set_colors(self, colors):
        for c in self.char_list:
            c.set_colors(colors)

    def get_colors(self):
        return self.color

    def set_position(self, pos):
        pos = Point3(pos[0], pos[1], pos[2])
            
    def move(self, vec):
        vec = Vector3(vec[0], vec[1], vec[2])
        for n in (self.char_list):
            n.move(vec)
            
    def delete(self):
        for n in (self.char_list):
            n.delete()


###############################################################################
############################################################ VectorChar #######
###############################################################################

class VectorChar (object):

    def __init__(self, char, pos=Point3(0,0,0), size=0.1, color=None):
        self.char = char
        self.pos = pos
        self.size = size
        self.colors = color
        vcpgdict = VCPGDict(
            vertices=[self.get_vertices()],
            colors=[self.get_colors()],
            prim_types=[self.get_prim_type()],
            drawgroups=[self.get_drawgroup()],
            parents=[self],
        )
        batch.add(vcpgdict)
        scale_vertex_list(self.vertex_list, size)
        translate_vertex_list(self.vertex_list, pos)

    def set_colors(self, colors):
        self.colors = colors
        self.vertex_list.colors = self.get_colors()[1]
        
        
    def set_char(self, c):
        #print "setting", c
        self.char = c
        self.vertex_list.colors = self.get_colors()[1]

    def set_position(self, pos):
        self.pos = pos
        self.vertex_list.vertices = self.get_vertices()[1]

    def move(self, vec):
        vec = Vector3(vec[0], vec[1], vec[2])
        translate_vertex_list(self.vertex_list, vec)

    def delete(self):
        try:
            self.vertex_list.delete()
        except:
            pass #print "leaked vbo"
        
    def get_vertices(self):
        vertices_format = 'v3f'
        vertices = []
        for r in display_verts:
            for v in r:
                vertices += v
        return (vertices_format,vertices)
        
    def get_colors(self):
        colors = []
        if chars.has_key(self.char):
            char = chars[self.char]
        else:
            char = BLORK
        for r in char:
            for c in r:
                if c:
                    colors += self.colors[0] *2
                else:
                    colors += self.colors[1] *2
        colors = ('c4f', colors)
        return colors
        
    def get_prim_type(self):
        return GL_LINES
        
    def get_drawgroup(self):
        return GRP_LINE_POLY
        
    def get_parent(self):
        return self

