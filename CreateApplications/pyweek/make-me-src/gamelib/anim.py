#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import pyglet
from pyglet.gl import *

import collide

def load_anims(file):
    anims = []
    anchors = {}
    for line in file:
        line = line.strip()
        if not line:
            continue
        key, value = line.split(' ', 1)
        if key == 'anim':
            anim = Anim(value)
            anims.append(anim)
        elif key == 'anim_bbox':
            x1, y1, x2, y2 = value.split(' ')
            anim.bbox.x1 = int(x1)
            anim.bbox.y1 = int(y1)
            anim.bbox.x2 = int(x2)
            anim.bbox.y2 = int(y2)
        elif key == 'duration':
            anim.duration = float(value)
        elif key == 'image':
            anim.images.append(value)
        elif key == 'frame':
            frame = anim.insert_frame(float(value) * anim.duration)
        elif key == 'mx':
            frame.mx = int(value)
        elif key == 'my':
            frame.my = int(value)
        elif key == 'tx':
            frame.tx = int(value)
        elif key == 'ty':
            frame.ty = int(value)
        elif key == 'tr':
            frame.tr = float(value)
        elif key == 'image_tx':
            frame.image_tx = [int(t) for t in value.split()]
        elif key == 'image_ty':
            frame.image_ty = [int(t) for t in value.split()]
        elif key == 'image_vis':
            frame.image_vis = [t in ('True', '1') for t in value.split()]
        elif key == 'anchor':
            x, y, name = value.split()
            anchors[name] = (int(x), int(y))

    return anims, anchors

class AnimSet(object):
    def __init__(self, filename):
        anims, anchors = load_anims(pyglet.resource.file(filename, 'rt'))
        self.images = {}
        for name, anchor in anchors.items():
            image = pyglet.resource.image(name)
            image.anchor_x, image.anchor_y = anchor
            self.images[name] = image

        self.anims = {}
        for anim in anims:
            self.anims[anim.name] = anim        
            anim.set_images(self.images)

        for name, anim in self.anims.items():
            if not name.endswith('Right') and not name + 'Right' in self.anims:
                # Make a right facing one
                self.anims[anim.name + 'Right'] = anim.create_flip()

    def get(self, name, facing, move, grounded):
        if not grounded:
            if name + 'Air' in self.anims:
                name += 'Air'
            else:
                name += 'Idle'
        elif move:
            if name + 'Move' in self.anims:
                name += 'Move'
            else:
                name += 'Idle'
        else:
            name += 'Idle'
        if facing == 'right':
            if name + 'Right' in self.anims:
                name += 'Right'
        return self.anims[name]
    
class Anim(object):
    def __init__(self, name):
        self.name = name
        self.frames = [AnimFrame()]
        self.images = []
        self.duration = 1.0
        self.bbox = collide.BBox(0, 0, 0, 0)

    def set_images(self, images):
        self.images = [images[name] for name in self.images]

    def get_interp_frames(self, time):
        for i, frame in enumerate(self.frames):
            if frame.time == time:
                return frame, frame, 0.
            if frame.time > time:
                break
        else:
            i += 1
        frame = AnimFrame()
        frame.time = time
        a = self.frames[i - 1]
        if i == len(self.frames):
            b = self.frames[0]
            to = self.duration
        else:
            b = self.frames[i]
            to = b.time
        f = (time - a.time) / (to - a.time)
        return a, b, f

    def create_flip(self):
        flipped = Anim(self.name + 'Right')
        flipped.frames = [frame.create_flip() for frame in self.frames]
        flipped.images = [image.get_transform(flip_x=True) \
                          for image in self.images]
        flipped.duration = self.duration
        flipped.bbox = self.bbox.get_flipped()
        return flipped

    # Editor ONLY (not efficient) below

    def get_image_index(self, name):
        return self.images.index(name)

    def validate_frames(self):
        def pad(l, value):
            d = len(self.images) - len(l)
            if d > 0:
                l.extend([value] * d)
        for frame in self.frames:
            pad(frame.image_tx, 0)
            pad(frame.image_ty, 0)
            pad(frame.image_vis, True)

    def get_frame(self, time):
        for i, frame in enumerate(self.frames):
            if frame.time == time:
                return frame
            if frame.time > time:
                break
        else:
            i += 1
        frame = AnimFrame()
        frame.time = time
        if i == len(self.frames):
            frame.interp_from(self.frames[i - 1], self.frames[0], 
                              to=self.duration)
        else:
            frame.interp_from(self.frames[i - 1], self.frames[i]) 
        return frame

    def insert_frame(self, time):
        for i, frame in enumerate(self.frames):
            if frame.time == time:
                return frame
            if frame.time > time:
                break
        else:
            i += 1
        frame = AnimFrame()
        frame.time = time
        self.frames.insert(i, frame)
        if i == len(self.frames) - 1:
            frame.interp_from(self.frames[i - 1], self.frames[0],
                              to=self.duration)
        else:
            frame.interp_from(self.frames[i - 1], self.frames[i + 1])
        return frame

    def delete_frame(self, time):
        for frame in self.frames:
            if frame.time == time:
                self.frames.remove(frame)
                return

class AnimFrame(object):
    def __init__(self):
        self.time = 0.
        self.tx = 0
        self.ty = 0
        self.tr = 0
        self.mx = 0
        self.my = 0
        self.image_tx = []
        self.image_ty = []
        self.image_vis = []

    def create_flip(self):
        flipped = AnimFrame()
        flipped.time = self.time
        flipped.tx = -self.tx
        flipped.ty = self.ty
        flipped.tr = -self.tr
        flipped.mx = -self.mx
        flipped.my = self.my
        flipped.image_tx = [-t for t in self.image_tx]
        flipped.image_tx = self.image_tx
        flipped.image_ty = self.image_ty
        flipped.image_vis = self.image_vis
        return flipped

    # EDITOR ONLY below

    def interp_from(self, a, b, to=None):
        assert a.time != b.time or a is b
        if to is None:
            to = b.time
        if a is b:
            f = 1.
        else:
            f = (self.time - a.time) / (to - a.time)
        self.tx = a.tx * (1 - f) + b.tx * f
        self.ty = a.ty * (1 - f) + b.ty * f
        self.tr = a.tr * (1 - f) + b.tr * f
        if a.time < b.time:
            self.mx = a.mx * (1 - f) + b.mx * f
            self.my = a.my * (1 - f) + b.my * f
        else:
            self.mx = a.mx
            self.my = a.my
        self.image_tx = [i * (1 - f) + j * f \
                         for (i, j) in zip(a.image_tx, b.image_tx)]
        self.image_ty = [i * (1 - f) + j * f \
                         for (i, j) in zip(a.image_ty, b.image_ty)]
        self.image_vis = a.image_vis[:]
        
_use_sprites = True

class AnimSprite(object):
    last_mx = 0
    last_my = 0

    def __init__(self, anim, batch=None):
        self.anim = anim
        self.time = 0.

        # TODO create vertices for sprites so order is maintained 

        if _use_sprites:
            self.sprites = [pyglet.sprite.Sprite(image) \
                            for image in anim.images]
        else:
            if batch is None:
                batch = pyglet.graphics.Batch()
            self.batch = batch
            tex_coords = []
            for image in anim.images:
                tex_coords.extend(image.tex_coords)
            self.vertex_list = batch.add(4 * len(anim.images), GL_QUADS, None,
                    'v2i',
                    ('t3f', tex_coords))

    def update(self, dt, loco=False):
        self.time += dt
        if self.time > self.anim.duration:
            self.time = self.time % self.anim.duration
            self.last_mx = 0
            self.last_my = 0

        a, b, f = self.anim.get_interp_frames(self.time)
        f1 = 1 - f
        if _use_sprites:
            for i, sprite in enumerate(self.sprites):
                sprite.x = int(a.image_tx[i] * f1 + b.image_tx[i] * f)
                sprite.y = int(a.image_ty[i] * f1 + b.image_ty[i] * f)
                sprite.visible = a.image_vis[i]
        else:
            for i, image in enumerate(self.anim.images):
                x = int(a.image_tx[i] * f1 + b.image_tx[i] * f) - image.anchor_x
                y = int(a.image_ty[i] * f1 + b.image_ty[i] * f) - image.anchor_y
                w = image.width
                h = image.height
                if a.image_vis[i]:
                    self.vertex_list.vertices[i*8:i*8+8] = [
                        x, y, x + w, y, x + w, y + h, x, y + h]
                else:
                    self.vertex_list.vertices[i*8:i*8+8] = [
                        0, 0, 0, 0, 0, 0, 0, 0]

        if loco:
            tx = int(a.tx * f1 + b.tx * f)
            ty = int(a.ty * f1 + b.ty * f)
            tr = a.tr * f1 + b.tr * f
            if b.time > a.time:
                mx = int(a.mx * f1 + b.mx * f)
                my = int(a.my * f1 + b.my * f)
            else:
                mx = a.mx
                my = a.my
            dx = mx - self.last_mx
            dy = my - self.last_my
            self.last_mx = mx
            self.last_my = my
            return tx, ty, tr, dx, dy

    def draw(self):
        if _use_sprites:
            for sprite in self.sprites:
                sprite.draw()
        else:
            self.vertex_list.draw(GL_QUADS)


    def delete(self):
        if _use_sprites:
            for sprite in self.sprites:
                sprite.delete() 
        else:
            self.vertex_list.delete()
