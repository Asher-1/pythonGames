'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import data

from GameWindow import GameWindow

def main():
    game = GameWindow(800,600, "Lawn Fairy")
    game.main_loop()

