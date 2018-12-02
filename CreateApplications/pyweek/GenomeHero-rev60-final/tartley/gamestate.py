
import math
import pyglet
from pyglet.window import key
from pyglet.gl import *

from state import State
from glsetup import *
from batchmanager import batch
from euclid import *
from helix import Helix
from ui import VectorString, Score, Streak, ATCGDisplay, Mutation, Timer
from endzone import EndZone
from attaboy import MsgQueue
from camera import Camera
import messages
import transitions
from gameobjects import check_hit
import transitions
import script
import audio

diff = {0: "mode", 1:"easy", 2: "medium", 3: "hard"}
spins = {1:(), 2: (), 3: ()}



###############################################################################
############################################################## GameState ######
###############################################################################

class GameState (State):
    def __init__(self, window, level, diff, pair_generator, win_conditions, *args, **kwargs):
        print "++++ new game state"
        self.level = level
        self.diff = diff
        self.pair_generator = pair_generator
        self.win_conditions = win_conditions
        State.__init__(self, window, "game", *args, **kwargs)
        self.build_scene()
        self.current_rung = None
        self.longest_streak = 0
        self.time = 0
        self.mutation_counter = 0
        
    def build_scene(self):
        self.camera = Camera((0.0, -8.0, 1.0), (0,0,1.0))
        self.score = Score(0)
        self.streak = Streak(0)
        self.atcg_display = ATCGDisplay()
        self.endzone = EndZone((-1.4,0,-1.3), 2.8, 0.18)
        self.attaboy = MsgQueue()
        self.mutation = Mutation(0)
        if self.win_conditions.has_key('time'):
            self.timer = Timer(self.win_conditions['time'])	
        else:
            self.timer = None
#        speed_dif = self.level * 0.07 * (self.diff*0.8)
#        spawn_dif = self.level * 0.07 + (self.diff*0.03)

## lower down        
#        self.helix = Helix(speed = 0.7 + speed_dif, spawn_rate=0.7-spawn_dif,
#            starthgt=7, endhgt=-5, spins=2.5, pair_generator=self.pair_generator)
        if self.level >= 4:
            starthgt = 7
            endhgt = -2.5
            spins = 2.5
        else:
            starthgt = 5
            endhgt = -2.5
            spins = 1.5  

        l, d = self.level, self.diff 
        speed_dif = 0.8 + (l * 0.04 * (d*0.6))
        spawn_dif = 0.5 - (l * 0.07 * (d*0.09))

        self.helix = Helix(speed = speed_dif, spawn_rate=spawn_dif,
            starthgt=starthgt, endhgt=endhgt, spins=spins, pair_generator=self.pair_generator)
        self.helix.register_callbacks(self.enter_callback, self.exit_callback)
#        for n in range(100):
#            self.helix.update(0.1)

        
        self.attaboy.add_centered_fade("level %d\n%s\n%s" % (self.level,
            diff[self.diff], messages.EASY_LEVELS[self.level]), 0.2, 0.1)

    def enter_callback(self, r):
        self.current_rung = r

    def exit_callback(self, r):
        if r.get_pair_data()[0] == None or r.get_pair_data()[1] == None:
            self.bad_move()
        self.current_rung = None
        

    def destroy_scene(self):
        pass

    def on_draw(self):
        set3D(self.window)
        self.window.clear()
        glLoadIdentity()
        self.camera.focus()
        batch.get_batch().draw()
        set2D(self.window)
        return pyglet.event.EVENT_HANDLED

    def bad_move(self):
        audio.play_sound('lose_streak')
        r = self.current_rung
        if r:
            r.miss()
        self.camera.shake(1,2, 1)
        self.attaboy.add_centered_fade(messages.random_bad_move(), 0.25, 1, ([0.7,0.7,0.7,1.0], [0.1,0.1,0.1,1.0]))
        self.streak.reset()
        l, d = self.level, self.diff 
        self.helix.mutate(0.2 + (l * 0.04))
        self.mutation_counter += 5 * (self.level*0.5)
        if self.mutation_counter > 100:
            self.lose()
        self.mutation.set_mutation(self.mutation_counter)

    def good_move(self):
        audio.play_sound('hit')
        r = self.current_rung
        if r:
            r.hit()
        if self.mutation_counter > 1:
            self.mutation_counter -= 1
            self.mutation.set_mutation(self.mutation_counter)
        s = self.streak.inc()
        p = s*0.5*100
        self.attaboy.add_score_fade(p)
        self.score.inc_score(p)

    def on_key_press(self, k, args):
## =A++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++===
        if k == key.A:
            self.atcg_display.A.on()
            if check_hit('A', self.current_rung):
                self.good_move()
            else:
                self.bad_move()
## =S++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++===                
        elif k == key.S:
            self.atcg_display.T.on()
            if check_hit('T', self.current_rung):
                self.good_move()
            else:
                self.bad_move()
## =D++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=== 
        elif k == key.D:
            self.atcg_display.C.on()
            if check_hit('C', self.current_rung):
                self.good_move()
            else:
                self.bad_move()
## =F++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++===             
        elif k == key.F:
            self.atcg_display.G.on()
            if check_hit('G', self.current_rung):
                self.good_move()
            else:
                self.bad_move()
## ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=

        elif k == key.LEFT:
            pass
        elif k == key.RIGHT:
            pass
        elif k == key.ESCAPE:
            self.pause()
            return pyglet.event.EVENT_HANDLED
        elif k == key.F11:
            if self.window.fullscreen:
                self.window.set_fullscreen(False)
            else:
                self.window.set_fullscreen(True)
        return pyglet.event.EVENT_HANDLED


    def on_key_release(self, k, args):
        if k == key.A:
            self.atcg_display.A.off()
        elif k == key.S:
            self.atcg_display.T.off()
        elif k == key.D:
            self.atcg_display.C.off()
        elif k == key.F:
            self.atcg_display.G.off()
        return pyglet.event.EVENT_HANDLED

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass

    def lose(self):
        self.window.pop_state()
        self.window.replace_state(transitions.ScriptedTransition, script=script.lose, script_name="lose")

    def win(self):
        self.window.replace_state(transitions.ScriptedTransition, script=script.win, script_name="win")
        
    def on_lose_focus(self):
        pyglet.clock.unschedule(self.on_update)
        return pyglet.event.EVENT_HANDLED

    def on_gain_focus(self):
        self.helix.unobscure()
        self.helix.update(0.1)
        pyglet.clock.schedule_interval(self.on_update, 1.0/60.0)
        return pyglet.event.EVENT_HANDLED

    def check_win_conditions(self):
        if self.win_conditions.has_key('score'):
            if self.score.points > self.win_conditions['score']:
                self.win()
        elif self.win_conditions.has_key('streak'):
            if self.streak.streak >= self.win_conditions['streak']:
                self.win()
        elif self.win_conditions.has_key('time'):
            if self.timer.time < 0:
                self.win()
    
    def on_update(self, dt):
        self.camera.update(dt)
        self.attaboy.update(dt)
        self.atcg_display.update(dt)
        self.check_win_conditions()
        self.helix.update(dt)
        if self.win_conditions.has_key('time'):
            self.timer.update_time(dt)


    def pause(self):
        self.helix.obscure()
        self.helix.update(0.1)
        self.window.push_state(transitions.Pause, "game")
        

