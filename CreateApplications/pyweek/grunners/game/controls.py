"""
Controller classes
"""

from pyglet.window import key
from pyglet import input

class Keyboard(object):
    """
    Keyboard controller
    """

    NAME = "Keyboard"

    def __init__(self, window):
        self.keys = None
        self.window = window
        self.keys = key.KeyStateHandler()
        self.window.push_handlers(self.keys)

    def clear(self):
        self.keys.clear()

    def close(self):
        self.window.pop_handlers()

    @property
    def up(self):
        return self.keys[key.UP]

    @property
    def down(self):
        return self.keys[key.DOWN]

    @property
    def left(self):
        return self.keys[key.LEFT]

    @property
    def right(self):
        return self.keys[key.RIGHT]

    @property
    def action(self):
        return self.keys[key.Z] or self.keys[key.ENTER]

    @property
    def escape(self):
        return self.keys[key.ESCAPE]

class Joystick(object):
    """
    Joystick controller
    """

    NAME = "Joystick"

    @staticmethod
    def get_joysticks():
        return input.get_joysticks()

    def __init__(self, window, joystick):
        self.window = window
        self.states = {}
        self.joystick = joystick
        self.joystick.on_joyaxis_motion = self.on_motion
        self.joystick.on_joybutton_press = self.on_press
        self.joystick.on_joybutton_release = self.on_release
        self.joystick.open()

    def clear(self):
        self.states.clear()

    def on_motion(self, joystick, axis, value):
        self.states[axis] = value

    def on_press(self, joystick, button):
        self.states[button] = True

    def on_release(self, joystick, button):
        self.states[button] = False

    def close(self):
        if self.joystick:
            self.joystick.close()

    @property
    def up(self):
        return self.states.get("y", 0) == -1

    @property
    def down(self):
        return self.states.get("y", 0) == 1

    @property
    def left(self):
        return self.states.get("x", 0) == -1

    @property
    def right(self):
        return self.states.get("x", 0) == 1

    @property
    def action(self):
        return self.states.get(0, False)

    @property
    def escape(self):
        return False

