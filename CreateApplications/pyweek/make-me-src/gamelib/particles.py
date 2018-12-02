#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: particles.py 386 2008-04-20 09:52:11Z aholkner $'

import random

import pyglet

import globals
import placeable

class ParticlesPlaceable(placeable.Placeable):
    image_name = 'spark.png'

    COUNT = 50
    TIME = 1.
    DX_RANGE = 100
    DY_RANGE = 100
    DY_BIAS = 0
    DDY = -100
    DSCALE_RANGE = 1.2
    DSCALE_BIAS = .5
    DR_RANGE = 180

    width = 64
    height = 64

    DESTROY_ON_HIT = False

    def place(self, x, y):
        return Particles(self, x, y)

class Particles(placeable.Placed):
    sprites = None

    
    def load(self, batch):
        if self.sprites:
            return

        self.t = 0
        image = self.placeable.get_image()
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprites = []
        p = self.placeable
        for i in range(p.COUNT):
            sprite = pyglet.sprite.Sprite(image, self.x, self.y, batch=batch)
            self.sprites.append(sprite)
            sprite.dx = (random.random() - .5) * p.DX_RANGE
            sprite.dy = (random.random() - .5) * p.DY_RANGE + p.DY_BIAS
            sprite.scale = 0.1
            sprite.dscale = random.random() * p.DSCALE_RANGE + p.DSCALE_BIAS
            sprite.dr = random.random() * p.DR_RANGE
        globals.game.clock.schedule(self.update)
        
    def unload(self):
        globals.game.clock.unschedule(self.update)
        if not self.sprites:
            return
        for sprite in self.sprites:
            sprite.delete()
        self.sprites = None

    def update(self, dt):
        self.t += dt
        TIME = self.placeable.TIME
        if self.t > TIME:
            globals.game.clock.unschedule(self.update)
            globals.game.effects_layer.remove_placed(self)
            return
        
        dy = self.placeable.DDY * dt

        for sprite in self.sprites:
            sprite.x += sprite.dx * dt
            sprite.y += sprite.dy * dt
            sprite.dy += dy
            sprite.scale += sprite.dscale * dt
            sprite.rotation += sprite.dr * dt
            sprite.opacity = min(TIME - self.t, 1) * 255

class DieEffect(ParticlesPlaceable):
    image_name = 'screw.png'

    COUNT = 10
    TIME = 1.
    DX_RANGE = 100
    DY_RANGE = 100
    DDY = -100
    DSCALE_RANGE = .5
    DSCALE_BIAS = .5
    DR_RANGE = 180

class ExplosionEffect(ParticlesPlaceable):
    image_name = 'spark.png'

    COUNT = 20
    TIME = 1.
    DX_RANGE = 200
    DY_RANGE = 200
    DSCALE_RANGE = 1.2
    DSCALE_BIAS = .5
    DR_RANGE = 360
    DDY = 0

class BubbleEffect(ParticlesPlaceable):
    image_name = 'bubble.png'

    COUNT = 30
    TIME = 1.
    DX_RANGE = 50
    DY_RANGE = 50
    DY_BIAS = 25
    DDY = 10
    DSCALE_RANGE = .5
    DSCALE_BIAS = 0
    DR_RANGE = 0

class SplashEffect(ParticlesPlaceable):
    image_name = 'bubble.png'

    COUNT = 10
    TIME = 1.
    DX_RANGE = 30
    DY_RANGE = 80
    DSCALE_RANGE = 0.1
    DSCALE_BIAS = 0.1
    DR_RANGE = 0
    DDY = -100

class DirtEffect(ParticlesPlaceable):
    image_name = 'rock.png'

    COUNT = 6
    TIME = 1.5
    DX_RANGE = 40
    DY_RANGE = 70
    DSCALE_RANGE = .5
    DSCALE_BIAS = .5
    DR_RANGE = 50
    DDY = -100

class StarEffect(ParticlesPlaceable):
    image_name = 'star-yellow.png'

    COUNT = 10
    TIME = 1.
    DX_RANGE = 200
    DY_RANGE = 200
    DSCALE_RANGE = 1.2
    DSCALE_BIAS = .5
    DR_RANGE = 360
    DDY = 0

class PurpleStarEffect(ParticlesPlaceable):
    image_name = 'star-purple.png'

    COUNT = 10
    TIME = 1.
    DX_RANGE = 200
    DY_RANGE = 200
    DSCALE_RANGE = 1.2
    DSCALE_BIAS = .5
    DR_RANGE = 360
    DDY = 0

die_effect = DieEffect()
explosion_effect = ExplosionEffect()
bubble_effect = BubbleEffect()
splash_effect = SplashEffect()
dirt_effect = DirtEffect()
star_effect = StarEffect()
purple_star_effect = PurpleStarEffect()
