from __future__ import division
from constants import *

import math
import random

from gamelib import sound

def sigmoid(x): return 1 / (1 + math.exp(-x))

class AbilityMeta(type):
    classes = []
    def __init__(self, name, bases, dct):
        AbilityMeta.classes.append(self())

class Ability(object):
    __metaclass__ = AbilityMeta
    kind = None
    level = 0
    name = ''
    precise = False
    time_cost = 0.8 * DELAY_MAX
    armour_piercing = False
    damage = (3, 3) #3d3
    # if specified, attack animation will zoom on any part with an attribute
    # from this list with value > 0, preferring the start of the list
    attack_part_tags = []
    attack_sound = None
    def condition(self, stats):
        return False
    
    def activate(self, user, target):
        if self.can_hit(user, target):
            if self.attack_sound:
                self.attack_sound()
            self.take_effect(user, target)
            return True
        else:
            return False
    
    def take_effect(self, user, target):
        us = user.stats
        ts = target.ancestor.stats
        if self.armour_piercing: 
            damage = 1
        else:
            damage = (us['power'] - ts['vitality']) // 5
        for i in xrange(self.damage[0]):
            damage += random.randint(1, self.damage[1])
        damage = int(damage * user.get_blood_pressure()/100)
        target.spread_damage(damage)
        
    def can_hit(self, user, target):
        us = user.stats
        ts = target.ancestor.stats
        return random.random() < sigmoid(3 + (us['speed'] - ts['speed']) / 5)
        
    def attack_part(self, user):
        for tag in self.attack_part_tags:
            parts = filter(lambda p: getattr(p, tag) > 0, user.active_parts())
            if len(parts) > 0:
                return random.choice(parts)
        return None
    
class Struggle(Ability):
    name = 'Struggle'
    def condition(self, stats):
        return False

    def can_hit(self, user, target):
        return False
        
# this is the only one we reference specifically
struggle = filter(lambda c: c.name == "Struggle", AbilityMeta.classes)[0]


# Bitey attacks
# armour piercing

class Bite(Ability):
    name = 'Bite'
    attack_part_tags = ['jaws']
    damage = (2, 5)
    attack_sound = sound.bite
    kind = 'bite'
    armour_piercing = True
    def condition(self, stats):
        return stats['jaws'] >= 1

class DoubleBite(Bite):
    name = 'Double Bite'
    damage = (2, 8)
    attack_sound = sound.bite.repeat([0.2])
    damage = (2, 10)
    level = 1
    def condition(self, stats):
        return stats['jaws'] >= 2

class Peck(Bite):
    name = 'Peck'
    attack_part_tags = ['beaks']
    attack_sound = sound.peck
    damage = (4, 6)
    level = 2
    def condition(self, stats):
        return stats['beaks'] >= 1

class BitePeck(Bite):
    name = 'Bite-and-peck'
    damage = (5, 10)
    level = 3
    attack_sound = sound.sequence([sound.bite, sound.peck], [0.2])
    
    def condition(self, stats):
        return stats['beaks'] >= 1 and stats['jaws'] >= 1

class Chew(Bite):
    name = 'Chew'
    damage = (12, 6)
    level = 4
    attack_sound = sound.bite.repeat([0.2, 0.2])
    
    def condition(self, stats):
        return stats['jaws'] >= 1 and stats['power'] >= 30


class Chomp(Bite):
    name = 'Chomp'
    damage = (15, 6)
    level = 5
    attack_sound = sound.bite

    def condition(self, stats):
        return stats['jaws'] >= 1 and stats['power'] >= 18 and stats['vitality'] >= 30

class Zap(Bite):
    name = 'Zap'
    damage = (20, 8)
    level = 6
    attack_part_tags = ['sparks']
    attack_sound = sound.laser
    
    def condition(self, stats):
        return stats['sparks'] >= 1
        
# Punchy attacks
# standard damage

class Trample(Ability):
    name = 'Trample'
    attack_part_tags = ['legs']
    damage = (3, 3)
    kind = 'punch'
    attack_sound = sound.punch

    def condition(self, stats):
        return stats['legs'] >= 2

class HeadButt(Ability):
    name = 'Headbutt'
    attack_part_tags = ['horns']
    attack_sound = sound.punch
    damage = (3, 6)
    kind = 'punch'
    level = 1

    def condition(self, stats):
        return stats['horns'] >= 1 and stats['power'] >= 18

class Punch(Ability):
    name = 'Punch'
    attack_part_tags = ['hands']
    attack_sound = sound.punch
    kind = 'punch'
    level = 2
    damage = (6, 5)

    def condition(self, stats):
        return stats['hands'] >= 1
        
class Pummel(Ability):
    name = 'Pummel'

    attack_part_tags = ['hands']
    attack_sound = sound.punch
    kind = 'punch'
    level = 3
    damage = (10, 8)

    def condition(self, stats):
        return stats['hands'] >= 2 and stats['speed'] >= 25
        
class Crush(Ability):
    name = 'Crush'
    
    attack_part_tags = ['tendrils']
    attack_sound = sound.punch
    kind = 'punch'
    level = 3
    damage = (10, 8)

    def condition(self, stats):
        return stats['tendrils'] >= 1 and stats['power'] >= 25  

class Kick(Ability):
    name = 'Kick'

    attack_part_tags = ['legs']
    attack_sound = sound.punch
    kind = 'punch'
    level = 3
    damage = (10, 8)

    def condition(self, stats):
        return stats['legs'] >= 1 and stats['power'] >= 25 and stats['speed'] >= 25  

class Stampede(Ability):
    name = 'Stampede'
    
    attack_part_tags = ['legs']
    attack_sound = sound.punch.repeat([0.1,0.1,0.1,0.1])
    kind = 'punch'
    level = 4
    damage = (12, 10)

    def condition(self, stats):
        return stats['legs'] >= 3 and stats['vitality'] >= 30
        
# Grabby attacks
# slow down

class Whip(Ability):
    name = 'Whip'
    attack_part_tags = ['tails', 'tendrils'] # don't zoom on coils if that's all there is
    attack_sound = sound.whip
    kind = 'grab'
    def take_effect(self, user, target):
        target.receive_temp_stat('speed', -5, 1)
        
    def condition(self, stats):
        return stats['tails'] >= 1 or stats['coils'] >= 1 or stats['tendrils'] >= 1
          
class Grapple(Ability):
    name = 'Grapple'
    kind = 'grab'
    level = 1
    attack_sound = sound.punch
    
    def condition(self, stats):
        return stats['arms'] >= 2

    def take_effect(self, user, target):
        target.receive_temp_stat('speed', -10, 1)

class BodyBlow(Ability):
    name = 'Body Blow'
    kind = 'grab'
    level = 2
    attack_sound = sound.punch

    def condition(self, stats):
        return stats['vitality'] >= 30

    def take_effect(self, user, target):
        target.receive_temp_stat('speed', -10, 2)
        target.receive_temp_stat('vitality', -5, 2)
        
# Gougey attacks
# lower vitality

class Gouge(Ability):
    name = 'Gouge'
    attack_part_tags = ['spikes', 'beaks', 'hands']
    kind = 'gouge'

    def condition(self, stats):
        return stats['beaks'] > 0 or stats['hands'] > 0 or stats['spikes'] > 0

    def take_effect(self, user, target):
        target.receive_temp_stat('vitality', -5, 4)
