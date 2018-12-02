import sys
from math import atan2, degrees

import pyglet
from pyglet import gl

import cocos.layer
from cocos.sprite import Sprite
from cocos.director import director

from gamelib.world import World, Rock, CheckPoint, HalfCheckPoint
from gamelib.world import InitialPosition, Fish
from gamelib.util import Vector, cargar, to_tuple

import os
pyglet.resource.path.append(os.path.join(os.path.dirname(__file__), "data"))
pyglet.resource.reindex()

class Cursor (Sprite):
    def __init__ (self, pos=Vector()):
        super(Cursor, self).__init__(cargar('cursor.png'), position=to_tuple(pos))
        self.pos = pos

class Editor():
    legend = {'P': 'Initial position',
              'R': 'Rock',
              'C': 'Checkpoint',
              'F': 'Fish'}
    def __init__(self, filename):
        self.filename = filename
        self.adding = "P"
        self.halfCP = None
        try:
            f = file(filename)
        except IOError:
            filename = None
        self.world = World(filename)

    def clicked(self, posx, posy):
        if self.adding == 'R':
            rock = Rock(Vector(posx, posy))
            self.world.items.append(rock)
            self.grid.add(rock)
        elif self.adding == 'C':
            if self.halfCP is None:
                self.halfCP = HalfCheckPoint (Vector(posx, posy))
                self.grid.add (self.halfCP)
            else:
                x1, y1 = self.halfCP.position
                chkpt = CheckPoint(Vector(x1, y1), Vector(posx, posy))
                self.world.checkpoints.append(chkpt)
                self.grid.remove(self.halfCP)
                self.grid.add(chkpt)
                self.halfCP = None
        elif self.adding == 'P':
            initialpos = InitialPosition(Vector(posx, posy))
            self.world.initialposs.append(initialpos)
            self.grid.add(initialpos)
            self.grid.setRotating (initialpos)
        elif self.adding == 'F':
            fish = Fish(Vector(posx, posy))
            self.world.fish.append(fish)
            self.grid.add(fish)
            self.grid.setRotating (fish)

    def sortCheckPoint (self, delta):
        if self.grid.selected is None or not isinstance (self.grid.selected.parent, CheckPoint):
            return
        cps = self.world.checkpoints
        index = cps.index(self.grid.selected.parent)
        if index +delta >= 0 and index + delta < len(cps):
            cp = cps.pop(index)
            cps.insert(index + delta, cp)
            cps[index].get("label").element.text = str(index)
            cps[index+delta].get("label").element.text = str(index + delta)

    def save (self):
        self.world.save(self.filename)
        self.status.element.text = "Saved " + self.filename

    def delete (self):
        if self.grid.selected is None:
            return
        child = self.grid.selected
        if isinstance (child, Fish):
            self.grid.remove(child)
            self.world.fish.remove(child)
        elif isinstance (child, Rock):
            self.grid.remove(child)
            self.world.items.remove(child)
        elif isinstance (child, InitialPosition):
            self.grid.remove(child)
            self.world.initialposs.remove(child)
        elif isinstance (child.parent, CheckPoint):
            self.grid.remove(child.parent)
            self.world.checkpoints.remove(child.parent)
        self.grid.cursor.visible = False

    def showHelp(self):
        print """
Drag with the mouse to move around the map, or scroll around with the arrow keys.
Clicking on the map adds the item you're currently adding.
You can add the following interesting stuff:
'P': Initial position
'C': Check point
'R': Rock
'F': Fish

To delete a feature hover over it and press 'DELETE'.

To reorder checkpoints, hover over a checkpoint and use '>' and '<'

Also, 'F2' saves the file, 'ESCAPE' quits, and 'H' shows this message, duh."""
        self.status.element.text = "Now go read standard output."

    scrollAmount = 40

    def scrollUp(self):
        self.grid.position = self.grid.position[0], self.grid.position[1] - self.scrollAmount

    def scrollDown(self):
        self.grid.position = self.grid.position[0], self.grid.position[1] + self.scrollAmount

    def scrollLeft(self):
        self.grid.position = self.grid.position[0] + self.scrollAmount, self.grid.position[1]

    def scrollRight(self):
        self.grid.position = self.grid.position[0] - self.scrollAmount, self.grid.position[1]

class KeyDisplay(cocos.layer.Layer):
    is_event_handler = True     #: enable pyglet's events
    def __init__(self, editor):
        self.ed = editor
        super( KeyDisplay, self ).__init__()
        self.text = cocos.text.Label("", x=10, y=10)
        self.update_text()
        self.add(self.text) 

    def update_text(self):
        text = 'Adding: ' + self.ed.legend.get (self.ed.adding, self.ed.adding)
        # Update self.text
        self.text.element.text = text

    def on_key_press (self, key, modifiers):
        """This function is called when a key is pressed.
        
        'key' is a constant indicating which key was pressed.
        'modifiers' is a bitwise or of several constants indicating which
           modifiers are active at the time of the press (ctrl, shift, capslock, etc.)
            
        """
        key = pyglet.window.key.symbol_string (key)
        if key == 'F2':
            self.ed.save()
        elif key == 'H':
            self.ed.showHelp()
        elif key == 'DELETE':
            self.ed.delete()
        elif key == 'GREATER':
            self.ed.sortCheckPoint(1)
        elif key == 'LESS':
            self.ed.sortCheckPoint(-1)
        elif key == 'UP':
            self.ed.scrollUp()
        elif key == 'DOWN':
            self.ed.scrollDown()
        elif key == 'LEFT':
            self.ed.scrollLeft()
        elif key == 'RIGHT':
            self.ed.scrollRight()
        else:
            self.ed.adding = key
        self.update_text()

class GridLayer(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self, editor, tileSize=100):
        super(GridLayer, self).__init__()
        self.ed = editor
        editor.grid = self
        self._batch = pyglet.graphics.Batch()
        self.tileSize = tileSize
        for item in self.ed.world.items:
            self.add (item)
        for initialpos in self.ed.world.initialposs:
            self.add (initialpos)
        for chkpt in self.ed.world.checkpoints:
            self.add (chkpt)
        for fish in self.ed.world.fish:
            self.add (fish)
        self.rotating = None
        self.selected = None
        self.cursor = Cursor()
        self.cursor.visible = False
        self.add (self.cursor)

    def add(self, child, z=0, name=None ):
        super(GridLayer, self).add(child, z, name)
        if isinstance(child, CheckPoint):
            label = cocos.text.Label(str(self.ed.world.checkpoints.index(child)),
                font_name='Sans Bold',
                font_size=12,
                anchor_x='center', anchor_y='center')

            label.position = to_tuple(child.left)
            child.add(label, name="label", z=2)
            connector = Sprite('connector.png', scale=child.rad / 100.0)
            connector.position = to_tuple((child.left + child.right) / 2.0)
            connector.rotation = degrees(atan2(child.right.imag - child.left.imag, child.left.real - child.right.real))
            connector.size = (4, child.rad * 2)
            child.add(connector, name="connector")


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
        x, y =  director.get_virtual_coordinates (x, y)
        if not self.rotating is None:
            Dy = self.rotating.position[1] - y
            Dx = x - self.rotating.position[0]
            if not (Dy == 0 and Dx == 0):
                self.rotating.rotation = degrees(atan2 (Dy, Dx))
        else:
            pos = Vector(x - self.x, y - self.y)
            for child in self.get_sprites():
                if hasattr(child, 'pos') and abs(pos - child.pos) < 15:
                    self.cursor.position = child.position
                    self.cursor.visible = True
                    self.selected = child
                    break
            else:
                self.cursor.visible = False
                self.selected = None

    def get_sprites(self):
        """ Returns the real sprites, descending through known composites"""
        result = []
        for child in self.get_children():
            if isinstance(child, CheckPoint):
                result += [child.get("left"), child.get("right")]
            else:
                result.append (child)
        return result

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.clicking = False
        if self.selected is None:
            self.position = (self.position[0] + dx, self.position[1] + dy)
        else:
            self.selected.position = self.selected.position[0] + dx, self.selected.position[1] + dy
            self.cursor.position = self.cursor.position[0] + dx, self.cursor.position[1] + dy
            self.selected.pos = Vector(self.selected.position[0] + dx, self.selected.position[1] + dy)
            if isinstance(self.selected.parent, CheckPoint):
                checkpoint = self.selected.parent
                checkpoint.updateRad()
                label = checkpoint.get("label")
                label.position = to_tuple(checkpoint.left)
                connector = checkpoint.get("connector")
                connector.position = to_tuple((checkpoint.left + checkpoint.right) / 2.0)
                connector.rotation = degrees(atan2(checkpoint.right.imag - checkpoint.left.imag,
                                                   checkpoint.left.real - checkpoint.right.real))
                connector.scale = checkpoint.rad / 100.0


    def on_mouse_press(self, x, y, buttons, modifiers):
        self.clicking = True

    def on_mouse_release(self, x, y, button, modifiers):
        if self.clicking:
            if self.rotating is None and self.selected is None:
                posx, posy = cocos.director.director.get_virtual_coordinates (x, y)
                posx -= self.position[0]
                posy -= self.position[1]
                self.ed.clicked(posx, posy)
            else:
                # Finished rotating
                self.rotating = None

    def setRotating (self, item):
        """ Set a sprite to be rotated when the mouse moves"""
        self.rotating = item

class EditorScene(cocos.scene.Scene):
    def __init__(self):
        super(EditorScene, self).__init__()
        self.editor = Editor(sys.argv[1])
        self.add (GridLayer(self.editor))
        self.add (KeyDisplay(self.editor))
        self.status = cocos.text.Label("Press 'H' for Help", x=300, y=10)
        self.editor.status = self.status
        self.add(self.status)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s <filename>" % sys.argv[0]
        sys.exit(-1)
    cocos.director.director.init()

    main_scene = EditorScene()

    # And now, start the application, starting with main_scene
    cocos.director.director.run (main_scene)

