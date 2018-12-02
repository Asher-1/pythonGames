#!/usr/bin/env python
    
#----------------------------------------------------------------------
# actors.py
# Dave Reed
# 02/27/2011
#----------------------------------------------------------------------

import sys

from GladeWindow import *

#----------------------------------------------------------------------

class Actors(GladeWindow):

    #----------------------------------------------------------------------

    def __init__(self):

        ''' '''
        
        self.init()

    #----------------------------------------------------------------------

    def init(self):

        filename = '/home/paul/workspace/svn/games/serge/builder/actors.glade'

        widget_list = [
            'actors',
            'vbox1',
            'vbox2',
            'scrolledwindow1',
            'view_actors',
            'button9',
            'button10',
            'label1',
            ]

        handlers = [
            'clickAddActor',
            'clickDeleteActor',
            ]

        top_window = 'actors'
        GladeWindow.__init__(self, filename, top_window, widget_list, handlers)
    #----------------------------------------------------------------------

    def clickAddActor(self, *args):
        pass

    #----------------------------------------------------------------------

    def clickDeleteActor(self, *args):
        pass


    


#----------------------------------------------------------------------

def main(argv):

    w = Actors()
    w.show()
    gtk.main()

#----------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv)
