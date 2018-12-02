"""The overall UI"""

import pygame
import serge.actor
import serge.engine
import serge.blocks.actors
import serge.blocks.timers
import serge.blocks.animations
from theme import G, theme


class UI(serge.actor.MountableActor):
    """The overall UI"""

    def addedToWorld(self, world):
        """Added the UI to the world"""
        super(UI, self).addedToWorld(world)
        #
        the_theme = theme.getTheme('main')
        self.L = L = the_theme.getProperty
        self.world = world
        #
        self.face_bg = serge.actor.Actor('ui', 'face-bg')
        self.face_bg.setSpriteName('ui-face-back')
        self.mountActor(self.face_bg, G('ui-face-bg-pos'))
        self.face_bg.setLayerName('ui-back')
        #
        self.face = serge.actor.Actor('ui', 'face')
        self.face.setSpriteName('sl-face-static')
        self.mountActor(self.face, G('ui-face-pos'))
        self.face.setLayerName('ui-front')
        #
        self.interaction = serge.blocks.actors.FormattedText(
            'ui', 'interaction', '%(action)s',
            colour=G('ui-interaction-colour'),
            font_name=G('ui-interaction-font-name'),
            font_size=G('ui-interaction-font-size'),
            action='Nothing',
            justify='left',
        )
        self.mountActor(self.interaction, G('ui-interaction-pos'))
        self.interaction.setLayerName('ui-front')
        self.interaction.visible = False
        #
        self.distraction = serge.blocks.actors.FormattedText(
            'ui', 'distraction', 'D: Drop Distraction [%(number)s]',
            colour=G('ui-distraction-colour'),
            font_name=G('ui-distraction-font-name'),
            font_size=G('ui-distraction-font-size'),
            number=G('player-max-distractions'),
        )
        self.mountActor(self.distraction, G('ui-distraction-pos'))
        self.distraction.setLayerName('ui-front')
        self.distraction.active = False
        #
        self.distraction_items_off = serge.blocks.actors.RepeatedVisualActor(
            'ui', 'distraction-items', repeat=G('player-max-distractions'),
            spacing=G('ui-distraction-items-spacing'),
        )
        self.mountActor(self.distraction_items_off, G('ui-distraction-items-pos'))
        self.distraction_items_off.setLayerName('ui-front')
        self.distraction_items_off.setSpriteName('ui-distractor-off')
        self.distraction_items_off = serge.blocks.actors.RepeatedVisualActor(
            'ui', 'distraction-items', repeat=G('player-max-distractions'),
            spacing=G('ui-distraction-items-spacing'),
        )
        self.distraction_items = serge.blocks.actors.RepeatedVisualActor(
            'ui', 'distraction-items', repeat=G('player-max-distractions'),
            spacing=G('ui-distraction-items-spacing'),
        )
        self.mountActor(self.distraction_items, G('ui-distraction-items-pos'))
        self.distraction_items.setLayerName('ui-front')
        self.distraction_items.setSpriteName('ui-distractor-on')
        #
        self.bubble_bg = serge.actor.Actor('ui', 'bubble-bg')
        self.bubble_bg.setSpriteName('ui-bubble-bg')
        self.mountActor(self.bubble_bg, G('ui-bubble-bg-pos'))
        self.bubble_bg.setLayerName('ui-front')
        self.bubble_bg.visible = False
        #
        self.switch = serge.actor.Actor('ui', 'switch')
        self.switch.setSpriteName('ui-switch-on')
        self.mountActor(self.switch, G('ui-switch-pos'))
        self.switch.setLayerName('ui')
        self.switch.active = False
        #
        self.device = serge.actor.Actor('ui', 'device')
        self.device.setSpriteName('ui-device-off')
        self.mountActor(self.device, G('ui-device-pos'))
        self.device.setLayerName('ui')
        self.device.active = False
        #
        self.speech_timer = serge.blocks.timers.Timer(
            'ui', 'timer', G('ui-speech-show-for'), callback=self.hideSpeech,
            started=False,
        )
        self.mountActor(self.speech_timer, (0, 0))
        #
        #
        self.next_button = next_button = serge.blocks.animations.AnimatedActor('next')
        next_button.setLayerName('ui-front')
        next_button.setSpriteName('return-key')
        next_button.moveTo(*L('next-position'))
        next_button.active = False
        next_button.setZoom(0.7)
        world.addActor(next_button)
        #
        self.next_button.addAnimation(
            serge.blocks.animations.PulsedVisibility(
                self.L('next-pulse-duration'), self.L('next-pulse-on-fraction')
            ),
            'flash-button'
        )
        #
        self.spoken_text = serge.blocks.actors.StringText(
            'ui', 'spoken-text', 'Nothing',
            colour=G('ui-spoken-text-colour'),
            font_name='strangelove',
            font_size=G('ui-spoken-text-font-size'),
            justify='left',
        )
        self.spoken_text.setLayerName('ui-front')
        self.mountActor(self.spoken_text, G('ui-spoken-text-pos'))
        self.spoken_text.visible = False
        self.showing_interaction = False
        #
        self.keyboard = serge.engine.CurrentEngine().getKeyboard()
        self.active_player = self.visible_key = None

    def setInteraction(self, name):
        """Set the interactions"""
        self.interaction.setValue('action', name)
        self.showing_interaction = True
        #
        self.active_player = self.getPlayers()
        self.active_player.showSpeech(name)
        # self.visible_key = self.active_player.mountActor(self.getKeyActor('space-key'), (40, 0), rotate_with_actor=False)

    def getPlayers(self):
        """Return the active and inactive players"""
        active_players = [player for player in self.world.findActorsByTag('Player') if player.obj.active]
        active_player = active_players[0]
        return active_player

    def getKeyActor(self, name, rotation=0):
        """Return an actor showing a key"""
        actor = serge.actor.Actor('key', 'key-%s' % name)
        actor.setLayerName('ui')
        actor.setSpriteName(name)
        actor.setAngle(rotation)
        actor.setZoom(0.35)
        return actor

    def clearInteractions(self):
        """Clear the interactions"""
        self.interaction.setValue('action', '')
        self.showing_interaction = False
        if self.active_player:
            self.active_player.showSpeech('')
            # self.active_player.unmountActor(self.visible_key)
            # self.world.scheduleActorRemoval(self.visible_key)
            # self.active_player = self.visible_key = None

    def setDistractions(self, number):
        """Set the number of distractions"""
        self.distraction.setValue('number', number)
        self.distraction_items.setRepeat(number)

    def speakText(self, text, auto_hide=True):
        """Speak some text"""
        self.bubble_bg.visible = True
        self.spoken_text.visible = True
        # self.next_button.active = True
        self.spoken_text.value = text
        self.face.setSpriteName('sl-face')
        if auto_hide:
            self.speech_timer.resetAndStartTimer()

    def hideSpeech(self):
        """Hide the speech bubble"""
        self.bubble_bg.visible = False
        self.spoken_text.visible = False
        self.next_button.active = False
        self.face.setSpriteName('sl-face-static')
        self.speech_timer.stopTimer()

    def flippedSwitch(self):
        """Player has flipped the switch"""
        self.switch.setSpriteName('ui-switch-off')

    def gotDevice(self):
        """Player has got the device"""
        self.device.setSpriteName('ui-device-on')

    def isShowingText(self):
        """Return True if we are showing text"""
        return self.bubble_bg.visible

    def updateActor(self, interval, world):
        """Update the actor"""
        super(UI, self).updateActor(interval, world)
        #
        if self.keyboard.isClicked(pygame.K_RETURN) and self.isShowingText():
            self.hideSpeech()