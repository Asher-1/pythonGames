'''main.py - entry point to the game, assumes that is has the necessary
environment already configured.'''

import sys
import optparse

import menu
import display

def main():
    parser = optparse.OptionParser()
    parser.add_option("-r", "--resolution", dest="res", default=None, type="string", help="display in resolution WxH", metavar="WxH")
    parser.add_option("-w", "--windowed", dest="win", action="store_true", default=False, help="use windowed mode (fullscreen is default)")
    parser.add_option("--no-particles", dest="nopart", action="store_true", default=False, help="don't display particle effects")
    opts, args = parser.parse_args()

    if opts.res is not None:
        res = map(int, opts.res.split("x"))
    else:
        res = None
    gl_options = {"noparticles": opts.nopart}
    renderer_options = {"res": res, "win": opts.win, "gl": gl_options}
    options = {"renderer": renderer_options}
    
    menu.Menu(display.gl_render.GLRenderer, options).run()
