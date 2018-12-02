'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

try:
    import pygame
    pygame.init()
except:
    print "Install pygame to get sounds/music"

import os.path
import data
import cocos
from menu import MenuScene
from intro import IntroScene
from game import Game
import options, sound

from pyglet import font

font.add_file(data.filepath(os.path.join('fonts','yellow.ttf')))

def main():
    cocos.director.director.init()
    cocos.director.director.window.set_fullscreen(options.getopt ('fullscreen'))
    theGame = Game()
    menu = MenuScene(theGame)
    cocos.director.director.run (IntroScene(menu))

