import pgzero.runner
import game.mainscreen
from game.settings import SETTINGS as S
from game import options


WIDTH = S['screen-width']
HEIGHT = S['screen-height']

TITLE = S['screen-title']

# a color used to draw things
MAIN_COLOR = 'yellow'


if __name__ == '__main__':
    pgzero.runner.main(__file__)


opt = options.read_options()
main_screen = game.mainscreen.MainScreen(opt)


def draw():
    """Main draw loop"""
    screen.fill((100, 100, 100))
    main_screen.draw(screen.surface)


def update(dt):
    """Main update loop"""
    main_screen.update(dt)


def on_mouse_up(pos, button):
    """Main handler for mouse events"""
    if button == mouse.LEFT:
        main_screen.on_mouse_up(pos, button)


def on_key_up(key):
    """Main handler for key presses"""
    main_screen.on_key_up(key)