#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: __init__.py 418 2008-04-20 18:28:58Z aholkner $'

import os
import pickle
import time

import pyglet
from pyglet.window import key
from pyglet.window import mouse
from pyglet.gl import *

import camera
import editor
import globals
import map
import placeable
import player
import sound

import init_placeables

_debug = False

class AnimSpriteScale(object):
    finished = False

    def __init__(self, sprite, start=1., goal=1.1, t=0.2):
        self.sprite = sprite
        self.start = start
        self.goal = goal
        self.speed = (goal - sprite.scale) / t
        self.t = 0
        pyglet.clock.schedule(self.update)

    def update(self, dt):
        if not self.sprite._vertex_list:
            pyglet.clock.unschedule(self.update)
            return

        self.t += dt
        self.sprite.scale += self.speed * dt
        if (self.speed > 0 and self.sprite.scale >= self.goal) or \
           (self.speed < 0 and self.sprite.scale <= self.goal):
            self.sprite.scale = self.goal
            pyglet.clock.unschedule(self.update)
            if self.speed < 0:
                self.finished = True

    def revert(self):
        if self.t == 0:
            return
        self.goal = self.start
        self.speed = (self.goal - self.sprite.scale) / self.t
        self.t = 0
        pyglet.clock.unschedule(self.update)
        pyglet.clock.schedule(self.update)

    def kill(self):
        pyglet.clock.unschedule(self.update)
        self.finished = True

class Game(object):
    update_t = 1/60.

    width = 800
    height = 400

    editing = False

    menu_coords = {
        'title': (254, 382),
        'menu': (2, -30),
        'pyglet': (-470, 384),
        'story1': (762, -323),
        'story2': (1545, -337),
        'story3': (1137, -826),
        'flipbook': (-815, -17),
        'gameover': (1043, 382)
    }

    menu_advances = {
        'pyglet': 'title',
        'title': 'menu',
        'story1': 'story2',
        'story2': 'story3',
        'gameover': 'title',
    }

    box_tally = 0
    coin_tally = 0
    flower_tally = 0

    #initial_player_x = -1600
    #initial_player_y = 400
    initial_player_x = 250
    initial_player_y = 540

    def __init__(self):
        self.maps = map.MapSet.load('map.txt', 'tiles.txt', 512, 256)
        self.foreground_maps = map.MapSet.load('water_map.txt', 
                                               'water_tiles.txt', 64, 128)
        self.darkness_maps = map.DarknessMapSet.load('dark_map.txt', 
                                               'dark_tiles.txt', 128, 128)
        self.pickups_layer = \
            placeable.Layer.load('pickups.txt', interactive=True)
        self.fixed_lights_layer = \
            placeable.Layer.load('fixed_lights.txt')
        self.background_layer = \
            placeable.Layer.load('backgrounds.txt')
        self.distant_layer = \
            placeable.Layer.load('distant.txt', paralax=.08)
        self.effects_layer = \
            placeable.Layer.load('effects.txt')
        self.menu_layer = \
            placeable.Layer.load('menu.txt')
        self.blueprint_layer = BlueprintLayer()
        self.tally_layer = TallyLayer()
        self.lamp_layer = LampLayer()

        for placed in self.menu_layer.placed:
            if placed.placeable.name == 'flipbook_light':
                self.flipbook_light = placed
            if placed.placeable.name == 'flipbook_head':
                self.flipbook_head = placed
            if placed.placeable.name == 'flipbook_head_left':
                self.flipbook_head_left = placed
            if placed.placeable.name == 'flipbook_head_right':
                self.flipbook_head_right = placed
            if placed.placeable.name == 'flipbook_torso':
                self.flipbook_torso = placed
            if placed.placeable.name == 'flipbook_torso_left':
                self.flipbook_torso_left = placed
            if placed.placeable.name == 'flipbook_torso_right':
                self.flipbook_torso_right = placed
            if placed.placeable.name == 'flipbook_leg':
                self.flipbook_leg = placed
            if placed.placeable.name == 'flipbook_leg_left':
                self.flipbook_leg_left = placed
            if placed.placeable.name == 'flipbook_leg_right':
                self.flipbook_leg_right = placed
            if placed.placeable.name == 'circle_sound_on':
                self.circle_sound_on = placed
            if placed.placeable.name == 'circle_sound_off':
                self.circle_sound_off = placed
            if placed.placeable.name == 'circle_music_on':
                self.circle_music_on = placed
            if placed.placeable.name == 'circle_music_off':
                self.circle_music_off = placed

        self.update_sound_music_circles()

        self.player = player.Player()

        self.game_layers = [
            self.distant_layer,
            self.maps,
            self.background_layer,
            self.pickups_layer, 
            self.player,
            self.effects_layer,
            self.foreground_maps,
            self.darkness_maps,
            self.lamp_layer,
        ]

        self.menu_layers = [
            self.blueprint_layer,
            self.menu_layer,
            self.tally_layer
        ]
        self.menu_hover = None
        self.menu_anims = []

        self.camera = camera.Camera()
        self.menu_camera = camera.Camera()
        self.menu_camera.follow = False
        self.active_camera = self.menu_camera
        self.tasks = []
        self.saved_state = None
        self.loaded_saved_state = None
        self.initial_saved_state = None

        self.accum_t = 0.
        self.game_time = 0.0
        self.clock = pyglet.clock.Clock(time_function=lambda: self.game_time)
        pyglet.clock.schedule_interval(self.update, self.update_t)

    def startup(self):
        self.clock.schedule(self.player.update)
        self.clock.schedule(self.camera.update)
        self.clock.schedule_interval(self.camera.update_visibility, 0.1)

        self.player.x = self.initial_player_x
        self.player.y = self.initial_player_y
        self.save_state(False)
        self.initial_saved_state = self.saved_state
        self.saved_state = None

    # ---
    # Fixed update

    def update(self, dt):
        self.process_tasks()

        if self.in_menu or self.editing:
            return

        # Align updates to fixed timestep
        self.accum_t += dt
        if self.accum_t > self.update_t * 3:
            self.accum_t = self.update_t
        while self.accum_t >= self.update_t:
            self.game_time += self.update_t 
            self.clock.tick()
            self.accum_t -= self.update_t

    # ---
    # Menu

    def enter_menu(self):
        self.in_menu = True
        self.layers = self.menu_layers
        self.active_camera = self.menu_camera
        self.tally_layer.refresh()
        pyglet.clock.schedule(self.menu_camera.update)
        pyglet.clock.schedule_interval(self.menu_camera.update_visibility, .1)
        self.go_menu(self.current_menu, True)

    def leave_menu(self):
        if not self.saved_state:
            return

        self.in_menu = False
        self.layers = self.game_layers
        self.active_camera = self.camera

        pyglet.clock.unschedule(self.menu_camera.update)
        pyglet.clock.unschedule(self.menu_camera.update_visibility)

        self.active_camera.update_visibility(0)
        self.wait_for_tasks()

    def go_menu(self, name, instant=True):
        self.current_menu = name
        x, y = self.menu_coords[name]
        self.menu_camera.goal_x = x
        self.menu_camera.goal_y = y
        if instant:
            self.menu_camera.x = x
            self.menu_camera.y = y

        pyglet.clock.unschedule(self.menu_advance)
        if name in self.menu_advances or name == 'story3':
            pyglet.clock.schedule_once(self.menu_advance, 5.)

    def menu_click(self, placed):
        if not placed:
            self.menu_advance()
        elif placed.placeable.name == 'startgame.png':
            self.go_menu('story1', False)
        elif placed.placeable.name in (
            'sound.png', 'circle_sound_off', 'circle_sound_on'):
            self.toggle_sound()
        elif placed.placeable.name in (
            'music.png', 'circle_music_off', 'circle_music_on'):
            if sound.have_avbin:
                self.toggle_music()
        elif placed.placeable.name == 'continue.png':
            if self.loaded_saved_state:
                self.saved_state = self.loaded_saved_state
                self.loaded_saved_state = None
                self.restore_state()
            self.leave_menu()
        elif placed.placeable.name == 'flipbook_head_right':
            self.player.cycle_head_part(1)
        elif placed.placeable.name == 'flipbook_torso_right':
            self.player.cycle_torso_part(1)
        elif placed.placeable.name == 'flipbook_leg_right':
            self.player.cycle_leg_part(1)
        elif placed.placeable.name == 'flipbook_head_left':
            self.player.cycle_head_part(-1)
        elif placed.placeable.name == 'flipbook_torso_left':
            self.player.cycle_torso_part(-1)
        elif placed.placeable.name == 'flipbook_leg_left':
            self.player.cycle_leg_part(-1)
        elif placed.placeable.name == 'menu.png':
            self.go_menu('menu', False)
        elif placed.placeable.name == 'quit.png':
            pyglet.app.exit()
        else:
            self.menu_advance()

    def menu_motion(self, placed):
        if placed is self.menu_hover:
            return

        for anim in self.menu_anims:
            anim.revert()
        self.menu_anims = [a for a in self.menu_anims if not a.finished]

        if placed and placed.sprite and placed.placeable.name in (
                'startgame.png',
                'continue.png',
                'flipbook_head_right',
                'flipbook_head_left',
                'flipbook_torso_right',
                'flipbook_torso_left',
                'flipbook_leg_right',
                'flipbook_leg_left',
                'menu.png',
                'quit.png'):
            self.menu_hover = placed
            for anim in self.menu_anims:
                if anim.sprite is placed.sprite:
                    anim.kill()
            self.menu_anims.append(AnimSpriteScale(placed.sprite))
        else:
            self.menu_hover = None


    def menu_update_flipbook(self):
        self.flipbook_head.anim_name = self.player.head_part.anims[-1]
        self.flipbook_head.update_anim()

        self.flipbook_light.visible = self.player.bright

        if self.player.torso_part:
            self.flipbook_torso.anim_name = self.player.torso_part.anims[-1]
            self.flipbook_torso.visible = True
        else:
            self.flipbook_torso.visible = False
        self.flipbook_torso.update_anim()

        if self.player.leg_part and \
           self.player.leg_part != player.spring_part:
            self.flipbook_leg.anim_name = self.player.leg_part.anims[-1]
            self.flipbook_leg.visible = True
        else:
            self.flipbook_leg.visible = False
        self.flipbook_leg.update_anim()

        self.flipbook_head_left.visible = len(self.player.head_parts) > 1
        self.flipbook_head_right.visible = len(self.player.head_parts) > 1

        self.flipbook_torso_left.visible = len(self.player.torso_parts) > 1
        self.flipbook_torso_right.visible = len(self.player.torso_parts) > 1

        self.flipbook_leg_left.visible = len(self.player.leg_parts) > 2
        self.flipbook_leg_right.visible = len(self.player.leg_parts) > 2

    def menu_advance(self, dt=None):
        pyglet.clock.unschedule(self.menu_advance)
        if self.current_menu == 'story3':
            self.new_game()
            self.leave_menu()

        try:
            self.go_menu(self.menu_advances[self.current_menu], False)
        except KeyError: 
            pass

    def toggle_sound(self):
        globals.sound = not globals.sound
        self.update_sound_music_circles()

    def toggle_music(self):
        globals.music = not globals.music
        if globals.music:
            sound.play_music()
        else:
            sound.stop_music()
        self.update_sound_music_circles()

    def update_sound_music_circles(self):
        self.circle_sound_on.visible = globals.sound
        self.circle_sound_off.visible = not globals.sound
        self.circle_music_on.visible = globals.music
        self.circle_music_off.visible = not globals.music

    # ---
    # Game state  


    def new_game(self):
        if _debug:
            print 'New game'

        self.saved_state = self.initial_saved_state
        self.loaded_saved_state = None
        self.restore_state()

    def kill_player(self):
        assert not self.player.dead
        self.player.input_disabled = True
        self.player.dead = True
        sound.stop_move()
        pyglet.clock.schedule_once(globals.window.fade_out, 2.)
        pyglet.clock.schedule_once(self.restore_state, 3.)
        pyglet.clock.schedule_once(globals.window.fade_in, 3.5)

    def stab_player(self):
        if self.player.dead:
            return
        if _debug:
            print 'Player stabbed!'
        self.player.movement = player.die_movement
        x = self.player.x
        bb = self.player.get_bbox()
        y = (bb.y2 + bb.y1) // 2
        self.player.visible = False
        self.add_effect(particles.die_effect, x, y)
        self.kill_player()
        sound.play('break.wav')

    def drown_player(self):
        if self.player.dead:
            return
        if _debug:
            print 'Player drowned!'
        self.player.movement = player.drown_movement
        x = self.player.x
        bb = self.player.get_bbox()
        y = (bb.y2 + bb.y1) // 2
        self.add_effect(particles.bubble_effect, x, y)
        self.kill_player()
        sound.play('bubbles.wav')

    def incr_tally(self, tally):
        if tally == 'box':
            self.box_tally += 1
            if self.box_tally >= 4:
                self.game_over()
        elif tally == 'flower':
            self.flower_tally += 1
        elif tally == 'coin':
            self.coin_tally += 1
        else:
            assert False

    def game_over(self):
        self.go_menu('gameover')
        self.enter_menu()

    # ---
    # Effects

    def add_effect(self, placeable, x, y):
        placed = placeable.place(x, y)
        self.effects_layer.add_placed(placed)
        placed.load(self.effects_layer.batch)

    # --- 
    # Tasks

    def add_task(self, task):
        self.tasks.append(task)

    def wait_for_tasks(self):
        for task in self.tasks:
            for _ in task:
                pass

    TASK_SLICE = 1/40.

    def process_tasks(self):
        if self.tasks:
            t = time.time
            end_time = t() + self.TASK_SLICE
            task = self.tasks[0]
            while self.tasks and t() < end_time:
                try:
                    task.next()
                except StopIteration:
                    self.tasks.pop(0)
                    if self.tasks:
                        task = self.tasks[0]

    # --- 
    # Save/restore game state

    def get_save_filename(self):
        dir = pyglet.resource.get_settings_path('MakeMe')
        try:
            os.makedirs(dir)
        except OSError:
            pass
        return os.path.join(dir, 'save_game')

    def save_state(self, save_to_disk=True):
        self.saved_state = d = {}
        d['box_tally'] = self.box_tally
        d['coin_tally'] = self.coin_tally
        d['flower_tally'] = self.flower_tally
        for layer in self.game_layers:
            layer.save_state(d)
        if _debug:
            print 'Saved state'
            
        if save_to_disk:
            filename = self.get_save_filename()
            if not filename:
                return
            try:
                pickle.dump(d, open(filename, 'wb'))
            except pickle.PickleError:
                raise
            except OSError:
                pass

            if _debug:
                print 'Saved state to disk'

    def load_save_state(self):
        filename = self.get_save_filename()
        if filename:
            try:
                self.loaded_saved_state = pickle.load(open(filename, 'rb'))
                if _debug:
                    print 'Loaded saved state from disk'
            except IOError:
                pass
            except:
                raise

    def restore_state(self, dt=None):
        if not self.saved_state:
            print 'No saved state to restore'
            return

        d = self.saved_state

        self.effects_layer.clear()
        for layer in self.game_layers:
            layer.restore_state(d)
        self.box_tally = d['box_tally']
        self.coin_tally = d['coin_tally']
        self.flower_tally = d['flower_tally']
        self.camera.x = None
        self.camera.update(0)
        self.camera.update_visibility()
        self.wait_for_tasks()

        self.player.input_disabled = False
        self.player.dead = False
        if _debug:
            print 'Restored state'

        sound.update_music(0, force=True)

class TallyLayer(object):
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        pyglet.resource.add_font('attractmorewomen.ttf')

        self.flower_label = pyglet.text.Label('123', x=-160, y=250,
            font_name='Attract more women', font_size=22,
            valign='center', halign='right', batch=self.batch)
        self.coin_label = pyglet.text.Label('456', x=-160, y=330,
            font_name='Attract more women', font_size=22,
            valign='center', halign='right', batch=self.batch)
        self.box_label = pyglet.text.Label('1 of 4', x=-160, y=145,
            font_name='Attract more women', font_size=22,
            valign='center', halign='right', batch=self.batch)

    def refresh(self):
        self.flower_label.text = '%d (%d%%)' % (
            globals.game.flower_tally, 
            100 * globals.game.flower_tally / globals.flower_total)
        self.coin_label.text = '%d (%d%%)' % (
            globals.game.coin_tally, 
            100 * globals.game.coin_tally / globals.coin_total)
        self.box_label.text = '%s of 4' % globals.game.box_tally

    def save_state(self, d):
        pass

    def restore_state(self, d):
        pass

    def draw(self):
        self.batch.draw()

    def update_visibility_bbox(self, bbox):
        pass

    def clear_highlight(self):
        pass

    def save(self):
        pass

class BlueprintLayer(object):
    def __init__(self):
        texture = self.texture = pyglet.resource.texture('background_tile.png')
        self.image = pyglet.image.TileableTexture(
            texture.width, texture.height, texture.target, texture.id)

    def save_state(self, d):
        pass

    def restore_state(self, d):
        pass

    def draw(self):
        tw = self.texture.width 
        th = self.texture.height
        offset_x = int(globals.game.menu_camera.x) % tw
        offset_y = int(globals.game.menu_camera.y) % th

        glColor3f(1, 1, 1)
        glPushMatrix()
        glLoadIdentity()
        self.image.blit_tiled(-offset_x, -offset_y, 0, 
                              globals.window.width + tw,
                              globals.window.height + th)
        glPopMatrix()

    def update_visibility_bbox(self, bbox):
        pass

    def clear_highlight(self):
        pass

    def save(self):
        pass

class LampLayer(object):
    enabled = True
    diameter = 350
    radius = diameter / 2
    fixed_diameter = 256
    fixed_radius = fixed_diameter / 2

    def __init__(self):
        self.image = pyglet.resource.image('lamp.png')
        #self.image.anchor_x = self.diameter // 2
        #self.image.anchor_y = self.diameter // 2

    def save_state(self, d):
        pass

    def restore_state(self, d):
        pass

    def draw(self):
        if not self.enabled:
            return

        glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT | GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_TRUE)
        glBlendFunc(GL_ONE, GL_ONE)
        glColor3f(1, 1, 1)

        for light in globals.game.fixed_lights_layer.placed:
            self.image.blit(light.x - self.fixed_radius, 
                            light.y - self.fixed_radius, 
                            width=self.fixed_diameter, 
                            height=self.fixed_diameter)

        if globals.game.player.bright:
            player = globals.game.player

            # Assume lamp is last sprite of last anim_sprite:
            lamp_sprite = player.anim_sprites[-1].sprites[-1]
            x = lamp_sprite.x - lamp_sprite.image.anchor_x + \
                player.x + player.loco_tx + lamp_sprite.image.width//2
            y = lamp_sprite.y - lamp_sprite.image.anchor_y + \
                player.y + player.loco_ty + lamp_sprite.image.height
            x -= self.radius
            y -= self.radius
            self.image.blit(x, y, width=self.diameter, height=self.diameter)

        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glBlendFunc(GL_ZERO, GL_DST_ALPHA)
        glPushMatrix()
        glLoadIdentity()
        glColor3f(0, 0, 0)
        glRectf(0, 0, globals.window.width, globals.window.height)
        glPopMatrix()

        glPopAttrib()

    def update_visibility_bbox(self, bbox):
        globals.game.fixed_lights_layer.update_visibility_bbox(bbox)

    def clear_highlight(self):
        globals.game.fixed_lights_layer.clear_highlight()

    def save(self):
        pass

class GameWindow(pyglet.window.Window):
    fade = 0.
    fade_t = 1.

    def on_draw(self):
        glClearColor(.2, .2, .3, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        globals.game.active_camera.apply()
        for layer in globals.game.layers:
            layer.draw()

        glLoadIdentity()

        if self.fade:
            glPushAttrib(GL_COLOR_BUFFER_BIT | GL_CURRENT_BIT)
            glEnable(GL_BLEND)
            glColor4f(0, 0, 0, self.fade)
            glRectf(0, 0, self.width, self.height)
            glPopAttrib()

        #fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        if globals.game.player.input_disabled:
            return

        if symbol == key.ESCAPE:
            if globals.game.in_menu:
                globals.game.leave_menu()
            else:
                globals.game.go_menu('menu')
                globals.game.enter_menu()
        elif symbol == key.SPACE:
            if globals.game.in_menu:
                globals.game.leave_menu()
            else:
                globals.game.go_menu('flipbook')
                globals.game.enter_menu()
        elif symbol == key.N and modifiers & key.MOD_ACCEL:
            globals.game.new_game()
            globals.game.leave_menu()
        elif symbol == key.E and modifiers & key.MOD_ACCEL: # CHEAT
            self.push_handlers(editor.Editor())
        elif globals.game.in_menu:
            globals.game.menu_advance()

    def on_mouse_press(self, x, y, button, modifiers):
        if button != mouse.LEFT:
            return

        if not globals.game.in_menu:
            return

        x, y = globals.game.menu_camera.window_to_world(x, y)
        placed = globals.game.menu_layer.get_placed_at(x, y)
        globals.game.menu_click(placed)

    def on_mouse_motion(self, x, y, dx, dy):
        if not globals.game.in_menu:
            return
        x, y = globals.game.menu_camera.window_to_world(x, y)
        placed = globals.game.menu_layer.get_placed_at(x, y)
        globals.game.menu_motion(placed)

    def fade_in(self, dt=None):
        self.fade_f1 = self.fade
        self.fade_f2 = 0.
        self.fade_t = 1. - self.fade_t
        pyglet.clock.unschedule(self.fade_update)
        pyglet.clock.schedule(self.fade_update)

    def fade_out(self, dt=None):
        self.fade_f1 = self.fade
        self.fade_f2 = 1.
        self.fade_t = 1. - self.fade_t
        pyglet.clock.unschedule(self.fade_update)
        pyglet.clock.schedule(self.fade_update)

    def fade_update(self, dt):
        self.fade_t += dt * 3 / 2
        if self.fade_t >= 1.:
            pyglet.clock.unschedule(self.fade_update)
        self.fade = self.fade_f1 * (1 - self.fade_t) + \
            self.fade_f2 * self.fade_t


def main():
    globals.game = Game()
    config = pyglet.gl.Config(double_buffer=True, alpha_size=8)
    globals.window = GameWindow(globals.game.width, globals.game.height,
        config=config, caption='Make Me', vsync=True)
    globals.window.push_handlers(globals.game.player)
    globals.window.push_handlers(globals.keys)

    globals.game.player.update_parts()

    globals.game.startup()
    globals.game.load_save_state()
    globals.game.go_menu('pyglet')
    globals.game.enter_menu()

    #global fps_display
    #fps_display = pyglet.clock.ClockDisplay()

    globals.game.wait_for_tasks()

    sound.init_music_zones()
    pyglet.app.run()

if __name__ == '__main__':
    main()
