#!/usr/bin/python

"""
game.py - main in-game scene classes
"""

import os
import pygame
from pygame.locals import *
from gamedirector import *

import random
from math import *

import resources
from common import Camera, FadeInOut, MenuButton, MenuList

import pymunk
from pymunk import Vec2d

import tilemap
import submarine
import monsters

class ProgressData(object):
    def __init__(self):
        self.current_level = "level_"
    
    def LoadProgressData(self):
        f = open(self.savepath, "r");
        self.current_level = f.readline().split()[0]
        f.close()
    
    def SaveProgressData(self):
        f = open(self.savepath, "w");
        f.write('%s\n'%(self.current_level))
        f.close()
    
    def Reset(self):
        self.current_level = "level_"

class MainGame(GameScene):
    def __init__(self, director, window_size):
        super(MainGame, self).__init__(director)
        self.window_size = window_size
        
        # frame rate recording
        self.avgframerate = -1
        self.frsamples = 0
        
        # fade in/out
        self.fade = FadeInOut(15)
        
        # Music
        self.current_music = 'none'
        
        # Background
        self.background = pygame.Surface(window_size)
        self.background.fill((0,0,0))
        self.background.convert()
        
        # Initialise player data
        self.progress_data = ProgressData()
    
    def on_switchto(self, switchtoargs):
        
        lvlreset = switchtoargs[0]
        if not lvlreset:
            return
        
        level_id = switchtoargs[1]
        
        # Save progress
        self.progress_data.current_level = level_id
        self.progress_data.SaveProgressData()
        
        # Initialise objects
        self.camera = Camera(self.window_size)
        self.tiledlayers = tilemap.TiledLayers()
        self.submarine = submarine.Submarine()
        
        # set cross handles
        self.tiledlayers.set_handles((self.camera, self.submarine))
        self.submarine.set_handles((self.camera, self.tiledlayers))
        
        # Initialise physics space
        self.space = pymunk.Space()
        self.space.gravity = Vec2d(0.0, -450.0)
        
        # collision types:
        # 1: harpoon (on hook)
        # 2: harpoon (loose)
        # 3: player
        # 4: dart
        # 5: shark
        # 6: mine
        # 7: roboshark
        # 8: squid
        # 9: dead squid
        
        self.space.add_collision_handler(0, 1, post_solve=submarine.harpoon_hit_func) # harpoon generics
        self.space.add_collision_handler(0, 2, post_solve=submarine.looseharpoon_hit_func)
        self.space.add_collision_handler(9, 1, post_solve=submarine.harpoon_hit_func) # harpoon generics
        self.space.add_collision_handler(9, 2, post_solve=submarine.looseharpoon_hit_func)
        
        self.space.add_collision_handler(0, 4, post_solve=monsters.dart_hit_func) # darts
        self.space.add_collision_handler(9, 4, post_solve=monsters.dart_hit_func)
        self.space.add_collision_handler(3, 4, post_solve=monsters.dart_hit_player_func)
        
        self.space.add_collision_handler(3, 5, post_solve=monsters.shark_bite_player_func) # shark bite
        self.space.add_collision_handler(0, 5, post_solve=monsters.shark_bite_thing_func) # shark bite
        
        self.space.add_collision_handler(5, 1, post_solve=submarine.harpoon_hit_monster) # harpoon hit monster
        self.space.add_collision_handler(5, 2, post_solve=submarine.harpoon_hit_monster) # harpoon hit monster
        self.space.add_collision_handler(8, 1, post_solve=submarine.harpoon_hit_monster) # harpoon hit monster
        self.space.add_collision_handler(8, 2, post_solve=submarine.harpoon_hit_monster) # harpoon hit monster
        
        # mine contact
        self.space.add_collision_handler(0, 6, post_solve=tilemap.mine_contact_func)
        self.space.add_collision_handler(1, 6, post_solve=tilemap.mine_contact_func)
        self.space.add_collision_handler(2, 6, post_solve=tilemap.mine_contact_func)
        self.space.add_collision_handler(3, 6, post_solve=tilemap.mine_contact_func)
        self.space.add_collision_handler(4, 6, post_solve=tilemap.mine_contact_func)
        self.space.add_collision_handler(5, 6, post_solve=tilemap.mine_contact_func)
        self.space.add_collision_handler(7, 6, post_solve=tilemap.mine_contact_func)
        self.space.add_collision_handler(8, 6, post_solve=tilemap.mine_contact_func)
        self.space.add_collision_handler(9, 6, post_solve=tilemap.mine_contact_func)
        
        self.submarine.space = self.space
        self.tiledlayers.space = self.space
        
        # load level data
        self.tiledlayers.load_level(level_id)
        self.camera.UpdateCamera([int(self.submarine.body.position[0]),-int(self.submarine.body.position[1])])
        
        # Check music
        if not self.current_music == resources.initleveldata[level_id].music:
            self.current_music = resources.initleveldata[level_id].music
            pygame.mixer.music.stop()
            if not self.current_music == 'none':
                pygame.mixer.music.load(resources.musicpaths[self.current_music])
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
        
        # Fade in game
        self.background.fill((0,0,0))
        self.fade.FadeIn()
        
        #self.submarine.SetThought("sub_plastic",120)
    
    def on_update(self):
        
        # framerate tracking
        self.frsamples += 1
        if self.frsamples == 1:
            self.avgframerate = self.director.framerate
        else:
            self.avgframerate = self.avgframerate + (self.director.framerate - self.avgframerate)/(self.frsamples)
        
        # Update player motion
        self.submarine.Update()
        self.camera.UpdateCamera([int(self.submarine.body.position[0]),-int(self.submarine.body.position[1])])
        
        # Update Boulders
        self.tiledlayers.UpdateEffects()
        self.tiledlayers.UpdateBoulders()
        self.tiledlayers.UpdateBlocks()
        
        # Update all Monsters
        self.tiledlayers.UpdateMonsters()
        
        # Update All items
        self.tiledlayers.UpdateItems()
        
        # Update Triggers
        self.tiledlayers.UpdateTriggers()
        
        # Update space
        self.space.step(1.0/120)
        self.space.step(1.0/120)
        self.space.step(1.0/120)
        self.space.step(1.0/120)
        
        # Post update steps
        if self.submarine.alive == True:
            self.submarine.PostUpdate()
        
        # Control fade in/out, look for end game cues
        self.fade.Update()
        if self.tiledlayers.exiting and self.fade.direction == 'in':
            if not self.current_music == resources.initleveldata[self.tiledlayers.destination].music:
                musicfade = True
            else:
                musicfade = False
            self.fade.FadeOut(musicfade)
        if self.submarine.death_to == 0 and self.fade.direction == 'in':
            self.fade.FadeOut()
        if self.fade.finished_out:
            if self.submarine.death_to == 0:
                self.director.change_scene('maingame', [True,self.tiledlayers.level_id])
            else:
                if self.tiledlayers.level_id == 'level_boulderlift_003':
                    self.director.change_scene('cutscene1', resources.cutscene1_data)
                elif self.tiledlayers.level_id == 'level_sharkminetwo_005':
                    self.director.change_scene('cutscene2', resources.cutscene2_data)
                elif self.tiledlayers.level_id == 'level_lasertunnel_007':
                    self.director.change_scene('cutscene3', resources.cutscene3_data)
                elif self.tiledlayers.level_id == 'level_sharkmagnet_008':
                    self.director.change_scene('cutscene4', resources.cutscene4_data)
                else:
                    self.director.change_scene('maingame', [True,self.tiledlayers.destination])
        
    def on_event(self, events):
        for event in events:
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                #self.director.change_scene(None, [])
                self.draw(self.h_pausescene.background)
                self.director.change_scene('pausescene', [self.tiledlayers.level_id])
            if event.type == KEYDOWN or event.type == KEYUP:
                self.submarine.control.ProcessKeyEvent(event)
    
    def draw(self, screen):
        self.tiledlayers.RenderBackdrop(screen)
        self.tiledlayers.RenderTileLayer(screen)
        self.tiledlayers.RenderBlocks(screen)
        self.tiledlayers.RenderBoulders(screen)
        self.tiledlayers.RenderFishSchools(screen)
        self.tiledlayers.RenderItems(screen)
        self.tiledlayers.RenderMonsters(screen)
        self.submarine.harpoon.Draw(screen)
        self.submarine.Draw(screen)
        self.tiledlayers.RenderFGLayer(screen)
        self.tiledlayers.RenderStaticAni(screen)
        self.tiledlayers.RenderBubbles(screen)
        self.submarine.RenderHUD(screen)
        self.submarine.RenderThought(screen)
    
    def on_draw(self, screen):
        self.draw(screen)
        self.background.set_alpha(self.fade.alpha)
        screen.blit(self.background, (0, 0))

class PauseScreen(GameScene):
    def __init__(self, director, window_size):
        super(PauseScreen, self).__init__(director)
        self.window_size = window_size
        
        # Background
        self.background = pygame.Surface(window_size)
        self.background.fill((0,0,0))
        self.background.convert()
    
    def resume_game_now(self):
        self.director.change_scene('maingame', [False,-1])
    
    def reset_game_now(self):
        self.director.change_scene('maingame', [True,self.from_level])
    
    def quit_game_now(self):
        self.h_maingame.current_music = 'none'
        self.director.change_scene('titlescene', [])
        #self.director.change_scene('logocutscene', resources.logocutscene_data)
    
    def on_switchto(self, switchtoargs):
        
        self.from_level = switchtoargs[0]
        
        # Setup background
        backfade = pygame.Surface(self.background.get_size())
        backfade.fill((0,0,0))
        backfade.convert()
        backfade.set_alpha(128)
        self.background.blit(backfade, (0,0))
        
        # top-level menu buttons
        #self.pos_h = (self.window_size[0]/2)-((resources.pausescreen_surfs['bg'].get_width()+resources.pausescreen_surfs['help'].get_width()+40)/2)
        #self.pos_h2 = self.pos_h + resources.pausescreen_surfs['bg'].get_width() + 40
        #self.pos_v = (self.window_size[1]/2)-(resources.pausescreen_surfs['bg'].get_height()/2)
        #self.pos_v2 = (self.window_size[1]/2)-(resources.pausescreen_surfs['help'].get_height()/2)
        self.pos_v = 200
        self.button_resume = MenuButton((0,self.pos_v),resources.pause_spritedata['resume_on'],resources.pause_spritedata['resume_off'],self.resume_game_now)
        self.button_reset = MenuButton((0,self.pos_v+32),resources.pause_spritedata['reset_on'],resources.pause_spritedata['reset_off'],self.reset_game_now)
        self.button_quit = MenuButton((0,self.pos_v+64),resources.pause_spritedata['quit_on'],resources.pause_spritedata['quit_off'],self.quit_game_now)
        self.buttonlist = [self.button_resume,self.button_reset,self.button_quit]
        self.topmenus = MenuList(self.buttonlist,0,resources.controlmap)
        
        # reset menu
        self.topmenus.select_ind = 0
        
    def on_update(self):
        pass
    
    def on_event(self, events):
        for event in events:
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.director.change_scene('maingame', [False,-1])
            if event.type == KEYDOWN:
                self.topmenus.ProcessKeyEvent(event)
    
    def on_draw(self, screen):
        screen.blit(self.background, (0,0))
        self.topmenus.Draw(screen)

