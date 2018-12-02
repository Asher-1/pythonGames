from __future__ import division

import interface
from vector import v

from pyglet.gl import *
import random

from constants import *

class BattlePanel(interface.Panel):
    team = interface.Attribute(None)
    background_color = interface.Attribute((0.2,0.2,0.2,1.0))

    def init_panel(self):
        super(BattlePanel, self).init_panel()
        self.camera = None
        self.camera_queue = []

        p = v((0, 0))
        for subject in self.team:
            subject.position(v((0, 0)))
            subject.create_sprites() # to initialise bounding box - kind of awkward
            min_x = subject.bounding_box.lo.x
            max_x = subject.bounding_box.hi.x
            p -= v((min_x, -TEAM_HEIGHT_OFFSET))
            subject.position(p)
            subject.create_sprites()
            p += v((max_x, -TEAM_HEIGHT_OFFSET))
        
    def draw_content(self):
        if not self.camera: return
        
        with self.camera:
            for subject in self.team:
                for p in subject.all_parts_to_draw():
                    # this should be more sophisticated eventually, they
                    # shouldn't disappear instantaneously
                    if p.disabled: 
                        p.sprite.color = (64, 32, 32)
                                            
                    p.sprite.draw()
                    if False:
                        bb = p.bounding_box
                        glBegin(GL_LINE_LOOP)
                        glVertex2f(bb.lo.x, bb.lo.y)
                        glVertex2f(bb.lo.x, bb.hi.y)
                        glVertex2f(bb.hi.x, bb.hi.y)
                        glVertex2f(bb.hi.x, bb.lo.y)
                        glEnd()
            # did this line do anything?
            #bb = self.subject.bounding_box
                
    def tick(self):
        if self.camera_queue and self.camera.ambient:
            self.camera = self.camera_queue.pop(0)
            self.camera.ambient = False
        if not self.camera or self.camera.done:
            camclass = random.choice([LongPan, WideShot])
            if self.team.active and random.random() < 0.5:
                # individual shot
                subject = self.team.random_active()
            else:
                # whole team shot
                subject = self.team
            self.camera = camclass(self.content_size, subject)
        self.camera.tick()
    
    def show_attack(self, user, part):
        if part:
            self.camera_queue.append(PartZoom(self.content_size, user, part=part, speed='fast'))
        else:
            self.camera_queue.append(WideShot(self.content_size, user, speed='fast'))
            

class Camera(object):
    def __init__(self, content_size, subject, **kwargs):
        self.content_size = content_size
        self.subject = subject 
        self.bbox = self.subject.bounding_box
        self.tickcount = 0
        self.ambient = True
        self.kwargs = kwargs
        self.setup()
    
    def setup(self):    
        self.target_zoom = 1
        self.init_zoom = 1       
        self.target_focus = self.bbox.center
        self.init_focus = self.bbox.center
        self.anim_length = 180
        
    def tick(self):
        alpha = (self.tickcount % self.anim_length) / self.anim_length            
            
        self.zoom = (1 - alpha) * self.init_zoom + alpha * self.target_zoom
        self.focus = (1 - alpha) * self.init_focus + alpha * self.target_focus
        
        self.tickcount += 1
        
    def __enter__(self):
        cw, ch = self.content_size
        glPushMatrix()
        glTranslatef(cw/2, ch/2, 0);
        glScalef(self.zoom, self.zoom, self.zoom)
        glTranslatef(-self.focus[0], -self.focus[1], 0)
    
    def __exit__(self, exc_type, exc_value, traceback):
        glPopMatrix()
    
    @property
    def done(self):
        return self.tickcount >= self.anim_length
        
class RandomCamera(Camera):
    def setup(self):
        self.init_zoom = random.uniform(1,1.5)
        self.target_zoom = random.uniform(1,2)
        self.init_focus = v((random.uniform(self.bbox.lo[0], self.bbox.hi[0]), random.uniform(self.bbox.lo[1], self.bbox.hi[1])))
        self.target_focus = v((random.uniform(self.bbox.lo[0], self.bbox.hi[0]), random.uniform(self.bbox.lo[1], self.bbox.hi[1])))
        self.anim_length = random.randint(180, 300)
        
class LongPan(Camera):
    def setup(self):
        sw = self.bbox.width
        sh = self.bbox.height
        hs = self.content_size[0]/sw
        vs = self.content_size[1]/sh
        zoom = max(hs, vs) 
        self.init_zoom = zoom
        self.target_zoom = zoom
        if hs > vs:
            offset = v(sw/2, sw/2 * vs/hs)
        else:
            offset = v(sh/2 * hs/vs, sh/2)
        self.init_focus = self.bbox.lo + offset
        self.target_focus = self.bbox.hi - offset
        if random.random() > .5:
            self.init_focus, self.target_focus = self.target_focus, self.init_focus
        if self.kwargs.get('speed', None) == 'fast':
            self.anim_length = random.randint(40, 50)
        else:
            self.anim_length = random.randint(300, 600)

class PartZoom(Camera):
    def setup(self):
        try:
            p = self.kwargs['part']
        except:
            p = random.choice([p for p in self.subject.all_parts() if not p.children])
        bb = p.bounding_box
        pw = bb.width
        ph = bb.height
        zoom = min(self.content_size[0]/pw, self.content_size[1]/ph)
        self.init_zoom = zoom * random.uniform(0.9, 1)
        self.target_zoom = zoom * random.uniform(1.2, 2)
        focus = bb.center
        self.init_focus = focus
        self.target_focus = focus
        if self.kwargs.get('speed', None) == 'fast':
            self.anim_length = random.randint(40, 50)
        else:
            self.anim_length = random.randint(90, 120)
        
class WideShot(Camera):
    def setup(self):
        zoom = min(self.content_size[0]/self.bbox.width, self.content_size[1]/self.bbox.height)
        self.init_zoom = zoom * random.uniform(1, 1.1)
        self.target_zoom = zoom * random.uniform(0.9, 1)
        focus = self.bbox.center
        self.init_focus = focus
        self.target_focus = focus
        if self.kwargs.get('speed', None) == 'fast':
            self.anim_length = random.randint(40, 50)
        else:
            self.anim_length = random.randint(120, 180)
