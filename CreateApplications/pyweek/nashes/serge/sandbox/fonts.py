"""Testing out fonts"""

import pygame
import os
import time

import serge.visual
import serge.engine
import serge.blocks.utils
import serge.blocks.visualblocks

e = serge.engine.Engine()

serge.blocks.utils.createLayersForEngine(e, ['main'])
serge.blocks.utils.createWorldsForEngine(e, ['main'])
main = e.setCurrentWorldByName('main')

serge.blocks.utils.addVisualActorToWorld(main, 't', 't', 
    serge.visual.Text('Hello', (255,0,0,255), 'KlaudiaRegular/KlaudiaRegular.ttf'), 'main', (300, 50))
    

e.run(60, time.time()+10)

