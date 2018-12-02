"""gamelib.__main__ -- gamelib package entry point

"""

import pyglet

from gamelib import app
from gamelib import cmdline
from gamelib import config


## Command Line ###############################################################

with cmdline.mutex():

    @cmdline.option('-w', '--windowed')
    def windowed():
        'run the game in windowed mode'
        app.config.fullscreen = False

    @cmdline.option('-f', '--fullscreen')
    def fullscreen():
        'run the game in fullscreen mode'
        app.config.fullscreen = True

@cmdline.option('-m', '--mute')
def mute():
    'do not play sound or music'
    app.config.music = False
    app.config.sound = False

@cmdline.option('--no-music')
def no_music():
    'do not play music'
    app.config.music = False

@cmdline.option('-p', '--profile', debug=True)
def profile():
    'enable the runtime profiler'
    app.config.profile = True

@cmdline.option('-s', '--start-scene', debug=True)
def start_scene(scene):
    'start the game in the scene SCENE'
    app.config.start_scene = scene

@cmdline.option('--debug-gl', debug=True)
def debug_gl():
    'enable OpenGL debugging options'
    pyglet.options['debug_gl_trace'] = True
    pyglet.options['debug_gl_trace_args'] = True


## Main #######################################################################

def main():

    # Create pyglet resource index.
    pyglet.resource.path = ['@gamelib.data']
    pyglet.resource.reindex()
    pyglet.resource.add_font('Stanislav.ttf')

    # Create the runtime config object.
    app.config = config.Config()

    # Parse command line arguments.
    cmdline.parse()

    # Create the runtime control object.
    from gamelib import control
    app.control = control.Control()

    # Run the game (with optional profiler).
    if app.config.profile:
        import cProfile
        import datetime
        output_format = 'profile-%Y.%m.%d-%H:%M:%S'
        output_file = datetime.datetime.now().strftime(output_format)
        cProfile.runctx('pyglet.app.run()', globals(), None, output_file)
    else:
        pyglet.app.run()

if __name__ == '__main__':
    main()
