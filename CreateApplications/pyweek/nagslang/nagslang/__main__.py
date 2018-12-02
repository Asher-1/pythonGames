import sys

import pygame
import pygame.locals as pgl

from nagslang.options import parse_args
from nagslang.constants import SCREEN
from nagslang.engine import Engine
from nagslang.sound import sound
from nagslang.resources import Resources


def main():
    '''Launch the nagslang'''
    parse_args(sys.argv)
    pygame.display.init()
    pygame.font.init()

    # set_icon needs to be called before set_mode on some platforms, but we
    # can't use convert_alpha until we've created a window with set_mode
    r = Resources('data')
    r.CONVERT_ALPHA = False
    pygame.display.set_icon(r.get_image('werewolf-sonata_24.png',
                                        basedir='icons'))

    pygame.display.set_mode(SCREEN, pgl.SWSURFACE | pgl.RESIZABLE)
    pygame.display.set_caption('Werewolf Sonata')
    sound.init()

    screen = pygame.display.get_surface()
    engine = Engine(screen)
    engine.run()
