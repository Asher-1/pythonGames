import pyglet
from gamelib import app

class Sound(object):
    def __init__(self, *names):
        self.names = list(names)
        self.player = None
        self.repeater = True
    def __call__(self):
        if app.config.sound and (not self.player or not self.player.playing or self.repeater):
            name = self.names.pop(0)
            self.names.append(name)
            try:
                self.player = pyglet.resource.media(name, streaming=False).play()
            except:
                pass
            return self.player

arrows = Sound('arrows.wav')
click = Sound('click.wav')
enchant = Sound('enchant.wav')
explosion = Sound('explosion.wav')
firebomb = Sound('firebomb.wav')
hit = Sound('hit.wav')
hit.repeater = False
laser = Sound('laser.wav')
missile = Sound('missile.wav')
miniexplosion = Sound('miniexplosion.wav')
negative = Sound('negative.wav')
repel = Sound('repel.wav')
scroll = Sound('scroll.wav')
shield = Sound('shield.wav')
shot = Sound('shot.wav')
summon = Sound('summon.wav')
teleport = Sound('teleport.wav')
vortex = Sound('vortex.wav')
