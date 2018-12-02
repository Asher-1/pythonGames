from pyglet.gl import *
import random

from euclid import *

class Camera (object):
    
    def __init__(self, pos, target):
        self.pos = Point3(pos[0], pos[1], pos[2])
        self.target = Point3(target[0], target[1], target[2])
        self.shaking = False
        self.shake_duration = 0
        self.shake_inten = 0
        self.shake_freq = 0
        self.shake_x = 0
        self.shake_z = 0
        self.subtle_motion = False
        self.subtle_x = 0
        self.subtle_z = 0
        self.subtle_x_dir = -1
        self.subtle_z_dir = 1
        self.subtle_range = (1.5, -1.5)
        self.subtle_speed = 0.01
        
    def focus(self):
        x = self.shake_x + self.pos.x + self.subtle_x
        z = self.shake_z + self.pos.z + (self.subtle_z*2)
        gluLookAt(x, self.pos.y, z, 
            self.target.x, self.target.y, self.target.z, 
            0.0, 0.0, 1.0) ## 

    def update(self, dt):
        if self.shake_duration <= 0:
            self.shaking = False
            self.shake_x = 0
            self.shake_z = 0
        if self.shaking:
            self.shake_x = self.shake_inten * random.uniform(-0.3, 0.3)
            self.shake_z = self.shake_inten * random.uniform(-0.3, 0.3)
            self.shake_duration -= dt
        elif self.subtle_motion:
            speed = self.subtle_speed
            if self.subtle_x >= self.subtle_range[0]:
                self.subtle_x_dir = random.randint(-1, 0)
            elif self.subtle_x <= self.subtle_range[1]:
                self.subtle_x_dir = random.randint(0, 1)
                
            if self.subtle_z >= self.subtle_range[0]:
                self.subtle_z_dir = random.randint(-1, 0)
            elif self.subtle_z <= self.subtle_range[1]:
                self.subtle_z_dir = random.randint(0, 1)

            self.subtle_x += 0.01 * self.subtle_x_dir
            self.subtle_z += 0.01 * self.subtle_z_dir
            
                
            
            

    def shake(self, duration, intensity, freq):
        self.shaking = True
        self.shake_duration = duration
        self.shake_inten = intensity
        self.shake_freq = freq

        
