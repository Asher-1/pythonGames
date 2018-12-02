
import os
import logging
from optparse import OptionParser
import ctypes

import pyglet
from pyglet import gl

# resources setup
DATA_PATH = os.path.join(os.path.abspath(pyglet.resource.get_script_home()), 'data')
pyglet.resource.path.append(DATA_PATH)
pyglet.font.add_directory(DATA_PATH)
pyglet.resource.reindex()

from game.const import APP_NAME, PROJECT_DESC, PROJECT_URL, VERSION, WIDTH, HEIGHT, AUDIO_DRIVERS
from game.controls import Keyboard, Joystick
import game.scenes

class Main(pyglet.window.Window):
    def __init__(self):

        # pyglet setup
        pyglet.options['audio'] = AUDIO_DRIVERS
        pyglet.options['debug_gl'] = False

        parser = OptionParser(description="%s - %s" % (APP_NAME, PROJECT_DESC),
                              epilog='Project website: %s' % PROJECT_URL,
                              version='%prog ' + VERSION,
                              )
        parser.add_option("-f", "--fullscreen",
                          dest="fullscreen",
                          default=False,
                          action="store_true",
                          )
        parser.add_option("--scene",
                          dest="scene",
                          default="IntroScene",
                          )
        parser.add_option("-d", "--debug",
                          dest="debug",
                          default=False,
                          action="store_true",
                          )
        self.options, args = parser.parse_args()

        if self.options.debug:
            logging.basicConfig(level=logging.DEBUG)
            logging.debug("Debug enabled")
            logging.debug("Options: %s" % self.options)

        if not hasattr(scenes, self.options.scene):
            parser.error("%s: no such scene" % self.options.scene)

        super(Main, self).__init__(width=WIDTH,
                                   height=HEIGHT,
                                   caption=APP_NAME,
                                   visible=True,
                                   )

        if self.options.fullscreen:
            self.set_fullscreen(True)

        # hide the mouse pointer
        self.set_mouse_visible(False)

        # display FPS on debug
        if self.options.debug:
            self.fps = pyglet.window.FPSDisplay(self)

        # set 60 FPS
        pyglet.clock.schedule_interval(self.update, 1.0/60)
        pyglet.clock.set_fps_limit(60)

        # enable alpha blending (transparent color)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # opengl setup
        gl.glEnable(gl.GL_POLYGON_SMOOTH)
        gl.glHint(gl.GL_POLYGON_SMOOTH_HINT, gl.GL_NICEST)

        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        gl.glEnable(gl.GL_DEPTH_TEST)

        fourfv = ctypes.c_float * 4
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, fourfv(0, -10, 5000, 1))
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, fourfv(0.0, 0.0, 0.0, 1.0))
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, fourfv(1.0, 1.0, 1.0, 1.0))
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, fourfv(1.0, 1.0, 1.0, 1.0))
        gl.glLightf(gl.GL_LIGHT0, gl.GL_CONSTANT_ATTENUATION, 1.0)
        gl.glLightf(gl.GL_LIGHT0, gl.GL_LINEAR_ATTENUATION, 0.0)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glEnable(gl.GL_LIGHTING)

        # set a wrapper for the controls
        self.controls = Keyboard(self)

        # will be set to True if 'p' is pressed
        self.paused = False
        self.paused_label = pyglet.text.Label("PAUSED",
                                              font_name="Russo One",
                                              color=(255, 128, 128, 128),
                                              font_size=30,
                                              anchor_x="center",
                                              anchor_y="center",
                                              )

        self.mode2d = True
        self.scene = None
        self.set_scene(getattr(scenes, self.options.scene))

        self.player = pyglet.media.Player()

    def set_scene(self, scene):
        if self.scene is not None:
            self.scene.delete()

        if scene is None:
            self.dispatch_event('on_close')
        else:
            self.scene = scene(self)
            # FIXME: I'm not sure if this is correct, but avoids
            # problems when starting from a random scene
            self.on_resize(self.width, self.height)

    def set_3d(self):
        if not self.mode2d:
            return
        gl.glViewport(self.viewport_x_offs, self.viewport_y_offs, self.viewport_width, self.viewport_height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluPerspective(35.0, float(self.viewport_width)/self.viewport_height, 0.01, 1000.0)
        # FIXME
        gl.gluLookAt(0, -10, 16, 0, 0, 0, 0, 1, 0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        self.mode2d = False

    def set_2d(self):
        if self.mode2d:
            return
        x = (self.width-WIDTH) / 2
        gl.glViewport(self.viewport_x_offs, self.viewport_y_offs, self.viewport_width, self.viewport_height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, self.viewport_width, 0, self.viewport_height, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        self.mode2d = True

    def update(self, dt):
        """Update game state"""

        if self.paused:
            return

        if self.scene:
            self.scene.update(dt)

    def on_close(self):
        # workaround for windows
        import gc
        gc.collect()
        super(Main, self).on_close()

    def on_resize(self, width, height):
        """Calculate the new viewport preserving aspect ratio"""

        aspect = float(WIDTH)/HEIGHT

        self.viewport_width = int(min(width, height*aspect))
        self.viewport_height = int(min(height, width/aspect))
        self.viewport_x_offs = (width-self.viewport_width) // 2
        self.viewport_y_offs = (height-self.viewport_height) // 2

        x = (width-WIDTH) / 2
        gl.glViewport(self.viewport_x_offs,
                      self.viewport_y_offs,
                      self.viewport_width,
                      self.viewport_height,
                      )
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, self.viewport_width, 0, self.viewport_height, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        logging.debug("Viewport: %s, %s, %s, %s" % (self.viewport_x_offs,
                                                    self.viewport_y_offs,
                                                    self.viewport_width,
                                                    self.viewport_height,
                                                    ))

        self.paused_label.y = self.viewport_height // 2
        self.paused_label.x = self.viewport_width // 2

        if self.scene:
            # scenes live in viewport world
            self.scene.on_resize(self.viewport_width, self.viewport_height)

    def menu(self):
        """Go to the menu"""
        self.set_scene(game.scenes.MenuScene)

    def on_key_press(self, symbol, mods):
        """
        Enhanced default key press handler.

            - Remove the default handler when not debugging, disables escape -> close
            - P set/uset pause flag
            - CRTL + s save a screenshot
            - CTRL + f toggle fullscreen
        """

        if self.options.debug:
            super(Main, self).on_key_press(symbol, mods)

        if symbol == pyglet.window.key.P:
            self.paused = not self.paused
            logging.debug("Paused: %s" % self.paused)
        elif mods == pyglet.window.key.MOD_CTRL and symbol == pyglet.window.key.S:
            filename = os.path.join(os.path.abspath(pyglet.resource.get_script_home()),
                                                    "screenshot%s.png" % pyglet.clock.tick())
            pyglet.image.get_buffer_manager().get_color_buffer().save(filename)
            logging.debug("Screenshot saved: %s" % filename)
        elif mods == pyglet.window.key.MOD_CTRL and symbol == pyglet.window.key.F:
            self.toggle_fullscreen()
            logging.debug("Fullscreen: %s" % self.options.fullscreen)

    def toggle_fullscreen(self):
        self.options.fullscreen = not self.options.fullscreen
        self.set_fullscreen(self.options.fullscreen)

    @property
    def alt_screen_mode(self):
        """The 'alternative' screen mode"""
        return "Fullscreen" if not self.options.fullscreen else "Windowed"

    def on_draw(self):
        """Draw the scene"""

        self.clear()

        if self.scene:
            self.scene.draw()

        if self.paused:
            self.set_2d()
            # tint the screen and draw the pause label
            gl.glPushAttrib(gl.GL_DEPTH_BUFFER_BIT | gl.GL_LIGHTING_BIT)
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_LIGHTING)

            gl.glColor4f(1.0, 0, 0, 0.1)
            w = self.viewport_width
            h = self.viewport_height
            pyglet.graphics.draw(4, gl.GL_QUADS, ('v2f', (0, 0, w, 0, w, h, 0, h,)))

            self.paused_label.draw()

            gl.glPopAttrib()

        if self.options.debug:
            self.set_2d()
            self.fps.draw()

