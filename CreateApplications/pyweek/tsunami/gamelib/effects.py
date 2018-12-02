import pyglet.graphics
import pyglet.resource
import pyglet.sprite
import os.path
from pyglet.gl import *

from random import randrange as rr, random
from util import Vector

from math import cos, sin, radians
from cocos.batch import BatchNode
from cocos.layer import Layer
from cocos.director import director

class Bubble: 
    def __init__(self, pos, speed,frame,size):
        self.pos, self.speed, self.frame, self.size = pos, speed, frame, size

class BubbleManager( BatchNode ):
    def __init__(self, width, num, racer):
        super( BubbleManager, self ).__init__()
        self.racer = racer
        self.view_width = width
        self.goodies = []
        self.batch = pyglet.graphics.Batch()
        self.fimg = pyglet.resource.image('bubble.png')
        self.group = pyglet.sprite.SpriteGroup(self.fimg.texture,
                             blend_src=GL_ONE, blend_dest=GL_ONE)
        self.vertex_list = self.batch.add(4*num, GL_QUADS, self.group,
            'v2i', 'c4B', ('t3f', self.fimg.texture.tex_coords*num))
        for n in xrange(0, num):
            f = Bubble(Vector(), Vector(),0,0)
            self.goodies.append(f)
            self.vertex_list.vertices[n*8:(n+1)*8] = [0, 0, 0, 0, 0, 0, 0, 0]
            self.vertex_list.colors[n*16:(n+1)*16] = [0,0,0,0,] * 4
        self.schedule( self.step )

    def replenish (self):
        bubbles = self.goodies
        rot = Vector(cos(radians(self.racer.rotation)), -sin(radians(self.racer.rotation)))
        for n, f in enumerate(bubbles):
            if not f.frame:
                vx = rr(-5,0)/3.0
                vy = rr(-self.view_width / 2, self.view_width / 2)/3.0
                f.speed = Vector(vx, vy) * rot
                f.pos =Vector(*self.racer.position) + (f.speed +  Vector (-20, 0)) * rot
                f.frame = rr(20,50)
                f.size = 12+pow(rr(0.0,70)/100.0,2.0)*32;
                f.scale= f.size/64.0


    def step(self,dt):
        w,h = self.fimg.width,self.fimg.height
        bubbles = self.goodies
        verts, clrs = self.vertex_list.vertices, self.vertex_list.colors
        for n,f in enumerate(bubbles):
            if not f.frame:
                continue
            x = f.pos.real + random() * f.speed.real + (random()*4.5 - 2.25) * f.speed.real
            y = f.pos.imag + random() * f.speed.imag + (random()*4.5 - 2.25) * f.speed.imag
            f.pos = Vector(x, y)
            f.speed = Vector(f.speed.real * (random()*0.03+0.97), f.speed.imag * (random()*0.03+0.97))
            c = 8*f.frame/255.0;
            r,g,b = (min(255,int(c*0x14)),min(255,int(c*0x30)),min(255,int(c*0x61)))
            f.frame -= 1
            ww,hh = w*f.scale,h*f.scale
            x-=ww/2
            verts[n*8:(n+1)*8] = map(int,[x,y,x+ww,y,x+ww,y+hh,x,y+hh])
            clrs[n*16:(n+1)*16] = [r,g,b,255] * 4


class Caustics (Layer):

    TEXCOUNT = 32
    INTERVAL = 0.08

    def __init__ (self, color=(0.0,0.3,0.4,1.0), scroller=None):
        super (Caustics, self).__init__ ()
        self.texs = [None]*self.TEXCOUNT
        for i in range(self.TEXCOUNT):
            self.texs[i] = pyglet.resource.image (os.path.join('water','save.%02d.tif' % (i+1)))
        self.width, self.height = director.get_window_size()
        self.current = 0
        self.color = color
        if scroller:
            scroller.add_action (self.scroll)

    def on_enter(self):
        super (Caustics, self).on_enter ()
        self.schedule_interval (self.change, self.INTERVAL)

    def on_exit(self):
        super (Caustics, self).on_exit ()
        self.unschedule (self.change)
    
    def scroll (self, p):
        self.x = p[0] % self.width
        self.y = p[1] % self.height

    def change(self, dt):
        self.current = (self.current + 1) % self.TEXCOUNT

    def draw (self):
        super (Caustics, self).draw()

        w, h = self.width, self.height
        glColor4f(*self.color)
        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)
        self.texs[self.current].blit(self.x-0, self.y-0, width=w, height=h)
        self.texs[self.current].blit(self.x-w, self.y-0, width=w, height=h)
        self.texs[self.current].blit(self.x-0, self.y-h, width=w, height=h)
        self.texs[self.current].blit(self.x-w, self.y-h, width=w, height=h)

