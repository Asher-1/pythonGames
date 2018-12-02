"""Common elements"""

import pygame
import os
import sys

import serge.engine
import serge.common
import serge.blocks.scores
import serge.blocks.settings

log = serge.common.getLogger('Game')
from theme import G

version = '0.1.1'


SETTINGS = serge.blocks.settings.Settings('nashes')
SETTINGS.defaults.last_level = None
SETTINGS.defaults.saw_tutorial = False
SETTINGS.defaults.saw_distraction_tutorial = False
for level in G('game-levels'):
    setattr(SETTINGS.defaults, level, False)
setattr(SETTINGS.defaults, G('game-levels')[0], True)
SETTINGS.safeRestoreValues()

#
# Events
#
# Put events here with names E_MY_EVENT
# and they will be registered automatically
#
# E_GAME_STARTED = 'game-started'
E_INTERACTION_AVAILABLE = 'interaction-available'
E_NO_INTERACTIONS = 'no-interactions'
E_PLAYER_CAPTURED = 'player-captured'
E_PLAYER_EXITED = 'played-exited'
E_PLAYER_GOT_DEVICE = 'player-got-device'
E_PLAYER_FLIPPED_SWITCH = 'player-flipped-switch'
E_PLAYER_DROPPED_DISTRACTION = 'player-dropped-distraction'
E_ALARM_DETECTED = 'alarm-detected'
E_SWITCH_THROW = 'switch-throw'
E_AI_SAW_PLAYER = 'ai-saw-player'

# Communication of level outcome
O_NEXT_LEVEL = 'next-level'
O_SAME_LEVEL = 'same-level'
O_QUIT = 'quit-game'
#
LEVEL_OUTCOME = None

CURRENT_LEVEL = None
