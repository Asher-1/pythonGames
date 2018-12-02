import optparse
import os

from nagslang.constants import DEFAULTS


class AttrDict(dict):
    '''A dict with attribute access'''
    def __getattr__(self, attr):
        return self[attr]


options = AttrDict()


def parse_args(args):
    '''
    Parse arguments and store them in the options dictionary.

    Note: If you add arguments, you need to add an appropriate default to the
    DEFAULTS dict.
    '''
    options.update(DEFAULTS)

    options.debug = 'DEBUG' in os.environ

    parser = optparse.OptionParser()
    parser.add_option('--no-sound',
                      dest='sound', action='store_false', default=True,
                      help='Disable all sound, including music')

    parser.add_option('--no-music',
                      dest='music', action='store_false', default=True,
                      help='Disable music (but not sound)')

    if options.debug:
        parser.add_option('--area', help='Initial area')
        parser.add_option('--point', help='Initial position x,y')
        parser.add_option('--shapes', help='Show collision shapes',
                          action='store_true', default=options.shapes)

    opts, _ = parser.parse_args(args)

    for k in DEFAULTS:
        if getattr(opts, k, None) is not None:
            options[k] = getattr(opts, k)
