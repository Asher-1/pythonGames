
from pyglet.window import key
import pyglet

from state import State
from gamestate import GameState
from glsetup import *
from ui import MainMenu
from camera import Camera
from helix import Helix
import script
import transitions
from attaboy import MsgQueue
import audio




class MainMenuState (State):
    def __init__(self, window, *args, **kwargs):
        print "++++ new pause state"
        State.__init__(self, window, "main_menu", *args, **kwargs)
        self.build_scene()
        
    def build_scene(self):
        self.attaboy = MsgQueue()
        self.menu = MainMenu()
        self.camera = Camera((3.8, -18.0, 1.0), (3.8,0,1.0))
        self.camera.subtle_motion = True
        self.helix = Helix(starthgt=5, endhgt=-2, spawn_rate=0.5)
#        for x in range(200):
#            self.helix.anima(0.1)

    def destroy_scene(self):
        pass

    def on_draw(self):
        set3D(self.window)
        self.window.clear()
        glLoadIdentity()
        self.camera.focus()
        self.batch.draw()
        set2D(self.window)
        return pyglet.event.EVENT_HANDLED

    def on_key_press(self, k, args):
        if not self.menu.on_key_press(k, args):
            return pyglet.event.EVENT_HANDLED
        if k == key.ENTER:
            if self.menu.choice == 1:
                audio.play_music_fade('chill')
                self.window.push_state(transitions.FadeOut, old_state="main_menu",
                next_state=transitions.ScriptedTransition, duration=0.453,
                next_state_args={ 'script': script.easy_levels, 'script_name': "easy"})
            elif self.menu.choice == 2:
                audio.play_music_fade('easy')
                self.window.push_state(transitions.FadeOut, old_state="main_menu",
                next_state=transitions.ScriptedTransition, duration=0.45,
                next_state_args={ 'script': script.tutorial, 'script_name': "tutorial"})
            elif self.menu.choice == 3:
                if self.window.fullscreen:
                    self.window.set_fullscreen(False)
                else:
                    self.window.set_fullscreen(True)
            elif self.menu.choice == 4:
                audio.play_music_fade('fast_groove')
                self.window.push_state(transitions.FadeOut, old_state="main_menu",
                next_state=transitions.ScriptedTransition, duration=0.45,
                next_state_args={ 'script': script.about, 'script_name': "about"})
            elif self.menu.choice == 5:
                self.window.pop_state()
                self.window.close()
            #self.window.push_state(LevelIntroState, next_state=GameState, level=1)
        elif k == key.F11:
            if self.window.fullscreen:
                self.window.set_fullscreen(False)
            else:
                self.window.set_fullscreen(True)
        elif k == key.ESCAPE:
            self.window.pop_state()
            self.window.close()
        else:
            pass
        return pyglet.event.EVENT_HANDLED
        
    def on_gain_focus(self):
        pyglet.clock.schedule_interval(self.on_update, 1.0/60.0)
        return pyglet.event.EVENT_HANDLED

    def on_lose_focus(self):
        pyglet.clock.unschedule(self.on_update)
        return pyglet.event.EVENT_HANDLED
        
    def on_update(self, dt):
        self.helix.update(dt)
        self.menu.update(dt)
        self.camera.update(dt)
        self.attaboy.update(dt)
        


