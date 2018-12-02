import pyglet
from pyglet.gl import *
import random

from gamelib import app
from gamelib import interface
from gamelib import monster
from gamelib import sound
from gamelib import vector
from gamelib.constants import *

## Icons ######################################################################

def load_icon(name):
    icon = pyglet.resource.image(name)
    icon.anchor_x = icon.width / 2
    icon.anchor_y = icon.height / 2
    return icon

_anchor = load_icon('icons/anchor.png')
_focusanchor = load_icon('icons/focusanchor.png')
_selectanchor = load_icon('icons/selectanchor.png')


## Scroll Menu ################################################################

class ScrollMenuItem(interface.MenuItem, interface.Image):

    focus_alpha = interface.Attribute(1.0)
    unfocus_alpha = interface.Attribute(1.0)
    alpha = interface.Tracking('unfocus_alpha')

    focus_scale = interface.Attribute(1.0)
    unfocus_scale = interface.Attribute(1.0)
    scale = interface.Tracking('unfocus_scale')

    focus_color = interface.Attribute((1.0, 1.0, 1.0))
    unfocus_color = interface.Attribute((1.0, 1.0, 1.0))
    color = interface.Tracking('unfocus_color')

    focus_param = interface.Attribute(None)

    def focus(self, key=False):
        self.alpha = self.focus_alpha
        self.scale = self.focus_scale
        self.color = self.focus_color
        if not key:
            self.parent.lab.set_focus(self, self.focus_param, key)

    def unfocus(self, key=False):
        self.alpha = self.unfocus_alpha
        self.scale = self.unfocus_scale
        self.color = self.unfocus_color
        self.parent.lab.set_focus(None, None, key)

    def activate(self):
        super(ScrollMenuItem, self).activate()
        sound.click()

class ScrollMenu(interface.Menu, interface.Vertical):

    scroll_sensitivity = interface.Attribute(0.2)
    target_scroll = interface.Tracking('scroll_yoffset')
    lab = interface.Attribute(None)

    child_class = ScrollMenuItem

    def tick(self):
        delta = (self.target_scroll - self.scroll_yoffset)
        if abs(delta) > 0.5:
            if delta > 0.0:
                self.scroll_yoffset += max(1, delta * 0.1)
            else:
                self.scroll_yoffset += min(-1, delta * 0.1)
    @property
    def scroll_bounds(self):
        cwidth, cheight = self.content_size
        vwidth, vheight = self.view_size
        scroll_min = (vheight - cheight) * (1 - self._sym(self.valign))
        scroll_max = (cheight - vheight) * self._sym(self.valign)
        return scroll_min, scroll_max
    def scroll_top(self, force=False):
        self.target_scroll = self.scroll_bounds[0]
        if force: self.scroll_yoffset = self.target_scroll
    def scroll_bottom(self, force=False):
        self.target_scroll = self.scroll_bounds[1]
        if force: self.scroll_yoffset = self.target_scroll
    def scroll_up(self, steps):
        rwidth, rheight = self.view_size
        self.target_scroll -= steps * self.scroll_sensitivity * rheight
        self.fix_scroll()
    def scroll_down(self, steps):
        rwidth, rheight = self.view_size
        self.target_scroll += steps * self.scroll_sensitivity * rheight
        self.fix_scroll()
    def scroll_child(self, child):
        self.fix_scroll(child)
    def fix_scroll(self, child=None):
        scroll_min, scroll_max = self.scroll_bounds
        if child is not None:
            cwidth, cheight = self.content_size
            vwidth, vheight = self.view_size
            offsetx, offsety = child.content_offset
            chwidth, chheight = child.content_size
            scroll_max = cheight - offsety - chheight + scroll_min
            scroll_min = cheight - offsety - vheight + scroll_min
        if self.target_scroll > scroll_max:
            self.target_scroll = scroll_max
        if self.target_scroll < scroll_min:
            self.target_scroll = scroll_min
    def change_focused(self, child, key=False):
        super(ScrollMenu, self).change_focused(child, key)
        if key: self.fix_scroll(child)
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scroll_down(-scroll_y)
    def set_part_list(self, part_list):
        for child in self.children:
            child.destroy()
        lab = self.lab
        self.add(ScrollMenuItem,
            image = pyglet.resource.image('icons/undo.png'),
            callback = lab.back,
            focus_param = 'back',)
        for part, n in part_list:
            i = self.add(ScrollMenuItem,
                image = pyglet.resource.image('pieces/%s.png' % part.imagename),
                callback = (lab.select_piece, part),
                focus_param = (part, n),)
            #i.add(interface.Image,
            #    halign = 'right',
            #    valign = 'bottom',
            #    anchor_x = 'right',
            #    anchor_y = 'bottom',
            #    width = 0.2,
            #    height = 0.2,
            #    image = pyglet.resource.image('icons/%s.png' % min(5, n)),
            #    )
        self.change_focused(None)
        self.scroll_top(True)
    def set_part_tool_list(self):
        for child in self.children:
            child.destroy()
        lab = self.lab
        self.add(ScrollMenuItem,
            image = pyglet.resource.image('icons/undo.png'),
            callback = lab.back,
            focus_param = 'backmonster',)
        self.add(ScrollMenuItem,
            image = pyglet.resource.image('icons/rotate.png'),
            callback = lab.rotate_part,
            focus_param = 'rotate',)
        self.add(ScrollMenuItem,
            image = pyglet.resource.image('icons/delete.png'),
            callback = lab.delete_part,
            focus_param = 'delete',)
        self.add(ScrollMenuItem,
            image = pyglet.resource.image('icons/mirror.png'),
            callback = lab.flip_part,
            focus_param = 'mirror',)
        self.change_focused(None)
        self.scroll_top(True)
    def set_main_tool_list(self):
        for child in self.children:
            child.destroy()
        lab = self.lab
        self.add(ScrollMenuItem,
            image = pyglet.resource.image('icons/monster1.png'),
            callback = (lab.load_monster, 0),
            focus_param = 'loadmonster0',)
        self.add(ScrollMenuItem,
            image = pyglet.resource.image('icons/monster2.png'),
            callback = (lab.load_monster, 1),
            focus_param = 'loadmonster1',)
        self.add(ScrollMenuItem,
            image = pyglet.resource.image('icons/monster3.png'),
            callback = (lab.load_monster, 2),
            focus_param = 'loadmonster2',)
        self.add(ScrollMenuItem,
            image = pyglet.resource.image('icons/exit.png'),
            callback = lab.exit_lab,
            focus_param = 'exit',)
        self.change_focused(None)
        self.scroll_top(True)
    def set_monster_tool_list(self):
        for child in self.children:
            child.destroy()
        lab = self.lab
        self.add(ScrollMenuItem,
            image = pyglet.resource.image('icons/undo.png'),
            callback = lab.back,
            focus_param = 'back',)
        self.add(ScrollMenuItem,
            image = pyglet.resource.image('icons/rename.png'),
            callback = lab.rename_monster,
            focus_param = 'rename',)
        self.change_focused(None)
        self.scroll_top(True)


## Text Edit ##################################################################

class TextEdit(interface.Text):

    callback = interface.Attribute(None)

    def init_panel(self):
        super(TextEdit, self).init_panel()
        self.caret = pyglet.text.caret.Caret(self.layout)

    def on_key_press(self, symbol, modifiers):
        if symbol != pyglet.window.key.ESCAPE:
            return True

    def on_text(self, text):
        if text == u'\r':
            self.callback(self.text)
            self.visible = False
        else:
            self.caret.on_text(text)
            self.text = self.document.text

    def on_text_motion(self, motion):
        self.caret.on_text_motion(motion)
        self.text = self.document.text

    def on_text_motion_select(self, motion):
        self.caret.on_text_motion_select(motion)
        self.text = self.document.text

    def set_text(self, text):
        self.text = text
        self.caret._set_mark(0)
        self.caret._set_position(len(text))
        self.visible = True


## Laboratory #################################################################

texts = {
    'rotate' : u'rotate this part...',
    'delete' : u'delete this part...',
    'mirror' : u'flip this part...',
    'rename' : u'rename this monster...',
    'exit' : u'exit the laboratory...',
    'back' : u'back...',
    'backmonster' : u'back...',
    }

class Laboratory(interface.Panel):

    scene = interface.Attribute(None)

    def init_panel(self):

        self.horiz = self.add(interface.Horizontal,
            spacing = 0.04,
            halign = 'left',
            )

        self.info_panel = self.horiz.add(interface.Panel,
            width = 0.3,
            background_color = (.4, .4, .4, 1),
            frame_color = (0, 0, 0, 1),
            frame_width = 0.005,
            halign = 'left',
            )

        self.info_text = self.info_panel.add(interface.Text,
            halign = 'left',
            valign = 'top',
            font_size = 0.02,
            align = 'left',
            padding = 0.02,
            )

        self.monster_view = self.horiz.add(MonsterView,
            width = 0.55,
            background_color = (.4, .4, .4, 1),
            frame_color = (0, 0, 0, 1),
            frame_width = 0.005,
            scissor = True,
            lab = self,
            )

        self.menu_bar = self.horiz.add(interface.Panel,
            width = 0.1,
            halign = 'right',
            valign = 'top',
        )

        self.up_button = self.menu_bar.add(interface.Image,
            image = pyglet.resource.image('icons/uparrow.png'),
            valign = 'top'
            )

        @self.up_button.handler
        def on_mouse_release(x, y, btn, mods):
            self.menu.scroll_up(3)

        self.down_button = self.menu_bar.add(interface.Image,
            image = pyglet.resource.image('icons/downarrow.png'),
            valign = 'bottom',
            )

        @self.down_button.handler
        def on_mouse_release(x, y, btn, mods):
            self.menu.scroll_down(3)

        self.menu = self.menu_bar.add(ScrollMenu,
            halign = "right",
            valign = "center",
            height = 0.8,
            spacing = 0.04,
            padding = 0.02,
            lab = self,
            scissor = True,
            item_options = dict(
                width = 0.75,
                aspect = 1.0,
                halign = 'center',
                focus_alpha = 1.0,
                unfocus_alpha = 1.0,
                focus_scale = 1.3,
                unfocus_scale = 1.0,
                focus_color = (1.0, 1.0, 1.0),
                unfocus_color = (0.5, 0.5, 0.5),
                ),
            )

        self.textedit = self.add(TextEdit,
            font_size = 0.08,
            padding = 0.02,
            background_color = (0, 0, 0, 1),
            )
        self.textedit.visible = False

        self.message_fade = app.interface.add(interface.Color,
                color = (0.0, 0.0, 0.0, 0.0),
                width = 1.0,
                height = 0.0,
                valign = "bottom",
                halign = "left",
        )
        self.message_display = app.interface.add(interface.Text,
                text = u'',
                font_size = 0.06,
                anchor_x = "right",
                halign = "left",
                valign = 0.0,
                width = 1.0,
                color = (1.0, 1.0, 1.0, 1.0),
        )

        self.focus_text = self.add(interface.Text,
            font_size = 0.02,
            background_color = (0, 0, 0, .8),
            italic = True,
            text = u'',
            padding = 0.02,
            halign = 'left',
            valign = 'bottom',
            anchor_x = 'right',
            anchor_y = 'bottom',
            )
        self.focus_text.visible = False

        self.set_main()
        self.selected_anchor = None
        self.selected_part = None
        self.team_idx = 0
        self.messages = []

    def on_mouse_motion(self, x, y, dx, dy):
        self.focus_text.xoffset = x
        self.focus_text.yoffset = y

    ## State Selectors ########################################################

    def set_select_heart(self):
        index = monster.MonsterPartMeta.hearty_index
        self.menu.set_part_list(app.game().invparts(index))
        self.state = 'select_heart'
    def set_select_part(self, size):
        index = monster.MonsterPartMeta.size_index[size]
        self.menu.set_part_list(app.game().invparts(index))
        self.state = 'select_part'
    def set_modify_part(self):
        self.menu.set_part_tool_list()
        self.state = 'modify_part'
    def set_monster(self):
        self.menu.set_monster_tool_list()
        self.state = 'monster'
    def set_main(self):
        self.info_text.text = u''
        self.menu.set_main_tool_list()
        self.state = 'main'

    ## Monster View Interactions ##############################################

    def click_on_part(self, part):
        sound.click()
        if self.selected_part == part:
            self.selected_part = None
            self.set_main()
        else:
            self.selected_part = part
            self.set_modify_part()
        self.selected_anchor = None

    def click_on_background(self):
        self.selected_part = None
        self.selected_anchor = None
        self.set_main()

    def click_on_anchor(self, part, anchor_id):
        sound.click()
        if self.selected_anchor == (part, anchor_id):
            self.selected_anchor = None
            self.set_main()
        else:
            self.selected_anchor = (part, anchor_id)
            size = part.anchors[anchor_id][2]
            self.set_select_part(size)
        self.selected_part = None

    ## Part Menu Interactions #################################################

    def select_piece(self, part):
        if self.textedit.visible: return
        if self.monster_view.subject is None:
            self.monster_view.subject = p = part(None)
            p.name = random.choice(['Chimera', 'Basilisk', 'Hybrid', 'Abomination', 'Monster', 'Creature', 'Hippogriff', 'Questing Beast', 'Wolpertinger'])
            w = p.image.width * (p.force_scale or 1)
            h = p.image.height * (p.force_scale or 1)
            self.monster_view.pan = vector.Vector((-w/2, -h/2))
            app.game().inventory[part] -= 1
        elif self.selected_anchor:
            parent, anchor_id = self.selected_anchor
            for root, (position, rotation, size) in enumerate(part.anchors):
                if size == parent.anchors[anchor_id][2]:
                    parent.add_part(part, anchor_id, root)
                    app.game().inventory[part] -= 1
                    break
        self.monster_view.update_anchors()
        self.save_current_monster()
        self.set_monster()

    ## Part Tool Interactions #################################################

    def rotate_part(self):
        if self.textedit.visible: return
        if self.selected_part.parent is None:
            self.add_message('you cannot rotate the heart...')
            sound.negative()
            return
        if self.selected_part.children:
            self.add_message('you cannot rotate parts with used anchors...')
            sound.negative()
            return
        self.selected_part = self.selected_part.rotate()
        self.monster_view.update_anchors()
        self.save_current_monster()

    def delete_part(self):
        if self.textedit.visible: return
        for part in self.selected_part.all_parts():
            app.game().inventory[type(part)] += 1
        self.selected_part.destroy()
        if self.monster_view.subject == self.selected_part:
            self.monster_view.subject = None
            self.monster_view.mscale = MONSTER_SCALE
            self.monster_view.pan = vector.zero
            self.set_select_heart()
        else:
            self.set_main()
        self.monster_view.update_anchors()
        self.save_current_monster()
        self.selected_part = None

    def flip_part(self):
        if self.textedit.visible: return
        if self.selected_part.parent is None:
            self.add_message('you cannot flip the heart...')
            sound.negative()
            return
        if self.selected_part.children:
            self.add_message('you cannot flip parts with used anchors...')
            sound.negative()
            return
        self.selected_part = self.selected_part.flip()
        self.monster_view.update_anchors()
        self.save_current_monster()

    ## Main Tool Interactions #################################################

    def back(self):
        if self.textedit.visible: return
        if self.state == 'monster':
            self.monster_view.subject = None
            self.set_main()
        else:
            self.selected_part = None
            self.selected_anchor = None
            self.set_monster()

    def _have_heart(self):
        for p, n in app.game().invparts():
            if p.can_be_root:
                return True
        return False

    def load_monster(self, idx):
        if self.textedit.visible: return
        if app.game().team[idx] is None and not self._have_heart():
            self.add_message('you cannot create a new chimera without any hearts...')
            sound.negative()
            return
        self.team_idx = idx
        self.monster_view.subject = app.game().team[idx]
        self.monster_view.update_anchors()

        if self.monster_view.subject is None:
            self.set_select_heart()
        else:
            self.set_monster()
            self.monster_view.subject.refresh()
            self.monster_view.pan = self.monster_view.target_pan
            self.monster_view.mscale = self.monster_view.target_mscale

    def rename_monster(self, text=None):
        if text is None:
            if self.textedit.visible: return
            self.textedit.set_text(self.monster_view.subject.name)
            self.textedit.callback = self.rename_monster
        else:
            self.monster_view.subject.name = text
            self.monster_view.update_anchors()
            self.save_current_monster()

    def exit_lab(self):
        if self.textedit.visible: return
        if len(list(app.game().team)) == 0:
            self.add_message('you cannot leave the laboratory without any chimera...')
            sound.negative()
            return
        from gamelib import world
        app.control.switch(world.WorldScene)

    ## Miscellaneous ##########################################################

    def context_escape(self):
        if self.state == 'main':
            self.exit_lab()
        else:
            self.back()

    def save_current_monster(self):
        app.game().team[self.team_idx] = self.monster_view.subject
        app.game().save()

    def set_focus(self, item, param, key):
        self.focus_text.visible = True
        if isinstance(param, tuple) and \
                isinstance(param[0], monster.MonsterPartMeta):
            param, n = param
            self.focus_text.text = param.fullname + ' (%d)' % n
        elif param in texts:
            self.focus_text.text = texts[param]
        elif param is not None and param.startswith('loadmonster'):
            m = app.game().team[int(param[11:])]
            if m:
                self.focus_text.text = 'edit ' + m.name + '...'
            else:
                self.focus_text.text = 'create new monster...'
        else:
            self.focus_text.text = u''
            self.focus_text.visible = False

    def add_message(self, message):
        if message not in self.messages:
            self.messages.append(message)
    def set_message(self, message):
        self.message_display.text = message
        self.message_ticks = 0
    message_ticks = MESSAGE_TIME + 1
    def tick(self):
        if self.messages and self.message_ticks > MESSAGE_TIME:
            self.set_message(self.messages.pop(0))
        self.message_ticks += 1
    def draw_content(self):
        f = lambda t: max(0, min(1, 1-(32*(t-.5)**5+.5)))
        self.message_display.xoffset = f(float(self.message_ticks) / MESSAGE_TIME) * (app.interface.content_size[0] + self.message_display.content_size[0])
        f = lambda t: max(0, min(1, 1-64*(t-0.5)**6))
        self.message_fade.height = self.message_display.content_size[1] / app.interface.content_size[1]
        self.message_fade.yoffset = self.message_display.content_offset[1]
        self.message_fade.color = [0, 0, 0, .8*f(float(self.message_ticks) / MESSAGE_TIME)]


## Monster View ###############################################################

class MonsterView(interface.Panel):

    subject = interface.Attribute(None)
    pan = interface.Attribute(vector.zero)
    target_mscale = mscale = MONSTER_SCALE
    target_pan = vector.zero
    lab = interface.Attribute(None)

    def init_panel(self):
        super(MonsterView, self).init_panel()
        self.anchors = []
        self.part_anchors = {}
        self.focus_anchor = None
        self.focus_part = None

    def on_mouse_motion(self, x, y, dx, dy):
        if self.lab.textedit.visible:
            return
        cw, ch = self.content_size
        px, py = self.pan
        scale = ch / self.mscale
        x = (x - cw / 2) / scale - px
        y = (y - ch / 2) / scale - py
        self.focus_anchor = None
        self.focus_part = None
        anchor_size = _anchor.width / 2
        for pos, part, ii in self.anchors:
            if (pos - (x, y)).length < anchor_size:
                self.focus_anchor = (part, ii)
                return
        part = self.in_part(x, y)
        if part is not None:
            self.focus_part = part

    def on_mouse_release(self, x, y, button, modifiers):
        if self.lab.textedit.visible:
            return
        cw, ch = self.content_size
        px, py = self.pan
        scale = ch / self.mscale
        x = (x - cw / 2) / scale - px
        y = (y - ch / 2) / scale - py
        anchor_size = _anchor.width / 2
        for pos, part, ii in self.anchors:
            if (pos - (x, y)).length < anchor_size:
                self.parent.parent.click_on_anchor(part, ii)
                return
        part = self.in_part(x, y)
        if part is not None:
            self.lab.click_on_part(part)
        else:
            self.lab.click_on_background()

    def in_part(self, x, y):
        if self.subject is None:
            return
        pos = vector.Vector((x, y))
        for part in reversed(list(self.subject.all_parts_to_draw())):
            scale = part.force_scale or 1.0
            orig = vector.Vector((part.sprite.x, part.sprite.y))
            uxr = vector.unit_x.rotated(part.rotation)
            uyr = vector.unit_y.rotated(part.rotation)
            if part.flipped:
                uyr *= -1
            width = part.sprite.width * scale
            height = part.sprite.height * scale
            xc, yc = uxr.dot(pos - orig), uyr.dot(pos - orig)
            if 0 <= xc < width and 0 <= yc < height:
                xc = float(xc) / scale / part.sprite.scale
                yc = float(yc) / scale / part.sprite.scale
                ix = int(max(0, min(part.image.width, xc)))
                iy = int(max(0, min(part.image.height, yc)))
                if part.test_alpha(ix, iy):
                    return part

    #def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
    #    scale = self.content_size[1] / self.mscale
    #    self.pan += (dx / scale, dy / scale)

    def update_anchors(self):
        if self.subject is None:
            self.lab.info_text.text = u''
            return
        self.subject.create_sprites()
        self.anchors = []
        self.part_anchors = {}
        for part in self.subject.all_parts_to_draw():
            self.part_anchors[part] = []
            for ii in part.unused_anchors():
                p, r, s = part.anchors[ii]
                ax, ay = p.rotated(part.rotation)
                ax += part.sprite.x
                ay += part.sprite.y
                self.anchors.append((vector.Vector((ax, ay)), part, ii))
            for ii in xrange(len(part.anchors)):
                p, r, s = part.anchors[ii]
                ax, ay = p.rotated(part.rotation)
                ax += part.sprite.x
                ay += part.sprite.y
                anchor = (vector.Vector((ax, ay)), part, ii)
                if ii != part.root_idx:
                    if not part.children:
                        self.part_anchors[part].append(anchor)
                    if ii not in part.children:
                        self.anchors.append(anchor)
        bb = self.subject.bounding_box
        cwidth, cheight = self.content_size
        self.target_mscale = max(MONSTER_SCALE, bb.height, bb.width * cheight / cwidth) * 1.1
        self.target_pan = -bb.center
        self.lab.info_text.text = self.subject.description

    def tick(self):
        delta = self.target_mscale - self.mscale
        self.mscale += delta * 0.1
        delta = self.target_pan - self.pan
        self.pan += delta * 0.1

    def draw_content(self):
        if self.subject is not None:
            cw, ch = self.content_size
            px, py = self.pan
            glPushMatrix()
            glTranslatef(cw/2, ch/2, 0.0)
            glScalef(ch/self.mscale, ch/self.mscale, 1.0)
            glTranslatef(px, py, 0.0)
            for part in self.subject.all_parts_to_draw():
                if part.misaligned:
                    part.sprite.color = (192, 64, 64)
                if part in (self.focus_part, self.parent.parent.selected_part):
                    r, g, b = part.sprite.color
                    part.sprite.color = (r//2, g//2, b//2)
                part.sprite.draw()
                part.sprite.color = (255, 255, 255)
                    
            anchors = self.anchors
            for pos, part, ii in anchors:
                glColor4ub(255, 255, 255, 255)
                if (part, ii) == self.focus_anchor:
                    _focusanchor.blit(*pos)
                elif (part, ii) == self.parent.parent.selected_anchor:
                    _selectanchor.blit(*pos)
                else:
                    _anchor.blit(*pos)
            glPopMatrix()


## Game Scene #################################################################

class GameScene(object):

    def __init__(self, newmap=None, newnode=None):

        if newmap is not None:
            app.game().current_map_name = newmap
        if newnode is not None:
            app.game().current_world_node = newnode
        app.game().save()

        self.background = app.interface.add(interface.Color
            )

        self.laboratory = app.interface.add(Laboratory,
            scene = self,
            #background_color = (.2, .2, .2, 1),
            frame_texture = pyglet.resource.texture('misc/labcorner.png'),
            background_texture = pyglet.resource.texture('misc/labtile.png'),
            background_tiles = 8,
            frame_width = 0.1,
            padding = 0.04,
            margin = 0.04,
            scissor = True,
            )

        p = app.interface.add(interface.Panel,
            padding = 0.04,
            margin = 0.04,
            )

        p.on_mouse_motion = self.laboratory.on_mouse_motion

    def on_key_press(self, sym, mods):
        from pyglet.window import key
        if DEBUG and sym == key.S:
            pyglet.image.get_buffer_manager().get_color_buffer().save(
                'screenshot.png')
        elif DEBUG and sym == key.M:
            import re
            m = self.laboratory.monster_view.subject
            name = re.sub(r'\s','', m.name.lower()) or 'UNKNOWN'
            pyglet.resource.file('monsters.py', 'a').write(
                    ('%s = ' % name) +
                    repr(m.serialise()) +
                    '\n\n')
        elif sym == pyglet.window.key.ESCAPE:
            self.laboratory.context_escape()
        else:
            return False
        return True

    def tick(self):
        self.laboratory.monster_view.tick()
        self.laboratory.menu.tick()
        self.laboratory.tick()

    def start(self):
        app.music.play_track(LAB_MUSIC, fadeout=0.5, looping=True)
