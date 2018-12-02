
from pyglet.gl import *
from pyglet.window import key
import pyglet

from euclid import *
from vectorgraph import *
from batchmanager import batch
from util import *

from attaboy import MsgQueue

letterbox_color = [0.0, 0.0, 0.0, 0.0]
letterbox_quads = [-10,-1,-10,   10,-1,-10,   10,-1,10,   -10,-1,10]

bandpic_color = [1.0, 1.0, 1.0, 1.0]
bandpic_quads = [-2,-1,0,   2,-1,0,   2,-1,4,   -2,-1,4]




class Timer (object):
    def __init__(self, time):
        self.time = time-1
        self.last_second = 59
        self.color = ([40/255.0,220/255.0,180/255.0,1.0], [0.0,0.1,0.0,1.0])
        self.display = VectorString("time %s" % self.format_time(), (1.6,0,-0.8), 0.08, self.color)

    def update_time(self, dt):
        #self.time -= dt
        if int(self.time % 60) <= self.last_second or 0 == self.last_second:
            self.display.set_string("time %s" % self.format_time())
            self.last_second = int(self.time % 60)
        else:
            pass
        self.time -= dt
    def format_time(self):
        m = self.time / 60.0
        s = self.time % 60.0
        string = "%02d %02d" % (int(m), int(self.last_second))
        return string

class Mutation (object):
    def __init__(self, mutation):
        self.mutation = mutation
        self.color = ([40/255.0,220/255.0,180/255.0,1.0], [0.0,0.1,0.0,1.0])
        self.display = VectorString("mutation %03d" % mutation, (1.6,0,0.0), 0.08, self.color)


    def set_mutation(self, mutation):
        self.mutation = mutation
        self.display.set_string("mutation %03d" % int(self.mutation))


###############################################################################
############################################################# AboutPic ########
###############################################################################

class AboutPic (object):

    def __init__(self, filename, speed = 0.1):
        self.texture = pyglet.image.load(filename).get_texture()
        self.group = TextureBindGroup(self.texture)

        self.vertex_list = batch._batch.add(4, GL_QUADS, self.group,
                ("v3f", bandpic_quads),
                ("c4f", bandpic_color * 4),
                ("t2f", [0,0,  1,0,  1,1,  0,1])
            )
        self.speed = speed
        self.time = 0.0
        self.finished = False

    def delete(self):
        self.vertex_list.delete()

    def update(self, dt):
        if not self.finished:
            if self.time < 1:
                self.time += self.speed * dt
            else:
                self.finished = True




###############################################################################
############################################################# ATCGDisplay #####
###############################################################################

_BASE_COLORS = {
    "A": ([1, 1, 0, 1.0], [1, 1, 0, 0.1]),
    "T": ([0, 1, 0, 1.0], [0, 1, 0, 0.1]),
    "C": ([0, 0, 1, 1.0], [0, 0, 1, 0.1]), # red 0.30 green 0.30 blue 1.00
    "G": ([1, 0, 0, 1.0], [1, 0, 0, 0.1]),
}

class ATCGDisplay (object):

    def __init__(self,):
        self.attaboy = MsgQueue()
        self.A = self.attaboy.on_off("a", 0.1, _BASE_COLORS['A'], pos=(-2,0,0))
        self.T = self.attaboy.on_off("t", 0.1, _BASE_COLORS['T'], pos=(-2,0,-0.3))
        self.C = self.attaboy.on_off("c", 0.1, _BASE_COLORS['C'], pos=(-2,0,-0.6))
        self.G = self.attaboy.on_off("g", 0.1, _BASE_COLORS['G'], pos=(-2,0,-0.9))

    def update(self, dt):
        self.attaboy.update(dt)


###############################################################################
############################################################### MainMenu ######
###############################################################################

class MainMenu (object):

    def __init__(self, pos=Point3(6.1, 0.0, 1.9)):
        self.choices = {  1: 'new game',
                          2: 'tutorial',
                          3: 'fullscreen',
                          4: 'about',
                          5: 'quit'
                    }
        self.choice = 1
        self.pos = pos
        self.attaboy = MsgQueue()
        self.title = VectorString("genome hero", (3,0,2.0), 0.3)
        self.labels = self.build_labels()
        self.labels[0].unpause()
        
    def build_labels(self):
        tl = []
        x, y, z = self.pos[:]
        for c in self.choices.keys():
            lx, lz = x, (z + (c*-0.7))# + -0.6
            l = self.attaboy.pulse(self.choices[c], 0.16, 1, (lx,0,lz))
            l.pause()
            tl.append(l)
        return tl

    def on_key_press(self, k, args):
        labels = self.labels
        if k == key.UP:
            if self.choice == 1:
                labels[self.choice-1].pause(1)
                self.choice = len(self.choices)
                labels[self.choice-1].unpause()
            else:
                labels[self.choice-1].pause(1)
                self.choice -= 1
                labels[self.choice-1].unpause()

        elif k == key.DOWN:
            if self.choice == len(self.choices):
                labels[self.choice-1].pause(1)
                self.choice = 1
                labels[self.choice-1].unpause()
            else:
                labels[self.choice-1].pause(1)
                self.choice += 1
                labels[self.choice-1].unpause()
        else:
            return True

    def update(self, dt):
        self.attaboy.update(dt)
        

###############################################################################
################################################################# Score #######
###############################################################################

class Score (object):
    def __init__(self, points):
        self.points = points
        self.color = ([40/255.0,220/255.0,180/255.0,1.0], [0.0,0.1,0.0,1.0])
        self.display = VectorString("%08d" % points, (1.6,0,-1.8), 0.08, self.color)


    def inc_score(self, points):
        self.points += points
        self.display.set_string("%08d" % self.points)


###############################################################################
################################################################# Streak ######
###############################################################################

class Streak (object):
    def __init__(self, streak):
        self.streak = streak
        self.attaboy = MsgQueue()
        self.color = ([1.0, 0.0, 0.0,1.0], [0.1,0.0,0.0,1.0])
        self.msg_color = ([40/255.0,220/255.0,180/255.0,1.0], [0.0,0.1,0.0,1.0])
        self.display = VectorString("streak%03d" % streak, (1.6,0,-1.55), 0.08, self.color)

    def inc(self):
        self.streak += 1
        self.display.set_string("streak%03d" % self.streak)
        return self.streak

    def reset(self):
        self.streak = 0
        self.display.set_string("streak%03d" % self.streak)

    def report(self):
        if messages.STREAK_TEXT.has_key(s):
            self.attaboy.add_centered_fade(messages.STREAK_TEXT[s], 0.2, 1, self.msg_color)

    def update(self, dt):
        self.attaboy.update(dt)

if __name__ == '__main__':
    v = VectorChar()
    print v.vertices
