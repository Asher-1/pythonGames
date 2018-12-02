'''
Created on 11.09.2011

'''

import data
import math
import sound

from math2d import Vector2
from renderables import AnimatedSprite

from globals import Z_INDICES
from globals import ARCHETYPE
from globals import BASE_CREEP
from globals import FATSO
from globals import DRUNK
from globals import ORPHAN

from game import Entity
from game import GameState
from pathfinding import Walker
from random import Random

from game import UniformGrid

from misc import BaseMarking

from effects import SmokeExplosion

class BaseCreep(BASE_CREEP, Entity):
    
    _sprite = None
    _path = None
    _walker = None
    _life = 100
    _lifeSoon = _life
    
    _LastMarkable = None
    
    WALK_CYCLE_LENGTH = None
    _walkCycle = 0.0
    
    rnd = Random()
    
    _ArcheType = ARCHETYPE.CREEP
    addToGrid = True
    gridPosDist = 0.0
    
    WALKER_OFFSET = 15.0
    
    _AttachedTo = None
    _AttachOffset = None
    
    def __init__(self):
        Entity.__init__(self)
        
        self.WALK_CYCLE_LENGTH = self.WALK_CYCLE_LENGTH_SPEED / self.SPEED;
        self._walkCycle = self.rnd.random() * self.WALK_CYCLE_LENGTH 
        
        self._sprite = self.add_renderable(AnimatedSprite())
        self._sprite.set_z_index(Z_INDICES.CREEP)
        self._sprite.fps = 30.0
        self._sprite.set_position(self._position)
        self._sprite.set_rotation(self._rotation)
        self._sprite.set_scale(0.8 + self.rnd.random() * 0.2)
        self._life = self.LIFE
        self._lifeSoon = self._life
        self.set_animation(data.load_texture(self.TEXTURE))
 
    def update_grid_pos(self):
        GameState.get_main_gamestate().entity_pos_changed(self, self.get_walker_position())
        
    def attach_to_path(self, path):
        self._path = path
        
        if not path or not path.get_start():
            print "empty path"
            self.on_target_reached()
            return
        
        self._walker = Walker(self._path.get_start(), True, self.SPEED, BaseCreep.WALKER_OFFSET)
        self.update_path_position(0, 0)
        self.update_grid_pos()
 
    def get_walker_position(self):
        if self._walker: return self._walker.get_position()
        return self.get_position()
           
    def set_speed_factor(self, factor):
        if self._walker:
            self._walker.set_speed(factor * self.SPEED)
    
    def delete(self):
        Entity.delete(self)
        if self._LastMarkable:
            self.on_leave_markable(self._LastMarkable)
            self._LastMarkable = None            
    
    def update(self, gameTime, deltaTime):
        Entity.update(self, gameTime, deltaTime)
        
        if self._life <= 0:
            self.on_die()            
            if self._IsDeleted:
                return
        
        if self._walker:
            self.update_path_position(gameTime, deltaTime)
            if self._walker.has_reached_target():
                self.on_target_reached()
            else:
                self._update_markable_attachment()
        elif self._AttachedTo:
            self.update_carry_position(gameTime, deltaTime)
    
    def _update_markable_attachment(self):
        gameState = GameState.get_main_gamestate()
        markable = gameState.get_entity_at_grid(self.get_walker_position(), ARCHETYPE.MARKABLE)
        self._set_current_markable(markable)
                
    def _set_current_markable(self, markable):
        if markable == self._LastMarkable: return
        if self._LastMarkable:
            self.on_leave_markable(self._LastMarkable)
        self._LastMarkable = markable
        if self._LastMarkable:
            self.on_enter_markable(self._LastMarkable)
                
    def on_enter_markable(self, markable):
        markable.on_creep_enter(self)
    
    def on_leave_markable(self, markable):
        markable.on_creep_leave(self)
    
    def update_carry_position(self, gameTime, deltaTime):
        back = Vector2.from_rotation(self._AttachedTo.get_rotation())
        right = back.right_vector()        
        self.set_position(self._AttachedTo.get_position() - back * 20.0 + right * self._AttachOffset)
        self.set_rotation(self._AttachedTo.get_rotation())
        
    def update_path_position(self, gameTime, deltaTime):
        self._walker.update(gameTime, deltaTime)
        
        self._walkCycle += deltaTime
        self._walkCycle = self._walkCycle % self.WALK_CYCLE_LENGTH
        
        walkCycle = self._walkCycle / self.WALK_CYCLE_LENGTH * 2.0 * math.pi
        walkCycleRotation = math.sin(walkCycle) * self.WALK_CYCLE_STRENGTH
        
        self.set_position(self._walker.get_visual_position())
        self.set_rotation(self._walker.get_rotation() + walkCycleRotation)
        
        self.gridPosDist += self._walker.frameMove
        if self.gridPosDist > UniformGrid.UPDATE_INTERVAL:
            self.gridPosDist = 0.0
            self.update_grid_pos()
    
    def on_target_reached(self):
        gameState = GameState.get_main_gamestate()
        gameState.set_success_Creep(self.CREEPTYPE)
        self.delete()
        
    def render(self, gameTime, deltaTime):
        pass
    
    def set_animation(self, *textures):
        self._sprite.set_animation(textures)
    
    def set_position(self, position):
        Entity.set_position(self, position)
        self._sprite.set_position(position)
    
    def set_rotation(self, rotation):
        Entity.set_rotation(self, rotation)
        self._sprite.set_rotation(rotation)
        
    def on_die(self):
        gameState = GameState.get_main_gamestate()
        gameState.update_living_creeps(False)
        effect = SmokeExplosion()
        effect.set_position(self.get_position())
        effect.set_color(self.DIE_COLOR)
        sound.play_sound(self.DIE_SOUND)
        effect.start()
        self.delete()
    
    def get_life(self):
        return self._life
    
    def set_life(self, life):
        change = life - self._life
        self._lifeSoon += change
        self._life = life
        
        red = float(self._life) / float(self.LIFE)
        self._sprite.set_color(1.0, red, red)
    
    def dead_man_walking(self):
        return self._lifeSoon <= 0
    
    def register_incoming_damage(self, damage, damageType):
        resistance = self.DAMAGE_RESISTANCE.get(damageType)
        if resistance == None: 
            resistance = 0.0
        self._lifeSoon -= damage * (1.0 - resistance)
        
    def deal_damage(self, damage, damageType):
        if self._AttachedTo:
            return
         
        resistance = self.DAMAGE_RESISTANCE.get(damageType)
        if resistance == None: 
            print "Missing resistance entry for", damageType, "!!"
            resistance = 0.0
        self._life -= damage * (1.0 - resistance)
        
        red = float(self._life) / float(self.LIFE)
        self._sprite.set_color(1.0, red, red)
        
    def on_pickup(self, carrier, offset = None):
        self.set_life(self.LIFE)
        self.remove_from_grid()
        self._AttachedTo = carrier
        self._walker = None
        self._set_current_markable(None)
        if offset == None:
            self._AttachOffset = self.rnd.random() * 20.0 - 10.0
        else: 
            self._AttachOffset = offset
            print offset
            
        
class Fatso(FATSO, BaseCreep):
    
    _Carrying = None
    _CarryOffsetCount = 0
    _CARRY_AREA = 40.0
    
    def __init__(self):
        BaseCreep.__init__(self)
        self._Carrying = []    

    def update(self, gameTime, deltaTime):
        BaseCreep.update(self, gameTime, deltaTime)
        
        if len(self._Carrying) < self.SPECIAL_MAX_CARRY:
            self.search_pickup()
    
    def search_pickup(self):
        if self._LastMarkable:
            for creep in self._LastMarkable.creeps():
                if creep.CREEPTYPE == ORPHAN.CREEPTYPE:
                    self.pickup(creep)
                    break
        
    def pickup(self, target):
        self._Carrying.append(target)
        offset = self._CarryOffsetCount * self._CARRY_AREA / (self.SPECIAL_MAX_CARRY-1)
        offset -= self._CARRY_AREA * 0.5
        self._CarryOffsetCount += 1
        if self._CarryOffsetCount >= self.SPECIAL_MAX_CARRY:
            self._CarryOffsetCount = 0
        
        target.on_pickup(self, offset)
     
    def deal_damage(self, damage, damageType):
        BaseCreep.deal_damage(self, damage, damageType)
        if self.get_life() < self.LIFE * self.SPECIAL_USE_THRESHOLD:
            self.eat_something()
            
    def eat_something(self):
        if len(self._Carrying):
            meal = self._Carrying.pop()
            meal.set_life(0)
            self.set_life(self.get_life() + self.SPECIAL_HEALTH_PER_USE * self.LIFE)
            sound.play_sound(self.EAT_SOUND)
            self._CarryOffsetCount -= 1
            if self._CarryOffsetCount < 0:
                self._CarryOffsetCount = self.SPECIAL_MAX_CARRY - 1
    
    def on_target_reached(self):
        for carry in self._Carrying:
            carry.on_target_reached()
        self._Carrying = []
        BaseCreep.on_target_reached(self)
        
        
class DrunkMarking(BaseMarking):

    _SpeedUpFactor = DRUNK.SPECIAL_SPEEDUP_FACTOR
    
    def __init__(self):
        BaseMarking.__init__(self, DRUNK.SPECIAL_MARK_DURATION)
        
    def on_creep_enter(self, creep):
        if creep.CREEPTYPE != DRUNK.CREEPTYPE:
            creep.set_speed_factor(self._SpeedUpFactor)        
        
    def on_creep_leave(self, creep):
        if creep.CREEPTYPE != DRUNK.CREEPTYPE:
            creep.set_speed_factor(1.0)            

class Drunk(DRUNK, BaseCreep):    
        
    def __init__(self):
        BaseCreep.__init__(self)
                
    def on_enter_markable(self, markable):
        BaseCreep.on_enter_markable(self, markable)
        markable.add_marking(DrunkMarking())      
    
    def deal_damage(self, damage, damageType):
        BaseCreep.deal_damage(self, damage, damageType)
        self.check_eat()
        
    def update(self, gameTime, deltaTime):
        BaseCreep.update(self, gameTime, deltaTime)
        self.check_eat()
    
    def check_eat(self):
        if self.get_life() < self.LIFE * self.SPECIAL_USE_THRESHOLD:
            self.eat_something()
            
    def eat_something(self):
        meal = self.search_meal()
        if meal:
            meal.set_life(0)
            self.set_life(self.get_life() + self.SPECIAL_HEALTH_PER_USE * self.LIFE)
            sound.play_sound(self.EAT_SOUND)
            
    def search_meal(self):
        if self._LastMarkable:
            for creep in self._LastMarkable.creeps():
                if creep.CREEPTYPE == ORPHAN.CREEPTYPE:
                    return creep
                

class Orphan(ORPHAN, BaseCreep):

    def __init__(self):
        BaseCreep.__init__(self)
        
        
        
        