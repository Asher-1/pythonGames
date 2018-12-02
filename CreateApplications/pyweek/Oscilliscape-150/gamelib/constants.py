"""Constant definitions.

This file is loaded during the program initialisation before the main module is
imported. Consequently, this file must not import any other modules, or those
modules will be initialised before the main module, which means that the DEBUG
value may not have been set correctly.

This module is intended to be imported with 'from ... import *' semantics but
it does not provide an __all__ specification.

"""

import math

#: Enable debug features. Should never be changed manually but is set to True
#: automatically when running `test_game.py`.
DEBUG = False

#: Version string. This may be represented somewhere in-game. It is also read
#: by `setup.py` as part of its versioning features.
VERSION = u"devel"

#: The directory (relative to the top level) wherein all the resources for the
#: game are stored, probably subdivided into types of resources. See `data.py`.
DATA_DIR = "data"

#: The name of the game used in locating the saved settings directory. Its best
#: not to have any spaces in this name.
CONFIG_NAME = "Oscilliscape"

#: The caption that appears at the top of the window. Obviously this is only
#: visible in windowed mode.
CAPTION = u"Oscilliscape"

#: The "top-level" tick rate; the maximum number of times per second that the
#: controller will call its tick method.
TICK_RATE = 60.0

#: The "top-level" update rate; the maximum number of times per second that the
#: controller will call its update method.
UPDATE_RATE = 60.0

SECONDS_TO_CROSS_GAMESPACE = 8

SIZE_OF_GAMESPACE_X = 852
SIZE_OF_GAMESPACE_Y = 480

PLAYER_OFFFSET_FROM_RIGHT_SCREEN_BOUND = 50

WIDTH_OF_TERRAIN_SLICE = SIZE_OF_GAMESPACE_X/2

# line colors (r, g, b, a)
LEVEL1_PATH_COLOR = (1, 0.5, 0, 0.9)
LEVEL2_PATH_COLOR = (0.5, 0, 0.5, 0.9)
LEVEL3_PATH_COLOR = (0.9, 0.9, 0.9, 0.9)
LEVEL4_PATH_COLOR = (0.2, 0.2, 0.8, 0.9)

# amplitude and frequency adjust flags
( INCREASE, CONSTANT, DECREASE ) = range(3)

# how many points of shield are drained per second of contact with terrain
SHIELD_TERRAIN_DRAIN_RATE = 10

# the default time in seconds for each level to last
DEFAULT_LEVEL_TIME = 90 

#Object of Interest types
TYPE_PLAYER_SHIP = "Player"
TYPE_HOSTILE_SHIP = "Hostile"
TYPE_DEBRIS = "Debris"
TYPE_TERRAIN = "Terrain"

##Ship Movement Characteristics
SHIP_SPEED = 1.0
# The maximum amplitude of the ship's path, 1 being the top of the screen
MAX_AMPLITUDE = 1
# the minimum amplitude of the ships path, 0 being perfectly horizontal
MIN_AMPLITUDE = .1
# how far the ship can move per tick
MAX_AMPLITUDE_VELOCITY = 0.1

MAX_FREQUENCY = 3*math.pi
MIN_FREQUENCY = .25*math.pi
MAX_FREQUENCY_VELOCITY = .5*math.pi

MAX_SHIELDS = 2000
STARTING_SHIELDS = 500
SHIELD_CHARGE_RATE = 50/math.pi
COLLISION_COOLDOW = 1

