from .menu import MenuScene
from .base import State, Scene

import pyglet
from pyglet import gl

class Prelude(State):

    # font size, text
    TEXT = ((0, 2, ""),
            (26, 4, "reidrac presents"),
            (0, 2, ""),
            (24, 4, "a PyWeek 17 solo entry"),
            (0, 2, ""),
            )
    DELAY = 10

    def _set_text(self):
        font_size, delay, text = self.TEXT[self.index]
        self.DELAY = delay
        self.label.text = text
        self.label.font_size = font_size
        if text:
            self.scene.engine_snd.play()

    def __init__(self, scene):
        super(Prelude, self).__init__(scene)

        self.label = pyglet.text.Label("",
                                       x=self.scene.width // 2,
                                       y=self.scene.height // 2,
                                       font_name="Russo One",
                                       anchor_x="center",
                                       anchor_y="center",
                                       )

        self.index = 0
        self.delay = 0

        self.skip = False
        self.next_state = Title

        self._set_text()

    def on_resize(self, width, height):
        self.label.x = width // 2
        self.label.y = height // 2

    def update(self, dt):

        if self.delay < self.DELAY:
            self.delay = min(self.DELAY, self.delay+dt)
        else:
            self.delay = 0
            self.index += 1
            if self.index < len(self.TEXT):
                self._set_text()
            else:
                self.scene.set_state(self.next_state)
                self.scene.tune = self.scene.tune.play()
                return

        # allow skipping this part
        if self.scene.parent.controls.escape:
            self.skip = True
        if not self.scene.parent.controls.escape and self.skip:
            self.scene.tune = self.scene.tune.play()
            self.scene.set_state(self.next_state)

    def draw(self):
        gl.glPushAttrib(gl.GL_DEPTH_BUFFER_BIT | gl.GL_LIGHTING_BIT)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_LIGHTING)

        self.label.draw()

        gl.glPopAttrib()

class Title(State):
    def __init__(self, scene):
        super(Title, self).__init__(scene)

        title = pyglet.resource.image("title.png")
        title.anchor_x = title.width // 2
        title.anchor_y = title.height // 2
        self.title = title

        moon_tex = pyglet.resource.image("moon_texture.png")
        moon_tex.anchor_x = moon_tex.width // 2
        moon_tex.anchor_y = moon_tex.height // 2
        self.moon_tex = moon_tex

        self.rot = 0.0
        self.scale = 0.0
        self.alpha = 0.0
        self.alpha_fade = 0.0

        self.skip = False
        self.next_scene = MenuScene
        self.w = self.scene.width
        self.h = self.scene.height

    def on_resize(self, width, height):
        self.w = width
        self.h = height

    def update(self, dt):

        self.rot += 10*dt

        if self.scale < 0.4:
            self.scale += dt/55

        if self.alpha < 0.4:
            self.alpha += dt/50

        if self.alpha > 0.2:
            if self.alpha_fade == 1.0:
                self.scene.engine_snd.play()
            self.alpha_fade -= dt/8
            if self.alpha_fade < 0:
                self.alpha_fade = 0
                self.scene.parent.set_scene(self.next_scene)
                self.scene.noise.pause()
                del self.scene.noise
                return
        else:
            self.alpha_fade = min(1.0, self.alpha_fade + dt/6)

        # allow skipping this part
        if self.scene.parent.controls.escape:
            self.skip = True
        if not self.scene.parent.controls.escape and self.skip:
            self.scene.parent.set_scene(self.next_scene)
            self.scene.noise.pause()
            del self.scene.noise
            self.scene.tune.pause()
            del self.scene.tune

    def draw(self):

        gl.glPushAttrib(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT | gl.GL_LIGHTING_BIT)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_LIGHTING)
        gl.glPushMatrix()

        gl.glColor4f(1.0, 1.0, 1.0, self.alpha_fade)
        gl.glLoadIdentity()
        gl.glTranslatef(self.w // 2, self.h // 2, 0)
        gl.glScalef(0.6+self.scale, 0.6+self.scale, 1.0)
        self.title.blit(0, 0, 0)

        gl.glColor4f(1.0, 1.0, 1.0, self.alpha)
        gl.glLoadIdentity()
        gl.glTranslatef(self.w // 2, self.h // 2, 0)
        gl.glRotatef(self.rot, 0, 0, 1)
        gl.glBlendFunc(gl.GL_DST_COLOR, gl.GL_ZERO)
        self.moon_tex.blit(0, 0, 0)

        gl.glPopMatrix()
        gl.glPopAttrib()


class IntroScene(Scene):
    START = Prelude
    STATES = (Prelude, Title, )

    def __init__(self, parent, **kwargs):
        super(IntroScene, self).__init__(parent, **kwargs)

        self.engine_snd = pyglet.media.StaticSource(pyglet.resource.media("engine.wav", streaming=False))
        self.tune = pyglet.resource.media("tune.ogg")
        self.noise = pyglet.resource.media("noise.ogg").play()

        # everything in this scene is 2d
        self.parent.set_2d()

