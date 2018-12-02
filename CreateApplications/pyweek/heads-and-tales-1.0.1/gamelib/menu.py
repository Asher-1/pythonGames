import os
import pyglet
import sys

from pyglet.gl import *

from gamelib import app
from gamelib import interface
from gamelib.constants import *


class MenuScene(object):

    def __init__(self):

        self.background = app.interface.add(interface.Panel,
            background_texture = pyglet.resource.texture('maps/credits.png'),
            )

        self.title = app.interface.add(interface.Image,
            width = 1.0,
            height = 0.2,
            valign = "top",
            image = pyglet.resource.image('misc/title.png'),
            )
        from gamelib import world

        self.left = app.interface.add(interface.Image,
                width = 0.5,
                height = 1.0,
                margin = (0.02, 0.0),
                halign = 'left',
                valign = 'bottom',
                image = world.get_left_portrait('Heinrich#point')[0],
                )
        self.right = app.interface.add(interface.Image,
                width = 0.5,
                height = 1.0,
                margin = (0.02, 0.0),
                halign = 'right',
                valign = 'bottom',
                image = world.get_right_portrait('Igor')[0],
                )
        self.ticks = 0

        spacing = 0.02
        if sys.platform == 'win32':
            spacing = -0.01
        self.menu = app.interface.add(interface.TextMenu,
            spacing = spacing,
            valign = 0.7,
            anchor_y = 'top',
            item_options = dict(
                font_size = 0.06,
                ),
            )

        self.set_options()

    def get_save(self, name='save'):
        path = pyglet.resource.get_settings_path(APP_NAME)
        path = os.path.join(path, '%s.sav' % name)
        if os.path.exists(path): return path

    def set_options(self):
        idx = 0
        if self.menu._focused:
            idx = self.menu.children.index(self.menu._focused)
        for c in self.menu.children:
            c.destroy()
        if self.get_save() is not None:
            self.menu.add(interface.TextMenuItem,
                text = u"Continue",
                callback = self.opt_load,
                )
        self.menu.add(interface.TextMenuItem,
            text = u"New Game",
            callback = self.opt_new,
            )
        fs = app.config.get('fullscreen')
        self.menu.add(interface.TextMenuItem,
            text = u'Fullscreen: ' + ['Off', 'On'][fs],
            callback = self.opt_fullscreen,
            )
        ss = app.config.get('sound')
        self.menu.add(interface.TextMenuItem,
            text = u'Sound Effects: ' + ['Off', 'On'][ss],
            callback = self.opt_sound,
            )
        ms = app.config.get('music')
        self.menu.add(interface.TextMenuItem,
            text = u'Music: ' + ['Off', 'On'][ms],
            callback = self.opt_music,
            )
        self.menu.add(interface.TextMenuItem,
            text=u"Exit",
            callback = self.opt_exit,
            )
        self.menu.change_focused(self.menu.children[idx])

    def opt_new(self):
        if self.get_save() is not None:
            os.remove(self.get_save())
        from gamelib import world, gamestate
        gamestate.new_game()
        app.control.switch(world.WorldScene)

    def opt_load(self):
        from gamelib import world, gamestate
        gamestate.new_game()
        app.control.switch(world.WorldScene)

    def opt_fullscreen(self):
        app.window.set_fullscreen(not app.config.get('fullscreen'))
        app.config.save('fullscreen', not app.config.get('fullscreen'))
        self.set_options()
    def opt_music(self):
        app.music.stop()
        app.config.save('music', not app.config.get('music'))
        self.set_options()
    def opt_sound(self):
        app.config.save('sound', not app.config.get('sound'))
        self.set_options()

    def opt_exit(self):
        app.control.exit()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.opt_exit()
            return True
        return False

    def tick(self):
        RATE = 500.0
        self.ticks += 1
        ease = lambda t: max(0, min(1, 1 - (3 * t * t - 2 * t * t * t)))
        t = max(0, min(1, 2 * self.ticks / RATE))
        self.title.yoffset = ease(t) * self.title.content_size[1]
        t = max(0, min(1, self.ticks / RATE))
        self.left.yoffset = -ease(t) * self.left.content_size[1]
        t = max(0, min(1, self.ticks / RATE - 1.0))
        self.right.yoffset = -ease(t) * self.right.content_size[1]

    def start(self):
        app.music.play_track(TITLE_MUSIC, fadeout=0.5, looping=False)
