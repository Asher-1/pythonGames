from __future__ import division

import collections
import random
from math import *

import pyglet
from pyglet.window import key
from pyglet.gl import *

from gamelib import app
from gamelib import worldgen
from gamelib import sound
from gamelib.vector import *

from gamelib.constants import *

class SpatialHash(object):

    def __init__(self, cell_size=50):
        self.cell_size = cell_size
        self.objects = collections.defaultdict(list)

    def intersects(self, obj, margin=0):
        if isinstance(obj, LineSegment):
            assert margin == 0
            return self.line_segment_intersects(obj)
        if isinstance(obj, PlatformObject):
            return self.platform_object_intersects(obj, margin=margin)
        return []

    def add(self, obj):
        for cell in self.intersects(obj):
            self.objects[cell].append(obj)

    def remove(self, obj):
        for cell in self.intersects(obj):
            self.objects[cell].remove(obj)
            if len(self.objects[cell]) == 0:
                del self.objects[cell]

    def line_segment_intersects(self, ls):
        x1, y1 = ls.start
        x2, y2 = ls.end
        lx, hx = sorted((x1, x2))
        ly, hy = sorted((y1, y2))
        cs = self.cell_size
        for x in xrange(int(floor(lx / cs)), int(floor(hx / cs)) + 1):
            for y in xrange(int(floor(ly / cs)), int(floor(hy / cs)) + 1):
                yield x, y

    def platform_object_intersects(self, po, margin=0):
        x, y = po.pos
        r = po.radius + margin
        lx = x - r
        hx = x + r
        ly = y - r
        hy = y + r
        cs = self.cell_size
        for x in xrange(int(floor(lx / cs)), int(floor(hx / cs)) + 1):
            for y in xrange(int(floor(ly / cs)), int(floor(hy / cs)) + 1):
                yield x, y

    def colliders(self, obj, margin=0):
        for cell in self.intersects(obj, margin=margin):
            if cell in self.objects:
                for other in self.objects[cell]:
                    yield other



class PlatformSegment(LineSegment):
    def __new__(cls, start, end):
        self = LineSegment.from_points(start, end)
        if self.line.direction.angle > -150 and self.line.direction.angle < -30:
            self.is_floor = True
        else:
            self.is_floor = False
        return self

class PlatformObject(object):
    texture = pyglet.resource.texture('red.png')
    left_wall = None # only used by player
    radius = 15
    scale = 1.0
    gravity = v((0, -1.5))
    drag = 0.9
    flipped = False
    solid = True
    hashed = True
    destroyed = False
    protected = False
    def __init__(self, world, pos, *args, **kwargs):
        self.world = world
        self.pos = pos
        self.old_pos = pos
        self.heading = 0.0
        self.grounded = False
        self.vlist = None
        self.delta = zero
        self.collided = []
        self.world.objecthash.add(self)
    def stop(self):
        self.delta = zero
    def resize(self, r):
        if self.hashed: self.world.objecthash.remove(self)
        self.radius = r
        if self.hashed: self.world.objecthash.add(self)
    def reposition(self, pos, stop=True):
        if self.hashed: self.world.objecthash.remove(self)
        self.pos = pos
        self.old_pos = pos
        if stop: self.delta = zero
        if self.hashed: self.world.objecthash.add(self)
    def impulse(self, vec):
        self.delta += vec
    def get_vel(self):
        return self.pos - self.old_pos
    def tick(self):
        self.collided = []
        # continue old motion
        self.old_pos = self.pos
        self.delta += self.gravity
        # apply accumulated impulses, respecting constraints
        self.grounded = False
        if self.hashed: self.world.objecthash.remove(self)
        while self.delta.length > 0:
            if self.delta.length > self.radius:
                d = self.delta.normalised() * self.radius
                self.pos += d
                self.delta -= d
            else:
                self.pos += self.delta
                self.delta = zero
            # apply constraints  
            if self.solid:  
                for l in self.world.spatialhash.colliders(self):
                    if isinstance(l, LineSegment):
                        d = l.distance_to(self.pos)
                        if d < self.radius:
                            self.collided.append(l)
                            if l.is_floor:
                                self.pos -= v((0, (self.radius - d) / sin(radians(l.line.direction.angle))))
                                self.grounded = True
                                self.heading = l.line.along.project(v(1, 0).rotated(self.heading)).angle
                                self.heading %= 360
                                if 90 < self.heading < 180:
                                    self.heading += 180
                                if 180 < self.heading < 270:
                                    self.heading -= 180
                            else:
                                self.pos -= l.line.direction * (self.radius - d)
                if self.left_wall is not None and self.pos.x < self.left_wall:
                    self.pos = v(self.left_wall, self.pos.y)
        if self.hashed: self.world.objecthash.add(self)
        self.delta = (self.pos - self.old_pos) * self.drag
        self.flipped = (self.pos - self.old_pos).x < 0.0

    def create_vlist(self, batch):
        if self.texture is not None:
            tc = self.texture.tex_coords
            vdata = [0] * 8
            cdata = [255, 255, 255, 255] * 4
            tdata = [tc[0], tc[1], tc[3], tc[4], tc[6], tc[7], tc[9], tc[10]]
            self.vlist = batch.add(4, GL_QUADS, pyglet.graphics.TextureGroup(self.texture), ('v2f', vdata), ('t2f', tdata), ('c4B', cdata))

    def update_vlist(self, batch):
        if self.texture is not None:
            if self.vlist is None:
                self.create_vlist(batch)
            from math import sin, cos, radians
            x, y = self.pos
            h = radians(self.heading)
            r = self.radius * self.scale
            rc = r * cos(h)
            rs = r * sin(h)
            if not self.flipped:
                self.vlist.vertices[:] = [
                        x-rc+rs, y-rs-rc,
                        x+rc+rs, y+rs-rc,
                        x+rc-rs, y+rs+rc,
                        x-rc-rs, y-rs+rc,
                ]
            else:
                self.vlist.vertices[:] = [
                        x+rc+rs, y+rs-rc,
                        x-rc+rs, y-rs-rc,
                        x-rc-rs, y-rs+rc,
                        x+rc-rs, y+rs+rc,
                ]

    def destroy(self):
        if not self.destroyed:
            self.destroyed = True
            if self.vlist is not None:
                self.vlist.delete()
            self.world.remove_object(self)



class Player(PlatformObject):
    texture = pyglet.resource.texture('wizard.png')
    radius = 40
    jump_timer = 0
    stun_timer = 0
    unstun_timer = 0
    jumping = False
    jumps_used = 0
    left_wall = 0
    protected = True
    def tick(self):
        self.unstun_timer -= 1
        if self.stun_timer > 0:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.unstun_timer = UNSTUN_TIME
        if self.grounded:
            self.jump_timer = 0
            self.jumps_used = 0
        if app.keys is not None and self.stun_timer <= 0:
            if (app.keys[key.UP] or app.keys[key.W]):
                if not self.jumping and self.jumps_used < app.state.max_jumps: # number of jumps
                    self.jump_timer = 0
                if self.jump_timer < JUMP_INITIAL_TIME:
                    if not self.jumping:
                        self.jumping = True
                        self.jumps_used += 1
                    self.jump_timer += 1
                    self.impulse(v((0, JUMP_BOOST)))
            else:
                self.jump_timer = JUMP_INITIAL_TIME # prevent mini double jump
                self.jumping = False
            if app.keys[key.LEFT] or app.keys[key.A]:
                self.impulse(v((-app.state.run_speed, 0)))
            if app.keys[key.RIGHT] or app.keys[key.D]:
                self.impulse(v((app.state.run_speed, 0)))
        super(Player, self).tick()
    def stun(self, ticks):
        if self.stun_timer <= 0 and self.unstun_timer <= 0:
            self.stun_timer = ticks
        self.world.dispatch_event('on_player_stun')
    @property
    def stunned(self):
        return self.stun_timer > 0


class Enemy(PlatformObject):
    hp = 2
    vincible = True
    def tick(self):
        if (self.pos - self.world.player.pos).length < self.radius + self.world.player.radius:
            self.hit_player()
        super(Enemy, self).tick()
    def hit_player(self):
        self.world.player.stop()
        self.world.player.impulse(v(app.state.knockback, 0).rotated(150))
        self.world.player.stun(app.state.stun_time)
    def damage(self, n):
        if self.vincible:
            sound.hit()
            self.hp -= n
            if self.hp <= 0:
                from gamelib import ability
                self.world.add_object(ability.SafeExplosion, self.pos, size=self.radius*self.scale*1.5)
                sound.miniexplosion()
                self.destroy()

class Demon(Enemy):
    texture = pyglet.resource.texture("demon.png")
    radius = 100
    gravity = zero
    solid = False
    protected = True
    timer = 0
    fired = False
    hp = 100
    def __init__(self, *args, **kwds):
        super(Demon, self).__init__(*args, **kwds)
        if DEBUG:
            self.hp = 1
    @property
    def vincible(self):
        from gamelib.data.upgrades import victory
        if victory not in app.state.unlocked_upgrades: return False
        if self.world.get_distance() < 3000: return False
        if self.pos.x < self.world.player.left_wall: return False
        if self.world.player.destroyed: return False
        if self.destroyed: return False
        return True
    def destroy(self):
        self.world.add_object(DemonDying, self.pos)
        super(Demon, self).destroy()
    def tick(self):
        if self.world.distance_correction is None:
            return
        if self.world.get_distance() < 0:
            p = v(self.world.player.pos.x - DEMON_STARTING_POS, DEMON_HEIGHT)
            self.reposition(p)
            return
        d = (self.world.player.left_wall - self.pos.x) / self.world.player.radius
        s = max(0.3, min((d / 50) - 1, 1.5))
        s *= 1 + (self.world.get_distance() / 4000)
        self.impulse(v(s, 0))
        super(Demon, self).tick()
        self.timer += 1
        if self.pos.x > self.world.player.left_wall: # only fire stars when on screen
            if self.timer % 80 == 0:
                for a in xrange(210, 360, 60):
                    s = self.world.add_object(DemonStar, self.pos)
                    s.impulse(v(5, 0).rotated(a))
                    s.impulse(self.delta)
            elif self.timer % 80 == 40:
                for a in xrange(180, 361, 60):
                    s = self.world.add_object(DemonStar, self.pos)
                    s.impulse(v(5, 0).rotated(a))
                    s.impulse(self.delta)
        if self.pos.x > self.world.player.pos.x and not self.fired:
            self.fired = True
            self.world.add_object(DemonDeathRay, self.pos)

class DemonStar(PlatformObject):
    texture = pyglet.resource.texture("ninjastar.png")
    radius = 15
    gravity = zero
    solid = False
    hashed = False
    drag = 1.0
    def tick(self):
        if (self.pos - self.world.player.pos).length < self.radius + self.world.player.radius:
            self.world.player.stop()
            self.world.player.impulse(v(app.state.knockback / 2, 0).rotated(150))
            self.world.player.stun(app.state.stun_time / 2)
        super(DemonStar, self).tick()

class DemonDeathRay(PlatformObject):
    texture = pyglet.resource.texture("skull.png")
    radius = 30
    scale = 2.0
    gravity = zero
    solid = False
    hashed = False
    def tick(self):
        d = self.world.player.pos - self.pos
        if d.length < 20:
            # DEAAAAAATTTHHHHHHHHH
            self.destroy()
            self.world.player.destroy()
            self.world.dispatch_event('on_player_dead')
        else:
            self.reposition(self.pos + d.safe_scaled_to(20))
        # no super, who needs it?

class DemonDying(PlatformObject):
    texture = None
    radius = 200
    steps = 10
    rate = 9
    def __init__(self, *args, **kwds):
        super(DemonDying, self).__init__(*args, **kwds)
        t = random.randint(self.rate, self.rate * 2)
        self.explosion_centers = [(self.pos, self.radius, t)]
        d = int(self.radius/self.steps)
        for i, r in enumerate(xrange(0, self.radius+1, d)):
            for _ in xrange(i):
                if random.random() < 0.2:
                    a = random.randrange(360)
                    p = self.pos + v(r, 0).rotated(a)
                    t = random.randint(self.rate, self.rate * 2)
                    self.explosion_centers.append((p, self.radius - i * d / 2, t))
        self.ticks = 1
    def tick(self):
        self.ticks -= 1
        if self.ticks == 0:
            pos, size, ticks = self.explosion_centers.pop(0)
            from gamelib.ability import Explosion
            self.world.add_object(Explosion, pos, size=size)
            from gamelib import sound
            sound.explosion()
            self.ticks = ticks
            if not self.explosion_centers:
                self.world.win()
                self.destroy()

class WalkingEnemy(Enemy):
    hp = 1
    scale = 1.2
    texture = pyglet.resource.texture("snail3.png")
    radius = 20
    def __init__(self, *args, **kwargs):
        super(WalkingEnemy, self).__init__(*args, **kwargs)
        if random.random() < 0.5:
            self.walk = v((0.3, 0))
        else:
            self.walk = v((-0.3, 0))
        self.last_change = 0
    def tick(self):
        self.last_change += 1
        if self.last_change > 30 and random.random() < 0.01:
            self.walk *= -1
        self.impulse(self.walk)
        super(WalkingEnemy, self).tick()

class WalkingEnemy2(WalkingEnemy):
    hp = 3
    scale = 1.2
    texture = pyglet.resource.texture("snail.png")

class WalkingEnemy3(WalkingEnemy):
    hp = 6
    scale = 1.2
    texture = pyglet.resource.texture("snail2.png")    

class FlyingEnemy(Enemy):
    texture = pyglet.resource.texture("wasp.png")
    scale = 3.0
    gravity = zero
    aggressive = False
    speed = 0.5
    aggro_speed = 3.0
    def __init__(self, *args, **kwargs):
        super(FlyingEnemy, self).__init__(*args, **kwargs)
        self.ang = random.randrange(360)
    def tick(self):
        spd = self.speed
        d = self.world.player.pos - self.pos
        if self.aggressive and d.length2 < 100000 and not self.world.player.stunned:
            self.ang = d.angle
            spd = self.aggro_speed
        else:
            self.ang += random.randrange(-10, 11)
        if self.pos.y > 900:
            self.ang %= 360
            if self.ang < 90 or self.ang > 270:
                self.ang -= 15
            else:
                self.ang += 15
        if self.grounded:
            self.ang = 90
        self.impulse(v(spd, 0).rotated(self.ang))
        super(FlyingEnemy, self).tick()
        self.heading = 0.0

class FlyingEnemy2(FlyingEnemy):
    texture = pyglet.resource.texture('bat.png')
    scale = 1.2
    aggressive = True
    radius = 25
    
class FlyingEnemy3(FlyingEnemy):
    texture = pyglet.resource.texture("sparkysparksparkspark.png")
    scale = 2.0
    aggressive = True
    radius = 20
    def hit_player(self):
        super(FlyingEnemy3, self).hit_player()
        self.destroy()
        
class ChasingFlyer(FlyingEnemy):
    texture = pyglet.resource.texture("frog.png")
    gravity = PlatformObject.gravity
    speed = 0
    aggressive = False
    def tick(self):
        if self.pos.x < self.world.player.pos.x:
            self.aggressive = True
            self.speed = 1.5
            self.gravity = zero
        super(ChasingFlyer, self).tick()
    def hit_player(self):
        self.aggressive = False
        self.speed = 0
        self.gravity = PlatformObject.gravity
        super(ChasingFlyer, self).hit_player()

class CaterpillarEnemy(Enemy):
    texture = pyglet.resource.texture("ball.png")
    solid = False
    hp = 5
    ang = 90
    radius = 40
    scale = 1.6
    gravity = zero
    def __init__(self, *args, **kwargs):
        super(CaterpillarEnemy, self).__init__(*args, **kwargs)
        self.bend = random.choice((-2, 2))
        self.theta = 0
        self.head = kwargs.get('head', None)
        self.tail = None
        self.history = []
        if self.head is not None:
            self.head.tail = self
    def tick(self):
        self.history = [(self.pos, self.heading)] + self.history[:CATERPILLAR_SPACING]
        if self.head is not None:
            if self.head.destroyed:
                self.head = None
            else:
                if len(self.head.history) > CATERPILLAR_SPACING:
                    newpos, newh = self.head.history[CATERPILLAR_SPACING]
                    self.reposition(newpos)
                    self.heading = newh
        if self.head is None:
            if self.theta > 360:
                self.bend *= -1
                self.theta = 0
            if self.theta > 60 and self.theta % 10 == 0:
                d = self.world.player.pos - self.pos
                targetbend = 2 if (d.angle - self.ang) % 360 < 180 else -2
                if targetbend != self.bend and random.random() < 0.5:
                    self.theta = 0
                    self.bend = targetbend
            self.theta += 2
            self.ang += self.bend
            self.impulse(v(1.2, 0).rotated(self.ang))
            self.heading = self.ang
        super(CaterpillarEnemy, self).tick()
    def damage(self, n):
        if self.tail is not None:
            self.tail.damage(n)
            if self.tail.destroyed:
                self.tail = None
        else:
            super(CaterpillarEnemy, self).damage(n)

class Scroll(PlatformObject):
    radius = 30
    solid = False
    hashed = False
    gravity = zero
    texture = pyglet.resource.texture("scroll.png")
    def tick(self):
        p = self.world.player
        if (self.pos - p.pos).length < self.radius + p.radius:
            self.destroy()
            self.world.dispatch_event('on_collect_scroll')
            # do something awesome
        super(Scroll, self).tick()

class World(pyglet.event.EventDispatcher):
    event_types = ['on_player_dead', 'on_collect_scroll', 'on_player_stun', 'on_ability', 'on_victory']
    def __init__(self, starting_distance=-5):
        self.paused = False
        self.energy = MAX_ENERGY
        self.objects = []
        self.objects_to_remove = []
        self.spatialhash = SpatialHash()
        self.objecthash = SpatialHash()

        from gamelib import worldgen
        self.floor_gen = worldgen.make_infinite_floor(100, 50)
        p, f = next(self.floor_gen)
        self.floor_points = [p]
        self.segments = []

        self.features = []
        self.feature_segs = {}

        self.starting_distance = starting_distance
        self.distance_correction = None
        self.player = self.add_object(Player, v(0, 0))
        from gamelib import ability # is this right?
        self.player.ability = None
        self.nemesis = self.add_object(Demon, v(self.player.pos.x - DEMON_STARTING_POS, DEMON_HEIGHT))
        self.enemy_budget = 0
        self.fixed_scroll = starting_distance >= 0

    def get_distance(self):
        if self.distance_correction is None:
            self.distance_correction = self.player.left_wall - self.starting_distance * self.player.radius
        return (self.player.left_wall - self.distance_correction) / self.player.radius
    def get_nemesis_distance(self):
        return (self.player.left_wall - self.nemesis.pos.x) / self.player.radius

    def extend_floor(self, distance, quietly=False):
        count = 0
        feature_count = 0
        distance += self.floor_points[-1].x
        while self.floor_points[-1].x < distance:
            p, f = next(self.floor_gen)
            self.floor_points.append(p)
            s = PlatformSegment(*self.floor_points[-2:])
            self.segments.append(s)
            self.spatialhash.add(self.segments[-1])
            if not quietly:
                self.populate_segment(s)
            if f:
                self.add_feature(f)
                feature_count += 1
            count += 1
        return count, feature_count

    def delete_floor(self, count):
        for _ in xrange(count):
            self.spatialhash.remove(self.segments.pop(0))

    def place_player(self):
        self.player.reposition(self.segments[12].mid + (0, self.player.radius))
        self.nemesis.reposition(v(self.segments[12].mid.x - DEMON_STARTING_POS, DEMON_HEIGHT))

    def add_feature(self, f):
        f = tuple(f)
        self.features.insert(0, f)
        self.feature_segs[f] = fs = []
        for idx in xrange(len(f)):
            s = PlatformSegment(f[idx], f[(idx+1)%len(f)])
            self.spatialhash.add(s)
            fs.append(s)

    def remove_feature(self, f):
        self.features.remove(f)
        for s in self.feature_segs[f]:
            self.spatialhash.remove(s)
        del self.feature_segs[f]

    enemy_dists = { WalkingEnemy: -1000,
                    WalkingEnemy2: 750,
                    WalkingEnemy3: 1500,
                    FlyingEnemy: -1000,
                    FlyingEnemy2: 1000,
                    FlyingEnemy3: 500,
                    CaterpillarEnemy: 1200,
                    ChasingFlyer: 900,
    }
    
    enemy_costs = { WalkingEnemy: 1000,
                    WalkingEnemy2: 2400,
                    WalkingEnemy3: 4000,
                    FlyingEnemy: 2000,
                    FlyingEnemy2: 10000,
                    FlyingEnemy3: 3000,
                    CaterpillarEnemy: 4000,
                    ChasingFlyer: 1500,
    }

    def populate_segment(self, s):
        dist = (s.mid.x - self.distance_correction) / self.player.radius
        self.enemy_budget += s.length * int((dist / 200) + 1)
        if self.enemy_budget > 0:
            avail = [e for e in self.enemy_dists if self.enemy_dists[e] < dist]
            cls = random.choice(avail)
            if cls is CaterpillarEnemy:
                l = random.randrange(5, min(int(dist/200), 20))
                self.add_caterpillar(s.mid, l)
                self.enemy_budget -= self.enemy_costs[CaterpillarEnemy] * l
            elif cls is ChasingFlyer:
                n = int(s.length / ChasingFlyer.radius / 2)
                d = (s.end - s.start) / n
                p = s.start + 0.5 * d + (0, 100)
                for ii in xrange(n):
                    self.add_object(ChasingFlyer, p)
                    p += d
                self.enemy_budget -= self.enemy_costs[ChasingFlyer] * n
            else:
                self.add_object(cls, s.mid+v(0,100))
                self.enemy_budget -= self.enemy_costs[cls]
        if dist > 0:
            if not self.fixed_scroll: # ensure tutorial contains a scroll
                self.add_object(Scroll, s.mid + v(0, Scroll.radius))
                self.fixed_scroll = True
            else:
                d = dist / sqrt(app.state.collected_scrolls) / 500
                if d > 1:
                    p = 0.01
                else:
                    p = 0.01 * (3*d**2 - 2*d**3)
                if random.random() < p:
                    self.add_object(Scroll, s.mid + v(0, Scroll.radius))
        
    def add_object(self, cls, *args, **kwargs):
        obj = cls(self, *args, **kwargs)
        self.objects.append(obj)
        return obj

    def remove_object(self, obj):
        self.objects_to_remove.append(obj)

    def activate_ability(self, pos):
        if self.player.ability and not self.paused:
            if self.energy >= self.player.ability.energy:
                self.player.ability.activate(self, pos)
                self.energy -= self.player.ability.energy
                self.dispatch_event('on_ability', self.player.ability)
            else:
                sound.negative()

    def add_caterpillar(self, pos, length):
        prev = None
        for i in xrange(length):
            prev = self.add_object(CaterpillarEnemy, pos, head=prev)

    def tick(self):
        for obj in self.objects_to_remove:
            self.objects.remove(obj)
            if obj.hashed: self.objecthash.remove(obj)
        self.objects_to_remove = []
        if self.paused:
            from gamelib.ability import Explosion
            for e in self.objects:
                if isinstance(e, DemonDying) or isinstance(e, Explosion):
                    e.tick()
            return
        for e in self.objects:
            if isinstance(e, DemonDying):
                self.paused = True
            xo = self.player.pos.x - e.pos.x
            if e.protected or (xo < EXPIRE_DISTANCE and e.pos.y < EXPIRE_HEIGHT and e.pos.y > EXPIRE_DEPTH):
                e.tick()
            else:
                e.destroy()
        self.energy = min(MAX_ENERGY, self.energy + 1)

    def win(self):
        self.paused = True
        self.dispatch_event('on_victory')
