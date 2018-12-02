import pyglet
from pyglet.gl import *
from platform import *

NORM_LINE = 2
WIDE_LINE = 4
THIN_LINE = 1
NORM_POINT = 4
SMOOTH_LINES = True

class BlendGroup(pyglet.graphics.Group):
    def __init__(self, parent=None):
        super(BlendGroup, self).__init__(parent=parent)
        
    def set_state(self):
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glEnable(GL_BLEND)
        glDepthMask(GL_FALSE)

    def unset_state(self):
        glDisable(GL_BLEND)
        glDepthMask(GL_TRUE)

GRP_BLEND = BlendGroup()

class OneAlphaGroup(pyglet.graphics.Group):
    def __init__(self):
        super(OneAlphaGroup, self).__init__(parent=GRP_BLEND)

    def set_state(self):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

GRP_BLEND_ONE = OneAlphaGroup()

class OneMinusAlphaGroup(pyglet.graphics.Group):
    def __init__(self):
        super(OneMinusAlphaGroup, self).__init__(parent=GRP_BLEND)

    def set_state(self):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
GRP_BLEND_ONE_MINUS = OneMinusAlphaGroup()

class LineSmoothGroup(pyglet.graphics.Group):
    def __init__(self):
        super(LineSmoothGroup, self).__init__(parent=GRP_BLEND_ONE)

    def set_state(self):
        glEnable(GL_LINE_SMOOTH)

GRP_LINE_SMOOTH = LineSmoothGroup()

class LineRoughGroup(pyglet.graphics.Group):
    def __init__(self):
        super(LineRoughGroup, self).__init__(parent=GRP_BLEND_ONE)

    def set_state(self):
        glDisable(GL_LINE_SMOOTH)

GRP_LINE_ROUGH = LineRoughGroup()

class LineWidthGroup(pyglet.graphics.Group):
    def __init__(self, width):
        super(LineWidthGroup, self).__init__(parent=GRP_LINE_SMOOTH)
        if OSX:
            pass
        self.width = width

    def set_state(self):
        glLineWidth(int(self.width))

class LineRoughWidthGroup(pyglet.graphics.Group):
    def __init__(self, width):
        super(LineRoughWidthGroup, self).__init__(parent=GRP_LINE_ROUGH)
        if OSX:
            pass
        self.width = width

    def set_state(self):
        glLineWidth(int(self.width))
        
class LinePolyGroup(pyglet.graphics.Group):
    def __init__(self, parent=None):
        super(LinePolyGroup, self).__init__(parent=parent)
        
    def set_state(self):
        glPolygonMode(GL_FRONT, GL_LINE)
        
    def unset_state(self):
        glPolygonMode(GL_FRONT, GL_FILL)
        
class SmoothPointGroup(pyglet.graphics.Group):
    def __init__(self, parent=GRP_BLEND_ONE):
        super(SmoothPointGroup, self).__init__(parent=parent)
        
    def set_state(self):
        glEnable(GL_POINT_SMOOTH)

class RoughPointGroup(pyglet.graphics.Group):
    def __init__(self, parent=GRP_BLEND_ONE):
        super(RoughPointGroup, self).__init__(parent=parent)
        
    def set_state(self):
        glDisable(GL_POINT_SMOOTH)

class PointGroup(pyglet.graphics.Group):
    def __init__(self, size, parent=None):
        super(PointGroup, self).__init__(parent=parent)
        if OSX:
            #size *= 0.8
            pass
        self.size = size

    def set_state(self):
        glPointSize(int(self.size))
	
GRP_SMOOTH_POINTS = SmoothPointGroup()
GRP_ROUGH_POINTS = RoughPointGroup()
GRP_POINTS_SMOOTH = PointGroup(NORM_POINT, GRP_SMOOTH_POINTS)
        
GRP_LINE_DRAW = LineWidthGroup(NORM_LINE)
GRP_LINE_DRAW_WIDE = LineWidthGroup(WIDE_LINE)
GRP_LINE_DRAW_THIN = LineWidthGroup(THIN_LINE)
GRP_LINE_POLY = LinePolyGroup(GRP_LINE_DRAW)
GRP_LINE_POLY_WIDE = LinePolyGroup(GRP_LINE_DRAW_WIDE)
GRP_LINE_POLY_THIN = LinePolyGroup(GRP_LINE_DRAW_THIN)

class CullGroup(pyglet.graphics.Group):
    def __init__(self, parent=None):
        super(CullGroup, self).__init__(parent=parent)
        
    def set_state(self):
        glEnable(GL_CULL_FACE)
    
    def unset_state(self):
        glDisable(GL_CULL_FACE)
        
GRP_CULL = CullGroup()
#GRP_CULL_BLEND_ONE = CullGroup(GRP_BLEND_ONE)
GRP_CULL_BLEND_ONE_MINUS = CullGroup(GRP_BLEND_ONE_MINUS)

class TextureEnableGroup(pyglet.graphics.Group):
    def __init__(self, parent=None):
        super(TextureEnableGroup, self).__init__(parent=parent)

    def set_state(self):
        glEnable(GL_TEXTURE_2D)

    def unset_state(self):
        glDisable(GL_TEXTURE_2D)

#GRP_TEX_2D = TextureEnableGroup()
GRP_TEX_BLEND = TextureEnableGroup(GRP_BLEND_ONE)
GRP_TEX_CULL = TextureEnableGroup(GRP_CULL)

class TextureBindGroup(pyglet.graphics.Group):
    def __init__(self, texture):
        super(TextureBindGroup, self).__init__(parent=GRP_TEX_CULL)
        assert texture.target == GL_TEXTURE_2D
        self.texture = texture
        
    def set_state(self):
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and self.texture == other.texture)
        
class TextureBlendGroup(pyglet.graphics.Group):
    def __init__(self, texture):
        super(TextureBlendGroup, self).__init__(parent=GRP_TEX_BLEND)
        assert texture.target == GL_TEXTURE_2D
        self.texture = texture
        
    def set_state(self):
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and self.texture == other.texture)
