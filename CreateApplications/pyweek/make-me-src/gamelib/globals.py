#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import pyglet

game = None
window = None
sound = True
music = True

flower_total = 0
coin_total = 0

keys = pyglet.window.key.KeyStateHandler()
