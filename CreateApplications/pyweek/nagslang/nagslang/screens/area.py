"""Display a game area."""

import pygame
import pymunk
import pymunk.pygame_util

from nagslang.resources import resources
from nagslang.mutators import ImageCentre, scaler
from nagslang.options import options
from nagslang.constants import (
    COLLISION_TYPE_WALL, COLLISION_TYPE_PLAYER, CALLBACK_COLLIDERS,
    COLLISION_TYPE_FURNITURE, COLLISION_TYPE_WEREWOLF_ATTACK,
    CMD_TOGGLE_FORM, CMD_ACTION, PROTAGONIST_HEALTH_MAX_LEVEL)
from nagslang.events import (
    AddDrawableEvent, DeathEvent, DoorEvent, QuitEvent, ScreenChange)
from nagslang.game_object import SplashImage
from nagslang.level import Level
from nagslang.screens.base import Screen
from nagslang.sound import sound


class ControlKeys(object):
    direction_keys = {
        (0, 1): set([pygame.locals.K_UP, pygame.locals.K_w]),
        (0, -1): set([pygame.locals.K_DOWN, pygame.locals.K_s]),
        (-1, 0): set([pygame.locals.K_LEFT, pygame.locals.K_a]),
        (1, 0): set([pygame.locals.K_RIGHT, pygame.locals.K_d]),
    }

    attack_keys = set([pygame.locals.K_z, pygame.locals.K_LCTRL])

    command_keys = {
        pygame.locals.K_c: CMD_TOGGLE_FORM,
        pygame.locals.K_SPACE: CMD_ACTION,
    }

    def __init__(self):
        self.keys_down = set()

    def key_down(self, key):
        self.keys_down.add(key)

    def key_up(self, key):
        self.keys_down.discard(key)

    def handle_event(self, ev):
        if ev.type == pygame.locals.KEYDOWN:
            self.key_down(ev.key)
        elif ev.type == pygame.locals.KEYUP:
            self.key_up(ev.key)

    def get_direction(self):
        dx, dy = 0, 0
        for (tx, ty), keys in self.direction_keys.iteritems():
            if self.keys_down & keys:
                dx += tx
                dy += ty
        return (dx, dy)

    def is_attacking(self):
        return bool(self.keys_down & self.attack_keys)

    def get_command_key(self, key):
        return self.command_keys.get(key, None)


class Drawables(object):
    def __init__(self):
        self._drawables = {}

    def add(self, drawable):
        self._drawables.setdefault(drawable.zorder, []).append(drawable)

    def remove(self, drawable):
        self._drawables[drawable.zorder].remove(drawable)

    def get_drawables(self):
        for zorder in sorted(self._drawables):
            for drawable in self._drawables[zorder]:
                yield drawable

    __iter__ = get_drawables


class AreaScreen(Screen):

    def setup(self):
        self._disable_render = False  # Avoid redrawing on scene changes
        self.keys = ControlKeys()
        self._level = Level(self.name, self.world)
        self._level.load(self.space)
        self._drawables = Drawables()
        self.add_walls()
        self._add_collision_handlers()
        self.add_protagonist()
        self.add_game_objects()
        self.save_progress()
        sound.play_music(self._level.music, self._level.music_volume)
        self._background = None
        self._surface = None

    def teardown(self):
        sound.stop()
        for collision_type in CALLBACK_COLLIDERS:
            self.space.remove_collision_handler(
                COLLISION_TYPE_PLAYER, collision_type)
            self.space.remove_collision_handler(
                COLLISION_TYPE_FURNITURE, collision_type)
            self.space.remove_collision_handler(
                COLLISION_TYPE_WEREWOLF_ATTACK, collision_type)

    @classmethod
    def list_areas(self):
        return Level.list_levels()

    def _player_collision_pre_solve_handler(self, space, arbiter):
        gobj = arbiter.shapes[1].physicser.game_object
        result = gobj.collide_with_protagonist(self.protagonist)
        # The collision handler must return `True` or `False`. We don't want to
        # accidentally reject collisions from handlers that return `None`, so
        # we explicitly check for `False` and treate everything else as `True`.
        return result is not False

    def _claw_attack_collision_pre_solve_handler(self, space, arbiter):
        claw = arbiter.shapes[0].physicser.game_object
        gobj = arbiter.shapes[1].physicser.game_object
        result = gobj.collide_with_claw_attack(claw)
        return result is not False

    def _furniture_collision_pre_solve_handler(self, space, arbiter):
        furniture = arbiter.shapes[0].physicser.game_object
        gobj = arbiter.shapes[1].physicser.game_object
        result = gobj.collide_with_furniture(furniture)
        return result is not False

    def _add_collision_handlers(self):
        for collision_type in CALLBACK_COLLIDERS:
            self.space.add_collision_handler(
                COLLISION_TYPE_PLAYER, collision_type,
                pre_solve=self._player_collision_pre_solve_handler)
            self.space.add_collision_handler(
                COLLISION_TYPE_FURNITURE, collision_type,
                pre_solve=self._furniture_collision_pre_solve_handler)
            self.space.add_collision_handler(
                COLLISION_TYPE_WEREWOLF_ATTACK, collision_type,
                pre_solve=self._claw_attack_collision_pre_solve_handler)

    def add_walls(self):
        self.walls = []
        body = pymunk.Body()
        body.position = (0, 0)
        walls = self._level.get_walls()
        for wall in walls:
            if len(wall) < 2:
                # Don't try to add a useless wall
                continue
            corners = wall
            corner = corners[-1]
            for next_corner in corners:
                wall = pymunk.Segment(body, corner, next_corner, 5)
                wall.collision_type = COLLISION_TYPE_WALL
                wall.elasticity = 1.0
                self.walls.append(wall)
                corner = next_corner
        self.space.add(*self.walls)

    def add_game_objects(self):
        for drawable in self._level.drawables:
            self._drawables.add(drawable)

    def add_protagonist(self):
        self.protagonist = self.world.protagonist
        self.protagonist.reset()
        self.protagonist.change_space(self.space)
        self.world.rooms += 1
        self._drawables.add(self.protagonist)

    def save_progress(self):
        if self.name == Level.game_starting_point()[0]:
            return
        self.world.level = (self.name, (self.protagonist.physicser.position.x,
                                        self.protagonist.physicser.position.y))
        self.world.save()

    def handle_event(self, ev):
        if ev.type == pygame.locals.KEYDOWN:
            if ev.key == pygame.locals.K_ESCAPE:
                if options.debug:
                    print ('Died at: (%i,%i)'
                           % (self.protagonist.physicser.position.x,
                              self.protagonist.physicser.position.y))
                if self._level.is_starting_level():
                    QuitEvent.post()
                    return
                self.protagonist.die()
                return
            cmd_key = self.keys.get_command_key(ev.key)
            if cmd_key is not None:
                self.protagonist.handle_keypress(cmd_key)
        elif DoorEvent.matches(ev):
            self.protagonist.set_position(ev.dest_pos)
            if ev.destination is not None and ev.destination != self.name:
                if options.debug:
                    print 'Teleporting to %s' % ev.destination
                # Go to anther screen
                self._disable_render = True
                ScreenChange.post(ev.destination)
                return
            # else we're teleporting within the screen, and just the
            # position change is enough
        elif DeathEvent.matches(ev):
            self._disable_render = True
            self.world.load()
            self.world.deaths += 1
            level, pos = Level.game_starting_point()
            self.protagonist.set_position(pos)
            ScreenChange.post(level)
        elif AddDrawableEvent.matches(ev):
            self._drawables.add(ev.drawable)
            if ev.drawable.overlay:
                self._level.overlay_drawables.append(ev.drawable.overlay)
        self.keys.handle_event(ev)

    def _calc_viewport(self, level_surface, display_surface):
        level_size = level_surface.get_size()
        display_size = display_surface.get_size()
        protagnist_pos = self.protagonist.physicser.get_render_position(
            level_surface)
        x_wide = display_size[0] // 2
        y_wide = display_size[1] // 2
        if display_size[0] > level_size[0]:
            x = -(display_size[0] - level_size[0]) // 2
        elif protagnist_pos[0] < x_wide:
            x = 0
        elif protagnist_pos[0] > level_size[0] - x_wide:
            x = level_size[0] - display_size[0]
        else:
            x = protagnist_pos[0] - x_wide
        if display_size[1] > level_size[1]:
            y = -(display_size[1] - level_size[1]) // 2
        elif protagnist_pos[1] < y_wide:
            y = 0
        elif protagnist_pos[1] > level_size[1] - y_wide:
            y = level_size[1] - display_size[1]
        else:
            y = protagnist_pos[1] - y_wide
        return pygame.rect.Rect(x, y, display_size[0], display_size[1])

    def render(self, surface):
        if self._disable_render:
            return
        if self._background is None:
            bg = self._level.get_background()
            self._background = pygame.surface.Surface(bg.get_size())
            self._background.blit(bg, (0, 0))
            self._surface = pygame.surface.Surface(self._background.get_size())
        render_rect = self._calc_viewport(self._surface, surface)
        self._surface.set_clip(render_rect)
        self._surface.blit(self._background, render_rect.topleft, render_rect)
        for drawable in self._drawables:
            drawable.render(self._surface)
        surface.blit(self._surface, (0, 0), render_rect)
        # Maximum width we allow for overlays
        max_width = min(render_rect.width, self._surface.get_width())
        for overlay in reversed(self._level.overlay_drawables):
            if overlay.is_visible():
                overlay.render(surface, render_rect.topleft, max_width)
                break
        self.render_health_bar(surface)
        self.render_inventory(surface)

    def tick_protagonist(self):
        dx, dy = self.keys.get_direction()
        self.protagonist.set_direction(dx, dy)
        if self.keys.is_attacking():
            self._handle_result(self.protagonist.handle_attack_key_down())

    def tick(self, seconds):
        super(AreaScreen, self).tick(seconds)
        self.tick_protagonist()
        for drawable in self._drawables:
            self._handle_result(drawable.update(seconds))

    def _handle_result(self, result):
        if result is not None:
            for drawable in result.add:
                self._drawables.add(drawable)
                if drawable.overlay:
                    self._level.overlay_drawables.add(drawable.overlay)
            for drawable in result.remove:
                self._drawables.remove(drawable)
                if drawable.overlay:
                    self._level.overlay_drawables.remove(drawable.overlay)

    def render_health_bar(self, surface, damage_experienced=None):
        bar_surface = pygame.Surface((110, 40)).convert(surface)
        if damage_experienced:
            health_box_colour = pygame.color.THECOLORS['red']
        else:
            health_box_colour = pygame.color.THECOLORS['white']
        bar_surface.fill(health_box_colour)
        if self.protagonist.in_human_form():
            health_colour = pygame.color.THECOLORS['red']
        else:
            health_colour = pygame.color.THECOLORS['violetred3']
        health = self.protagonist.get_health_level()
        rect = pygame.Rect(
            5, 5, (100 * health) / PROTAGONIST_HEALTH_MAX_LEVEL, 30)
        pygame.draw.rect(bar_surface, health_colour, rect, 0)
        bar_surface.set_alpha(192)
        y_pos = surface.get_height() - 20 - bar_surface.get_height()
        surface.blit(bar_surface, (20, y_pos))

    def render_inventory(self, surface):
        items = len(self.world.inventory)
        if not items:
            return
        padding = 4
        img_size = 64
        size = 32
        inv_surf = pygame.Surface(
            (padding + (size + padding) * items,
             (2 * padding + size)))
        inv_surf = inv_surf.convert(surface)
        inv_surf.set_alpha(192)
        inv_surf.fill(pygame.color.THECOLORS['white'])
        for index, item in enumerate(sorted(self.world.inventory)):
            img = resources.get_image(
                'objects', item + '.png',
                transforms=(ImageCentre((img_size, img_size)),
                            scaler((size, size))))
            inv_surf.blit(img, (padding + index * (size + padding), padding))
        y_pos = surface.get_height() - 20 - inv_surf.get_height()
        x_pos = 130 + padding
        surface.blit(inv_surf, (x_pos, y_pos))

    def splash(self):
        AddDrawableEvent.post(SplashImage(resources.get_image('title.png'), 5))
