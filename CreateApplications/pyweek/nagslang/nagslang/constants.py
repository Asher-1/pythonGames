SCREEN = (800, 600)
FPS = 40
FONT = 'DejaVuSans.ttf'
FONT_SIZE = 16

DEFAULTS = dict(
    debug=False,
    shapes=False,

    sound=True,
    music=True,
    # Debug starting position:
    area=None,
    point=None,
)

# Sound constants
FREQ = 44100   # same as audio CD
BITSIZE = -16  # unsigned 16 bit
CHANNELS = 2   # 1 == mono, 2 == stereo
BUFFER = 1024  # audio buffer size in no. of samples
DEFAULT_SOUND_VOLUME = 1.0  # sound volume
DEFAULT_MUSIC_VOLUME = 0.3  # music volume

COLLISION_TYPE_OTHER = 0
COLLISION_TYPE_PLAYER = 1
COLLISION_TYPE_WALL = 2
COLLISION_TYPE_SWITCH = 3
COLLISION_TYPE_FURNITURE = 4
COLLISION_TYPE_ENEMY = 5
COLLISION_TYPE_DOOR = 6
COLLISION_TYPE_PROJECTILE = 7
COLLISION_TYPE_WEREWOLF_ATTACK = 8
COLLISION_TYPE_SHEEP = 9
COLLISION_TYPE_SHEEP_PEN = 10

SWITCH_PUSHERS = [COLLISION_TYPE_PLAYER, COLLISION_TYPE_FURNITURE]

CALLBACK_COLLIDERS = [
    # Collisions between the player and shapes with these collision types will
    # fire callbacks on the game object associated with the shape.
    COLLISION_TYPE_SWITCH,
    COLLISION_TYPE_FURNITURE,
    COLLISION_TYPE_ENEMY,
    COLLISION_TYPE_DOOR,
    COLLISION_TYPE_SHEEP,
]

NON_GAME_OBJECT_COLLIDERS = [
    # These collision types are excluded from action checks, etc.
    COLLISION_TYPE_WALL,
    COLLISION_TYPE_PROJECTILE,
    COLLISION_TYPE_WEREWOLF_ATTACK,
]

ZORDER_FLOOR = 0
ZORDER_LOW = 1
ZORDER_MID = 2
ZORDER_HIGH = 3

WEREWOLF_SOAK_FACTOR = 5
PROTAGONIST_HEALTH_MAX_LEVEL = 200
PROTAGONIST_HEALTH_MIN_LEVEL = 0

BULLET_DAMAGE = 25
CLAW_DAMAGE = 5
ACID_DAMAGE = 7

BULLET_SPEED = 1000
ACID_SPEED = 300

CMD_TOGGLE_FORM = 'toggle_form'
CMD_ACTION = 'action'
