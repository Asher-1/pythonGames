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


class GameWindow(pyglet.window.Window):
    def __init__(self, **kwargs):
        pyglet.window.Window.__init__(self, **kwargs)
        self.state_stack = []
        
    def push_state(self, state, *args, **kwargs):
        if self.state_stack:
            self.dispatch_event('on_lose_focus')
        self.state_stack.append(state(self, *args, **kwargs))
        self.dispatch_event('on_push_state', self.state_stack[-1])
        self.dispatch_event('on_gain_focus')
        
    def pop_state(self):
        self.dispatch_event('on_lose_focus')
        self.dispatch_event('on_pop_state', self.state_stack.pop())
        self.dispatch_event('on_regain_focus')
        self.dispatch_event('on_gain_focus')
        
    def replace_state(self, state, *args, **kwargs):
        self.dispatch_event('on_lose_focus')
        self.dispatch_event('on_pop_state', self.state_stack.pop())
        self.state_stack.append(state(self, *args, **kwargs))
        self.dispatch_event('on_push_state', self.state_stack[-1])
        self.dispatch_event('on_gain_focus')


# initialization
GameWindow.register_event_type('on_push_state')
GameWindow.register_event_type('on_pop_state')
GameWindow.register_event_type('on_lose_focus')
GameWindow.register_event_type('on_gain_focus')
GameWindow.register_event_type('on_regain_focus')


