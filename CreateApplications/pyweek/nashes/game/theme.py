"""Our main visual theme"""

import serge.blocks.themes

W, H = 1024, 768

TILES_WIDE, TILES_HIGH = 40, 30
TILE_WIDTH = 24

#
# Modes
M_PATROLLING = 'patrolling'
M_INVESTIGATING = 'investigating'
M_CHASING = 'chasing'
M_SEARCHING = 'searching'
M_GOING_TO_REST = 'going-to-rest'
M_RESTING = 'resting'
M_FIXING = 'fixing'
M_NONE = 'none'


theme = serge.blocks.themes.Manager()
theme.load({
    'main': ('', {

        # Main properties
        'screen-height': H,
        'screen-width': W,
        'screen-center': (W / 2, H / 2),
        'help-center': (W / 2, H / 2 + 40),
        'screen-title': 'Nashes to Ashes',
        'screen-icon-filename': 'logo.png',
        'screenshot-size': (0, 0, W, H),

        # Mute button
        'mute-button-alpha': 0.4,
        'mute-button-position': (30, 30),
        'pre-stop-pause': 0.5,

        # FPS display
        'fps-x': 50,
        'fps-y': H-30,
        'fps-colour': (255, 255, 0),
        'fps-size': 12,

        # Tile map
        'tile-width': TILE_WIDTH,
        'tile-height': TILE_WIDTH,
        'tiles-wide': TILES_WIDE,
        'tiles-high': TILES_HIGH,
        'tile-position': (W / 2, H / 2),
        'tile-offset': (
            W / 2 - TILES_WIDE / 2 * TILE_WIDTH,
            H / 2 - TILES_HIGH / 2 * TILE_WIDTH
        ),
        'overlay-size': (W, H),

        # Next for speech
        'next-position': (W - 180, 190),
        'next-pulse-duration': 1000.0,
        'next-pulse-on-fraction': 0.8,

        # AI
        'ai-ahead-sight-distance': 10,
        'ai-side-sight-distance': 4,
        'ai-ahead-angle': 35,
        'ai-search-distance': 10,
        'ai-max-search-locations': 4,
        'ai-controllables-distance': 2.5,
        'ai-max-hear-distance': 15,
        'ai-max-tiredness': 50,
        'ai-min-tiredness': 5,
        'ai-speech-colour': (255, 255, 255),
        'ai-speech-size': 12,
        'ai-speech-font': 'DEFAULT',
        'ai-speech-offset': (0, -20),
        'ai-speech-delay': 1000.0,
        'ai-speech-pause': 0.5,

        'ai-timings': {
            M_CHASING: 0.1,
            M_INVESTIGATING: 0.1,
            M_SEARCHING: 0.25,
            M_FIXING: 0.35,
            M_NONE: 0.5,
        },

        # Player
        'player-max-distractions': 3,
        'player-distraction-timer': 3.0,
        'player-distraction-active-timer': 1.5,
        'framerate-per-step-size': 16.0 / 24.0,
        'player-transition-time': 700.0,

        # Camera
        'camera-max-sight-distance': 7,

        # Overlay
        'overlay-line-width': 4,
        'overlay-colours': [
            (0, 255, 0),
            (255, 255, 0),
            (0, 255, 255),
            (255, 0, 255),
            (150, 150, 150),
        ],
        'overlay-position': (
            W / 2,
            H / 2
        ),

        # Music
        'music-fade-out': 5000.0,

        # Doors
        'door-close-time': 10.0,

        # UI
        'ui-position': (W / 2 - 35, 100),
        'ui-face-bg-pos': (35, -30),
        'ui-face-pos': (-420, -30),
        'ui-interaction-pos': (-220, -88),
        'ui-distraction-pos': (-400, 75),
        'ui-bubble-bg-pos': (10, 50),
        'ui-spoken-text-pos': (-200, 15),
        'ui-switch-pos': (230, -80),
        'ui-device-pos': (70, -80),

        # Interaction
        'ui-interaction-colour': (255, 255, 255),
        'ui-interaction-font-size': 30,
        'ui-interaction-font-name': 'DEFAULT',

        # Spoke text
        'ui-spoken-text-colour': (0, 0, 0),
        'ui-spoken-text-font-size': 30,
        'ui-spoken-text-font-name': 'DEFAULT',

        # Distraction
        'ui-distraction-colour': (255, 255, 255),
        'ui-distraction-font-size': 12,
        'ui-distraction-font-name': 'DEFAULT',
        'ui-distraction-items-spacing': -40,
        'ui-distraction-items-pos': (W / 2 - 40, -75),

        # Speech
        'ui-speech-show-for': 5,

        # Sound dropoff
        'sound-dropoff': 200,

        # Debug
        'disable-ais': [],

        # Levels
        'game-levels': [
            # 'test-level-1',
            # 'test-level-2',

            'level-1',
            'level-2',
            'level-3',
            'level-4',
            # 'level-5',
            'level-6',
            'level-7',
            'level-14',
        ],
    }),

    'start-screen': ('main', {
        # Logo and title
        'logo-position': (W/2, 140),
        'title': 'oxygorgon',
        'title-position': (W/2, 300),
        'title-colour': (255, 255, 255, 255),
        'title-font-size': 36,
        # Version text
        'version-position': (W/2, H-10),
        'version-colour': (50, 50, 50),
        'version-font-size': 12,
        # Start button
        'start-position': (W/2, H-120),
        'start-colour': (255, 255, 0, 255),
        'start-font-size': 48,
        'start-font': 'techno',
        # Continue button
        'continue-position': (W/2, H-200),
        'continue-colour': (255, 255, 0, 255),
        'continue-font-size': 52,
        'continue-font': 'techno',
        # Help button
        'help-position': (W-100, H-40),
        'help-colour': (0, 255, 0, 255),
        'help-font-size': 24,
        'help-font': 'techno',
        # Credits button
        'credits-position': (100, H-40),
        'credits-colour': (0, 255, 0, 255),
        'credits-font-size': 24,
        'credits-font': 'techno',
        # Achievements button
        'achievements-position': (W/2, H-40),
        'achievements-colour': (0, 255, 0, 255),
        'achievements-font-size': 24,
        'achievements-font': 'techno',

        # Animation
        'nashes-start-x': W / 2,
        'nashes-end-x': W / 2,
        'nashes-start-y': -50,
        'nashes-end-y': 100,
        'nashes-animation-time': 1000.0,
        'nashes-animation-delay': 0.0,

        'to-start-x': -50,
        'to-end-x': W / 2,
        'to-start-y': 130,
        'to-end-y': 130,
        'to-animation-time': 1750.0,
        'to-animation-delay': 0.0,

        'ashes-start-x': W / 2,
        'ashes-end-x': W / 2,
        'ashes-start-y': H + 50,
        'ashes-end-y': 170,
        'ashes-animation-time': 2250.0,
        'ashes-animation-delay': 0.0,
    }),

    'sub-screen': ('start-screen', {
        # Logo and title
        'logo-position': (W/2, 80),
        'title-position': (W/2+50, 40),
        'title-colour': (255, 255, 255, 255),
        'title-font-size': 36,
        # Back button
        'back-colour': (255, 255, 0, 255),
        'back-font-size': 24,
        'back-font': 'techno',

    }),
    'help-screen': ('sub-screen', {
        # Help text
        'text-position': (W/2, H/2),
        'text-font': 'techno',

    }),
    'credits-screen': ('sub-screen', {
        # Author
        'author-title-colour': (0, 220, 220),
        'author-title-font-size': 24,
        'author-title-position': (W/2, 160),
        'author-colour': (0, 0, 0),
        'author-font-size': 32,
        'author-position': (W/2, 200),
        'url-colour': (255, 0, 0),
        'url-font-size': 14,
        'url-position': (W/2, 220),
        # Music
        'music-title1-colour': (0, 220, 220),
        'music-title1-font-size': 20,
        'music-title1-position': (W/2, 270),
        'music-title2-colour': (0, 220, 220),
        'music-title2-font-size': 18,
        'music-title2-position': (W/2, 290),
        'music-colour': (0, 0, 0),
        'music-font-size': 16,
        'music-position': (W/2, 310),
        # Sound
        'sound-title1-colour': (0, 220, 220),
        'sound-title1-font-size': 20,
        'sound-title1-position': (W/2, 390),
        'sound-title2-colour': (0, 220, 220),
        'sound-title2-font-size': 18,
        'sound-title2-position': (W/2, 410),
        # Cut scene
        'cut-scene-art-colour': (0, 220, 220),
        'cut-scene-art-font-size': 20,
        'cut-scene-art-position': (W/2, 480),
        'cut-scene-art-name-colour': (255, 255, 0),
        'cut-scene-art-name-font-size': 20,
        'cut-scene-art-name-position': (W/2, 505),
        # Built using
        'built-title-colour': (0, 220, 220),
        'built-title-font-size': 20,
        'built-title-position': (W/4, 470),
        'built-colour': (255, 255, 0),
        'built-font-size': 16,
        'built-position': (W/4, 490),
        # Engine
        'engine-title-colour': (0, 220, 220),
        'engine-title-font-size': 20,
        'engine-title-position': (W/4, 530),
        'engine-colour': (255, 255, 0),
        'engine-font-size': 16,
        'engine-position': (W/4, 550),
        # Engine version
        'engine-version-colour': (75, 75, 0),
        'engine-version-font-size': 10,
        'engine-version-position': (W/4, 570),
        # Fonts
        'font-title1-colour': (0, 220, 220),
        'font-title1-font-size': 20,
        'font-title1-position': (W*3/4, 470),
        'font-title2-colour': (0, 220, 220),
        'font-title2-font-size': 18,
        'font-title2-position': (W*3/4, 490),
        'font-colour': (255, 255, 0),
        'font-font-size': 16,
        'font-position': (W*3/4, 510),
        #
        'back-position': (100, H-40),

    }),

    'achievements': ('main', {
        # Properties of the achievements system
        'banner-duration': 5,
        'banner-position': (175, 525),
        'banner-size': (300, 50),
        'banner-backcolour': (0, 0, 0, 50),
        'banner-font-colour': (255, 255, 0, 255),
        'banner-name-size': 14,
        'banner-description-size': 8,
        'banner-name-position': (-100, -18),
        'banner-description-position': (-100, 0),
        'banner-font-name': 'DEFAULT',
        'banner-graphic-position': (-125, 0),

        'time-colour': (255, 255, 255, 100),
        'time-size': 10,
        'time-position': (-100, 24),

        'logo-position': (400, 50),
        'screen-background-sprite': None,
        'screen-background-position': (400, 300),
        'grid-size': (2, 5),
        'grid-width': 800,
        'grid-height': 400,
        'grid-position': (400, 320),

        'back-colour': (255, 255, 255, 255),
        'back-font-size': 20,
        'back-font-name': 'DEFAULT',
        'back-position': (400, 560),
        'back-sound': 'click',
    }),

    'cut-scene-screen': ('sub-screen', {
        'text-colour': (255, 255, 255),
        'text-size': 32,
        'text-font': 'cut-scene',
        'text-appear-rate': 10,
        'text-delay-time': 200,
        'text-pos': (60, 60),

        'next-position': (W - 100, H - 100),
        'next-pulse-duration': 1000.0,
        'next-pulse-on-fraction': 0.8,

        'initial-delay': 2000.0,
        'post-delay': 1000.0,
        'screens': [
            ('cs-1', 'As the bombs fell @and the sky boiled with\nthe hatred of man'),
            ('cs-2', 'Great cities @splintered and fractured'),
            ('cs-3', 'The summer of our existence @turned to fall'),
            ('cs-4', 'Civilisation @@@a fading @@@distant @@@memory'),
            ('cs-5', 'Life\n@@@extinguished'),
        ],

        'strangelove-text-pos': (60, H - 130),
        'strangelove-text-font': 'strangelove',
        'strangelove': [
            ('cs-6', 'And zis iz what vill happen if you don\'t get\nget ze Doomsday devices from ze Russians!'),
            ('cs-7', "Zhat dingbat General Ripper haz launched ze nuclear\nmissile at Russia to trigger ze all-out war"),
            ('cs-8', "But ze Russians invented a Doomsday device\nthat vill detect ze nuclear explosion and blow up\nze freeking world"),
            ('cs-9', "It'z too late to ztop Ripper's missile zo you'll\nhave to recover ze Doomsday devices"),
            ('cs-10', "Fortunately all ze devices are ztored in\nze Vaziani military base and ve happen to our agents,\nze Nash twins, over there right now"),
            ('cs-11', "Twins! Zhere are almost like one person.\nWho would have thought it? It iz almost like a\ncunning ruize to meet a specific game theme!"),
            ('cs-12', "Go to ze base now and get zhose devices before\nze world dissolves into a steaming heap of rubble!"),

        ],
    }),

    'closing-cut-scene': ('sub-screen', {
        'congrats-position': (W/2, H / 2),
        'congrats-colour': (255, 255, 255, 255),
        'congrats-font-size': 52,
        'congrats-font': 'cut-scene',

        'thanks-position': (W/2, H / 2 + 150),
        'thanks-colour': (255, 255, 255, 255),
        'thanks-font-size': 32,
        'thanks-font': 'cut-scene',

        'back-position': (W - 100, H-40),

    }),

    'level-select-screen': ('sub-screen', {

        'back-position': (W - 100, H-40),

        'level-colour': (255, 255, 255),
        'highlight-colour': (255, 255, 0),
        'level-font': 'techno',
        'level-size': 23,
        'level-x': W / 2,
        'level-y': 200,
        'level-dy': 50,


    }),

    '__default__': 'main',

    'base-level': ('main', {
        'level-name': 'unknown name',

        'start-instructions': [
            ],
        'success-instructions': [
            'You did it!\nLet\'s go to ze next one!'
            ],
        'failure-instructions': [
            'Ack! You didn\'t get the Doomsday device\nHow you gonna ztop ze apocalypse baby?\nTry again.',
            ],
        'failure-captured-instructions': [
            'Dratz! One of ze tvins waz captured!\nBetter try again.'
            ],

    }),

    'level-1': ('base-level', {
        'level-name': 'Switcher two',

        'start-instructions': [
            'Velcome to Vaziani. You need\nto get ze Doomsday devize',
            'It is in zee red room over\nzere. Zee it?'
            'You control zee Nash tvins.\nLetz go!'
            ],

    }),

    'level-2': ('base-level', {
        'level-name': 'Driven to distraction',


        'start-instructions': [
            'In zis part you vill need to diztract ze guards',
            'Press D to drop ze fire cracker.\nYou only get three of zem.\nSo be careful!',
            'D for Distract. Geddit?',
            ],
    }),

    'level-3': ('base-level', {
        'level-name': 'Under pressure',
        'start-instructions': [
            'You are own your own on zis one.\nI don\'t know what ze heck is going on!',
            ],
        'failure-instructions': [
            'You have to get ze Doomsday devize before\nyou leave! Or you wont save the vorld!',
            ],
    }),

    'level-4': ('base-level', {
        'level-name': 'Fixer upper',

    }),

    'level-5': ('base-level', {
        'level-name': 'Keep on running',

        'success-instructions': [
            'That\'t is! You saved the world',
        ],
    }),

    'level-6': ('base-level', {
        'level-name': 'Buying time',
    }),

    'level-7': ('base-level', {
        'level-name': 'Fixing to leave me',
    }),

    'level-8': ('base-level', {

    }),

    'level-9': ('base-level', {

    }),

    'level-10': ('base-level', {

    }),

    'level-11': ('base-level', {

    }),

    'level-12': ('base-level', {

    }),

    'level-13': ('base-level', {

    }),

    'level-14': ('base-level', {
        'level-name': 'Do not hang around',
    }),

})

G = theme.getProperty
