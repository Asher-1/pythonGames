#! /usr/bin/env python
import os, pyglet

pyglet.resource.path.append(os.path.join(os.path.dirname(__file__), "data"))
pyglet.resource.reindex()
del os, pyglet

from gamelib import main
main.main()
