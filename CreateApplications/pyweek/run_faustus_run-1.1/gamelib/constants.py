"""gamelib.constants -- constant global values used throughout

"""


## Main #######################################################################

#: Debug flag enabled by running test_game.py instead of run_game.py.
DEBUG = False

#: Caption in window title bar in windowed mode.
CAPTION = u'Run, Faustus, Run!'

#: Number of times to try to tick the model per second.
TICK_RATE = 60.0

#: Minimum number of frames per second before lowering the model tick rate.
MIN_FPS = 10.0

#: Name of the config directory, should be fairly unique.
CONFIG_NAME = 'SE.Poliwag'

#: Default values for config parameters.
CONFIG_DEFAULTS = {
    'fullscreen' : True,
    'profile' : False,
    'start_scene' : 'gamelib.menu.MainMenuScene',
    'state' : None,
    'music' : True,
    'sound' : True,
    }


## Rendering ##################################################################

WINDOW_ASPECT = (16, 9)

WORLD_HEIGHT = 1000.0

FLOOR_WIDTH = 30


## World Generation ###########################################################

FLOOR_LOW = 100

FLOOR_HIGH = 500


## Gameplay

EXPIRE_DISTANCE = 2000 # destroy objects which fall this far behind the player
EXPIRE_HEIGHT = 4000 # destroy objects which exceed this height
EXPIRE_DEPTH = -750 # or fall below this height

UNSTUN_TIME = 15 # after emerging from stunned state, ticks until can be stunned again

JUMP_INITIAL_TIME = 15
JUMP_BOOST = 5

DEMON_HEIGHT = 800
DEMON_STARTING_POS = 2000
CATERPILLAR_SPACING = 8
MAX_ENERGY = 2000
PARALLAX_FACTOR = 3000

## Interface ##################################################################

DEFAULT_FONT = 'Stanislav'
