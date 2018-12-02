import logging
import json
from time import time

import pyglet
from pyglet import gl
from ext.obj import OBJ

from .base import State, Scene
from ..json_tmx import Map

class Intro(State):

    TEXT = """
Year 2040.

Two decades have passed since the first corporation established a permanent lunar base under the surface of the Moon.

Today the Lunar Commerce Commission maintains a frail balance between the different corporations competing for mineral resources.

Accidents are frequent, although officials refuse to admit that they're due to sabotage or an undercover war for the rich lunar underground.
"""

    DELAY = 16

    def __init__(self, scene):
        super(Intro, self).__init__(scene)

        self.label = pyglet.text.Label(text=self.TEXT,
                                       color=(255, 255, 255, 255),
                                       multiline=True,
                                       x=self.scene.width // 2,
                                       y=self.scene.height // 2,
                                       width=480,
                                       font_name="Russo One",
                                       anchor_x="center",
                                       anchor_y="center",
                                       )

        self.delay = 0

        self.skip = False
        self.next_state = CutScene

        self.scene.fade_in()

    def update(self, dt):

        self.delay += dt
        if self.delay > self.DELAY:
            self.scene.set_state(self.next_state)
            self.scene.noise = self.scene.noise.play()
            return

        # allow skipping this part
        if self.scene.parent.controls.action:
            self.skip = True
        if not self.scene.parent.controls.action and self.skip:
            self.scene.set_state(self.next_state)
            self.scene.noise = self.scene.noise.play()
            self.scene.abort_fade()

    def on_resize(self, width, height):
        self.label.x = width // 2
        self.label.y = height // 2

    def draw(self):
        gl.glPushAttrib(gl.GL_DEPTH_BUFFER_BIT | gl.GL_LIGHTING_BIT)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_LIGHTING)

        self.label.draw()

        gl.glPopAttrib()

class CutScene(State):

    # font size, text
    TEXT = ((2, "", None),
            (6, "*buzzz* This is Orbital Eco-Bravo-6-4-7 reporting *buzzz*", "cut1.ogg"),
            (2, "", None),
            (6, "*buzzz* No response from Daedalus; repeat: no response *buzzz*", "cut2.ogg"),
            (4, "", None),
            (6, "*buzzz* Roger that, connecting with one of the droids. OUT *buzzz*", "cut3.ogg"),
            (4, "", None),
            )
    DELAY = 10

    def _set_text(self):
        delay, text, cut = self.TEXT[self.index]
        self.DELAY = delay
        self.label.text = text
        if cut:
            self.playing = pyglet.resource.media(cut).play()

    def __init__(self, scene):
        super(CutScene, self).__init__(scene)

        self.label = pyglet.text.Label("",
                                       x=self.scene.width // 2,
                                       y=40,
                                       font_name="Russo One",
                                       font_size=14,
                                       anchor_x="center",
                                       anchor_y="center",
                                       )

        self.index = 0
        self.delay = 0

        self.skip = False
        self.next_state = Play

        self._set_text()

        self.msg = """Connection succeeded!

    Use the %s to move around and investigate.
    Press *action* to dismiss messages like this one.""" % self.scene.parent.controls.NAME

    def on_resize(self, width, height):
        self.label.x = width // 2

    def update(self, dt):

        if self.delay < self.DELAY:
            self.delay = min(self.DELAY, self.delay+dt)
        else:
            self.delay = 0
            self.index += 1
            if self.index < len(self.TEXT):
                self._set_text()
            else:
                self.scene.fade_in()
                self.scene.set_state(self.next_state)
                self.scene.noise.pause()
                del self.scene.noise
                self.scene.show_message(self.msg)
                self.scene.started = time()
                self.scene.bg_snd.play()
                return

        # allow skipping this part
        if self.scene.parent.controls.action:
            self.skip = True
        if not self.scene.parent.controls.action and self.skip:
            self.scene.fade_in()
            self.scene.set_state(self.next_state)
            self.scene.noise.pause()
            del self.scene.noise
            if hasattr(self, "playing") and self.playing.playing:
                self.playing.pause()
                del self.playing
            self.scene.show_message(self.msg)
            self.scene.started = time()
            self.scene.bg_snd.play()

    def draw(self):
        gl.glPushAttrib(gl.GL_DEPTH_BUFFER_BIT | gl.GL_LIGHTING_BIT)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_LIGHTING)

        self.label.draw()

        gl.glPopAttrib()

class Play(State):

    R_DOWN = 0
    R_LEFT = -90
    R_RIGHT = 90
    R_UP = 180

    MAPS = ("droids.json", "dock_door.json", "infirmary.json",
            "lab.json", "control.json", "quarters.json", "quarters2.json",
            "biometry.json", "reactor.json", )

    def __init__(self, scene):
        super(Play, self).__init__(scene)

        self.top_score = 0
        self.maps = {}
        for filename in self.MAPS:
            self.maps[filename] = Map.load_json(filename)
            for events in self.maps[filename].extra.values():
                for event in events.values():
                    if "score" in event:
                        self.top_score += 1
                        event["score"] = self.top_score
        logging.debug("top score is %s" % self.top_score)

        self.flags = {}
        self.actions = {}
        self.location = None
        self.map = None
        self.set_map(self.MAPS[0])

        self._score = set()
        self.score_label = pyglet.text.Label("Score %02d%% " % (len(self._score)*100//self.top_score),
                                             x=0, y=0,
                                             font_name="Russo One",
                                             color=(255, 255, 255, 128),
                                             font_size=20,
                                             anchor_x="right",
                                             )
        self.inv_label = pyglet.text.Label("",
                                           x=0, y=4,
                                           font_name="Russo One",
                                           color=(255, 255, 255, 128),
                                           font_size=12,
                                           anchor_x="right",
                                           anchor_y="bottom",
                                           )
        image = pyglet.resource.image("attention.png")
        self.attention = image.get_region(1, 1, image.width-2, image.height-2)

        self.player = OBJ.from_resource("droid.obj")
        self.px, self.py = self.map.to_screen(*json.loads(self.map.properties["start"]))
        self.rot = self.R_UP
        self.speed = 1.4

        self.event = None
        self.event_type = None

        self.wheels_snd = pyglet.resource.media("wheels.wav", streaming=False)
        self.wheels_snd = self.wheels_snd.play()
        self.wheels_snd.eos_action = "loop"
        self.wheels_snd.pause()
        self.door_snd = pyglet.media.StaticSource(pyglet.resource.media("door_down.wav", streaming=False))
        self.error_snd = pyglet.media.StaticSource(pyglet.resource.media("error.wav", streaming=False))
        self.denied_snd = pyglet.media.StaticSource(pyglet.resource.media("denied.wav", streaming=False))

    @property
    def top(self):
        return self.py

    @property
    def bottom(self):
        return self.py-0.9

    @property
    def center_y(self):
        return self.py-(0.9/2)

    @property
    def left(self):
        return self.px

    @property
    def right(self):
        return self.px+0.8

    @property
    def center_x(self):
        return self.px+(0.8/2)

    @property
    def controls(self):
        return self.scene.parent.controls

    def facing(self, incx, incy):

        rot = None
        # face direction
        if incy != 0:
            if incy > 0:
                rot = self.R_UP
                if incx < 0:
                    rot += 45
                elif incx > 0:
                    rot -= 45
            else:
                rot = self.R_DOWN
                if incx < 0:
                    rot -= 45
                elif incx > 0:
                    rot += 45
        elif incx < 0:
            rot = self.R_LEFT
        elif incx > 0:
             rot = self.R_RIGHT

        return rot

    def test_direction(self, direction, incx, incy):
        # this is hacky, but my wife found a bug in last minute!
        if direction == self.R_UP and incy > 0:
            return True
        elif direction == self.R_DOWN and incy < 0:
            return True
        elif direction == self.R_LEFT and incx < 0:
            return True
        elif direction == self.R_RIGHT and incx > 0:
            return True
        else:
            return False

    def score(self, event):
        if "score" in event:
            id = event["score"]
            self._score.add(id)
            self.score_label.text = "Score %02d%% " % (len(self._score)*100//self.top_score)

    def set_map(self, mapname):
        # clean up pending actions
        if self.actions:
            for id, action in self.actions.iteritems():
                if action["type"] == "door":
                    for target in action["target"]:
                        props = self.map.cell("Fg", *target)
                        if props.get("opening", False):
                            z = -1.1
                            props["open"] = True
                            props["opening"] = False
                        else:
                            z = 0.0
                            props["open"] = False
                            props["opening"] = True
                        props["z"] = z
                        self.map.update_cell("Fg", *target, props=props)
                    logging.debug("action %r cleaned up" % action)
            self.map.compile(1) # 1 is Fg!
            self.actions = {}

        self.map = self.maps[mapname]

        if "title" in self.map.properties:
            self.location = pyglet.text.Label(self.map.properties["title"],
                                              x=4, y=0,
                                              font_name="Russo One",
                                              color=(255, 255, 255, 128),
                                              font_size=20,
                                              )
            if self.scene.height:
                self.location.y = self.scene.height-24
        elif self.location:
            del self.location
            self.location = None

    def unlock_doors(self):
        m = self.maps["control.json"]
        del m.extra["info"]["7,1"]
        m.extra["action"]["7,1"] = dict(id=2, type="door", valid=[7,2], target=[[5,1], [6,1]])
        m.tilelayers["Fg"].data[7+1*m.width] = 7 # green switch
        m.compile(1) # FG
        m = self.maps["dock_door.json"]
        del m.extra["info"]["6,7"]
        m.extra["action"]["6,7"] = dict(id=3, type="door", valid=[6,8], target=[[4,7], [5,7]])
        m.tilelayers["Fg"].data[6+7*m.width] = 7 # green switch
        m.compile(1) # FG

    def update(self, dt):

        incx = 0
        incy = 0
        rot = None
        if self.controls.up:
            incy += dt*self.speed
        if self.controls.down:
            incy -= dt*self.speed
        if self.controls.left:
            incx -= dt*self.speed
        if self.controls.right:
            incx += dt*self.speed
        if self.controls.escape:
            self.scene.bg_snd.pause()
            self.scene.parent.menu()

        if self.event and self.controls.action:
            if self.event_type == "info":
                if self.scene.msg is None:
                    req = self.event.get("required", None)
                    if req is None or req in self.flags:
                        alt = self.event.get("alt", None)
                        if alt in self.flags:
                            self.scene.show_message(self.event["alt_text"])
                            if "alt_snd" in self.event:
                                if self.event["alt_snd"] == "error":
                                    self.error_snd.play()
                                elif self.event["alt_snd"] == "denied":
                                    self.denied_snd.play()
                        else:
                            self.scene.show_message(self.event["text"])
                            if "snd" in self.event:
                                if self.event["snd"] == "error":
                                    self.error_snd.play()
                                elif self.event["snd"] == "denied":
                                    self.denied_snd.play()

                        self.score(self.event)
                        if "flag" in self.event:
                            logging.debug("flag %r set" % self.event["flag"])
                            self.flags[self.event["flag"]] = True

                        # too complex to do it scripted, so use python
                        special = self.event.get("special", None)
                        if special == "unlock" and "code" in self.flags:
                            self.unlock_doors()
                            del self.event["special"]
                        elif special == "dna" and "sample" in self.flags:
                                self.flags["dna"] = True
                                del self.event["special"]
                        elif special == "biometry" and "dna" in self.flags:
                                self.actions[99] = dict(id=99, type="door", target=[[2,1], [3,1]])
                                del self.event["special"]
                        elif special == "win":
                            ended = time() - self.scene.started
                            m = int(ended // 60)
                            self.scene.msg_queue.append("You played for %s minutes and scored %02d%%." % (m, (len(self._score)*100//self.top_score)))
                            self.scene.msg_queue.append("Thanks for playing the game.")
                            self.scene.quit = True
                            self.scene.bg_snd.pause()
                            del self.event["special"]

            elif self.event_type == "action" and self.event["id"] not in self.actions:
                self.score(self.event)
                logging.debug("action %s added" % self.event["id"])
                if self.event["type"] == "door":
                    self.door_snd.play()
                self.actions[self.event["id"]] = self.event

        # collision detection, helping the player to get in path
        px, py = self.px, self.py
        if incy != 0:
            py = self.top if incy > 0 else self.bottom
        if incx != 0:
            px = self.left if incx < 0 else self.right

        rot = self.facing(incx, incy)

        if incy !=0:
            if self.map.is_blocked(self.left, py+incy) or \
                self.map.is_blocked(self.center_x, py+incy) or \
                self.map.is_blocked(self.right, py+incy):
                if incx == 0 and not self.map.is_blocked(self.right, py+incy):
                    incx += dt*self.speed
                    rot = self.facing(incx, 0)
                elif incx == 0 and not self.map.is_blocked(self.left, py+incy):
                    incx -= dt*self.speed
                    rot = self.facing(incx, 0)
                incy = 0

        if incx != 0:
            if self.map.is_blocked(px+incx, self.top) or \
                self.map.is_blocked(px+incx, self.center_y) or \
                self.map.is_blocked(px+incx, self.bottom):
                if incy == 0 and not self.map.is_blocked(px+incx, self.top):
                    incy += dt*self.speed
                    rot = self.facing(0, incy)
                elif incy == 0 and not self.map.is_blocked(px+incx, self.bottom):
                    incy -= dt*self.speed
                    rot = self.facing(0, incy)
                incx = 0

        if incx != 0 or incy != 0:
            if not self.wheels_snd.playing:
                self.wheels_snd.play()
        elif self.wheels_snd.playing:
            self.wheels_snd.pause()

        self.py += incy
        self.px += incx
        if rot is not None:
            self.rot = rot

        # current cell, used for exists and some events
        cx, cy = self.map.cell_coord(self.center_x, self.center_y)

        # check exits
        exit = self.map.cell_exit(cx, cy)
        if exit and self.test_direction(exit["face"], incx, incy):
            logging.debug("exit: %r" % exit)
            self.set_map(exit["target"])
            self.px, self.py = self.map.to_screen(*exit["destination"])
            logging.debug("player to %s, %s" % (self.px, self.py))
            return

        # check if there's an event ahead
        if incx == 0 and incy == 0:
            pcx, pcy = cx, cy
            if self.rot == self.R_UP:
                cy -= 1
            elif self.rot == self.R_DOWN:
                cy += 1
            elif self.rot == self.R_LEFT:
                cx -= 1
            elif self.rot == self.R_RIGHT:
                cx += 1
            self.event_type, self.event = self.map.cell_event(cx, cy)
            # some events are only work if you're in a valid location
            if self.event and "valid" in self.event:
                vx, vy = self.event["valid"]
                if vx != pcx or vy != pcy:
                    self.event_type, self.event = None, None
        else:
            self.event_type, self.event = None, None

        # actions
        if self.actions:
            dirty = False
            pending = {}
            for id, action in self.actions.iteritems():
                if action["type"] == "door":
                    for target in action["target"]:
                        props = self.map.cell("Fg", *target)
                        # if we're not opening and we're not open, is opening
                        # otherwise it is not!
                        props["opening"] = props.get("opening", not props.get("open", False))
                        z = props.get("z", 0.0)
                        if props.get("opening"):
                            if z > -1.1:
                                z = max(-1.1, z-dt*0.6)
                                dirty = True
                                pending[id] = action
                            else:
                                logging.debug("action %s done" % id)
                                props["open"] = True
                                props["opening"] = False
                        else:
                            if z < 0.0: # this is the ground
                                props["open"] = False
                                z = min(0.0, z+dt*0.6)
                                dirty = True
                                pending[id] = action
                            else:
                                logging.debug("action %s done" % id)
                                # it's closed
                                props["opening"] = True

                        props["z"] = z
                        self.map.update_cell("Fg", *target, props=props)

            self.actions = pending
            if dirty:
                self.map.compile(1) # 1 is Fg!

    def on_resize(self, width, height):
        self.score_label.y = height-24
        self.score_label.x = width
        self.inv_label.x = width
        if self.location:
            self.location.y = height-24

    def draw(self):
        self.scene.parent.set_3d()
        self.map.draw()

        gl.glPushMatrix()
        gl.glTranslatef(self.px, self.py, 0)
        gl.glRotatef(90, 1, 0, 0)
        gl.glRotatef(self.rot, 0, 1, 0)
        self.player.draw()
        gl.glPopMatrix()

        if self.event:
            req = self.event.get("required", None)
            if req is None or req in self.flags:
                gl.glPushMatrix()
                gl.glLoadIdentity()
                gl.glTranslatef(self.center_x-0.5, self.center_y, 2.0)
                gl.glScalef(0.02, 0.02, 0.02)
                gl.glRotatef(45, 1, 0, 0)
                self.attention.blit(0, 0, 0)
                gl.glPopMatrix()

        self.scene.parent.set_2d()
        self.score_label.draw()
        if self.location:
            self.location.draw()
        if "sample" in self.flags:
            if "dna" in self.flags:
                self.inv_label.text = "Campbell's blood "
            else:
                self.inv_label.text = "Blood sample "
            self.inv_label.draw()

class GameScene(Scene):
    START = Intro
    STATES = (Intro, CutScene, Play,)

    MSG_WIDTH = 760

    def __init__(self, parent, **kwargs):
        self.started = None

        self.fade = None
        self.alpha = None
        self.alpha_to = 0

        self.quit = False
        self.msg = None
        self.msg_text = None
        self.msg_y = 0
        self.msg_top = 0
        self.msg_queue = []

        super(GameScene, self).__init__(parent, **kwargs)

        self.noise = pyglet.resource.media("noise.ogg")

        self.bg_snd = pyglet.resource.media("bg.ogg").play()
        self.bg_snd.eos_action = "loop"
        self.bg_snd.pause()
        self.bg_snd.volume = 0.3

        self.label = pyglet.text.Label(text="",
                                       color=(255, 255, 255, 192),
                                       multiline=True,
                                       width=self.MSG_WIDTH,
                                       font_name="Russo One",
                                       font_size=12,
                                       anchor_x="center",
                                       )

    def fade_in(self):
        self.fade = "in"
        self.alpha = 1.0
        self.alpha_to = 0.0

    def fade_out(self):
        self.fade = "out"
        self.alpha = 0.0
        self.alpha_to = 1.0

    def abort_fade(self):
        self.alpha = 0

    def show_message(self, text):
        if isinstance(text, list):
            self.msg_queue = list(text)
            text = self.msg_queue.pop(0)

        logging.debug("show_message: %r" % text)
        lines = len(text.split("\n"))
        self.msg = "show"
        self.msg_y = 0
        self.msg_top = (lines+1)*24
        self.msg_text = text
        self.label.text = text
        self.label.x = self.width // 2
        self.label.width = self.MSG_WIDTH

    def dismiss_message(self):
        logging.debug("dismiss_message")
        self.msg = "dismiss"
        if self.msg_queue:
            self.show_message(self.msg_queue)
        elif self.quit:
            self.fade_out()

    def on_resize(self, width, height):
        super(GameScene, self).on_resize(width, height)

        self.label.x = self.width // 2

    def update(self, dt):
        if not self.quit:
            super(GameScene, self).update(dt)

        if self.alpha is not None:
            if self.fade == "in":
                self.alpha = max(0.0, self.alpha - dt*0.25)
            else:
                self.alpha = min(1.0, self.alpha + dt*0.25)

        if self.msg_text:
            if self.msg == "show":
                if self.msg_y < self.msg_top:
                    self.msg_y = min(self.msg_top, self.msg_y+dt*400)
                elif self.parent.controls.action:
                    self.dismiss_message()
            elif self.msg == "dismiss":
                if self.msg_y > 0:
                    self.msg_y = max(0, self.msg_y-dt*600)
                else:
                    self.msg = None
                    self.msg_text = None
                    logging.debug("message dismissed")

    def draw(self):
        super(GameScene, self).draw()

        if self.msg_text is not None:
            self.parent.set_2d()
            gl.glPushAttrib(gl.GL_DEPTH_BUFFER_BIT | gl.GL_LIGHTING_BIT)
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_LIGHTING)

            gl.glColor4f(0.38, 0.49, 0.56, 0.4)
            x = self.width//2 - self.MSG_WIDTH//2 - 4
            y = int(self.msg_y) + 24.0
            w = x + self.MSG_WIDTH + 4
            pyglet.graphics.draw(4, gl.GL_QUADS, ('v2f', (x, 0, w, 0, w, y, x, y,)))

            self.label.y = int(self.msg_y)
            self.label.draw()

            gl.glPopAttrib()

        if self.alpha is not None:
            self.parent.set_2d()
            gl.glPushAttrib(gl.GL_DEPTH_BUFFER_BIT | gl.GL_LIGHTING_BIT)
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_LIGHTING)

            gl.glColor4f(0, 0, 0, self.alpha)
            pyglet.graphics.draw(4, gl.GL_QUADS, ('v2f', (0, 0, self.width, 0, self.width, self.height, 0, self.height,)))

            gl.glPopAttrib()

            if self.alpha == self.alpha_to:
                self.alpha = None
                logging.debug("GameScene: fade %s done" % self.fade)
                if self.quit:
                    self.parent.menu()

