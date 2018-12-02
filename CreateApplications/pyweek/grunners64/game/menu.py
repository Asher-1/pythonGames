import logging

import pyglet
from pyglet import gl
from pyglet.graphics import Batch, OrderedGroup
from pyglet.sprite import Sprite
from pyglet.image import Animation, AnimationFrame

from .base import State, Scene
from .const import WIDTH, HEIGHT
from .pixfont import get_font
from .utils import get_texture, texture_parameters, get_texture_sequence
from .controls import Keyboard, Joystick
import shader

from .play import PlayScene

class ProgramScrollTex(shader.ShaderProgram):

    vs = """
void main()
{
    gl_FrontColor = gl_Color;
    gl_TexCoord[0] = gl_MultiTexCoord0;
    gl_Position = ftransform();
}
    """

    fs = """
uniform sampler2D source;
uniform float t;

void main() {
  vec2 texCoord = vec2(gl_TexCoord[0]);
  vec4 texel = texture2D(source, vec2(texCoord.x+t, texCoord.y+t));
  gl_FragColor = texel;
}
    """
    @classmethod
    def create(cls):
        return cls.simple_program('tex_scroller', cls.vs, cls.fs)

    def set_state(self, provider):
        self.install()
        self.usetTex('source', 0, provider.target, provider.id)
        self.uset1F("t", provider.scroll)

    def unset_state(self):
        self.uninstall()

class Tutorial(State):

    stages = ("Tokyo", "Madrid",)

    text = dict(Tokyo="""\
To clear a Grid you have to crack all
the terminals.

Remember that your time is limited as
a Grid Scan is in progress.

Choose your targets wisely as only the
nearby items will be affected!

If you get stuck, press ESC to
disconnect and try again.
""",
Madrid="""\
Lasers will give your location away,
increasing the effectiveness of the
Grid Scan.

Did I mention enemies?

You can zap them and they will dis-
connect, although they will try to do
the same to you!

Good luck.
""")

    def __init__(self, scene, prev_state=None):
        super(Tutorial, self).__init__(scene, prev_state)

        self.batch = Batch()

        stage = self.window.current_stage
        font = self.scene.font
        self.sprites =  []
        y = HEIGHT-25
        x = 10

        self.sprites.append(font.render(self.batch, WIDTH//2, y, "Tutorial: %s" % stage, align="center"))
        y -= 16

        for text in self.text[stage].split("\n"):
            y -= 14
            if not text:
                continue
            self.sprites.append(font.render(self.batch, x, y, text))

    @property
    def window(self):
        return self.scene.window

    def update(self, dt):
        if self.window.controls.action or self.window.controls.escape:
            self.window.controls.clear()
            self.window.set_scene(PlayScene)

    def draw(self):

        self.batch.draw()

class StageSelect(State):

    stages = (
              ("Tokyo", 236, 71, 0),

              ("Madrid", 119, 70, 1),

              ("Johannesburg", 144, 130, 2),
              ("Buenos Aires", 77, 136, 2),

              ("Berlin", 131, 58, 4),
              ("Canberra", 243, 140, 4),

              ("Tel Aviv", 152, 78, 6),
              ("London", 122, 58, 6),

              ("Moscow", 151, 55, 8),
              ("Washington DC", 60, 68, 9),
              )

    levels = ((0, "Apprentice"),
              (2, "Junior"),
              (6, "Senior"),
              (8, "Architect"),
              (10, "Grid Master"),
              )

    selected = 0

    def __init__(self, scene, prev_state=None):
        super(StageSelect, self).__init__(scene, prev_state)

        self.batch = Batch()

        img = get_texture("world.png")
        self.world = Sprite(img, x=WIDTH//2-img.width//2, y=20, batch=self.batch, group=OrderedGroup(0))

        font = self.scene.font
        self.select_stage = font.render(self.batch, WIDTH//2, HEIGHT-26, "< Select Grid >", align="center")

        stage, loc_x, loc_y, lock = self.stages[self.selected]
        self.stage = font.render(self.batch, WIDTH//2, HEIGHT-26-16, stage, align="center")

        img = get_texture_sequence("map_loc.png", 6, 6, 0, 0)
        frames = [AnimationFrame(f, 0.2) for f in img]
        self.loc = Sprite(Animation(frames),
                          x=loc_x-3+self.world.x,
                          y=self.world.y+self.world.height-loc_y-3,
                          batch=self.batch, group=OrderedGroup(1))

        img = get_texture("done.png")
        self.done = Sprite(img, x=self.stage.x-14, y=self.stage.y+2, batch=self.batch)
        self.done.visible = stage in self.window.state["done"]

        level = ""
        for r, l in self.levels:
            if len(self.window.state["done"]) >= r:
                level = l
        self.level = font.render(self.batch, WIDTH//2, 8, "Level: %s" % level, align="center")

        img = get_texture("lock.png")
        self.lock = Sprite(img, x=self.stage.x-14, y=self.stage.y+2, batch=self.batch)
        self.lock.visible = lock>len(self.window.state["done"])
        self.locked = 0

    @property
    def window(self):
        return self.scene.window

    def update(self, dt):
        if self.window.controls.action:
            if self.stages[self.selected][3] > len(self.window.state["done"]):
                self.window.controls.clear()
                self.scene.locked.play()
                self.locked = 0.4
                self.lock.color = (224, 60, 40)
            else:
                self.window.controls.clear()
                self.window.current_stage = self.stages[self.selected][0]
                self.window.current_stage_index = self.selected

                if self.window.current_stage in Tutorial.stages:
                    self.scene.set_state(Tutorial)
                else:
                    self.window.set_scene(PlayScene)
                return

        if self.locked > 0:
            self.locked -= dt;
            if self.locked <= 0:
                self.lock.color = (255, 255, 255)

        if self.window.controls.escape:
            self.scene.keystroke.play()
            self.window.controls.clear()
            self.scene.set_prev_state()

        dirty = False
        if self.window.controls.left and self.selected>0:
            self.scene.keystroke.play()
            self.window.controls.clear()
            self.selected -= 1
            dirty = True
        if self.window.controls.right and self.selected<len(self.stages)-1:
            self.scene.keystroke.play()
            self.window.controls.clear()
            self.selected += 1
            dirty = True

        if dirty:
            stage, loc_x, loc_y, lock = self.stages[self.selected]
            self.loc.x = loc_x-3+self.world.x
            self.loc.y = self.world.y+self.world.height-loc_y-3
            self.stage.delete()
            self.stage = self.scene.font.render(self.batch, WIDTH//2, HEIGHT-26-16, stage, align="center")
            self.lock.x = self.stage.x-14
            self.lock.visible = lock>len(self.window.state["done"])
            self.done.x = self.stage.x-14
            self.done.visible = stage in self.window.state["done"]

    def draw(self):
        self.batch.draw()

class ViewCredits(State):

    def __init__(self, scene, prev_state=None):
        super(ViewCredits, self).__init__(scene, prev_state)

        self.batch = Batch()

        self.title = Sprite(self.scene.title_texture, x=WIDTH//2-self.scene.title_texture.width//2, y=140, batch=self.batch)

        font = self.scene.font
        y = 120
        self.text = []
        for text in ("A game by @reidrac for PyWeek 18", None,
                     "Programming / Graphics / Sound", "Juan J. Martinez", None,
                     "usebox.net",
                     ):
            if text is not None:
                self.text.append(font.render(self.batch, WIDTH//2, y, text, align="center"))
            y -= 14

    @property
    def window(self):
        return self.scene.window

    def update(self, dt):
        if self.window.controls.action or self.window.controls.escape:
            self.scene.keystroke.play()
            self.window.controls.clear()
            self.scene.set_prev_state()

    def draw(self):
        self.batch.draw()

class MainMenu(State):

    def __init__(self, scene, prev_state=None):
        super(MainMenu, self).__init__(scene, prev_state)

        self.batch = Batch()

        self.title = Sprite(self.scene.title_texture, x=WIDTH//2-self.scene.title_texture.width//2, y=140, batch=self.batch)

        music = "On" if self.window.state["music"] else "Off"
        font = self.scene.font
        self.menu = [[font.render(self.batch, WIDTH//2, 120, "Start Game", align="center"), self.start_game],
                     [font.render(self.batch, WIDTH//2, 120-14*1, "Controls: %s" % self.window.controls.NAME, align="center"), self.toggle_controls],
                     [font.render(self.batch, WIDTH//2, 120-14*2, "Music: %s" % music, align="center"), self.toggle_music],
                     [font.render(self.batch, WIDTH//2, 120-14*3, self.current_mode, align="center"), self.toggle_fullscreen],
                     [font.render(self.batch, WIDTH//2, 120-14*4, "View Credits", align="center"), self.view_credits],
                     [font.render(self.batch, WIDTH//2, 120-14*5, "Exit", align="center"), self.exit_game],
                     ]
        self.sel_w = max(self.menu, key=lambda x: x[0].width)[0].width+16
        self.sel = 0

    @property
    def window(self):
        return self.scene.window

    @property
    def current_mode(self):
        return "Windowed Mode" if self.window.fullscreen else "Fullscreen"

    def start_game(self):
        logging.debug("start_game -> select stage")
        StageSelect.selected = 0
        self.scene.set_state(StageSelect)

    def toggle_controls(self):
        if isinstance(self.window.controls, Keyboard):
            joys = Joystick.get_joysticks()
            if joys:
                self.window.controls = Joystick(self.window, joys[0])
        else:
            self.window.controls.close()
            self.window.controls = Keyboard(self.window)
        self.menu[self.sel][0].delete()
        self.menu[self.sel][0] = self.scene.font.render(self.batch, WIDTH//2, 120-14*1, "Controls: %s" % self.window.controls.NAME, align="center")

    def toggle_music(self):
        logging.debug("toggle_music")
        if self.scene.player.playing:
            self.scene.player.pause()
        else:
            self.scene.player.play()
        music = "On" if self.scene.player.playing else "Off"
        self.window.state["music"] = self.scene.player.playing
        self.menu[self.sel][0].delete()
        self.menu[self.sel][0] = self.scene.font.render(self.batch, WIDTH//2, 120-14*2, "Music: %s" % music, align="center")

    def view_credits(self):
        logging.debug("view_credits")
        self.scene.set_state(ViewCredits)

    def toggle_fullscreen(self):
        logging.debug("toggle_fullscreen")
        self.window.set_fullscreen(not self.window.fullscreen)
        self.menu[self.sel][0].delete()
        self.menu[self.sel][0] = self.scene.font.render(self.batch, WIDTH//2, 120-14*3, self.current_mode, align="center")

    def exit_game(self):
        logging.debug("exit_game")
        self.window.set_scene(None)

    def update(self, dt):
        if self.window.controls.up and self.sel>0:
            self.scene.keystroke.play()
            self.window.controls.clear()
            self.sel -= 1
        if self.window.controls.down and self.sel<len(self.menu)-1:
            self.scene.keystroke.play()
            self.window.controls.clear()
            self.sel += 1

        if self.window.controls.action:
            self.scene.keystroke.play()
            self.window.controls.clear()
            self.menu[self.sel][1]()

    def draw(self):
        x = WIDTH//2-self.sel_w//2
        y = 120-self.sel*14-6
        w = self.sel_w
        h = 14
        gl.glPushAttrib(gl.GL_CURRENT_BIT)
        gl.glColor4f(0.20, 0.20, 0.20, 0.8)
        pyglet.graphics.draw(4, gl.GL_QUADS, ('v2f', (x, y, x+w, y, x+w, y+h, x, y+h,)))
        gl.glColor4f(1.00, 1.00, 1.00, 0.8)
        pyglet.graphics.draw(4, gl.GL_LINE_LOOP, ('v2f', (x, y, x+w, y, x+w, y+h, x, y+h,)))
        gl.glPopAttrib()

        self.batch.draw()

class MenuScene(Scene):

    START = MainMenu

    player = pyglet.media.Player()

    def __init__(self, window, **kwargs):
        # these are used by the states
        self.title_texture = get_texture("title.png")
        self.font = get_font("default")

        super(MenuScene, self).__init__(window, **kwargs)

        self.bg = pyglet.resource.texture("menu_bg.png")
        texture_parameters(self.bg, clamp=False)
        self.bg.scroll = 0
        self.bg_shader = ProgramScrollTex.create()

        source = pyglet.resource.media("grid-intro.ogg")
        sc_group = pyglet.media.SourceGroup(source.audio_format, None)
        sc_group.queue(source)
        sc_group.next_source(immediate=False)
        sc_group.queue(pyglet.resource.media("grid-loop.ogg"))
        sc_group.loop = True
        self.player.queue(sc_group)
        if self.window.state["music"]:
            self.player.play()

        self.keystroke = pyglet.resource.media("keystroke.wav", streaming=False)
        self.locked = pyglet.resource.media("locked.wav", streaming=False)

    def to_the_loop(self):
        if not self.window.state["music"]:
            return

        self.player.pause()
        MenuScene.player = pyglet.media.Player()
        source = pyglet.resource.media("grid-loop.ogg")
        sc_group = pyglet.media.SourceGroup(source.audio_format, None)
        sc_group.queue(source)
        sc_group.loop = True
        self.player.queue(sc_group)
        self.player.play()

    def update(self, dt):
        super(MenuScene, self).update(dt)

        self.bg.scroll += dt/6
        if self.bg.scroll > 0.50:
            self.bg.scroll -= 0.50

    def draw(self):
        tex_coords = (0., 0., 0., 2., 0., 0., 2., 2., 0., 0., 2., 0.)
        gl.glEnable(self.bg.target)
        gl.glBindTexture(self.bg.target, self.bg.id)
        self.bg_shader.set_state(self.bg)
        pyglet.graphics.draw(4, gl.GL_QUADS, ('v2f', (0, 0, WIDTH, 0, WIDTH, HEIGHT, 0, HEIGHT,)),
                                             ('t3f', tex_coords),
                                             )
        self.bg_shader.unset_state()
        gl.glDisable(self.bg.target)

        super(MenuScene, self).draw()

    def delete(self):
        if self.player.playing:
            self.player.pause()
            self.player = None

