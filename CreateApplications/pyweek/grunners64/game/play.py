import logging

import pyglet
from pyglet import gl
from pyglet.sprite import Sprite
from pyglet.graphics import OrderedGroup
from pyglet.image import Animation, AnimationFrame

from .base import State, Scene
from .const import WIDTH, HEIGHT
from .pixfont import get_font
from .utils import get_texture, get_texture_sequence
from .map import Map

class Zap(object):

    SPEED = 100
    D = 0.6
    impact = pyglet.resource.media("impact.wav", streaming=False)
    frames = get_texture_sequence("zap.png", 16, 16, 0, 0)
    alive = True
    d = 0

    r = 0
    w = 3
    h = 3

    def __init__(self, owner, x, y, dir, map):
        self.owner = owner
        self.x = x
        self.y = y
        self.map = map

        if dir == 0:
            self.incx = 1
            self.incy = 0
            self.mx = 10
            self.my = 0
            group_number = 1
        elif dir == 1:
            self.incx = -1
            self.incy = 0
            self.mx = 6
            self.my = 0
            self.g = 1
            group_number = 1
        elif dir == 2:
            self.incx = 0
            self.incy = -1
            self.mx = 8
            self.my = 0
            group_number = 1
        elif dir == 3:
            self.incx = 0
            self.incy = 1
            self.mx = 8
            self.my = -6
            group_number = 3

        self.frame = 0
        self.sprite = Sprite(self.frames[self.frame], x=int(x), y=HEIGHT-int(y), batch=map.batch, group=OrderedGroup(map.last_group+group_number))

    def update(self, dt):

        if (self.incx != 0 or self.incy != 0) and not self.map.is_free(self.x+self.mx, self.y+self.my):
            self.impact.play()
            self.d = self.D
            self.incx = 0
            self.incy = 0

        self.d += dt
        if self.d > self.D:
            self.d = 0.5
            self.frame += 1
            if self.frame < len(self.frames):
                self.sprite.image = self.frames[self.frame]
            else:
                self.alive = False

        self.x += self.SPEED*self.incx*dt
        self.y += self.SPEED*self.incy*dt

        self.sprite.x = int(self.x)
        self.sprite.y = HEIGHT-int(self.y)

    def collision(self, other):
        return self.x+self.mx < other.x+other.w-other.r and \
                other.x+other.r < self.x+self.mx+self.w and \
                self.y+self.my < other.y+other.h-other.r and \
                other.y+other.r < self.y+self.my+self.h

class EnemyRunner(object):

    frames = get_texture_sequence("enemy.png", 16, 16, 0, 0)
    loading_frames = get_texture_sequence("loading_runner.png", 16, 16, 0, 0)
    loading_runner = pyglet.resource.media("loading_runner.wav", streaming=False)
    unloading_runner = pyglet.resource.media("unloading_runner.wav", streaming=False)
    alive = True
    hit = False
    unloading = None

    r = 2
    w = 16
    h = 16

    MAX_CD = 0.4

    def __init__(self, x, y, scene, map):
        self.scene = scene
        self.map = map
        self.x = x
        self.y = y

        self.dframes = ((4, 5, 6, 7), (3, 2, 1, 0), (8, 9, 10, 11), (12, 13, 14, 15))
        self.dir = 3

        self.cframe = 0
        self.fdelay = 0.2

        self.sprite = Sprite(self.frames[self.dframes[self.dir][self.cframe]], x=x, y=HEIGHT-y, batch=self.map.batch, group=OrderedGroup(self.map.last_group+2))

        self.font = get_font("default")
        self.label = self.font.render(self.map.batch, x+8, HEIGHT-y+24, "Loading", align="center", group=OrderedGroup(self.map.last_group+1))
        anim_frames = [AnimationFrame(f, 0.2) for f in self.loading_frames]
        anim_frames[-1].duration = None
        self.loading = Sprite(Animation(anim_frames), x=x, y=HEIGHT-y-1, batch=self.map.batch, group=OrderedGroup(self.map.last_group+3))

        mx, my = self.map.viewport_to_screen(x, y)
        if -self.map.data["tilewidth"] < mx < self.map.w and -self.map.data["tileheight"] < my < self.map.h:
            self.loading_runner.play()

        def anim_done():
            self.label.delete()
            self.label = None
            self.loading.delete()
            self.loading = None
        self.loading.on_animation_end = anim_done

        self.cool_down = 0

        self.idle = 0

    def update_sprite(self, dt, stopped = False):
        if stopped:
            if self.cframe != 0:
                self.cframe = 0
                self.fdelay = 0.2
                self.sprite.image = self.frames[self.dframes[self.dir][self.cframe]]
        else:
            self.sprite.x = int(self.x)
            self.sprite.y = HEIGHT-int(self.y)

            self.fdelay += dt
            if self.fdelay > 0.2:
                self.fdelay = 0
                self.cframe += 1
                if self.cframe > 3:
                    self.cframe = 0

                self.sprite.image = self.frames[self.dframes[self.dir][self.cframe]]

    def enemy_free(self, x, y):
        for e in self.scene.entities:
            if not isinstance(e, EnemyRunner) or e == self:
                continue

            if abs(self.x-e.x) < 8 and abs(self.y-e.y) < 8:
                return False
        return True

    def update(self, dt):

        if self.loading or not self.alive:
            return

        if self.hit:
            if not self.unloading:
                self.sprite.image = self.frames[self.dframes[3][0]]
                anim_frames = [AnimationFrame(f, 0.2) for f in self.loading_frames]
                anim_frames = anim_frames[::-1]
                anim_frames[-1].duration = None
                self.unloading = Sprite(Animation(anim_frames), x=self.x, y=HEIGHT-self.y-1, batch=self.map.batch, group=OrderedGroup(self.map.last_group+3))
                self.unloading_runner.play()
                def anim_done():
                    self.alive = False
                    self.unloading.delete()
                    self.unloading = None
                self.unloading.on_animation_end = anim_done
            return

        if self.cool_down <= self.MAX_CD:
            self.cool_down += dt

        blocked = False
        incx = 0
        incy = 0

        dx = self.scene.p.x-self.x
        dy = self.scene.p.y-self.y-6
        if abs(dx) < 64 or abs(dy) < 64:
            self.idle = 0
            if abs(dx) < abs(dy) or float(abs(dx))/abs(dy) > 3:
                ddir = 3 if dy > 0 else 2
                dx = self.x-self.scene.p.x
                if dx > 4:
                    self.dir = 1
                    incx -= 52*dt
                elif dx < -4:
                    self.dir = 0
                    incx += 52*dt
                else:
                    self.dir = ddir

                if incx > 0 and not (
                        self.map.is_free(self.x+12+incx, self.y) and
                        self.map.is_free(self.x+12+incx, self.y-4) and
                        self.enemy_free(self.x+12+incx, self.y-2)
                        ):
                    blocked = True
                    incx = 0

                if incx < 0 and not (
                        self.map.is_free(self.x+3+incx, self.y) and
                        self.map.is_free(self.x+3+incx, self.y-4) and
                        self.enemy_free(self.x+3+incx, self.y-2)
                        ):
                    blocked = True
                    incx = 0

                if not self.map.is_free(self.x+8+incx*2, self.y+8):
                    blocked = True

                self.x += incx
                self.update_sprite(dt, incx == 0 )

                if not blocked and incx == 0:
                    if self.cool_down > self.MAX_CD and abs(dy) < 64:
                        self.cool_down = 0
                        self.scene.add_enemy_zap(self.x, self.y, self.dir)
            else:
                ddir = 0 if dx > 0 else 1
                dy = self.y-self.scene.p.y-6
                if dy > 4:
                    self.dir = 2
                    incy -= 52*dt
                elif dy < -4:
                    self.dir = 3
                    incy += 52*dt
                else:
                    self.dir = ddir

                if incy > 0 and not (
                        self.map.is_free(self.x+3, self.y+incy) and
                        self.map.is_free(self.x+12, self.y+incy) and
                        self.enemy_free(self.x+7, self.y+incy)
                        ):
                    blocked = True
                    incy = 0

                if incy < 0 and not (
                        self.map.is_free(self.x+3, self.y-4+incy) and
                        self.map.is_free(self.x+12, self.y-4+incy) and
                        self.enemy_free(self.x+7, self.y-4+incy)
                        ):
                    blocked = True
                    incy = 0

                if not self.map.is_free(self.x+8, self.y+8+incy*2):
                    blocked = True

                self.y += incy
                self.update_sprite(dt, incy == 0 )

                if not blocked and incy == 0:
                    if self.cool_down > self.MAX_CD and abs(dx) < 64:
                        self.cool_down = 0
                        self.scene.add_enemy_zap(self.x, self.y, self.dir)
        else:
            self.idle += dt
            if self.idle > 2:
                self.idle = 0
                self.dir = 3
                self.update_sprite(dt, True)

class Runner(object):

    frames = get_texture_sequence("grunner.png", 16, 16, 0, 0)
    loading_frames = get_texture_sequence("loading_runner.png", 16, 16, 0, 0)

    r = 2
    w = 16
    h = 16

    def __init__(self, x, y, scene, map, controls):
        self.scene = scene
        self.map = map
        self.controls = controls
        self.x = x
        self.y = y

        self.dframes = ((4, 5, 6, 7), (3, 2, 1, 0), (8, 9, 10, 11), (12, 13, 14, 15))
        self.dir = 3

        self.cframe = 0
        self.fdelay = 0.2

        self.sprite = Sprite(self.frames[self.dframes[self.dir][self.cframe]], x=x, y=HEIGHT-y, batch=self.map.batch, group=OrderedGroup(self.map.last_group+2))

        font = get_font("default")
        self.loading_label = font.render(self.map.batch, x+8, HEIGHT-y+24, "Loading", align="center", group=OrderedGroup(self.map.last_group+1))
        anim_frames = [AnimationFrame(f, 0.2) for f in self.loading_frames]
        anim_frames[-1].duration = None
        self.loading = Sprite(Animation(anim_frames), x=x, y=HEIGHT-y-1, batch=self.map.batch, group=OrderedGroup(self.map.last_group+3))
        def anim_done():
            self.loading_label.delete()
            self.loading_label = None
            self.loading.delete()
            self.loading = False
        self.loading.on_animation_end = anim_done

        self.in_terminal = False

        self.cool_down = 0
        self.walk = pyglet.resource.media("walk.wav", streaming=False)
        self.walk = self.walk.play()
        self.walk.eos_action = "loop"
        self.walk.pause()

    def update(self, dt):

        if self.loading:
            return

        if self.controls.escape:
            self.controls.clear()
            if self.walk.playing:
                self.walk.pause()
            self.scene.disconnection("Mission Terminated")
            return

        # if wer're in terminal state, controls work different
        if self.in_terminal:
            if self.controls.down:
                self.in_terminal = False
                self.scene.exit_terminal()

            if self.controls.left:
                self.controls.clear()
                self.scene.prev_target()
            if self.controls.right:
                self.scene.next_target()
                self.controls.clear()

            return

        incx = 0
        incy = 0

        if self.controls.up:
            self.dir = 2
            incy -= 52*dt
        if self.controls.down:
            self.dir = 3
            incy += 52*dt
        if self.controls.left:
            self.dir = 1
            incx -= 52*dt
        if self.controls.right:
            self.dir = 0
            incx += 52*dt

        if self.controls.action and self.cool_down > 0.2:
            self.cool_down = 0
            self.scene.add_zap(self.x, self.y, self.dir)
        else:
            self.cool_down += dt

        # basic collision detection
        old_incx = incx
        def test_incx(incx, incy):
            if incx > 0 and not (
                    self.map.is_free(self.x+12+incx, self.y+incy) and
                    self.map.is_free(self.x+12+incx, self.y-4+incy)
                    ):
                incx = 0
                if incy == 0:
                    self.cframe = 1
            if incx < 0 and not (
                    self.map.is_free(self.x+3+incx, self.y+incy) and
                    self.map.is_free(self.x+3+incx, self.y-4+incy)
                    ):
                incx = 0
                if incy == 0:
                    self.cframe = 1
            return incx
        incx = test_incx(incx, incy)

        if incy > 0 and not (
                self.map.is_free(self.x+3+incx, self.y+incy) and
                self.map.is_free(self.x+12+incx, self.y+incy)
                ):
            incy = 0
            incx = old_incx
            # retest incx
            incx = test_incx(incx, incy)
            if incx == 0:
                self.cframe = 1
        if incy < 0 and not (
                self.map.is_free(self.x+3+incx, self.y-4+incy) and
                self.map.is_free(self.x+12+incx, self.y-4+incy)
                ):
            incy = 0
            incx = old_incx

            # test for a terminal
            mx = self.x//self.map.data["tilewidth"]
            my = self.y//self.map.data["tileheight"]-1

            was_in_terminal = self.in_terminal
            self.in_terminal = False
            if self.dir == 2 and (mx, my) in self.map.objectgroups["Entities"]:
                obj = self.map.objectgroups["Entities"][mx, my]
                if obj["type"] == "Terminal":
                    self.in_terminal = True

            if self.in_terminal:
                if not was_in_terminal:
                    self.scene.enter_terminal(obj)

            # retest incx
            incx = test_incx(incx, incy)
            if incx == 0:
                self.cframe = 1

        if incx or incy:
            if not self.walk.playing:
                self.walk.play()

            if incy == 0:
                self.dir = 0 if incx>0 else 1
            if incx == 0:
                self.dir = 3 if incy>0 else 2
            self.x += incx
            self.y += incy

            self.sprite.x = int(self.x)
            self.sprite.y = HEIGHT-int(self.y)

            self.fdelay += dt
            if self.fdelay > 0.2:
                self.fdelay = 0
                self.cframe += 1
                if self.cframe > 3:
                    self.cframe = 0

                self.sprite.image = self.frames[self.dframes[self.dir][self.cframe]]
        else:
            if self.walk.playing:
                self.walk.pause()
            if self.cframe != 0:
                self.cframe = 0
                self.fdelay = 0.2
                self.sprite.image = self.frames[self.dframes[self.dir][self.cframe]]

        # lasers!
        mx = self.x//self.map.data["tilewidth"]
        my = self.y//self.map.data["tileheight"]
        if (mx, my) in self.map.objectgroups["Entities"]:
            obj = self.map.objectgroups["Entities"][mx, my]
            if obj["type"] == "Laser" and obj["visible"]:
                if obj["properties"]["dir"] == "v":
                    if 6 < self.x % self.map.data["tilewidth"] < 11:
                        self.scene.laser_hit()
                elif obj["properties"]["dir"] == "h":
                    if 15 < self.y % self.map.data["tileheight"] < 20:
                        self.scene.laser_hit()


class PlayScene(Scene):

    CRACK_TIME = 12
    MAX_SCAN = 255
    MAX_LINK = 5

    player = pyglet.media.Player()

    def __init__(self, window, **kwargs):
        super(PlayScene, self).__init__(window, **kwargs)

        self.font = get_font("default")
        self.font_n = get_font("numbers")
        self.targets = get_texture_sequence("targets.png", 32, 12, 0, 0)

        stage = self.window.current_stage
        self.map = Map.load_json(pyglet.resource.file("%s.json" % stage.lower().replace(" ", "-")))

        x = int(self.map.data["properties"]["start_x"])*int(self.map.data["tilewidth"])+8
        y = (int(self.map.data["properties"]["start_y"])+1)*int(self.map.data["tileheight"])-int(self.map.data["tileheight"])//2
        self.map.set_viewport(0, 0, WIDTH, HEIGHT)

        self.loading_runner = pyglet.resource.media("loading_runner.wav", streaming=False)

        self.loading_runner.play()
        self.p = Runner(x, y, self, self.map, self.window.controls)

        # build the HUD
        self.batch = pyglet.graphics.Batch()

        self.was_disconnected = None
        img = get_texture("disconnected.png")
        self.disconnected = Sprite(img, x=0, y=HEIGHT//2-img.height//2, batch=self.batch, group=OrderedGroup(3))
        self.disconnected.visible = False
        img = get_texture("clear.png")
        self.cleared = Sprite(img, x=0, y=HEIGHT//2-img.height//2, batch=self.batch, group=OrderedGroup(3))
        self.cleared.visible = False

        self.grid_scan_label = self.font.render(self.batch, WIDTH-2, HEIGHT-14, "Grid Scan", align="right")

        self.warn = pyglet.resource.media("locked.wav", streaming=False)
        self.last_warn = None
        self.grid_scan_delay = 0
        self.grid_scan = self.MAX_SCAN
        self.laser_hit_red = False
        self.laser_hit_delay = 0
        self.numbers = None
        self.grid_scan_clock()

        self.link_level = self.MAX_LINK
        self.update_link_levels()

        self.terminal_count = len(self.map.objectgroups["Entities"].get_by_type("Terminal"))
        self.cracking = pyglet.resource.media("cracking.wav", streaming=False)
        self.cracked = pyglet.resource.media("cracked.wav", streaming=False)
        self.disconnect_short = pyglet.resource.media("disconnect_short.wav", streaming=False)
        self.change_target = pyglet.resource.media("target.wav", streaming=False)
        self.cracking_sound = None
        self.terminal = None
        self.terminal_obj = None
        self.terminal_delay = 0
        self.terminal_counter = 0
        self.terminal_target = 0
        self.cracked_message = None
        self.cracked_message_delay = 0

        self.zap = pyglet.resource.media("zap.wav", streaming=False)

        self.entities = []

        self.enemies = True
        try:
            for e in self.map.objectgroups["Entities"]["Enemy"]:
                self.spawn_enemy(int(e["x"])+8, int(e["y"])-8)
                e["visible"] = False
        except KeyError:
            self.enemies = False

        source = pyglet.resource.media("uplink-loop.ogg")
        sc_group = pyglet.media.SourceGroup(source.audio_format, None)
        sc_group.queue(source)
        sc_group.loop = True
        self.player.queue(sc_group)
        if self.window.state["music"]:
            self.player.play()

    def enter_terminal(self, obj):
        logging.debug("enter_terminal")
        self.terminal_obj = obj
        self.terminal_delay = 0
        self.terminal_counter = 0
        x = obj["x"]+self.map.data["tilewidth"]//2
        y = obj["y"]-self.map.data["tileheight"]//2-8
        x, y = self.map.viewport_to_screen(x, y)
        self.terminal = self.font.render(self.batch, x, y, "Cracking", align="center")
        self.target = Sprite(self.targets[0], self.terminal.x+self.terminal.width//2-16, y+self.terminal.height-4, batch=self.batch)
        self.terminal_target = 0

    def prev_target(self):
        if self.terminal_target > 0:
            self.terminal_target -= 1
        else:
            self.terminal_target = len(self.targets)-1
        self.target.image = self.targets[self.terminal_target]
        self.change_target.play()

    def next_target(self):
        if self.terminal_target < len(self.targets)-1:
            self.terminal_target += 1
        else:
            self.terminal_target = 0
        self.target.image = self.targets[self.terminal_target]
        self.change_target.play()

    def exit_terminal(self, done=False):
        logging.debug("exit_terminal")
        self.terminal.delete()
        self.terminal = None
        self.target.delete()
        self.target = None
        if self.cracking_sound and self.cracking_sound.playing:
            self.cracking_sound.next_source()
            del self.cracking_sound
            self.cracking_sound = None
        if not done and self.terminal_counter > 0:
            self.terminal_counter = 0
            self.disconnect_short.play()
        if done:
            self.cracked.play()

    def update_link_levels(self):
        self.link_levels = pyglet.graphics.Batch()
        x = 202
        y = HEIGHT-24
        w = 5
        h = 5
        for i in range(self.MAX_LINK):
            self.link_levels.add(4, gl.GL_QUADS, OrderedGroup(0),
                                ('v2f', (x, y, x, y-h, x+w, y-h, x+w, y)),
                                ('c4f', (1, 1, 1, 0.2)*4),
                                )
            if i < self.link_level:
                self.link_levels.add(4, gl.GL_QUADS, OrderedGroup(1),
                                    ('v2f', (x, y, x, y-h, x+w, y-h, x+w, y)),
                                    ('c4f', (1, 1, 1, 1)*4),
                                    )
            x += w+3
            y += 5
            h += 5

    def laser_hit(self):
        self.laser_hit_delay = 1
        self.grid_scan_delay = 1
        self.laser_hit_red = True

    def grid_scan_clock(self):
        if self.numbers:
            self.numbers.delete()
        self.numbers = self.font_n.render(self.batch, WIDTH-16, HEIGHT-30, "%03d" % self.grid_scan, align="right")
        if self.grid_scan < 11 or self.laser_hit_red:
            for sprite in self.numbers.sprites:
                sprite.color = (224, 60, 40)
            if not self.last_warn or not self.last_warn.playing:
                self.last_warn = self.warn.play()

    def disconnection(self, reason):
        self.batch.add(4, gl.GL_QUADS, OrderedGroup(2),
                      ('v2f', (0, 0, 0, HEIGHT, WIDTH, HEIGHT, WIDTH, 0)),
                      ('c4f', (0, 0, 0, 0.6)*4),
                      )
        if reason:
            self.disconnected.visible = True
            self.was_disconnected = self.font.render(self.batch, WIDTH//2, HEIGHT//2-16, reason, align="center", group=OrderedGroup(4))
            self.disconnect_short.play()
        else:
            self.cleared.visible = True
            # not exactly, but works
            self.was_disconnected = True

    def update(self, dt):

        if self.was_disconnected:
            if self.window.controls.action or self.window.controls.escape:
                self.window.controls.clear()
                self.window.to_stage_select()
            return

        if not self.p.loading:
            self.grid_scan_delay += dt
            if self.grid_scan_delay > 1:
                self.grid_scan -= 1
                self.grid_scan_delay = 0
                self.grid_scan_clock()

            self.laser_hit_delay = max(0, self.laser_hit_delay-dt)
            if self.laser_hit_red and self.laser_hit_delay == 0:
                self.laser_hit_red = False
                if self.grid_scan > 10:
                    for sprite in self.numbers.sprites:
                        sprite.color = (255, 255, 255)

            if self.grid_scan <= 0:
                self.grid_scan = 0
                if self.p.walk.playing:
                    self.p.walk.pause()
                self.disconnection("Connection Reset by Peer")
                return

            if self.link_level <= 0:
                if self.p.walk.playing:
                    self.p.walk.pause()
                self.disconnection("No Carrier")
                return

        if self.cracked_message:
            self.cracked_message_delay += dt
            if self.cracked_message_delay > 1:
                self.cracked_message.delete()
                self.cracked_message = None

        if self.terminal:
            self.terminal_delay += dt
            if self.terminal_delay > 0.5:
                self.terminal_counter += 1
                self.terminal_delay = 0
                if self.terminal_counter == self.CRACK_TIME:
                    self.p.in_terminal = False
                    self.terminal_obj["type"] = ""
                    # FIXME this should be defined in the object
                    self.terminal_obj["gid"] = 21
                    logging.debug("cracked terminal!")

                    if self.terminal_target == 0:
                        msg = "ACCESS GRANTED"
                        for obj in self.map.on_screen_type("Door"):
                            obj["visible"] = False
                    elif self.terminal_target == 1:
                        msg = "DISABLED"
                        names = set([o["name"] for o in self.map.on_screen_type("Laser")])
                        for name in names:
                            for obj in self.map.objectgroups["Entities"][name]:
                                if obj["type"] != "Laser" or not obj["visible"]:
                                    continue
                                # FIXME this should be defined in the map
                                if obj["gid"] == 23:
                                    obj["gid"] = 22
                                elif obj["gid"] == 25:
                                    obj["gid"] = 29
                                elif obj["gid"] == 26:
                                    obj["gid"] = 30
                                else:
                                    obj["visible"] = False
                                obj["type"] = "DisabledLaser"
                    elif self.terminal_target == 2:
                        msg = "LINK UP"
                        self.link_level = self.MAX_LINK
                        self.update_link_levels()
                    elif self.terminal_target == 3:
                        msg = "FIREWALLED"
                        self.grid_scan = min(self.MAX_SCAN, self.grid_scan+16)

                    self.map.invalidate()

                    self.cracked_message_delay = 0
                    self.cracked_message = self.font.render(self.batch, self.terminal.x+self.terminal.width//2, self.terminal.y+12, msg, align="center")
                    self.exit_terminal(True)
                    self.terminal_target = 0

                    self.terminal_count -= 1
                    if self.terminal_count == 0:
                        if self.p.walk.playing:
                            self.p.walk.pause()
                        self.window.state["done"].append(self.window.current_stage)
                        self.window.save_config()
                        self.disconnection(None)
                else:
                    self.cracking_sound = self.cracking.play()

        self.p.update(dt)

        self.entities[:] = [e for e in self.entities if self.filtering(e, dt)]

        super(PlayScene, self).update(dt)

    def filtering(self, e, dt):
        e.update(dt)

        if isinstance(e, Zap):
            if e.owner != "player" and e.collision(self.p):
                self.warn.play()
                self.link_level -= 1
                self.update_link_levels()
                e.alive = False
            if e.owner == "player":
                for other in self.entities:
                    if isinstance(other, EnemyRunner) and other.alive and e.collision(other):
                        e.alive = False
                        other.hit = True
        return e.alive

    def add_zap(self, x, y, dir):
        self.zap.play()
        self.entities.append(Zap("player", x, y, dir, self.map))

    def add_enemy_zap(self, x, y, dir):
        self.zap.play()
        self.entities.append(Zap("enemy", x, y, dir, self.map))

    def spawn_enemy(self, x, y):
        self.entities.append(EnemyRunner(x, y, self, self.map))

    def draw(self):

        self.map.set_focus(self.p.x, self.p.y)
        self.map.draw()

        # FIXME: would be nice to include this in the batch
        if self.terminal:
            x = self.terminal.x-4
            y = self.terminal.y
            tw = self.terminal.width+4
            w = int((float(tw)*self.terminal_counter)/self.CRACK_TIME)
            h = self.terminal.height+2
            gl.glPushAttrib(gl.GL_CURRENT_BIT)
            gl.glColor4f(1.00, 1.00, 1.00, 0.4)
            pyglet.graphics.draw(4, gl.GL_QUADS, ('v2f', (x, y, x+tw, y, x+tw, y+h, x, y+h,)))
            gl.glColor4f(0.34, 0.82, 0.19, 0.9)
            pyglet.graphics.draw(4, gl.GL_QUADS, ('v2f', (x, y, x+w, y, x+w, y+h, x, y+h,)))
            gl.glPopAttrib()

        self.batch.draw()
        self.link_levels.draw()

    def delete(self):
        if self.p.walk.playing:
            self.p.walk.pause()
            self.p.walk = None
        if self.player.playing:
            self.player.pause()
            self.player = None

