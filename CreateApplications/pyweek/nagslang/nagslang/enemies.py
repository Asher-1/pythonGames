import math
import random

import pymunk
import pymunk.pygame_util

from nagslang import render
from nagslang.constants import (
    COLLISION_TYPE_ENEMY, COLLISION_TYPE_FURNITURE, COLLISION_TYPE_SHEEP,
    ACID_SPEED, ACID_DAMAGE, ZORDER_MID)
from nagslang.game_object import (GameObject, SingleShapePhysicser, Result,
                                  Bullet, make_body)
from nagslang.collectable import KeyCard
from nagslang.mutators import FLIP_H
from nagslang.resources import resources
from nagslang.utils import vec_with_length
from nagslang.sound import sound


def get_editable_enemies():
    classes = []
    for cls_name, cls in globals().iteritems():
        if isinstance(cls, type) and issubclass(cls, Enemy):
            if hasattr(cls, 'requires'):
                classes.append((cls_name, cls))
    return classes


def get_alien_image(enemy_type, suffix, *transforms):
    image_name = 'alien_%s_%s.png' % (enemy_type, suffix)
    return resources.get_image('creatures', image_name, transforms=transforms)


class Enemy(GameObject):
    """A base class for mobile enemies"""
    zorder = ZORDER_MID
    enemy_type = None  # Which set of images to use
    enemy_damage = None
    health = None
    impulse_factor = None
    random_move_time = 0.3

    def __init__(self, space, world, position):
        super(Enemy, self).__init__(
            self.make_physics(space, position), self.make_renderer())
        self.world = world
        self.angle = 0
        self.add_timer('random_move', self.random_move_time)
        self._last_random_direction = (0, 0)

    def make_physics(self, space, position):
        raise NotImplementedError

    def make_renderer(self):
        return render.FacingSelectionRenderer({
            'left': render.TimedAnimatedRenderer(
                [get_alien_image(self.enemy_type, '1'),
                 get_alien_image(self.enemy_type, '2')], 3),
            'right': render.TimedAnimatedRenderer(
                [get_alien_image(self.enemy_type, '1', FLIP_H),
                 get_alien_image(self.enemy_type, '2', FLIP_H)], 3),
        })

    def get_render_angle(self):
        # No image rotation when rendering, please.
        return 0

    def get_facing_direction(self):
        # Enemies can face left or right.
        if - math.pi / 2 < self.angle <= math.pi / 2:
            return 'right'
        else:
            return 'left'

    def hit(self, weapon):
        self.lose_health(weapon.damage)

    def lose_health(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.world.kills += 1
            self.physicser.remove_from_space()

    def set_direction(self, dx, dy, force_factor=1):
        vec = vec_with_length((dx, dy), self.impulse_factor * force_factor)
        self.angle = vec.angle
        self.physicser.apply_impulse(vec)

    def collide_with_protagonist(self, protagonist):
        if self.enemy_damage is not None:
            protagonist.lose_health(self.enemy_damage)

    def collide_with_claw_attack(self, claw_attack):
        self.lose_health(claw_attack.damage)

    def range_to_visible_protagonist(self):
        """Get a vector to the protagonist if there are no barriers in between.

        Returns a vector to the protagonist if she is within line of sight,
        otherwise `None`
        """

        pos = self.physicser.position
        target = self.world.protagonist.get_shape().body.position

        for collision in self.get_space().segment_query(pos, target):
            shape = collision.shape
            if (shape in (self.get_shape(), self.world.protagonist.get_shape())
                    or shape.sensor):
                continue
            return None
        return target - pos

    def ranged_attack(self, range_, speed, damage, type_, reload_time, result):
        vec = self.range_to_visible_protagonist()
        if vec is None:
            return

        if not self.check_timer('reload_time'):
            self.start_timer('reload_time', reload_time)
            if vec.length < range_:
                vec.length = speed
                result.add += (Bullet(
                    self.get_space(), self.physicser.position, vec, damage,
                    type_, COLLISION_TYPE_ENEMY,
                    "mouth_pop_2a.ogg"),)

    def greedy_move(self, target):
        """Simple greedy path finder"""
        def _calc_step(tp, pp):
            step = 0
            if (tp < pp):
                step = max(-1, tp - pp)
            elif (tp > pp):
                step = min(1, tp - pp)
            if abs(step) < 0.5:
                step = 0
            return step
        x_step = _calc_step(target[0], self.physicser.position[0])
        y_step = _calc_step(target[1], self.physicser.position[1])
        return (x_step, y_step)

    def random_move(self):
        """Random move"""
        if not self.check_timer('random_move'):
            self.start_timer('random_move')
            self._last_random_direction = (
                random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        return self._last_random_direction

    def attack(self, result):
        pass

    def move(self, result):
        pass

    def update(self, dt):
        super(Enemy, self).update(dt)
        result = Result()
        if self.health <= 0:
            result.remove += (self,)
            result.add += (DeadEnemy(self.get_space(), self.world,
                                     self.physicser.position,
                                     self.enemy_type),)
            self.play_death_sound()
        self.move(result)
        self.attack(result)
        return result

    def play_death_sound(self):
        sound.play_sound("synth_detuned1.ogg")

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates")]


class DeadEnemy(GameObject):
    def __init__(self, space, world, position, enemy_type='A'):
        body = make_body(10, 10000, position, damping=0.5)
        self.shape = pymunk.Poly(
            body, [(-20, -20), (20, -20), (20, 20), (-20, 20)])
        self.shape.friction = 0.5
        self.shape.collision_type = COLLISION_TYPE_FURNITURE
        super(DeadEnemy, self).__init__(
            SingleShapePhysicser(space, self.shape),
            render.ImageRenderer(resources.get_image(
                'creatures', 'alien_%s_dead.png' % enemy_type)),
        )

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates")]


class PatrollingAlien(Enemy):
    is_moving = True  # Always walking.
    enemy_type = 'A'
    health = 42
    enemy_damage = 15
    impulse_factor = 50

    def __init__(self, space, world, position, end_position):
        # An enemy that patrols between the two points
        super(PatrollingAlien, self).__init__(space, world, position)
        self._start_pos = position
        self._end_pos = end_position
        self._direction = 'away'

    def make_physics(self, space, position):
        body = make_body(10, pymunk.inf, position, 0.8)
        shape = pymunk.Circle(body, 30)
        shape.elasticity = 1.0
        shape.friction = 0.05
        shape.collision_type = COLLISION_TYPE_ENEMY
        return SingleShapePhysicser(space, shape)

    def _switch_direction(self):
        if self._direction == 'away':
            self._direction = 'towards'
        else:
            self._direction = 'away'

    def move(self, result):
        if self._direction == 'away':
            target = self._end_pos
        else:
            target = self._start_pos
        x_step, y_step = self.greedy_move(target)
        if abs(x_step) < 1 and abs(y_step) < 1:
            self._switch_direction()
        self.set_direction(x_step, y_step)

    def attack(self, result):
        self.ranged_attack(300, ACID_SPEED, ACID_DAMAGE, 'acid', 0.2, result)

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("end_position", "coordinates")]


class ChargingAlien(Enemy):
    # Simplistic charging of the protagonist
    is_moving = False
    enemy_type = 'B'
    health = 42
    enemy_damage = 20
    impulse_factor = 300

    def __init__(self, space, world, position, attack_range=100):
        super(ChargingAlien, self).__init__(space, world, position)
        self._range = attack_range

    def make_physics(self, space, position):
        body = make_body(100, pymunk.inf, position, 0.8)
        shape = pymunk.Circle(body, 30)
        shape.elasticity = 1.0
        shape.friction = 0.05
        shape.collision_type = COLLISION_TYPE_ENEMY
        return SingleShapePhysicser(space, shape)

    def move(self, result):
        pos = self.physicser.position
        target = self.world.protagonist.get_shape().body.position
        if pos.get_distance(target) > self._range:
            # stop
            self.is_moving = False
            return 0, 0
        self.is_moving = True
        dx, dy = self.greedy_move(target)
        self.set_direction(dx, dy)

    def attack(self, result):
        self.ranged_attack(300, ACID_SPEED, ACID_DAMAGE, 'acid', 0.2, result)

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("attack_range", "distance")]


class RunAndGunAlien(ChargingAlien):
    # Simplistic shooter
    # Move until we're in range, and then randomly
    enemy_type = "C"
    impulse_factor = 90
    health = 42
    enemy_damage = 25
    is_moving = True

    def make_physics(self, space, position):
        body = make_body(10, pymunk.inf, position, 0.8)
        shape = pymunk.Circle(body, 30)
        shape.elasticity = 1.0
        shape.friction = 0.05
        shape.collision_type = COLLISION_TYPE_ENEMY
        return SingleShapePhysicser(space, shape)

    def move(self, result):
        pos = self.physicser.position
        target = self.world.protagonist.get_shape().body.position
        if pos.get_distance(target) < self._range:
            step = self.random_move()
        else:
            step = self.greedy_move(target)
        self.set_direction(*step)

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("attack_range", "distance")]


class Queen(RunAndGunAlien):
    enemy_type = "queen"
    impulse_factor = 180
    health = 500
    enemy_damage = 50
    is_moving = True
    spawn_time = 10
    spawn_size = 5
    spawn_class = ChargingAlien
    spawn_class_args = (400,)

    def __init__(self, space, world, position, attack_range=100):
        super(Queen, self).__init__(space, world, position, attack_range)
        self.add_timer('spawn', self.spawn_time)

    def spawn(self, result):
        if not self.check_timer('spawn'):
            self.start_timer('spawn', self.spawn_time)
            for i in range(self.spawn_size):
                result.add += (self.spawn_class(self.get_space(),
                self.world, self.physicser.position,
                *self.spawn_class_args),)

    def attack(self, result):
        self.ranged_attack(300, ACID_SPEED, ACID_DAMAGE, 'acid', 1, result)

    def update(self, dt):
        result = super(Queen, self).update(dt)
        self.spawn(result)
        if (self.health <= 0
                and not self.world.protagonist.has_item('keycard_cyan')):
            result.add += (KeyCard(self.get_space(),
                                   self.physicser.position, 'keycard_cyan'),)
        return result

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("attack_range", "distance")]


class Sheep(Enemy):  # Only because we don't have a DeliciousCreature class.
    is_moving = True  # Always walking.
    enemy_type = 'sheep'
    health = 10
    impulse_factor = 50

    human_vision_range = 100
    wolf_vision_range = 200

    def make_physics(self, space, position):
        body = make_body(10, pymunk.inf, position, 0.8)
        shape = pymunk.Circle(body, 20)
        shape.elasticity = 1.0
        shape.friction = 0.05
        shape.collision_type = COLLISION_TYPE_SHEEP
        return SingleShapePhysicser(space, shape)

    def move(self, result):
        vec = self.range_to_visible_protagonist()
        prot = self.world.protagonist
        if vec is not None:
            if prot.in_human_form() and vec.length < self.human_vision_range:
                self.set_direction(vec.x, vec.y, 1.5)
                return
            if prot.in_wolf_form() and vec.length < self.wolf_vision_range:
                vec = -vec
                self.set_direction(vec.x, vec.y, 3)
                return
        self.set_direction(*self.random_move())

    def play_death_sound(self):
        sound.play_sound("eviltoy1.ogg")

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates")]
