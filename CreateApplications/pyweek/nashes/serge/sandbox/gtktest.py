import os

import gobject
import gtk
import pygame

WINX = 400
WINY = 200

window = gtk.Window()
window.connect('delete-event', gtk.main_quit)
window.set_resizable(False)
area = gtk.DrawingArea()
area.set_app_paintable(True)
area.set_size_request(WINX, WINY)
window.add(area)
area.realize()

# Force SDL to write on our drawing area
os.putenv('SDL_WINDOWID', str(area.window.xid))

# We need to flush the XLib event loop otherwise we can't
# access the XWindow which set_mode() requires
gtk.gdk.flush()

pygame.init()
pygame.display.set_mode((WINX, WINY), 0, 0)
screen = pygame.display.get_surface()

image_surface = pygame.image.load('../test/images/greenship.png')
screen.blit(image_surface, (0, 0))

gobject.idle_add(pygame.display.update)

window.show_all()

gtk.main()
