from cocos.layer import Layer
from cocos.sprite import Sprite
from cocos.actions import *

from pyglet.window import key

import os.path

class HelpLayer(Layer):

    is_event_handler = True
    
    def __init__ (self):
        super(HelpLayer, self).__init__()
        self.pages = [
            Sprite ('help1.png', anchor=(0,0)),
            Sprite ('help2.png', anchor=(0,0), position=(0, -480)) ]
        for p in self.pages:
            self.add (p)
        self.cpage = 0
        self.scrolling= False
        
    def enable_scrolling(self):
        self.scrolling = False
        
    def on_key_press (self, symbol, modifier):
        if self.scrolling: return False
        if symbol== key.PAGEDOWN and self.cpage+1<len(self.pages):
            self.scrolling = True
            action = MoveBy((0, +480), 0.25) + CallFunc(self.enable_scrolling)
            for p in self.pages:
                p.do (action)
            self.cpage += 1
            return True
        elif symbol== key.PAGEUP and self.cpage>0:
            self.scrolling = True
            action = MoveBy((0, -480), 0.25) + CallFunc(self.enable_scrolling)
            self.cpage -= 1
            for p in self.pages:
                p.do (action)                
            return True
            
