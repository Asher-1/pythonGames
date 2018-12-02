CAPTION = u"Heads and Tales"
TICK_RATE = 60.0
WINDOW_ASPECT = (16, 10)
DEBUG = False

RATINGS = ('speed', 'power', 'vitality', 'mystery')
ATTRIBUTES = ('legs', 'arms', 'hands', 'heads', 'beaks',
              'jaws', 'coils', 'tails', 'horns', 'eyes',
              'sparks', 'tendrils', 'spikes', 'fins')
STATS = RATINGS + ATTRIBUTES

DELAY_MAX = 1000
BASE_SPEED = 10

MONSTER_SCALE = 2000.0

TEAM_OVERLAP = 0.75
TEAM_HEIGHT_OFFSET = 150 # This does less than we'd like it to

DEFAULT_LOOT_CHANCE = 0.2

APP_NAME = 'SE14'

PATH_STEP_LENGTH = 15.0
PATH_UNSTEP_LENGTH = 10.0
PATH_WIDTH = 8.0
LOCATION_SIZE = 100.0
PLAYER_SIZE = 100.0
BEZIER_STEP_LENGTH = 15.0
BEZIER_CURVINESS = 10.0

DEFAULT_FONT_NAME = 'Knewave'

HP_GAUGE_SPEED = 5
FADE_RATE = 0.04

MAP_REPLACEMENTS = {
    'tower2': 'tower1',
    'tower3': 'tower1',
    'act4': 'act1',
    'finale': 'tower1',
    }

MESSAGE_TIME = 150

BATTLE_MUSIC = 'music/Mistake the Getaway.mp3'
MAP_MUSIC = 'music/Sneaky Snitch.mp3'
LAB_MUSIC = 'music/Power Restored.mp3'
TITLE_MUSIC = 'music/Split In Synapse.mp3'
SPEED = 4.0
BATTLE_SPEED = 100
HP_GAUGE_SPEED = 2 * BATTLE_SPEED / 100
BATTLE_MESSAGE_SPEED = 100 * BATTLE_SPEED / 100
BATTLE_ATB_SPEED = 5 * BATTLE_SPEED / 100
ESCAPE_TEXT = u'Press escape again to return to menu...'
