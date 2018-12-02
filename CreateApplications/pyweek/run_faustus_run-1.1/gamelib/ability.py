from __future__ import division

from math import *

from gamelib.vector import *
from gamelib import app
from gamelib import world
from gamelib import sound
from gamelib.data import upgrades

import pyglet

class Ability(object):
    upgrade = None
    energy = 500
    effect = None

class Projectile(world.PlatformObject):
    timer = 0
    def tick(self):
        super(Projectile, self).tick()
        self.timer += 1
        if self.timer > 500:
            self.destroy()
        if self.collided:
            self.collide()
            self.destroy()
    def collide(self):
        pass
    
class Bullet(Projectile):
    texture = pyglet.resource.texture("staralt.png")
    scale = 8.0
    drag = 1.0
    radius = 3
    gravity = zero
    vel = 10
    damage = 1
    def tick(self):
        super(Bullet, self).tick()
        for o in self.world.objecthash.colliders(self):
            if isinstance(o, world.Enemy):
                if (self.pos - o.pos).length < self.radius + o.radius:
                    o.damage(self.damage)
                    if o.solid:
                        o.impulse(self.delta.safe_scaled_to(self.vel))
                    self.destroy()
                    break

class Missile(Bullet):
    texture = pyglet.resource.texture("star.png")
    scale = 3.0
    radius = 10
    spin = 2
    def __init__(self, *args, **kwds):
        super(Missile, self).__init__(*args, **kwds)
        self.spin *= random.choice([-2, -1, 1, 2])
    @property
    def damage(self):
        return app.state.missile_damage
    def tick(self):
        self.heading += self.spin
        for o in self.world.objecthash.colliders(self, margin=45):
            if isinstance(o, world.Enemy):
                d = o.pos - self.pos
                if d.length2 < 2000:
                    self.reposition(o.pos, stop=False)
                    break # hit enemies which pass close
        super(Missile, self).tick()

class Arrow(Bullet):
    scale = 3.0
    drag = 0.95
    radius = 7
    solid = False
    texture = pyglet.resource.texture("staralt.png")
    def __init__(self, *args, **kwargs):
        super(Arrow, self).__init__(*args, **kwargs)
        self.ang = kwargs['ang']
        self.dest = kwargs['dest']
        self.timer = 0
    def tick(self):
        if self.timer < 20:
            spd = max(0, 10 - self.timer) * 0.15
            self.impulse(v(spd, 0).rotated(self.ang))
        elif self.timer == 20:
            self.stop()
            self.ang = (self.dest - self.pos).angle
        else:
            self.impulse(v(1.5, 0).rotated(self.ang))
        super(Arrow, self).tick()

class Firebomb(Projectile):
    drag = 1.0
    radius = 5
    gravity = v((0, -0.1))
    vel = 10
    texture = pyglet.resource.texture('bomb.png')
    def collide(self):
        self.world.add_object(Explosion, self.pos, size=app.state.firebomb_radius)
        sound.explosion()

class Explosion(world.PlatformObject):
    solid = False
    gravity = zero
    radius = 1
    ticks = 0
    texture = pyglet.resource.texture('boom.png')
    def __init__(self, *args, **kwargs):
        super(Explosion, self).__init__(*args, **kwargs)
        self.size = kwargs.get("size", 100)
        self.spin = (random.random() * 1.5 + 1.0) * random.choice((1, -1))
        self.damaged = set()
    def tick(self):
        self.ticks += 1
        self.resize(sin(self.ticks * pi / 30) * self.size)
        self.heading += self.spin
        if self.ticks > 30:
            self.destroy()
        if not self.safe:
            for o in self.world.objects:
                if isinstance(o, world.Enemy) and o.vincible:
                    if (o.pos - self.pos).length2 < self.radius ** 2:
                        if o not in self.damaged:
                            self.damaged.add(o)
                            o.damage(app.state.firebomb_damage)
        super(Explosion, self).tick()
    safe = False

class SafeExplosion(Explosion):
    safe = True

class Vortex(world.PlatformObject):
    texture = pyglet.resource.texture("vortex_icon.png")
    scale = 4.0
    solid = False
    drag = 1.0
    radius = 15
    gravity = v(0, 0.1)
    vel = 7
    ticks = 0
    def tick(self):
        self.ticks += 1
        if self.ticks > 100:
            self.destroy()
        for o in self.world.objects:
            if isinstance(o, world.Enemy) and o.solid:
                d = self.pos - o.pos
                m = min(100000 / d.length2, 10)
                o.impulse(d.safe_scaled_to(m))
        super(Vortex, self).tick()

class SummonedFlyer(world.PlatformObject):
    texture = pyglet.resource.texture("fairy.png")
    scale = 2.0
    gravity = zero
    def __init__(self, *args, **kwargs):
        super(SummonedFlyer, self).__init__(*args, **kwargs)
        self.ang = 90
        self.ticks = 0
    def tick(self):
        self.ang += random.randrange(-10,11)
        self.impulse(v(0.3, 0).rotated(self.ang))
        self.ticks += 1
        if self.ticks % 30 == 0:
            es = [o for o in self.world.objects if isinstance(o, world.Enemy) and o.vincible]
            if es:
                e = min(es, key=lambda e1: (e1.pos - self.pos).length2)
                b = self.world.add_object(Bullet, self.pos)
                projected_pos = e.pos + e.get_vel() * (e.pos - self.pos).length / b.vel
                dirn = (projected_pos - self.pos).safe_scaled_to(b.vel)
                b.impulse(dirn)
        if self.ticks > 300:
            self.destroy()
        super(SummonedFlyer, self).tick()

class Shield(world.PlatformObject):
    texture = pyglet.resource.texture("star.png")
    scale = 2.0
    gravity = zero
    solid = False
    def __init__(self, *args, **kwargs):
        self.phase = kwargs.get('phase', 0)
        super(Shield, self).__init__(*args, **kwargs)
        self.timer = 0
    def tick(self):
        self.phase += 10
        self.reposition(self.world.player.pos + v(75, 0).rotated(self.phase))
        self.timer += 1
        if self.timer > app.state.shield_time:
            self.destroy()
        super(Shield, self).tick()
        for o in self.world.objecthash.colliders(self):
            if isinstance(o, world.Enemy) and o.solid:
                if (self.pos - o.pos).length < self.radius + o.radius:
                    o.impulse((o.pos - self.world.player.pos).safe_scaled_to(15))

class ShieldAbility(Ability):
    upgrade = upgrades.s_shield
    effect = sound.shield
    energy = 1000
    def activate(self, world, pos):
        for p in xrange(0, 361, 360 // app.state.shield_count):
            world.add_object(Shield, world.player.pos, phase=p)

class FirebombAbility(Ability):
    upgrade = upgrades.s_firebomb
    effect = sound.firebomb
    energy = 250
    def activate(self, world, pos):
        fb = world.add_object(Firebomb, world.player.pos)
        dirn = (pos - world.player.pos).safe_scaled_to(fb.vel)
        fb.impulse(dirn)
        #fb.impulse(world.player.delta)

        maths = """
            Projectile launched at speed v and angle t to the horizontal from
            `(0, 0)` hits the ground again at `(L, 0)`. Parabola has equation
            `y = x (L - x)`.

            Projectile takes time `2 v sin t / g` to reach `(L, 0)` so we have
            `L = v cos t . 2 v sin t / g = v^2 sin 2t / g`.

                     y = x (v^2 sin 2t / g - x)
                sin 2t = g (x + y / x) / v^2

        """

        #disp = pos - world.player.pos
        #sinetwotheta = -fb.gravity.y * (disp.x + disp.y / disp.x) / (fb.vel**2)
        #sinetwotheta = min(sinetwotheta, 1)
        #print sinetwotheta
        #theta = degrees(asin(sinetwotheta) / 2)
        #fb.impulse(v(fb.vel, 0).rotated(theta))
                
class TeleportAbility(Ability):
    upgrade = upgrades.s_teleport
    effect = sound.teleport
    @property
    def energy(self):
        return app.state.teleport_cost
    def activate(self, world, pos):
        p = world.player
        segs = []
        for s in world.segments:
            xmin = min(s.start.x, s.end.x)
            xmax = max(s.start.x, s.end.x)
            if xmin < pos.x + p.radius and xmax > pos.x - p.radius:
                segs.append(s)
        if len(segs) == 0 : return # couldn't find safe destination
        dests = [s.mid - s.line.direction * p.radius for s in segs]
        newpos = min(dests, key=lambda d: (pos - d).length2)
        world.player.reposition(newpos)

class RepelAbility(Ability):
    upgrade = upgrades.s_repel
    effect = sound.repel
    energy = 150
    def activate(self, w, pos):
        for o in w.objects:
            if isinstance(o, world.Enemy) and o.solid:
                d = o.pos - v((w.player.pos.x, w.player.pos.y - 200))
                if d.length2 < 1000000:
                    o.impulse(d.safe_scaled_to(50))

class SummonAbility(Ability):
    upgrade = upgrades.s_summon
    effect = sound.summon
    energy = 300
    def activate(self, world, pos):
        world.add_object(SummonedFlyer, world.player.pos)

class VortexAbility(Ability):
    upgrade = upgrades.s_vortex
    effect = sound.vortex
    energy = 300
    def activate(self, world, pos):
        v = world.add_object(Vortex, world.player.pos)
        dirn = (pos - world.player.pos).safe_scaled_to(v.vel)
        v.impulse(dirn)

class ArrowsAbility(Ability):
    upgrade = upgrades.s_arrows
    effect = sound.arrows
    energy = 100
    def activate(self, world, pos):
        n = app.state.num_arrows
        for ii in xrange(n):
            world.add_object(Arrow, world.player.pos, ang=360*ii/n, dest=pos)

class MissileAbility(Ability):
    upgrade = upgrades.s_missile
    effect = sound.missile
    energy = 50
    def activate(self, world, pos):
        m = world.add_object(Missile, world.player.pos)
        dirn = (pos - world.player.pos).safe_scaled_to(m.vel)
        m.impulse(dirn)

abilities = [MissileAbility, FirebombAbility, TeleportAbility, RepelAbility, SummonAbility, VortexAbility, ArrowsAbility, ShieldAbility]
