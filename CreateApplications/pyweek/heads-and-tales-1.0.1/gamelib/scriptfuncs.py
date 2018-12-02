from gamelib import app
from gamelib.team import Team
from gamelib.data import monsters
from gamelib.monsterparts import *
from gamelib import sound

import random # used in some scripts

def locscript(name):
    def _decorator(func):
        locscript.index[name] = func
        return func
    return _decorator
locscript.index = {}

def mapscript():
    def _decorator(func):
        locscript.index['__init__'] = func
        return func
    return _decorator

def dialogue(dialogue=None, speaker=None, side=None):
    return ('dialogue', dialogue, speaker, side)

def endcutscene():
    return ('endcutscene',)

def battle(team=None, reward=None):
    return ('battle', team, reward)

def enterlab(newmap=None, newnode=None):
    return ('enterlab', newmap, newnode)

def teleport(game, locname):
    game.teleport(locname)

def win():
    return ('win',)

def changemap(mapname, locname):
    return ('changemap', mapname, locname)

def setflag(game, flagname, value=True):
    game.set_plot_flag(flagname, value)
    
def flag(game, flagname):
    return game.get_plot_flag(flagname)
    
def first(game, flagname):
    if game.get_plot_flag(flagname):
        return False
    game.set_plot_flag(flagname, True)
    return True

def setportrait(name, side):
    app.control.scene.cutscene.set_portrait(name, side)

def changeimage(location, image):
    app.control.scene.changeimage(location, image)

def help(message, delay):
    return ('help', message, delay)
