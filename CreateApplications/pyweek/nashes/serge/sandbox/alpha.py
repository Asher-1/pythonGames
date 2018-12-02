"""Testing of alpha"""

import pygame
import serge.engine
import serge.visual

import serge.blocks.behaviours
import serge.blocks.utils
import serge.blocks.visualeffects

e = serge.engine.Engine()
serge.blocks.utils.createWorldsForEngine(e, ['main'])

l1 = serge.blocks.visualeffects.FadingLayer('back', 0)
l2 = serge.blocks.visualeffects.FadingLayer('front', 1)
e.getRenderer().addLayer(l1)
e.getRenderer().addLayer(l2)

w = e.setCurrentWorldByName('main')

serge.visual.Sprites.setPath('test/images')
serge.visual.Sprites.registerItem('blue-ship', 'blueship.png')
serge.visual.Sprites.registerItem('green-ship', 'greenship.png')

b = serge.blocks.behaviours.BehaviourManager('b', 'b')
w.addActor(b)
b.assignBehaviour(None, serge.blocks.behaviours.KeyboardQuit(), 'quit')

serge.blocks.utils.addSpriteActorToWorld(w, 'ship', 'ship', 'blue-ship', 'back', (50, 50))
serge.blocks.utils.addSpriteActorToWorld(w, 'ship', 'ship', 'green-ship', 'front', (60, 60))

visibility1 = visibility2 = 255

def doIt((dx, dy)):
    """Change the visibility"""
    global visibility1, visibility2
    w.log.debug('Changing %d, %d' % (dx, dy))
    visibility1 += dy*10
    visibility2 += dx*10
    l1.visibility = visibility1    
    l2.visibility = visibility2
    
def adjustIt(layer, arg):
    """Adjust the layer visibility"""
    w.log.debug('Visiblity now %f' % visibility)
    l1.visibility = visibility1    
    l2.visibility = visibility2
    
b.assignBehaviour(None, serge.blocks.behaviours.KeyboardNSEWToVectorCallback(doIt), 'change')

l = e.getRenderer().getLayer('back')
l.linkEvent(serge.events.E_AFTER_RENDER, adjustIt)

e.run(60)
