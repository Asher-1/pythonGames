from __future__ import division, print_function, unicode_literals

import pyglet

# Load our resources here before we import anything else
pyglet.resource.path = ['data', 'data/fonts', 'data/music', 'data/sounds',
                        'data/sprites', 'data/story', 'data/ui']
pyglet.resource.reindex()

from pyglet.window import key, Window

from constants import *
from profile import Profile
from screens import ScreenManager, MainMenuScreen
import sounds

class Game(object):
    FPS = 60.0
    NAME = 'The Last Gardener'

    def __init__(self, vsync=True, show_fps=False):
        self.window = Window(vsync=vsync, width=800, height=600,
                             caption=Game.NAME)

        # Push this handler before adding any screens so that it's on the
        # bottom of the event handler stack
        self.window.push_handlers(self.on_close, self.on_draw,
                                  self.on_key_press)

        self.profile = Profile()

        sounds.music_on = self.profile.get('music', True)
        sounds.sound_on = self.profile.get('sound', True)

        # Loads font
        pyglet.resource.add_font('bagnard_sans.ttf')
        pyglet.font.load(DEFAULT_FONT)

        self.fps_display = None
        if show_fps:
            self.fps_display = pyglet.clock.ClockDisplay()

        # Enable the alpha channel (it's disabled by default)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA,
                              pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        # Load the main menu screen
        self.screens = ScreenManager(self)
        self.screens.add('main', MainMenuScreen(self))
        self.screens.change('main')

        pyglet.clock.schedule_interval(self.update, 1.0 / Game.FPS)

    def update(self, dt):
        # Note: even though we pass in dt to every update function, nothing
        # uses dt. This has the side effect of the gamesim slowing down when
        # the FPS drops, but that's actually okay for bullet hell games
        self.screens.current.update(dt)

    def on_close(self):
        self.profile.save()

    def on_draw(self):
        self.window.clear()

        self.screens.current.draw()

        if self.fps_display is not None:
            self.fps_display.draw()

        sounds.tick()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.HOME:
            pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot.png')

    def start(self):
        pyglet.app.run()
