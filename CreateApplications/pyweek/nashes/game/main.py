"""Main module for the game"""

import pygame
import os
import time

import serge.engine
import serge.world
import serge.actor
import serge.zone
import serge.render
import serge.sound 
import serge.events
import serge.blocks.achievements
try:
    import serge.builder.builder
except ImportError:
    pass

import serge.visual
import serge.blocks.actors
import serge.blocks.utils
import serge.blocks.onlinescores

import common
import mainscreen
import startscreen
import helpscreen
import creditsscreen
import cutscene
import closingcutscene
import levelselect

from theme import G, theme


def registerSounds():
    """Register the sounds to use"""
    serge.sound.Sounds.setPath('sound')
    r = serge.sound.Sounds.registerItem
    r('click', 'back-click.wav')
    #
    r('transition-swish', 'transition-swish.wav')
    r('alarm', 'alarm.wav')
    r('switch-thrown', 'switch-thrown.wav')
    r('door-open', 'door-open.wav')
    r('footstep', 'footstep.wav')
    r('take', 'take.wav')
    r('cracker', 'cracker.wav')
    r('fuse', 'fuse.wav')
    r('surprise', 'surprise.wav')
    r('captured', 'captured.wav')
    r('success', 'success.wav')
    r('failure', 'failure.wav')
    r('cancel', 'cancel.wav')
    r('forward-click', 'forward-click.wav')
    r('back-click', 'back-click.wav')
    r('overview-on', 'overview-on.wav')
    r('typing', 'typing.wav')
    r('soft-click', 'soft-click.wav')
    r('massive-explosion', 'massive-explosion.ogg')
    r('near-device', 'near-device.ogg')
    r('eerie-ambience', 'eerie-ambience.ogg')

def registerMusic():
    """Register the music to use"""
    serge.sound.Music.setPath('music')
    r = serge.sound.Music.registerItem
    #
    r('start-music', 'start-music.ogg')
    r('cut-scene', 'cut-scene.ogg')


def registerGraphics():
    """Register the graphics to use"""
    serge.visual.Sprites.setPath('graphics')
    r = serge.visual.Sprites.registerItem
    rf = serge.visual.Sprites.registerFromFiles
    rm = serge.visual.Sprites.registerMultipleItems
    rp = serge.visual.Sprites.registerItemsFromPattern
    r('icon', 'icon.png')
    r('logo', 'logo.png')
    r('small-icon', 'icon.png', zoom=0.2)
    r('help-text', 'help-text.png')
    rf('mute-button', 'music-%d.png', 2, zoom=0.5)
    rf('achievement', 'achievement-%d.png', 2)
    #
    rp('obj-.*?.png')
    rp('ui-.*?.png')
    rp('overlay-.*?.png')
    rp('.*?-key.png', zoom=0.3)
    r('sl-face', 'sl-face.png', w=8, h=4, running=True, framerate=48,
      one_direction=True, loop=False)
    r('sl-face-static', 'sl-face-static.png', w=8, h=4, running=True, framerate=24,
      one_direction=True, loop=False)
    #
    r('camera-on', 'camera-on.png', w=8, h=4, running=True, framerate=8, one_direction=True)
    r('camera-off', 'camera-off.png')
    #
    r('ai-walking', 'ai-walking.png', w=8, h=4, running=True, framerate=16, one_direction=True)
    #
    r('player-walking', 'player-walking.png', w=8, h=4, running=True, framerate=16, one_direction=True)
    r('player-sitting', 'player-sitting.png')
    r('player-waiting-transition', 'player-waiting-transition.png')
    r('black-hat', 'black-hat.png')
    r('yellow-hat', 'yellow-hat.png')
    r('help', 'help.png')
    #
    r('nashes', 'nashes.png')
    r('ashes', 'ashes.png')
    r('to', 'to.png')
    r('start-back', 'start-back.png')
    r('main-background', 'main-background.png')
    #
    r('device-on', 'device-on.png', w=8, h=4, running=True, framerate=3, one_direction=True)
    #
    r('door-opening', 'door-opening.png', w=8, h=4, running=True, framerate=24,
      one_direction=True, loop=False)
    r('door-closing', 'door-closing.png', w=8, h=4, running=True, framerate=24,
      one_direction=True, loop=False)
    r('door-locking', 'door-locking.png', w=8, h=4, running=True, framerate=24,
      one_direction=True, loop=False)
    r('door-locking-closed', 'door-locking-closed.png', w=8, h=4, running=True, framerate=24,
      one_direction=True, loop=False)
    r('door-unlocking-closed', 'door-unlocking-closed.png', w=8, h=4, running=True, framerate=24,
      one_direction=True, loop=False)
    #
    r('cracker-lit', 'cracker-lit.png', w=8, h=4, running=True, framerate=16, one_direction=True)
    r('cracker-explode', 'cracker-explode.png', w=8, h=4, running=True, framerate=32, one_direction=True, loop=False)
    #
    r('exit', 'exit.png', w=8, h=4, running=True, framerate=8, one_direction=True, loop=True)
    #
    serge.visual.Sprites.setPath('cutscene')
    rp('cs-.*?.png')
    #
    # Fonts
    serge.visual.Fonts.setPath('fonts')
    serge.visual.Fonts.registerItem('techno', 'TECHC.TTF')
    serge.visual.Fonts.registerItem('cut-scene', 'americandream.ttf')
    serge.visual.Fonts.registerItem('strangelove', 'deutschgothic.ttf')


def registerEvents():
    """Register all the events"""
    broadcaster = serge.events.getEventBroadcaster()
    broadcaster.registerEventsFromModule(common)


def registerAchievements(options):
    """Register the achievements for the game"""
    r = serge.blocks.achievements.initManager('oxygorgon').safeRegisterAchievement
    a = serge.blocks.achievements.Achievement
    r(a('Played the game', 'You played the game at least once', 
        'badge', False, 'play', condition_string=': True'))
    serge.blocks.achievements.addAchievementsWorld(options, theme)
    

def startEngine(options):
    """Start the main engine"""
    engine = serge.engine.Engine(
        width=G('screen-width'), height=G('screen-height'),
        title=G('screen-title'), icon=os.path.join('graphics', G('screen-icon-filename')))
    serge.blocks.utils.createVirtualLayersForEngine(
        engine,
        ['background', 'middleground', 'objects', 'mobs', 'hats',
         'foreground', 'overlay', 'main',
         'ui-back', 'ui', 'ui-front', 'very-front'
         ]
    )
    serge.blocks.utils.createWorldsForEngine(
        engine, [
        'start-screen', 'main-screen', 'credits-screen', 'help-screen',
        'cut-scene-screen', 'closing-cut-scene', 'level-select-screen',
        ]
     )
    #
    engine.setCurrentWorldByName('start-screen' if not options.straight else 'main-screen')
    return engine


def stoppingNow(obj, arg):
    """We are about to stop"""
    #
    # Fade out music and wait for a bit before going away
    serge.sound.Music.fadeout(G('pre-stop-pause')*1000)
    time.sleep(G('pre-stop-pause'))
       

def createHighScores(options):
    """Create the high score table"""
    hs = serge.blocks.onlinescores.HighScoreSystem(
        G('app-url', 'high-score-screen'), secret_user=options.cheat)
    app_name = G('app-name', 'high-score-screen')
    if hs.gameExists(app_name):
        return
    #
    common.log.info('Creating high score table')
    hs.createGame(app_name)
    #
    # Create categories
    # hs.createGameCategory(
    #     app_name,
    #     'CATEGORY_NAME',
    #     'SCORE_NAME',
    #     LOWER_IS_BETTER,
    #     MAX_PLAYER_SCORES
    # )


def main(options, args):
    """Start the engine and the game"""
    #
    # Create the high scores
    if options.high_score:
        createHighScores(options)
    #
    # Create the engine
    engine = startEngine(options)
    engine.linkEvent(serge.events.E_BEFORE_STOP, stoppingNow)
    #
    registerSounds()
    registerMusic()
    registerGraphics()
    registerEvents()
    #
    # Record a movie
    if options.movie:
        serge.blocks.utils.RecordDesktop(options.movie)
    #
    # Change theme settings
    if options.theme:
        theme.updateFromString(options.theme)
    #
    # Muting
    mute = serge.blocks.actors.MuteButton('mute-button', 'ui', alpha=G('mute-button-alpha'))
    serge.blocks.utils.addMuteButtonToWorlds(mute, center_position=G('mute-button-position'))
    #
    if options.musicoff:
        mute.toggleSound()
    #
    # Initialise the main logic
    registerAchievements(options)
    mainscreen.main(options)
    startscreen.main(options)
    helpscreen.main(options)
    creditsscreen.main(options)
    cutscene.main(options)
    closingcutscene.main(options)
    levelselect.main(options)
    #
    if options.debug:
        serge.builder.builder.main(engine, options.framerate)
    else:
        engine.run(options.framerate)
