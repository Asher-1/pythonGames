import sys
from math import atan2, degrees, sqrt

import pyglet
from pyglet import gl

import cocos.layer, cocos.draw
from cocos.cocosnode import CocosNode
from cocos.sprite import Sprite
from cocos.director import director
from gamelib.util import Vector, cargar, to_tuple
import os, os.path

pyglet.resource.path.append(os.path.join(os.path.dirname(__file__), "data"))
pyglet.resource.path.append(os.path.join(os.path.dirname(__file__), os.path.join("cocos", "resources")))
pyglet.resource.reindex()

class Cursor (Sprite):
    def __init__ (self):
        super(Cursor, self).__init__(cargar('cursor.png'))
        self.scale = 0.25

class CenterMarker(Sprite):
    def __init__ (self):
        super(CenterMarker, self).__init__(cargar('highlight_checkpoint.png'))


class Body (cocos.draw.Canvas):

    def __init__ (self):
        """position es un Vector (el centro de masa)
           points es una lista de vertices (coordenadas relativas a position)
        """
        super (Body, self).__init__()
        self.points = []
        self.mass = 0
        self.center = None
        self.moment_i = 0
        self.v_drag = 0
        self.w_drag = 0

    def render (self):
        p = self.points[-1].real, self.points[-1].imag
        self.move_to (p)
        for v in self.points:
            p = v.real, v.imag
            self.line_to (p)

    def set_points(self, p):
        self.points = p
        self._dirty=True
        self._context_change = True

    def unserialize(self, f):
        for line in f.readlines():
            if line.startswith('Center:'):
                self.center = tuple(float(f) for f in line[7:].strip().split())
            elif line.startswith('Mass:'):
                self.mass = float(line[5:].strip())
            elif line.startswith('MofI:'):
                self.moment_i = float(line[5:].strip())
            elif line.startswith('Point:'):
                x, y = (float(f) for f in line[6:].strip().split())
                self.points.append(Vector(x, y))
            elif line.startswith('VDrag:'):
                self.v_drag = float(line[6:].strip())
            elif line.startswith('WDrag:'):
                self.w_drag = float(line[6:].strip())

class Point (CocosNode):
    def __init__ (self, x, y):
        super(Point, self).__init__()
        self.good = Sprite(cargar('point.png'))
        self.bad = Sprite(cargar('badpoint.png'))
        self.add(self.good, name="good")
        self.add(self.bad, name="bad")
        self.bad.visible = False
        self.position = x, y
    def pos(self):
        return Vector(*self.position)

class Editor():
    def __init__(self, filename, spriteFilename):
        self.filename = filename
        self.spriteFilename = spriteFilename
        self.body = Body()
        f = None
        try:
            f = open(self.filename)
        except:
            pass
        if not f is None:
            self.body.unserialize(f)

    def save(self):
        f = open(self.filename, 'w')
        f.write("Center: %d %d\n" % self.body.center)
        f.write("Mass: %f\n" % self.body.mass)
        f.write("MofI: %f\n" % self.body.moment_i)
        f.write("VDrag: %f\n" % self.body.v_drag)
        f.write("WDrag: %f\n" % self.body.w_drag)
        for p in reversed(self.body.points):
            f.write("Point: %f %f\n" % (p.real / float(self.grid.sprite.scale), p.imag / float(self.grid.sprite.scale)))
        f.close()
        self.status.element.text = "Saved " + self.filename

class GridLayer(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self, editor, tileSize=100):
        super(GridLayer, self).__init__()
        self.ed = editor
        editor.grid = self
        self.selected = None
        self._batch = pyglet.graphics.Batch()
        self.tileSize = tileSize
        self.cursor = Cursor()
        self.cursor.visible = False
        self.add (self.cursor, z=100)
        self.sprite = Sprite(editor.spriteFilename)
        self.sprite.scale = max(1, min(5, min (400.0 / self.sprite.width, 400.0 / self.sprite.height)))
        self.add (self.sprite,z=-2)
        self.add (self.ed.body)
        self.ed.body.visible = False
        self.center = CenterMarker()
        self.add(self.center)
        if self.ed.body.center is None:
            self.setCenter()
        else:
            self.sprite.position = ((self.sprite.image_anchor[0] - self.ed.body.center[0]) * self.sprite.scale,
                                    (self.sprite.image_anchor[1] - self.ed.body.center[1]) * self.sprite.scale)
        self.position= 320, 240
        for p in self.ed.body.points:
            self.add(Point(p.real * self.sprite.scale, p.imag * self.sprite.scale))
        self.updatePoly()

    def on_enter(self):
        super(GridLayer, self).on_enter()
        ox, oy = self.position
        lines = []
        N = 20
        for i in range(-N, N+1):
            lines += [-N*self.tileSize, i*self.tileSize,
                      N*self.tileSize, i*self.tileSize,
                      i*self.tileSize, -N*self.tileSize,
                      i*self.tileSize, N*self.tileSize]
        self._vertex_list = self._batch.add(N*8+4, pyglet.gl.GL_LINES, None,
            ('v2i', lines))

    def on_key_press (self, key, modifiers):
        """This function is called when a key is pressed.
        
        'key' is a constant indicating which key was pressed.
        'modifiers' is a bitwise or of several constants indicating which
           modifiers are active at the time of the press (ctrl, shift, capslock, etc.)
            
        """
        key = pyglet.window.key.symbol_string (key)
        if key == 'F2':
            self.ed.save()
        elif key == 'DELETE':
            if not self.selected is None:
                self.remove(self.selected)
                self.cursor.visible = False
                self.updatePoly()
        elif key == 'H':
            self.show_help()

    def show_help(self):
        print """
Add points to the polygon: left click
Select points:             hover over them with the mouse
Move points:               drag them while they're selected
Delete points:             press 'DELETE' while they're selected
Move center of mass:       drag the yellow marker
Save to file:              press 'F2'
Modify mass/moment of inertia: You can't.  Edit the file directly,
                               the editor will preserve any value in the file.

"""
        self.ed.status.element.text = "Go check standard output!"

    def on_exit(self):
        super(GridLayer, self).on_exit()
        self._vertex_list.delete()
        self._vertex_list = None

    def draw(self):
        super(GridLayer, self).draw()
        gl.glPushMatrix()
        self.transform()
        gl.glTranslatef( 
                -self.children_anchor_x, 
                -self.children_anchor_y,
                 0 )
        gl.glPushAttrib(gl.GL_CURRENT_BIT)
        self._batch.draw()
        gl.glPopAttrib()
        gl.glPopMatrix()

    def on_mouse_motion (self, x, y, dx, dy):
        x, y = director.get_virtual_coordinates (x, y)
        pos = Vector(x - self.x, y - self.y)
        for child in self.get_points():
            if isinstance(child, Point) and abs(pos - child.pos()) < 8:
                self.cursor.position = child.position
                self.cursor.visible = True
                self.selected = child
                break
        else:
            self.cursor.visible = False
            self.selected = None

    def get_points(self):
        return [x for x in self.get_children() if isinstance(x, Point)]

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.clicking = False
        # First check if she's dragging the center marker
        X = x - self.position[0]
        Y = y - self.position[1]
        if not self.selected is None:
            self.selected.position = self.selected.position[0] + dx, self.selected.position[1] + dy
            self.cursor.position = self.cursor.position[0] + dx, self.cursor.position[1] + dy
            self.updatePoly()
        elif sqrt(X * X + Y * Y) < 10:
            self.position = (self.position[0] + dx, self.position[1] + dy)
            self.sprite.position = (self.sprite.position[0] - dx, self.sprite.position[1] - dy)
            for p in self.get_points():
                p.position = (p.position[0] - dx, p.position[1] - dy)
            self.updatePoly()
            self.setCenter()
        else:
            self.position = (self.position[0] + dx, self.position[1] + dy)

    def setCenter(self):
            s = self.sprite
            self.ed.body.center = (s.image_anchor[0] - s.position[0] / float(s.scale),
                                   s.image_anchor[1] - s.position[1] / float(s.scale))

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.clicking = True

    def on_mouse_release(self, x, y, button, modifiers):
        if self.clicking:
            posx, posy = cocos.director.director.get_virtual_coordinates (x, y)
            posx -= self.position[0]
            posy -= self.position[1]
            self.add(Point(posx, posy))
            self.updatePoly()

    def _isRightTurn(self, (p, q, r)):
        p,q,r = p.position, q.position, r.position
        sum1 = q[0]*r[1] + p[0]*q[1] + r[0]*p[1]
        sum2 = q[0]*p[1] + r[0]*q[1] + p[0]*r[1]
        return sum1 - sum2 < 0

    def _pointCompare(self, a, b):
        if a.position < b.position:
            return -1
        elif a.position == b.position:
            return 0
        else:
            return 1

    def updatePoly(self):
        points = self.get_points()
        points.sort(self._pointCompare)
        # Remove any duplicates
        points = [points[i] for i in range(len(points)) if i or points[i].position != points[i-1].position]
        if len(points) < 3:
            return
        # Build upper half of the hull.
        upper = [points[0], points[1]]
        for p in points[2:]:
            upper.append(p)
            while len(upper) > 2 and not self._isRightTurn(upper[-3:]):
                del upper[-2]

        # Build lower half of the hull.
        points.reverse()
        lower = [points[0], points[1]]
        for p in points[2:]:
            lower.append(p)
            while len(lower) > 2 and not self._isRightTurn(lower[-3:]):
                del lower[-2]

        # Remove duplicates.
        del lower[0]
        del lower[-1]

        # Paint them red
        chull = lower+upper
        for point in self.get_points():
            point.good.visible = point in chull
            point.bad.visible = not point.good.visible
        #Update the body
        if len(chull) > 0:
            self.ed.body.set_points ([Vector(*p.position) for p in chull])
            self.ed.body.visible = True
        else:
            self.ed.body.visible = False
        
class EditorScene(cocos.scene.Scene):
    def __init__(self):
        super(EditorScene, self).__init__()
        self.editor = Editor(sys.argv[1], sys.argv[2])
        self.add (GridLayer(self.editor))
        self.status = cocos.text.Label("Press 'H' for Help", x=30, y=10)
        self.editor.status = self.status
        self.add(self.status)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: %s <polygonFilename> <spriteFilename>" % sys.argv[0]
        sys.exit(-1)
    cocos.director.director.init()

    main_scene = EditorScene()

    # And now, start the application, starting with main_scene
    cocos.director.director.run (main_scene)

