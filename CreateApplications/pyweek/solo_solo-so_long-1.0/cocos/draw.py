import cocosnode
import pyglet
from pyglet.gl import *
from euclid import *
import math
import copy

cuadric_t = '''
void main() {
    vec2 pos = gl_TexCoord[0].st;
    float res = pos.x*pos.x - pos.y;
    if (res<0.0) {
        gl_FragColor = gl_Color;
    } else {
        gl_FragColor = vec4(0.0,0.0,0.0,0.0);
    }
}
'''

class Shader(object):
    def __init__(self, source):
        self.source = source 
        self.shader_no = glCreateShader(self.shader_type)
        if not self.shader_no:
            raise Exception("could not create shader")
        prog = (c_char_p * 1)(source+chr(0))
        length = (c_int * 1)(0)
        glShaderSource(self.shader_no, 1,
                          cast(prog, POINTER(POINTER(c_char))),
                          cast(0, POINTER(c_int)))
        glCompileShader(self.shader_no)
        self.program_no = glCreateProgram()
        if not self.program_no:
            raise Exception("could not create program")
        glAttachShader(self.program_no, self.shader_no)
        glLinkProgram(self.program_no)
        
    def begin(self):
        glUseProgram(self.program_no)
    def end(self):
        glUseProgram(0)
    

class VertexShader(Shader):
    shader_type = GL_VERTEX_SHADER

class FragmentShader(Shader):
    shader_type = GL_FRAGMENT_SHADER
    
#cuadric = FragmentShader(cuadric_t)

def parameter(default=None):
    o = object()
    name = str(id(o))
    
    def setter(self, value):
        self._dirty = True
        setattr(self, "_"+name, value)
        
    def getter(self):
        return getattr(self, "_"+name, default)
    
    
    return property(getter, setter)
    
ROUND_CAP, SQUARE_CAP, BUTT_CAP = range(3)
MITER_JOIN, BEVEL_JOIN, ROUND_JOIN = range(3)

class Context(object):
    def __init__(self):
        self.color = 255,255,255,255
        self.stroke_width = 2
        self.cap = ROUND_CAP
        self.join = ROUND_JOIN
        self.transform = Matrix3()
        
    def set_state(self):
        glPushAttrib(GL_CURRENT_BIT|GL_LINE_BIT)
        glColor4ub(*self.color)
        glLineWidth(self.stroke_width)
        
    def unset_state(self):
        glPopAttrib()
        
    def copy(self):
        return copy.deepcopy(self)
        
        
def flatten(*args):
    ret = []
    for a in args:
        for v in a:
            ret.append( v )
    return ret
    
class Segment:
    def __init__(self, start, end, width):
        self.start = Point2(*start)
        self.end = Point2(*end)
        self.width = width
        self._tl = None
        self._bl = None
        self._tr = None
        self._br = None
        
    @property
    def direction(self):
        return Vector2( *(self.end-self.start)).normalized()
        
    @property
    def line_width(self):
        return ( 
            Matrix3.new_rotate(math.radians(90)) * self.direction *
            (self.width / 2.0)
            )
            
    @property
    def tl(self):
        if self._tl: return self._tl
        return self.end + self.line_width
    @property
    def tr(self):
        if self._tr: return self._tr
        return self.end - self.line_width
    @property
    def bl(self):
        if self._bl: return self._bl
        return self.start + self.line_width
    @property
    def br(self):
        if self._br: return self._br
        return self.start - self.line_width   
        
    @property
    def left(self):
        return LineSegment2( Point2(*self.bl), Point2(*self.tl) )
        
    @property
    def right(self):
        return LineSegment2( Point2(*self.br), Point2(*self.tr) )
        
    @property
    def points(self):
        return flatten( self.bl, self.br, self.tr, self.bl, self.tr, self.tl )
        
    def reversed(self):
        return Segment(self.end, self.start, self.width)
        
class Canvas(cocosnode.CocosNode):
    def __init__(self):
        super(Canvas, self).__init__()
        self._dirty = True
        self._color = 255,255,255,255
        self._stroke_width = 1
        self._parts = []        
        self._vertex_list = None
        self._context = Context()
        self._context_stack = []
        self._texture = image = pyglet.resource.image('draw_texture.png').get_texture()
        
        self._context_change = True
        self._position = 0,0
        
    def draw(self):
        if self._dirty:
            self._context = Context()
            self._parts = []
            self.free()
            self.render()
            self.build_vbo()
            self._dirty = False
            
        # set
        glEnable(self._texture.target)
        glBindTexture(self._texture.target, self._texture.id)
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glPushMatrix()
        self.transform()
        #cuadric.begin()
        self._vertex_list.draw(GL_TRIANGLES)
        #cuadric.end()
        
        # unset
        glPopMatrix()
        glPopAttrib()
        glDisable(self._texture.target)
        
    def endcap(self, line, cap_type):
        strip = []
        texcoord = []
        
        if cap_type == ROUND_CAP:
            s = Segment( line.start, 
                        line.start + (-line.direction) * line.width / 2,
                        line.width
                        )
            strip.extend([int(x) for x in flatten(
                            s.bl, s.br, s.end,
                            s.br, s.tr, s.end,
                            s.bl, s.tl, s.end
                            )])
            texcoord.extend([
                    0.1,0.9,0.1,0.5,0.5,0.9,
                    0,0,0.5,0,1,1,
                    0,0,0.5,0,1,1,
                    ])
        elif cap_type == SQUARE_CAP:
            segment = Segment( line.start, 
                        line.start + (-line.direction) * line.width / 2,
                        line.width
                        )
            strip.extend([int(x) for x in segment.points])
            texcoord.extend( flatten(*[ (0.1,0.9,0.1,0.5,0.5,0.9) for x in range(len(segment.points)/6) ]) ) 
            
        return strip, texcoord
        
    def build_vbo(self):
        strip = []
        colors = []
        texcoord = []
        for ctx, parts in self._parts:
            start_len = len(strip)
            for line in parts:
            
                # build the line segments
                last = line[0]
                segments = []
                for next in line[1:]:
                    segments.append( Segment( last, next, ctx.stroke_width ) )
                    last = next
                
                # do we need caps?
                if line[0] == line[-1]:
                    closed_path = True
                else:
                    closed_path = False
                    
                # add caps
                if not closed_path:
                    vertex, tex = self.endcap(segments[0], ctx.cap)
                    strip += vertex
                    texcoord += tex
                    vertex, tex = self.endcap(segments[-1].reversed(), ctx.cap)
                    strip += vertex
                    texcoord += tex                    
                 
                # update middle points  
                prev = None
                for i, current in enumerate(segments):
                    # if not starting line
                    if ( prev ):
                        # turns left
                        inter = prev.left.intersect( current.left )
                        if inter:
                            prev._tl = inter
                            current._bl = inter
                            bottom = prev.tr
                            top = current.br
                        else:
                            inter = prev.right.intersect( current.right )
                            if inter:
                                prev._tr = inter
                                current._br = inter
                                bottom = prev.tl
                                top = current.bl
                        
                    
                    # add elbow
                    if ( prev and inter ):
                            if ctx.join == BEVEL_JOIN:
                                strip.extend( [ int(x) for x in
                                    list(inter) + list(bottom) + list(top)
                                ])
                                texcoord += [ 0.1,0.9,0.1,0.5,0.5,0.9 ]
                            elif ctx.join in (MITER_JOIN, ROUND_JOIN):
                                far = Ray2(
                                    Point2(*bottom), prev.direction
                                    ).intersect(Ray2(
                                    Point2(*top), -current.direction
                                    ))
                                strip.extend( [ int(x) for x in
                                    list(inter) + list(bottom) + list(top) +
                                    list(bottom) + list(top) + list(far)
                                ])
                                if ctx.join == ROUND_JOIN:
                                    texcoord += [ 0.1,0.9,0.1,0.5,0.5,0.9, 0,0,1,1,0.5,0]
                                elif ctx.join == MITER_JOIN:
                                    texcoord += [ 0.1,0.9,0.1,0.5,0.5,0.9,0.1,0.9,0.1,0.5,0.5,0.9 ]

                    # rotate values
                    prev = current
                
                # add boxes for lines
                for s in segments:
                    strip.extend( [ int(x) for x in s.points ] )
                    texcoord += flatten(*[ (0.1,0.9,0.1,0.5,0.5,0.9)
                                for x in range( len(s.points)/6) 
                            ])
                            

            colors.extend( list(ctx.color)*((len(strip)-start_len)/2) )
            
        vertex_list = pyglet.graphics.vertex_list(len(strip)/2,
            ('v2i', strip),
            ('c4B', colors ),
            ('t2f', texcoord),
        )
        self._vertex_list = vertex_list
        
    def on_exit(self):
        super(Canvas, self).on_exit()
        self.free()
        
    def free(self):
        if self._vertex_list:
            self._vertex_list.delete()
            
    def set_color(self, color):
        self._context.color = color
        self._context_change = True
        
    def set_stroke_width(self, stroke_width):
        self._context.stroke_width = stroke_width
        self._context_change = True        
    
    def set_endcap(self, cap):
        self._context.cap = cap
        self._context_change = True   
        
    def set_join(self, join):
        self._context.join = join
        self._context_change = True 
        
    def rotate(self, radians):
        self._context.transform.rotate( radians )
    def translate(self, vect):
        self._context.transform.translate( *vect )
        
    def move_to(self, position):
        self._position = self._context.transform * Point2(*position)
        
    def line_to(self, end):
        if self._context_change:
            context, parts = self._context, [[self._position]]
            self._parts.append((context, parts))
            self._context = context.copy()
            self._context_change = False
        else:
            context, parts = self._parts[-1]

        end = self._context.transform * Point2(*end)
        
        if parts[-1][-1] == self._position:
            parts[-1].append( end )
        else:
            parts.append( [self._position, end] )
            
        self._position = end
        
    def push(self):
        self._context_stack.append( self._context.copy() )
        
    def pop(self):
        self._context = self._context_stack.pop()
    
        
class Line(Canvas):
    start = parameter()
    end = parameter()
    stroke_width = parameter()
    color = parameter()
    
    def __init__(self, start, end, color, stroke_width=1):
        super(Line, self).__init__()
        self.start = start
        self.end = end
        self.color = color
        self.stroke_width = stroke_width
        
    def render(self):
        self.set_color( self.color )
        self.set_stroke_width( self.stroke_width )
        self.move_to( self.start )
        self.line_to( self.end )
        
        
        