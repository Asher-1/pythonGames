"""Objects in the game"""

import os
import pygame
import random
import serge.common
import serge.events
import serge.actor
import serge.sound
import serge.engine
import serge.visual
from serge.simplevecs import Vec2d
import serge.blocks.actors
import serge.blocks.sounds
import serge.blocks.animations
import serge.blocks.textgenerator
import serge.blocks.timers
import common
import grid
from theme import G, theme


class Grid(serge.actor.MountableActor):
    """"The overall grid"""


class GameObject(serge.actor.MountableActor):
    """An actor in the game"""

    visual_sprite_name = None
    normal_layer = 'objects'
    pixel_relaxation = 1.0

    def __init__(self, name, obj, level_grid):
        """Initialise the camera"""
        super(GameObject, self).__init__(self.__class__.__name__, name)
        #
        self.obj = obj
        self.level_grid = level_grid
        self.type = obj.type
        self.looking_direction = 0
        self.last_step_size = 0
        #
        if self.visual_sprite_name:
            self.setSpriteName(self.visual_sprite_name)

    def addedToWorld(self, world):
        """Added to the world"""
        super(GameObject, self).addedToWorld(world)
        #
        self.event_pump = world.findActorByName('behaviours')

    def repositionBasedOnCell(self, immediate=False):
        """Reposition ourselves in visual coords"""
        px, py = self.obj.getVisualCoords(self.obj.cx, self.obj.cy)
        #
        # Under-relax for smooth movement of mobs
        nx = px * self.pixel_relaxation + self.x * (1.0 - self.pixel_relaxation)
        ny = py * self.pixel_relaxation + self.y * (1.0 - self.pixel_relaxation)
        #
        delta = Vec2d(nx, ny) - Vec2d(self.x, self.y)
        self.looking_direction = delta.angle_degrees
        self.obj.looking_direction = self.looking_direction
        #
        if immediate:
            self.moveTo(px, py, override_lock=True)
        else:
            self.moveTo(nx, ny, override_lock=True)
        self.last_step_size = delta.length


class Camera(GameObject):
    """A camera"""

    visual_sprite_name = 'camera-on'
    normal_layer = 'foreground'

    def __init__(self, *args, **kw):
        """Initialise the camera"""
        super(Camera, self).__init__(*args, **kw)
        #
        self.setAngle(self.obj.angle)

    def updateActor(self, interval, world):
        """Update the door"""
        if self.obj.is_on:
            self.setSpriteName('camera-on')
            self.setAngle(self.obj.angle)
        else:
            self.setSpriteName('camera-off')
            self.setAngle(self.obj.angle)


class PressurePad(GameObject):
    """Pressure pad"""

    def updateActor(self, interval, world):
        """Update the door"""
        if self.obj.is_on:
            self.setSpriteName('ui-pad-on')
        else:
            self.setSpriteName('ui-pad-off')


class Controller(GameObject):
    """"Controller"""

    def updateActor(self, interval, world):
        """Update the door"""
        if self.obj.visible:
            if self.obj.is_on:
                self.setSpriteName('ui-switch-on')
            else:
                self.setSpriteName('ui-switch-off')
        else:
            self.visible = False


class Door(GameObject):
    """"Door"""

    visual_sprite_name = 'door-opening'

    def __init__(self, name, obj, *args, **kw):
        """Initialise the door"""
        super(Door, self).__init__(name, obj, *args, **kw)
        #
        self.open = obj.is_open
        self.locked = obj.is_locked
        #
        if self.locked:
            self.setSpriteName('door-locking')
        else:
            self.setSpriteName('door-closing')
        #
        self.visual.running = False
        self.visual.setCell(self.visual.getNumberOfCells() - 1)
        self.setAngle(self.obj.angle)

    def addedToWorld(self, world):
        """Added tot he world"""
        super(Door, self).addedToWorld(world)
        #
        self.door_closer = serge.blocks.timers.Timer(
            'timer', 'door-closer',
            G('door-close-time'),
            callback=self.closeDoor,
            started=False,
        )
        world.addActor(self.door_closer)

    def closeDoor(self):
        """Close the door"""
        self.obj.is_open = False

    def updateActor(self, interval, world):
        """Update the door"""
        sound = False
        if self.obj.is_open and not self.open:
            self.setSpriteName('door-opening')
            self.open = True
            self.setAngle(self.obj.angle)
            self.visual.running = True
            sound = True
            self.door_closer.resetAndStartTimer()
        elif not self.obj.is_open and self.open:
            if self.obj.is_locked:
                self.setSpriteName('door-locking')
                self.locked = True
            else:
                self.setSpriteName('door-closing')
                self.locked = False
            self.open = False
            self.setAngle(self.obj.angle)
            self.visual.running = True
            sound = True
        elif self.obj.is_locked and not self.locked:
            if self.open:
                self.setSpriteName('door-locking')
                sound = True
            else:
                self.setSpriteName('door-locking-closed')
            self.locked = True
            self.open = False
            self.setAngle(self.obj.angle)
        elif not self.obj.is_locked and self.locked:
            self.setSpriteName('door-unlocking-closed')
            self.locked = False
            self.setAngle(self.obj.angle)
        #
        if sound:
            serge.sound.Sounds.play('door-open')



class MOB(GameObject):
    """A mobile actor on the grid"""

    normal_layer = 'mobs'
    pixel_relaxation = 0.2
    framerate_per_step_size = G('framerate-per-step-size')
    speech_delay = G('ai-speech-delay')

    def __init__(self, *args, **kw):
        """Initialise the mob"""
        super(MOB, self).__init__(*args, **kw)
        #
        self.speaking = serge.blocks.actors.StringText(
            'speech-bubble', '%s-bubble' % self.name, 'Speaking',
            colour=G('ai-speech-colour'),
            font_name=G('ai-speech-font'),
            font_size=G('ai-speech-size'),
        )
        self.speaking.setLayerName('objects')
        self.speaking.visible = False
        self.mountActor(self.speaking, G('ai-speech-offset'), rotate_with_actor=False)
        #
        self.text = serge.blocks.textgenerator.TextGenerator()
        self.text.addExamplesFromFile(os.path.join('dialog', 'ai-speech.txt'))
        self.text_visible_counter = 0

    def addedToWorld(self, world):
        """Added to the world"""
        super(MOB, self).addedToWorld(world)
        #
        self.state_machine = world.findActorByName('state-machine')
        self.repositionBasedOnCell(immediate=True)

    def canMoveRelative(self, dx, dy):
        """Return True if we can move to a cell"""
        return self.canMoveTo(self.obj.cx + dx, self.obj.cy + dy)

    def canMoveTo(self, cx, cy):
        """Return True if we can move to a cell"""
        return self.level_grid.isWalkable(cx, cy, self)

    def moveRelative(self, dx, dy):
        """Move relative distance"""
        self.obj.cx += dx
        self.obj.cy += dy
        self.repositionBasedOnCell()

    def updateActor(self, interval, world):
        """Update the actor"""
        super(MOB, self).updateActor(interval, world)
        #
        # Keep doing movement
        self.repositionBasedOnCell()
        self.visual.framerate = self.framerate_per_step_size * self.last_step_size
        #
        self.setAngle(-self.looking_direction)


class AI(MOB):
    """An AI person"""

    visual_sprite_name = 'ai-walking'

    def addedToWorld(self, world):
        """Added to the world"""
        super(AI, self).addedToWorld(world)
        #
        self.linkEvent(serge.events.E_LEFT_CLICK, self.clickedOn)
        self.debug_view = False
        #
        self.ai_timer = serge.blocks.timers.Timer(
            'ai-timer', '%s-timer' % self.name,
            self.obj.getAITickTime(),
            callback=self.doAITick,
        )
        world.addActor(self.ai_timer)
        #
        self.ai_pauser = serge.blocks.timers.Timer(
            'ai-pause-timer', '%s-pauser' % self.name,
            G('ai-speech-pause'),
            callback=self.unpauseAI,
            started=False,
        )
        world.addActor(self.ai_pauser)

    def doAITick(self):
        """Tick of the AI"""
        self.obj.tickAI()
        self.repositionBasedOnCell()
        self.ai_timer.least_time = self.obj.getAITickTime()

    def clickedOn(self, obj, arg):
        """Clicked on the MOB"""
        self.debug_view = not self.debug_view

    def updateActor(self, interval, world):
        """Update the actor"""
        super(AI, self).updateActor(interval, world)
        #
        if self.obj.speech_hint and not self.speaking.visible:
            self.showSpeech()
        #
        if self.debug_view:
            self.speaking.visible = True
            self.speaking.value = '%s: Mode %s, tiredness %s' % (
                self.name, self.obj.ai.mode, self.obj.ai.tiredness
            )
        elif self.speaking.visible:
            self.text_visible_counter -= interval
            if self.text_visible_counter <= 0:
                self.speaking.visible = False

    def showSpeech(self):
        """Show some speech"""
        old_mode, new_mode = self.obj.speech_hint
        name = 'mode-%s-%s' % (old_mode.lower(), new_mode.lower())
        try:
            sentence = self.text.getRandomSentence('@{%s}@' % name)
        except serge.blocks.textgenerator.NameNotFound:
            self.log.info('No text for transition "%s"' % name)
        else:
            self.log.info('Text for transition "%s": %s' % (name, sentence))
            self.speaking.value = sentence
            self.speaking.visible = True
            self.text_visible_counter = self.speech_delay
        #
        self.obj.speech_hint = None
        #
        # And then pause for a little bit
        self.ai_timer.stopTimer()
        self.ai_pauser.startTimer()
        self._old_pr, self.pixel_relaxation = self.pixel_relaxation, 0.0 # stop use dead

    def unpauseAI(self):
        """Unpause the AI"""
        self.ai_timer.startTimer()
        self.ai_pauser.resetTimer()
        self.pixel_relaxation = self._old_pr


class Player(MOB):
    """Represents the player object"""

    visual_sprite_name = 'player-walking'
    pixel_relaxation = 0.8

    def addedToWorld(self, world):
        """Added to the world"""
        super(Player, self).addedToWorld(world)
        #
        self.keyboard = serge.engine.CurrentEngine().getKeyboard()
        self.interactable = None
        self.event_pump = world.findActorByName('behaviours')
        self.distractions = G('player-max-distractions')
        self.transitioning = False
        self.is_captured = False
        self.has_exited = False
        #
        devices = self.level_grid.getObjectsOfType('doomsday-device')
        self.sound = serge.blocks.sounds.SoundTexture('sound', 'sound')
        device_sound = serge.sound.Sounds.getItem('near-device')
        device_sound.set_volume(0.0)
        device_sound.play(-1)
        #
        for device in devices:
            self.log.info('Adding positional sound of device')
            self.sound.addPositionalSound(
                serge.blocks.sounds.LocationalSound(
                    device_sound,
                    (device.px, device.py),
                    G('sound-dropoff'),
                )
            )
        self.sound.setListener(self)
        # world.addActor(self.sound)

    def updateActor(self, interval, world):
        """Update the player"""
        super(Player, self).updateActor(interval, world)
        #
        if self.obj.is_captured:
            self.event_pump.processEvent((common.E_PLAYER_CAPTURED, self))
            self.is_captured = True
        #
        if not self.is_captured:
            if self.transitioning:
                self.setSpriteName('player-waiting-transition')
            elif self.has_exited:
                pass
            else:
                if self.obj.active:
                    self.setSpriteName('player-walking')
                    #
                    if self.keyboard.isClicked(pygame.K_d) and self.distractions > 0:
                        self.dropDistraction(world)
                    #
                    dx = dy = 0
                    if self.keyboard.isClicked(pygame.K_LEFT):
                        dx = -1
                    if self.keyboard.isClicked(pygame.K_RIGHT):
                        dx = 1
                    if self.keyboard.isClicked(pygame.K_UP):
                        dy = -1
                    if self.keyboard.isClicked(pygame.K_DOWN):
                        dy = 1
                    if self.keyboard.isClicked(pygame.K_SPACE):
                        if self.interactable:
                            self.interactable.interactWith()
                    #
                    if (dx or dy) and self.canMoveRelative(dx, dy):
                        self.log.debug('Trying to move %s, %s' % (dx, dy))
                        self.moveRelative(dx, dy)
                        serge.sound.Sounds.play('footstep')
                    #
                    self.checkForInteractions()
                else:
                    self.setSpriteName('player-sitting')
                #
                if self.keyboard.isClicked(pygame.K_TAB):
                    self.state_machine.add_generator('transition', self.beginTransition(world))

            #
            self.checkForDetections()
        #
        if not self.transitioning and self.obj.has_exited and not self.has_exited:
            self.log.info('Detected exit for %s' % self.name)
            other_player = self.getOtherPlayer(world)
            if not other_player.has_exited:
                self.state_machine.add_generator('transition', other_player.beginTransition(world))
                self.state_machine.add_generator('transition', self.beginTransition(world))

    def showSpeech(self, sentence):
        """Show some speech"""
        self.speaking.value = sentence
        self.speaking.visible = True
        self.text_visible_counter = self.speech_delay

    def getOtherPlayer(self, world):
        """Return the other player"""
        other_players = [player for player in world.findActorsByTag('Player') if player != self]
        other_player = other_players[0]
        return other_player

    def beginTransition(self, world):
        """Transition from one state to another"""
        self.log.info('Begining transition for %s' % self.name)
        #
        # Find the other actor
        other_player = self.getOtherPlayer(world)
        #
        if other_player.has_exited:
            serge.sound.Sounds.play('cancel')
            self.log.info('Cannot transition - other player %s has exited' % other_player.name)
            return
        #
        self.transitioning = True
        hat = serge.blocks.animations.AnimatedActor('hat', 'hat')
        hat.setSpriteName('yellow-hat' if self.obj.active else 'black-hat')
        hat.setLayerName('hats')
        hat.moveTo(self.x, self.y)
        world.addActor(hat)
        #
        animation1 = hat.addAnimation(
            serge.blocks.animations.MovementTweenAnimation(
                hat, Vec2d(hat.x, hat.y), Vec2d(other_player.x, other_player.y),
                duration=G('player-transition-time'),
                function=serge.blocks.animations.TweenAnimation.sinInOut,
            ),
            'move-the-hat'
        )
        animation2 = hat.addAnimation(
            serge.blocks.animations.TweenAnimation(
                hat, 'setAngle', 0, 360,
                duration=G('player-transition-time') / 2.0,
                function=serge.blocks.animations.TweenAnimation.sinInOut,
                repeat=True, is_method=True,
            ),
            'rotate-the-hat'
        )
        #
        if self.obj.active:
            serge.sound.Sounds.play('transition-swish')
        #
        while not animation1.complete:
            yield 0
        #
        world.scheduleActorRemoval(hat)
        self.transitioning = False
        self.obj.active = not self.obj.active
        self.has_exited = self.obj.has_exited

    def checkForInteractions(self):
        """Check if we have possible interactions"""
        for dx, dy in [(-1, 0), (0, -1), (0, 1), (1, 0), (0, 0)]:
            cx, cy = self.obj.cx + dx, self.obj.cy + dy
            obj = self.level_grid.getObjectAt(cx, cy)
            if obj and obj.canBeInteractedWith():
                self.event_pump.processEvent((common.E_INTERACTION_AVAILABLE, obj.getInteraction()))
                self.interactable = obj
                break
        else:
            self.event_pump.processEvent((common.E_NO_INTERACTIONS, None))
            self.interactable = None

    def checkForDetections(self):
        """Check if there are any detections"""
        self.level_grid.checkForDetections(self.obj)

    def dropDistraction(self, world):
        """Create and drop a distraction"""
        self.log.info('Dropping a distraction')
        place = grid.Distraction(self.obj.cx, self.obj.cy)
        new_distraction = Distraction('distraction', place, self.level_grid)
        new_distraction.moveTo(self.x, self.y)
        new_distraction.setLayerName('objects')
        world.addActor(new_distraction)
        self.distractions -= 1
        #
        self.event_pump.processEvent((common.E_PLAYER_DROPPED_DISTRACTION, self))


class DoomsdayDevice(GameObject):
    """A doomsday device in the level"""

    visual_sprite_name = 'device-on'

    def updateActor(self, interval, world):
        """Update the switch"""
        if self.visible and self.obj.picked_up:
            self.event_pump.processEvent((common.E_PLAYER_GOT_DEVICE, self))
            self.visible = False
            serge.sound.Sounds.play('take')


class DoomsdaySwitch(GameObject):
    """A doomsday switch in the level"""

    visual_sprite_name = 'obj-doomsday-switch'
    turned_off = False

    def updateActor(self, interval, world):
        """Update the switch"""
        if not self.turned_off and self.obj.turned_off:
            self.turned_off = True
            self.setSpriteName('obj-doomsday-switch-off')
            self.event_pump.processEvent((common.E_PLAYER_FLIPPED_SWITCH, self))


class Exit(GameObject):
    """An exit for the level"""

    visual_sprite_name = 'exit'
    ready_to_exit = False

    def addedToWorld(self, world):
        """Added to the world"""
        super(Exit, self).addedToWorld(world)
        #
        self.setAngle(self.obj.angle)

    def updateActor(self, interval, world):
        """Update the exit"""
        if self.ready_to_exit:
            self.visual.running = True
        else:
            self.visual.running = False
        #
        if self.obj.used:
            self.event_pump.processEvent((common.E_PLAYER_EXITED, self))
            self.obj.used = False
            self.active = False



class Distraction(GameObject):
    """A distraction"""

    def addedToWorld(self, world):
        """Added to the world"""
        self.setSpriteName('cracker-lit')
        self.activate_fuse = serge.blocks.timers.Timer('timer', 'distraction', G('player-distraction-timer'),
            callback=self.timerExpired, one_shot=True)
        self.deactivate_fuse = serge.blocks.timers.Timer('timer', 'distraction', G('player-distraction-active-timer'),
            callback=self.deactivateExpired, one_shot=True, started=False)
        #
        world.addActor(self.activate_fuse)
        world.addActor(self.deactivate_fuse)
        serge.sound.Sounds.play('fuse')

    def timerExpired(self):
        """The timer expired"""
        self.setSpriteName('ui-distractor-on')
        self.setSpriteName('cracker-explode')
        self.deactivate_fuse.startTimer()
        serge.sound.Sounds.play('cracker')
        for ai in self.level_grid.getAIWithin(self.obj, G('ai-max-hear-distance')):
            ai.mobDetected(self.obj)

    def deactivateExpired(self):
        """Fuse should be deactivated"""


class ControlOverlay(serge.actor.MountableActor):
    """An overlay to show the controllers"""

    def __init__(self, tag, name, level_grid):
        """Initialise the overlay"""
        super(ControlOverlay, self).__init__(tag, name)
        #
        self.level_grid = level_grid

    def addedToWorld(self, world):
        """Create the overlay"""
        self.createVisual()

    def createVisual(self):
        """Create the overall visual"""
        self.visual = serge.visual.SurfaceDrawing(*G('overlay-size'))
        bg = serge.visual.Sprites.getItem('overlay-background')
        bg.renderTo(0, self.visual.getSurface(), (0, 0))
        #
        # Place objects
        for type_name in ('controller', 'door', 'pressure-mat', 'camera'):
            for obj in self.level_grid.getObjectsOfType(type_name):
                px, py = obj.getVisualCoords(obj.cx - 0.5, obj.cy - 0.5)
                sprite = serge.visual.Sprites.getItem('obj-overlay-%s' % type_name)
                sprite.renderTo(0, self.visual.getSurface(), (px, py))
        #
        # For all controllers - draw the lines
        for idx, controller in enumerate(self.level_grid.getObjectsOfType('controller')):
            if controller.draw_line:
                for obj in controller.controls:
                    self.log.debug('Overlay line from %s to %s (%s, %s)' % (
                        controller.name, obj.name, obj.cx, obj.cy
                    ))
                    if controller.is_on:
                        if obj.type == 'camera':
                            self.drawCamera(obj)
                        self.drawLine(controller, obj, idx)
                    else:
                        self.drawLine(controller, obj, -1)
        #
        # Draw disconnected cameras
        for camera in self.level_grid.getObjectsOfType('camera'):
            if not camera.controlled_by and camera.is_on:
                self.drawCamera(camera)
        #
        # For pads - draw the lines
        for idx, mat in enumerate(self.level_grid.getObjectsOfType('pressure-mat')):
            controller = mat.locks
            if mat.draw_line:
                if controller.is_on:
                    self.drawLine(mat, controller, idx)
                else:
                    self.drawLine(mat, controller, -1)
        #
        if common.OPTIONS.cheat:
            pygame.image.save(self.visual.getSurface(), os.path.join('sandbox', 'overlay.png'))

    def drawLine(self, from_obj, to_obj, index):
        """Draw a control line from an object and to another object"""
        sx = sy = G('tile-width')
        fx, fy = from_obj.getVisualCoords(from_obj.cx, from_obj.cy)
        tx, ty = to_obj.getVisualCoords(to_obj.cx, to_obj.cy)
        #
        # Alternate approach
        if index % 2 == 0:
            point_list = [(fx, fy), (tx, fy), (tx, ty),]
        else:
            point_list = [(fx, fy), (fx, ty), (tx, ty),]
        #
        pygame.draw.lines(
            self.visual.getSurface(),
            G('overlay-colours')[index],
            False,
            point_list,
            G('overlay-line-width'),
        )

    def drawCamera(self, camera):
        """Draw the visible area of a camera"""
        for cx, cy in self.level_grid.iterCellLocations():
            point = grid.Point(cx, cy)
            if camera.canDetect(point, self.level_grid):
                self.log.debug('Camera %s can see %s, %s' % (
                    camera.name, cx, cy
                ))
                px, py = point.getVisualCoords(cx, cy)
                w = G('tile-width')
                rect = (px - w / 2, py - w / 2, w, w)
                colour = G('overlay-colours')[0] + (100, )
                pygame.draw.rect(self.visual.getSurface(), colour, rect)
