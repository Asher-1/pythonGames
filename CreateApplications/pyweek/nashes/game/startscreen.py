"""The start screen for the game"""

import random
import math
import pygame

from serge.simplevecs import Vec2d
import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.sound
import serge.blocks.utils
import serge.blocks.statemachine
import serge.blocks.visualblocks
import serge.blocks.animations
import serge.blocks.behaviours
import serge.blocks.actors

if serge.common.PYMUNK_OK:
    import pymunk
    import serge.physical

from theme import G, theme
import common
import mainscreen


class StartScreen(serge.blocks.actors.ScreenActor):
    """The logic for the start screen"""

    def __init__(self, options):
        """Initialise the screen"""
        super(StartScreen, self).__init__('item', 'main-screen')
        self.options = options
        self.stop_music = False

    def addedToWorld(self, world):
        """The start screen was added to the world"""
        super(StartScreen, self).addedToWorld(world)
        #
        self.state = world.addActor(serge.blocks.statemachine.StateMachine('state', 'state'))
        #
        # Logo
        the_theme = theme.getTheme('start-screen')
        L = the_theme.getProperty
        #
        bg = serge.blocks.utils.addSpriteActorToWorld(world, 'bg', 'bg', 'start-back', 'background',
            center_position=L('screen-center'))
        #
        nashes = serge.blocks.animations.AnimatedActor(
            'logo', 'nashes',
        )
        nashes.setSpriteName('ashes')
        nashes.setLayerName('foreground')
        nashes.addAnimation(
            serge.blocks.animations.MovementTweenAnimation(
                nashes, Vec2d(L('nashes-start-x'), L('nashes-start-y')),
                Vec2d(L('nashes-end-x'), L('nashes-end-y')),
                duration=L('nashes-animation-time'),
                function=serge.blocks.animations.TweenAnimation.sinInOut,
                delay=L('nashes-animation-delay'),
            ),
            'nashes-enter'
        )
        world.addActor(nashes)
        #
        to = serge.blocks.animations.AnimatedActor(
            'logo', 'to',
        )
        to.setSpriteName('to')
        to.setLayerName('foreground')
        to.addAnimation(
            serge.blocks.animations.MovementTweenAnimation(
                to, Vec2d(L('to-start-x'), L('to-start-y')),
                Vec2d(L('to-end-x'), L('to-end-y')),
                duration=L('to-animation-time'),
                function=serge.blocks.animations.TweenAnimation.sinInOut,
                delay=L('to-animation-delay'),
            ),
            'to-enter'
        )
        world.addActor(to)
        #
        ashes = serge.blocks.animations.AnimatedActor(
            'logo', 'ashes',
        )
        ashes.setSpriteName('nashes')
        ashes.setLayerName('foreground')
        ashes.addAnimation(
            serge.blocks.animations.MovementTweenAnimation(
                ashes, Vec2d(L('ashes-start-x'), L('ashes-start-y')),
                Vec2d(L('ashes-end-x'), L('ashes-end-y')),
                duration=L('ashes-animation-time'),
                function=serge.blocks.animations.TweenAnimation.sinInOut,
                delay=L('ashes-animation-delay'),
            ),
            'ashes-enter'
        )
        world.addActor(ashes)
        #
        serge.blocks.utils.addTextItemsToWorld(world, [
                    # (L('title'), 'title'),
                    ('v' + common.version, 'version'),
                    # ('Start', 'start',  self.startClicked),
                    ('Help', 'help',  serge.blocks.utils.worldCallback('help-screen', 'forward-click')),
                    ('Credits', 'credits',  serge.blocks.utils.worldCallback('credits-screen', 'forward-click')),
                    # ('Achievements', 'achievements', serge.blocks.utils.worldCallback('achievements-screen', 'forward-click')),
                ],
                the_theme, 'foreground')

        self.start = serge.blocks.utils.addTextToWorld(
            world, 'Start', 'start', theme.getTheme('start-screen'), 'foreground',
        )
        self.start.linkEvent(serge.events.E_LEFT_CLICK, self.startClicked)
        #
        self.continue_button = serge.blocks.utils.addTextToWorld(
            world, 'Continue', 'continue', theme.getTheme('start-screen'), 'foreground',
        )
        self.continue_button.linkEvent(serge.events.E_LEFT_CLICK, self.continueClicked)
        if common.SETTINGS.values.last_level:
            self.continue_button.visible = True
        else:
            self.continue_button.visible = False
        #
        world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.worldActivated)
        self.auto_go_to_level = False

    def updateActor(self, interval, world):
        """Update this actor"""
        super(StartScreen, self).updateActor(interval, world)
        #
        if not self.stop_music and not serge.sound.Music.isPlayingSong('start-music'):
            self.log.info('Starting music')
            serge.sound.Music.play('start-music')
        #
        if self.auto_go_to_level:
            self.engine.setCurrentWorldByName(self.auto_go_to_level)
            self.auto_go_to_level = False
            serge.sound.Music.fadeout(5000.0)

    def worldActivated(self, obj, arg):
        """The world was activated"""
        #
        # Check the level outcome
        if common.LEVEL_OUTCOME == common.O_SAME_LEVEL:
            self.recreateMainScreen(common.CURRENT_LEVEL)
        elif common.LEVEL_OUTCOME == common.O_NEXT_LEVEL:
            all_levels = G('game-levels')
            index = all_levels.index(common.CURRENT_LEVEL)
            if index < len(all_levels) - 1:
                new_level = all_levels[index + 1]
                self.recreateMainScreen(new_level)
                common.SETTINGS.values.last_level = new_level
                setattr(common.SETTINGS.values, new_level, True)
                common.SETTINGS.saveValues()
            else:
                self.auto_go_to_level = 'closing-cut-scene'
        else:
            self.stop_music = False
            if common.LEVEL_OUTCOME == common.O_QUIT:
                self.auto_go_to_level = False

    def startClicked(self, obj, arg):
        """User clicked start"""
        common.SETTINGS.values.last_level = common.CURRENT_LEVEL
        common.SETTINGS.saveValues()

        serge.sound.Sounds.play('forward-click')
        self.stop_music = True
        serge.sound.Music.fadeout(G('music-fade-out'))
        self.state.add_generator('fade-out', self.fadeOutAnimation())
        self.continue_button.visible = True

    def continueClicked(self, obj, arg):
        """User clicked continue"""
        serge.sound.Sounds.play('forward-click')
        self.stop_music = True
        serge.sound.Music.fadeout(G('music-fade-out'))
        self.engine.setCurrentWorldByName('level-select-screen')

    def fadeOutAnimation(self):
        """Fade out this screen"""
        serge.sound.Sounds.play('massive-explosion')
        block = serge.blocks.visualblocks.Rectangle(
            (G('screen-width'), G('screen-height')), (255, 255, 255, 0))
        overlay = serge.actor.Actor('overlay')
        overlay.visual = block
        overlay.setLayerName('ui-front')
        overlay.moveTo(*G('screen-center'))
        self.world.addActor(overlay)
        yield 0
        #
        for i in range(0, 255, 20):
            self.log.debug('Setting fade to %s' % i)
            overlay.visual.colour = (255, 255, 255, i)
            yield 10
            if self.keyboard.isClicked(pygame.K_SPACE):
                break
        #
        for i in range(0, 255, 20):
            self.log.debug('Setting fade to %s' % i)
            overlay.visual.colour = (255 - i, 255 - i, 255 - i, 255)
            yield 10
            if self.keyboard.isClicked(pygame.K_SPACE):
                break
        #
        self.world.removeActor(overlay)
        self.engine.setCurrentWorldByName('cut-scene-screen')

    def recreateMainScreen(self, level_name):
        """Recreate the main screen"""
        self.engine.removeWorldNamed('main-screen')
        serge.blocks.utils.createWorldsForEngine(self.engine, ['main-screen'])
        mainscreen.main(self.options, level_name)
        self.auto_go_to_level = 'main-screen'


def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = StartScreen(options)
    world = serge.engine.CurrentEngine().getWorld('start-screen')
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

