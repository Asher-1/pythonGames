from __future__ import division, print_function, unicode_literals

import pyglet
from pyglet import resource

from pyglet.media import Player, Source, SourceGroup

#Sounds
_sound_dict = {
    'mowing' : resource.media('mowing_loop.ogg', streaming=False),
    'mowing_idle' : resource.media('mowing_idle.ogg', streaming=False),
    'player_death' : resource.media('mowing_slowdown.ogg', streaming=False),
    'player_hit' : resource.media('player_hit.ogg', streaming=False),
    'enemy_fire' : resource.media('enemy_fire.ogg', streaming=False),
    'victory' : resource.media('victory.ogg', streaming=False),
    'big_victory' : resource.media('big_victory.ogg', streaming=False),
    'failure' : resource.media('failure.ogg', streaming=False),
    'menu_move' : resource.media('menu_move.ogg', streaming=False),
    'menu_select' : resource.media('menu_select.ogg', streaming=False),
    'time_countdown' : resource.media('time_countdown.ogg', streaming=False),
}

# Music
# Store only the filenames because we shouldn't load the entire song in memory
_music_dict = {
    'menu': 'menu.ogg',
    'gameplay': 'gameplay.ogg',
    'boss': 'boss.ogg',
}

sound_on = True
music_on = True

_looping = {}

# key -> Bool
_pending = {}

_music_player = None
_current_music = None

def init_loop(key):
    """Prepares a loop for playback.

    Sounds that use this method will be handled differently from sounds
    that are fired and forgot about.
    """
    if key in _looping:
        remove_loop(key)

    source = _sound_dict[key]
    group = SourceGroup(source.audio_format, None)
    group.loop = True
    group.queue(source)

    player = Player()
    player.queue(group)
    _looping[key] = player

def play_sound(key):
    """Plays a sound with the given key.

    If the given key was passed as a loop to init_loop, the loop will be
    played. Otherwise, the sound will be played only once.
    """
    _pending[key] = True

def pause_loop(key):
    """Pauses a sound loop with the given key."""
    _pending[key] = False

def remove_loop(key):
    _looping[key].delete()
    del _looping[key]

def toggle_sound():
    global sound_on  # Required to assign to globals
    sound_on = not sound_on
    # WONTFIX: playing loops should be handled here, but oh well

def play_music(key, restart=False):
    global _current_music, _music_player

    if not music_on:
        return

    if _current_music is not None and _current_music == key:
        if not _music_player.playing and not restart:
            _music_player.play()
            return
        elif not restart:
            return

    # Pause the currently playing song
    if _music_player is not None:
        _music_player.pause()

    source = resource.media(_music_dict[key])
    group = SourceGroup(source.audio_format, None)
    group.loop = True
    group.queue(source)

    _music_player = Player()
    _music_player.queue(group)

    # Whee more hardcoding
    _music_player.volume = 0.4 if key == 'menu' else 1.0
    _music_player.play()
    _current_music = key

def pause_music():
    if _music_player.playing:
        _music_player.pause()

def toggle_music(key):
    global music_on
    music_on = not music_on

    if music_on:
        play_music(key, True)
    else:
        pause_music()

def tick():
    if sound_on:
        # Handle any pending actions
        for key in _pending.iterkeys():
            # Handle sounds that are designed to loop differently
            if key in _looping:
                play = _pending[key]
                loop = _looping[key]

                if play and not loop.playing:
                    loop.play()
                elif not play and loop.playing:
                    loop.pause()

            # Otherwise, just get the sound and play it
            else:
                player = _sound_dict[key].play()

    # Clear the list of all pending actions
    _pending.clear()
