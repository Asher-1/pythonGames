#!/usr/bin/python

"""
cutscenes.py - scene classes for cutscenes/story
"""

import os
import pygame
from pygame.locals import *
from gamedirector import *

import pymunk
from pymunk import Vec2d

import resources
from common import FadeInOut, MenuButton, MenuList, Camera
import tilemap
import submarine

class TitleScreen(GameScene):
    def __init__(self, director, window_size):
        super(TitleScreen, self).__init__(director)
        self.window_size = window_size
        
        # Background
        self.background = pygame.Surface(window_size)
        self.background.fill((0,0,0))
        self.background.convert()
    
    def start_game_now(self):
        self.start_game = True
    
    def continue_game_now(self):
        self.continue_game = True
    
    def on_switchto(self, switchtoargs):
        
        # Check music
        pygame.mixer.music.load(resources.musicpaths['pamgaea'])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        
        # top-level menu buttons
        pos_h1 = (self.window_size[0]/2)-(resources.titlescreen_surfs['continue_red'].get_width()/2)
        pos_h2 = (self.window_size[0]/2)-(resources.titlescreen_surfs['newgame_red'].get_width()/2)
        if os.path.isfile(self.savepath):
            self.button_continue = MenuButton((pos_h1,280),resources.titlescreen_surfs['continue_red'],resources.titlescreen_surfs['continue_gold'],self.continue_game_now)
            self.button_newgame = MenuButton((pos_h2,320),resources.titlescreen_surfs['newgame_red'],resources.titlescreen_surfs['newgame_gold'],self.start_game_now)
            self.buttonlist = [self.button_continue,self.button_newgame]
        else:
            self.button_newgame = MenuButton((pos_h2,280),resources.titlescreen_surfs['newgame_red'],resources.titlescreen_surfs['newgame_gold'],self.start_game_now)
            self.buttonlist = [self.button_newgame]
        self.topmenus = MenuList(self.buttonlist,0,resources.controlmap)
                
        # fade in/out
        self.fade = FadeInOut(30)
        
        # reset menu
        self.topmenus.select_ind = 0
        
        # control
        self.start_game = False
        self.continue_game = False
        
        # run "game"
        
        
        level_id = 'level_explore_001'
        
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
        
        self.submarine.space = self.space
        self.tiledlayers.space = self.space
        
        # load level data
        self.tiledlayers.load_level(level_id)
        #self.camera.UpdateCamera([int(self.submarine.body.position[0]),-int(self.submarine.body.position[1])])
        self.camera.UpdateCamera([int(16*self.tiledlayers.map_size[0]),int(16*self.tiledlayers.map_size[1])])
        
        
        
        # Fade in game
        self.fade.FadeIn()
        
    def on_update(self):
        
        
        
        # Update Boulders
        self.tiledlayers.UpdateEffects()
        self.tiledlayers.UpdateBoulders()
        self.tiledlayers.UpdateBlocks()
        
        
        
        # Control fade in/out, look for end game cues
        self.fade.Update()
        if self.fade.direction == 'in' and (self.start_game or self.continue_game):
            self.fade.FadeOut(True)
        if self.fade.finished_out and self.start_game:
            self.h_progress_data.Reset()
            #self.director.change_scene('introcutscene', resources.introcutscene_data)
            self.director.change_scene('maingame', [True,"level_explore_001"])
        elif self.fade.finished_out and self.continue_game: 
            self.h_progress_data.LoadProgressData()
            self.director.change_scene('maingame', [True,self.h_progress_data.current_level])
    
    def on_event(self, events):
        for event in events:
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.director.change_scene(None, [])
            if event.type == KEYDOWN:
                self.topmenus.ProcessKeyEvent(event)
    
    def on_draw(self, screen):
        
        self.tiledlayers.RenderBackdrop(screen)
        self.tiledlayers.RenderTileLayer(screen)
        self.tiledlayers.RenderFishSchools(screen)
        self.tiledlayers.RenderStaticAni(screen)
        self.tiledlayers.RenderBubbles(screen)
        
        screen.blit(resources.titlescreen_surfs['bg'], (183,170))
        
        self.topmenus.Draw(screen)
        self.background.set_alpha(self.fade.alpha)
        screen.blit(self.background, (0, 0))


class CutScene(GameScene):
    def __init__(self, director, window_size):
        super(CutScene, self).__init__(director)
        self.window_size = window_size
        
        # Background
        self.background = pygame.Surface(window_size)
        self.background.fill((0,0,0))
        self.background.convert()
        
        self.midground = pygame.Surface(window_size)
        self.midground.fill((0,0,0))
        self.midground.convert()
        
        self.fadebackground = pygame.Surface(window_size)
        self.fadebackground.fill((0,0,0))
        self.fadebackground.convert()
        
        self.fade = FadeInOut(30)
        self.fade_text = FadeInOut(15)
        
        self.go_next = False
        
    def on_switchto(self, switchtoargs):
        
        self.sequence = switchtoargs[0] # [ [bgid, [textid1, textid2, ...] ]
        self.musicid = switchtoargs[1]
        self.next_scene_type = switchtoargs[2]
        self.next_scene_switchtoargs = switchtoargs[3]
        
        self.step = 0
        self.textstep = -1
        
        self.ani_to = 0
        self.ani_frame1 = 0
        self.ani_frame2 = 0
        
        # Check music
        pygame.mixer.music.stop()
        if not self.musicid == 'none':
            pygame.mixer.music.load(resources.musicpaths[self.musicid])
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        
        self.fade.FadeIn()
        
    def on_update(self):
        
        # update animation
        if self.ani_to == 0:
            self.ani_frame1 = (self.ani_frame1+1) % 5
            self.ani_frame2 = (self.ani_frame2+1) % 2
            self.ani_to = 15
        else:
            self.ani_to -= 1
        
        # Check for return to game
        self.fade.Update()
        self.fade_text.Update()
        if self.fade.direction == 'in' and self.fade.finished_in and not self.fade_text.running:
            if len(self.sequence[self.step][1]) > 0:
                self.textstep = 0
                self.fade_text.FadeIn()
        if self.go_next:
            if len(self.sequence[self.step][1]) > 0: # any text?
                if self.fade.direction == 'in' and self.fade_text.direction == 'in' and self.fade_text.running:
                    self.fade_text.FadeOut()
            else:
                self.fade.FadeOut()
            self.go_next = False
        if self.fade_text.finished_out: # next text
            self.fade_text.Reset()
            self.textstep += 1
            if self.textstep == len(self.sequence[self.step][1]):
                self.textstep = -1
                if self.step == len(self.sequence)-1:
                    self.fade.FadeOut(True)
                else:
                    self.fade.FadeOut()
            else:
                self.fade_text.FadeIn()
        if self.fade.finished_out: # next cut
            self.step += 1
            if self.step == len(self.sequence):
                self.director.change_scene(self.next_scene_type,self.next_scene_switchtoargs)
            else:
                self.fade.Reset()
                self.fade.FadeIn()
        
    def on_event(self, events):
        for event in events:
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.mixer.music.stop()
                self.director.change_scene(self.next_scene_type,self.next_scene_switchtoargs)
            if event.type == KEYDOWN:
                self.go_next = True
    
    def render_animation(self, screen):
        raise NotImplementedError("render_animation abstract method must be defined in subclass.")
    
    def render_bg(self, screen):
        bgdata = self.sequence[self.step][0]
        if isinstance(bgdata,list):
            render_animation(screen)
            return
        surf = resources.cutscenesurfs[bgdata]
        pos = ((self.window_size[0]/2)-(surf.get_width()/2), (self.window_size[1]/2)-(surf.get_height()/2))
        screen.blit(surf, pos)
        
        # check for extra animation render in intro seq
        if len(self.sequence[self.step][1]) > 0:
            
            if self.sequence[self.step][1][0] == 'introtxt_001':
                tilecoords = resources.introcutscenespritedata['water'][self.ani_frame1]
                tilecoords2 = list(tilecoords)
                tilecoords2[2] = tilecoords[2]-7
                screen.blit(resources.cutscenesurfs['intro_sprites'], (168-8, 359+4*7), tilecoords)
                screen.blit(resources.cutscenesurfs['intro_sprites'], (168+56-8, 359+4*7), tilecoords)
                screen.blit(resources.cutscenesurfs['intro_sprites'], (168+2*56-8, 359+4*7), tilecoords2)
                
                tilecoords = resources.introcutscenespritedata['man'][self.ani_frame2]
                screen.blit(resources.cutscenesurfs['intro_sprites'], (166+3*7*8, 359-7*7), tilecoords)
                
                tilecoords = resources.introcutscenespritedata['penguin'][self.ani_frame2]
                screen.blit(resources.cutscenesurfs['intro_sprites'], (166-2*7*8, 359-7*7), tilecoords)
            
            
            if self.sequence[self.step][1][0] == 'introtxt_005':
                
                tilecoords = resources.introcutscenespritedata['sub'][0]
                if self.ani_frame2 == 0:
                    screen.blit(resources.cutscenesurfs['intro_sprites'], (168+7, 359-6*7), tilecoords)
                else:
                    screen.blit(resources.cutscenesurfs['intro_sprites'], (168+7, 359-5*7), tilecoords)
                
                tilecoords = resources.introcutscenespritedata['water'][self.ani_frame1]
                tilecoords2 = list(tilecoords)
                tilecoords2[2] = tilecoords[2]-7
                screen.blit(resources.cutscenesurfs['intro_sprites'], (168-8, 359+4*7), tilecoords)
                screen.blit(resources.cutscenesurfs['intro_sprites'], (168+56-8, 359+4*7), tilecoords)
                screen.blit(resources.cutscenesurfs['intro_sprites'], (168+2*56-8, 359+4*7), tilecoords2)
    
    def render_text(self, screen):
        textdata = self.sequence[self.step][1][self.textstep]
        surf = resources.cutscenesurfs[textdata]
        #pos = ((self.window_size[0]/2)-(surf.get_width()/2), (self.window_size[1]/2)-(surf.get_height()/2))
        pos = ((self.window_size[0]/2)-(surf.get_width()/2), 20)
        surf.set_alpha(255-self.fade_text.alpha)
        screen.blit(surf, pos)
    
    def on_draw(self, screen):
        screen.blit(self.background, (0, 0))
        self.render_bg(screen)
        if self.textstep >= 0:
            self.render_text(screen)
        self.fadebackground.set_alpha(self.fade.alpha)
        screen.blit(self.fadebackground, (0, 0))

