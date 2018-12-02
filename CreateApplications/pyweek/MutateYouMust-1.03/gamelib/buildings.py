'''
Created on 11.09.2011

'''

import data
import sound

from game import Entity
from game import GameState
from renderables import Sprite
from globals import Z_INDICES

from globals import BASE_SPAWNER
from globals import FASTFOOD
from globals import ORPHANAGE
from globals import BEERGARDEN
from globals import ARCHETYPE

from creeps import Fatso
from creeps import Orphan
from creeps import Drunk

class BaseBuilding(Entity):
    
    _sprite = None
    
    def __init__(self):
        Entity.__init__(self)
        
    def _create_sprite(self, texture):
        self._sprite = self.add_renderable(Sprite())
        self._sprite.set_texture(texture)
        self._sprite.set_z_index(Z_INDICES.BUILDING)
        
    def set_position(self, position):
        Entity.set_position(self, position)
        self._sprite.set_position(position)
    
    def set_rotation(self, rotation):
        Entity.set_rotation(self, rotation)
        self._sprite.set_rotation(rotation)


class HQ(BaseBuilding):
    
    def __init__(self):
        BaseBuilding.__init__(self)
        
        self._create_sprite(data.load_texture("building_hq.png"))
        
        
class Spawner(BASE_SPAWNER, BaseBuilding):
    
    path = None
    _spawned = 0
    _my_spawn_limit = 0
        
    _ArcheType = ARCHETYPE.SPAWNER
    
    def __init__(self):
        BaseBuilding.__init__(self)
        
        self._create_sprite(data.load_texture(self.TEXTURE))
        gameState = GameState.get_main_gamestate()
        self._my_spawn_limit = gameState.get_building_type_clicks(self.SPAWN_LIMIT_TYPE)
        
    def __getstate__(self):
        state = BaseBuilding.__getstate__(self)
        state.add_data(self, "path", self.path)
        return state
    
    def __setstate__(self, state):
        BaseBuilding.__setstate__(self, state)
        self.path = state.get_data(self, "path")
        
    def is_interactable(self):
        return True
    
    def interact(self):
        gameState = GameState.get_main_gamestate()
        if (self._spawned < self.SPAWN_LIMIT) and (gameState.get_building_clicks() <= int(gameState.get_max_building_clicks()) - 1 and (self._my_spawn_limit > 0)):
            self._spawned += 1
            self._my_spawn_limit -= 1
            gameState.update_building_clicks(True)
            for _ in range(self.SPAWN_COUNT):
                creep = self.do_spawn()
                gameState.update_living_creeps(True)
                creep.attach_to_path(self.path)
            sound.play_sound(self.SPAWN_SOUND)
            self._do_spawn_effect()
        else:
            sound.play_sound(self.ZONK_SOUND)
    
    def _do_spawn_effect(self):
        pass
    
    def do_spawn(self, path):
        pass
    
    
class FastFood(FASTFOOD, Spawner):
    
    def __init__(self):
        Spawner.__init__(self)
    
    def do_spawn(self):
        return Fatso()


class Orphanage(ORPHANAGE, Spawner):
    
    def __init__(self):
        Spawner.__init__(self)
    
    def do_spawn(self):
        return Orphan()    
        
        
class Beergarden(BEERGARDEN, Spawner):
    
    def __init__(self):
        Spawner.__init__(self)

    def do_spawn(self):
        return Drunk()
    
    
    