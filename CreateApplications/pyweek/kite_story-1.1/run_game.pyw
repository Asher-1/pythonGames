#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import sys

if sys.platform == 'win32' and False:
    sys.stderr = sys.stdout = open('errors.txt', 'w')

import pyglet

pyglet.options['debug_gl'] = False

pyglet.resource.path = ('res',)
pyglet.resource.reindex()

import gamelib
gamelib.main()
