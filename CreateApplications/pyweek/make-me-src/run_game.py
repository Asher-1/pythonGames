#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

#import sys
#if sys.platform == 'win32':
#    sys.stderr = open('stderr.txt', 'w')

import pyglet
pyglet.options['debug_gl'] = False

pyglet.resource.path = [
    'res', 
    'res/anims', 
    'res/tiles',
    'res/water_tiles',
    'res/dark_tiles',
    'res/fixed_lights',
    'res/effects',
    'res/pickups',
    'res/backgrounds',
    'res/distant',
    'res/menu',
    'res/music',
    'res/sounds',
    'res/fonts'
]
pyglet.resource.reindex()

import gamelib

gamelib.main()
