import pyglet
from gamelib import app

class Sound(object):
    def __init__(self, *names):
        self.names = ['sounds/'+name for name in names]
    def __call__(self):
        if app.config.get('sound'):
            name = self.names.pop(0)
            self.names.append(name)
            try:return pyglet.resource.media(name, streaming=False).play()
            except:pass
    def repeat(self, delays):
        return repeat(self, delays)

def sequence(sounds, delays):
    assert len(sounds) == len(delays) + 1
    @staticmethod
    def play():
        ss = list(sounds)
        ds = list(delays)
        def _play(dt):
            ss.pop(0)()
            if ds:
                pyglet.clock.schedule_once(_play, ds.pop(0))
        _play(None)
    return play

def repeat(sound, delays):
    return sequence([sound] * (len(delays) + 1), delays)

sting = Sound('sting.wav')
click = Sound('click.wav')
pop = Sound('pop.wav')
negative = Sound('negative.wav')
victory = Sound('victory.wav')
bite = Sound('bite.wav')
miss = Sound('miss.wav')
multipunch = Sound('multipunch.wav')
punch = Sound('punch1.wav', 'punch2.wav')
whip = Sound('whip1.wav', 'whip2.wav')
peck = Sound('peck.wav')
laser = Sound('laser.wav')
