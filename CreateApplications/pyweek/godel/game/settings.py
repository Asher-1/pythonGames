"""Settings for the game"""

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

SCREEN_CENTER_X = SCREEN_WIDTH / 2
SCREEN_CENTER_Y = SCREEN_HEIGHT / 2


SETTINGS = {
    # Version
    'version': '0.3',

    # Items relating to the screen layout
    'screen-title': 'The Gödel Sentence',
    'screen-width': SCREEN_WIDTH,
    'screen-height': SCREEN_HEIGHT,

    # Logo properties
    'logo-y-offset': -200,

    # Items relating to the callouts
    'in-game-callout': {
        'callout-initial-x': -SCREEN_CENTER_X,
        'callout-initial-y': SCREEN_CENTER_Y,
        'callout-final-x': SCREEN_CENTER_X - 200,
        'callout-final-y': SCREEN_CENTER_Y,
        'callout-animation-time': 1,
        'callout-animation-tween-in': 'decelerate',
        'callout-animation-tween-out': 'accelerate',
        'callout-button-x': 140,
        'callout-button-y': -75,
        'callout-text-pos': (140, 0),
        'callout-font': 'computerfont',
        'callout-colour': 'white',
        'callout-width': 350,
        'callout-title-font': 'computerfont',
        'callout-title-colour': 'white',
        'callout-title-pos': (140, -100),
    },
    'end-game-callout': {
        'callout-initial-x': SCREEN_WIDTH + SCREEN_CENTER_X,
        'callout-initial-y': SCREEN_CENTER_Y,
        'callout-final-x': SCREEN_CENTER_X + 200,
        'callout-final-y': SCREEN_CENTER_Y,
        'callout-animation-time': 1,
        'callout-animation-tween-in': 'decelerate',
        'callout-animation-tween-out': 'accelerate',
        'callout-button-x': -140,
        'callout-button-y': -95,
        'callout-text-pos': (-130, 80),
        'callout-font': 'computerfont',
        'callout-colour': 'white',
        'callout-width': 350,
    },

    'out-of-game-callout': {
        'callout-initial-x': SCREEN_WIDTH + SCREEN_CENTER_X,
        'callout-initial-y': SCREEN_CENTER_Y,
        'callout-final-x': SCREEN_CENTER_X,
        'callout-final-y': SCREEN_CENTER_Y,
        'callout-animation-time': 1,
        'callout-animation-tween-in': 'bounce_end',
        'callout-animation-tween-out': 'bounce_end',
    },

    # The text entry
    'text-entry-icon-pos': (-280, -20),
    'text-entry-name-pos': (-280, 20),
    'text-entry-text-pos': (-220, -20),
    'text-entry-width': 650,
    'text-entry-height': 80,
    'text-entry-icon-scale': 0.4,

    # Scrolled region
    'scrolled-scroll-width': 40,
    'scrolled-scroll-height': 60,
    'scrolled-scroll-offset': 100,
    'scrolled-scroll-colour': (255, 255, 0),

    # VDU
    'vdu-size': (794, 410),
    'vdu-position': (600, 510),
    'vdu-colour': (20, 225, 25),

    # End of game VDU
    'end-vdu-size': (794, 510),
    'end-vdu-position': (600, 510),
    'end-vdu-colour': (20, 225, 25),

    # Vessel
    'vessel-size': (60, 600),
    'vessel-position': (14, 0),
    'vessel-bar-offset': (95, 345),
    'vessel-water-colour': (0, 0, 255),
    'vessel-back-colour': (0, 0, 0, 100),

    # Health panels
    'panel-initial-x': 170,
    'panel-initial-y': 34,
    'panel-dx': 170,
    'panel-water-size': (13, 144),
    'panel-water-pos': (149, 40),
    'panel-water-colour': (0, 0, 255),
    'panel-health-size': (92, 26),
    'panel-health-pos': (50, 150),
    'panel-health-colour': (0, 75, 0),
    'panel-button-pos': (157, 217),
    'panel-name-pos': (85, 20),
    'panel-talking-light-pos': (45, 197),
    'panel-light-flash': 0.5,
    'panel-talking-button-pos': (45, 220),
    'panel-drinking-pos': (43, 21),

    # Talking
    'talking-time-per-letter': 0.03,
    'drinking-talk-probability': 0.2,

    # Clock
    'clock-pos': (70, 107),
    'clock-tween': 'bounce_end',
    'clock-tween-time': 1,
    'clock-wait-time': 60 / 12 - 1,

    # Tabbed display
    'tabbed-buttons': [
        'dialog',
        'people',
        'health',
        'water',
        'food',
    ],
    'tabbed-initial-x': 280,
    'tabbed-initial-y': 750,
    'tabbed-delta-x': 130,

    # Initial reserves
    'reserves-water': 70,
    'reserves-food': 65,
    'reserves-amount-to-give': 20,
    'reserves-water-ratio': 0.2,

    # People properties
    'person-a-properties': {
        'eats': 1.0,
        'drinks': 20,
        'health': 45,
        'water': 10,
        'thirst_decrease': 14,
        'drink_increase': 5,
        'eat_increase': 0,
        'hunger_decrease': 0,
    },
    'person-b-properties': {
        'eats': 1.5,
        'drinks': 25,
        'health': 55,
        'water': 30,
        'thirst_decrease': 15,
        'drink_increase': 5,
        'eat_increase': 0,
        'hunger_decrease': 0,
    },
    'person-c-properties': {
        'eats': 0.5,
        'drinks': 15,
        'health': 50,
        'water': 25,
        'thirst_decrease': 18,
        'drink_increase': 5,
        'eat_increase': 0,
        'hunger_decrease': 0,
    },
    'person-d-properties': {
        'eats': 1.4,
        'drinks': 15,
        'health': 35,
        'water': 15,
        'thirst_decrease': 12,
        'drink_increase': 5,
        'eat_increase': 0,
        'hunger_decrease': 0,
    },
    'person-e-properties': {
        'eats': 1.8,
        'drinks': 20,
        'health': 60,
        'water': 5,
        'thirst_decrease': 13,
        'drink_increase': 5,
        'eat_increase': 0,
        'hunger_decrease': 0,
    },

    # Peoples names
    'names': {
        'person_a': 'Amber',
        'person_b': 'Brock',
        'person_c': 'Crystal',
        'person_d': 'Dax',
        'person_e': 'Eva',
    },

    # Drinking
    'drinking-individual-delay': 2,
    'drinking-start-delay': 2,
    'drinking-end-delay': 1,

    # Alternate properties for testing
    'person-a-alt-properties': {
        'eats': 1.0,
        'drinks': 20,
        'health': 4,
        'water': 0,
        'thirst_decrease': 14,
        'drink_increase': 5,
    },
    'person-b-alt-properties': {
        'eats': 1.5,
        'drinks': 25,
        'health': 4,
        'water': 0,
        'thirst_decrease': 15,
        'drink_increase': 5,
    },
    'person-c-alt-properties': {
        'eats': 0.5,
        'drinks': 15,
        'health': 50,
        'water': 25,
        'thirst_decrease': 18,
        'drink_increase': 5,
    },
    'person-d-alt-properties': {
        'eats': 1.4,
        'drinks': 15,
        'health': 0,
        'water': 0,
        'thirst_decrease': 12,
        'drink_increase': 5,
    },
    'person-e-alt-properties': {
        'eats': 1.8,
        'drinks': 20,
        'health': 60,
        'water': 5,
        'thirst_decrease': 13,
        'drink_increase': 5,
    },
}
