#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: sound.py 408 2008-04-20 15:23:01Z aholkner $'

import math
import pyglet
import time

import globals

music_player = pyglet.media.Player()
music_next_time = 0
current_music = None

try:
    import pyglet.media.avbin
    have_avbin = True
except:
    have_avbin = False
    globals.music = False

def set_music(name=None):
    global current_music
    global music_next_time

    if not have_avbin:
        return

    if name == current_music:
        return
    current_music = name

    if not globals.music:
        return

    if not current_music:
        music_player.pause()
        return
    
    music_next_time = time.time() + 4.
    music_player.next()
    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.play()
    music_player.eos_action = 'loop'

def play_music():
    if music_player.playing or not current_music:
        return

    if not have_avbin:
        return

    name = current_music
    music_player.next()
    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.play()
    music_player.eos_action = 'loop'

def stop_music():
    music_player.pause()

music_zones = []
music_tracks = {}

def init_music_zones():
    for line in pyglet.resource.file('music_zones.txt', 'rt'):
        line = line.strip()
        cmd, value = line.split(' ', 1)
        if cmd == 'zone':
            x, y, name = value.split(' ', 2)
            music_zones.append((int(x), int(y), name))
        elif cmd == 'track':
            track, filename = value.split(' ', 1)
            music_tracks[track] = filename
    pyglet.clock.schedule_interval(update_music, 0.5)

def update_music(dt=None, force=False):
    global music_next_time
    player_x = globals.game.player.x
    player_y = globals.game.player.y
    zone = None
    for x, y, name in music_zones:
        if player_x > x and player_y > y:
            zone = name
    if force or time.time() > music_next_time:
        if zone in music_tracks:
            set_music(music_tracks[zone])

sounds = {}

def play(name):
    if not globals.sound:
        return

    if name not in sounds:
        sounds[name] = pyglet.resource.media(name, streaming=False)

    sounds[name].play()

def play_positioned(name, x, y):
    if not globals.sound:
        return

    if name not in sounds:
        sounds[name] = pyglet.resource.media(name, streaming=False)

    player = pyglet.media.ManagedSoundPlayer()
    player.queue(sounds[name])
    player.play()

    dx = x - globals.game.player.x
    dy = y - globals.game.player.y
    dist = math.sqrt(dx * dx + dy * dy)
    player.volume = 1 - dist / globals.window.width / 3

move_player = pyglet.media.Player()
current_move = None

def start_move(name):
    global current_move

    if not globals.sound:
        return

    if current_move == name:
        return

    if name not in sounds:
        sounds[name] = pyglet.resource.media(name, streaming=False)

    move_player.next()
    move_player.queue(sounds[name])
    move_player.play()
    move_player.eos_action = 'loop'
    current_move = name

def stop_move():
    global current_move

    move_player.pause()
    current_move = None
