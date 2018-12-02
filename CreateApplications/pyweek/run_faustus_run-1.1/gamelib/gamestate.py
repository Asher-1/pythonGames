import pickle
from gamelib.data import upgrades
from gamelib.constants import *

class cached(object):
    def __init__(self, function):
        self.function = function
    def __get__(self, obj, cls=None):
        value = self.function()
        setattr(obj, self.function.__name__, value)
        return value

class GameState(object):

    def __init__(self, data=None):
        if data is None:
            self.starting_state()
        else:
            self.deserialise(data)
        if DEBUG:
            self.unlocked_upgrades.extend(upgrades.Upgrade.index['spell'])

    def starting_state(self):
        self.current_spells = [upgrades.s_missile, upgrades.s_shield, None, None]
        self.unlocked_upgrades = [upgrades.s_missile, upgrades.s_shield]
        self.upgrade_coins = 0

    def serialise(self):
        from gamelib import app
        app.config.save_option('state',
            pickle.dumps((
                [up if up is None else up.name for up in self.current_spells],
                [up.name for up in self.unlocked_upgrades],
                self.upgrade_coins,
                )))

    def deserialise(self, data):
        try:
            (cs, uu, uc) = pickle.loads(data)
            self.current_spells = [upgrades.Upgrade.name_index[n] for n in cs]
            self.unlocked_upgrades = [upgrades.Upgrade.name_index[n] for n in uu]
            self.upgrade_coins = uc
        except:
            import traceback
            traceback.print_exc()
            self.starting_state()
            self.serialise()

    # this needs to cache its results - but only until something is unlocked!
    gmv_cache = {}
    def get_max_value(self, name, default):
        if name in self.gmv_cache:
            return self.gmv_cache[name]
        res = default
        for u in self.unlocked_upgrades:
            if name in u.attribs:
                res = max(res, u.attribs[name])
        self.gmv_cache[name] = res
        return res
    def get_min_value(self, name, default):
        if name in self.gmv_cache:
            return self.gmv_cache[name]
        res = default
        for u in self.unlocked_upgrades:
            if name in u.attribs:
                res = min(res, u.attribs[name])
        self.gmv_cache[name] = res
        return res

    def available_upgrades(self):
        ms = []
        for upn in sorted(upgrades.Upgrade.name_index):
            up = upgrades.Upgrade.name_index[upn]
            if up is None: continue
            if up in self.unlocked_upgrades: continue
            an = any(u in self.unlocked_upgrades for u in up.prereqs)
            miss = [u for u in up.prereqs if u not in self.unlocked_upgrades]
            if an:
                if miss: ms.append((up, miss))
                else: yield up, miss
        for x in ms: yield x

    def unlock(self, up):
        if self.can_upgrade():
            if all(u in self.unlocked_upgrades for u in up.prereqs):
                self.unlocked_upgrades.append(up)
                self.upgrade_coins -= 1
                self.serialise()
                self.gmv_cache = {}
                return True

    def can_upgrade(self):
        return self.upgrade_coins > 0 or DEBUG

    @property
    def collected_scrolls(self):
        return len(self.unlocked_upgrades) + self.upgrade_coins

    @property
    def max_jumps(self):
        return self.get_max_value('max_jumps', 1)
        
    @property
    def run_speed(self):
        return self.get_max_value('run_speed', 1.0)
        
    @property
    def num_arrows(self):
        return self.get_max_value('num_arrows', 5)

    @property
    def start_dist(self):
        return self.get_max_value('start_dist', 0)

    @property
    def missile_damage(self):
        return self.get_max_value('missile_damage', 1)
        
    @property
    def shield_time(self):
        return self.get_max_value('shield_time', 240)
        
    @property
    def shield_count(self):
        return self.get_max_value('shield_count', 2)

    @property
    def teleport_cost(self):
        return self.get_min_value('teleport_cost', 1500)
        
    @property
    def knockback(self):
        return self.get_min_value('knockback', 25)
        
    @property
    def stun_time(self):
        return self.get_min_value('stun_time', 40)
        
    @property
    def firebomb_radius(self):
        return self.get_max_value('firebomb_radius', 200)
        
    @property
    def firebomb_damage(self):
        return self.get_max_value('firebomb_damage', 4)
