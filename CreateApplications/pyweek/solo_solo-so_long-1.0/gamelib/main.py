
from pyglet.gl import *

import pyglet

import cocos
from cocos.director import director

#from game_scene import *
from menu_scene import *

import data

def main():

    pyglet.resource.path.append('data')
    pyglet.resource.reindex()
    font.add_directory('data')

    director.init()
    director.set_depth_test(True)

    s = get_menu_scene()
    director.run (s)

if __name__ == "__main__":
    main()
