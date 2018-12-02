import pyglet
from pyglet import gl, graphics
from math import degrees, atan2

from cocos.cocosnode import CocosNode
from cocos.layer import Layer

class Soga(Layer):
    def __init__(self, start, end, model):
        super(Soga, self).__init__()
        self.model = model
        self._start = start
        self._end = end
        self._texture = pyglet.image.load('data/soga.png').get_texture(rectangle=True)
        self.update()

    def draw(self):
        gl.glEnable(self._texture.target)
        gl.glBindTexture(self._texture.target, self._texture.id)
        gl.glPushAttrib(gl.GL_COLOR_BUFFER_BIT)
        
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        gl.glPushMatrix()
        self.transform()
        gl.glTranslatef (self._start.real, self._start.imag, 0.0)
        gl.glRotatef(float(self._angle), 0.0, 0.0, 1.0)
        self._vertex_list.draw(gl.GL_QUADS)

        gl.glPopMatrix()
        gl.glPopAttrib()
        gl.glDisable(self._texture.target)

    def setStart(self, start):
        self._start = start
        self.update()
    start = property (lambda x: self._start, setStart)

    def setEnd(self, end):
        self._end = end
        self.update()
    end = property (lambda x: self._end, setEnd)

    def update(self):
        diff = self._end - self._start
        self.length = int(abs(diff))
        self._angle = degrees(atan2(diff.imag, diff.real))
        start = 1 - self.length/256.0
        self._vertex_list = graphics.vertex_list(4,
                      ('v2i', (0, -2, 0, 2, self.length, 2, self.length, -2)),
                      ('c4B', (255, 255, 255, 255) * 4),
                      ('t2f', (start, 0.0, start, 1.0, 1.0, 1.0, 1.0, 0.0)))

    def remove(self):
        if self.parent is None:
            self.visible = False
        else:
            self.parent.remove(self)
            self.model.ropes.remove (self)

