import math

import pymunk
import pymunk.pygame_util

from nagslang import render
from nagslang.constants import (
    COLLISION_TYPE_PLAYER, ZORDER_MID, WEREWOLF_SOAK_FACTOR,
    PROTAGONIST_HEALTH_MIN_LEVEL, PROTAGONIST_HEALTH_MAX_LEVEL,
    NON_GAME_OBJECT_COLLIDERS, BULLET_DAMAGE, BULLET_SPEED, CLAW_DAMAGE,
    CMD_TOGGLE_FORM, CMD_ACTION)
from nagslang.game_object import (
    GameObject, Physicser, Result, Bullet, ClawAttack, EphemeralNote,
    make_body)
from nagslang.mutators import FLIP_H
from nagslang.resources import resources
from nagslang.events import AddDrawableEvent, DeathEvent
from nagslang.utils import vec_from_angle, vec_with_length


class ProtagonistPhysicser(Physicser):
    def __init__(self, space, form_shapes):
        self._space = space
        self._form_shapes = form_shapes
        for shape in form_shapes.values():
            shape.physicser = self

    def switch_form(self, old_form, new_form):
        self._space.remove(self._form_shapes[old_form])
        shape = self._form_shapes[new_form]
        self._space.add(shape)
        for attr, value in shape.protagonist_body_props.iteritems():
            setattr(shape.body, attr, value)

    def get_shape(self):
        return self._form_shapes[self.game_object.form]


class ProtagonistFormSelectionRenderer(render.RendererSelectionRenderer):
    def select_renderer(self):
        return self.game_object.form


def _make_change_sequence(old, new):
    return (
        new, new, old, old, old, old,
        new, new, old, old, old,
        new, new, old, old,
        new, new, new, old, old,
        new, new, new, new, old, old,
        new)


class Protagonist(GameObject):
    """Representation of our fearless protagonist.

    TODO: Factor out a bunch of this stuff when we need it for other objects.
    """

    HUMAN_FORM = 'human'
    WOLF_FORM = 'wolf'

    CHANGING_SEQUENCE = {
        # The key is the form we're changing *from*.
        HUMAN_FORM: _make_change_sequence(HUMAN_FORM, WOLF_FORM),
        WOLF_FORM: _make_change_sequence(WOLF_FORM, HUMAN_FORM),
    }

    zorder = ZORDER_MID

    def __init__(self, space, world, position):
        self.form = self.HUMAN_FORM
        super(Protagonist, self).__init__(
            self._make_physics(space, position), self._make_renderer())
        self.world = world
        self.health_level = PROTAGONIST_HEALTH_MAX_LEVEL

        self.angle = 0
        self.is_moving = False
        self.changing_sequence = []
        self.add_timer('attack_cooldown', 0.2)
        self.add_timer('change_delay', 0.1)

        self.go_human()

    def _make_physics(self, space, position):
        body = make_body(10, pymunk.inf, position, 0.8)
        body.velocity_limit = 1000

        human = pymunk.Poly(body, [(-15, -30), (15, -30), (15, 30), (-15, 30)])
        human.elasticity = 1.0
        human.collision_type = COLLISION_TYPE_PLAYER
        human.protagonist_body_props = {
            'mass': 10,
            'damping': 0.8,
        }

        wolf = pymunk.Circle(body, 30)
        wolf.elasticity = 1.0
        wolf.collision_type = COLLISION_TYPE_PLAYER
        wolf.protagonist_body_props = {
            'mass': 100,
            'damping': 0.9,
        }

        return ProtagonistPhysicser(space, {
            self.HUMAN_FORM: human,
            self.WOLF_FORM: wolf,
        })

    def _get_image(self, name, *transforms):
        return resources.get_image('creatures', name, transforms=transforms)

    def change_space(self, new_space):
        self.physicser.remove_from_space()
        self.physicser.set_space(new_space)
        self.physicser.add_to_space()

    def reset(self):
        self.health_level = PROTAGONIST_HEALTH_MAX_LEVEL
        self.is_moving = False

        self.go_human()

    def _make_renderer(self):
        return ProtagonistFormSelectionRenderer({
            self.HUMAN_FORM: render.FacingSelectionRenderer(
                {
                    'N': render.MovementAnimatedRenderer(
                        [self._get_image('human_N_1.png'),
                         self._get_image('human_N_2.png')], 3),
                    'S': render.MovementAnimatedRenderer(
                        [self._get_image('human_S_1.png'),
                         self._get_image('human_S_2.png')], 3),
                    'W': render.MovementAnimatedRenderer(
                        [self._get_image('human_W_1.png'),
                         self._get_image('human_W_2.png')], 3),
                    'E': render.MovementAnimatedRenderer(
                        [self._get_image('human_W_1.png', FLIP_H),
                         self._get_image('human_W_2.png', FLIP_H)], 3),
                    'NW': render.MovementAnimatedRenderer(
                        [self._get_image('human_NW_1.png'),
                         self._get_image('human_NW_2.png')], 3),
                    'NE': render.MovementAnimatedRenderer(
                        [self._get_image('human_NW_1.png', FLIP_H),
                         self._get_image('human_NW_2.png', FLIP_H)], 3),
                    'SW': render.MovementAnimatedRenderer(
                        [self._get_image('human_SW_1.png'),
                         self._get_image('human_SW_2.png')], 3),
                    'SE': render.MovementAnimatedRenderer(
                        [self._get_image('human_SW_1.png', FLIP_H),
                         self._get_image('human_SW_2.png', FLIP_H)], 3),
                }),
            self.WOLF_FORM: render.FacingSelectionRenderer(
                {
                    'N': render.MovementAnimatedRenderer(
                        [self._get_image('werewolf_N_1.png'),
                         self._get_image('werewolf_N_2.png')], 3),
                    'S': render.MovementAnimatedRenderer(
                        [self._get_image('werewolf_S_1.png'),
                         self._get_image('werewolf_S_2.png')], 3),
                    'W': render.MovementAnimatedRenderer(
                        [self._get_image('werewolf_W_1.png'),
                         self._get_image('werewolf_W_2.png')], 3),
                    'E': render.MovementAnimatedRenderer(
                        [self._get_image('werewolf_W_1.png', FLIP_H),
                         self._get_image('werewolf_W_2.png', FLIP_H)], 3),
                    'NW': render.MovementAnimatedRenderer(
                        [self._get_image('werewolf_NW_1.png'),
                         self._get_image('werewolf_NW_2.png')], 3),
                    'NE': render.MovementAnimatedRenderer(
                        [self._get_image('werewolf_NW_1.png', FLIP_H),
                         self._get_image('werewolf_NW_2.png', FLIP_H)], 3),
                    'SW': render.MovementAnimatedRenderer(
                        [self._get_image('werewolf_SW_1.png'),
                         self._get_image('werewolf_SW_2.png')], 3),
                    'SE': render.MovementAnimatedRenderer(
                        [self._get_image('werewolf_SW_1.png', FLIP_H),
                         self._get_image('werewolf_SW_2.png', FLIP_H)], 3),
                }),
        })

    @classmethod
    def from_saved_state(cls, saved_state):
        """Create an instance from the provided serialised state.
        """
        obj = cls()
        # TODO: Update from saved state.
        return obj

    def handle_attack_key_down(self):
        if self.changing_sequence:
            self.fire_note(
                "You can't do anything until your form has stabilised.")
            return
        if self.check_timer('attack_cooldown'):
            return
        self.start_timer('attack_cooldown')
        self.world.attacks += 1
        return self.attack()

    def handle_keypress(self, key_command):
        if self.changing_sequence:
            self.fire_note(
                "You can't do anything until your form has stabilised.")
        if key_command == CMD_TOGGLE_FORM:
            self.world.transformations += 1
            self.toggle_form()
        if key_command == CMD_ACTION:
            self.perform_action()

    def get_render_angle(self):
        # No image rotation when rendering, please.
        return 0

    def get_facing_direction(self):
        # Our angle is quantised to 45 degree intervals, so possible values for
        # x and y in a unit vector are +/-(0, sqrt(2)/2, 1) with some floating
        # point imprecision. Rounding will normalise these to (-1.0, 0.0, 1.0)
        # which we can safely turn into integers and use as dict keys.
        vec = vec_from_angle(self.angle)
        x = int(round(vec.x))
        y = int(round(vec.y))

        return {
            (0, 1): 'N',
            (0, -1): 'S',
            (-1, 0): 'W',
            (1, 0): 'E',
            (1, 1): 'NE',
            (1, -1): 'SE',
            (-1, 1): 'NW',
            (-1, -1): 'SW',
        }[(x, y)]

    def go_werewolf(self):
        self.physicser.switch_form(self.form, self.WOLF_FORM)
        self.form = self.WOLF_FORM
        self.impulse_factor = 4000

    def go_human(self):
        self.physicser.switch_form(self.form, self.HUMAN_FORM)
        self.form = self.HUMAN_FORM
        self.impulse_factor = 500

    def set_direction(self, dx, dy):
        if (dx, dy) == (0, 0) or self.changing_sequence:
            self.is_moving = False
            return
        self.is_moving = True
        vec = vec_with_length((dx, dy), self.impulse_factor)
        self.angle = vec.angle
        self.physicser.apply_impulse(vec)

    def set_position(self, position):
        self.physicser.position = position

    def copy_state(self, old_protagonist):
        self.physicser.position = old_protagonist.physicser.position
        self.physicser.switch_form(self.form, old_protagonist.form)
        self.impulse_factor = old_protagonist.impulse_factor
        self.form = old_protagonist.form
        self.angle = old_protagonist.angle

    def toggle_form(self):
        if self.check_timer('change_delay'):
            return
        self.changing_sequence.extend(self.CHANGING_SEQUENCE[self.form])

    def _go_to_next_form(self):
        if self.changing_sequence.pop(0) == self.WOLF_FORM:
            self.go_werewolf()
        else:
            self.go_human()

    def get_current_interactible(self):
        for shape in self.get_space().shape_query(self.get_shape()):
            if shape.collision_type in NON_GAME_OBJECT_COLLIDERS:
                # No game object here.
                continue
            interactible = shape.physicser.game_object.interactible
            if interactible is not None:
                return interactible
        return None

    def perform_action(self):
        """Perform an action on the target.
        """
        interactible = self.get_current_interactible()
        if interactible is None:
            # Nothing to interact with.
            return
        action = interactible.select_action(self)
        if action is None:
            # Nothing to do with it.
            return
        return action.perform(self)

    def attack(self):
        """Attempt to hurt something.
        """
        if self.in_wolf_form():
            return self.claw()
        else:
            return self.shoot()

    def shoot(self):
        if not self.has_item('gun'):
            self.fire_note('You are not armed.')
            return
        vec = vec_from_angle(self.angle, BULLET_SPEED)
        return Result(add=(Bullet(self.get_space(), self.physicser.position,
                                  vec, BULLET_DAMAGE, 'bullet',
                                  COLLISION_TYPE_PLAYER,
                                  "vocoder2_short.ogg"),))

    def claw(self):
        claw_range = (math.sqrt(math.pow(self.physicser.get_velocity()[0], 2) +
                                math.pow(self.physicser.get_velocity()[1], 2))
                      / 20) + 30
        vec = vec_from_angle(self.angle, claw_range)
        return Result(add=(ClawAttack(
            self.get_space(), self.physicser.position, vec, CLAW_DAMAGE),))

    def in_wolf_form(self):
        return self.form == self.WOLF_FORM

    def in_human_form(self):
        return self.form == self.HUMAN_FORM

    def has_item(self, item):
        return item in self.world.inventory

    def add_item(self, item):
        self.world.inventory.add(item)

    def get_health_level(self):
        """Return current health level
        """
        return self.health_level

    def hit(self, weapon):
        '''Recieve an attack'''
        self.lose_health(weapon.damage)

    def die(self):
        # Handle player death - may be called due to other reasons
        # than zero health
        self.reset()
        DeathEvent.post()

    def lose_health(self, amount):
        if self.in_human_form():
            self.health_level -= amount
        else:
            self.health_level -= amount / WEREWOLF_SOAK_FACTOR
        if self.health_level <= PROTAGONIST_HEALTH_MIN_LEVEL:
            self.die()

    def gain_health(self, amount):
        self.health_level += amount
        if self.health_level > PROTAGONIST_HEALTH_MAX_LEVEL:
            self.health_level = PROTAGONIST_HEALTH_MAX_LEVEL

    def _decrement_timer(self, timer, dt):
        if self._timers[timer] > 0:
            self._timers[timer] -= dt
        if self._timers[timer] < 0:
            self._timers[timer] = 0

    def update(self, dt):
        if self.changing_sequence:
            self._go_to_next_form()
        if int(self.lifetime + dt) > int(self.lifetime):
            if self.in_wolf_form():
                self.gain_health(2)
        super(Protagonist, self).update(dt)

    def force_wolf_form(self):
        if self.in_human_form() and not self.changing_sequence:
            self.toggle_form()
        self.start_timer('change_delay')

    def fire_note(self, msg, secs=1):
        AddDrawableEvent.post(EphemeralNote(msg, secs))
