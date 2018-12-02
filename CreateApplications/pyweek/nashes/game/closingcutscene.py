"""The credits screen for the game"""

import random
import math
import pygame
import threading

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors

if serge.common.PYMUNK_OK:
    import pymunk
    import serge.physical

from theme import G, theme
import common



class ClosingCutScene(serge.blocks.actors.ScreenActor):
    """The logic for the credits screen"""

    def __init__(self, options):
        """Initialise the screen"""
        super(ClosingCutScene, self).__init__('item', 'closing-cut-screen')
        self.options = options

    def addedToWorld(self, world):
        """The screen was added to the world"""
        super(ClosingCutScene, self).addedToWorld(world)
        the_theme = theme.getTheme('closing-cut-scene')
        L = the_theme.getProperty

        logo = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'logo', 'logo', 'foreground',
            center_position=L('logo-position'))

        logo = serge.blocks.utils.addSpriteActorToWorld(world, 'bg', 'bg', 'cs-end', 'background',
            center_position=L('screen-center'))

        serge.blocks.utils.addTextItemsToWorld(world, [
                    ('Congratulations', 'congrats'),
                    ('Thanks for Playing', 'thanks'),
                    ('Back', 'back', serge.blocks.utils.worldCallback('start-screen', 'forward-click')),
                ],
                the_theme, 'ui')
        #

    def updateActor(self, interval, world):
        """Update this actor"""
        super(ClosingCutScene, self).updateActor(interval, world)
        common.LEVEL_OUTCOME = common.O_QUIT



def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = ClosingCutScene(options)
    world = serge.engine.CurrentEngine().getWorld('closing-cut-scene')
    world.addActor(s)
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    manager.assignBehaviour(None, serge.blocks.behaviours.KeyboardQuit(), 'keyboard-quit')
    #
    # Screenshots
    if options.screenshot:
        manager.assignBehaviour(None,
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

