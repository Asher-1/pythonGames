"""A test of the new mouse system


Prev    This
-------------
Up      Down
Up      Up
Down    Up
Down    Up + Down


"""

import sys
import pygame

import serge.engine
import serge.world
import serge.input
import serge.blocks.utils
import serge.blocks.actors

e = serge.engine.Engine()
serge.blocks.utils.createWorldsForEngine(e, ['test'])

class A(serge.blocks.actors.ScreenActor):
    def updateActor(self, interval, world):
        """Update ourself"""
        if self.mouse.isClicked(serge.input.M_LEFT):
            self.log.info('Left clicked')        
        if self.keyboard.isClicked(pygame.K_ESCAPE):
            e.stop()
            
a = A('tester')
w = e.getWorld('test')
w.addActor(a)
e.setCurrentWorld(w)

e.run(int(sys.argv[1]))
