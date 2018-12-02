#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

'''
Newton iteration method for solving sqrt
f(x) = x^2 - R
f'(x) = 2*x

x0 = R
x1 = x0 - (x0^2 - R)/(2 * x0)
x2 = x1 - (x1^2 - R)/(2 * x1)


After one iteration, series expansion (taking x/2 as initial
guess) is

sqrt(x) = x / 2 - (x * x / 4 - x) / x
        = x * 0.25 + 1.0

After two iterations

sqrt(x) = (x * 0.25 + 1.0) - ((x * .25 + 1.0)^2 - x/2) 
                                 / (2 * (x * .25 + 1.0)))
        = x * 0.125 - 4.0 / (0.5 * x + 2.0) + 2.5

For values likely to be less than 1, taking x is a better
initial guess.  After one iteration:

sqrt(x) = x - (x * x - x) / (2 * x)
        = x - x * x / 2x + x / 2x
        = x - x / 2 + 1/2
        = x * .5 + .5

'''

from math import sqrt, sin, cos, atan2, degrees, pi

import pyglet
from pyglet.window import key, mouse
from pyglet.gl import *

enable_cheats = False

try:
    import pyglet.media.avbin
    have_avbin = True
except:
    have_avbin = False

# monkey-patch some pixels of padding into texture atlas:
def _texture_atlas_add(self, img):
    pad = 1
    x, y = self.allocator.alloc(img.width + pad * 2, img.height + pad * 2)
    self.texture.blit_into(img, x + pad, y + pad, 0)
    region = self.texture.get_region(x + pad, y + pad, img.width, img.height)
    return region 
pyglet.image.atlas.TextureAtlas.add = _texture_atlas_add

TIME_SLICE = 1/30.
TIME_SLICE_2 = TIME_SLICE ** 2

class GameSprite(pyglet.sprite.Sprite):
    radius_x = None
    radius_y = None
    radius = None

    def __init__(self, *args, **kwargs):
        super(GameSprite, self).__init__(*args, **kwargs)
        # radius_[xy] define ellipse used for tail collision
        if self.radius_x is None:
            self.radius_x = self.image.width  / 2.0
        if self.radius_y is None:
            self.radius_y = self.image.height  / 2.0

        # radius defines circle for kite collision
        if self.radius is None:
            self.radius = min(self.radius_x, self.radius_y)
        self.radius_2 = self.radius ** 2

right_spawn_points = [(650, 300), (650, 200), (650, 400), 
                      (650, 100), (650, 450)]
top_spawn_points = [(200, 650), (400, 650)]
bottom_spawn_points = [(200, -350), (400, -350)]
low_right_spawn_points = [(x, y) for x, y in right_spawn_points \
                                if y < 300]
mid_right_spawn_points = [(x, y) for x, y in right_spawn_points \
                                if 300 <= y < 400]
high_right_spawn_points = [(x, y) for x, y in right_spawn_points \
                                 if y > 300]

class Food(GameSprite):
    mass_x = 0.1
    mass_y = 0.01

    spawn_points = right_spawn_points

    strangle_x = None
    strangle_y = None
    strangle_rotation = -90

    dangerous = True

    # Angular velocity while eaten
    dr = 0

    def __init__(self, *args, **kwargs):
        super(Food, self).__init__(*args, **kwargs)

        self.staged = True
        self.strangle_i = None
        self.strangle_bits = 0
        self.strangle_count = 0

        if self.strangle_x is None:
            self.strangle_x = self.image.anchor_x
        if self.strangle_y is None:
            self.strangle_y = self.image.anchor_y


        # Needed for integration when falling
        self.last_x = self.x
        self.last_y = self.y

    def update(self, x1, y1, x2, y2):
        pass

    @classmethod
    def spawn(cls, window, spawn_point):
        x, y = spawn_point
        y += window.level_y
        food = cls(cls.image_resource, x, y, batch=window.batch)
        window.food.append(food)

class LinearFood(Food):
    dx = -3
    dy = 1
    
    def __init__(self, *args, **kwargs):
        super(LinearFood, self).__init__(*args, **kwargs)
        self.base_dx = self.dx
        self.base_dy = self.dy

    def update(self, x1, y1, x2, y2):
        self.x += self.dx
        self.y += self.dy

        if self.base_dx >= 0 and self.x > x2 + self.radius_x:
            self.staged = False
        elif self.base_dy >= 0 and self.y > y2 + self.radius_y:
            self.staged = False
        elif self.base_dx <= 0 and self.x < x1 - self.radius_x:
            self.staged = False
        elif self.base_dy <= 0 and self.y < y1 - self.radius_y:
            self.staged = False

def flip(food_class):
    class Flipped(food_class):
        def __init__(self, *args, **kwargs):
            super(Flipped, self).__init__(*args, **kwargs)

        dx = -food_class.dx
        if hasattr(food_class, 'amplitude_dx'):
            amplitude_dx = -food_class.amplitude_dx
        image_resource = food_class.image_resource.get_transform(flip_x=True)
        spawn_points = [(600 - _x, _y) for _x, _y in food_class.spawn_points]

        if food_class.strangle_x is not None:
            strangle_x = image_resource.width - food_class.strangle_x

        flipped_class = food_class
    return Flipped

class LinearSawToothFood(LinearFood):
    period = 10

    def __init__(self, *args, **kwargs):
        super(LinearSawToothFood, self).__init__(*args, **kwargs)
        self.t = 0

    def update(self, x1, y1, x2, y2):
        self.t += 1
        if self.t > self.period:
            self.t = 0
            self.dy *= -1
        super(LinearSawToothFood, self).update(x1, y1, x2, y2)

class LinearASawToothFood(LinearFood):
    period_a = 20
    period_b = 10

    def __init__(self, *args, **kwargs):
        super(LinearASawToothFood, self).__init__(*args, **kwargs)
        self.t = 0

    def update(self, x1, y1, x2, y2):
        self.t += 1
        if self.dy > 0:
            period = self.period_a
        else:
            period = self.period_b
        if self.t > period:
            self.t = 0
            self.dy *= -1
        super(LinearASawToothFood, self).update(x1, y1, x2, y2)

class LinearCirclesFood(LinearFood):
    period = pi / 30
    amplitude_x = 5
    amplitude_y = 0

    dx = -3

    def __init__(self, *args, **kwargs):
        super(LinearCirclesFood, self).__init__(*args, **kwargs)
        self.theta = 0.

    def update(self, x1, y1, x2, y2):
        self.theta += self.period
        self.dx = self.base_dx + cos(self.theta) * self.amplitude_x
        self.dy = self.base_dy + sin(self.theta) * self.amplitude_y
        super(LinearCirclesFood, self).update(x1, y1, x2, y2)

class Angel(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/angel.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_x = 82
    strangle_y = 128

    spawn_points = [(200, -100), (400, -100)]
    dx = 0
    dy = 1

    period = pi / 30
    amplitude_x = 2
    amplitude_y = 0

class Astronaut(LinearFood):
    image_resource = pyglet.resource.image('food/astronaut.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_x = 52
    strangle_y = 107

class Balloon(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/balloon.png')
    image_resource.anchor_x = 17
    image_resource.anchor_y = 86
    radius_x = 19
    radius_y = 20
    strangle_x = 17
    strangle_y = 61

    spawn_points = mid_right_spawn_points

    dx = -1.8
    dy = 0

    period = -pi / 100
    amplitude_x = 0
    amplitude_y = -1

class FirstBalloon(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/balloon.png')
    image_resource.anchor_x = 17
    image_resource.anchor_y = 86
    radius_x = 19
    radius_y = 20
    strangle_x = 17
    strangle_y = 61

    dx = 0
    dy = 0
    spawn_points = [(200, 300)]

    period = pi / 100 
    amplitude_x = 0
    amplitude_y = 1

    # For purposes of challenge mode
    flipped_class = Balloon

class Bee(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/bee.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    period = pi / 30
    amplitude_x = 5
    amplitude_y = 0

    dx = -3


class BlueBird(LinearFood):
    image_resource = pyglet.resource.image('food/blue_bird.png')
    image_resource.anchor_x = image_resource.width / 2 
    image_resource.anchor_y = image_resource.height / 2

    strangle_x = 23
    strangle_y = 17
    strangle_rotation = 90

    dx = -3
    dy = 0

class Boy(Food):
    image_resource = pyglet.resource.image('food/boy.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    spawn_points = [(150, 150 + 100)]
    strangle_x = 55
    strangle_y = 241

    dangerous = False
    mass = 0.

    @classmethod
    def spawn(cls, window, spawn_point):
        x, y = spawn_point
        food = cls(cls.image_resource, x, y, batch=window.batch)
        window.food.append(food)

class BrownBird(LinearFood):
    image_resource = pyglet.resource.image('food/brown_bird.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_x = 20
    strangle_y = 60
    strangle_rotation = 0

    dx = -4
    dy = -1.5

class Bug(LinearSawToothFood):
    image_resource = pyglet.resource.image('food/bug.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    period = 3
    dx = -3
    dy = 4

class Butterfly(LinearSawToothFood):
    period = 30
    dx = -1
    dy = 1.5

    image_resource = pyglet.resource.image('food/butterfly.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

class Cloud(LinearFood):
    image_resource = pyglet.resource.image('food/cloud.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

class Comet(LinearFood):
    image_resource = pyglet.resource.image('food/comet.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_x = 15
    strangle_y = 15

    spawn_points = high_right_spawn_points

    dx = -3.5
    dy = -3.5

class Devil(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/devil.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_x = 57
    strangle_y = 110

    spawn_points = top_spawn_points
    dx = 0
    dy = -1

    period = pi / 15
    amplitude_x = 2
    amplitude_y = 0

class Fish(LinearFood):
    image_resource = pyglet.resource.image('food/fish.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_x = 42
    strangle_y = 27
    strangle_rotation = 90

    dx = -4
    dy = 0

class Ghost(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/ghost.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    dx = -4
    dy = 0

    period = pi / 40
    amplitude_x = 3
    amplitude_y = 3

class Harp(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/harp.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_x = 45
    strangle_y = 60

    dx = -2
    dy = 0
    period = pi / 60
    amplitude_x = 0
    amplitude_y = 3

class Helicopter(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/helicopter.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_x = 110
    strangle_y = 33
    strangle_rotation = 90

    dx = -3
    dy = 0

    period = pi / 10
    amplitude_x = 3
    amplitude_y = 0

class JellyFish(LinearFood):
    image_resource = pyglet.resource.image('food/jelly_fish.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    dx = -1
    dy = 1

    count = 3
 
    def update(self, x1, y1, x2, y2):
        self.x += self.dx
        self.y += self.dy

        if self.dx > 0 and self.x > x2 - self.radius_x:
            if self.count > 0:
                self.dx *= -1
                self.count -= 1
        elif self.dy > 0 and self.y > y2 - self.radius_y:
            if self.count > 0:
                self.dy *= -1
                self.count -= 1
        elif self.dx < 0 and self.x < x1 + self.radius_x:
            if self.count > 0:
                self.dx *= -1
                self.count -= 1
        elif self.dy < 0 and self.y < y1 + self.radius_y:
            if self.count > 0:
                self.dy *= -1
                self.count -= 1

        self.base_dx = self.dx
        self.base_dy = self.dy

        super(JellyFish, self).update(x1, y1, x2, y2)

class Mars(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/mars.png')
    image_resource.anchor_x = 88
    image_resource.anchor_y = 53

    radius_x = 53
    radius_y = 53

    spawn_points = [(650, 200)]

    period = pi / 500
    dx = -1
    dy = 0
    amplitude_x = -2
    amplitude_y = 2

class Moon(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/moon.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    spawn_points = [(-50, 500)]

    period = pi / 500
    dx = -2
    dy = 0
    amplitude_x = 5.
    amplitude_y = -5.

class Robot(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/pi.png')
    image_resource.anchor_x = 28
    image_resource.anchor_y = 60

    radius_x = 40
    radius_y = 64
    strangle_y = 70


    dx = -0.8
    dy = 0

    period = pi / 100
    amplitude_x = 0
    amplitude_y = 1

class Plane(LinearFood):
    image_resource = pyglet.resource.image('food/plane.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_x = 96
    strangle_y = 36
    strangle_rotation = 90

    dx = -7.
    dy = 0.
    
class FlyingPig(LinearASawToothFood):
    image_resource = pyglet.resource.image('food/pyglet.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_x = 60
    strangle_y = 25
    strangle_rotation = -90

    dy = 1.5
    dx = -3.5
    period_a = 60
    period_b = 20

class Rocket(LinearFood):
    image_resource = pyglet.resource.image('food/rocket.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_rotation = 180

    spawn_points = bottom_spawn_points

    dx = 0
    dy = 10

class Satellite(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/satellite.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    radius_x = 108
    strangle_x = 88
    strangle_y = 51
    strangle_rotation = -90

    spawn_points = high_right_spawn_points

    period = pi / 1500.
    dx = -2
    dy = 0
    amplitude_x = 0
    amplitude_y = -3

class Saturn(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/saturn.png')
    image_resource.anchor_x = 80
    image_resource.anchor_y = 80

    radius_x = 60
    radius_y = 60
    strangle_x = 22
    strangle_y = 22
    strangle_rotation = 90

    spawn_points = [(-50, 200)]

    period = pi / 500
    dx = 1
    dy = 0
    amplitude_x = 2
    amplitude_y = 2


class SkyDiver(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/sky_diver.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_x = 39
    strangle_y = 20
    strangle_rotation = 90

    spawn_points = top_spawn_points
    dx = 0
    dy = -6
    period = pi / 50
    amplitude_x = 3
    amplitude_y = 0

class SpaceRock(LinearFood):
    image_resource = pyglet.resource.image('food/space_rock.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    dx = -4.
    dy = 3

class StingRay(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/sting_ray.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = 42

    spawn_points = mid_right_spawn_points

    radius_y = 44
    strangle_x = 188
    strangle_y = 35
    strangle_rotation = -90

    dx = -3
    dy = 0

    period = pi / 80
    amplitude_x = 0
    amplitude_y = -3

class UFO(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/ufo.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    strangle_rotation = 90

    dx = -4.5
    dy = 0

    period = pi / .3
    amplitude_x = 0
    amplitude_y = 5

class Worm(LinearCirclesFood):
    image_resource = pyglet.resource.image('food/worm.png')
    image_resource.anchor_x = image_resource.width / 2
    image_resource.anchor_y = image_resource.height / 2

    dx = -3
    dy = 0

    period = pi / 10
    amplitude_x = 3
    amplitude_y = 0

class Level(object):
    background_positions = [
        (300, 300), (100, 300), (400, 300)]

    def __init__(self, food_count, target_score, food_classes, color,
                 *backgrounds):
        self.food_count = food_count
        self.food_classes = food_classes
        self.target_score = target_score
        self.backgrounds = backgrounds
        self.color = color

        self.loaded = False
        self.loaded_backgrounds = []

        self.challenge_target = set()
        for food_class in food_classes:
            if hasattr(food_class, 'flipped_class'):
                food_class = food_class.flipped_class
            self.challenge_target.add(food_class)

        self.reset(False)

    def load(self, window, index):
        if self.loaded:
            return

        self.loaded = True
        i = index
        for background in self.backgrounds:
            if type(background) is tuple:
                background, x, y, is_foreground = background
                if is_foreground:
                    batch = window.foreground_batch
                else:
                    batch = window.background_batch
            else:
                i = (i + 1) % len(self.background_positions)
                x, y = self.background_positions[i]
                batch = window.background_batch
            self.loaded_backgrounds.append(pyglet.sprite.Sprite(
                pyglet.resource.image(background), 
                x, y + index * 300, batch=batch))

    def unload(self):
        if not self.loaded:
            return

        self.loaded = False
        for sprite in self.loaded_backgrounds:
            sprite.delete()
        del self.loaded_backgrounds[:]

    def reset(self, challenge):
        self.food_class_index = 0

        self.is_done = False
        self.score = 0
        self.spawn_point_index = 0

        self.challenge = challenge
        self.challenge_score = set()

    def eat_food(self, food):
        if self.challenge:
            food_class = food.__class__
            if hasattr(food_class, 'flipped_class'):
                food_class = food_class.flipped_class
            self.challenge_score.add(food_class)
            if len(self.challenge_score) == len(self.challenge_target):
                self.is_done = True
        else:
            self.score += 1
            if self.score >= self.target_score:
                self.is_done = True

    def spawn(self, window):
        if len(window.food) >= self.food_count:
            return

        food_class = self.food_classes[self.food_class_index]
        self.food_class_index = (self.food_class_index + 1) % \
                                    len(self.food_classes)

        spawn_points = food_class.spawn_points 
        spawn_point = spawn_points[self.spawn_point_index % len(spawn_points)]
        self.spawn_point_index += 1
        food_class.spawn(window, spawn_point)

class PenultimateLevel(Level):
    def spawn(self, window):
        # only spawn if there is not enough on screen to fulfil target score.
        # - 1 to account for boy
        if len(window.food) + self.score  - 1 >= self.target_score:
            return

        super(PenultimateLevel, self).spawn(window)

class BoyLevel(Level):
    spawned = False

    def load(self, window, index):
        if self.loaded:
            return

        super(BoyLevel, self).load(window, index)

        food_class = self.food_classes[0]
        x, y = food_class.spawn_points[0]
        y += index * 300
        food_class.spawn(window, (x, y))

    def unload(self):
        super(BoyLevel, self).unload()
        self.spawned = False

    def reset(self, challenge):
        super(BoyLevel, self).reset(challenge)
        self.spawned = False

    def spawn(self, window):
        if self.score > 3:
            return

class TextFood(pyglet.text.Label): # Pretending to be Food
    dangerous = False

    mass_x = 0.2
    mass_y = 0.2

    strangle_rotation = 0
    dr = 0

    def __init__(self, *args, **kwargs):
        kwargs.update(dict(
            font_name='I hate Comic Sans',
            color=(0, 0, 0, 255)))
        super(TextFood, self).__init__(*args, **kwargs)

        self.anchor_x = 'center'
        self.anchor_y = 'center'

        self.staged = True
        self.strangle_i = None
        self.strangle_bits = 0
        self.strangle_count = 0

        self.radius_x = self.content_width / 2
        self.radius_y = self.content_height / 2 
        self.strangle_x = 0
        self.strangle_y = 0
        self.last_x = self.x
        self.last_y = self.y

        self.opacity = 255

    def update(self, x1, y1, x2, y2):
        pass

    @classmethod
    def spawn(cls, window, spawn_point):
        raise RuntimeError("Don't spawn me, bro")

    # sprites have rgb color, labels have rgba color. doh
    def _set_color(self, value):
        pass

    def _get_color(self):
        return super(TextFood, self)._get_color()[:3]

    color = property(_get_color, _set_color)

    def _set_opacity(self, opacity):
        r, g, b, _ = super(TextFood, self)._get_color()
        super(TextFood, self)._set_color((r, g, b, int(opacity)))

    def _get_opacity(self):
        _, _, _, opacity = super(TextFood, self)._get_color()
        return opacity
        
    opacity = property(_get_opacity, _set_opacity)

def food_remover(food, window, clock):
    def remove(dt):
        if food in window.food:
            Animator(clock, food, 'opacity', 0, 1.0)
            clock.schedule_once(lambda dt: food.delete(), 1.1)
            window.food.remove(food)
    return remove

def sprite_remover(sprite, clock):
    def remove(dt):
        Animator(clock, sprite, 'opacity', 0, 1.0)
        clock.schedule_once(lambda dt: sprite.delete(), 1.1)
    return remove

class Credits(object): # Pretending to be a level
    def __init__(self):
        self.is_done = False

        self.credits = [
            (0.0, 3.0, 'background', 'background/end.png', 40, 0),
            (3.5, 14.0, 'foodtext', ('Kite', 48), 230, 300), 
            (3.5, 14.0, 'foodtext', ('Story', 48), 370, 300),
            (4.5, 14.0, 'foodtext', ("Rebecca 'Biccy' Wong", 20), 170, 500),
            (4.5, 14.0, 'foodtext', ("Art, Design", 14), 170, 470),
            (5.5, 14.0, 'foodtext', ("Alex Holkner", 20), 430, 500),
            (5.5, 14.0, 'foodtext', ("Code, Piano", 14), 430, 470),
            (6.5, 14.0, 'foodtext', ("Sofie Bird", 20), 300, 150),
            (6.5, 14.0, 'foodtext', ("Vocals", 14), 300, 120),
            (15.5, 31.0, 'spawn', flip(BlueBird), -50, 400),
            (15.5, 31.0, 'spawn', Bee, 650, 200),
            (20, 31.0, 'spawn', Moon, -50, 500),
            (20, 31.0, 'spawn', SpaceRock, 650, 300),
            (26, 31.0, 'spawn', Mars, 650, 100),
            (31, 47, 'spawn', Rocket, 400, -100),
            (31, 47, 'spawn', flip(Plane), -50, 400),
            (37, 47, 'spawn', flip(Satellite), -100, 300),
            (37, 47, 'spawn', Helicopter, 650, 200),
            (40, 47, 'spawn', flip(JellyFish), -50, 500),
            (40, 47, 'spawn', StingRay, 740, 400),
            (48, 63, 'spawn', Devil, 200, 650),
            (48, 63, 'spawn', Angel, 400, -50),
            (51, 63, 'spawn', flip(Balloon), -50, 300),
            (52, 63, 'spawn', Astronaut, 650, 200),
            (54, 63, 'spawn', flip(Robot), -50, 200),
            (55, 63, 'spawn', FlyingPig, 650, 400),
            (64, 70, 'foodtext', ('PyWeek', 36), 300, 300),
            (64, 70, 'foodtext', ('September 2008', 24), 300, 250),
            (66, 70, 'foodtext', ('Greetings to all', 14), 300, 400),
            (66, 70, 'foodtext', ('contestants!', 14), 300, 150),
            (72, 72, 'fadeout', None, None, None),
        ]
        self.credits_i = 0
        self.credits_time = 0
        self.sprites = []

    def update(self, dt):
        self.credits_time += dt

        if self.credits_i >= len(self.credits):
            return

        while (self.credits[self.credits_i][0] <= self.credits_time):
            _, end, format, value, x, y = self.credits[self.credits_i]

            if format == 'foodtext':
                text, size = value
                food = TextFood(text, x=x, y=y + self.window.camera_y, 
                                font_size=size,
                                batch=self.window.batch)
                food.opacity = 0
                Animator(pyglet.clock.get_default(), food, 'opacity', 255, 1.0)
                self.window.food.append(food)
                pyglet.clock.schedule_once(
                    food_remover(food, self.window, pyglet.clock.get_default()),
                    end - self.credits_time)
                    
            elif format == 'background':
                sprite = pyglet.sprite.Sprite(
                    pyglet.resource.image(value), 
                    x, y + self.window.camera_y, 
                    batch=self.window.background_batch)
                self.sprites.append(sprite)
                pyglet.clock.schedule_once(
                    sprite_remover(sprite, pyglet.clock.get_default()),
                    end - self.credits_time)

            elif format == 'spawn':
                value.spawn(self.window, (x, y))
                food = self.window.food[-1]
                pyglet.clock.schedule_once(
                    food_remover(food, self.window, pyglet.clock.get_default()),
                    end - self.credits_time)

            elif format == 'fadeout':
                self.window.restart()
                self.unload()

            self.credits_i += 1
            if self.credits_i >= len(self.credits):
                break
    
    def start_credits(self, window):
        self.window = window
        self.window.set_music('music/world.mp3')
        pyglet.clock.schedule(self.update)

    def stop_credits(self):
        pyglet.clock.unschedule(self.update)

    def load(self, window, index):
        pass

    def unload(self):
        pass

    def spawn(self, window):
        pass

    def eat_food(self, food):
        pass
    
    def reset(self, challenge):
        pass

levels = [
    # Treetops
    Level(1, 3, [FirstBalloon, flip(Balloon), Balloon, flip(Balloon)],
        (255, 255, 200), 
        ('background/tree.png', 300, 0, False),
        ('background/grass.png', 0, -15, False),
        ('background/boy.png', 420, 15, True)),
    Level(2, 3, [Butterfly, flip(Butterfly)],
        (200, 255, 255),
        ('background/tree.png', 300, -300, False)),
    Level(3, 3, [Bee, flip(Bee)],
        (200, 255, 255), 'background/cloud1.png'),
    Level(3, 3, [BlueBird, Butterfly, flip(Bee), flip(Butterfly), 
                 flip(BlueBird)],
        (255, 255, 255), 'background/cloud2.png'),

    # Sky
    Level(3, 3, [BlueBird, flip(Robot), BlueBird, BlueBird, flip(BlueBird),
                 BlueBird, flip(BlueBird), BlueBird, flip(BlueBird)],
        (255, 255, 200), 'background/cloud1.png'),
    Level(3, 3, [BrownBird, BlueBird, flip(BrownBird), BrownBird,
                 flip(BlueBird), BlueBird, BrownBird],
        (200, 200, 255), 'background/cloud1.png'),
    Level(3, 3, [FlyingPig, BrownBird, BlueBird, flip(BrownBird), BrownBird,
                 flip(BlueBird), BlueBird, BrownBird],
        (255, 200, 255)),

    # Upper sky
    Level(4, 3, [SkyDiver, flip(BlueBird), BlueBird],
        (255, 200, 255), 'background/cloud2.png'),
    Level(3, 3, [flip(Helicopter), BrownBird, flip(BlueBird), Helicopter],
        (200, 180, 255), 'background/cloud1.png'),
    Level(2, 3, [flip(Plane), Helicopter, flip(BrownBird), flip(Plane), 
                 BrownBird],
        (180, 150, 200), 'background/cloud1.png'),
    Level(4, 3, [flip(Plane), Plane, Plane, flip(Plane), Plane],
        (150, 120, 150)),

    # Space
    Level(1, 1, [Rocket],
        (100, 100, 150), 'background/star.png'),
    Level(3, 3, [flip(Satellite), flip(SpaceRock), SpaceRock, Comet],
        (100, 50, 100), 'background/star.png', 'background/star.png'),
    Level(4, 3, [Astronaut, flip(SpaceRock), SpaceRock, flip(SpaceRock),
                 Comet, flip(SpaceRock), flip(Comet)],
        (100, 50, 100), 'background/star.png'),
    Level(4, 3, [flip(Astronaut), UFO, Comet, flip(SpaceRock), flip(Comet),
                 SpaceRock, flip(SpaceRock),], 
        (100, 50, 100), 'background/star.png', 'background/star.png'),
    Level(5, 3, [flip(UFO), UFO, flip(UFO), Rocket, Rocket, UFO],
        (100, 50, 100), 'background/star.png'),

    # Planetary
    Level(4, 3, [Moon, SpaceRock, Comet,
                 flip(SpaceRock), Astronaut, SpaceRock, Comet],
        (100, 50, 100), 'background/star.png'),
    Level(3, 3, [Mars, SpaceRock, flip(Comet),
                 flip(SpaceRock), SpaceRock, Comet],
        (100, 50, 100), 'background/star.png'),
    Level(4, 3, [Saturn, SpaceRock, flip(Comet), Comet, SpaceRock, flip(Comet),
                 flip(SpaceRock), SpaceRock, Comet],
        (150, 100, 150), 'background/star.png'),

    # Heaven
    Level(5, 3, [SpaceRock, SpaceRock, flip(SpaceRock), SpaceRock,
                 flip(SpaceRock), flip(SpaceRock)],
        (200, 150, 200), 'background/h_nimbus.png'),
    Level(3, 3, [Angel, flip(Harp), Harp, Harp, flip(Harp)],
        (220, 160, 220), 'background/h_twin_nimbus.png'),
    Level(5, 3, [Harp, flip(Harp), flip(Harp), Harp],
        (220, 160, 220), 'background/h_nimbus.png'),

    # Hell
    Level(4, 3, [Harp, Ghost, flip(Ghost), flip(Ghost)],
        (245, 150, 160), 'background/torch.png'),
    Level(3, 3, [Devil, flip(Ghost), Ghost, Devil, Devil, Ghost],
        (160, 20, 25), 'background/flame.png'),
    Level(4, 3, [flip(Ghost), Ghost, Ghost],
        (160, 20, 25), 'background/flame.png', 'background/torch.png'),

    # Underwater
    Level(3, 3, [flip(JellyFish), JellyFish, flip(JellyFish)],
        (150, 30, 40), 'background/seaweed.png'),
    Level(3, 3, [StingRay, flip(JellyFish), StingRay,
                 JellyFish, flip(JellyFish), JellyFish],
        (50, 95, 160), 'background/squid.png'),
    Level(5, 3, [Fish, JellyFish, Fish, flip(JellyFish), Fish,
                 flip(Fish)],
        (100, 120, 120), 'background/bones.png'),

    # Underground
    Level(6, 3, [Bug, flip(Bug), Worm, flip(Bug), flip(Worm), Bug],
        (175, 150, 110), 'background/bone.png'),
    PenultimateLevel(2, 2, [Worm, Bug, flip(Worm), flip(Bug), Worm, 
                            flip(Bug), Bug],
        (175, 160, 120), ('background/bone.png', 200, 250, False)),

    # Final
    BoyLevel(1, 1, [Boy],
        (255, 255, 200),
        ('background/tree.png', 300, 50, False),
        ('background/grass.png', 0, 50-14, False),
        ('background/string.png', -65, 290, False),
        ('background/jeepers.png', 200, 400, True)),

    # sentinals
    Level(0, 0, [],
        (200, 255, 255)),
    Level(0, 0, [],
        (200, 255, 255)),
    Level(0, 0, [],
        (180, 180, 255)),
    Level(0, 0, [],
        (0, 0, 0)),
    Level(0, 0, [],
        (0, 0, 0)),
]

class Animator(object):
    def __init__(self, clock, obj, attr, goal, delay):
        self.clock = clock
        self.obj = obj
        self.attr = attr

        # sine interpolate
        start = getattr(obj, attr)
        self.bias = start
        self.multiplier = goal - start
        self.period = pi/2 / delay
        self.delay = delay
        self.goal = goal

        self.clock.schedule(self.update)

    def update(self, dt):
        self.delay -= TIME_SLICE
        if self.delay < 0:
            setattr(self.obj, self.attr, self.goal)
            self.clock.unschedule(self.update)
        
        value = \
            sin(pi / 2 - self.delay * self.period) * self.multiplier + self.bias
        setattr(self.obj, self.attr, value)

class Button(pyglet.sprite.Sprite):
    def hit(self, x, y):
        return (0 < x - (self.x - self.image.anchor_x) < self.width and
                0 < y - (self.y - self.image.anchor_y) < self.height)

class Button2(object):
    def __init__(self, sprite, x1, y1, x2, y2):
        self.x1 = sprite.x + x1
        self.y1 = sprite.y + sprite.height - y1
        self.x2 = sprite.x + x2
        self.y2 = sprite.y + sprite.height - y2

    def hit(self, x, y):
        return self.x1 < x < self.x2 and self.y1 < y < self.y2

class Menu(object):
    def __init__(self, window):
        self.window = window
        self.window.push_handlers(self)
        self.batch = window.background_batch
        self.title_sprite = pyglet.sprite.Sprite(
            pyglet.resource.image('menu/title.png'), 820, 360,
            batch=window.foreground_batch)
        self.menu_sprite = pyglet.sprite.Sprite(
            pyglet.resource.image('menu/menu.png'), 870, 0, 
            batch=window.foreground_batch)
        self.easy_button = Button2(self.menu_sprite, 42, 144, 233, 105)
        self.hard_button = Button2(self.menu_sprite, 51, 217, 233, 176)
        self.quit_button = Button2(self.menu_sprite, 58, 294, 234, 241)

    def delete(self):
        self.menu_sprite.delete()
        self.window.remove_handlers(self)
        self.window.menu = None

    def on_mouse_press(self, x, y, button, modifiers):
        x += self.window.camera_x
        y += self.window.camera_y
        if self.easy_button.hit(x, y):
            self.window.begin_game()
        elif self.hard_button.hit(x, y):
            self.window.begin_game(challenge=True)
        elif self.quit_button.hit(x, y):
            self.window.close()

class TranslateGroup(pyglet.graphics.Group):
    x = y = 0

    def set_state(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)

    def unset_state(self):
        glPopMatrix()

class TailGroup(pyglet.graphics.Group):
    def __init__(self, texture, parent=None):
        super(TailGroup, self).__init__(parent)
        self.texture = texture

    def set_state(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)

    def unset_state(self):
        glDisable(self.texture.target)
        glDisable(GL_BLEND)

class DropdownMenu(object):
    def __init__(self, window):
        self.window = window
        self.window.push_handlers(self)
        self.batch = window.overlay_batch
        self.group = TranslateGroup()
        self.group.y = 200
        self.sprite = pyglet.sprite.Sprite(
            pyglet.resource.image('menu/drop_down.png'), 74, 410,
            group=self.group, batch=self.batch)
        self.continue_button = Button2(self.sprite, 
            32, 68, 201, 38)
        self.start_again_button = Button2(self.sprite, 
            30, 122, 197, 87)
        self.quit_button = Button2(self.sprite, 
            29, 186, 190, 155)

        self.dismissed = False
        Animator(self.window.game_clock, self.group, 'y', 0, 0.5)

    def delete(self):
        self.sprite.delete()
        self.window.remove_handlers(self)
        self.window.dropdown_menu = None

    def dismiss(self):
        if self.dismissed:
            return
        self.dismissed = True
        Animator(self.window.game_clock, self.group, 'y', 200, 0.5)
        self.window.game_clock.schedule_once(
            lambda dt: self.delete(), 1.0)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.dismiss()
        return True

    def on_mouse_press(self, x, y, button, modifiers):
        if self.continue_button.hit(x, y):
            self.dismiss()
        elif self.start_again_button.hit(x, y):
            self.dismiss()
            self.window.restart()
        elif self.quit_button.hit(x, y):
            self.window.close()

class BaseInstructor(object):
    def delete(self):
        pass

    def event(self, event):
        pass

class Instructor(BaseInstructor):
    fade_time = 0.5

    def __init__(self, window):
        self.window = window
        self.clock = window.game_clock
        self.batch = self.window.overlay_batch
        self.sprite = s = pyglet.sprite.Sprite(
            pyglet.resource.image('instruction.png'), x=0, y=0,
            batch=self.batch)
        self.sprite.opacity = 0
        self.label = pyglet.text.HTMLLabel('', 
            x=s.x + s.width//2, y=s.y + s.height//2 - 5,
            multiline=True, width=s.width-70,
            anchor_x='center', anchor_y='center',
            batch=self.batch)

        self.blocked = True
        self.showing = False
        self.queue = []
        self.shown_eaten = False
        self.shown_impact = False
        self.shown_drop = False
        self.shown_rise = False
        self.shown_rise2 = False
        self.shown_rise3 = False

        self.clock.schedule_once(lambda dt: self.intro(), 2.0)

    def delete(self):
        if not self.sprite:
            return
        self.clock.unschedule(self.intro)
        self.clock.unschedule(self.next_message)
        self.sprite.delete()
        self.label.delete()
        self.sprite = None

    def intro(self):
        self.queue_message('Move the mouse around to direct your kite.')
        self.queue_message(
            'Wrap and tighten your kite string around the balloon ' + 
            'to catch it.', True)

    def event(self, event):
        if event == 'dismiss':
            self.next_message()
        elif event == 'eat_food':
            if not self.shown_eaten:
                self.shown_eaten = True
                self.queue_message(
                    "That's the idea.  Catch two more balloons to advance " +
                    "to the next level.")
        elif event == 'next_level':
            if not self.shown_rise:
                self.shown_rise = True
                self.queue_message(
                    "Whee!  Now see if you can catch these butterflies.")
            if not self.shown_rise2 and self.window.level_index == 2:
                self.shown_rise2 = True
                self.queue_message(
                    "You only need to catch any three objects to advance " +
                    "to the next level.")
            if not self.shown_rise3 and self.window.level_index == 6:
                self.shown_rise3 = True
                self.queue_message(
                    "You might need to use the birds to help you catch the " +
                    "skydivers.")
        elif event == 'impact':
            if not self.shown_impact and self.shown_eaten:
                self.shown_impact = True
                self.queue_message(
                    "Ow!  Try not to let objects touch the wing of your kite.")
        elif event == 'drop_food':
            if not self.shown_drop:
                self.shown_drop = True
                self.queue_message(
                    "When your kite is hit, you'll lose objects you've " +
                    "caught.")
                self.queue_message(
                    "If you don't have any objects left, you'll drop back " +
                    "a level.")

    def queue_message(self, text, block=False):
        self.queue.append((text, block))

        if self.blocked:
            self.next_message()

    def next_message(self):
        if self.queue:
            message, block = self.queue.pop(0)
            self.set_message(message)
            if block and not self.queue:
                self.window.game_clock.schedule_once(
                    lambda dt: self.block_message(), 4.0)
            else:
                self.window.game_clock.schedule_once(
                    lambda dt: self.next_message(), 4.0)
                self.blocked = False
        else:
            self.hide_message()
            self.blocked = True

    def block_message(self):
        if self.queue:
            self.next_message()
        else:
            self.blocked = True

    def set_message(self, text):
        if self.showing:
            self.hide_message()
            self.window.game_clock.schedule_once(
                lambda dt: self.show_message(text), self.fade_time)
        else:
            self.show_message(text)

    def show_message(self, text):
        self.showing = True
        text = '<center><font face="I hate Comic Sans" size="5">' + text + \
               '</font></center>'
        self.label.text = text
        self.label.color = (0, 0, 0, 0)
        Animator(self.window.game_clock, self, 'opacity', 250, self.fade_time)

    def hide_message(self):
        if not self.showing:
            return
        self.showing = False
        Animator(self.window.game_clock, self, 'opacity', 0, self.fade_time)

    def get_opacity(self):
        if self.sprite:
            return self.sprite.opacity
        return 0

    def set_opacity(self, opacity):
        if self.sprite:
            self.sprite.opacity = opacity
            self.label.color = (0, 0, 0, int(opacity))

    opacity = property(get_opacity, set_opacity)

class ChallengeInstructor(Instructor):
    def intro(self):
        self.queue_message('You must catch at least one object of every ' +
            'type to advance to the next level.')
        self.queue_message('Good luck!')

    def event(self, event):
        pass

class Window(pyglet.window.Window):
    dropdown_menu = None

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        pyglet.resource.add_font('fonts/IHateComicSans.ttf')

        self.game_time = 0.
        self.game_clock = pyglet.clock.Clock(
            time_function=lambda: self.game_time)

        self.invulnerable = True
        self.mouse_active = True
        self.level_index = 0
        self.level_y = 0
        self.camera_x = 0
        self.camera_y = 0
        self.fade = 1.
        self.game_clock.schedule_once(self.set_vulnerable, 2.0)

        self.batch = pyglet.graphics.Batch()
        self.foreground_batch = pyglet.graphics.Batch()

        # For verlet integration, track the previous and current point
        # positions of each segment of the tail.
        x, y = self.boy_position = 429, 209
        self.last_tail_segments = [(i+x, y) for i in range(100)]
        self.tail_segments = self.last_tail_segments[:]

        # Rendered tail.
        tail_texture = pyglet.resource.texture('tail.png')
        glBindTexture(tail_texture.target, tail_texture.id)
        glTexParameteri(tail_texture.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        
        self.tail = self.batch.add(len(self.tail_segments) * 2, 
                GL_TRIANGLE_STRIP, TailGroup(tail_texture), 
                'v2f', 
                ('t2f', [0, 0, 1, 0, 0, 1, 1, 1] * (len(self.tail_segments)/2)),
                ('c4B', [255, 255, 255, 255] * len(self.tail_segments) * 2))

        # Rendered kite
        kite_image = pyglet.resource.image('kite.png')
        kite_image.anchor_x = kite_image.width / 2
        kite_image.anchor_y = 6
        self.kite = GameSprite(kite_image,
                               x=self.width/2, y=self.height/2,
                               batch=self.batch)

        self.food = []
        self.eaten_food = []
        self.falling_food = []

        self.mouse_x = self.width/2
        self.mouse_y = self.height/2

        self.game_clock.schedule_interval(self.respawn_food, 1.0)

        # Background gradients
        background_vertices = []
        background_colors = []
        y = 0
        for level in levels:
            r, g, b = level.color
            background_vertices.extend((0, y, self.width * 2, y))
            background_colors.extend((r, g, b, 255, r, g, b, 255))
            y += self.height // 2
        self.background_batch = pyglet.graphics.Batch()
        self.background_batch.add(len(levels) * 2, GL_QUAD_STRIP, None,
            ('v2f', background_vertices),
            ('c4B', background_colors)
        )

        self.overlay_batch = pyglet.graphics.Batch()

        self.player = pyglet.media.Player()
        self.music = None

        self.instructor = BaseInstructor()
        self.set_level(0, immediate=True)
        self.begin_menu()
        self.fade_in()

    def set_music(self, music, loop=False):
        if not have_avbin:
            return

        if music == self.music:
            return

        self.player.next()
        self.player = pyglet.media.Player()
        self.player.queue(pyglet.resource.media(music, streaming=True))
        self.player.play()
        self.player.volume = 1.0
        if loop:
            self.player.eos_action = 'loop'
        self.music = music

    def begin_menu(self):
        self.camera_y = 0
        self.camera_x = 600
        self.instructor.delete()
        self.menu = Menu(self)
        self.set_music('music/OMDb.mp3', loop=True)

    def begin_game(self, challenge=False):
        if challenge:
            self.instructor = ChallengeInstructor(self)
        else:
            self.instructor = Instructor(self)
        for level in levels:
            level.reset(challenge=challenge)
        Animator(self.game_clock, 
                 self, 'camera_x', 0, 1.5)
        self.game_clock.schedule_once(lambda dt: self.menu.delete(), 1.5)
    
        # Spawn initial balloon
        self.get_level().spawn(self)

    def fade_out(self):
        Animator(self.game_clock,
                 self, 'fade', 1., 1.0)
        Animator(self.game_clock,
                 self.player, 'volume', 0.0, 1.0)
                 
    def fade_in(self):
        Animator(self.game_clock,
                 self, 'fade', 0., 1.0)
        Animator(self.game_clock,
                 self.player, 'volume', 1.0, 1.0)

    def restart(self):
        self.fade_out()
        def restart_actual(dt):
            if isinstance(self.level, Credits):
                self.level.stop_credits()
            self.set_level(0, immediate=True)
            self.begin_menu()
            for food in self.food:
                food.delete()
            self.food = []
            for food in self.eaten_food:
                food.delete()
            self.eaten_food = []
            for food in self.falling_food:
                food.delete()
            self.falling_food = []
            self.invulnerable = False
            self.kite.color = (255, 255, 255)
            self.fade_in()
        self.game_clock.schedule_once(restart_actual, 1.0)

    def on_expose(self):
        self.invalid = True

    def on_resize(self, width, height):
        super(Window, self).on_resize(width, height)
        pyglet.clock.unschedule(self.update)
        pyglet.clock.schedule_interval(self.update, TIME_SLICE)

    def on_activate(self):
        pyglet.clock.unschedule(self.update)
        pyglet.clock.schedule_interval(self.update, TIME_SLICE)

    def on_deactivate(self):
        pyglet.clock.unschedule(self.update)

    def on_close(self):
        pyglet.clock.unschedule(self.update)
        super(Window, self).on_close()

    def close(self):
        pyglet.clock.unschedule(self.update)
        super(Window, self).close()

    def setup(self):
        glClearColor(1, 1, 1, 1)
        glLineWidth(2)

    def on_draw(self):
        self.invalid = False

        glLoadIdentity()
        glTranslatef(-self.camera_x, -self.camera_y, 0)

        self.background_batch.draw()
        self.batch.draw()
        self.foreground_batch.draw()

        glLoadIdentity()
        self.overlay_batch.draw()

        if self.fade:
            glPushAttrib(GL_CURRENT_BIT | GL_ENABLE_BIT)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(0, 0, 0, self.fade)
            glRectf(0, 0, self.width, self.height)
            glPopAttrib()

    def on_key_press(self, symbol, modifiers):
        global enable_cheats
        if (symbol == key.C and 
            modifiers & key.MOD_CTRL and modifiers & key.MOD_SHIFT):
            enable_cheats = True
        elif symbol == key.SPACE and enable_cheats:
            self.next_level()
        elif symbol == key.W and enable_cheats:
            self.win_game()
        elif symbol == key.BACKSPACE and enable_cheats:
            self.previous_level()
        elif symbol == key.ENTER:
            self.instructor.event('dismiss')
        elif symbol == key.ESCAPE:
            if self.menu is not None:
                self.close()
            else:
                self.dropdown_menu = DropdownMenu(self)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def get_level(self):
        return self.level
        #if 0 <= self.level_index < len(levels):
        #    return levels[self.level_index]

    def set_level(self, level, immediate=False):
        self.level_index = level
        self.level = levels[self.level_index]
        self.get_level().score = 0
        self.level_y = self.level_index * self.height / 2
        if immediate:
            self.camera_y = self.level_y
        else:
            Animator(self.game_clock, 
                     self, 'camera_y', self.level_y, 1.0)

        for i, level in enumerate(levels):
            if -2 <= i - self.level_index <= 2:
                level.load(self, i)
            else:
                level.unload()


    def next_level(self):
        self.set_level(self.level_index + 1)

    def previous_level(self):
        self.invulnerable = True
        self.kite.color = (200, 0, 0)
        self.mouse_active = False
        self.game_clock.schedule_once(self.set_mouse_active, 2.0)
        self.game_clock.schedule_once(self.set_vulnerable, 2.0)

        if self.level_index == 0:
            return

        self.instructor.event('prev_level')
        self.set_level(self.level_index - 1)

    def impact_food(self):
        if isinstance(self.get_level(), Credits):
            return

        self.instructor.event('impact')
        if self.eaten_food:
            self.instructor.event('drop_food')
            n = (len(self.eaten_food) + 1) // 2
            self.falling_food.extend(self.eaten_food[:n])
            del self.eaten_food[:n]

            self.kite.color = (200, 0, 0)
            self.invulnerable = True
            self.mouse_active = False
            self.game_clock.schedule_once(self.set_mouse_active, 2.0)
            self.game_clock.schedule_once(self.set_vulnerable, 2.0)
        else: 
            self.previous_level()

    def eat_food(self, food):
        self.instructor.event('eat_food')
        self.eaten_food.append(food)
        food.color = (100, 100, 100)
        food.staged = False

        # Move anchor point on image to strangle point.
        if not isinstance(food, TextFood):
            food.image = food.image.get_region(
                0, 0, food.image.width, food.image.height)
            food.image.anchor_x = food.strangle_x
            food.image.anchor_y = food.strangle_y

        if isinstance(food, Boy):
            self.win_game()
            return

        level = self.get_level()
        level.eat_food(food)
        if level.is_done:
            self.instructor.event('next_level')
            self.next_level()

    def win_game(self):
        self.fade_out()
        def win_game_actual(dt):
            for level in levels:
                level.unload()
            self.instructor.delete()

            self.food = []
            self.invulnerable = False    
            self.kite.color = (255, 255, 255)
            self.level_index = -1
            self.level = Credits()
            self.level.start_credits(self)
            self.fade_in()
        self.game_clock.schedule_once(win_game_actual, 1.0)

    def set_mouse_active(self, dt=None):
        self.mouse_active = True

    def set_vulnerable(self, dt=None):
        self.invulnerable = False
        self.kite.color = (255, 255, 255)

    def respawn_food(self, dt):
        if self.menu is None:
            level = self.get_level()
            level.spawn(self)

    def update(self, dt):
        self.invalid = True
        self.game_time += TIME_SLICE
        self.game_clock.tick()

        if self.dropdown_menu is not None:
            return

        # Add kite-to-mouse force
        dx = (self.mouse_x + self.camera_x) - self.kite.x
        dy = (self.mouse_y + self.camera_y) - self.kite.y
        if self.mouse_active:
            # Follow mouse
            #self.kite.x += dx * 0.2
            #self.kite.y += dy * 0.1 #0.05
            x, y = self.last_tail_segments[0]
            x += dx * 0.2
            y += dy * 0.1
            self.last_tail_segments[0] = x, y


        # Uniform grid for food.
        grid_rows = 20
        grid_cols = 20
        grid_cell_width = self.width // (grid_cols - 1)
        grid_cell_height = self.height // (grid_rows - 1)
        grid = [[] for i in range(grid_rows * grid_cols)]

        # Move food and put into grid
        for food in self.food:
            food.update(0, self.camera_y, 
                        self.width, self.camera_y + self.height)
            
            if self.invulnerable:
                continue

            grid_x1 = int((food.x - food.radius_x) / grid_cell_width)
            grid_x2 = int((food.x + food.radius_x) / grid_cell_width)
            grid_y1 = int((food.y - food.radius_y - self.camera_y) / 
                            grid_cell_height)
            grid_y2 = int((food.y + food.radius_y - self.camera_y) / 
                            grid_cell_height)
            for grid_x in range(grid_x1, grid_x2 + 1):
                if 0 <= grid_x < grid_cols:
                    for grid_y in range(grid_y1, grid_y2 + 1):
                        if 0 <= grid_y < grid_rows:
                            grid[grid_y * grid_cols + grid_x].append(food)

        ddy =  -500.

        constraint = .4

        for i in range(1, len(self.tail_segments)):
            lx, ly = self.last_tail_segments[i]
            x, y = self.tail_segments[i]

            # verlet
            x = 2 * x - lx # + ddx * dt2    {ddx == 0}
            y = 2 * y - ly + ddy * TIME_SLICE_2
            self.last_tail_segments[i] = (x, y)

        self.tail_segments, self.last_tail_segments = (
            self.last_tail_segments, self.tail_segments)

        for food in self.food:
            food.strangle_bits = 0

        # iterate for relaxation
        for j in range(10):

            # constrain tail 
            ox, oy = self.tail_segments[0]
            for i in range(1, len(self.tail_segments)):
                # distance constraint
                x, y = self.tail_segments[i]
                dx = ox - x
                dy = oy - y
                if dx == 0 and dy == 0:
                    dx = 0.01

                #length = sqrt(dx * dx + dy * dy)
                length = (dx * dx + dy * dy) * 0.25 + 1.0
                diff = (length - constraint) / length
                if i == 1:
                    # rope has little effect on kite
                    x += dx * .90 * diff
                    y += dy * .90 * diff
                    ox -= dx * .1 * diff
                    oy -= dy * .1 * diff
                else:
                    # rope to rope effect
                    x += dx * .5 * diff
                    y += dy * .5 * diff
                    ox -= dx * .5 * diff
                    oy -= dy * .5 * diff

                # Shift prev tail segment.
                self.tail_segments[i-1] = (ox, oy)

                # Get grid cell
                grid_x = int(x / grid_cell_width)
                grid_y = int((y - self.camera_y) / grid_cell_height)
                if 0 <= grid_x < grid_cols and 0 <= grid_y < grid_rows:
                    grid_cell = grid[grid_y * grid_cols + grid_x]
                else:
                    grid_cell = ()

                # collide with food
                for food in grid_cell:
                    ox = food.x
                    oy = food.y
                    dx = (ox - x) / food.radius_x
                    dy = (oy - y) / food.radius_y

                    l2 = dx * dx + dy * dy
                    if l2 < 1.0:
                        # This is what we're calculating:
                        #length = sqrt(l2)
                        #diff = (length - 1) / length
                        
                        # First-order approximation doesn't work well at all
                        # here -- but second order does:
                        #length = l2 * 0.125 - 4.0 / (0.5 * l2 + 2.0) + 2.5
                        
                        # Using an online algebra simplifier, i get:
                        #diff = (l2 - 0.944)*(16.944 + l2)/(
                        #            (0.686 + l2)*(23.313 + l2)) 

                        # But the sqrt() function is still faster according to
                        # timeit :-(
                        length = sqrt(l2)
                        diff = (length - 1) / length

                        x += dx * (1.0 - food.mass_x) * diff * food.radius_x
                        y += dy * (1.0 - food.mass_y) * diff * food.radius_y
                        food.x -= dx * food.mass_x * diff
                        food.y -= dy * food.mass_y * diff
                        food.strangle_i = i

                        if dx > 0.7:
                            food.strangle_bits |= 1
                        if dx < -0.7:
                            food.strangle_bits |= 2
                        if dy > 0.7:
                            food.strangle_bits |= 4
                        if dy < -0.7:
                            food.strangle_bits |= 8

                    
                # collide with ground
                y = max(y, 20)

                # Pass result on to next segment
                ox, oy = x, y

            self.tail_segments[-1] = (ox, oy)

            # fix location of tail end of string
            x, y = self.tail_segments[-1]
            if self.camera_y > 200:
                # ground not seen; constrain tail below camera
                if y > self.camera_y:
                    y = self.camera_y
            else:
                # boy visible, constrain to hand
                x, y = self.boy_position
            if x < 0:
                x = 0
            if x > self.width:
                x = self.width
            self.tail_segments[-1] = x, y

        ox, oy = self.tail_segments[0]
        vertex_data = [ox, oy]
        tail_width = 3
        for x, y in self.tail_segments[1:]:
            # Calculate tangent to this segment
            dy = -(ox - x)
            dx = oy - y
            length = sqrt(dx * dx + dy * dy)
            if length > 0:
                dx *= tail_width / length
                dy *= tail_width / length
            vertex_data.extend((x + dx, y + dy, x - dx, y - dy))
            ox = x
            oy = y
        vertex_data.extend((x, y))

        self.tail.vertices[:] = vertex_data

        self.kite.x, self.kite.y = self.tail_segments[0]

        for food in self.food:
            if food.strangle_bits == 15:
                food.color = (255, 0, 0)
                food.strangle_count += 1
                if food.strangle_count > 2:
                    self.eat_food(food)
            else:
                food.color = (255, 255, 255)
                food.strangle_count = 0

        self.food = [food for food in self.food if food.staged]

        # Move eaten food onto tail
        ddr = 1
        for food in self.eaten_food:
            food.last_x = food.x
            food.last_y = food.y
            food.x, food.y = self.tail_segments[food.strangle_i]

            # Stupidly hacky fake of angular momentum :-)
            food.dr = food.dr * .8 + food.last_x - food.x * .1
            food.rotation = food.strangle_rotation + food.dr * .04

        # Integrate falling food (verlet)
        for food in self.falling_food:
            lx = food.x
            ly = food.y
            food.x = 2 * food.x - food.last_x #+ ddx * TIME_SLICE_2
            food.y = 2 * food.y - food.last_y + ddy * TIME_SLICE_2
            food.last_x = lx
            food.last_y = ly
        self.falling_food = [f for f in self.falling_food \
                               if f.y + f.radius_y > self.camera_y]

        # Kite angle
        x1, y1 = self.tail_segments[1]
        x2, y2 = self.tail_segments[0]
        dx = x2 - x1
        dy = y2 - y1

        # TODO if anal: use dy/dx directly to calculate cos/sin needed
        # by sprite instead of feeding into rotation.  should save on the
        # atan2, cos and sin per frame per rotated sprite
        angle = 90 - degrees(atan2(dy, dx))
        self.kite.rotation = angle

        # Check for kite collision with food
        # Box-box collision because ellipse-ellipse doesn't fit in my brain
        # atm.
        if not self.invulnerable:
            # Find center of kite
            length = sqrt(dx * dx + dy * dy)
            kite_x = x2 + dx * self.kite.radius / length
            kite_y = y2 + dy * self.kite.radius / length

            for food in self.food:
                if not food.dangerous:
                    continue
                dx = kite_x - food.x
                dy = kite_y - food.y
                if dx * dx + dy * dy < self.kite.radius_2 + food.radius_2:
                    # Hit! Push back and go back a level
                    self.impact_food()
                    break

def main():
    window = Window(600, 600, caption='Kite Story')
    window.setup()
    pyglet.app.run()
