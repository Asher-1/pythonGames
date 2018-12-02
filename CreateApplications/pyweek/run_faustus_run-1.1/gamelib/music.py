import pyglet
from gamelib import app


class MusicMan(object):
    def __init__(self):
        self.current = None
        self.player = pyglet.media.Player()
        self.player.eos_action = self.player.EOS_LOOP
        self.eos = None
    def change_track(self, name):
        if app.config.music:
            if name != self.current:
                source = pyglet.resource.media(name, streaming=False)
                self.player.next()
                self.player.queue(source)
                self.player.play()
                self.current = name
    def set_eos(self, value):
        if value is not None:
            self.player.eos_action = self.player.EOS_STOP
            self.eos = value
    def on_player_eos(self):
        if self.eos is not None:
            self.eos()
            self.player.eos_action = self.player.EOS_LOOP
            return True
