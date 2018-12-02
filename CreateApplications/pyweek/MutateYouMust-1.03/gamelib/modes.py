'''
Created on 11.09.2011

Different application modes
'''

import data
from gui import MainMenuGui

class Mode:
    _app = None
    
    def __init__(self, application):
        self._app = application
        
    def enter(self):
        self.register_handlers()
    
    def leave(self):
        self.unregister_handlers()
    
    def update(self, gameTime, deltaTime):
        pass
    
    def register_handlers(self):
        self._app.push_handlers(self)
    
    def unregister_handlers(self):
        self._app.remove_handlers(self)
    
    def on_mouse_press(self, x, y, button, modifiers):
        pass
    
    def on_mouse_motion(self, x, y, dx, dy, buttons, modifiers):
        pass
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass

    def on_key_press(self, symbol, modifiers):
        pass
    
    def on_key_release(self, symbol, modifiers):
        pass
    

from effects import AlienThingy 
from math2d import Vector2

class MainMenu(Mode):
    _Gui = None
    
    alieny = None
    
    def __init__(self, application):
        Mode.__init__(self, application)
        self._Gui = MainMenuGui(self._app)
        self._Gui.hide()
        
    def enter(self):
        Mode.enter(self)
        self._Gui.show() 
        self._app.window.set_background(data.load_texture("gui_menu.jpg"))
        self.alieny = AlienThingy()
        self.alieny.set_position(Vector2(95.0, 195.0))
        self.alieny.start()

    def leave(self):
        Mode.leave(self)
        self._Gui.hide()
        self._app.window.set_background(data.load_texture("background.jpg"))
        self.alieny.delete()
        self.alieny = None
        
    def activate_credits(self):
        self._Gui.on_credits()
    
    def update(self, gameTime, deltaTime):
        Mode.update(self, gameTime, deltaTime)
        self.alieny.update(gameTime, deltaTime)
        