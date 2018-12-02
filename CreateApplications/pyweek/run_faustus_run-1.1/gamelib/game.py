from __future__ import division

import pyglet
from pyglet.window import key
from pyglet.gl import *

from gamelib import app
from gamelib import ability
from gamelib import interface
from gamelib import vector
from gamelib import worldgen
from gamelib import particle
from gamelib import sound
from gamelib.constants import *
from gamelib import menu

from gamelib import world

floor_spec = [
      # (depth, texture_name, texture_scale, texture_offset, color)
        (20, 'crystal.png', 1000, vector.zero, (0, 140, 0, 255)),
        (50, 'crystal.png', 1000, (0.2, 0.2), (150, 100, 0, 255)),
        ]

class ImageButton(interface.Image):

    callback = interface.Attribute(None)
    fade = interface.Attribute(1.0)
    _focused = False

    def on_mouse_motion(self, x, y, dx, dy):
        if self.contains_coordinates(x, y):
            if not self._focused:
                self._focused = True
        elif self._focused:
            self._focused = False

    def on_mouse_release(self, x, y, button, modifiers):
        self.callback[0](*self.callback[1:])
        return True

class OrderTextureGroup(pyglet.graphics.TextureGroup):
    def __init__(self, order, texture, parent=None):
        super(OrderTextureGroup, self).__init__(texture, parent)
        self.order = order
    def __lt__(self, other):
        if isinstance(other, OrderTextureGroup):
            return self.order < other.order
        return super(OrderTextureGroup, self).__lt__(other)
    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
            self.order == other.order and
            self.texture.target == other.texture.target and
            self.texture.id == other.texture.id and
            self.parent == other.parent)

class GameScene(menu.Fader):

    def __init__(self, tutorial=False):
        self.tutorial = tutorial
        self.fps = pyglet.clock.ClockDisplay()
        if self.tutorial:
            sd = -250
        else:
            sd = app.state.start_dist
        self.world = world.World(starting_distance=sd)
        self.build_world_batch()
        self.world.place_player()

        self.camera = app.interface.add(interface.Camera,
                world_height = WORLD_HEIGHT,
                world_angle = 0.0,
                draw_world = self.draw_world,
                camera_anchor_y = 'bottom',
                scissor = True,
                )

        self.distance = app.interface.add(interface.Text,
                text = u'',
                font_size = 0.04,
                halign = 'right',
                valign = 0.91,
                anchor_y = 'top',
                margin = 0.02,
                font_name = DEFAULT_FONT,#'Silkscreen',
                )

        self.impending = app.interface.add(interface.Text,
                text = u'',
                font_size = 0.04,
                halign = 'left',
                valign = 0.91,
                anchor_y = 'top',
                margin = 0.02,
                font_name = DEFAULT_FONT,#'Silkscreen',
                )

        self.energy_bg = app.interface.add(interface.Color,
                halign = 'right',
                valign = 'top',
                width = 0.5,
                height = 0.12,
                color = (0,0,0, 1),
                frame_color = (0.5, 0.5, 0.5, 1),
                frame_width = 0.01,
                margin = 0.02,
                )

        self.energy = self.energy_bg.add(interface.Color,
                halign = 'right',
                color = (0, 0, 1, 1),
                )

        self.energy_bg.add(interface.Text,
                font_size = 0.04,
                font_name = DEFAULT_FONT,#'Silkscreen',
                halign = 'right',
                valign = 0.3,
                text = u'Energy',
                margin = (0.2, 0.0),
                )

        self.boss_bg = app.interface.add(interface.Color,
                halign = 'left',
                valign = 'top',
                width = 0.5,
                height = 0.12,
                color = (0,0,0, 1),
                frame_color = (0.5, 0.5, 0.5, 1),
                frame_width = 0.01,
                margin = 0.02,
                )

        self.boss = self.boss_bg.add(interface.Color,
                halign = 'left',
                color = (1, 0, 0, 1),
                )

        self.boss_bg.add(interface.Text,
                font_size = 0.04,
                font_name = DEFAULT_FONT,#'Silkscreen',
                halign = 'left',
                valign = 0.3,
                text = u'Mephistopheles Health',
                margin = (0.2, 0.0),
                )

        self.message = app.interface.add(interface.Text,
                font_size = 0.04,
                font_name = DEFAULT_FONT,#'Silkscreen',
                halign = 'left',
                valign = 'bottom',
                width = 1.0,
                padding = 0.02,
                text = u'message area',
                background_color = (0, 0, 0, 0.75),
                )

        self.abilities = app.interface.add(interface.Horizontal,
                valign = 'bottom',
                halign = 'right',
                spacing = 0.02,
                padding = 0.02,
                margin = 0.02
                )

        for i, up in enumerate(app.state.current_spells):
            if up is not None:
                button = self.abilities.add(ImageButton,
                        height = 0.08,
                        image = pyglet.resource.texture(up.image),
                        callback = (self.do_change_ability, up),
                        )
                button.add(interface.Text,
                        font_size = 0.04,
                        font_name = DEFAULT_FONT,#'Silkscreen',
                        text = unicode(i+1),
                        color = (0.0, 0.0, 0.0, 1.0),
                        )

        self.victory = app.interface.add(interface.Image,
            width = 0.8,
            image = pyglet.resource.texture('victory.png'),
            )

        self.victory.visible = False

        self.message.visible = False
        self.message_queue = []
        self.message_time = None

        self.camera.camera_xoffset = self.world.player.pos.x
        self.camera.camera_yoffset = 0
        self.distance_correction = None

        app.control.set_cursor('cursor2.png')
        self.do_change_ability(app.state.current_spells[0])
        self.particle_systems = []

        if self.tutorial:
            self.set_message('Use the W, A and D keys to move and jump.', 120)
            self.set_message('Use the mouse to aim and cast spells', 120)
        self.tutorial_flags = set()

        self.world.push_handlers(self)

        menu.Fader.__init__(self)

        app.music.change_track('Hitman.ogg')

    def on_victory(self):
        self.victory.visible = True
        self.victory.fade = -0.4
        app.music.change_track('RunningFanfare.ogg')
        def x(dt):
            from gamelib import menu
            self.start_fade(1.0, (app.control.switch, menu.MainMenuScene))
        pyglet.clock.schedule_once(x, 20.0)

    def tut(self, flag):
        if self.tutorial:
            if flag not in self.tutorial_flags:
                self.tutorial_flags.add(flag)
                return True
        return False

    def on_collect_scroll(self):
        app.state.upgrade_coins += 1
        app.state.serialise()
        sound.scroll()
        if self.tut('first scroll'):
            self.set_message('You found a scroll!', 120)
            self.set_message('You can use it to gain new powers later.', 120)

    def on_player_stun(self):
        sound.hit()
        if self.tut('first stun'):
            self.set_message('Getting hit will slow you down.', 120)

    def on_ability(self, ab):
        if ab.effect:
            ab.effect()

    def on_player_dead(self):
        self.set_message('Mephistopheles caught you!', 120)
        self.do_exit(True)

    def set_message(self, message, time):
        self.message_queue.append((message, time))

    def build_world_batch(self):
        self.batch = pyglet.graphics.Batch()
        def floorgen():
            idx = 0
            while True:
                yield self.world.floor_points[idx]
                idx += 1
        floor = floorgen()
        self.world_batch_generators = [floor]
        for size, texture, tscale, toff, color in floor_spec:
            newfloor = worldgen.deepen_infinite_floor(self.world.floor_points, size)
            self.world_batch_generators.append(newfloor)
        self.world_vlists = []
        self.feature_vlists = []
        count, feature_count = self.world.extend_floor(5000, quietly=True)
        self.old_floor_ps = [next(f) for f in self.world_batch_generators]
        self.extend_world_batch(count-1, feature_count)

    def extend_world_batch(self, count, feature_count):
        wbgs = self.world_batch_generators
        vdatas = [[] for _ in xrange(len(wbgs) - 1)]
        cdatas = [[] for _ in xrange(len(wbgs) - 1)]
        tdatas = [[] for _ in xrange(len(wbgs) - 1)]
        for i in xrange(count+1):
            if i == 0:
                ps = self.old_floor_ps
            else:
                ps = [next(f) for f in wbgs]
            ps[-1] = vector.v(ps[-1].x, 0)
            for i, (size, texture, tscale, toff, color) in enumerate(floor_spec):
                vdatas[i].extend(ps[0])
                vdatas[i].extend(ps[i+1])
                cdatas[i].extend(2*color)
                tdatas[i].extend(ps[0]/tscale+toff)
                tdatas[i].extend(ps[i+1]/tscale+toff)
            self.old_floor_ps = ps
        vlists = []
        for i, (size, texture, tscale, toff, color) in enumerate(floor_spec):
            tex = pyglet.resource.texture(texture)
            vdatas[i] = 2*vdatas[i][:2] + vdatas[i] + 2*vdatas[i][-2:]
            cdatas[i] = 2*cdatas[i][:4] + cdatas[i] + 2*cdatas[i][-4:]
            tdatas[i] = 2*tdatas[i][:2] + tdatas[i] + 2*tdatas[i][-2:]
            vlists.append(self.batch.add(
                    len(vdatas[i]) // 2,
                    GL_TRIANGLE_STRIP,
                    OrderTextureGroup(-i, tex),
                    ('v2f', vdatas[i]),
                    ('c4B', cdatas[i]),
                    ('t2f', tdatas[i]),))
        self.world_vlists.append((count, vlists))

        for idx in xrange(feature_count):
            vdatas = [[] for _ in xrange(len(floor_spec))]
            cdatas = [[] for _ in xrange(len(floor_spec))]
            tdatas = [[] for _ in xrange(len(floor_spec))]
            surface = self.world.features[idx]
            floors = [surface] + [worldgen.deepen_feature(surface, s[0]) for s in floor_spec]
            for j, ps in enumerate(zip(*floors)):
                c = (surface[j] + surface[-(j+1)]) / 2
                ps = list(ps)
                ps[-1] = c
                for i, (size, texture, tscale, toff, color) in enumerate(floor_spec):
                    vdatas[i].extend(ps[0])
                    vdatas[i].extend(ps[i+1])
                    cdatas[i].extend(2*color)
                    tdatas[i].extend(ps[0]/tscale+toff)
                    tdatas[i].extend(ps[i+1]/tscale+toff)
            vlists = []
            for i, (size, texture, tscale, toff, color) in enumerate(floor_spec):
                vdatas[i] = 2*vdatas[i][:2] + vdatas[i] + vdatas[i][:4] + 2*vdatas[i][-2:]
                cdatas[i] = 2*cdatas[i][:4] + cdatas[i] + cdatas[i][:8] + 2*cdatas[i][-4:]
                tdatas[i] = 2*tdatas[i][:2] + tdatas[i] + tdatas[i][:4] + 2*tdatas[i][-2:]
                tex = pyglet.resource.texture(texture)
                vlists.append(self.batch.add(
                        len(vdatas[i]) // 2,
                        GL_TRIANGLE_STRIP,
                        OrderTextureGroup(-i, tex),
                        ('v2f', vdatas[i]),
                        ('c4B', cdatas[i]),
                        ('t2f', tdatas[i]),))
            right = max(v.x for v in surface)
            self.feature_vlists.append((surface, right, vlists))

    def tick(self):
        menu.Fader.tick(self)
        self.world.tick()

        if self.victory.visible:
            self.victory.fade = min(1.0, self.victory.fade + 0.001)

        # Update entity vertex lists.
        self.world.player.update_vlist(self.batch)
        for e in self.world.objects:
            e.update_vlist(self.batch)

        # Update camera position.
        self.camera.camera_xoffset += \
            max(0, self.world.player.pos.x - self.camera.camera_xoffset) * 0.1

        # Update world geometry and batches.
        if len(self.world_vlists) > 2:
            count, vlists = self.world_vlists.pop(0)
            for vlist in vlists:
                vlist.delete()
            self.world.delete_floor(count)
        d1, _ = self.camera.transform_root_coordinates(0, 0)
        d2, _ = self.camera.transform_root_coordinates(app.window.width, 0)
        if 2 * d2 - d1 > self.world.floor_points[-1].x:
            count = self.world.extend_floor(2 * (d2 - d1))
            self.extend_world_batch(*count)
        self.world.player.left_wall = d1

        # Update feature geometry.
        for surface, right, vlists in list(self.feature_vlists):
            if right < d1:
                for v in vlists:
                    v.delete()
                self.world.remove_feature(surface)
            self.feature_vlists.remove((surface, right, vlists))

        self.parallax_pos = d1/PARALLAX_FACTOR
        d = self.world.get_distance()
        if d >= 0:
            if self.tut('demon time'):
                self.set_message('Mephistopheles is chasing you!', 120)
                self.set_message('His distance from you is shown in the top left.', 120)
                self.set_message('Good luck!', 120)
            self.distance.text = '%d m' % int(d)
            nd = self.world.get_nemesis_distance()
            if nd > 0:
                self.impending.text = '<< %d m' % int(nd)
            else:
                self.impending.text = u''
        if DEBUG:
            self.world.energy = MAX_ENERGY

        self.energy.width = (self.world.energy / MAX_ENERGY)
        self.boss.width = (self.world.nemesis.hp / world.Demon.hp)
        self.boss_bg.visible = self.world.nemesis.vincible

        for ps in list(self.particle_systems):
            ps.tick()
            if ps.is_dead():
                ps.vlist.delete()
                self.particle_systems.remove(ps)

        if not self.message_time:
            if self.message_queue:
                m, t = self.message_queue.pop(0)
                self.message.text = m
                self.message_time = t
                self.message.visible = True
            else:
                self.message_time = None
                self.message.visible = False
        elif self.message_time is not None:
            self.message_time -= 1

    parallax_pos = 0.0
    parallax_tex = pyglet.resource.texture('bg.png')

    def draw_world(self):
        w, h = app.interface.content_size
        t = self.parallax_tex
        glEnable(t.target)
        glBindTexture(t.target, t.id)
        tx1, ty1 = t.tex_coords[0:2]
        tx2, ty2 = t.tex_coords[6:8]
        cx1, cy1 = self.camera.transform_root_coordinates(0, 0)
        cx2, cy2 = self.camera.transform_root_coordinates(w, h)
        s = (ty2 - ty1) / (cy2 - cy1)
        tx1 = cx1 * s
        ty1 = cy1 * s
        tx2 = cx2 * s
        ty2 = cy2 * s
        tx1 -= self.parallax_pos
        tx2 -= self.parallax_pos
        pyglet.graphics.draw(4, GL_QUADS,
                ('v2f', (cx1, cy1, cx2, cy1, cx2, cy2, cx1, cy2)),
                ('c4B', (255, 255, 255, 255) * 4),
                ('t2f', (tx1, ty1, tx2, ty1, tx2, ty2, tx1, ty2)),
                )
        glDisable(t.target)
        self.batch.draw()
        for ps in self.particle_systems:
            ps.batch.draw()

    def do_change_ability(self, up):
        for ab in ability.abilities:
            if ab.upgrade is up: break
        else:
            assert False
        self.world.player.ability = ab()
        for im in self.abilities.children:
            if im.callback[1] is up:
                im.scale = 2.0
                im.order = 1
            else:
                im.scale = 1.0
                im.order = 0

    def on_key_press(self, symbol, modifiers):
        numbers = [key._1, key._2, key._3, key._4]
        if symbol in numbers:
            idx = numbers.index(symbol)
            if idx < len(app.state.current_spells):
                self.do_change_ability(app.state.current_spells[idx])
        elif symbol == key.ESCAPE:
            self.do_exit()
        else:
            return
        return True

    def do_exit(self, long=False):
        if long:
            self.start_fade(1.0, (app.control.switch, menu.PowerSelectScene), 3.0)
        else:
            self.start_fade(1.0, (app.control.switch, menu.PowerSelectScene))

    def on_mouse_press(self, x, y, btns, mods):
        if not self.world.player.destroyed:
            self.world.activate_ability(vector.v(self.camera.transform_window_coordinates(x, y)))
    
            #self.particle_systems.append(particle.ParticleSystem(
            #    pos=self.world.player.pos,
            #    color=(200, 0, 200),
            #    alpha=127,
            #    autoadd=True,
            #    ))
            if self.tut('first spell'):
                self.set_message('Good work!', 120)
                self.set_message('Press the numbers 1-4 to switch between spells.', 120)
            elif self.tut('second spell'):
                self.set_message('Remember to keep an eye on your energy level.', 120)

    def on_draw(self):
        app.window.clear()
        app.interface.draw()
        if DEBUG:
            self.fps.draw()
