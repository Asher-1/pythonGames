#!/usr/bin/env python
    
#----------------------------------------------------------------------
# test.py
# Dave Reed
# 02/27/2011
#----------------------------------------------------------------------

from GladeWindow import *

import sys
import pygame
import gobject
import gtk


#----------------------------------------------------------------------

class Test(GladeWindow):

    #----------------------------------------------------------------------

    def __init__(self):

        ''' '''
        
        self.init()

    #----------------------------------------------------------------------

    def init(self):

        filename = 'gtkpygame.glade'

        widget_list = [
            'window1',
            'vbox1',
            'area_51',
            ]

        handlers = [
            ]

        top_window = 'window1'
        GladeWindow.__init__(self, filename, top_window, widget_list, handlers)


        WINX = 400
        WINY = 200
        
        area = self.widgets['area_51']
        area.set_size_request(WINX, WINY)
        area.set_app_paintable(True)
        area.realize()
        os.putenv('SDL_WINDOWID', str(area.window.xid))
        gtk.gdk.flush()
        
        pygame.init()
        pygame.display.set_mode((WINX, WINY), 0, 0)
        screen = pygame.display.get_surface()

        image_surface = pygame.image.load('../test/images/greenship.png')
        screen.blit(image_surface, (0, 0))

        gobject.idle_add(pygame.display.update)



#----------------------------------------------------------------------

def main(argv):

    w = Test()
    w.show()

    gtk.main()

#----------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv)
