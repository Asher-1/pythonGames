import pyglet
from pyglet.gl import *

from gamewindow import GameWindow
from transitions import ScriptedTransition
import script
from glsetup import *
import sys, os
import audio

def main():
    """ Main Entry point. Create a window and set the resource dir
    """
    print ">>> Genome Hero starting up <<<"
    pyglet.options['debug_gl'] = False
    if os.name == "posix":
        pyglet.options['audio'] = ('openal', 'silent')

    window = GameWindow(width=1024, height=768, vsync=False, resizable=True)
    window.set_caption("Genome Hero")
    window.set_fullscreen(True)
    gl_init(window.width, window.height)

    print pyglet.options
    
    pyglet.clock.schedule_interval(audio.update, 1.0/60.0)
    ## Put the menu state on the stack
    window.push_state(ScriptedTransition, script=script.intro, script_name="intro")
    
    #set3D(window)

    pyglet.app.run()
    

