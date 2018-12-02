"""gamelib.control -- game control and event management

"""

import importlib

import pyglet
from pyglet.gl import *

from gamelib import app
from gamelib import gamestate
from gamelib import interface
from gamelib import music
from gamelib.constants import *

__all__ = ['Control']


## Control ####################################################################

class Control(object):
    """Global game control and event stack management object.

    The Control instance creates the window and then manages different scenes
    of the game.

    ::Methods::

        `Control.switch(scene, *, **)`
            Instantiate the given scene class with the given arguments and
            rebuild the event stack.

        `Control.set_cursor(image_name)`
            Create a new mouse cursor from the named image file and set it on
            the window.

    """

    scene = None

    def __init__(self):

        # Create global application objects.
        app.control = self
        app.keys = pyglet.window.key.KeyStateHandler()
        app.window = self._create_window()
        app.state = gamestate.GameState(app.config.state)
        app.music = music.MusicMan()

        # Create the interface event handler.
        self.handler = interface.Handler()

        # Load the window event stack.
        app.window.push_handlers(self)
        app.window.push_handlers(self.handler)
        app.window.push_handlers(app.keys)

        # Create the initial scene.
        self.switch(app.config.start_scene)

        # Schedule the update function.
        self.next_tick = 0.0
        pyglet.clock.schedule(self.update)

    def _create_window(self):

        # Create the window object.
        app.window = pyglet.window.Window(800, 480, caption=CAPTION,
                visible=False)

        # Enable fullscreen if necessary.
        if app.config.fullscreen:
            app.window.set_fullscreen(True)

        # Clear the window's color and depth buffers.
        app.window.switch_to()
        glClearColor(0.0, 0.0, 0.0, 1.0); glClearDepth(0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_BLEND)
        app.window.flip()

        # Show and return the window.
        app.window.set_visible(True)
        return app.window

    def switch(self, scene, *args, **kwds):
        if isinstance(scene, str):
            scene_module_name, scene_class_name = scene.rsplit('.', 1)
            scene_module = importlib.import_module(scene_module_name)
            scene = getattr(scene_module, scene_class_name)
        app.window.remove_handlers(app.keys)
        app.window.remove_handlers(self.handler)
        app.window.remove_handlers(self.scene)
        app.interface = interface.Root(
                aspect = WINDOW_ASPECT,
                window = app.window,
                scissor = True,
                )
        self.handler.root = app.interface
        self.scene = scene(*args, **kwds)
        app.window.push_handlers(self.scene)
        app.window.push_handlers(self.handler)
        app.window.push_handlers(app.keys)

    def set_cursor(self, image_name=None):
        if image_name is None:
            app.window.set_mouse_cursor(None)
        else:
            image = pyglet.resource.texture(image_name)
            app.window.set_mouse_cursor(pyglet.window.ImageMouseCursor(
                image, image.width // 2, image.height // 2))

    def update(self, dt):
        remaining_ticks = int(TICK_RATE // MIN_FPS)
        self.next_tick -= dt
        while self.next_tick <= 0.0:
            remaining_ticks -= 1
            if hasattr(self.scene, 'tick'):
                self.scene.tick()
            if remaining_ticks == 0:
                self.next_tick = 0.0
            self.next_tick += 1.0 / TICK_RATE
