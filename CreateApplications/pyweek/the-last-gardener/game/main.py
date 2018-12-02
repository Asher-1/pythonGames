from __future__ import division, print_function, unicode_literals

import argparse
import pyglet

from game import Game

def main():
    parser = argparse.ArgumentParser(
        description='The Last Gardener: '
                    'A PyWeek 21 Entry by Jjp137 and LegoBricker')

    parser.add_argument("--disable-vsync",
                        help='Disables vertical sync.',
                        action="store_true")
    parser.add_argument("--show-fps",
                        help='Make the game display the current FPS.',
                        action="store_true")
    args = parser.parse_args()

    vsync = not args.disable_vsync

    game = Game(vsync, args.show_fps)
    game.start()
