import math
import collections
from batchmanager import batch
from drawgroups import *
import heliograph
from gameobjects import random_pair
from mutation import Mutation

#KEYS = ['rung_ends', 'lbase', 'rbase', 'lsphere', 'rsphere', 'lconnect', 'rconnect']
KEYS = ['lend', 'rend', 'lbase', 'rbase', 'lsphere', 'rsphere', 'lconnect', 'rconnect']
#KEYS = ['lend', 'rend']

SPD_DEFAULT = 1.0
SPD_MUT_RATIO = 0.1
SPD_DECAY = 0.02

class Rung:
    def __init__(self, helix, game_obj):
        self.helix = helix
        self.maxhgt = helix.maxhgt
        self.endhgt = helix.endhgt
        self.radius = helix.radius
        self._last_ends = helix._last_ends
        self._hgt = helix.starthgt
        self._animas = 0
        self.graphics = {}
        self.endpoints = []
        self.dead = False
        self.spin = 0
        self.cos_spin = 0
        self.sin_spin = 1
        self.game_obj = game_obj
        self.graphics['lend'] = heliograph.RungEnds(self, 0)
        self.graphics['rend'] = heliograph.RungEnds(self, sign=-1)
        self.graphics['lbase'] = heliograph.Base(self, self.game_obj.left, 3)
        self.graphics['rbase'] = heliograph.Base(self, self.game_obj.right, sign=-1)
        self.graphics['lsphere'] = heliograph.Sphere(self,3)
        self.graphics['rsphere'] = heliograph.Sphere(self)
        self.graphics['lconnect'] = heliograph.Connect(self,3 )
        self.graphics['rconnect'] = heliograph.Connect(self)
        self.prev = None
        self.next = None
        self.in_box = False
        self.complete = False
        

    def trigcache(self):
        self.spin = self._animas * heliograph.SPINRATE
        self.cos_spin = math.cos(self.spin)
        self.sin_spin = math.sin(self.spin)
        
    def update(self, dt, speed):
        #print self.vertex_list
        self._hgt -= dt * heliograph.CLIMBRATE * speed
        if self._hgt < self.endhgt and not self.dead:
            for k in self.graphics.keys():
                self.graphics[k].delete()
            self.dead = True
            return
        self._animas += dt * speed
        self.trigcache()
        self.endpoints = []
        for k in KEYS:
            self.graphics[k].update(dt)

    def __str__(self):
        return "Rung: %s - %s" % (self.game_obj.left, self.game_obj.right)

    def get_pair_data(self):
        return (self.game_obj.left, self.game_obj.right)

    def update_game_obj(self):
        self.graphics['lbase']._type = self.game_obj.left
        self.graphics['rbase']._type = self.game_obj.right

    def obscure(self):
        self.graphics['lbase'].obscured = True
        self.graphics['rbase'].obscured = True

    def unobscure(self):
        self.graphics['lbase'].obscured = False
        self.graphics['rbase'].obscured = False

    def miss(self):
        self.graphics['lbase']._type = None
        self.graphics['rbase']._type = None

    def hit(self):
        self.graphics['lbase'].complete = True
        self.graphics['rbase'].complete = True

class Helix:
    def __init__(self, starthgt=11, endhgt=-9, spins=3.5, radius=1,
        speed=SPD_DEFAULT, spawn_rate=1, pair_generator=random_pair):
        self.starthgt = starthgt
        self.endhgt = endhgt
        self.spins = spins
        self.maxhgt = self.starthgt - (math.pi)*self.spins
        self.radius = radius
        self._animas = 0
        self._rungs = []
        self._tba = []
        self.speed = speed
        self.spdmod = 1
        self._last_rung = None
        self._last_ends = []
        self.spawn_rate = spawn_rate
        self.pair_generator = pair_generator
        self.mutation = Mutation()
        self.enter_callback = None
        self.exit_callback = None
        self.in_box = []
        
    def mutate(self, amt):
        self.mutation.mutate(amt)
        self.spdmod += amt * SPD_MUT_RATIO

    ### DO NOT USE
    def make_rung(self, next=None):
        rung = Rung(self, self.pair_generator())
        if next:
            rung.next = next
            self._last_rung.prev = rung
        self._rungs.append(rung)
        self._last_ends = rung
        self._last_rung = rung

    def obscure(self):
        map(Rung.obscure, self._rungs)

    def unobscure(self):
        map(Rung.unobscure, self._rungs)

    def register_callbacks(self, enter_callback, exit_callback):
        self.enter_callback = enter_callback
        self.exit_callback = exit_callback

    def update(self, dt):
        ## update the mutation
        self.mutation.update(dt)

        ## check to see if the last rung is far enough away for a new one
        if self._last_rung:
            if self._last_rung._hgt <= self.starthgt - self.spawn_rate:
                self.make_rung(self._last_rung)
        else:
            self.make_rung()

        ## compute the speed with mod -1.12 -> -1.3
        speed = self.speed*self.spdmod    
        #print "speed", speed

        ## update the mutation
        self.mutation.update(dt)

        ## check to see if the last rung is far enough away for a new one
        if self._last_rung:
            if self._last_rung._hgt <= self.starthgt - self.spawn_rate:
                self.make_rung(self._last_rung)
        else:
            self.make_rung()
            
        self.spdmod = max(self.spdmod - dt*SPD_DECAY, 1)
        ## compute the speed with mod -1.12 -> -1.3
        speed = self.speed*self.spdmod    

        for r in self._rungs:
            if r._hgt < -1.12 and r._hgt > -1.3:
                if not r.in_box:
                    r.in_box=True
                    if self.enter_callback:
                        self.enter_callback(r)
            if r.in_box and r._hgt < -1.3:
                r.in_box = False
                if self.exit_callback:
                    self.exit_callback(r)
            r.update(dt, speed)
            
        ## update and kill the rungs that have it coming :P
        dead = []
        for entity in self._rungs:
            if entity.dead:
                dead.append(entity)
        for e in dead:
            self._rungs.remove(e)




#    def anima(self, dt, speed=-1, active=True, kill_rung=None, shake=False):
#        self.mutation.update(dt)
#        
##        self._animas += min(dt,1)
##        if speed >= 0:
##            self.speed = speed
##        self.spdmod = max(self.spdmod - dt*SPD_DECAY, 1)
##        spd = self.speed*self.spdmod
##        dx = self._animas - self._last_rung
##        if active and dx > 1.0/spd/self.spawn_rate:
##            #print self._animas, self._last_rung, self.speed
##            new_rung = self.make_rung()
##            self._last_rung = new_rung
#        

#        dead = []
#        for entity in self._rungs:
#            if entity.dead:
#                dead.append(entity)
#            else:
#                entity.update(dt, spd)
#        for e in dead:
#            self._rungs.remove(e)

#        

### ----------------------------------------------------------------------------
#        rung = self._rungs[:10]
#        #print rung
#        rib = []
#        for ru in rung: ## -1.2 -1.3
#            if ru._hgt <= -1.2:
#                pass
#            elif ru._hgt <= -0.2 and ru._hgt >= -1.2:
#                rib += [ru]
#        if rib:
#            return rib[:1]
#        else:
#            return []
### ----------------------------------------------------------------------------
#        return []

if __name__ == '__main__':
    h = Helix()
