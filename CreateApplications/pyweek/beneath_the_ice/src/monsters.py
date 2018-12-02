#!/usr/bin/python

"""
monsters.py - monster classes
"""

import os
import pygame
from pygame.locals import *
from gamedirector import *
from math import *

import random

import pymunk
from pymunk import Vec2d

import resources

def dart_hit_func(space, arbiter):
    a,b = arbiter.shapes
    position = arbiter.contacts[0].position
    other_body = a.body
    b.collision_type = 0
    b.group = 1
    dart_body = b.body
    if dart_body.dart_ref.state == 1:
        dart_body.dart_ref.state = 2
        dart_body.dart_ref.finish_pos = [position[0],position[1]]

def dart_hit_player_func(space, arbiter):
    a,b = arbiter.shapes
    position = arbiter.contacts[0].position
    b.collision_type = 0
    b.group = 1
    other_body = a.body
    dart_body = b.body
    if dart_body.dart_ref.state == 1:
        dart_body.dart_ref.finish_pos = [position[0],position[1]]
        dart_body.dart_ref.state = 2
        dart_body.dart_ref.h_player.hudflash_to = 20
        dart_body.dart_ref.h_player.health -= 10

def shark_bite_player_func(space, arbiter):
    a,b = arbiter.shapes
    position = arbiter.contacts[0].position
    #b.group = 1
    other_body = a.body
    shark_body = b.body
    if shark_body.monster_ref.bite_to == 0:
        # hurt player
        shark_body.monster_ref.bite_to = 30
        shark_body.monster_ref.h_player.health -= 2
        shark_body.monster_ref.h_player.hudflash_to = 20
        resources.soundfx['bodythud'].play()

def shark_bite_thing_func(space, arbiter):
    a,b = arbiter.shapes
    position = arbiter.contacts[0].position
    #b.group = 1
    other_body = a.body
    shark_body = b.body
    if shark_body.monster_ref.bite_to == 0:
        if hasattr(other_body, 'monster_ref'):
            if other_body.monster_ref.is_squid == True:
                shark_body.monster_ref.bite_to = 30

class Dart(object):
    def __init__(self,pos,h_tiledlayer,h_player,type):
        self.h_tiledlayer = h_tiledlayer
        self.h_player = h_player
        self.body = pymunk.Body(1, 100)
        if type == 0:
            self.body.position = (pos[0]+8,-(pos[1]+8))
            self.body.apply_impulse((0.0,1200.0))
        elif type == 1:
            self.body.position = (pos[0]+8,-(pos[1]+8))
            self.body.apply_impulse((0.0,-1200.0))
        elif type == 2:
            self.body.position = (pos[0],-(pos[1]))
            px = self.h_player.body.position[0]
            py = self.h_player.body.position[1]
            sx = self.body.position[0]
            sy = self.body.position[1]
            dist2player = sqrt(pow(px-sx,2)+pow(py-sy,2))
            if not dist2player == 0:
                unitx = (px-sx)/dist2player
                unity = (py-sy)/dist2player
                self.body.apply_impulse((1200*unitx,1200.0*unity))
        self.body.angle = 0.0
        self.body.space = self.h_tiledlayer.space
        self.body.dart_ref = self
        self.shape = pymunk.Circle(self.body, 5, (0,0))
        self.shape.collision_type = 4
        self.shape.friction = 0.5
        self.h_tiledlayer.space.add(self.body, self.shape)
        self.state = 1
        self.to = 5
        self.finish_pos = [0,0]
        
        self.init_pos = [pos[0]+8,-(pos[1]+8)]
    
    def Update(self):
        if self.state == 2:
            #print self.init_pos
            self.to -= 1
            if self.to == 0:
                self.h_tiledlayer.space.remove(self.body, self.shape)
                self.state = 3
        else:
            self.finish_pos = [self.body.position[0],self.body.position[1]]
    """
    def Render(self,screen):
        tilecoords = resources.tiles_coords[resources.monster_spriteseq['dart'][0]]
        screen.blit(resources.tiles, (self.body.position[0]-(16/2)-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2, -self.body.position[1]-(16/2)-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2), area=tilecoords)
    """
    
    def Render(self,screen):
        if self.state == 1:
            x1 = self.body.position[0]-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2
            y1 = -self.body.position[1]-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2
        elif self.state == 2:
            x1 = self.finish_pos[0]-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2
            y1 = -self.finish_pos[1]-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2
            radius = int(3*(5-self.to))
            if radius > 2:
                pygame.draw.circle(screen, (255,255,0), (int(x1),int(y1)), radius, 2)
        x2 = self.init_pos[0]-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2
        y2 = -self.init_pos[1]-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2
        pygame.draw.line(screen, (255,0,0), (x1,y1), (x2,y2), 2)

class DartShooter(object):
    def __init__(self,pos,h_tiledlayer,h_player,type):
        self.h_tiledlayer = h_tiledlayer
        self.h_player = h_player
        self.type = type
        self.pos = pos[:]
        self.fire_to = 0
        self.ani_to = 0
        self.darts = []
        self.frame = 0
        self.finished = False
        
        self.is_squid = False
    
    def Update(self):
        
        # check for player proximity
        px = self.h_player.body.position[0]
        py = -self.h_player.body.position[1]
        if self.fire_to == 0 and fabs(px-self.pos[0]) < 10:
            if self.type == 0 and (self.pos[1]-py) > 0 and (self.pos[1]-py) < 256: # potshot
                self.ani_to = 5
                self.fire_to = 20
                self.darts.append(Dart(self.pos,self.h_tiledlayer,self.h_player,self.type))
                resources.soundfx['laser'].play()
            elif self.type == 1 and (self.pos[1]-py) < 0 and (self.pos[1]-py) > -256: # potshot
                self.ani_to = 5
                self.fire_to = 20
                self.darts.append(Dart(self.pos,self.h_tiledlayer,self.h_player,self.type))
                resources.soundfx['laser'].play()
            
        # Update all darts fired
        for d in self.darts:
            d.Update()
        for d in self.darts:
            if d.state == 3:
                self.darts.remove(d)
        
        # animation frame stuff
        if self.fire_to > 0:
            self.fire_to -= 1
            if self.ani_to > 0:
                self.frame = 1
                self.ani_to -= 1
            else:
                self.frame = 0
        else:
            self.frame = 0
    
    def Render(self,screen):
        if self.type == 0:
            tilecoords1 = resources.tiles_coords[resources.monster_spriteseq['dartshooter'][0]]
            tilecoords2 = resources.tiles_coords[resources.monster_spriteseq['dartshooter'][0]-16]
            screen.blit(resources.tiles, (self.pos[0]-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2, self.pos[1]-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2), area=tilecoords1)
            screen.blit(resources.tiles, (self.pos[0]-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2, self.pos[1]-16-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2), area=tilecoords2)
        elif self.type == 1:
            tilecoords1 = resources.tiles_coords[resources.monster_spriteseq['dartshooter'][1]]
            tilecoords2 = resources.tiles_coords[resources.monster_spriteseq['dartshooter'][1]+16]
            screen.blit(resources.tiles, (self.pos[0]-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2, self.pos[1]-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2), area=tilecoords1)
            screen.blit(resources.tiles, (self.pos[0]-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2, self.pos[1]+16-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2), area=tilecoords2)
        for d in self.darts:
            d.Render(screen)

class Squid(object):
    def __init__(self,pos,h_tiledlayer,h_player):
        
        self.h_tiledlayer = h_tiledlayer
        self.h_player = h_player
        
        self.addtospace(pos,10)
        
        self.targety = -pos[1]
        
        self.frametype = 'swim'
        self.frame = 0
        self.frame_to = 0
        self.patrol_state = 0
        self.patrol_to = 0
        
        self.propel_to = 0
        
        self.alive = True
        self.death_to = 60
        self.finished = False
        
        self.is_squid = True
    
    def addtospace(self,pos,mass):
        
        vs_body = [(-18,-9),(-18,9),(18,9),(18,-9)]
        moment = pymunk.moment_for_poly(mass, vs_body)
        self.body = pymunk.Body(mass, moment)
        self.shape = pymunk.Poly(self.body, vs_body)
        self.shape.friction = 0.5
        self.shape.collision_type = 8
        self.body.position = (pos[0],-pos[1])
        self.body.angle = 0
        self.body.monster_ref = self
        self.h_tiledlayer.space.add(self.body, self.shape)
    
    def Kill(self):
        
        self.alive = False
        self.frametype = 'dead'
        self.frame = 0
        self.frame_to = 0
        
        for i in xrange(5):
            self.h_tiledlayer.bubbles.AddBubble([self.body.position[0]-24+random.randint(0,48),-self.body.position[1]-24+random.randint(0,48)])
    
    def Update(self):
        if self.alive == True:
            
            # behaviour
            if self.patrol_to == 0:
                self.patrol_state = (self.patrol_state+1) % 2
                self.patrol_to = 180
            else:
                self.patrol_to -= 1
            
            control_gain_x = 30
            if self.patrol_state == 0:
                self.heading = 'left'
                self.body.apply_impulse((-control_gain_x,0.0))
            else:
                self.heading = 'right'
                self.body.apply_impulse((control_gain_x,0.0))
            
            if self.body.position[1] < self.targety and self.propel_to == 0:
                self.propel_to = 10
                self.frame_to = 2
                self.frame = 0
                
            if self.propel_to > 0:
                self.propel_to -= 1
                control_gain_y = 300.0
                self.body.apply_impulse((0.0,control_gain_y))
            
            # animation
            if self.propel_to > 0:
                if self.frame_to == 0:
                    self.frame_to = 2
                    self.frame = (self.frame+1) % 6
                else:
                    self.frame_to -= 1
            else:
                self.frame = 5
            
            # physical effects
            
            # Apply buoyancy and drag
            gain_x = 1.0
            gain_y = 1.0
            drag = (-gain_x*self.body.velocity[0],-gain_y*self.body.velocity[1])
            self.body.apply_impulse(drag)
            self.body.apply_impulse((0.0,120.0)) # buoyancy
            
            gain_ang1 = 100.0
            gain_ang2 = 500.0
            righting = gain_ang1*self.body.angular_velocity + gain_ang2*self.body.angle
            self.body.apply_impulse((0.0,righting),r=(-10, 0))
            self.body.apply_impulse((0.0,-righting),r=(10, 0))
            
        else:
            
            self.frame = 6
            
            # Apply buoyancy and drag
            gain_x = 1.0
            gain_y = 1.0
            drag = (-gain_x*self.body.velocity[0],-gain_y*self.body.velocity[1])
            self.body.apply_impulse(drag)
            self.body.apply_impulse((0.0,75.0)) # buoyancy
            
            gain_ang1 = 100.0
            gain_ang2 = 500.0
            righting = gain_ang1*self.body.angular_velocity + gain_ang2*self.body.angle
            self.body.apply_impulse((0.0,righting),r=(-10, 0))
            self.body.apply_impulse((0.0,-righting),r=(10, 0))
            
            if self.death_to > 0:
                self.death_to -= 1
    
    def Render(self,screen):
        coords2 = resources.tiles_coords[resources.monster_spriteseq['squid'][self.frame]]
        coords = list(coords2)
        coords[2] = 32
        coords[3] = 32
        coords = tuple(coords)
        x = int(self.body.position[0])
        y = int(-self.body.position[1])
        screen.blit(resources.tiles, (x-(32/2)-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2,y-(32/2)-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2), area=coords)

class Shark(object):
    def __init__(self,pos,h_tiledlayer,h_player,type):
        
        self.h_tiledlayer = h_tiledlayer
        self.h_player = h_player
        
        self.type = type
        
        self.addtospace(pos,10)
        
        self.targety = -pos[1]
        
        self.heading = 'right'
        self.frametype = 'swim'
        self.frame = 0
        self.frame_to = 0
        
        self.patrol_state = 1
        self.patrol_to = 0
        
        self.bite_to = 0
        
        if self.type == 1:
            self.darts = []
            self.powered = False
        else:
            self.powered = True
        
        self.alive = True
        self.death_to = 60
        self.finished = False
        
        self.is_squid = False
    
    def addtospace(self,pos,mass):
        
        vs_body = [(-18,-9),(-18,9),(18,9),(18,-9)]
        moment = pymunk.moment_for_poly(mass, vs_body)
        self.body = pymunk.Body(mass, moment)
        self.shape = pymunk.Poly(self.body, vs_body)
        self.shape.friction = 0.5
        if self.type == 0:
            self.shape.collision_type = 5
        elif self.type == 1:
            self.shape.collision_type = 7
        self.body.position = (pos[0],-pos[1])
        self.body.angle = 0
        self.body.monster_ref = self
        self.h_tiledlayer.space.add(self.body, self.shape)
    
    def Kill(self):
        
        self.alive = False
        self.frametype = 'dead'
        self.frame = 0
        self.frame_to = 0
        
        self.shape.collision_type = 0
        
        for i in xrange(5):
            self.h_tiledlayer.bubbles.AddBubble([self.body.position[0]-24+random.randint(0,48),-self.body.position[1]-24+random.randint(0,48)])
    
    def Update(self):
        if self.alive == True:
            
            # behaviour
            sx = self.body.position[0]
            sy = self.body.position[1]
            
            if self.type == 0:
                closest_squid = 1000
                for m in self.h_tiledlayer.monsters:
                    if m.is_squid == True and m.alive == False:
                        px2 = m.body.position[0]
                        py2 = m.body.position[1]
                        dist2squid = sqrt(pow(px2-sx,2)+pow(py2-sy,2))
                        if dist2squid < 300 and dist2squid < closest_squid:
                            closest_squid = dist2squid
                            dist2player = closest_squid
                            px = px2
                            py = py2
                if closest_squid == 1000:
                    px = self.h_player.body.position[0]
                    py = self.h_player.body.position[1]
                    dist2player = sqrt(pow(px-sx,2)+pow(py-sy,2))
            else:
                px = self.h_player.body.position[0]
                py = self.h_player.body.position[1]
                dist2player = sqrt(pow(px-sx,2)+pow(py-sy,2))
            
            dx = 0
            dy = 0
            
            if ((self.type == 0 and dist2player < 300) or (self.type == 1 and dist2player < 600)) and self.powered == True: # swimming after player
                
                self.patrol_state = 0
                self.patrol_to = 0
                
                if (px-sx) > 0:
                    dx = 1
                    self.heading = 'right'
                elif (px-sx) < 0:
                    dx = -1
                    self.heading = 'left'
                if (py-sy) > 0:
                    dy = 1
                elif (py-sy) < 0:
                    dy = -1
                
                if self.type == 0:
                    control_gain_x = 100
                    control_gain_y = 100
                else:
                    control_gain_x = 80
                    control_gain_y = 80
                if dx == -1:
                    self.body.apply_impulse((-control_gain_x,0.0))
                elif dx == 1:
                    self.body.apply_impulse((control_gain_x,0.0))
                if dy == 1:
                    self.body.apply_impulse((0.0,control_gain_y))
                elif dy == -1:
                    self.body.apply_impulse((0.0,-control_gain_y))
                
                self.targety = self.body.position[1]
                
            elif self.powered == True: # on patrol
                
                if self.patrol_to == 0:
                    self.patrol_state = (self.patrol_state+1) % 2
                    self.patrol_to = 180
                else:
                    self.patrol_to -= 1
                
                control_gain_x = 30
                control_gain_y = 30
                if self.patrol_state == 0:
                    self.heading = 'left'
                    self.body.apply_impulse((-control_gain_x,0.0))
                else:
                    self.heading = 'right'
                    self.body.apply_impulse((control_gain_x,0.0))
                
                control_gain_y = 10.0*(self.targety-self.body.position[1])
                self.body.apply_impulse((0.0,control_gain_y))
            
            if self.type == 1 and self.powered == True: # additional roboshark behaviours
                if dist2player < 150 and self.bite_to == 0: # fire the laser!
                    if self.heading == 'left':
                        self.darts.append(Dart([self.body.position[0]-20,-self.body.position[1]],self.h_tiledlayer,self.h_player,2))
                    else:
                        self.darts.append(Dart([self.body.position[0]+20,-self.body.position[1]],self.h_tiledlayer,self.h_player,2))
                    self.bite_to = 15
                    resources.soundfx['laser'].play()
                
                # Update all darts fired
                for d in self.darts:
                    d.Update()
                    if self.heading == 'left':
                        d.init_pos = [self.body.position[0]-20,self.body.position[1]]
                    else:
                        d.init_pos = [self.body.position[0]+20,self.body.position[1]]
                for d in self.darts:
                    if d.state == 3:
                        self.darts.remove(d)
            
            # physical effects
            
            # Apply buoyancy and drag
            gain_x = 1.0
            gain_y = 1.0
            drag = (-gain_x*self.body.velocity[0],-gain_y*self.body.velocity[1])
            self.body.apply_impulse(drag)
            self.body.apply_impulse((0.0,140.0)) # buoyancy
            
            gain_ang1 = 100.0
            gain_ang2 = 500.0
            righting = gain_ang1*self.body.angular_velocity + gain_ang2*self.body.angle
            self.body.apply_impulse((0.0,righting),r=(-10, 0))
            self.body.apply_impulse((0.0,-righting),r=(10, 0))
            
            # animation
            
            
            if self.bite_to >= 25:
                self.frame_to = 0
                self.frame = 2
            else:
                if self.frame_to == 0:
                    self.frame_to = 5
                    self.frame = (self.frame+1) % 2
                else:
                    self.frame_to -= 1
                
            if self.bite_to > 0:
                self.bite_to -= 1
            
        else:
            
            self.frame = 3
            
            # Apply buoyancy and drag
            gain_x = 1.0
            gain_y = 1.0
            drag = (-gain_x*self.body.velocity[0],-gain_y*self.body.velocity[1])
            self.body.apply_impulse(drag)
            self.body.apply_impulse((0.0,75.0)) # buoyancy
            
            gain_ang1 = 100.0
            gain_ang2 = 500.0
            righting = gain_ang1*self.body.angular_velocity + gain_ang2*self.body.angle
            self.body.apply_impulse((0.0,righting),r=(-10, 0))
            self.body.apply_impulse((0.0,-righting),r=(10, 0))
            
            if self.death_to > 0:
                self.death_to -= 1
            """
            if self.death_to == 0:
                self.h_tiledlayer.space.remove(self.body, self.shape)
                self.finished = True
            """
    
    def Render(self,screen):
        ang_ind = int(round((180*self.body.angle/pi+180)/10.0)) % 35
        if self.type == 0:
            coords2 = resources.tiles_coords[resources.monster_spriteseq['shark'][self.heading][self.frame]]
        elif self.type == 1:
            coords2 = resources.tiles_coords[resources.monster_spriteseq['roboshark'][self.heading][self.frame]]
        coords = list(coords2)
        coords[2] = 48
        coords = tuple(coords)
        x = int(self.body.position[0])
        y = int(-self.body.position[1])
        screen.blit(resources.tiles, (x-(48/2)-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2,y-(16/2)-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2), area=coords)
        if self.type == 1:
            for d in self.darts:
                d.Render(screen)
    
        
