"""The main screen for the game"""

import random
import math
import pygame
import os
import time

import serge.actor
import serge.registry
import serge.sound
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.statemachine
import serge.blocks.textgenerator

if serge.common.PYMUNK_OK:
    import pymunk
    import serge.physical

from theme import G, theme
import common
import grid
import gameobjects
import ui


class MainScreen(serge.blocks.actors.ScreenActor):
    """The logic for the main screen"""

    def __init__(self, options, current_level):
        """Initialise the screen"""
        super(MainScreen, self).__init__('item', 'main-screen')
        self.options = options
        self.level_name = current_level if current_level else G('game-levels')[0]

    def addedToWorld(self, world):
        """Added to the world"""
        super(MainScreen, self).addedToWorld(world)
        #
        self.L = theme.getTheme(self.level_name).getProperty
        #
        self.event_pump = world.findActorByName('behaviours')
        self.game_state = serge.blocks.statemachine.StateMachine('state-machine', 'state-machine')
        self.game_state.add_generator('main', self.initialGameState())
        world.addActor(self.game_state)
        #
        self.grid = grid.LevelGrid(os.path.join('levels', '%s.tmx' % self.level_name), self.event_pump)
        common.CURRENT_LEVEL = self.level_name
        #
        # Set main graphics
        self.setMainGraphics()
        self.addObjects(self.grid.objects)
        self.addObjects(self.grid.ais)
        self.addUI()
        #
        self.text = serge.blocks.textgenerator.TextGenerator()
        self.text.addExamplesFromFile(os.path.join('dialog', 'strangelove.txt'))
        #
        self.alarm_sound = serge.sound.Sounds.getItem('alarm')
        self.alarm_sound.last_play = time.time()
        #
        self.event_pump.linkEvent(common.E_PLAYER_CAPTURED, self.playerCaptured)
        self.event_pump.linkEvent(common.E_INTERACTION_AVAILABLE, self.interactionAvailable)
        self.event_pump.linkEvent(common.E_NO_INTERACTIONS, self.noInteractionAvailable)
        self.event_pump.linkEvent(common.E_PLAYER_EXITED, self.playerExited)
        self.event_pump.linkEvent(common.E_PLAYER_GOT_DEVICE, self.playerGotDevice)
        self.event_pump.linkEvent(common.E_PLAYER_FLIPPED_SWITCH, self.playerFlippedSwitch)
        self.event_pump.linkEvent(common.E_PLAYER_DROPPED_DISTRACTION, self.playerDroppedDistraction)
        self.event_pump.linkEvent(common.E_ALARM_DETECTED, self.detectedAlarm)
        self.event_pump.linkEvent(common.E_SWITCH_THROW, self.switchThrown)
        self.event_pump.linkEvent(common.E_AI_SAW_PLAYER, self.sawPlayer)
        #
        self.eerie = serge.sound.Sounds.getItem('eerie-ambience')
        self.eerie.play(-1)
        #
        world.linkEvent(serge.events.E_DEACTIVATE_WORLD, self.worldDeactivated)
        #
        # Cheating
        if self.options.cheat:
            fps = serge.blocks.utils.addActorToWorld(world,
                serge.blocks.actors.FPSDisplay(G('fps-x'), G('fps-y'), G('fps-colour'), G('fps-size')))

    def worldDeactivated(self, obj, arg):
        """World was deactivated"""
        self.eerie.stop()

    def setMainGraphics(self):
        """Setup the main graphics"""
        #
        self.background = serge.blocks.utils.addSpriteActorToWorld(
            self.world, 'graphic', 'background',
            'main-background',
            layer_name='background',
        )
        self.background.visual.getSurface().blit(self.grid.background, G('tile-offset'))
        self.background.visual.getSurface().blit(self.grid.foreground, G('tile-offset'))
        # self.background.resizeTo(
        #     self.grid.background.get_width(),
        #     self.grid.background.get_height()
        # )
        #
        # self.foreground = serge.blocks.utils.addVisualActorToWorld(
        #     self.world, 'graphic', 'foreground',
        #     serge.visual.SurfaceDrawing(1, 1),
        #     layer_name='middleground',
        # )
        # self.foreground.moveTo(*G('tile-position'))
        # self.foreground.visual.setSurface(self.grid.foreground)
        # self.foreground.resizeTo(
        #     self.grid.foreground.get_width(),
        #     self.grid.foreground.get_height()
        # )
        # self.foreground.moveTo(*G('tile-position'))
        #
        try:
            self.graphical_layer = serge.blocks.utils.addSpriteActorToWorld(
                self.world, 'overlay', 'overlay', 'overlay-%s' % self.level_name,
                center_position=G('tile-position'),
                layer_name='middleground',
            )
        except serge.registry.UnknownItem:
            self.log.warn('No graphical overlay for this tiled level')
        #
        self.overlay = serge.blocks.utils.addActorToWorld(
            self.world,
            gameobjects.ControlOverlay('overlay', 'overlay', self.grid),
            layer_name='overlay',
        )
        self.overlay.moveTo(*G('overlay-position'))
        #
        self.visual_grid = gameobjects.Grid('grid', 'grid')
        self.world.addActor(self.visual_grid)
        self.visual_grid.setLayerName('objects')
        self.visual_grid.setSpatial(*self.background.getSpatial())
        self.visual_grid.x = self.visual_grid.x - self.visual_grid.width / 2
        self.visual_grid.y = self.visual_grid.y - self.visual_grid.height / 2
        #
        # self.foreground.visible = True
        self.overlay.visible = False
        #
        self.has_switch = False
        self.has_device = False
        self.has_exited = False
        self.has_been_captured = False
        self.players_exited = set()

    def addObjects(self, items):
        """Add the objects to the screen"""
        #
        for name, obj in items.iteritems():
            try:
                cls = getattr(gameobjects, obj.__class__.__name__)
            except AttributeError:
                raise ValueError('Unknown game object "%s" for "%s"' % (
                    obj.__class__.__name__, name
                ))
            new_obj = cls(name, obj, self.grid)
            self.world.addActor(new_obj)
            new_obj.repositionBasedOnCell()
            new_obj.setLayerName(new_obj.normal_layer)

    def addUI(self):
        """Add the UI"""
        self.ui = ui.UI('ui', 'ui')
        self.ui.moveTo(*G('ui-position'))
        self.world.addActor(self.ui)

    def updateActor(self, interval, world):
        """Update this actor"""
        super(MainScreen, self).updateActor(interval, world)
        #
        if self.keyboard.isDown(pygame.K_o):
            if not self.overlay.visible:
                self.overlay.createVisual()
                serge.sound.Sounds.play('overview-on')
            self.overlay.visible = True
        else:
            self.overlay.visible = False
        #
        if self.keyboard.isClicked(pygame.K_ESCAPE):
            serge.sound.Sounds.play('back-click')
            self.engine.setCurrentWorldByName('level-select-screen')
        #
        if self.options.cheat and self.keyboard.isClicked(pygame.K_t):
            self.ui.speakText('Hello there\nThis is some multiline text\nAnd it works well')
        if self.options.cheat and self.keyboard.isClicked(pygame.K_e):
            self.has_device = True
            self.players_exited = [1,2]
        if self.options.cheat and self.keyboard.isClicked(pygame.K_f):
            self.players_exited = [1,2]
        if self.options.cheat and self.keyboard.isClicked(pygame.K_c):
            self.has_been_captured = True

    def playerCaptured(self, obj, arg):
        """The player was captured"""
        self.log.info('The player was captured')
        self.has_been_captured = True

    def interactionAvailable(self, obj, msg):
        """An interaction is available"""
        self.ui.setInteraction(obj)

    def noInteractionAvailable(self, obj, arg):
        """No interactions are available"""
        self.ui.clearInteractions()

    def playerExited(self, obj, arg):
        """The player exited the level"""
        #
        # Determine the player
        for player in self.grid.players:
            if player.active:
                the_player = player
                break
        else:
            raise ValueError('Could not determine the player')
        self.log.info('The player %s exited the level' % the_player.name)
        the_player.has_exited = True
        self.players_exited.add(the_player)

    def playerGotDevice(self, obj, arg):
        """The player got the device"""
        self.log.info('The player got the device')
        self.has_device = True
        self.ui.gotDevice()
        #
        for exit in self.world.findActorsByTag('Exit'):
            exit.ready_to_exit = True

    def playerFlippedSwitch(self, obj, arg):
        """The player flipped the switch"""
        self.log.info('The player flipped the switch')
        self.has_switch = True
        self.ui.flippedSwitch()

    def playerDroppedDistraction(self, obj, arg):
        """The player dropped a distraction"""
        self.ui.setDistractions(obj.distractions)

    def speakLines(self, name):
        """Speak some lines"""
        initial_lines = G(name, self.level_name)
        #
        # Show the text
        for text in initial_lines:
            if text == 'QUIT':
                break
            self.ui.speakText(text)
            while self.ui.isShowingText():
                yield 0

    # Game states
    def initialGameState(self):
        """The main game state"""
        #
        # Pause all AI's and player
        self.setActorStates(True, 'Pausing all game actors')
        #
        for result in self.speakLines('start-instructions'):
            yield result

        #
        custom_name = self.level_name.replace('-', '_')
        if hasattr(self, custom_name):
            self.log.info('Using custom level state')
            self.game_state.add_generator('tutorial', getattr(self, custom_name)())
        #
        self.setActorStates(False, 'Unpausing actors')
        #
        while True:
            if len(self.players_exited) == 2:
                if self.has_device:
                    self.game_state.add_generator('ending-state', self.leftLevelSuccess())
                else:
                    self.game_state.add_generator('ending-state', self.leftLevelFailure())
                break
            if self.has_been_captured:
                self.game_state.add_generator('ending-state', self.wasCapturedFailure())
                break
            #
            yield 0

    def level_1(self):
        """Custom tutorial for level 1"""
        #
        self.ui.setDistractions(0)
        #
        if common.SETTINGS.values.saw_tutorial:
            return
        #
        active_players = [player for player in self.world.findActorsByTag('Player') if player.obj.active]
        inactive_players = [player for player in self.world.findActorsByTag('Player') if not player.obj.active]
        active_player = active_players[0]
        inactive_player = inactive_players[0]
        #
        self.log.info('Adding keys to player')
        a1 = active_player.mountActor(self.getKeyActor('up-key'), (0, -40), rotate_with_actor=False)
        a2 = active_player.mountActor(self.getKeyActor('down-key'), (0, 40), rotate_with_actor=False)
        a3 = active_player.mountActor(self.getKeyActor('up-key', rotation=90), (-40, 0), rotate_with_actor=False)
        a4 = active_player.mountActor(self.getKeyActor('up-key', rotation=-90), (40, 0), rotate_with_actor=False)
        #
        used = 0
        while used < 3:
            if self.keyboard.isClicked(pygame.K_UP) or \
                    self.keyboard.isClicked(pygame.K_DOWN) or \
                    self.keyboard.isClicked(pygame.K_LEFT) or \
                    self.keyboard.isClicked(pygame.K_RIGHT):
                used += 1
            #
            yield 0
        #
        active_player.unmountActor(a1)
        active_player.unmountActor(a2)
        active_player.unmountActor(a3)
        active_player.unmountActor(a4)
        #
        interaction = active_player.mountActor(self.getKeyActor('space-key'), (40, 0), rotate_with_actor=False)
        interaction.visible = False
        shown = 0
        #
        while shown <= 0:
            if self.ui.showing_interaction:
                interaction.visible = True
            else:
                interaction.visible = False
            if self.keyboard.isClicked(pygame.K_SPACE):
                shown += 1
            yield 0
        #
        active_player.unmountActor(interaction)
        #
        while active_player.obj.cx <= 13:
            yield 0
        #
        self.ui.speakText('Use ze controller to open ze door for your\nbrother. Stand by it unt press zpace', auto_hide=False)
        #
        while not self.keyboard.isClicked(pygame.K_SPACE):
            yield 0
        #
        self.ui.hideSpeech()
        yield 2000
        #
        self.ui.speakText('Now zwitch to controlling your\nbrother. Press zee TAB key.', auto_hide=False)
        while not self.keyboard.isClicked(pygame.K_TAB):
            yield 0
        #
        self.ui.hideSpeech()
        #
        while inactive_player.obj.cx < 13:
            self.log.debug('Waiting for inactive player to get into next room')
            yield 0
        #
        # And then tell about overlay
        self.ui.speakText('You can zee vat controllers do uzing ze overlay\nHold "O". "O" vur Overlay. Geddit?', auto_hide=False)
        #
        while not self.keyboard.isDown(pygame.K_o):
            yield 0
        #
        self.ui.hideSpeech()
        yield 2000
        #
        self.ui.speakText('Pretty zimple eh? \nWat ver you expecting ... a PipBoy??')
        while self.ui.isShowingText():
            yield 0
        #
        yield 2000
        self.ui.speakText('You are on your own now!\nSPC to do stuff. TAB to svitch. O for Overlay!')
        while self.ui.isShowingText():
            yield 0
        #
        while not self.has_device:
            yield 0
        #
        self.ui.speakText('Now you muzt get both\nzee tvins out to ze\nexitz.')
        while self.ui.isShowingText():
            yield 0
        #
        common.SETTINGS.values.saw_tutorial = True
        common.SETTINGS.saveValues()

    def getKeyActor(self, name, rotation=0):
        """Return an actor showing a key"""
        actor = serge.actor.Actor('key', 'key-%s' % name)
        actor.setLayerName('ui')
        actor.setSpriteName(name)
        actor.setAngle(rotation)
        actor.setZoom(0.35)
        return actor

    def setActorStates(self, state, log=None):
        """Set the states of all the critical actors"""
        if log:
            self.log.info(log)
        #
        all_actors = self.world.findActorsByTag('Player')
        for actor in all_actors:
            actor.is_captured = state

    def leftLevelSuccess(self):
        """Player has left the level and wins"""
        self.setActorStates(True, 'Stopping actors when leaving')
        serge.sound.Sounds.play('success')
        for result in self.speakLines('success-instructions'):
            yield result
        #
        common.LEVEL_OUTCOME = common.O_NEXT_LEVEL
        self.engine.setCurrentWorldByName('start-screen')

    def leftLevelFailure(self):
        """Player has left the level and loses"""
        self.setActorStates(True, 'Stopping actors when leaving')
        serge.sound.Sounds.play('failure')
        #
        for result in self.speakLines('failure-instructions'):
            yield result
        #
        common.LEVEL_OUTCOME = common.O_SAME_LEVEL
        self.engine.setCurrentWorldByName('start-screen')

    def wasCapturedFailure(self):
        """Player was captured and loses"""
        serge.sound.Sounds.play('captured')
        self.setActorStates(True, 'Stopping actors when leaving')
        #
        for result in self.speakLines('failure-captured-instructions'):
            yield result
        #
        common.LEVEL_OUTCOME = common.O_SAME_LEVEL
        self.engine.setCurrentWorldByName('start-screen')

    def detectedAlarm(self, obj, arg):
        """An alarm was detected"""
        if not self.alarm_sound.isPlaying() or time.time() - self.alarm_sound.last_play > 2.0:
            self.log.info('Playing the alarm sound')
            self.alarm_sound.play()
            # This whole logic doesn't seem to work which means the
            # alarm sometimes wont play
            # so we are fudging it here
            self.alarm_sound.last_play = time.time()
        else:
            self.log.info('Alarm already playing')

    def switchThrown(self, obj, arg):
        """A switch was thrown"""
        serge.sound.Sounds.play('switch-thrown')

    def sawPlayer(self, obj, arg):
        """The AI saw a player"""
        serge.sound.Sounds.play('surprise')
        self.log.info('Saw player %s, %s' % (obj.mob, obj.mob))


def main(options, current_level=None):
    """Create the main logic"""
    #
    # The screen actor
    s = MainScreen(options, current_level)
    world = serge.engine.CurrentEngine().getWorld('main-screen')
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    #
    world.addActor(s)
    #
    # Screenshots
    if options.screenshot:
        manager.assignBehaviour(None, 
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

