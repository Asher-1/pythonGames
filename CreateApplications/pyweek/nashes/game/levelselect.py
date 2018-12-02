"""The credits screen for the game"""

import random
import math
import pygame
import threading

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.sound
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors

if serge.common.PYMUNK_OK:
    import pymunk
    import serge.physical

from theme import G, theme
import common



class LevelSelect(serge.blocks.actors.ScreenActor):
    """The logic for the credits screen"""

    def __init__(self, options):
        """Initialise the screen"""
        super(LevelSelect, self).__init__('item', 'level-select-screen')
        self.options = options

    def addedToWorld(self, world):
        """The screen was added to the world"""
        super(LevelSelect, self).addedToWorld(world)
        the_theme = theme.getTheme('level-select-screen')
        self.L = L = the_theme.getProperty

        logo = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'logo', 'logo', 'foreground',
            center_position=L('logo-position'))

        logo = serge.blocks.utils.addSpriteActorToWorld(world, 'bg', 'bg', 'cs-level', 'background',
            center_position=L('screen-center'))

        serge.blocks.utils.addTextItemsToWorld(world, [
                    ('Back', 'back', serge.blocks.utils.worldCallback('start-screen', 'forward-click')),
                ],
                the_theme, 'ui')
        #
        self.levels = {}
        for idx, level_name in enumerate(G('game-levels')):
            is_unlocked = getattr(common.SETTINGS.values, level_name)
            display_name = '%s%s' % (G('level-name', level_name), ' LOCKED' if not is_unlocked else '')

            new_level = serge.blocks.actors.StringText(
                'level', level_name, display_name,
                colour=L('level-colour'),
                font_name=L('level-font'),
                font_size=L('level-size'),
            )
            new_level.setLayerName('ui')
            new_level.moveTo(L('level-x'), L('level-y') + idx * L('level-dy'))
            world.addActor(new_level)
            new_level.resizeTo(100, L('level-dy'))
            new_level.is_unlocked = is_unlocked
            #
            self.levels[level_name] = new_level
            #
            new_level.linkEvent(serge.events.E_LEFT_CLICK, self.clickLevel, level_name)
        #
        world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.worldActivated)

    def worldActivated(self, obj, arg):
        """World was activated - update the locked status"""
        for name, level in self.levels.iteritems():
            level.is_unlocked = getattr(common.SETTINGS.values, name)
            display_name = '%s%s' % (G('level-name', name), ' LOCKED' if not level.is_unlocked else '')
            level.visual.setText(display_name)

    def clickLevel(self, obj, arg):
        """Clicked on a level"""
        if self.levels[arg].is_unlocked or self.options.cheat:
            common.LEVEL_OUTCOME = common.O_SAME_LEVEL
            common.CURRENT_LEVEL = arg
            self.engine.setCurrentWorldByName('start-screen')
            serge.sound.Sounds.play('forward-click')

    def mouseEnter(self, obj):
        """Mouse entered"""
        if obj.is_unlocked:
            obj.visual.setColour(self.L('highlight-colour'))

    def mouseLeave(self, obj):
        """Mouse entered"""
        obj.visual.setColour(self.L('level-colour'))

    def updateActor(self, interval, world):
        """Update this actor"""
        super(LevelSelect, self).updateActor(interval, world)
        common.LEVEL_OUTCOME = common.O_QUIT
        #
        for obj in self.levels.values():
            self.mouseLeave(obj)
        #
        for obj in self.engine.getMouse().getActorsUnderMouse(self.world):
            if obj in self.levels.values():
                self.mouseEnter(obj)

        if self.keyboard.isClicked(pygame.K_ESCAPE):
            serge.sound.Sounds.play('back-click')
            common.LEVEL_OUTCOME = common.O_QUIT
            self.engine.setCurrentWorldByName('start-screen')




def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = LevelSelect(options)
    world = serge.engine.CurrentEngine().getWorld('level-select-screen')
    world.addActor(s)
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    #
    # Screenshots
    if options.screenshot:
        manager.assignBehaviour(None,
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

