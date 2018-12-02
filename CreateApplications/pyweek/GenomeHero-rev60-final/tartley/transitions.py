import math
import pyglet
from pyglet.window import key
from pyglet.gl import *

from state import State
from glsetup import *
from batchmanager import batch
from ui import VectorString, AboutPic
from attaboy import MsgQueue
from camera import Camera
from drawgroups import *
from script import tutorial
import audio
import gamestate
import menustate


class ScriptedTransition (State):

    def __init__(self, window, *args, **kwargs):
        print "++++ new level intro state"
        script_name = kwargs['script_name']
        State.__init__(self, window, "scripted%s" % script_name, *args, **kwargs)
        self.build_scene()
        self.script = kwargs['script'][:]
        self.running_text = False
        self.band_pic = None

    def build_scene(self):
        self.camera = Camera((0.0, -8.0, 1.0), (0,0,1.0))
        self.camera.subtle_motion = True
        self.camera.subtle_range = (1.5, -1.5)
        self.camera.subtle_speed = 0.04
        self.attaboy = MsgQueue()

    def destroy_scene(self):
        pass
        
    def on_key_press(self, k, args):
        if k == key.F11:
            if self.window.fullscreen:
                self.window.set_fullscreen(False)
            else:
                self.window.set_fullscreen(True)    
        return pyglet.event.EVENT_HANDLED
        
    def on_draw(self):
        set3D(self.window)
        self.window.clear()
        glLoadIdentity()
        self.camera.focus()
        self.batch.draw()
        set2D(self.window)
        return pyglet.event.EVENT_HANDLED

    def on_lose_focus(self):
        pyglet.clock.unschedule(self.on_update)
        self.destroy_scene()
        return pyglet.event.EVENT_HANDLED

    def on_gain_focus(self):
        pyglet.clock.schedule_interval(self.on_update, 1.0/60.0)
        return pyglet.event.EVENT_HANDLED

    def on_update(self, dt):
        self.camera.update(dt)
        self.attaboy.update(dt)
        
        
        if self.running_text:
            if self.running_text.finished:
                self.running_text = None
                return pyglet.event.EVENT_HANDLED
            else:
                return pyglet.event.EVENT_HANDLED
        elif self.band_pic:
            if self.band_pic.finished:
                self.band_pic.delete()
                self.band_pic = None
                return pyglet.event.EVENT_HANDLED
            else:
                self.band_pic.update(dt)
                return pyglet.event.EVENT_HANDLED
        if self.script:
            s = self.script.pop(0)
            if s[0] == "fade":
                self.running_text = self.attaboy.add_centered_fade(*s[1])
            elif s[0] == "game":
                self.window.push_state(gamestate.GameState, s[1], s[2], s[3], s[4])
            elif s[0] == "music":
                if audio.playing():
                    audio.play_music_fade(s[1])
                else:
                    audio.play_music(s[1])
            elif s[0] == "main_menu":
                self.window.replace_state(menustate.MainMenuState)
            elif s[0] == "band_pic":
                self.band_pic = AboutPic('./data/rsjf.png')
            elif s[0] == "cc_pic":
                self.band_pic = AboutPic('./data/ccsa.png')
            else:
                pass
#            self.window.replace_state(self.next_state)
        else:
            #self.window.replace_state(self.next_state, **self.next_state_args)
            self.window.pop_state()
        return pyglet.event.EVENT_HANDLED


###############################################################################
###################################################### Pause ##################
###############################################################################

class Pause (State):

    def __init__(self, window, *args, **kwargs):
        print "++++ new pause state"
        State.__init__(self, window, "pause", *args, **kwargs)
        audio.attenuate_music()
        self.menuloc = (-0.9, 1.0)        
        self.choices = {1: 'resume',
                        2: 'quit',
                    }
        self.choice = 1
        self.old_state_batch = args[0]
        self.build_scene()
        

    def build_labels(self):
        tl = []
        x, z = self.menuloc
        for c in self.choices.keys():
            lx, lz = x, (z + (c*-0.4))# + -0.6
            l = self.attaboy.pulse(self.choices[c], 0.11, 1, (lx,-1,lz))
            l.pause()
            tl.append(l)
        return tl

        
    def build_scene(self):
        self.camera = Camera((0.0, -8.0, 1.0), (0,0,1.0))
        self.camera.subtle_motion = True
        self.camera.subtle_range = (3.5, -3.5)
        self.camera.subtle_speed = 0.04
        self.attaboy = MsgQueue()
        self.attaboy.pulse("pause", 0.25, 1, (-1.0, -1, 1)).pause(1)
        self.labels = self.build_labels()
        self.labels[0].unpause()
        

    def destroy_scene(self):
        pass
        
    def on_draw(self):
        set3D(self.window)
        self.window.clear()
        glLoadIdentity()
        self.camera.focus()
        batch.get_batch(self.old_state_batch).draw()
        self.batch.draw()
        set2D(self.window)
        return pyglet.event.EVENT_HANDLED

    def on_lose_focus(self):
        pyglet.clock.unschedule(self.on_update)
        self.destroy_scene()
        return pyglet.event.EVENT_HANDLED

    def on_gain_focus(self):
        pyglet.clock.schedule_interval(self.on_update, 1.0/60.0)
        return pyglet.event.EVENT_HANDLED

    def on_update(self, dt):
        self.camera.update(dt)
        self.attaboy.update(dt)

    def on_key_press(self, k, mod):
        labels = self.labels
        if k == key.UP:
            if self.choice == 1:
                labels[self.choice-1].pause(1)
                self.choice = len(self.choices)
                labels[self.choice-1].unpause()
            else:
                labels[self.choice-1].pause(1)
                self.choice -= 1
                labels[self.choice-1].unpause()

        elif k == key.DOWN:
            if self.choice == len(self.choices):
                labels[self.choice-1].pause(1)
                self.choice = 1
                labels[self.choice-1].unpause()
            else:
                labels[self.choice-1].pause(1)
                self.choice += 1
                labels[self.choice-1].unpause()

        elif k == key.ENTER:
            if self.choice == 1:
                audio.unattenuate_music()
                self.destroy_scene()
                self.window.pop_state()
            elif self.choice == 2:
                self.destroy_scene()
                audio.play_music_fade('intro')
                self.window.pop_state()
                self.window.pop_state()
                self.window.pop_state()
        elif k == key.F11:
            if self.window.fullscreen:
                self.window.set_fullscreen(False)
            else:
                self.window.set_fullscreen(True)

        elif k == key.ESCAPE:
            audio.unattenuate_music()
            self.destroy_scene()
            self.window.pop_state()
            
        #self.window.pop_state()
        return pyglet.event.EVENT_HANDLED


    
fade_color = [0.0, 0.0, 0.0, 0.0]
fade_quad = [-10,-1,-10,   10,-1,-10,   10,-1,10,   -10,-1,10]


###############################################################################
###################################################### Fade ###################
###############################################################################

class FadeOut (State):

    def __init__(self, window, *args, **kwargs):
        print "++++ new fade state"
        State.__init__(self, window, "fade", *args, **kwargs)
        self.old_state_batch = kwargs['old_state']
        self.duration = kwargs['duration']
        self.next_state = kwargs['next_state']
        self.next_state_args = kwargs['next_state_args']
        self.build_scene()
        self.alpha = 0.0
        
    def build_scene(self):
        self.quad = batch.get_batch().add(4, GL_QUADS, GRP_BLEND_ONE_MINUS,
                ("v3f", fade_quad),
                ("c4f", fade_color*4),
                )
        self.camera = Camera((3.8, -18.0, 1.0), (3.8,0,1.0))
        self.attaboy = MsgQueue()

    def destroy_scene(self):
        pass
        
    def on_draw(self):
        set3D(self.window)
        self.window.clear()
        glLoadIdentity()
        self.camera.focus()
        batch.get_batch(self.old_state_batch).draw()
        batch.get_batch().draw()
        set2D(self.window)
        return pyglet.event.EVENT_HANDLED

    def on_key_press(self, k, args):
        if k == key.F11:
            if self.window.fullscreen:
                self.window.set_fullscreen(False)
            else:
                self.window.set_fullscreen(True)    
        return pyglet.event.EVENT_HANDLED

    def on_lose_focus(self):
        pyglet.clock.unschedule(self.on_update)
        self.destroy_scene()
        return pyglet.event.EVENT_HANDLED

    def on_gain_focus(self):
        pyglet.clock.schedule_interval(self.on_update, 1.0/60.0)
        return pyglet.event.EVENT_HANDLED

    def on_update(self, dt):
        self.attaboy.update(dt)
        if self.alpha > 1:
            self.window.replace_state(self.next_state, **self.next_state_args)
        else:
            color = fade_color
            color[3] = self.alpha
            self.quad.colors = color *4
            self.alpha += self.duration*dt
        return pyglet.event.EVENT_HANDLED


        
