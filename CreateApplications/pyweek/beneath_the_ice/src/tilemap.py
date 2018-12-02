#!/usr/bin/python

"""
tilemap.py - tilemap classes
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
import monsters

class StaticAni(object):
    def __init__(self,x,y,sequence,startframe,to_val):
        self.x = x
        self.y = y
        self.sequence = sequence
        self.to_val = to_val
        #self.to = 0
        self.to = random.randint(0, self.to_val)
        self.frame = startframe
        
    def Update(self):
        if self.to == 0:
            self.to = self.to_val
            #self.to = random.randint(self.to_val-5, self.to_val+5)
            self.frame = (self.frame+1) % len(self.sequence)
        else:
            self.to -= 1

class Bubble(object):
    def __init__(self,pos,h_tiledlayers,global_to):
        self.h_tiledlayers = h_tiledlayers
        self.pos = pos[:]
        self.to_val = 10
        self.to = 0
        self.frame = random.randint(0,3)
        self.state = True
        self.global_to = global_to
    
    def Update(self):
        
        tsize = self.h_tiledlayers.tilesize
        current_tile = self.h_tiledlayers.map_size[0]*(int(self.pos[1]-8)/tsize)+(int(self.pos[0])/tsize)
        if self.h_tiledlayers.occlayer[current_tile] == 1:
            self.state = False
        else:
            self.pos[1] -= 1
        
        if self.to == 0:
            self.to = self.to_val
            self.frame = (self.frame+1) % 4
        else:
            self.to -= 1
        
        if self.global_to > 0:
            self.global_to -= 1
        else:
            self.state = False

class BubbleGen(object):
    def __init__(self,pos,period,parent):
        self.parent = parent
        self.pos = pos[:]
        self.period = period
        self.to = random.randint(0,self.period)
    
    def Update(self):
        if self.to == 0:
            self.to = random.randint(0,self.period)
            self.parent.AddBubble(self.pos)
        else:
            self.to -= 1

class Bubbles(object):
    def __init__(self,parent):
        self.parent = parent
        self.bubbles = []
        self.bubblegens = []
    
    def AddBubble(self,pos,global_to=255):
        self.bubbles.append(Bubble(pos,self.parent,global_to))
    
    def AddBubbleGen(self,pos,period):
        self.bubblegens.append(BubbleGen(pos,period,self)) 
    
    def Update(self):
        for b in self.bubbles:
            b.Update()
        for b in self.bubbles:
            if b.state == False:
                self.bubbles.remove(b)
        for b in self.bubblegens:
            b.Update()
        
    def RenderBubbles(self,screen):
        for b in self.bubbles:
            resources.bubbles_spritedata[b.frame].set_alpha(b.global_to)
            #tilecoords = resources.tiles_coords[resources.bubbles_spriteseq['normal'][b.frame]]
            #screen.blit(resources.tiles, (b.pos[0]-self.parent.h_camera.x+self.parent.h_camera.w_view/2, b.pos[1]-self.parent.h_camera.y+self.parent.h_camera.h_view/2), area=tilecoords)
            screen.blit(resources.bubbles_spritedata[b.frame], (b.pos[0]-self.parent.h_camera.x+self.parent.h_camera.w_view/2, b.pos[1]-self.parent.h_camera.y+self.parent.h_camera.h_view/2))

class FishSchool(object):
    def __init__(self,type,pos,h_tiledlayers):
        self.h_tiledlayers = h_tiledlayers
        self.type = type
        self.initpos = pos[:]
        self.pos = self.initpos[:]
        self.to_val = 10
        self.to = 0
        self.frame = 0
        self.count = 0
    
    def Update(self):
        period1 = 300.0
        period2 = 50.0
        if self.type == 0:
            self.pos[0] = self.initpos[0] + 50*sin(float(self.count)/period1) + 10*cos(float(self.count)/period2)
            self.pos[1] = self.initpos[1] + 10*cos(float(self.count)/period1) + 5*sin(float(self.count)/period2)
        elif self.type == 1:
            self.pos[0] -= 0.5
            self.pos[1] = self.initpos[1] + 10*cos(float(self.count)/period2)
            if self.pos[0] < 0:
                self.pos[0] = self.h_tiledlayers.tilesize*self.h_tiledlayers.map_size[0]
        self.count += 1
        
        if self.to == 0:
            self.to = random.randint(0,self.to_val)
            self.frame = (self.frame+1) % 4
        else:
            self.to -= 1

class FishSchools(object):
    def __init__(self,parent):
        self.parent = parent
        self.schools = []
    
    def AddSchool(self,type,pos):
        self.schools.append(FishSchool(type,pos,self.parent))
    
    def UpdateSchools(self):
        for s in self.schools:
            s.Update()
    
    def RenderFishSchools(self,screen):
        for s in self.schools:
            tilecoords1 = resources.tiles_coords[resources.fishschool_spriteseq['normal'][s.frame]]
            tilecoords2 = resources.tiles_coords[resources.fishschool_spriteseq['normal'][s.frame]+1]
            screen.blit(resources.tiles, (int(s.pos[0])-self.parent.h_camera.x+self.parent.h_camera.w_view/2, int(s.pos[1])-self.parent.h_camera.y+self.parent.h_camera.h_view/2), area=tilecoords1)
            screen.blit(resources.tiles, (int(s.pos[0])+self.parent.tilesize-self.parent.h_camera.x+self.parent.h_camera.w_view/2, int(s.pos[1])-self.parent.h_camera.y+self.parent.h_camera.h_view/2), area=tilecoords2)

def mine_contact_func(space, arbiter):
    a,b = arbiter.shapes
    position = arbiter.contacts[0].position
    b.collision_type = 0
    b.group = 1
    other_body = a.body
    mine_body = b.body
    if mine_body.item_ref.state == 0 and not b.collision_type == 6:
        mine_body.item_ref.state = 1
        mine_body.item_ref.explode_pos = [position[0],position[1]]
        mine_body.item_ref.explode_to = 10
        
        # check if its a harpoon
        if a.collision_type == 1:
            mine_body.item_ref.h_player.harpoon.TransfertoLoose()
        
        # explode
        explode_gain = 5.0
        explode_range = mine_body.item_ref.explode_range
        bb = pymunk.BB(position[0]-explode_range,position[1]-explode_range,position[0]+explode_range,position[1]+explode_range)
        bother_list = mine_body.item_ref.h_tiledlayer.space.bb_query(bb)
        for shape in bother_list:
            if shape.body == mine_body or shape.body.is_static == True:
                continue
            relx = position[0]-shape.body.position[0]
            rely = position[1]-shape.body.position[1]
            if fabs(relx) == 0:
                magx = 0
            else:
                magx = explode_gain*(relx/fabs(relx))*(explode_range-fabs(relx))
            if fabs(rely) == 0:
                magy = 0
            else:
                magy = explode_gain*(rely/fabs(rely))*(explode_range-fabs(rely))
            shape.body.apply_impulse(( -magx, -magy ))
            
            # break up blocks
            if hasattr(shape.body, 'block_ref'):
                b = shape.body.block_ref
                if b[0] < 2: # blow it up, turn into boulders
                    xc = b[2].position[0]
                    yc = b[2].position[1]
                    sizex = 50
                    sizey = 30
                    for i in xrange(5):
                        x = xc-sizex/2+float(random.randint(0,sizex))
                        y = yc-sizey/2+float(random.randint(0,sizey))
                        body = pymunk.Body(10, 100)
                        body.position = (x,y)
                        shape = pymunk.Circle(body, 8, (0,0))
                        shape.friction = 0.5
                        mine_body.item_ref.h_tiledlayer.space.add(body, shape)
                        if b[0] == 0:
                            buoy = 0.0
                        elif b[0] == 1:
                            buoy = 250.0
                        mine_body.item_ref.h_tiledlayer.boulders.append([x,-y,8,buoy,body,shape])
                    mine_body.item_ref.h_tiledlayer.space.remove(b[2],b[3])
                    mine_body.item_ref.h_tiledlayer.blocks.remove(b)
            
            if hasattr(shape, 'collision_type'):
                if shape.collision_type == 5: # hit shark
                    shape.body.monster_ref.Kill()
                elif shape.collision_type == 3: # hit player
                    mine_body.item_ref.h_player.health -= 10
                    mine_body.item_ref.h_player.hudflash_to = 20
        
        for i in xrange(10):
            mine_body.item_ref.h_tiledlayer.bubbles.AddBubble([position[0]-50+random.randint(0,100),-position[1]-50+random.randint(0,100)])
        
        mine_body.item_ref.h_tiledlayer.space.remove(mine_body.item_ref.slidejoint)
        mine_body.item_ref.h_tiledlayer.space.remove(mine_body.item_ref.body2,mine_body.item_ref.shape2)
        
        resources.soundfx['mineexplode'].play()

class Mine(object):
    def __init__(self,pos,h_tiledlayer,h_player):
        self.h_tiledlayer = h_tiledlayer
        self.h_player = h_player
        
        self.body1 = pymunk.Body(10, 100)
        self.body1.position = (pos[0],-pos[1])
        self.body1.angle = 0.0
        self.body1.space = self.h_tiledlayer.space
        self.body1.item_ref = self
        self.shape1 = pymunk.Circle(self.body1, 5, (0,0))
        self.shape1.collision_type = 0
        self.shape1.friction = 0.5
        self.h_tiledlayer.space.add(self.body1, self.shape1)
        
        self.body2 = pymunk.Body(10, 100)
        self.body2.position = (pos[0],-pos[1]+48)
        self.body2.angle = 0.0
        self.body2.space = self.h_tiledlayer.space
        self.body2.item_ref = self
        self.shape2 = pymunk.Circle(self.body2, 5, (0,0))
        self.shape2.collision_type = 6
        self.shape2.friction = 0.5
        self.h_tiledlayer.space.add(self.body2, self.shape2)
        
        self.state = 0
        self.explode_to = 0
        self.explode_range = 150.0
        
        self.slidejoint = pymunk.SlideJoint(self.body1, self.body2, (0.0,0.0), (0.0,0.0), 0.0,44.0)
        self.h_tiledlayer.space.add(self.slidejoint)
    
    def Update(self):
        
        gain_x = 1.0
        gain_y = 1.0
        
        drag1 = (-gain_x*self.body1.velocity[0],-gain_y*self.body1.velocity[1])
        self.body1.apply_impulse(drag1)
        self.body1.apply_impulse((0.0,50.0))
        
        if self.state == 0:
            drag2 = (-gain_x*self.body2.velocity[0],-gain_y*self.body2.velocity[1])
            self.body2.apply_impulse(drag2)
            self.body2.apply_impulse((0.0,200.0))
        
        if self.explode_to > 0:
            self.explode_to -= 1
        
    def Render(self,screen):
        tilecoords1 = resources.tiles_coords[resources.item_spriteseq['mine'][0]]
        x1 = self.body1.position[0]-(16/2)-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2
        y1 = -self.body1.position[1]-(16/2)-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2
        screen.blit(resources.tiles, (x1, y1), area=tilecoords1)
        if self.state == 0:
            tilecoords2 = resources.tiles_coords[resources.item_spriteseq['mine'][1]]
            x2 = self.body2.position[0]-(16/2)-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2
            y2 = -self.body2.position[1]-(16/2)-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2
            screen.blit(resources.tiles, (x2, y2), area=tilecoords2)
            pygame.draw.line(screen, (255,255,255), (x1+8,y1+8), (x2+8,y2+8), 1)
        else:
            if self.explode_to > 0:
                x = int(self.explode_pos[0]-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2)
                y = int(-self.explode_pos[1]-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2)
                radius = int((self.explode_range/10.0)*(10-self.explode_to))
                if radius > 2:
                    pygame.draw.circle(screen, (255,255,255), (x,y), radius, 2)

class Magnet(object):
    def __init__(self,pos,h_tiledlayer,h_player):
        self.h_tiledlayer = h_tiledlayer
        self.h_player = h_player
        
        self.body2 = pymunk.Body(8, 100)
        self.body2.position = (pos[0],-pos[1])
        self.body2.angle = 0.0
        self.body2.space = self.h_tiledlayer.space
        self.body2.item_ref = self
        self.shape1 = pymunk.Circle(self.body2, 8, (0,0))
        self.shape1.collision_type = 0
        self.shape1.friction = 0.5
        self.h_tiledlayer.space.add(self.body2, self.shape1)
        
        self.effect_range = 75.0
    
    def Update(self):
        
        gain_x = 1.0
        gain_y = 1.0
        
        drag1 = (-gain_x*self.body2.velocity[0],-gain_y*self.body2.velocity[1])
        self.body2.apply_impulse(drag1)
        self.body2.apply_impulse((0.0,50.0))
        
        # check for attraction
        attract_gain = 10.0
        bb = pymunk.BB(self.body2.position[0]-self.effect_range,self.body2.position[1]-self.effect_range,self.body2.position[0]+self.effect_range,self.body2.position[1]+self.effect_range)
        bother_list = self.h_tiledlayer.space.bb_query(bb)
        for shape in bother_list:
            if hasattr(shape.body,'item_ref'): # is a mine or other magnet
                if shape.body == shape.body.item_ref.body2:
                    range = sqrt(pow(self.body2.position[0]-shape.body.position[0],2)+pow(self.body2.position[1]-shape.body.position[1],2))
                    if range > 0 and range < self.effect_range:
                        attraction = attract_gain*(self.effect_range-range)
                        relx = self.body2.position[0]-shape.body.position[0]
                        rely = self.body2.position[1]-shape.body.position[1]
                        shape.body.apply_impulse(( attraction*(relx/range), attraction*(rely/range) ))
                        self.body2.apply_impulse(( -attraction*(relx/range), -attraction*(rely/range) ))
            if hasattr(shape.body,'monster_ref'): # is a roboshark
                if shape.body.monster_ref.is_squid == False:
                    if shape.body.monster_ref.type == 1:
                        range = sqrt(pow(self.body2.position[0]-shape.body.position[0],2)+pow(self.body2.position[1]-shape.body.position[1],2))
                        if range > 0 and range < self.effect_range:
                            attraction = attract_gain*(self.effect_range-range)
                            relx = self.body2.position[0]-shape.body.position[0]
                            rely = self.body2.position[1]-shape.body.position[1]
                            shape.body.apply_impulse(( attraction*(relx/range), attraction*(rely/range) ))
                            self.body2.apply_impulse(( -attraction*(relx/range), -attraction*(rely/range) ))
            """
            if shape.body == self.body1 or shape.body.is_static == True:
                continue
            """
        
    def Render(self,screen):
        tilecoords1 = resources.tiles_coords[resources.item_spriteseq['magnet'][0]]
        x1 = self.body2.position[0]-(16/2)-self.h_tiledlayer.h_camera.x+self.h_tiledlayer.h_camera.w_view/2
        y1 = -self.body2.position[1]-(16/2)-self.h_tiledlayer.h_camera.y+self.h_tiledlayer.h_camera.h_view/2
        screen.blit(resources.tiles, (x1, y1), area=tilecoords1)

class TiledLayers(object):
    
    def __init__(self):
        pass
    
    def set_handles(self,handles):
        (self.h_camera, self.h_player) = handles
    
    def PreRenderTexturedBlocks(self):
        angles = [float(i) for i in xrange(-180,170,10)]
        self.blocksprites = []
        for b in self.blocks:
            self.blocksprites.append([])
            if b[0] == 0:
                #edgecolour = (78,59,12)
                edgecolour = (128,0,128)
            elif b[0] == 1:
                edgecolour = (0,125,125)
            texdata = resources.block_spritedata[b[0]]
            xvals = []
            yvals = []
            nvert = (len(b)-3)/2
            for i in xrange(nvert):
                xvals.append(b[2*i+3])
                yvals.append(b[2*i+3+1])
            cx = int(sum(xvals)/float(nvert))
            cy = int(sum(yvals)/float(nvert))
            minx = int(floor(min(xvals)))
            miny = int(floor(min(yvals)))
            maxx = int(ceil(max(xvals)))
            maxy = int(ceil(max(yvals)))
            offx = cx-max(abs(minx-cx),abs(maxx-cx))
            offy = cy-max(abs(miny-cy),abs(maxy-cy))
            xvals = [i-offx for i in xvals]
            yvals = [i-offy for i in yvals]
            imw = 2*(cx - offx)
            imh = 2*(cy - offy)
            img = pygame.Surface((imw, imh))
            img.fill((255,255,255))
            img.set_colorkey((255,255,255))
            for i in xrange(imw/16 + 1):
                for j in xrange(imh/16 + 1):
                    img.blit(texdata,(i*16,j*16))
            pygame.draw.polygon(img, edgecolour, [(int(x),int(y)) for (x,y) in zip(xvals,yvals)], 4)
            img2 = pygame.Surface((imw, imh))
            img2.fill((255,0,255))
            img2.set_colorkey((255,255,255))
            pygame.draw.polygon(img2, (255,255,255), [(int(x),int(y)) for (x,y) in zip(xvals,yvals)], 0)
            img.blit(img2,(0,0))
            img.set_colorkey((255,0,255))
            for ang in angles:
                self.blocksprites[-1].append(pygame.transform.rotate(img,ang))
    
    def load_level(self, level_id):
        
        self.exiting = False
        
        self.level_id = level_id
        self.map_size = resources.initleveldata[level_id].map_size[:]
        self.tilesize = 16
        self.player_start_tile = resources.initleveldata[level_id].player_start_tile
        self.finish_tile = resources.initleveldata[level_id].finish_tile[:]
        self.tilelayer = resources.initleveldata[level_id].tilelayer[:]
        self.tilelayer_bg = resources.initleveldata[level_id].tilelayer_bg[:]
        self.tilelayer_fg = resources.initleveldata[level_id].tilelayer_fg[:]
        self.occlayer = resources.initleveldata[level_id].occlayer[:]
        self.effectslayer = resources.initleveldata[level_id].effectslayer[:]
        self.monsterlayer = resources.initleveldata[level_id].monsterlayer[:]
        self.itemlayer = resources.initleveldata[level_id].itemlayer[:]
        self.boulders = []
        for b in resources.initleveldata[level_id].boulders:
            self.boulders.append(list(b[:]))
        self.blocks = []
        for b in resources.initleveldata[level_id].blocks:
            self.blocks.append(list(b[:]))
        self.triggers = []
        for t in resources.initleveldata[level_id].triggers:
            self.triggers.append(list(t[:]))
        
        self.objectlayer = [[] for i in xrange(self.map_size[0]*self.map_size[1])]
        
        # send initial data to camera
        self.h_camera.xlim = self.map_size[0]*self.tilesize
        self.h_camera.ylim = self.map_size[1]*self.tilesize
        
        # Initialise player data and load into object layer
        playerx = self.tilesize*(self.player_start_tile%self.map_size[0])
        playery = self.tilesize*(self.player_start_tile/self.map_size[0])
        self.h_player.reset((playerx,-playery))
        self.InsertObj(self.player_start_tile,0)
        
        # check for level 1 dive
        if self.level_id == 'level_explore_001':
            self.h_player.body.apply_impulse((0.0,-2000.0))
        
        # render tiled layers
        self.bglayer_t = pygame.Surface((self.tilesize*self.map_size[0],self.tilesize*self.map_size[1]))
        self.bglayer_t.fill((255,0,255))
        self.bglayer_t.convert()
        self.bglayer_t.set_colorkey((255,0,255))
        self.bglayer_tfg = pygame.Surface((self.tilesize*self.map_size[0],self.tilesize*self.map_size[1]))
        self.bglayer_tfg.fill((255,0,255))
        self.bglayer_tfg.convert()
        self.bglayer_tfg.set_colorkey((255,0,255))
        for i in range(self.map_size[0]):
            for j in range(self.map_size[1]):
                coords = [i*self.tilesize, j*self.tilesize]
                tileval = self.tilelayer[self.map_size[0]*j+i]
                tilevalbg = self.tilelayer_bg[self.map_size[0]*j+i]
                tilevalfg = self.tilelayer_fg[self.map_size[0]*j+i]
                if tilevalbg >= 0:
                    tilecoords = resources.tiles_coords[tilevalbg]
                    self.bglayer_t.blit(resources.tiles, (coords[0],coords[1]), area=tilecoords)
                if tileval >= 0:
                    tilecoords = resources.tiles_coords[tileval]
                    self.bglayer_t.blit(resources.tiles, (coords[0],coords[1]), area=tilecoords)
                if tilevalfg >= 0:
                    tilecoords = resources.tiles_coords[tilevalfg]
                    self.bglayer_tfg.blit(resources.tiles, (coords[0],coords[1]), area=tilecoords)
        
        # enter tiled layer data into space as static bodies
        ts = self.tilesize
        
        static_body = pymunk.Body()
        ground = pymunk.Segment(static_body, (0.0,0.0), (self.map_size[0]*ts,0.0), 0.0)
        ground.friction = 0.5
        self.space.add(ground)
        static_body = pymunk.Body()
        ground = pymunk.Segment(static_body, (self.map_size[0]*ts,0.0), (self.map_size[0]*ts,-self.map_size[1]*ts), 0.0)
        ground.friction = 0.5
        self.space.add(ground)
        static_body = pymunk.Body()
        ground = pymunk.Segment(static_body, (self.map_size[0]*ts,-self.map_size[1]*ts), (0.0,-self.map_size[1]*ts), 0.0)
        ground.friction = 0.5
        self.space.add(ground)
        static_body = pymunk.Body()
        ground = pymunk.Segment(static_body, (0.0,-self.map_size[1]*ts), (0.0,0.0), 0.0)
        ground.friction = 0.5
        self.space.add(ground)
        
        rns = [-self.map_size[0],-1,1,self.map_size[0]]
        for i in xrange(len(self.occlayer)):
            if self.occlayer[i] == 1:
                ix = i%self.map_size[0]
                iy = i/self.map_size[0]
                for jrns in rns:
                    j = i+jrns
                    if j >= 0 and j < len(self.occlayer):
                        if self.occlayer[j] == 0:
                            if jrns == -self.map_size[0]:
                                lstart = (ts*ix,-ts*iy)
                                lend = (ts*(ix+1),-ts*iy)
                            elif jrns == -1:
                                lstart = (ts*ix,-ts*iy)
                                lend = (ts*ix,-ts*(iy+1))
                            elif jrns == 1:
                                lstart = (ts*(ix+1),-ts*iy)
                                lend = (ts*(ix+1),-ts*(iy+1))
                            elif jrns == self.map_size[0]:
                                lstart = (ts*ix,-ts*(iy+1))
                                lend = (ts*(ix+1),-ts*(iy+1))
                            static_body = pymunk.Body()
                            ground = pymunk.Segment(static_body, lstart, lend, 0.0)
                            ground.friction = 0.5
                            self.space.add(ground)
        
        # Initialise Bubble Effects
        self.bubbles = Bubbles(self)
        
        # Initialise Fish School Effects
        self.fishschools = FishSchools(self)
        
        # Read out and assign effects
        # 1: kelp
        # 2: bubble generator
        # 3: static fish school
        # 4: moving fish school
        self.static_ani = []
        for i in xrange(len(self.effectslayer)):
            if self.effectslayer[i] == 1:
                sequence = resources.static_spriteseq['kelp']
                x = self.tilesize*(i%self.map_size[0])
                y = self.tilesize*(i/self.map_size[0])
                self.static_ani.append(StaticAni(x,y,sequence,random.randint(0,len(sequence)-1),10))
            if self.effectslayer[i] == 2:
                x = self.tilesize*(i%self.map_size[0])
                y = self.tilesize*(i/self.map_size[0])
                self.bubbles.AddBubbleGen([x,y],120)
            if self.effectslayer[i] == 3:
                x = self.tilesize*(i%self.map_size[0])
                y = self.tilesize*(i/self.map_size[0])
                self.fishschools.AddSchool(0,[x,y])
            if self.effectslayer[i] == 4:
                x = self.tilesize*(i%self.map_size[0])
                y = self.tilesize*(i/self.map_size[0])
                self.fishschools.AddSchool(1,[x,y])
        
        # Read out and assign monsters
        # 1: laser (up)
        # 2: laser (down)
        # 3: squid
        # 4: shark
        # 5: roboshark
        self.monsters = []
        for i in xrange(len(self.monsterlayer)):
            if self.monsterlayer[i] == 1: # laser (up)
                x = self.tilesize*(i%self.map_size[0])
                y = self.tilesize*(i/self.map_size[0])
                self.monsters.append(monsters.DartShooter([x,y],self,self.h_player,0))
            if self.monsterlayer[i] == 2: # laser (down)
                x = self.tilesize*(i%self.map_size[0])
                y = self.tilesize*(i/self.map_size[0])
                self.monsters.append(monsters.DartShooter([x,y],self,self.h_player,1))
            if self.monsterlayer[i] == 3: # squid
                x = self.tilesize*(i%self.map_size[0])
                y = self.tilesize*(i/self.map_size[0])
                self.monsters.append(monsters.Squid([x,y],self,self.h_player))
            if self.monsterlayer[i] == 4: # shark
                x = self.tilesize*(i%self.map_size[0])
                y = self.tilesize*(i/self.map_size[0])
                self.monsters.append(monsters.Shark([x,y],self,self.h_player,0))
            if self.monsterlayer[i] == 5: # robo shark
                x = self.tilesize*(i%self.map_size[0])
                y = self.tilesize*(i/self.map_size[0])
                self.monsters.append(monsters.Shark([x,y],self,self.h_player,1))
        
        # Read out and assign item
        # 1: mine
        # 2: magnet
        self.items = []
        for i in xrange(len(self.itemlayer)):
            if self.itemlayer[i] == 1: # mine
                x = self.tilesize*(i%self.map_size[0])+8
                y = self.tilesize*(i/self.map_size[0])+8
                self.items.append(Mine([x,y],self,self.h_player))
            if self.itemlayer[i] == 2: # magnet
                x = self.tilesize*(i%self.map_size[0])+8
                y = self.tilesize*(i/self.map_size[0])+8
                self.items.append(Magnet([x,y],self,self.h_player))
        
        # Add boulders to space
        for b in self.boulders:
            body = pymunk.Body(10, 100)
            body.position = (b[0],-b[1])
            shape = pymunk.Circle(body, b[2], (0,0))
            shape.friction = 0.5
            self.space.add(body, shape)
            b.extend([body,shape])
            b[4].boulder_ref = b
        
        # Setup triggers
        for t in self.triggers:
            t.append(False)
        
        # pre-render block sprites from textures
        self.PreRenderTexturedBlocks()
        
        # Add blocks to space
        for i in xrange(len(self.blocks)):
            b = self.blocks[i]
            vs_body = []
            pos = [0,0]
            for i in xrange((len(b)-3)/2):
                x = b[2*i+3]
                y = -b[2*i+3+1]
                vs_body.append([x,y])
                pos[0] += x
                pos[1] += y
            pos = (pos[0]/((len(b)-3)/2), pos[1]/((len(b)-3)/2))
            for i in xrange(len(vs_body)):
                v = vs_body[i]
                vs_body[i] = (v[0]-pos[0],v[1]-pos[1])
            moment = pymunk.moment_for_poly(b[1], vs_body)
            body = pymunk.Body(b[1], moment)
            shape = pymunk.Poly(body, vs_body)
            shape.friction = 0.5
            ps = shape.get_vertices()
            shape.ang_offset = atan2(-(ps[1].x-ps[0].x),ps[1].y-ps[0].y)
            body.position = pos
            body.angle = 0.0
            self.space.add(body, shape)
            b.extend([body,shape])
        for i in xrange(len(self.blocks)):
            b = self.blocks[i]
            self.blocks[i] = [b[0],b[2],b[-2],b[-1],self.blocksprites[i]]
            self.blocks[i][2].block_ref = self.blocks[i]
        
    def UpdateTileLayer(self, tile, tileval):
        coords = [(tile%self.map_size[0])*self.tilesize, (tile/self.map_size[0])*self.tilesize]
        if tileval >= 0:
            tilecoords = resources.tiles_coords[tileval]
            self.bglayer_t.blit(resources.tiles, (coords[0],coords[1]), area=tilecoords)
    
    def UpdateEffects(self):
        for sa in self.static_ani:
            sa.Update()
        self.bubbles.Update()
        self.fishschools.UpdateSchools()
    
    def UpdateMonsters(self):
        for m in self.monsters:
            m.Update()
        """
        for m in self.monsters:
            if m.finished == True:
                self.monsters.remove(m)
        """
    
    def UpdateItems(self):
        for i in self.items:
            i.Update()
    
    def UpdateBoulders(self):
        for b in self.boulders:
            gain_x = 1.0
            gain_y = 1.0
            drag = (-gain_x*b[4].velocity[0],-gain_y*b[4].velocity[1])
            b[4].apply_impulse(drag)
            b[4].apply_impulse((0.0,b[3]))
    
    def UpdateTriggers(self):
        for t in self.triggers:
            if t[4] == False:
                xdiff = self.h_player.body.position[0]-t[0]
                ydiff = -self.h_player.body.position[1]-t[1]
                range = sqrt(pow(xdiff,2)+pow(ydiff,2))
                if range < t[2] and self.h_player.alive == True:
                    t[4] = True
                    self.h_player.SetThought(t[3],resources.thoughtto[t[3]])
                    if t[3] == 'lvlfinal_a':
                        self.monsters[0].powered = True
    
    def UpdateBlocks(self):
        for b in self.blocks:
            gain_x = 1.0
            gain_y = 1.0
            drag = (-gain_x*b[2].velocity[0],-gain_y*b[2].velocity[1])
            b[2].apply_impulse(drag)
            b[2].apply_impulse((0.0,b[1]))
            #gain_ang1 = 0.0001
            #righting = gain_ang1*b[2].moment*b[2].angular_velocity
            #b[2].apply_impulse((0.0,righting),r=(-10, 0))
            #b[2].apply_impulse((0.0,-righting),r=(10, 0))
    
    def RenderTileLayer(self, screen):
        screen.blit(self.bglayer_t, (0,0), area=(self.h_camera.x-self.h_camera.w_view/2, self.h_camera.y-self.h_camera.h_view/2, self.h_camera.w_view, self.h_camera.h_view))
    
    def RenderFGLayer(self, screen):
        screen.blit(self.bglayer_tfg, (0,0), area=(self.h_camera.x-self.h_camera.w_view/2, self.h_camera.y-self.h_camera.h_view/2, self.h_camera.w_view, self.h_camera.h_view))
    
    def RenderBackdrop(self, screen):
        screen.blit(resources.backdrop, (0,0), area=(self.h_camera.x/2-self.h_camera.w_view/4,0,640,480))
        #screen.fill((52,42,151))
    
    def RenderStaticAni(self,screen):
        for sa in self.static_ani:
            #tilecoords = resources.tiles_coords[resources.static_spriteseq['kelp'][sa.frame]]
            #screen.blit(resources.tiles, (sa.x-self.h_camera.x+self.h_camera.w_view/2, sa.y-self.h_camera.y+self.h_camera.h_view/2), area=tilecoords)
            tilecoords = resources.tiles_coords[resources.static_spriteseq['kelp'][sa.frame]]
            tilecoords = list(tilecoords)
            tilecoords[1] = tilecoords[1]-1
            tilecoords[3] = tilecoords[3]+1
            tilecoords = tuple(tilecoords)
            screen.blit(resources.tiles, (sa.x-self.h_camera.x+self.h_camera.w_view/2, sa.y-1-self.h_camera.y+self.h_camera.h_view/2), area=tilecoords)
    
    def RenderBubbles(self,screen):
        self.bubbles.RenderBubbles(screen)
    
    def RenderFishSchools(self,screen):
        self.fishschools.RenderFishSchools(screen)
    
    def RenderMonsters(self,screen):
        for m in self.monsters:
            m.Render(screen)
    
    def RenderItems(self,screen):
        for i in self.items:
            i.Render(screen)
    
    def RenderBoulders(self, screen):
        for b in self.boulders:
            body = b[4]
            ang_ind = int(round((180*body.angle/pi+180)/10.0)) % 35
            x = int(body.position[0])
            y = int(-body.position[1])
            if b[3] > 150.0:
                type = 1
            else:
                type = 0
            sprite_data = resources.boulder_spritedata[type][ang_ind]
            (imw,imh) = (sprite_data.get_width(),sprite_data.get_height())
            screen.blit(sprite_data, (x-(imw/2)-self.h_camera.x+self.h_camera.w_view/2, y-(imh/2)-self.h_camera.y+self.h_camera.h_view/2) )
    
    def RenderBlocks(self, screen):
        for b in self.blocks:
            bs = b[4]
            
            ps = b[3].get_vertices()
            #angle = atan2(-(ps[1].x-ps[0].x),ps[1].y-ps[0].y)-b[3].ang_offset
            angle = b[2].angle
            
            ang_ind = int(round((180*angle/pi+180)/10.0)) % 35
            x = int(b[2].position[0])
            y = int(-b[2].position[1])
            sprite_data = bs[ang_ind]
            (imw,imh) = (sprite_data.get_width(),sprite_data.get_height())
            screen.blit(sprite_data, (x-(imw/2)-self.h_camera.x+self.h_camera.w_view/2, y-(imh/2)-self.h_camera.y+self.h_camera.h_view/2) )
        """
        for b in self.blocks:
            ps = b[3].get_vertices()
            ps = [(p.x-self.h_camera.x+self.h_camera.w_view/2, -p.y-self.h_camera.y+self.h_camera.h_view/2) for p in ps]
            ps += [ps[0]]
            pygame.draw.lines(screen, (0,255,0), False, ps, 3)
        """
        
    def InsertObj(self,tileind,objid):
        self.objectlayer[tileind].append(objid)
        if objid == 0 and tileind == self.finish_tile[0]:
            self.exiting = True
            self.destination = self.finish_tile[1]
            if self.h_player.harpoon.state == 2:
                self.h_player.harpoon.Release()
    
    def RemoveObj(self,tileind,objid):
        if objid in self.objectlayer[tileind]:
            self.objectlayer[tileind].pop(self.objectlayer[tileind].index(objid))
    
    def UpdateObj(self,tileind_old,tileind_new,objid):
        self.RemoveObj(tileind_old,objid)
        self.InsertObj(tileind_new,objid)
    
    
