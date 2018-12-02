"""The start screen for the game"""

import random
import math
import pygame


import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.sound
import serge.blocks.utils
import serge.blocks.animations
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors

if serge.common.PYMUNK_OK:
    import pymunk
    import serge.physical

from theme import G, theme
import common
import mainscreen


class CutScene(serge.blocks.actors.ScreenActor):
    """The logic for the cutscene screen"""

    def __init__(self, options):
        """Initialise the screen"""
        super(CutScene, self).__init__('item', 'main-screen')
        self.options = options

    def addedToWorld(self, world):
        """The start screen was added to the world"""
        super(CutScene, self).addedToWorld(world)
        #
        # Logo
        the_theme = theme.getTheme('cut-scene-screen')
        self.L = L = the_theme.getProperty
        #
        block = serge.blocks.visualblocks.Rectangle(
            (G('screen-width'), G('screen-height')), (0, 0, 0, 255))
        self.overlay = overlay = serge.actor.Actor('overlay')
        overlay.visual = block
        overlay.setLayerName('middleground')
        overlay.moveTo(*G('screen-center'))
        self.world.addActor(overlay)
        #
        self.picture = picture = serge.actor.Actor('picture')
        picture.setLayerName('background')
        picture.moveTo(*G('screen-center'))
        self.world.addActor(picture)
        #
        self.strangelove = strangelove = serge.actor.Actor('strangelove')
        strangelove.setLayerName('foreground')
        strangelove.moveTo(*G('screen-center'))
        strangelove.setSpriteName('cs-strangelove')
        strangelove.visible = False
        self.world.addActor(strangelove)
        #
        self.next_button = next_button = serge.blocks.animations.AnimatedActor('next')
        next_button.setLayerName('ui-front')
        next_button.setSpriteName('return-key')
        next_button.moveTo(*L('next-position'))
        next_button.active = False
        self.world.addActor(next_button)
        #
        self.next_button.addAnimation(
            serge.blocks.animations.PulsedVisibility(
                self.L('next-pulse-duration'), self.L('next-pulse-on-fraction')
            ),
            'flash-button'
        )
        #
        self.text = serge.blocks.actors.StringText(
            'text', 'text', '',
            colour=L('text-colour'),
            font_size=L('text-size'),
            font_name=L('text-font'),
            justify='left',
        )
        self.text.setLayerName('ui')
        self.text.moveTo(*L('text-pos'))
        world.addActor(self.text)
        #
        self.typing = serge.sound.Sounds.getItem('typing')
        #
        world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.worldActivated)
        #
        self.game_state = serge.blocks.statemachine.StateMachine('state-machine', 'state-machine')
        self.game_state.add_generator('main', self.startCutScene())
        world.addActor(self.game_state)

    def updateActor(self, interval, world):
        """Update this actor"""
        super(CutScene, self).updateActor(interval, world)
        #

    def worldActivated(self, obj, arg):
        """The world was activated"""
        #
        # Check the level outcome

    def fadeToPicture(self):
        """Fade the overlay to a picture"""
        for i in range(0, 255, 50):
            self.overlay.visual.colour = (0, 0, 0, 255 - i)
            yield 10

    def fadeToBlack(self):
        """Fade the overlay to black"""
        for i in range(0, 255, 50):
            self.overlay.visual.colour = (0, 0, 0, i)
            yield 10

    def appearText(self, text):
        """Make some text appear"""
        self.typing.play()
        display = ''
        for char in text:
            if char != '@':
                display += char
                self.text.value = display
                yield self.L('text-appear-rate')
            else:
                self.typing.pause()
                yield self.L('text-delay-time')
                self.typing.unpause()
        #
        self.typing.stop()

    def showCutScene(self, items, immediate_text):
        """"Start the cut scene"""
        #
        for image_name, text in items:
            self.next_button.active = False

            self.picture.setSpriteName(image_name)
            self.text.value = ''
            for result in self.fadeToPicture():
                yield result
            #
            if immediate_text:
                self.text.value = text
            else:
                for result in self.appearText(text):
                    yield result

            yield self.L('post-delay')
            self.next_button.active = True
            while not self.keyboard.isClicked(pygame.K_RETURN):
                yield 10

            serge.sound.Sounds.play('soft-click')

    def startCutScene(self):
        """Start the whole cut scene"""
        #
        yield self.L('initial-delay')
        #
        for result in self.showCutScene(self.L('screens'), immediate_text=False):
            yield result

        self.strangelove.visible = True
        self.picture.setSpriteName(self.L('strangelove')[0][0])
        self.text.moveTo(*self.L('strangelove-text-pos'))
        self.text.visual.font_name = self.L('strangelove-text-font')
        self.text.visual.setFontSize(self.L('text-size'))
        self.text.value = self.L('strangelove')[0][1]

        serge.sound.Music.play('cut-scene')

        yield self.L('post-delay')
        self.next_button.active = True

        while not self.keyboard.isClicked(pygame.K_RETURN):
            yield 10

        serge.sound.Sounds.play('soft-click')

        for result in self.showCutScene(self.L('strangelove')[1:], immediate_text=True):
            yield result

        self.overlay.setLayerName('ui-front')
        self.world.requestResortActors()

        for result in self.fadeToBlack():
            yield result

        serge.sound.Music.fadeout(G('music-fade-out'))
        self.engine.setCurrentWorldByName('main-screen')


def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = CutScene(options)
    world = serge.engine.CurrentEngine().getWorld('cut-scene-screen')
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

