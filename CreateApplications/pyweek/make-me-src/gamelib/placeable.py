#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import pyglet
from pyglet.gl import *

import anim
import collide
import globals
import player

_debug = False

class Placed(object):
    sprite = None
    bbox = None
    _visible = True

    def __init__(self, placeable, x, y):
        self.placeable = placeable
        self.x = x
        self.y = y

    def load(self, batch):
        if self.sprite:
            return

        #print 'load', self
        self.sprite = pyglet.sprite.Sprite(self.placeable.get_image(),
            self.x, self.y, batch=batch)
        self.sprite.visible = self._visible

    def unload(self):
        if self.sprite:
            #print 'unload', self, self.sprite._group
            self.sprite.delete()
            self.sprite = None

    def set_visible(self, visible):
        self._visible = visible
        if self.sprite:
            self.sprite.visible = visible

    visible = property(lambda self: self._visible, set_visible)

    def __repr__(self):
        return 'Placed(%r at %d, %d)' % (self.placeable, self.x, self.y)

class Placeable(object):
    image_name = 'tmpplaceable.png'
    name = 'tmpplaceable.png'

    KILL_ON_HIT = False
    DESTROY_ON_HIT = True
    INFLUENCE = False

    placed_class = Placed

    def get_image(self):
        return pyglet.resource.image(self.image_name)

    def hit(self, placed, cell):
        if self.DESTROY_ON_HIT:
            cell.remove_placed(placed)

        if self.INFLUENCE:
            globals.game.player.influenced.add(placed)

        if self.KILL_ON_HIT:
            globals.game.stab_player()

    def enter(self, placed):
        if _debug:
            print 'enter', placed

    def leave(self, placed):
        if _debug:
            print 'leave', placed

    def place(self, x, y):
        return self.placed_class(self, x, y)

class ImagePlaceable(Placeable):
    def __init__(self, image_name, width, height, name=None):
        if name is None:
            name = image_name
        self.name = name
        self.image_name = image_name
        if width is None or height is None:
            image = self.get_image()
            self.width = image.width
            self.height = image.height
            if _debug:
                print 'Warning: examined size of', name
        else:
            self.width = width
            self.height = height

    def get_image(self):
        return pyglet.resource.image(self.image_name)

    def __repr__(self):
        return self.name

placeables = {}

def get_placeable(name, width=None, height=None):
    try:
        return placeables[name]
    except KeyError:
        return ImagePlaceable(name, width, height)

class AnimPlaced(Placed):
    anim_sprite = None
    loaded = False
    anim_name = ''

    facing_int = -1
    move = False
    grounded = True

    r = 0
    visible = True

    def load(self, batch):
        if self.loaded:
            return
        self.loaded = True
        self.update_anim()
        return True

    def unload(self):
        self.anim_sprite = None
        self.loaded = False

    def update_anim(self):
        if not self.loaded:
            return
        if self.facing_int < 0:
            facing = 'left'
        else:
            facing = 'right'
        anim_set = self.placeable.get_anim_set()
        self.anim_sprite = anim.AnimSprite(anim_set.get(
            self.anim_name, facing, self.move, self.grounded))

    def draw(self):
        if not self.anim_sprite or not self.visible:
            return
        glPushMatrix()
        glTranslatef(self.x, self.y - 8, 0)
        if self.r:
            glRotatef(self.r, 0, 0, 1)
        self.anim_sprite.draw()
        glPopMatrix()

    def update_bbox(self):
        if self.anim_sprite:
            self.bbox = self.anim_sprite.anim.bbox.get_translated(
                self.x, self.y)

class AnimPlaceable(Placeable):
    # TODO weakref
    anim_set = None
    anim_name = ''

    placed_class = AnimPlaced

    def __init__(self, image_filename, anim_filename, width, height):
        self.name = self.image_name = image_filename
        self.filename = anim_filename
        self.width = width
        self.height = height

    def place(self, x, y):
        placed = self.placed_class(self, x, y)
        placed.anim_name = self.anim_name
        return placed

    def get_anim_set(self):
        if not self.anim_set:
            self.anim_set = anim.AnimSet(self.filename)
        return self.anim_set

class Layer(object):
    highlight_image = None
    highlight_image_x = 0
    highlight_image_y = 0

    def __init__(self, name, interactive, paralax):
        self.name = name
        self.interactive = interactive
        self.visible_placed = set()
        self.paralax = paralax
        self.placed = []
        self.manual_draw = []
        self.batch = pyglet.graphics.Batch()

    def clear(self):
        for placed in self.placed:
            placed.unload()
        for placed in self.manual_draw:
            placed.unload()
        self.placed = []
        self.manual_draw = []

    def add_placeable_at(self, placeable, x, y):
        placed = placeable.place(x, y)
        placed.bbox = collide.BBox(
            x, y, x + placeable.width, y + placeable.height)
        self.placed.append(placed)

    def remove_placeable_at(self, placeable, x, y):
        for placed in list(self.placed):
            if placed.bbox and placed.bbox.has_point(x, y):
                self.remove_placed(placed)

    def get_placed_at(self, x, y):
        for placed in list(self.placed):
            if placed.bbox and placed.bbox.has_point(x, y):
                return placed 

    def add_placed(self, placed):
        self.placed.append(placed)
        placed.bbox = collide.BBox(
            placed.x, placed.y, 
            placed.x + placed.placeable.width, 
            placed.y + placed.placeable.height)

    def remove_placed(self, placed):
        placed.unload()
        if placed in self.manual_draw:
            self.manual_draw.remove(placed)
        try:
            self.placed.remove(placed)
        except ValueError:
            # Not supposed to happen... but, meh.
            pass

    @classmethod
    def load(cls, name, interactive=False, paralax=1):
        layer = cls(name, interactive, paralax)
        for line in pyglet.resource.file(name, 'rt'):
            line = line.strip()
            if not line:
                continue
            x, y, width, height, value = line.split(' ', 4)
            x = int(x)
            y = int(y)
            width = int(width)
            height = int(height)
            placeable = get_placeable(value, width, height)
            layer.add_placeable_at(placeable, x, y)

        return layer

    def save(self):
        file = pyglet.resource.file(self.name, 'w')
        for placed in self.placed:
            try:
                image = placed.placeable.get_image()
                width = image.width
                height = image.height
            except pyglet.resource.ResourceNotFoundException:
                width = height = 64
            print >> file, '%d %d %d %d %s' % (
                placed.x, placed.y, width, height, placed.placeable.name)

    def get_intersecting_placed(self, bbox):
        for placed in self.placed:
            if placed.bbox.intersects(bbox):
                yield placed

    def update_visibility_bbox(self, bbox):
        if self.paralax != 1:
            hw = (bbox.x2 - bbox.x1) / 2
            hh = (bbox.y2 - bbox.y1) / 2
            cx = (bbox.x1 + bbox.x2) / 2 * self.paralax
            cy = (bbox.y1 + bbox.y2) / 2 * self.paralax
            bbox = collide.BBox(cx - hw, cy - hh, cx + hw, cy + hh)
            # HACK
            visible_placed = set(self.placed)
        else:
            visible_placed = set(self.get_intersecting_placed(bbox))

        for placed in self.visible_placed- visible_placed:
            if _debug:
                print 'unload', placed
            placed.unload()
            if placed in self.manual_draw:
                self.manual_draw.remove(placed)
        for placed in visible_placed - self.visible_placed:
            if _debug:
                print 'load', placed
            manual_draw = placed.load(self.batch)
            if manual_draw:
                self.manual_draw.append(placed)
        self.visible_placed = visible_placed

    def draw(self):
        if self.paralax != 1:
            glPushMatrix()
            glLoadIdentity()
            camera = globals.game.camera
            glTranslatef(-int((camera.x)*self.paralax) + 400, 
                         -int((camera.y)*self.paralax), 0)

        self.batch.draw()
        for manual_draw in self.manual_draw:
            manual_draw.draw()

        if self.highlight_image:
            glPushAttrib(GL_CURRENT_BIT | GL_COLOR_BUFFER_BIT)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(1, 1, 1, .5)
            self.highlight_image.blit(self.highlight_image_x,
                                      self.highlight_image_y)
            glPopAttrib()

        if self.paralax != 1:
            glPopMatrix()
    
    def highlight_image_at(self, image, x, y):
        self.highlight_image = image
        self.highlight_image_x = x
        self.highlight_image_y = y

    def clear_highlight(self):
        self.highlight_image = None

    def save_state(self, d):
        if not self.interactive:
            return

        v = []
        for placed in self.placed:
            v.append((placed.x, placed.y, placed.placeable.name))
        
        assert self.name not in d
        d[self.name] = v

    def restore_state(self, d):
        if not self.interactive:
            return
    
        for placed in self.placed:
            placed.unload()
        self.placed = []
        self.manual_draw = []

        v = d[self.name]
        for x, y, name in v:
            placeable = get_placeable(name)
            self.add_placeable_at(placeable, x, y)

        self.visible_placed = set()
