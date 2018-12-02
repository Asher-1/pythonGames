import argparse
import os
import pickle

import pyglet
from pyglet.gl import *

pyglet.resource.path = ["@gamelib.data"]
pyglet.resource.reindex()
pyglet.resource.add_font('fonts/KnewaveTTF.ttf')
#pyglet.resource.add_font('fonts/Knewave.otf')

from gamelib import app
from gamelib import battle
from gamelib import game
from gamelib import interface
from gamelib import menu
from gamelib import music
from gamelib import world
from gamelib.constants import *


class Config(object):
    _defaults = {
        'music' : True,
        'sound' : True,
        'fullscreen' : True,
        }
    def __init__(self):
        self.data = dict(self._defaults)
        path = pyglet.resource.get_settings_path(APP_NAME)
        path = os.path.join(path, 'settings')
        if os.path.exists(path):
            self.data = pickle.load(open(path, 'rb'))
        self.saved = dict(self._defaults)
    def get(self, name):
        return self.data[name]
    def set(self, name, value):
        self.data[name] = value
    def save(self, name, value):
        self.data[name] = value
        self.saved[name] = value
        path = pyglet.resource.get_settings_path(APP_NAME)
        path = os.path.join(path, 'settings')
        pickle.dump(self.saved, open(path, 'wb'))


class Control(object):

    def __init__(self, scene):

        config = Config()
        if args.fullscreen:
            config.set('fullscreen', True)
        if args.window:
            config.set('fullscreen', False)
        if args.mute:
            config.set('sound', False)
            config.set('music', False)

        # Create global application objects.
        app.control = self
        app.config = config
        app.keys = pyglet.window.key.KeyStateHandler()
        if config.get('fullscreen'):
            app.window = pyglet.window.Window(caption=CAPTION, fullscreen=True, visible = False)
            app.window._windowed_size = (800, 500)
        else:
            app.window = pyglet.window.Window(800, 500, caption=CAPTION, visible = False)
        idata = pyglet.resource.image('misc/icon.png').get_image_data()
        app.window.set_icon(idata)
        app.music = music.MusicManager()
        app.interface = interface.Root(
                aspect = WINDOW_ASPECT,
                window = app.window,
                scissor = True,)

        # Create the interface event handler.
        self.handler = interface.Handler()

        # Load the window event stack.
        app.window.push_handlers(self)
        app.window.push_handlers(self.handler)
        app.window.push_handlers(app.keys)

        # Clear the window.
        app.window.switch_to()
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        app.window.flip()
        app.window.set_visible(True)

        # Fading.
        self.fade_rate = FADE_RATE
        self.fade_alpha = 1.0
        self.fade_value = 1.0
        self.fade_target = 1.0
        self.fade_callback = None

        # Create the initial scene.
        self.switch(scene)

        # Schedule the update function.
        self.next_tick = 0.0
        pyglet.clock.schedule(self.update)

    def switch(self, scene, *args, **kwds):
        def _switch():
            if hasattr(self, "scene"):
                app.music.remove_handlers(self.scene)
                app.window.remove_handlers(self.scene)
                app.game().remove_handlers(self.scene)
            app.interface = interface.Root(
                    aspect = WINDOW_ASPECT,
                    window = app.window,
                    scissor = True,)
            self.handler.root = app.interface
            self.scene = scene(*args, **kwds)
            app.game().push_handlers(self.scene)
            app.window.push_handlers(self.scene)
            app.music.push_handlers(self.scene)
            if hasattr(self.scene, 'start'):
                self.scene.start()
            self.fade_target = 0.0
        self.fade_target = 1.0
        self.fade_callback = _switch

    def exit(self):
        self.fade_target = 1.0
        self.fade_callback = pyglet.app.exit

    scene = None
    _have_ticked = False
    def update(self, dt):
        self.next_tick -= dt
        while self.next_tick <= 0.0:
            self._have_ticked = True
            self.next_tick += 1.0 / TICK_RATE
            if self.process_fade():
                self.scene.tick()

    def process_fade(self):
        if self.fade_target > self.fade_value:
            v = min(self.fade_target, self.fade_value + self.fade_rate)
        else:
            v = max(self.fade_target, self.fade_value - self.fade_rate)
        self.fade_alpha = max(0.0, min(1.0, 3 * v * v - 2 * v * v * v))
        self.fade_value = v
        if self.fade_value == self.fade_target:
            if self.fade_callback:
                self.fade_callback()
                self.fade_callback = None
            return True
        return False

    def on_draw(self):
        if not self._have_ticked: return
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        app.interface.draw()
        # not needed eventually, I think?
        if hasattr(self.scene, "draw"):
            self.scene.draw()
        # fade
        w, h = app.window.get_size()
        pyglet.graphics.draw(4, GL_QUADS, ('v2f', [0, 0, w, 0, w, h, 0, h]),
                ('c4f', [0, 0, 0, self.fade_alpha] * 4))


parser = argparse.ArgumentParser()

parser.add_argument(
        '-f', '--fullscreen',
        dest = 'fullscreen',
        action = 'store_const',
        const = True,
        default = False,
        help = 'run in fullscreen mode',
        )

parser.add_argument(
        '-w', '--window',
        dest = 'window',
        action = 'store_const',
        const = True,
        default = False,
        help = 'run in windowed mode',
        )

parser.add_argument(
        '-m', '--mute',
        dest = 'mute',
        action = 'store_const',
        const = True,
        default = False,
        help = 'run without sound',
        )

if DEBUG:

    parser.add_argument(
            '-p', '--profile',
            dest = 'profile',
            action = 'store_const',
            const = True,
            default = False,
            help = 'run in the profiler',
            )

    parser.add_argument(
            '-s', '--scene',
            dest = 'scene',
            metavar = 'SCENE',
            default = 'menu.MenuScene',
            help = 'choose the default scene',
            )

args = parser.parse_args()


def main():
    ## create control object
    control = Control(eval(getattr(args, 'scene', 'menu.MenuScene')))
    if getattr(args, 'profile', False):
        ## run with profiling
        import cProfile, datetime
        cProfile.runctx('pyglet.app.run()', globals(), None, 'profile-%s.log' %
                datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S'))
    else:
        ## run without profiling
        pyglet.app.run()

if __name__ == "__main__":
    main()
