#!/usr/bin/env python
    
#----------------------------------------------------------------------
# build.py
# Dave Reed
# 02/27/2011
#----------------------------------------------------------------------

import sys

from GladeWindow import *

#----------------------------------------------------------------------

class Build(GladeWindow):

    #----------------------------------------------------------------------

    def __init__(self):

        ''' '''
        
        self.init()

    #----------------------------------------------------------------------

    def init(self):

        filename = '/home/paul/workspace/svn/games/serge/builder/builder.glade'

        widget_list = [
            'main',
            'vbox1',
            'btn_save',
            'button14',
            'button4',
            'note_main',
            'vbox2',
            'vbox5',
            'scrolledwindow2',
            'view_worlds',
            'button1',
            'button2',
            'label9',
            'vbox6',
            'view_layer',
            'button12',
            'button13',
            'label11',
            'label1',
            'vbox3',
            'scrolledwindow1',
            'view_sprites',
            'button5',
            'button6',
            'button7',
            'label2',
            'label7',
            'label3',
            'label8',
            'label4',
            'vbox4',
            'scrolledwindow3',
            'view_layers',
            'button9',
            'button10',
            'label5',
            'label10',
            'entry_image_location',
            'button8',
            'label6',
            ]

        handlers = [
            'gtk_main_quit',
            'clickSave',
            'clickOpen',
            'doDebug',
            'changedWorld',
            'clickAddWorld',
            'clickDeleteWorld',
            'clickAddZone',
            'clickDeleteZone',
            'clickAddSprite',
            'clickDeleteSprite',
            'clickSelectSpriteFile',
            'clickAddLayer',
            'clickDeleteLayer',
            'changedImageLocation',
            'clickSelectImageLocation',
            ]

        top_window = 'main'
        GladeWindow.__init__(self, filename, top_window, widget_list, handlers)
    #----------------------------------------------------------------------

    def gtk_main_quit(self, *args):
        pass
    #----------------------------------------------------------------------

    def gtk_main_quit(self, *args):
        pass
    #----------------------------------------------------------------------

    def clickAddWorld(self, *args):
        pass

    #----------------------------------------------------------------------

    def clickDeleteWorld(self, *args):
        pass

    #----------------------------------------------------------------------

    def clickRenameWorld(self, *args):
        pass
    #----------------------------------------------------------------------

    def doDebug(self, *args):
        pass
    #----------------------------------------------------------------------

    def addSprite(self, *args):
        pass

    #----------------------------------------------------------------------

    def deleteSprite(self, *args):
        pass
    #----------------------------------------------------------------------

    def clickAddSprite(self, *args):
        pass

    #----------------------------------------------------------------------

    def clickDeleteSprite(self, *args):
        pass
    #----------------------------------------------------------------------

    def clickSelectSpriteFile(self, *args):
        pass
    #----------------------------------------------------------------------

    def clickSelectImageLocation(self, *args):
        pass
    #----------------------------------------------------------------------

    def clickedSave(self, *args):
        pass
    #----------------------------------------------------------------------

    def clickAddLayer(self, *args):
        pass

    #----------------------------------------------------------------------

    def clickDeleteLayer(self, *args):
        pass
    #----------------------------------------------------------------------

    def clickAddZone(self, *args):
        pass

    #----------------------------------------------------------------------

    def clickDeleteZone(self, *args):
        pass
    #----------------------------------------------------------------------

    def clickSave(self, *args):
        pass

    #----------------------------------------------------------------------

    def clickOpen(self, *args):
        pass
    #----------------------------------------------------------------------

    def changedImageLocation(self, *args):
        pass
    #----------------------------------------------------------------------

    def changedWorld(self, *args):
        pass















    


#----------------------------------------------------------------------

def main(argv):

    w = Build()
    w.show()
    gtk.main()

#----------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv)
