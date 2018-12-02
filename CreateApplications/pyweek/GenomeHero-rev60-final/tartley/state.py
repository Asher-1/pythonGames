################################################################################
#   Copyright 2011 Chris Statzer and David Reichard                            #
#                                                                              #
#   Licensed under the Apache License, Version 2.0 (the "License");            #
#   you may not use this file except in compliance with the License            #
#   You may obtain a copy of the License at                                    #
#                                                                              #
#       http://www.apache.org/licenses/LICENSE-2.0                             #
#                                                                              #
#   Unless required by applicable law or agreed to in writing, software        #
#   distributed under the License is distributed on an "AS IS" BASIS,          #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
#   See the License for the specific language governing permissions and        #
#   limitations under the License.                                             #
################################################################################

import pyglet
from batchmanager import batch
import audio
import sys

class State(object):
    def __init__(self, window, name="default", *args, **kwargs):
        window.push_handlers(self)
        self.window = window
        self.name = name
        self.batch = batch.get_batch(self.name)
        
    def on_lose_focus(self):
        return pyglet.event.EVENT_HANDLED

    def on_gain_focus(self):
        return pyglet.event.EVENT_HANDLED
    
    def on_regain_focus(self):
        batch.set_batch(self.name)
        return pyglet.event.EVENT_HANDLED
        
    def on_push_state(self, state):
        batch.set_batch(self.name)
        return pyglet.event.EVENT_HANDLED
    
    def on_pop_state(self, state):
        batch.clear(self.name)
        batch.set_batch('default')
        self.window.pop_handlers()
        return pyglet.event.EVENT_HANDLED
    
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()
        return pyglet.event.EVENT_HANDLED
    
    def on_key_release(self, symbol, modifiers):
        return pyglet.event.EVENT_HANDLED
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        return pyglet.event.EVENT_HANDLED
    
    def on_mouse_enter(self, x, y):
        return pyglet.event.EVENT_HANDLED
    
    def on_mouse_leave(self, x, y):
        return pyglet.event.EVENT_HANDLED
    
    def on_mouse_motion(self, x, y, dx, dy):
        return pyglet.event.EVENT_HANDLED
    
    def on_mouse_press(self, x, y, button, modifiers):
        return pyglet.event.EVENT_HANDLED
    
    def on_mouse_release(self, x, y, button, modifiers):
        return pyglet.event.EVENT_HANDLED
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        return pyglet.event.EVENT_HANDLED
    
    def on_text_motion(self, motion):
        return pyglet.event.EVENT_HANDLED
    
    def on_text_motion_select(self, motion):
        return pyglet.event.EVENT_HANDLED
        
    def on_deactivate(self):
        audio.pause_music()
        if sys.platform == "win32":
            pass
        elif self.window.fullscreen:
            self.window.set_fullscreen(False)
        if self.name == "game":
            self.pause()
        return pyglet.event.EVENT_HANDLED
            
    def on_activate(self):
        audio.resume_music()
        return pyglet.event.EVENT_HANDLED

        


