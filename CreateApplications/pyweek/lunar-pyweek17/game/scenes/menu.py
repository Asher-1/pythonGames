import logging
from .base import State, Scene
from .game import GameScene
from ..controls import Keyboard, Joystick

import pyglet
from pyglet import gl

class Start(State):
    pass

class Exit(State):

    (x, y, w, h) = (0, 0, 0, 0)
    alpha = 1.0

    def __init__(self, scene):
        super(Exit, self).__init__(scene)

        self.w = self.scene.width
        self.h = self.scene.height
        self.alpha = 0.0

    def on_resize(self, width, height):
        self.w = width
        self.h = height

    def update(self, dt):

        self.alpha = min(1.0, self.alpha + dt)
        if self.alpha == 1.0:
            # fade out done, exit the game
            self.scene.parent.set_scene(None)

    def draw(self):
        gl.glPushAttrib(gl.GL_DEPTH_BUFFER_BIT | gl.GL_LIGHTING_BIT)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_LIGHTING)

        gl.glColor4f(0.0, 0, 0, self.alpha)
        pyglet.graphics.draw(4, gl.GL_QUADS, ('v2f', (0, 0, self.w, 0, self.w, self.h, 0, self.h,)))

        gl.glPopAttrib()

class MenuScene(Scene):
    START = Start
    STATES = (Start, Exit)

    SIZE = 26
    DELAY = 0.2

    def __init__(self, parent, **kwargs):
        super(MenuScene, self).__init__(parent, **kwargs)

        # everything is 2d in this scene
        self.parent.set_2d()

        # remember: inverse order!
        self.entries = (("Exit",  self.exit_game),
                        (self.parent.alt_screen_mode, self.fullscreen),
                        ("Controls: %s" % self.parent.controls.NAME,
                            self.controls),
                        ("Start Game", self.start_game),                                             )

        labels = []
        for text, _ in self.entries:
            labels.append(pyglet.text.Label(text,
                                            font_size=self.SIZE,
                                            font_name="Russo One",
                                            anchor_x="center",
                                            anchor_y="center",
                                            ))

        self.labels = labels
        self.selected = len(labels)-1

        self.delay = 0

        self.menu_snd = pyglet.media.StaticSource(pyglet.resource.media("select.wav", streaming=False))

    def update(self, dt):
        super(MenuScene, self).update(dt)

        # we're leaving!
        if self.state == Exit:
            return

        if self.delay < self.DELAY:
            self.delay += dt
            return

        # remember: inverse order!
        if self.parent.controls.down and self.selected > 0:
            self.delay = 0
            self.selected -= 1
            self.menu_snd.play()
        elif self.parent.controls.up and self.selected < len(self.labels)-1:
            self.delay = 0
            self.selected += 1
            self.menu_snd.play()
        elif self.parent.controls.escape:
            self.exit_game()
        elif self.parent.controls.action:
            self.menu_snd.play()
            self.delay = 0
            fn = self.entries[self.selected][-1]
            fn()

    def draw(self):

        gl.glPushAttrib(gl.GL_DEPTH_BUFFER_BIT | gl.GL_LIGHTING_BIT)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_LIGHTING)

        y = self.height // 2 - self.SIZE*len(self.labels) // 2
        for index in range(len(self.labels)):
            label = self.labels[index]
            label.x= self.width // 2
            label.y = y
            if index == self.selected:
                label.color = (255, 230, 65, 255)
            else:
                label.color = (255, 255, 255, 128)
            label.draw()
            y += self.SIZE*2

        gl.glPopAttrib()

        super(MenuScene, self).draw()

    def start_game(self):
        logging.debug("Menu: start_game")
        self.parent.set_scene(GameScene)

    def fullscreen(self):
        logging.debug("Menu: fullscreen")
        self.parent.toggle_fullscreen()
        # workaround the key handler going bananas after loosing the focus
        self.parent.controls.reset()
        # HACK; if we add menu entries this will fail
        self.labels[1].text = self.parent.alt_screen_mode

    def controls(self):
        logging.debug("Menu: controls")
        if self.parent.controls.NAME == Keyboard.NAME:
            joys = Joystick.get_joysticks()
            if joys:
                self.parent.controls = Joystick(joys[0])
        else:
            if isinstance(self.parent.controls, Joystick):
                self.parent.controls.joystick.close()
            self.parent.controls = Keyboard(self.parent)
        # HACK; if we add menu entries this will fail
        self.labels[2].text = "Controls: %s" % self.parent.controls.NAME

    def exit_game(self):
        logging.debug("Menu: exit_game")
        self.set_state(Exit)

