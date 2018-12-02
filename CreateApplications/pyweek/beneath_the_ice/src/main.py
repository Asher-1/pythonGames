#!/usr/bin/python

"""
main.py - Main entry point for game
"""

import os
import pygame
from pygame.locals import *
from gamedirector import *

import resources
import cutscenes
import game

# Start
def main(mainpath):

    # Initialise pygame
    pygame.init()
    pygame.mixer.init()
    
    # start up director
    framerate = 30
    screen_res = (640,480)
    window_title = "Game"
    dir = GameDirector(window_title, screen_res, framerate)
    
    # Load resources
    resources.init(mainpath,screen_res)
    
    # Logo and title screens
    logocutscene = cutscenes.CutScene(dir, screen_res)
    dir.addscene('logocutscene', logocutscene)
    
    titlescene = cutscenes.TitleScreen(dir, screen_res)
    titlescene.savepath = os.path.join(mainpath,'data','saved_progress.txt')
    dir.addscene('titlescene', titlescene)
    
    # Load game scenes
    maingame = game.MainGame(dir, screen_res)
    maingame.progress_data.savepath = os.path.join(mainpath,'data','saved_progress.txt')
    dir.addscene('maingame', maingame)
    titlescene.h_progress_data = maingame.progress_data
    
    pausescene = game.PauseScreen(dir, screen_res)
    dir.addscene('pausescene', pausescene)
    maingame.h_pausescene = pausescene
    pausescene.h_maingame = maingame
    
    # Cutscenes
    
    introcutscene = cutscenes.CutScene(dir, screen_res)
    dir.addscene('introcutscene', introcutscene)
    
    cutscene1 = cutscenes.CutScene(dir, screen_res)
    dir.addscene('cutscene1', cutscene1)
    
    cutscene2 = cutscenes.CutScene(dir, screen_res)
    dir.addscene('cutscene2', cutscene2)
    
    cutscene3 = cutscenes.CutScene(dir, screen_res)
    dir.addscene('cutscene3', cutscene3)
    
    cutscene4 = cutscenes.CutScene(dir, screen_res)
    dir.addscene('cutscene4', cutscene4)
    
    cutscene5 = cutscenes.CutScene(dir, screen_res)
    dir.addscene('cutscene5', cutscene5)
    
    # start up director
    dir.change_scene('logocutscene', resources.logocutscene_data)
    
    #dir.change_scene('cutscene4', resources.cutscene4_data)
    
    #dir.change_scene('titlescene', [])
    
    #dir.change_scene('maingame', [True,'level_explore_001'])
    #dir.change_scene('maingame', [True,'level_blockages_002'])
    #dir.change_scene('maingame', [True,'level_boulderlift_003'])
    #dir.change_scene('maingame', [True,'level_sharksandmines_004'])
    #dir.change_scene('maingame', [True,'level_sharkminetwo_005'])
    #dir.change_scene('maingame', [True,'level_magnet_006'])
    #dir.change_scene('maingame', [True,'level_lasertunnel_007'])
    #dir.change_scene('maingame', [True,'level_sharkmagnet_008'])
    
    dir.loop()
    
    # exiting, record framerate
    #print maingame.avgframerate
    #fp = open(os.path.join(mainpath,'framerate.txt'),"w")
    #fp.write("%f\n"%(maingame.avgframerate))
    #fp.close()

