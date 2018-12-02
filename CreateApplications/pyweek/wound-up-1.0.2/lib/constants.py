'''constants.py - constants anywhere and everywhere, note the format for
constants stored in this file.'''

import string

import pygame
from pygame.locals import *
from pygame.constants import *

# SOUND_EVENT - pygame event type for sound manager.
SOUND_EVENT = USEREVENT + 1

# DISPLAY_CAPTION - The window title or whatever
DISPLAY_CAPTION = 'Wound Up!'
DISPLAY_CAPTION_FLAT = 'Wound Up! (Flat Renderer)'

# ELF_GREETING - A list of sfx for elf greetings.
ELF_GREETING = (
    "sfx/Elf-Free-1.ogg",
    "sfx/Elf-Free-2.ogg",
    "sfx/Elf-Hello-1.ogg",
    "sfx/Elf-Hello-2.ogg",
    "sfx/Elf-Hello-3.ogg",
    "sfx/Elf-HeyThere-1.ogg",
    "sfx/Elf-HeyThere-2.ogg",
    "sfx/Elf-Howdy-1.ogg",
    "sfx/Elf-Howdy-2.ogg",
    "sfx/Elf-Howdy-3.ogg",
)

# ELF_ACK - A list of sfx for elves' acknowledgements.
ELF_ACK = (
    "sfx/Elf-GoGo-1.ogg",
    "sfx/Elf-HereIGo-1.ogg",
    "sfx/Elf-LetsGo-1.ogg",
    "sfx/Elf-LetsGo-2.ogg",
    "sfx/Elf-LetsGo-3.ogg",
    "sfx/Elf-Okay-1.ogg",
    "sfx/Elf-Okay-2.ogg",
    "sfx/Elf-Okay-3.ogg",
    "sfx/Elf-RockAndRoll-1.ogg",
    "sfx/Elf-Roger-1.ogg",
)

# ELF_READY - A list of sfx for elf readiness.
ELF_READY = (
    "sfx/Elf-LetsGo-1.ogg",
    "sfx/Elf-LetsGo-2.ogg",
    "sfx/Elf-LetsGo-3.ogg",
    "sfx/Elf-HereIAm-1.ogg",
    "sfx/Elf-LetsDoIt-1.ogg",
    "sfx/Elf-ReadyForWork-1.ogg",
    "sfx/Elf-ReadyToGo-1.ogg",
    "sfx/Elf-ShowMeWhatToDo-1.ogg",
)

# ELF_CHEER - A list of sfx for elves cheering.
ELF_CHEER = (
    "sfx/Elf-Yippee-1.ogg",
    "sfx/Elf-Yippee-2.ogg",
    "sfx/Elf-Viva-1.ogg",
    "sfx/Elf-OhYeah-1.ogg",
    "sfx/Elf-Hooray-1.ogg",
    "sfx/Elf-Woohoo-1.ogg",
    "sfx/Elf-Woo-1.ogg",
    "sfx/Elf-Woo-2.ogg",
    "sfx/Elf-Yeah-1.ogg",
)

# SCOTT_ELVES_NEEDED - A list of sfx for needing elves.
SCOTT_ELVES_NEEDED = (
    "sfx/Scott-ElvesNeeded-1.ogg",
)

# SCOTT_METAL_NEEDED - A list of sfx for needing metal.
SCOTT_METAL_NEEDED = (
    "sfx/Scott-MetalLow-1.ogg",
)

# SCOTT_RUBBER_NEEDED - A list of sfx for needing rubber.
SCOTT_RUBBER_NEEDED = (
    "sfx/Scott-RubberLow-1.ogg",
    "sfx/Scott-RubberLow-2.ogg",
)

# MUSIC_FILES - A list of filenames for the in-game music.
MUSIC_FILES = [
    "music/Olde Timey.ogg",
    "music/Conflicted.ogg",
    "music/Hand Trolley.ogg",
    "music/Look Busy.ogg",
]

# TITLE_MUSIC - A filename for the music to play when the title screen
# comes up.
TITLE_MUSIC = "music/Gold Rush.ogg"

# ENERGY_COST_GUMBALL - Amount of energy to amass in a gumball machine
# before producing a capsule.
# 
# NB. Energy is conserved through the system and is measured in elf ticks.
ENERGY_COST_GUMBALL = 800

# ENERGY_DECAY_FACTOR - proportion of the spring's stored energy which is
# dissipated each tick. Amount of energy transmitted to the attached devices
# should be mostly independent of this, but a lower factor will store more
# energy in the spring at any given moment, meaning that:
#   * the cogs spin faster
#   * the cogs take longer to adjust to their new speed when the number
#     of elves changes
ENERGY_DECAY_FACTOR = 0.01

# METAL_COST_*, RUBBER_COST_* - Costs of producing various things.
METAL_COST_COG = {1: 50, 3: 100, 5: 150, 7: 200}
METAL_COST_PLATFORM = 50
METAL_COST_LADDER = 100
RUBBER_COST_BELT = 25 # This is cost per distance squared.

# RETHING_DELAY - Number of ticks which elapse between tasks looking for a new,
# nearer elf which could fulfil one of their requests faster than the one
# they've already found (we don't do this every tick because it might be
# expensive)
RETHINK_DELAY = 10

# SPEED_MULTIPLIER - Scaling factor applied to the rate at which the cogs turn.
# This is purely cosmetic and has no impact on the energy economy
SPEED_MULTIPLIER = 0.03

# EFFICIENCY_DECAY_RATE - Loss in factory efficiency for each unit of energy
# which passes through the factory
EFFICIENCY_DECAY_RATE = 0.05

# EFFICIENCY_MINIMUM - Minimum efficiency of a factory
EFFICIENCY_MINIMUM = 5

# POST_VICTORY_PAUSE - Number of ticks to remain on the game screen after
# winning the level
POST_VICTORY_PAUSE = 200

# SCORES_PER_LEVEL - Number of best times which are saved for each level
SCORES_PER_LEVEL = 5

# BEST_TIME_NAME_* - Properties of allowable names for the charts
BEST_TIME_NAME_LENGTH = 4
BEST_TIME_NAME_VALID = set(string.ascii_uppercase + string.digits)

# GAME_TEXT_COLOUR - Colour of the context-sensitive text
GAME_TEXT_COLOUR = (255,255,255)

# OVERLAY_LINE_LENGTH - Maximum number of characters before breaking lines
# displayed in the lower-right overlay
OVERLAY_LINE_LENGTH = 70

# SCOTT_RESOURCE_WARNING_CHECK - Interval after which to check whether
# resources are low (in ticks)
SCOTT_RESOURCE_WARNING_CHECK = 40

# SCOTT_RESOURCE_WARNING_INTERVAL - Minimum interval in ticks between actually
# giving warnings
SCOTT_RESOURCE_WARNING_INTERVAL = 750

# ZOOM_*_DISTANCE - Controls the range of camera zoom
ZOOM_MIN_DISTANCE = 5
ZOOM_MAX_DISTANCE = 15

# SCROLL_MARGIN_SIZE - How close the cursor has to be to the edge of the
# screen to make the level scroll
SCROLL_MARGIN_SIZE = 30

# SCROLL_RATE - How fast the screen scrolls
SCROLL_RATE = 0.4

# LEVELS_PER_PAGE - Number of levels to show per page in the best times and
# level select screens
LEVELS_PER_PAGE = 3
