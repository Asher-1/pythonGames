from __future__ import division

import pyglet
import json
import math

from constants import *

from vector import v, zero, Rectangle

import ability

defaultpos = v((0, 0)) # who knows what this should really be

class MonsterTopologyException(Exception):
    pass

class MonsterPartMeta(type):
    all_index = []
    hearty_index = []
    size_index = {1: [], 2: []}
    def __new__(cls, name, bases, dct):
        res = type.__new__(cls, name, bases, dct)
        if '__metaclass__' not in dct:
            cls.all_index.append(res)
            if dct.get('can_be_root', False):
                cls.hearty_index.append(res)
        if hasattr(res, "imagename"):
            res.image = pyglet.resource.image("pieces/%s.png" % res.imagename)
            res.flippedimage = pyglet.resource.image("pieces/%s.png" % res.imagename, flip_y=True)
            # chard said it was fine to load this multiple times
            alldata = json.load(pyglet.resource.file('pieces/pieces.dat', 'r'))
            scale = 1.0
            if res.force_scale is not None:
                scale *= res.force_scale
            res.anchors = []
            sizes = set()
            res.dim = alldata[res.imagename][-1]
            
            for seg in alldata[res.imagename][:-1]:
                start, end = map(v, seg)
                position = (start + end) / 2
                gap = end - start
                angle = gap.angle + 90
                size = 1 if gap.length * res.dim < 300 else 2
                res.anchors.append((position * scale * res.dim, angle, size))
                sizes.add(size)
            for size in sizes:
                cls.size_index[size].append(res)
        else:
            for s in STATS:
                setattr(res, s, 0)
        return res
    def __repr__(self):
        # THIS IS A TERRIBLE IDEA!
        return self.__name__

class MonsterPart(pyglet.event.EventDispatcher):
    __metaclass__ = MonsterPartMeta
    pos = zero
    rotation = 0
    force_down = None
    force_scale = None
    flipped = False
    draw_layer = 0

    ideal_angle = 0
    angle_range = 180

    loot_chance = DEFAULT_LOOT_CHANCE # rare parts/boss parts should probably always drop

    blood_use = 0

    damage = 0
    max_damage = 1

    friendly = False
    
    name = 'Nameless Monster'

    # points where another part can be attached
    # each one is a tuple of position (relative to this part's own root,
    # assuming this part is in its native orientation) and rotation
    anchors = []
    offset = zero
    default_root_idx = 0
    parent_anchor = None

    def test_alpha(self, x, y):
        image = self.flippedimage if self.flipped else self.image
        image_data = image.get_image_data()
        if image_data._current_format != 'RGBA':
            if DEBUG:
                print 'non-RGBA monster part:', self, image_data._current_format
            return True
        i = y * image_data._current_pitch + x * 4 + 3
        return image_data._current_data[i] != 0


    def __init__(self, parent, parent_anchor=(zero, 0, 00), root_idx=None, flipped=None):

        parent_idx = 0
        if parent is not None:
            for idx, anchor in enumerate(parent.anchors):
                if anchor == parent_anchor:
                    parent_idx = idx
        self._args = (type(self), parent_idx, root_idx, flipped)

        self.parent = parent
        if root_idx is None:
            root_idx = self.default_root_idx
        self.root_idx = root_idx

        self.children = {}
        self.temp_stats = []

        if self.parent is None:
            if not self.can_be_root:
                raise MonsterTopologyException("tried to build monster with no heart")
            self.root_idx = None
            self.pos = defaultpos
            self.rotation = 0
        else:
            if root_idx is None:
                self.root_idx = self.default_root_idx
            else:
                self.root_idx = root_idx

            self.rotation = 180 + self.parent.rotation + parent_anchor[1]
            r_amt = self.anchors[self.root_idx][1]

            if flipped is not None:
                # forced flip
                self.flipped = flipped
            elif self.force_down is None:
                # no auto flip
                self.flipped = False
            else:
                # auto flip
                r1 = (self.rotation - r_amt + self.force_down - 270) % 360 # unflipped option
                r2 = (self.rotation + r_amt + self.force_down - 90) % 360 # flipped option
                self.flipped = min(r1, 360 - r1) > min(r2, 360 - r2)

            if self.flipped:
                self.rotation += r_amt
                self.anchors = [(v((t[0][0], -t[0][1])), -t[1], t[2])
                                for t in self.anchors]
            else:
                self.rotation -= r_amt

        self.update_position(parent_anchor)

    def update_position(self, parent_anchor=(zero, 0, 00)):
        anchor_position, anchor_rotation, anchor_size = parent_anchor
        if self.parent is None:
            pass
        else:
            self.pos = self.parent.pos + anchor_position.rotated(self.parent.rotation)
            self.pos -= self.anchors[self.root_idx][0].rotated(self.rotation)

        for idx, child in self.children.items():
            child.update_position(self.anchors[idx])

    def position(self, new_position):
        self.pos = new_position
        self.update_position()

    def create_sprites(self):
        self.sprite = pyglet.sprite.Sprite(self.flippedimage if self.flipped else self.image)
        self.sprite.scale = self.dim/max(self.image.width, self.image.height)
        self.sprite.x, self.sprite.y = self.pos
        if self.force_scale is not None:
            self.sprite.scale = self.force_scale
        self.sprite.rotation = -self.rotation # pyglet is weird
        for c in self.children.values():
            c.create_sprites()

    def add_part(self, cls, anchor_idx, root_idx=None, flipped=None):
        if anchor_idx == self.root_idx:
            raise MonsterTopologyException("adding to root anchor")
        if anchor_idx in self.children:
            raise MonsterTopologyException("anchor in use")
        if root_idx is None:
            root_idx = cls.default_root_idx
        if self.anchors[anchor_idx][2] != cls.anchors[root_idx][2]:
            raise MonsterTopologyException("anchor sizes do not match")
        p = cls(self, self.anchors[anchor_idx], root_idx, flipped)
        p.parent_anchor = anchor_idx
        self.children[anchor_idx] = p
        return p

    def serialise(self):
        misc = {'name': self.name}
        for k, v in list(misc.items()):
            if v == getattr(type(self), k):
                del misc[k]
        return self._args, [c.serialise() for c in self.children.values()], \
                misc

    @classmethod
    def deserialise(cls, data, parent=None):
        args, children, misc = data
        if parent is None:
            part = args[0](None)
        else:
            part = parent.add_part(*args)
        part.__dict__.update(misc)
        for cdata in children:
            cls.deserialise(cdata, part)
        return part

    def all_parts(self):
        yield self
        for k in sorted(self.children):
            c = self.children[k]
            for p in c.all_parts():
                yield p

    def all_parts_to_draw(self):
        parts = list(self.all_parts())
        parts.sort(key=lambda p: p.draw_layer)
        return parts

    def active_parts(self):
        return filter(lambda p: not p.disabled, self.all_parts())

    def unused_anchors(self):
        for ii in xrange(len(self.anchors)):
            if ii != self.root_idx and ii not in self.children:
                yield ii

    def destroy(self):
        for c in self.children.values():
            c.destroy()
        if self.parent is not None:
            for ii in self.parent.children.keys():
                if self.parent.children[ii] == self:
                    del self.parent.children[ii]
        self.sprite.delete()

    def rotate(self):
        if self.parent and not self.children:
            part_cls = type(self)
            parent = self.parent
            anchor = self.parent_anchor
            root = (self.root_idx + 1) % len(self.anchors)
            while self.anchors[root][2] != parent.anchors[anchor][2]:
                root = (root + 1) % len(self.anchors)
            flipped = self.flipped
            self.destroy()
            return parent.add_part(part_cls, anchor, root, flipped)
        return self

    def flip(self):
        if self.parent and not self.children:
            part_cls = type(self)
            parent = self.parent
            anchor = self.parent_anchor
            root = self.root_idx
            flipped = not self.flipped
            self.destroy()
            return parent.add_part(part_cls, anchor, root, flipped)
        return self

    @property
    def can_be_root(self):
        return hasattr(self, "heart_strength")

    @property
    def ancestor(self):
        if self.parent is None:
            return self
        return self.parent.ancestor

    # combat

    @property
    def disabled(self):
        if self.misaligned: return self.damage > 0
        return self.damage >= self.max_damage * self.ancestor.get_blood_pressure() / 100

    def disable(self):
        self.damage = self.max_damage
        for c in self.children.values():
            c.disable()

    def apply_damage(self, amt):
        if self.disabled: return
        self.damage += amt
        if self.disabled:
            if self.parent is None:
                self.temp_stats = []
                self.dispatch_event('on_defeated', self)
            else:
                self.ancestor.dispatch_event('on_part_disabled', self)
            self.disable()

    def spread_damage(self, amt):
        if self.disabled: return
        self.ancestor.dispatch_event('on_receive_damage', self, amt)
        targets = self.active_parts()
        amt = int(math.ceil(amt / len(targets)))
        for t in targets:
            t.apply_damage(amt)

    def refresh(self):
        self.damage = 0
        for c in self.children.values():
            c.refresh()

    def get_total_damage(self):
        return sum(map(lambda p: p.damage, self.all_parts()))

    def get_total_max_damage(self):
        return sum(map(lambda p: p.max_damage, self.all_parts()))

    def use_ability(self, ability, target):
        self.dispatch_event('on_use_ability', self, ability, target)
        if not ability.activate(self, target):
            self.dispatch_event('on_miss', self, ability, target)

    def receive_temp_stat(self, stat, delta, duration):
        self.temp_stats.append((stat, delta, duration))
        self.dispatch_event('on_temp_stat', self, stat, delta, duration)
        
    # stats stuff

    @property
    def description(self):
        res = '%s\n\n' % self.name.upper()
        s = self.stats
        for r in RATINGS:
            res += '%s: %i\n' % (r.upper(), s[r])
        res += '\nBlood pressure: %i%%\n\nAbilities:' % int(self.get_blood_pressure())
        for a in self.abilities():
            res += '\n' + a.name
        return res

    @property
    def stats(self):
        res = {}
        for s in STATS:
            tot = 0
            for p in self.all_parts():
                if not p.disabled and not p.misaligned:
                    tot += getattr(p, s)
            res[s] = tot
        # penalise speed, power etc. if heart overloaded, but do not penalise
        # e.g. number of legs
        bp = self.get_blood_pressure()
        for r in RATINGS:
            res[r] = max(int(res[r] * bp / 100), 1)
        for s, delta, _ in self.temp_stats:
            res[s] += delta
        return res

    @property
    def misaligned(self):
        theta = self.sprite.rotation
        if self.flipped: theta = 180 - theta
        mis = abs(((theta - self.ideal_angle + 180) % 360) - 180)
        return mis > self.angle_range
    
    def get_blood_pressure(self):
        # returns 100 most of the time, or a smaller number if heart is overloaded
        prop = self.get_blood_use() / self.heart_strength
        return 100 * min(1, (prop ** -4))
            
    def get_blood_use(self):
        tot = self.blood_use + 1 # avoid zero division
        for c in self.children.values():
            tot += c.get_blood_use()
        return tot

    def abilities(self):
        s = self.stats
        # I challenge a non-python programmer to figure this out
        res = filter(lambda a: a.condition(s), ability.AbilityMeta.classes)
        if len(res) == 0:
            return [ability.struggle]
        kinds = dict([(a.kind, max(b.level for b in res if b.kind == a.kind)) for a in res])
        abils = []
        for kind, level in kinds.items():
            if kind is None:
                abils.extend([a for a in res if a.kind is None])
            else:
                abils.extend([a for a in res if a.kind == kind and a.level == level])
        return sorted(abils, key = lambda a: a.damage[0] * a.damage[1], reverse=True)

    def begin_turn(self):
        ts = self.temp_stats
        self.temp_stats = []
        for s, delta, t in ts:
            if t == 0: continue
            self.temp_stats.append((s, delta, t-1))

    def begin_fight(self):
        self.temp_stats = []
        if DEBUG:
            print self.name, self.get_blood_pressure(), self.stats
    
    def end_fight(self):
        self.temp_stats = []
        for p in self.all_parts():
            p.sprite.color = (255, 255, 255)
        
    @property
    def bounding_box(self):
        # this currently gets the bounding box for this part and all children
        # this is what we want some of the time, but some camera shots might want to zoom on actual torso pieces?
        sprites = [(p.sprite, p.flipped) for p in self.all_parts()]
        pts = []
        for s, flipped in sprites:
            base = v(s.x, s.y)
            h = s.height * (-1 if flipped else 1)
            w = s.width
            pts.append(base)
            pts.append(base + v(w, 0).rotated(-s.rotation))
            pts.append(base + v(w, h).rotated(-s.rotation))
            pts.append(base + v(0, h).rotated(-s.rotation))
        return Rectangle.as_bounding(pts)

MonsterPart.register_event_type('on_part_disabled')
MonsterPart.register_event_type('on_use_ability')
MonsterPart.register_event_type('on_miss')
MonsterPart.register_event_type('on_receive_damage')
MonsterPart.register_event_type('on_temp_stat')
MonsterPart.register_event_type('on_defeated')
