"""Test of making a shadow"""

import pygame
import Numeric
import os
import time

import serge.visual
import serge.engine
import serge.blocks.utils
import serge.blocks.visualblocks

serge.visual.Register.setPath(os.path.join('..', 'test', 'images'))
serge.visual.Register.registerItem('green', 'greenship.png')
serge.visual.Register.registerItem('blue', 'blueship.png')

e = serge.engine.Engine()
r = e.getRenderer()

serge.blocks.utils.createLayersForEngine(e, ['back', 'middle', 'front'])
serge.blocks.utils.createWorldsForEngine(e, ['main'])
main = e.setCurrentWorldByName('main')

serge.blocks.utils.addSpriteActorToWorld(main, 't', 't', 'green', 'front', (150, 150))
serge.blocks.utils.addSpriteActorToWorld(main, 't', 't', 'blue', 'front', (275, 225))
serge.blocks.utils.addVisualActorToWorld(main, 'b', 'b', 
    serge.blocks.visualblocks.Rectangle((800,600), (255,255,255)), 'back', (0, 0))

b = serge.visual.SurfaceDrawing(800, 600)
main.renderTo(r, 0)
s = r.getLayer('front').getSurface()


def doit(s):
    ambience = 0.5
    image_alpha = pygame.surfarray.pixels_alpha(s)
    if ambience > 0.0:
        shadow_alpha = (image_alpha *
                        (1.0 - ambience)).astype(Numeric.UInt8)
    else:
        shadow_alpha = image_alpha


    shadow = s.convert_alpha()
    shading = pygame.Surface(s.get_size(), pygame.SRCALPHA, 32)
    pygame.surfarray.pixels_alpha(shading)[...] = image_alpha
    shadow.blit(shading, (0, 0))
    pygame.surfarray.pixels_alpha(shadow)[...] = shadow_alpha

    image_alpha = None
    return shadow

s = doit(s)
b.setSurface(s)
sa = serge.blocks.utils.addVisualActorToWorld(main, 's', 's', b, 'middle', (325, 245))

pygame.image.save(sa.visual.getSurface(), 'test.png')
sa.log.debug('%s %s' % (sa.visual.getSurface(), id(sa.visual.getSurface())))

s = r.getLayer('front').active = True
s = r.getLayer('back').active = True
s = r.getLayer('middle').active = True

e.run(60, time.time()+2)

pygame.image.save(sa.visual.getSurface(), 'test3.png')
sa.log.debug('%s %s' % (sa.visual.getSurface(), id(sa.visual.getSurface())))

