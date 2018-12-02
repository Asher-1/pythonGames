#!/usr/bin/python

"""
submarine.py - classes for player controlled submarine
"""

import os
import pygame
from pygame.locals import *
from gamedirector import *

import random
from math import *

import pymunk
from pymunk import Vec2d

import resources

class KeyControl(object):
    def __init__(self,controlmap):
        self.CM = controlmap
        self.l = 0
        self.r = 0
        self.u = 0
        self.d = 0
        self.fire = 0
    
    def ProcessKeyEvent(self,event):
        if event.type == KEYDOWN:
            if event.key == self.CM["L"]:
                self.l = 1
            elif event.key == self.CM["R"]:
                self.r = 1
            elif event.key == self.CM["U"]:
                self.u = 1
            elif event.key == self.CM["D"]:
                self.d = 1
            elif event.key == self.CM["Fire"]:
                self.fire = True
        elif event.type == KEYUP:
            if event.key == self.CM["L"]:
                self.l = 0
            elif event.key == self.CM["R"]:
                self.r = 0
            elif event.key == self.CM["U"]:
                self.u = 0
            elif event.key == self.CM["D"]:
                self.d = 0
            elif event.key == self.CM["Fire"]:
                pass

def looseharpoon_hit_func(space, arbiter):
    a,b = arbiter.shapes
    position = arbiter.contacts[0].position
    b.collision_type = 0
    b.group = 1
    other_body = a.body
    harpoon_body = b.body
    pivotjoint = pymunk.PivotJoint(harpoon_body, other_body, position)
    harpoon_body.space.add(pivotjoint)
    harpoon_body.harpoonparent.harpconst = pivotjoint

def harpoon_hit_func(space, arbiter):
    a,b = arbiter.shapes
    position = arbiter.contacts[0].position
    b.collision_type = 0
    b.group = 1
    other_body = a.body
    harpoon_body = b.body
    if harpoon_body.harpoonparent.state == 1:
        
        x3 = position[0]-other_body.position[0]
        y3 = position[1]-other_body.position[1]
        angle3 = other_body.angle
        x4 = x3*cos(angle3) + y3*sin(angle3)
        y4 = -x3*sin(angle3) + y3*cos(angle3)
        hook_other_point = (x4, y4)
        
        harpoon_body.harpoonparent.hook_end_data = [hook_other_point, other_body, harpoon_body.angle-other_body.angle]
        slidejoint = pymunk.SlideJoint(other_body, harpoon_body.harpoonparent.parent.body, hook_other_point, (0.0,0.0), 0.0, 100.0)
        space.add(slidejoint)
        harpoon_body.harpoonparent.harpconst_slidejoint = slidejoint
        harpoon_body.harpoonparent.parent.space.remove(harpoon_body,harpoon_body.harpoonparent.hook[1])
        harpoon_body.harpoonparent.state = 2
        
        resources.soundfx['bigthud'].play()

def harpoon_hit_monster(space, arbiter):
    a,b = arbiter.shapes
    position = arbiter.contacts[0].position
    
    other_body = a.body
    harpoon_body = b.body
    
    if b.collision_type == 1: # was on rope
        harpoon_body.harpoonparent.looseharpoons.append(LooseHarpoon(harpoon_body.harpoonparent,harpoon_body.harpoonparent.hook,harpoon_body.harpoonparent.parent.heading))
        harpoon_body.harpoonparent.hook[1].harpoonparent = harpoon_body.harpoonparent.looseharpoons[-1]
        harpoon_body.harpoonparent.hook = []
        harpoon_body.harpoonparent.state = 0
        harpoon_body.harpoonparent.hook_to = 0
    
    b.collision_type = 0
    b.group = 1
    
    a.collision_type = 0
    a.group = 1
    
    pivotjoint = pymunk.PivotJoint(harpoon_body, other_body, position)
    harpoon_body.space.add(pivotjoint)
    harpoon_body.harpoonparent.harpconst = pivotjoint
    
    other_body.monster_ref.Kill()

class LooseHarpoon(object):
    def __init__(self,parent,hook,heading):
        self.parent = parent
        self.body = hook[0]
        self.shape = hook[1]
        self.heading = heading
        self.to = 20
    
    def Update(self):
        self.to -= 1
        gain_x = 0.1
        self.body.apply_impulse((-gain_x*self.body.velocity[0],30.0)) # drag and buoyancy
        if self.to == 0:
            self.parent.parent.space.remove(self.shape,self.body)
    
    def Draw(self,screen):        
        ang_ind = int(round((180*self.body.angle/pi+180)/10.0)) % 35
        sprite_data = resources.harpoon_spritedata[ang_ind]
        x = int(self.body.position[0])
        y = int(-self.body.position[1])
        (imw,imh) = (sprite_data.get_width(),sprite_data.get_height())
        screen.blit(sprite_data, (x-(imw/2)-self.parent.parent.h_camera.x+self.parent.parent.h_camera.w_view/2,y-(imh/2)-self.parent.parent.h_camera.y+self.parent.parent.h_camera.h_view/2))

class Harpoons(object):
    def __init__(self,parent):
        
        self.parent = parent
        self.state = 0
        self.rope = []
        self.hook = []
        self.hook_to = 0
        
        self.looseharpoons = []
        
        self.fire_to = 0
    
    def Release(self):
        self.parent.control.fire = 0
        self.fire_to = 30
        self.parent.space.remove(self.harpconst_slidejoint)
        self.hook = []
        self.state = 0
    
    def TransfertoLoose(self):
        self.hook[1].collision_type = 2
        self.looseharpoons.append(LooseHarpoon(self,self.hook,self.parent.heading))
        self.hook[1].harpoonparent = self.looseharpoons[-1]
        self.hook = []
        self.state = 0
        self.hook_to = 0
    
    def Update(self):
        
        # Update loose harpoons
        for harpoon in self.looseharpoons:
            harpoon.Update()
        for harpoon in self.looseharpoons:
            if harpoon.to == 0:
                self.looseharpoons.remove(harpoon)
        
        # Update main harpoon
        if self.state == 1 and self.hook_to == 0: # out of rope, transfer to loose hook list
            self.TransfertoLoose()
        else:
            self.hook_to -= 1
        
        # look for fire new one
        if self.parent.control.fire == 1 and self.parent.alive == True and self.fire_to == 0 and self.state == 0:
            self.parent.control.fire = 0
            self.fire_to = 30
            body = pymunk.Body(2, 100)
            if self.parent.heading == 'right':
                body.position = (self.parent.body.position[0]+30,self.parent.body.position[1])
                body.apply_impulse((1000.0,0.0))
                body.angle = 0.0
            else:
                body.position = (self.parent.body.position[0]-30,self.parent.body.position[1])
                body.apply_impulse((-1000.0,0.0))
                body.angle = pi
            body.space = self.parent.space
            body.harpoonparent = self
            shape = pymunk.Circle(body, 5, (0,0))
            shape.collision_type = 1
            shape.friction = 0.5
            self.parent.space.add(body, shape)
            self.hook = [body,shape]
            self.hook_to = 10
            self.state = 1
            resources.soundfx['swish'].play()
        
        # look for release existing one
        if self.parent.control.fire == 1 and self.fire_to == 0 and self.state == 2:
            self.Release()
        
        # Update fire timeout
        if self.fire_to > 0:
            self.parent.control.fire = 0
            self.fire_to -= 1
    
    def Draw(self, screen):
        if self.state > 0:
            if self.state == 1:
                ang_ind = int(round((180*self.hook[0].angle/pi+180)/10.0)) % 35
                sprite_data = resources.harpoon_spritedata[ang_ind]
                x = int(self.hook[0].position[0])
                y = int(-self.hook[0].position[1])
                (imw,imh) = (sprite_data.get_width(),sprite_data.get_height())
                screen.blit(sprite_data, (x-(imw/2)-self.parent.h_camera.x+self.parent.h_camera.w_view/2,y-(imh/2)-self.parent.h_camera.y+self.parent.h_camera.h_view/2))
                x = x-self.parent.h_camera.x+self.parent.h_camera.w_view/2
                y = y-self.parent.h_camera.y+self.parent.h_camera.h_view/2
            elif self.state == 2:
                x3 = self.hook_end_data[0][0]
                y3 = self.hook_end_data[0][1]
                angle3 = self.hook_end_data[1].angle
                x4 = x3*cos(angle3) - y3*sin(angle3) + self.hook_end_data[1].position[0]
                y4 = x3*sin(angle3) + y3*cos(angle3) + self.hook_end_data[1].position[1]
                ang_ind = int(round((180*(self.hook_end_data[1].angle+self.hook_end_data[2])/pi+180)/10.0)) % 35
                sprite_data = resources.harpoon_spritedata[ang_ind]
                (imw,imh) = (sprite_data.get_width(),sprite_data.get_height())
                screen.blit(sprite_data, (x4-(imw/2)-self.parent.h_camera.x+self.parent.h_camera.w_view/2,-y4-(imh/2)-self.parent.h_camera.y+self.parent.h_camera.h_view/2))
                x = x4-self.parent.h_camera.x+self.parent.h_camera.w_view/2
                y = -y4-self.parent.h_camera.y+self.parent.h_camera.h_view/2
            x2 = self.parent.body.position[0]-self.parent.h_camera.x+self.parent.h_camera.w_view/2
            y2 = -self.parent.body.position[1]-self.parent.h_camera.y+self.parent.h_camera.h_view/2
            pygame.draw.line(screen, (255,255,255), (x,y), (x2,y2), 1)
                
        for harpoon in self.looseharpoons:
            harpoon.Draw(screen)

class Submarine(object):
    def __init__(self):
        pass
    
    def set_handles(self,handles):
        (self.h_camera, self.h_tiledlayers) = handles
    
    def reset(self,pos):
        
        self.control = KeyControl(resources.controlmap)
        
        self.heading = 'right'
        self.gaittype = 'float'
        self.gait = 0
        self.gait_to = 5
        self.bubblegait_to = 0
        
        self.harpoon = Harpoons(self)
        
        self.health = 10
        self.alive = True
        self.death_to = 60
        
        self.thought_queue = []
        self.thought_to = 0
        self.thoughtlen = 0
        
        # Add submarine to space
        mass = 10
        #vs_body = [(-24,-16),(-24,0),(-8,16),(8,16),(24,0),(24,-16)]
        vs_body = [(-18,-16),(-18,0),(-8,16),(8,16),(18,0),(18,-16)]
        moment = pymunk.moment_for_poly(mass, vs_body)
        self.body = pymunk.Body(mass, moment)
        self.shape = pymunk.Poly(self.body, vs_body)
        self.shape.friction = 0.5
        self.shape.collision_type = 3
        self.body.position = pos
        self.body.angle = 0
        self.space.add(self.body, self.shape)
        
        self.hudflash_to = 0
    
    def SetThought(self,thought,to):
        self.current_thought = thought
        self.thought_queue = [i for i in xrange(len(resources.thoughtsurfs[thought]))]
        self.thoughtlen = to
        self.thought_to = to
    
    def Kill(self):
        
        self.alive = False
        
        self.space.remove(self.body, self.shape)
        x = self.body.position[0]
        y = self.body.position[1]
        vx = self.body.velocity[0]
        vy = self.body.velocity[1]
        mass = 5
        vs_body1 = [(-12,-16),(-12,0),(12,16),(12,-16)]
        vs_body2 = [(12,-16),(12,0),(-12,16),(-12,-16)]
        
        moment = pymunk.moment_for_poly(mass, vs_body1)
        self.body = pymunk.Body(mass, moment)
        self.shape = pymunk.Poly(self.body, vs_body1)
        self.shape.friction = 0.5
        self.shape.collision_type = 0
        self.body.position = (x-12,y)
        self.body.velocity = (vx,vy)
        self.body.angle = 0
        self.body.apply_impulse((-100.0,0.0))
        self.space.add(self.body, self.shape)
        
        moment = pymunk.moment_for_poly(mass, vs_body2)
        self.body2 = pymunk.Body(mass, moment)
        self.shape2 = pymunk.Poly(self.body2, vs_body2)
        self.shape2.friction = 0.5
        self.shape2.collision_type = 0
        self.body2.position = (x+12,y)
        self.body2.velocity = (vx,vy)
        self.body2.angle = 0
        self.body2.apply_impulse((100.0,0.0))
        self.space.add(self.body2, self.shape2)
        
        for i in xrange(10):
            self.h_tiledlayers.bubbles.AddBubble([x-32+random.randint(0,64),-y-32+random.randint(0,64)])
        
        if self.harpoon.state == 2:
            self.harpoon.Release()
        
        self.gait = 0
        
        self.thought_queue = [0]
        self.current_thought = 'arrggh'
        self.thoughtlen = 45
        self.thought_to = 30
        
        resources.soundfx['subbreak'].play()
    
    def Update(self):
        
        if self.alive == True:
            
            # set animation stuff
            vx = self.control.r-self.control.l
            vy = self.control.u-self.control.d
            if abs(vx) > 0 or abs(vy) > 0:
                if self.harpoon.state == 2 or self.harpoon.fire_to > 0:
                    self.gaittype = "move_harp"
                else:
                    self.gaittype = "move"
                if self.bubblegait_to == 0:
                    self.bubblegait_to = 5
                    if self.heading == 'right':
                        self.h_tiledlayers.bubbles.AddBubble([self.body.position[0]-30,-self.body.position[1]],global_to=100)
                    else:
                        self.h_tiledlayers.bubbles.AddBubble([self.body.position[0]+16,-self.body.position[1]],global_to=100)
                else:
                    self.bubblegait_to -= 1
            else:
                if self.harpoon.state == 2 or self.harpoon.fire_to > 0:
                    self.gaittype = "float_harp"
                else:
                    self.gaittype = "float"
            
            # Set heading and gait info
            if vx > 0:
                self.heading = 'right'
            elif vx < 0:
                self.heading = 'left'
            
            # Player animation
            if (self.gaittype == 'move' or self.gaittype == 'move_harp') and self.gait_to == 0:
                self.gait_to = 3
                self.gait = self.gait + 1
                if self.gait > 3:
                    self.gait = 0
            elif self.gaittype == 'float' or self.gaittype == 'float_harp':
                self.gait = 0
                self.gait_to = 0
            self.gait_to = max(0,self.gait_to-1)
            
            # Apply impulses to player based on control inputs
            if self.h_tiledlayers.exiting == False:
                control_gain_x = 200
                control_gain_y = 200
                if self.control.l == 1:
                    self.body.apply_impulse((-control_gain_x,0.0))
                elif self.control.r == 1:
                    self.body.apply_impulse((control_gain_x,0.0))
                if self.control.u == 1:
                    self.body.apply_impulse((0.0,control_gain_y))
                elif self.control.d == 1:
                    self.body.apply_impulse((0.0,-control_gain_y))
            else:
                self.gaittype = 'float'
                self.gait = 0
                self.gait_to = 0
            
            # Apply buoyancy and drag
            gain_x = 1.0
            gain_y = 1.0
            drag = (-gain_x*self.body.velocity[0],-gain_y*self.body.velocity[1])
            self.body.apply_impulse(drag)
            self.body.apply_impulse((0.0,150.0)) # buoyancy
            
            gain_ang1 = 100.0
            gain_ang2 = 500.0
            righting = gain_ang1*self.body.angular_velocity + gain_ang2*self.body.angle
            self.body.apply_impulse((0.0,righting),r=(-10, 0))
            self.body.apply_impulse((0.0,-righting),r=(10, 0))
            
            tsize = self.h_tiledlayers.tilesize
            self.init_tile = self.h_tiledlayers.map_size[0]*(-int(self.body.position[1])/tsize)+(int(self.body.position[0])/tsize)
            
            if self.health <= 0:
                self.Kill()
            
        else: # dead
        
            # Apply buoyancy and drag
            gain_x = 0.3
            gain_y = 0.3
            drag = (-gain_x*self.body.velocity[0],-gain_y*self.body.velocity[1])
            self.body.apply_impulse(drag)
            self.body.apply_impulse((0.0,50.0)) # buoyancy
            drag2 = (-gain_x*self.body2.velocity[0],-gain_y*self.body2.velocity[1])
            self.body2.apply_impulse(drag2)
            self.body2.apply_impulse((0.0,50.0)) # buoyancy
            
            if self.death_to > 0:
                self.death_to -= 1
            
        # Update harpoon    
        self.harpoon.Update()
        
        if self.thought_to > 0:
            self.thought_to -= 1
        else:
            if len(self.thought_queue) > 0:
                self.thought_queue.pop()
                self.thought_to = self.thoughtlen
        
        if self.hudflash_to > 0:
            self.hudflash_to -= 1
    
    def PostUpdate(self):
        
        # Check if need to inform tilemap object layer of updates
        tsize = self.h_tiledlayers.tilesize
        final_tile = self.h_tiledlayers.map_size[0]*(-int(self.body.position[1])/tsize)+(int(self.body.position[0])/tsize)
        if not self.init_tile == final_tile:
            self.h_tiledlayers.UpdateObj(self.init_tile,final_tile,0)
    
    def Draw(self, screen):
        if self.alive == True:
            ang_ind = int(round((180*self.body.angle/pi+180)/10.0)) % 35
            sprite_data = resources.sub_spritedata[self.heading][resources.sub_spriteseq[self.gaittype][self.gait]][ang_ind]
            x = int(self.body.position[0])
            y = int(-self.body.position[1])
            (imw,imh) = (sprite_data.get_width(),sprite_data.get_height())
            screen.blit(sprite_data, (x-(imw/2)-self.h_camera.x+self.h_camera.w_view/2,y-(imh/2)-self.h_camera.y+self.h_camera.h_view/2))
        else:
            ang_ind1 = int(round((180*self.body.angle/pi+180)/10.0)) % 35
            sprite_data1 = resources.sub_spritedata[self.heading][resources.sub_spriteseq["dead"][0]][ang_ind1]
            x1 = int(self.body.position[0])
            y1 = int(-self.body.position[1])
            (imw1,imh1) = (sprite_data1.get_width(),sprite_data1.get_height())
            screen.blit(sprite_data1, (x1-(imw1/2)-self.h_camera.x+self.h_camera.w_view/2,y1-(imh1/2)-self.h_camera.y+self.h_camera.h_view/2))
            ang_ind2 = int(round((180*self.body2.angle/pi+180)/10.0)) % 35
            sprite_data2 = resources.sub_spritedata[self.heading][resources.sub_spriteseq["dead"][1]][ang_ind2]
            x2 = int(self.body2.position[0])
            y2 = int(-self.body2.position[1])
            (imw2,imh2) = (sprite_data2.get_width(),sprite_data2.get_height())
            screen.blit(sprite_data2, (x2-(imw2/2)-self.h_camera.x+self.h_camera.w_view/2,y2-(imh2/2)-self.h_camera.y+self.h_camera.h_view/2))
    
    def RenderHUD(self,screen):
        if (self.hudflash_to/2) % 2 == 0:
            border_c = (225,201,151)
            inner_c = (186,143,54)
        else:
            border_c = (255,0,0)
            inner_c = (186,143,54)
        #border_c = (200,200,0)
        #inner_c = (128,128,0)
        screen.blit(resources.hudtext_spritedata,(518,8))
        pygame.draw.rect(screen,border_c,((524,24),(103,8)),2)
        barlen = 10*self.health
        if barlen > 0:
            pygame.draw.rect(screen,inner_c,((526,26),(barlen,5)),0)
    
    def RenderThought(self, screen):
        if len(self.thought_queue) > 0:
            td1 = self.thought_to-self.thoughtlen+15
            if td1 > 0:
                alpha = int(255*(1.0 - float(td1)/15.0))
            elif self.thought_to <= 15:
                alpha = int(255*(self.thought_to/15.0))
            else:
                alpha = 255
            surf_thought = resources.thoughtsurfs[self.current_thought][self.thought_queue[-1]]
            surf_thought_bg = resources.thoughtsurfs_bg[self.current_thought][self.thought_queue[-1]]
            (imw,imh) = (surf_thought_bg.get_width(),surf_thought_bg.get_height())
            x = int(self.body.position[0])
            y = int(-self.body.position[1])-16-imh
            surf_thought_bg.set_alpha(alpha/2)
            screen.blit(surf_thought_bg, (x-(imw/2)-self.h_camera.x+self.h_camera.w_view/2,y-(imh/2)-self.h_camera.y+self.h_camera.h_view/2))
            (imw2,imh2) = (surf_thought.get_width(),surf_thought.get_height())
            surf_thought.set_alpha(alpha)
            screen.blit(surf_thought, (x-(imw2/2)-self.h_camera.x+self.h_camera.w_view/2,y-(imh2/2)-self.h_camera.y+self.h_camera.h_view/2))
    

