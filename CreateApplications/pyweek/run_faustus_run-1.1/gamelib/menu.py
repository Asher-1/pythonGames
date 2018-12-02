"""gamelib.menu -- game interface and menus

"""

import pyglet

from gamelib import app
from gamelib import data
from gamelib import interface
from gamelib import sound
from gamelib.data import upgrades
from gamelib.constants import *


class EventBlock(object):
    def ev(*args, **kwds):
        return None
    for name in pyglet.window.Window.event_types:
        locals()[name] = ev
EventBlock = EventBlock()

class Fader(object):
    def __init__(self):
        self.fade = app.interface.add(interface.Color,
                color = (0, 0, 0, 1.0),
                )
        self.fade_rate = None
        self.fade_alpha = None
        self.fade_target = None
        self.fade_action = None
        self.start_fade(0.0, ((lambda: None),))
    def tick(self):
        if self.fade_rate:
            self.fade_alpha += self.fade_rate
            alpha = max(0.0, min(1.0, self.fade_alpha))
            self.fade.color = self.fade.color[:3] + (alpha,)
            if (self.fade_rate > 0 and self.fade_alpha >= self.fade_target) or\
               (self.fade_rate < 0 and self.fade_alpha <= self.fade_target):
                app.window.remove_handlers(EventBlock)
                func = self.fade_action[0]
                args = self.fade_action[1:]
                func(*args)
                self.fade_rate = self.fade_alpha = self.fade_target = self.fade_action = None
    def start_fade(self, target, action, time=0.3):
        self.fade_alpha = self.fade.color[3]
        self.fade_target = target
        r = abs(self.fade_target - self.fade_alpha) / time / TICK_RATE
        self.fade_rate = r * [-1, 1][target > self.fade_alpha]
        self.fade_target += self.fade_rate * 10
        self.fade_action = action
        app.window.push_handlers(EventBlock)



class ImageButton(interface.Image):

    callback = interface.Attribute(None)
    fade = interface.Attribute(1.0)
    info = interface.Attribute(None)
    info_text = interface.Attribute(u'')
    focus_color = interface.Attribute(None)
    unfocus_color = interface.Attribute(None)
    _focused = False

    def on_mouse_motion(self, x, y, dx, dy):
        if self.contains_coordinates(x, y):
            if not self._focused:
                self._focused = True
                if self.focus_color:
                    self.color = self.focus_color
                if self.info is not None:
                    self.info.text = self.info_text
                self.scale = 1.3
        elif self._focused:
            self._focused = False
            if self.unfocus_color:
                self.color = self.unfocus_color
            if self.info is not None:
                self.info.text = u''
            self.scale = 1.0
    def on_mouse_release(self, x, y, button, modifiers):
        sound.click()
        self.callback[0](*self.callback[1:])
        return True

class TextButton(interface.Text):

    focus_color = interface.Attribute((1.0, 1.0, 0.0, 1.0))
    unfocus_color = interface.Attribute((1.0, 1.0, 1.0, 1.0))
    callback = interface.Attribute(None)

    _focused = False
    def focus(self):
        self.color = self.focus_color
    def unfocus(self):
        self.color = self.unfocus_color
    def on_mouse_motion(self, x, y, dx, dy):
        if self.contains_coordinates(x, y):
            if not self._focused:
                self._focused = True
                self.focus()
        elif self._focused:
            self._focused = False
            self.unfocus()
    def on_mouse_release(self, x, y, button, modifiers):
        self.callback[0](*self.callback[1:])

class PowerMenuItem(interface.MenuItem):

    image_width = interface.Attribute(0.2)
    spacing = interface.Attribute(0.02)
    font_size = interface.Attribute(0.04)
    info = interface.Attribute(None)
    help_text = interface.Attribute(u'')
    color = interface.Attribute((0, 0, 0, 1))

    def init_panel(self):
        self.image_panel = self.add(interface.Image,
                width = self.image_width,
                halign = 'left',
                )
        self.text_panel = self.add(interface.Text,
                width = 1.0 - self.image_width - self.spacing,
                anchor_x = 'left',
                halign = self.image_width + self.spacing,
                font_size = self.font_size,
                font_name = DEFAULT_FONT,
                align = 'left',
                color = self.color,
                )
        self.background_texture = pyglet.resource.texture('highlight.png')
        self.background_color = (1,1, 0.0, 0.0)

    def compute_content_size(self):
        pmvw, pmvh = self.parent.max_view_size
        return pmvw, pmvw * self.image_width

    def set_upgrade(self, upgrade, spell=True, greyed=False, missing=None):
        if upgrade is None:
            self.image_panel.image = None
            self.text_panel.text = u'[empty slot]'
            self.help_text = 'Click on the slot to choose a spell.'
        else:
            self.image_panel.image = pyglet.resource.texture(upgrade.image)
            if spell:
                self.text_panel.text = upgrade.spell_name + '\n' + upgrade.spell_caption
                self.help_text = upgrade.spell_text
            else:
                self.text_panel.text = upgrade.name + '\n' + upgrade.caption
                self.help_text = upgrade.text
                if greyed:
                    self.text_panel.text = upgrade.name + '\nNo scrolls available.'
                    self.image_panel.image = pyglet.resource.texture('lock.png')
                    self.help_text = 'No scrolls available.'
                if missing:
                    req = ["'" + up.spell_name + "'" for up in missing]
                    reqs = ', '.join(req[:-1])
                    if reqs: reqs = reqs + ' and ' + req[-1]
                    else: reqs = req[-1]
                    self.text_panel.text = upgrade.name + '\nRequires %s.' % reqs
                    self.help_text = 'Requires %s.' % reqs
        self.unselect()

    _focused = False
    _selected = False

    def activate(self):
        if self._selected:
            self.unselect()
        else:
            for c in self.parent.children:
                c.unselect()
            if self.parent.selectable:
                self.select()
        sound.click()
        super(PowerMenuItem, self).activate()

    def set_bg_color(self, c):
        vl = self.background_vlist
        ca = tuple(c) + (vl.colors[3],)
        self._set_bg(ca)
    def set_bg_alpha(self, a):
        vl = self.background_vlist
        ca = tuple(vl.colors[0:3]) + (a,)
        self._set_bg(ca)
    def _set_bg(self, ca):
        self.target_color = ca
        vl = self.background_vlist
        vl.colors[:] = ca * 4

    def focus(self):
        if self.parent.focusable:
            self.info.text = self.help_text
            self.image_panel.scale = 1.5
            self.order = 1
            self.outside = True
            self._focused = True
    def unfocus(self):
        if self.parent.focusable:
            self.info.text = u''
            self.image_panel.scale = 1.0
            self.order = 0
            self.outside = False
            self._focused = False
    def select(self):
        self.set_bg_color((255, 255, 0))
        self.set_bg_alpha(255)
        self._selected = True
    def unselect(self):
        self._selected = False
        self.set_bg_alpha(0)

class PowerMenu(interface.Vertical, interface.Menu):
    child_class = PowerMenuItem
    selectable = False
    focusable = True

    def tr_corner(self):
        x, y = self.content_offset
        fx, fy = self.frame_offset
        fw, fh = self.frame_size
        return x + fx + fw - fw/6, y + fy + fh

    def br_corner(self):
        x, y = self.content_offset
        fx, fy = self.frame_offset
        fw, fh = self.frame_size
        return x + fx + fw - fw/6, y + fy

    def tl_corner(self):
        x, y = self.content_offset
        fx, fy = self.frame_offset
        fw, fh = self.frame_size
        return x + fx + fw/6, y + fy + fh

    def bl_corner(self):
        x, y = self.content_offset
        fx, fy = self.frame_offset
        fw, fh = self.frame_size
        return x + fx + fw/6, y + fy

    def compute_content_size(self):
        w, h = super(PowerMenu, self).compute_content_size()
        mw, mh = self.max_view_size
        if mh > h:
            for c in self.children:
                c.yoffset = mh - h
        return max(w, mw), max(h, mh)


class PowerSelect(interface.Panel):

    scene = interface.Attribute(None)

    def init_panel(self):

        self.bg = self.add(interface.Color,
                color = (0.1, 0.1, 0.1, 0.0),
                background_texture = pyglet.resource.texture('hatch.png'),
                background_tiles = 2,
                )

        self.title = self.add(interface.Text,
                height = 0.1,
                valign = 'top',
                font_size = 0.08,
                padding = 0.00,
                margin = 0.00,
                font_name = DEFAULT_FONT,
                color = (0, 0, 0, 1),
                text = u'Prepare!',
                )

        self.info = self.add(interface.Text,
                width = 1.0,
                height = 0.2,
                padding = 0.02,
                margin = 0.02,
                valign = 'bottom',
                font_size = 0.04,
                font_name = DEFAULT_FONT,
                color = (0, 0, 0, 1),
                #background_color = (0,0,0,1),
                #frame_color = (.5,.5,.5,1),
                #frame_width = 0.01,
                )

        self.left_text_attrs = dict(
                height = 0.1,
                width = 0.25,
                padding = (0.02, 0.0),
                margin = (0.02, 0.0),
                halign = 'left',
                anchor_y = 'bottom',
                valign = 0.8,
                font_size = 0.04,
                font_name = DEFAULT_FONT,
                color = (0, 0, 0, 1),
                )
        self.left_attrs = dict(
                height = 0.6,
                width = 0.333,
                padding = 0.02,
                margin = 0.02,
                halign = 'left',
                anchor_y = 'top',
                valign = 0.8,
                scissor = True,
                spacing = 0.02,
                item_options = dict(
                    font_size = 0.02,
                    color = (0, 0, 0, 1),
                    spacing = 0.08,
                    info = self.info,
                    ),
                background_texture = pyglet.resource.texture('sand.png'),
                background_tiles = 5,
                frame_color = (0, 0, 0, 1),
                frame_width = 0.01,
                )
        self.right_text_attrs = dict(self.left_text_attrs)
        self.right_text_attrs.update(dict(
                halign = 'right',
                ))
        self.right_attrs = dict(self.left_attrs)
        self.right_attrs.update(dict(
                halign = 'right',
                ))

        # Active spells.
        self.active_text = self.add(interface.Text,
                text = u'spell slots',
                **self.left_text_attrs
                )
        self.active = self.add(PowerMenu,
                **self.left_attrs
                )
        self.active.selectable = True

        # Available spells
        self.available_text = self.add(interface.Text,
                text = u'spell book',
                **self.right_text_attrs
                )
        self.available = self.add(PowerMenu,
                **self.right_attrs
                )

        # Current upgrades
        self.upgrades_text = self.add(interface.Text,
                text = u'enchantments',
                **self.left_text_attrs
                )
        self.upgrades_text.visible = False
        self.upgrades = self.add(PowerMenu,
                **self.left_attrs
                )
        self.upgrades.visible = False
        # Coming soon
        self.coming_text = self.add(interface.Text,
                text = u'available',
                **self.right_text_attrs
                )
        self.coming_text.visible = False
        self.coming = self.add(PowerMenu,
                **self.right_attrs
                )
        self.coming.visible = False

        self.menu = self.add(interface.Vertical,
                valign = 0.8,
                anchor_y = 'top',
                spacing = 0.02,
                )

        self.menu.add(ImageButton,
                image = pyglet.resource.texture('start_button.png'),
                width = 0.3,
                callback = (self.scene.do_start,),
                info = self.info,
                info_text = u'Start running from the demon.',
                )
        self.sw_button = self.menu.add(ImageButton,
                image = pyglet.resource.texture('enchantments_button.png'),
                width = 0.3,
                callback = (self.scene.do_enchantments,),
                info = self.info,
                info_text = u'Unlock spells and enchantments.',
                )
        self.menu.add(ImageButton,
                image = pyglet.resource.texture('exit_button.png'),
                width = 0.3,
                callback = (self.scene.do_exit,),
                info = self.info,
                info_text = u'Return to the main menu.',
                )
        self.scrolls = self.menu.add(interface.Text,
                text = u'Scrolls: %d' % app.state.upgrade_coins,
                font_size = 0.06,
                font_name = DEFAULT_FONT,
                color = (0, 0, 0, 1),
                )

        for idx in xrange(4):
            item = self.active.add(callback=(self.scene.do_select_active, idx))
            up = app.state.current_spells[idx]
            item.set_upgrade(up)

        self._make_ups()

        tr_x, tr_y = self.active.tr_corner()
        self.left_scroll_up = self.add(ImageButton,
                halign = 'left',
                valign = 'bottom',
                anchor_x = 'center',
                anchor_y = 'bottom',
                width = 0.05,
                xoffset = tr_x,
                yoffset = tr_y,
                image = pyglet.resource.texture('up.png'),
                callback = (self.scene.do_lscroll, 1),
                )

        br_x, br_y = self.active.br_corner()
        self.left_scroll_down = self.add(ImageButton,
                halign = 'left',
                valign = 'bottom',
                anchor_x = 'center',
                anchor_y = 'top',
                width = 0.05,
                xoffset = br_x,
                yoffset = br_y,
                image = pyglet.resource.texture('down.png'),
                callback = (self.scene.do_lscroll, -1),
                )

        tl_x, tl_y = self.available.tl_corner()
        self.right_scroll_up = self.add(ImageButton,
                halign = 'left',
                valign = 'bottom',
                anchor_x = 'center',
                anchor_y = 'bottom',
                width = 0.05,
                xoffset = tl_x,
                yoffset = tl_y,
                image = pyglet.resource.texture('up.png'),
                callback = (self.scene.do_rscroll, 1),
                )

        bl_x, bl_y = self.available.bl_corner()
        self.right_scroll_down = self.add(ImageButton,
                halign = 'left',
                valign = 'bottom',
                anchor_x = 'center',
                anchor_y = 'top',
                width = 0.05,
                xoffset = bl_x,
                yoffset = bl_y,
                image = pyglet.resource.texture('down.png'),
                callback = (self.scene.do_rscroll, -1),
                )

    def _make_ups(self):
        self.scrolls.text = u'Scrolls: %d' % app.state.upgrade_coins
        for c in self.available.children:
            c.destroy()
        for c in self.upgrades.children:
            c.destroy()
        for c in self.coming.children:
            c.destroy()
        for up in upgrades.Upgrade.index['spell']:
            if up in app.state.unlocked_upgrades:
                self.available.add(
                    callback = (self.scene.do_select_available, up),
                    ).set_upgrade(up)
        for up in app.state.unlocked_upgrades:
            if up.category != 'spell':
                item = self.upgrades.add(
                        callback = (lambda: None,),
                        )
                item.set_upgrade(up, False)
        for up, miss in app.state.available_upgrades():
            item = self.coming.add(
                    callback = (self.scene.do_unlock, up),
                    )
            item.set_upgrade(up, False, not app.state.can_upgrade(), missing=miss)
        if app.state.can_upgrade():
            self.sw_button.color = (1, 1, 0)
        else:
            self.sw_button.color = (1, 1, 1)

class PowerSelectScene(Fader):

    def __init__(self, ench=False):

        self.power_select = app.interface.add(PowerSelect,
                scene = self,
                )

        self.selected_slot = None

        self.fps = pyglet.clock.ClockDisplay()

        if ench:
            self.do_enchantments()
        Fader.__init__(self)
        app.music.change_track('MoonlightHall.ogg')

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.do_exit()
        else:
            return False
        return True

    def do_unlock(self, upgrade):
        if app.state.unlock(upgrade):
            sound.enchant()
            self.power_select._make_ups()
        else:
            sound.negative()

    def do_start(self):
        from gamelib import game
        self.start_fade(1.0, (app.control.switch, game.GameScene))

    def do_lscroll(self, n):
        ps = self.power_select
        if ps.coming_text.visible:
            ps.upgrades.scroll_by(0, n)
        else:
            pass

    def do_rscroll(self, n):
        ps = self.power_select
        if ps.coming_text.visible:
            ps.coming.scroll_by(0, n)
        else:
            ps.available.scroll_by(0, n)

    def do_enchantments(self):
        ps = self.power_select
        if ps.coming_text.visible:
            ps.coming_text.visible = False
            ps.upgrades_text.visible = False
            ps.coming.visible = False
            ps.upgrades.visible = False
            ps.active_text.visible = True
            ps.available_text.visible = True
            ps.active.visible = True
            ps.available.visible = True
            ps.sw_button.image = pyglet.resource.texture('enchantments_button.png')
            ps.sw_button.info_text = u'Review your enchantments.'
        else:
            ps.coming_text.visible = True
            ps.upgrades_text.visible = True
            ps.coming.visible = True
            ps.upgrades.visible = True
            ps.active_text.visible = False
            ps.available_text.visible = False
            ps.active.visible = False
            ps.available.visible = False
            ps.sw_button.image = pyglet.resource.texture('spellbook_button.png')
            ps.sw_button.info_text = u'Review your spells.'

    def do_exit(self):
        self.start_fade(1.0, (app.control.switch, MainMenuScene))

    def do_select_active(self, idx):
        self.selected_slot = idx

    def do_select_available(self, upgrade):
        active = self.power_select.active
        if self.selected_slot is not None:
            for idx, up in enumerate(app.state.current_spells):
                if up is upgrade:
                    app.state.current_spells[idx] = None
                    active.children[idx].set_upgrade(None)
                if idx == self.selected_slot:
                    app.state.current_spells[idx] = upgrade
                    active.children[idx].set_upgrade(upgrade)
            app.state.serialise()
            self.selected_slot = None
        elif None in app.state.current_spells:
            found = False
            for idx, up in enumerate(app.state.current_spells):
                if up is None and not found:
                    found = True
                    app.state.current_spells[idx] = upgrade
                    active.children[idx].set_upgrade(upgrade)
                elif up is upgrade:
                    if not found:
                        found = True
                    else:
                        app.state.current_spells[idx] = None
                        active.children[idx].set_upgrade(None)
        app.state.serialise()

    def on_draw(self):
        app.window.clear()
        app.interface.draw()
        self.fps.draw()



## Main Menu ##################################################################

class TextMenuItem(interface.Text, interface.MenuItem):
    focus_color = interface.Attribute((1, 1, 0.0, 1.0))
    unfocus_color = interface.Attribute((0.0, 0.0, 0.0, 1.0))
    def focus(self):
        self.color = self.focus_color
    def unfocus(self):
        self.color = self.unfocus_color
    def activate(self):
        sound.click()
        super(TextMenuItem, self).activate()

class TextMenu(interface.Vertical, interface.Menu):
    child_class = TextMenuItem

class MainMenuScene(Fader):

    def __init__(self):

        self.background = app.interface.add(interface.Color,
                color = (0.1, 0.1, 0.1, 0.0),
                background_texture = pyglet.resource.texture('hatch.png'),
                background_tiles = 2,
                )

        self.title = app.interface.add(interface.Text,
                halign = 'center',
                valign = 'top',
                text = u'Run, Faustus, Run!',
                font_name = DEFAULT_FONT,
                font_size = 0.12,
                color = (0, 0, 0,1),
                )

        self.menu = app.interface.add(TextMenu,
                item_options = dict(
                    font_name = DEFAULT_FONT,
                    font_size = 0.08,
                    color = (0, 0, 0,1),
                    )
                )

        self.menu.add(
                text = u'New Game',
                callback = self.do_start,
                )

        if app.config.state is not None:
            self.menu.add(
                    text = u'Continue',
                    callback = self.do_resume,
                    )

        self.menu.add(
                text=u'Exit',
                callback = self.do_exit,
                )
        Fader.__init__(self)
        app.music.change_track('MoonlightHall.ogg')

    def on_key_press(self, sym, mods):
        if sym == pyglet.window.key.ESCAPE:
            self.do_exit()
        else:
            return
        return True

    def do_start(self):
        from gamelib import game
        app.state.starting_state()
        app.state.serialise()
        self.start_fade(1.0, (app.control.switch, game.GameScene, True))

    def do_resume(self):
        self.start_fade(1.0, (app.control.switch, PowerSelectScene))

    def do_exit(self):
        self.start_fade(1.0, (pyglet.app.exit,))

    def on_draw(self):
        app.window.clear()
        app.interface.draw()

