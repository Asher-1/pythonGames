import pymunk
import pymunk.pygame_util

import math

from nagslang import environment
from nagslang import puzzle
from nagslang import render
from nagslang.mutators import FLIP_H, ImageOverlay, rotator, scaler
from nagslang.constants import (
    COLLISION_TYPE_DOOR, COLLISION_TYPE_FURNITURE, COLLISION_TYPE_PROJECTILE,
    COLLISION_TYPE_SWITCH, COLLISION_TYPE_SHEEP, COLLISION_TYPE_SHEEP_PEN,
    COLLISION_TYPE_WEREWOLF_ATTACK, SWITCH_PUSHERS, ZORDER_FLOOR, ZORDER_LOW,
    ZORDER_HIGH)
from nagslang.resources import resources
from nagslang.events import DoorEvent, QuitEvent
from nagslang.sound import sound


class Result(object):
    '''
    Return from an update() function, to add new objects to the world, and/or
    remove old objects.
    '''
    def __init__(self, add=(), remove=()):
        self.add = add
        self.remove = remove

    def merge(self, result):
        if result is not None:
            self.add += result.add
            self.remove += result.remove
        return self


def get_editable_game_objects():
    classes = []
    for cls_name, cls in globals().iteritems():
        if isinstance(cls, type) and hasattr(cls, 'requires'):
            classes.append((cls_name, cls))
    return classes


class Physicser(object):
    def __init__(self, space):
        self._space = space

    def get_space(self):
        return self._space

    def set_space(self, new_space):
        self._space = new_space

    def set_game_object(self, game_object):
        self.game_object = game_object

    def get_shape(self):
        raise NotImplementedError()

    def add_to_space(self):
        shape = self.get_shape()
        self.get_space().add(shape)
        if not shape.body.is_static:
            self.get_space().add(shape.body)

    def remove_from_space(self):
        shape = self.get_shape()
        self.get_space().remove(shape)
        if not shape.body.is_static:
            self.get_space().remove(shape.body)

    def get_render_position(self, surface):
        pos = self.get_shape().body.position
        return pymunk.pygame_util.to_pygame(pos, surface)

    def get_angle(self):
        return self.get_shape().body.angle

    def get_velocity(self):
        return self.get_shape().body.velocity

    def _get_position(self):
        return self.get_shape().body.position

    def _set_position(self, position):
        self.get_shape().body.position = position

    position = property(_get_position, _set_position)

    def apply_impulse(self, j, r=(0, 0)):
        return self.get_shape().body.apply_impulse(j, r)


class SingleShapePhysicser(Physicser):
    def __init__(self, space, shape):
        super(SingleShapePhysicser, self).__init__(space)
        self._shape = shape
        shape.physicser = self

    def get_shape(self):
        return self._shape


class MultiShapePhysicser(Physicser):
    def __init__(self, space, shape, *extra_shapes):
        super(MultiShapePhysicser, self).__init__(space)
        self._shape = shape
        self._extra_shapes = extra_shapes
        shape.physicser = self
        for es in extra_shapes:
            es.physicser = self

    def get_shape(self):
        return self._shape

    def add_to_space(self):
        shape = self.get_shape()
        self.get_space().add(shape)
        if not shape.body.is_static:
            self.get_space().add(shape.body)
        for s in self._extra_shapes:
            self.get_space().add(s)

    def remove_from_space(self):
        shape = self.get_shape()
        self.get_space().remove(shape)
        if not shape.body.is_static:
            self.get_space().remove(shape.body)
        for s in self._extra_shapes:
            self.get_space().remove(s)


def damping_velocity_func(body, gravity, damping, dt):
    """Apply custom damping to this body's velocity.
    """
    damping = getattr(body, 'damping', damping)
    return pymunk.Body.update_velocity(body, gravity, damping, dt)


def make_body(mass, moment, position, damping=None):
    body = pymunk.Body(mass, moment)
    body.position = tuple(position)
    if damping is not None:
        body.damping = damping
        body.velocity_func = damping_velocity_func
    return body


class GameObject(object):
    """A representation of a thing in the game world.

    This has a rendery thing, physicsy things and maybe some other things.
    """

    zorder = ZORDER_LOW
    is_moving = False  # `True` if a movement animation should play.

    def __init__(self, physicser, renderer, puzzler=None, overlay=None,
                 interactible=None):
        self.lifetime = 0
        self.physicser = physicser
        if physicser is not None:
            physicser.set_game_object(self)
            self.physicser.add_to_space()
        self.renderer = renderer
        renderer.set_game_object(self)
        self.puzzler = puzzler
        if puzzler is not None:
            puzzler.set_game_object(self)
        self.overlay = overlay
        if overlay is not None:
            self.overlay.set_game_object(self)
        self.interactible = interactible
        if interactible is not None:
            self.interactible.set_game_object(self)
        self._timers = {}
        self._active_timers = {}

    def add_timer(self, name, secs):
        self._timers[name] = secs

    def start_timer(self, name, secs=None):
        if secs is None:
            secs = self._timers[name]
        self._active_timers[name] = secs

    def check_timer(self, name):
        return name in self._active_timers

    def set_stored_state_dict(self, stored_state):
        """Override this to set up whatever state storage you want.

        The `stored_state` dict passed in contains whatever saved state we
        might have for this object. If the return value of this method
        evaluates to `True`, the contents of the `stored_state` dict will be
        saved, otherwise it will be discarded.
        """
        pass

    def get_space(self):
        return self.physicser.get_space()

    def get_shape(self):
        return self.physicser.get_shape()

    def get_render_position(self, surface):
        return self.physicser.get_render_position(surface)

    def get_render_angle(self):
        return self.physicser.get_angle()

    def get_facing_direction(self):
        """Used by rendererd that care what direction an object is facing.
        """
        return None

    def render(self, surface):
        return self.renderer.render(surface)

    def update(self, dt):
        self.lifetime += dt
        for timer in self._active_timers.keys():
            self._active_timers[timer] -= dt
            if self._active_timers[timer] <= 0:
                self._active_timers.pop(timer)
        self.renderer.update(dt)

    def hit(self, weapon):
        '''Was hit with a weapon (such as a bullet)'''
        pass

    def collide_with_protagonist(self, protagonist):
        """Called as a `pre_solve` collision callback with the protagonist.

        You can return `False` to ignore the collision, anything else
        (including `None`) to process the collision as normal.
        """
        return True

    def collide_with_furniture(self, furniture):
        return True

    def collide_with_claw_attack(self, claw_attack):
        return True

    def environmental_movement(self, vec):
        self.physicser.apply_impulse(vec)

    @classmethod
    def requires(cls):
        """Hints for the level editor"""
        return [("name", "string")]

    @classmethod
    def movable(cls):
        # Are we movable
        hints = cls.requires()
        for x in hints:
            if 'position' in x:
                return True
        return False


class FloorSwitch(GameObject):
    zorder = ZORDER_FLOOR

    def __init__(self, space, position):
        body = make_body(None, None, position)
        self.shape = pymunk.Circle(body, 30)
        self.shape.collision_type = COLLISION_TYPE_SWITCH
        self.shape.sensor = True
        super(FloorSwitch, self).__init__(
            SingleShapePhysicser(space, self.shape),
            render.ImageStateRenderer({
                True: resources.get_image('objects', 'sensor_on.png'),
                False: resources.get_image('objects', 'sensor_off.png'),
            }),
            puzzle.CollidePuzzler(*SWITCH_PUSHERS),
        )

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates")]


class Note(GameObject):
    zorder = ZORDER_FLOOR

    def __init__(self, space, position, message):
        body = make_body(None, None, position)
        self.shape = pymunk.Circle(body, 30)
        self.shape.sensor = True
        super(Note, self).__init__(
            SingleShapePhysicser(space, self.shape),
            render.ImageRenderer(resources.get_image('objects', 'note.png')),
            puzzle.CollidePuzzler(),
            render.TextOverlay(message),
        )

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("message", "text")]


class EphemeralNote(GameObject):
    def __init__(self, message, timeout, **kwargs):
        kwargs.setdefault('bg_colour', (255, 180, 180, 192))
        super(EphemeralNote, self).__init__(
            None,
            render.NullRenderer(),
            puzzle.YesPuzzler(),
            render.TextOverlay(message, **kwargs),
        )
        self.add_timer('timeout', timeout)
        self.start_timer('timeout')

    def update(self, dt):
        super(EphemeralNote, self).update(dt)
        if not self.check_timer('timeout'):
            return Result(remove=[self])


class SplashImage(GameObject):
    def __init__(self, image, timeout):
        super(SplashImage, self).__init__(
            None,
            render.NullRenderer(),
            puzzle.YesPuzzler(),
            render.ImageOverlay(image),
        )
        self.add_timer('timeout', timeout)
        self.start_timer('timeout')

    def update(self, dt):
        super(SplashImage, self).update(dt)
        if not self.check_timer('timeout'):
            return Result(remove=[self])


class FloorLight(GameObject):
    zorder = ZORDER_FLOOR

    def __init__(self, space, position, state_source):
        body = make_body(None, None, position)
        self.shape = pymunk.Circle(body, 10)
        self.shape.collision_type = COLLISION_TYPE_SWITCH
        self.shape.sensor = True
        super(FloorLight, self).__init__(
            SingleShapePhysicser(space, self.shape),
            render.ImageStateRenderer({
                True: resources.get_image('objects', 'light_on.png'),
                False: resources.get_image('objects', 'light_off.png'),
            }),
            puzzle.StateProxyPuzzler(state_source),
        )

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("state_source", "puzzler")]


class Box(GameObject):
    def __init__(self, space, position):
        body = make_body(10, 10000, position, damping=0.5)
        self.shape = pymunk.Poly(
            body, [(-20, -20), (20, -20), (20, 20), (-20, 20)])
        self.shape.friction = 0.5
        self.shape.collision_type = COLLISION_TYPE_FURNITURE
        super(Box, self).__init__(
            SingleShapePhysicser(space, self.shape),
            render.ImageRenderer(resources.get_image('objects', 'crate.png')),
        )

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("state_source", "puzzler")]


class SokoBox(GameObject):
    def __init__(self, space, position):
        body = make_body(5, pymunk.inf, position, 0.1)
        self.shape = pymunk.Poly(
            body, [(-40, -40), (40, -40), (40, 40), (-40, 40)])
        self.shape.friction = 2.0
        self.shape.collision_type = COLLISION_TYPE_FURNITURE
        super(SokoBox, self).__init__(
            SingleShapePhysicser(space, self.shape),
            render.ImageRenderer(
                resources.get_image('objects', 'sokobox.png')),
        )

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("state_source", "puzzler")]


class BaseDoor(GameObject):
    zorder = ZORDER_FLOOR
    is_open = True

    def __init__(self, space, position, destination, dest_pos, angle,
                 renderer, condition):
        body = make_body(pymunk.inf, pymunk.inf, position, damping=0.5)
        self.shape = pymunk.Circle(body, 30)
        self.shape.collision_type = COLLISION_TYPE_DOOR
        self.shape.body.angle = float(angle) / 180 * math.pi
        self.shape.sensor = True
        self.destination = destination
        self.dest_pos = tuple(dest_pos)
        super(BaseDoor, self).__init__(
            SingleShapePhysicser(space, self.shape),
            renderer,
            puzzle.ParentAttrPuzzler('is_open'),
            interactible=environment.Interactible(
                environment.Action(self._post_door_event, condition)),
        )

    def _post_door_event(self, protagonist):
        self.door_opened()
        DoorEvent.post(self.destination, self.dest_pos)

    def door_opened(self):
        sound.play_sound('robotstep2.ogg')


class Door(BaseDoor):

    image_name = "door.png"

    def __init__(self, space, position, destination, dest_pos, angle):
        super(Door, self).__init__(
            space, position, destination, dest_pos, angle,
            render.ImageRenderer(
                resources.get_image('objects', self.image_name)),
            environment.YesCondition(),
        )

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("destination", "level name"), ("dest_pos", "coordinate"),
                ("angle", "degrees")]


class RestartGameDoor(Door):
    def _post_door_event(self, protagonist):
        protagonist.world.reset()
        super(RestartGameDoor, self)._post_door_event(protagonist)


class ContinueGameDoor(Door):
    def _post_door_event(self, protagonist):
        world = protagonist.world
        if world.level[0]:
            DoorEvent.post(world.level[0], world.level[1])
        else:
            # New game?
            super(ContinueGameDoor, self)._post_door_event(protagonist)


class RocketConsole(Door):

    image_name = "rocket_console.png"

    def _post_door_event(self, protagonist):
        QuitEvent.post()


def make_overlay_image(image_name, angle):
    transforms = ()
    if angle != 0:
        transforms = (rotator(-angle),)
    return resources.get_image('objects', image_name, transforms=transforms)


class PuzzleDoor(BaseDoor):
    def __init__(self, space, position, destination, dest_pos, angle,
                 key_state):
        self._key_state = key_state
        overlay = ImageOverlay(make_overlay_image('lock.png', angle))
        super(PuzzleDoor, self).__init__(
            space, position, destination, dest_pos, angle,
            render.ImageStateRenderer({
                True: resources.get_image('objects', 'door.png'),
                False: resources.get_image(
                    'objects', 'door.png', transforms=(overlay,)),
            }),
            environment.FunctionCondition(lambda p: self.is_open),
        )

    @property
    def is_open(self):
        if self._stored_state['is_open']:
            return True
        return self.puzzler.glue.get_state_of(self._key_state)

    def door_opened(self):
        self._stored_state['is_open'] = True
        super(PuzzleDoor, self).door_opened()

    def set_stored_state_dict(self, stored_state):
        self._stored_state = stored_state
        self._stored_state.setdefault('is_open', False)
        return True

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("destination", "level name"), ("dest_pos", "coordinate"),
                ("angle", "degrees"),
                ("key_state", "puzzler")]


class KeyedDoor(BaseDoor):
    def __init__(self, space, position, destination, dest_pos, angle,
                 key_item=None):
        self._key_item = key_item
        overlay = ImageOverlay(
            make_overlay_image('%s.png' % (key_item,), angle))
        super(KeyedDoor, self).__init__(
            space, position, destination, dest_pos, angle,
            render.ImageRenderer(resources.get_image(
                'objects', 'door.png', transforms=(overlay,))),
            environment.ItemRequiredCondition(key_item),
        )

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("destination", "level name"), ("dest_pos", "coordinate"),
                ("angle", "degrees"), ("key_item", "item name")]


class Hatch(GameObject):
    zorder = ZORDER_FLOOR

    def __init__(self, space, end1, end2, key_state=None):
        a = pymunk.Vec2d(end1)
        b = pymunk.Vec2d(end2)
        offset = b - a
        offset.length /= 2
        mid = (a + offset).int_tuple
        body = make_body(None, None, mid)
        self.shape = pymunk.Segment(
            body, body.world_to_local(tuple(end1)),
            body.world_to_local(tuple(end2)), 7)
        self.shape.collision_type = COLLISION_TYPE_DOOR
        if key_state is None:
            puzzler = puzzle.YesPuzzler()
        else:
            puzzler = puzzle.StateProxyPuzzler(key_state)
        super(Hatch, self).__init__(
            SingleShapePhysicser(space, self.shape),
            render.HatchRenderer(),
            puzzler,
        )

    def collide_with_protagonist(self, protagonist):
        if self.puzzler.get_state():
            # Reject the collision, we can walk through.
            return False
        return True

    collide_with_furniture = collide_with_protagonist

    @classmethod
    def requires(cls):
        return [("name", "string"), ("end1", "coordinates"),
                ("end2", "coordinates"), ("key_state", "puzzler")]

    # The level knows that hatches are magical
    @classmethod
    def movable(cls):
        return True


class KeyedHatch(GameObject):
    zorder = ZORDER_FLOOR

    def __init__(self, space, end1, end2, key_item):
        a = pymunk.Vec2d(end1)
        b = pymunk.Vec2d(end2)
        offset = b - a
        offset.length /= 2
        mid = (a + offset).int_tuple
        body = make_body(None, None, mid)
        self.shape = pymunk.Segment(
            body, body.world_to_local(tuple(end1)),
            body.world_to_local(tuple(end2)), 7)
        self.shape.collision_type = COLLISION_TYPE_DOOR
        other_shape = pymunk.Circle(body, 30)
        other_shape.collision_type = COLLISION_TYPE_DOOR
        other_shape.sensor = True
        self._key_item = key_item
        super(KeyedHatch, self).__init__(
            MultiShapePhysicser(space, self.shape, other_shape),
            render.KeyedHatchRenderer(
                resources.get_image(
                    'objects', '%s.png' % (key_item,),
                    transforms=(scaler((32, 32)),))),
            puzzle.ParentAttrPuzzler('is_open'),
        )
        self.add_timer('door_open', 0.1)

    @property
    def is_open(self):
        return self.check_timer('door_open')

    def collide_with_protagonist(self, protagonist):
        if protagonist.has_item(self._key_item):
            self.start_timer('door_open')
            return False
        return True

    @classmethod
    def requires(cls):
        return [("name", "string"), ("end1", "coordinates"),
                ("end2", "coordinates"), ("key_item", "item name")]

    # The level knows that hatches are magical
    @classmethod
    def movable(cls):
        return True


class ToggleSwitch(GameObject):
    zorder = ZORDER_LOW

    def __init__(self, space, position):
        body = make_body(None, None, position)
        self.shape = pymunk.Circle(body, 20)
        self.shape.sensor = True
        super(ToggleSwitch, self).__init__(
            SingleShapePhysicser(space, self.shape),
            render.ImageStateRenderer({
                True: resources.get_image('objects', 'lever.png'),
                False: resources.get_image(
                    'objects', 'lever.png', transforms=(FLIP_H,)),
            }),
            puzzle.ParentAttrPuzzler('toggle_on'),
            interactible=environment.Interactible(
                environment.Action(self._toggle)),
        )

    @property
    def toggle_on(self):
        return self._stored_state['toggle_on']

    def _toggle(self, protagonist):
        self._stored_state['toggle_on'] = not self.toggle_on

    def set_stored_state_dict(self, stored_state):
        self._stored_state = stored_state
        # We start in the "off" position.
        self._stored_state.setdefault('toggle_on', False)
        return True

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates")]


class Bullet(GameObject):
    def __init__(self, space, position, impulse, damage, bullet_type,
                 source_collision_type, bullet_sound=None):
        body = make_body(1, pymunk.inf, position)
        body.angle = impulse.angle
        self.last_position = position
        self.shape = pymunk.Circle(body, 2)
        self.shape.sensor = True
        self.shape.collision_type = COLLISION_TYPE_PROJECTILE
        self.damage = damage
        self.type = bullet_type
        self.source_collision_type = source_collision_type
        super(Bullet, self).__init__(
            SingleShapePhysicser(space, self.shape),
            render.ImageRenderer(resources.get_image(
                'objects', '%s.png' % self.type)),
        )
        self.physicser.apply_impulse(impulse)
        if bullet_sound is not None:
            sound.play_sound(bullet_sound, 0.3)

    def update(self, dt):
        super(Bullet, self).update(dt)
        position = (self.physicser.position.x, self.physicser.position.y)
        r = self.get_space().segment_query(self.last_position, position)
        self.last_position = position
        for collision in r:
            shape = collision.shape
            if (shape.collision_type == self.source_collision_type
                    or shape == self.physicser.get_shape()
                    or shape.sensor):
                continue
            if hasattr(shape, 'physicser'):
                shape.physicser.game_object.hit(self)
            self.physicser.remove_from_space()
            return Result(remove=[self])


class ClawAttack(GameObject):
    def __init__(self, space, pos, vector, damage):
        body = make_body(1, pymunk.inf,
                         (pos[0] + (vector.length * math.cos(vector.angle)),
                          pos[1] + (vector.length * math.sin(vector.angle))))
        body.angle = vector.angle
        self.shape = pymunk.Circle(body, 30)
        self.shape.sensor = True
        self.shape.collision_type = COLLISION_TYPE_WEREWOLF_ATTACK
        self.damage = damage
        super(ClawAttack, self).__init__(
            SingleShapePhysicser(space, self.shape),
            render.ImageRenderer(resources.get_image(
                'objects', 'werewolf_SW_claw_attack.png',
                transforms=(FLIP_H,))),
        )

    def update(self, dt):
        super(ClawAttack, self).update(dt)
        if self.lifetime > 0.1:
            self.physicser.remove_from_space()
            return Result(remove=[self])


class HostileTerrain(GameObject):
    zorder = ZORDER_FLOOR
    damage = None
    tiles = []
    tile_alpha = 255
    tile_frame_ticks = 3
    # How often to hit the player
    rate = 5

    def __init__(self, space, position, outline):
        body = make_body(10, pymunk.inf, position)
        # Adjust shape relative to position
        shape_outline = [(p[0] - position[0], p[1] - position[1]) for
                         p in outline]
        self.shape = pymunk.Poly(body, shape_outline)
        self._ticks = 0
        self.shape.collision_type = COLLISION_TYPE_SWITCH
        self.shape.sensor = True
        renderer = self._fix_image(outline)
        self._collider = puzzle.CollidePuzzler()
        self._collider.set_game_object(self)
        self._protagonist = None
        super(HostileTerrain, self).__init__(
            SingleShapePhysicser(space, self.shape),
            renderer)

    def _fix_image(self, outline):
        if len(self.tiles) > 1:
            tile_images = [resources.get_image('tiles', x)
                           for x in self.tiles]
            renderer = render.TimedTiledRenderer(outline, tile_images,
                                                 self.tile_frame_ticks,
                                                 self.tile_alpha)
        else:
            tile_image = resources.get_image('tiles', self.tiles[0])
            renderer = render.TiledRenderer(outline, tile_image,
                                            self.tile_alpha)
        return renderer

    def update_image(self, new_outline):
        self.renderer = self._fix_image(new_outline)

    def update(self, seconds):
        if self._collider.get_state():
            if self._ticks == 0:
                self.apply_effect(self._protagonist)
            self._ticks += 1
            if self._ticks > self.rate:
                self._ticks = 0
        self.renderer.update(seconds)

    def collide_with_protagonist(self, protagonist):
        self._protagonist = protagonist

    def apply_effect(self, protagonist):
        protagonist.lose_health(self.damage)

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("outline", "polygon (convex)")]


class AcidFloor(HostileTerrain):
    damage = 1
    tiles = ['acid.png', 'acid2.png', 'acid3.png']
    tile_alpha = 200
    tile_frame_ticks = 10


class ForceWolfFloor(HostileTerrain):
    tiles = ['moonlight.png']
    rate = 0
    tile_alpha = 150
    zorder = ZORDER_HIGH

    def apply_effect(self, protagonist):
        protagonist.force_wolf_form()


class GravityWell(GameObject):
    zorder = ZORDER_FLOOR
    # How often to hit the player
    rate = 5

    def __init__(self, space, position, radius, force):
        body = make_body(None, None, position)
        # Adjust shape relative to position
        self._radius = radius
        self.shape = pymunk.Circle(body, radius)
        self.centre = pymunk.Circle(body, 10)
        self.centre.friction = pymunk.inf
        self._ticks = 0
        self.force = force
        self.shape.collision_type = COLLISION_TYPE_SWITCH
        self.shape.sensor = True
        super(GravityWell, self).__init__(
            MultiShapePhysicser(space, self.shape, self.centre),
            render.ImageRenderer(resources.get_image(
                'objects', 'gravity_well.png')),
        )

    def collide_with_protagonist(self, protagonist):
        # We're called every frame we're colliding, so
        # There are timing issues with stepping on and
        # off terrian, but as long as the rate is reasonably
        # low, they shouldn't impact gameplay
        self.apply_effect(protagonist)

    def collide_with_furniture(self, furniture):
        # We're called every frame we're colliding, so
        # There are timing issues with stepping on and
        # off terrian, but as long as the rate is reasonably
        # low, they shouldn't impact gameplay
        self.apply_effect(furniture)

    def apply_effect(self, object_to_move):
        movement = self.physicser.position - object_to_move.physicser.position
        local_force = self.force * math.sqrt(
            object_to_move.get_shape().body.mass)
        movement.length = local_force
        object_to_move.environmental_movement(movement)

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("radius", "int"), ("force", "int")]


class SheepPen(GameObject):
    zorder = ZORDER_FLOOR

    def __init__(self, space, position, outline, sheep_count):
        body = make_body(None, None, position)
        # Adjust shape relative to position
        shape_outline = [(p[0] - position[0], p[1] - position[1]) for
                         p in outline]
        self.shape = pymunk.Poly(body, shape_outline)
        self.shape.collision_type = COLLISION_TYPE_SHEEP_PEN
        self.shape.sensor = True
        super(SheepPen, self).__init__(
            SingleShapePhysicser(space, self.shape),
            render.Renderer(),
            puzzle.MultiCollidePuzzler(sheep_count, COLLISION_TYPE_SHEEP),
        )

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("outline", "polygon (convex)"), ("sheep_count", "int")]
