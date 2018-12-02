import os
import logging
from argparse import ArgumentParser
from hashlib import md5
import json

import pyglet
from pyglet import gl

# resources setup
DATA_PATH = os.path.join(os.path.abspath(pyglet.resource.get_script_home()), 'data')
pyglet.resource.path.append(DATA_PATH)
pyglet.font.add_directory(DATA_PATH)
pyglet.resource.reindex()

from .const import APP_NAME, PROJECT_DESC, PROJECT_URL, VERSION, \
                   WIDTH, HEIGHT, SCALE, AUDIO_DRIVERS, \
                   FPS, UFPS
from .controls import Keyboard
from . import scenes
from .pixfont import register_font, get_font

class Main(pyglet.window.Window):
    def __init__(self):

        # pyglet setup
        pyglet.options['audio'] = AUDIO_DRIVERS
        #pyglet.options['xlib_fullscreen_override_redirect'] = True
        #pyglet.options['debug_gl'] = False

        parser = ArgumentParser(description="%s - %s" % (APP_NAME, PROJECT_DESC),
                                epilog='Project website: %s' % PROJECT_URL,
                                )
        parser.add_argument("--version", action="version", version="%(prog)s "+VERSION)
        parser.add_argument("-f", "--fullscreen",
                            dest="fullscreen",
                            action="store_true",
                            help="run the game in full screen mode",
                            )
        parser.add_argument("--scene",
                            dest="scene",
                            default="MenuScene",
                            )
        parser.add_argument("-d", "--debug",
                            dest="debug",
                            action="store_true",
                            )
        self.options = parser.parse_args()

        if self.options.debug:
            logging.basicConfig(level=logging.DEBUG)
            logging.debug("Debug enabled")
            logging.debug("Options: %s" % self.options)

        if not hasattr(scenes, self.options.scene):
            parser.error("%s: no such scene" % self.options.scene)

        super(Main, self).__init__(width=WIDTH*SCALE,
                                   height=HEIGHT*SCALE,
                                   caption=APP_NAME,
                                   visible=True,
                                   )

        if self.options.fullscreen:
            self.set_fullscreen(True)

        # display FPS on debug
        if self.options.debug:
            self.fps = pyglet.window.FPSDisplay(self)

        # hide the mouse pointer
        self.set_mouse_visible(False)

        # set 60 FPS
        pyglet.clock.schedule_interval(self.update, FPS)
        pyglet.clock.set_fps_limit(FPS)

        # enable alpha blending (transparent color)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # register fonts
        my_map = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?()@:/'.,- <>"
        register_font("default", "default_font.png", 7, 11, my_map)
        register_font("numbers", "numbers.png", 13, 16, "0123456789")

        # will be set to True if 'p' is pressed
        self.paused = False
        font = get_font("default")
        self.paused_sprite = font.render(None, WIDTH//2, HEIGHT//2, "THE GRID IS PAUSED", align="center")

        self.scene = None
        # delay a little bit so the window is ready
        pyglet.clock.schedule_once(lambda x: self.set_scene(getattr(scenes, self.options.scene)), 1.0)

        self.dt = 0.0

        # config options and state
        self.load_config()
        self.controls = Keyboard(self)

        # in case we skip to the play scene
        self.current_stage = "Tokyo"
        self.current_stage_index = 0

    def load_config(self):
        self.state = dict(music=True, done=[])

        logging.debug("loading state...")
        try:
            with open(pyglet.resource.get_settings_path("gr-savegame.dat"), "r") as fd:
                state = json.load(fd)
                # test the data!
                state["music"] = state.get("music", "on") == "on"
                state["done"] = state.get("done", [])
                if not isinstance(state["done"], list):
                    state["done"] = []
        except BaseException:
            logging.debug("failed!")
        else:
            self.state = state
            logging.debug("new state: %r" % self.state)

    def save_config(self):
        logging.debug("saving state...")
        state = self.state.copy()
        state["music"] = "on" if state["music"] else "off"
        try:
            with open(pyglet.resource.get_settings_path("gr-savegame.dat"), "w") as fd:
                json.dump(state, fd)
        except BaseException:
            logging.debug("failed!")

    def set_scene(self, scene):
        if self.scene is not None:
            self.scene.delete()

        if scene is None:
            self.dispatch_event('on_close')
        else:
            self.scene = scene(self)

    def to_stage_select(self):
        # HACKY!
        self.set_scene(scenes.MenuScene)
        scenes.StageSelect.selected = self.current_stage_index
        self.scene.set_state(scenes.StageSelect)
        # jump to the music loop
        self.scene.to_the_loop()

    def update(self, dt):
        if self.paused:
            return

        if self.scene:
            self.dt += dt
            while self.dt >= UFPS:
                self.scene.update(UFPS)
                self.dt -= UFPS

    def on_close(self):
        # workaround for audio players not being gc on windows
        import gc
        logging.debug("Garbage: %r" % gc.garbage)
        gc.collect()
        self.save_config()
        super(Main, self).on_close()

    def on_resize(self, width, height):
        """Calculate the new viewport preserving aspect ratio"""
        super(Main, self).on_resize(width, height)

        logging.debug("on_resize: %s, %s" % (width, height))

        aspect = float(WIDTH)/HEIGHT

        # this will avoid artifacts after scaling fullscreen
        if self.fullscreen:
            width = (width // 32)*32
            height = (height // 32)*32

        vw = width
        vh = int(width/aspect)

        if vh > height:
            vh = height
            vw = int(height*aspect)

        vx = (width-vw) // 2
        vy = (height-vh) // 2

        gl.glViewport(vx, vy, vw, vh)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, WIDTH, 0, HEIGHT, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        logging.debug("Viewport: %s, %s, %s, %s" % (vx, vy, vw, vh))

    def on_key_press(self, symbol, mods):
        """
        Enhanced default key press handler.

            - Remove the default handler when not debugging, disables escape -> close
            - P set/uset pause flag
            - CRTL + s save a screenshot
        """

        if self.options.debug:
            super(Main, self).on_key_press(symbol, mods)

        if symbol == pyglet.window.key.P:
            self.paused = not self.paused
            if self.scene:
                if self.scene.player.playing:
                    self.scene.player.pause()
                else:
                    self.scene.player.play()
            logging.debug("Paused: %s" % self.paused)
        elif mods == pyglet.window.key.MOD_CTRL and symbol == pyglet.window.key.S:
            filename = os.path.join(os.path.abspath(pyglet.resource.get_script_home()),
                                                    "screenshot%s.png" % pyglet.clock.tick())
            pyglet.image.get_buffer_manager().get_color_buffer().save(filename)
            logging.debug("Screenshot saved: %s" % filename)

    def on_draw(self):
        """Draw the scene"""

        gl.glColor4f(1, 1, 1, 1)
        self.clear()

        if self.scene:
            self.scene.draw()

        if self.paused:
            gl.glPushAttrib(gl.GL_CURRENT_BIT)
            gl.glColor4f(0, 0.4, 0, 0.8)
            pyglet.graphics.draw(4, gl.GL_QUADS, ('v2f', (0, 0, WIDTH, 0, WIDTH, HEIGHT, 0, HEIGHT,)))
            gl.glPopAttrib()

            self.paused_sprite.draw()

        if self.options.debug:
            self.fps.draw()

