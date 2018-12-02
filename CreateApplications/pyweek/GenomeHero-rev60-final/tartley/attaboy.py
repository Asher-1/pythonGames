from util import *
from ui import VectorString


class MsgTransition (object):
    def __init__(self, msg):
        self.msg = msg
        self.children = []
        self.finished = False

    def update(self, dt):
        pass

    def add(self, trans):
        self.children.append(trans)



class OnOff (MsgTransition):
    def __init__(self, msg, colors):
        MsgTransition.__init__(self, msg)
        self.colors = colors
        self.off()
        
    def update(self, dt):
        return False
        
    def on(self):
        self.msg.set_string(self.msg.string)

    def off(self):
        self.msg.set_string(" "*len(self.msg.char_list))

        



class Fade (MsgTransition):
    def __init__(self, msg, speed):
        MsgTransition.__init__(self, msg)
        self.alpha = 1.0
        self.speed = speed

    def update(self, dt):
        new_colors = []
        self.alpha -= self.speed * dt 
        colors = self.msg.get_colors()
        for c in colors:
            c[3] = self.alpha
        self.msg.set_colors(colors)
        if self.alpha <= 0.0:
            self.finished = True
            return True
        return False

class Pulse (MsgTransition):
    def __init__(self, msg, speed):
        MsgTransition.__init__(self, msg)
        self.alpha = 1.0
        self.inc_dir = -1
        self.speed = speed
        self.paused = False

    def update(self, dt):
        if self.paused:
            return False
        new_colors = []
        self.alpha += (self.speed * dt) *self.inc_dir
        colors = self.msg.get_colors()
        colors[0][3] = self.alpha
        self.msg.set_colors(colors)

        if self.alpha <= 0.0:
            self.inc_dir = 1
        if self.alpha >= 1.0:
            self.inc_dir = -1
        return False

    def pause(self, full_bright=None):
        if full_bright:
            self.alpha = 1.0
            colors = self.msg.get_colors()
            for c in colors:
                c[3] = self.alpha
            self.msg.set_colors(colors)
        self.paused = True

    def unpause(self):
        self.alpha = 0.0
        colors = self.msg.get_colors()
        for c in colors:
            c[3] = self.alpha
        self.msg.set_colors(colors)
        self.paused = False
        


class Mover (MsgTransition):
    def __init__(self, msg, speed, vector=Vector3(0,0,0), target=Point3(0,0,0)):
        MsgTransition.__init__(self, msg)
        self.speed = speed
        self.vector = vector
        
    def update(self, dt):
        d = speed*dt
        v = self.vector
        x,y,z = v.x*d, v.y*d, v.z*d
        self.msg.move((x,y,z))


class MsgQueue (object):
    def __init__(self):
        self.messages = []

    def add_msg(self, tmsg):
        self.messages.append(tmsg)
        
    def update(self, dt):
        dead = []
        for m in self.messages:
            m.update(dt)
            if m.finished:
                dead.append(m)
            for d in dead:
                try:
                    self.messages.remove(d)
                except ValueError:
                    pass #print "already removed"
                m.msg.delete()
            

    def add_centered_fade(self, msg, size, speed, color=([0.0,0.7,0.0,1.0], [0.0,0.1,0.0,1.0])):
        msg = msg.split("\n")
        print msg
        tm = None
        for n in range(0, len(msg)):
            spacing = size + (size/1.5)
            vsize = spacing * len(msg[n]) /2 #
            hsize = spacing * len(msg)/2
            m =  VectorString(msg[n], (0-(vsize),0,(1.0-(n*hsize))+(len(msg)/3) ), size, color)
            tm = Fade(m, speed)
            self.add_msg(tm)
        return tm

    def add_score_fade(self, points):
        color = ([1.0, 0.0, 0.0,1.0], [0.1,0.0,0.0,1.0])
        m =  VectorString("+%d" % points, (1.6,0,-1.2), 0.1, color)
        tm = Fade(m, 1.1)
        self.add_msg(tm)
        return tm
        
    def pulse(self, msg, size, speed, pos=Point3(0,0,0)):
        m =  VectorString(msg, pos, size)
        tm = Pulse(m, speed)
        self.add_msg(tm)
        return tm

    def on_off(self, msg, size, colors, pos=Point3(0,0,0)):
        m =  VectorString(msg, pos, size, colors)
        tm = OnOff(m, colors)
        tm.off()
        self.add_msg(tm)
        return tm



#pos + (0+(spacing*n),0,0) spacing = size + (size/1.5)

