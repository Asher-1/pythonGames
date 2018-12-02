'''
Created on 15.09.2011

@author: Archy
'''

import data 

from game import Entity
from renderables import Sprite

from globals import ARCHETYPE

class Beauty(Entity):

    _Sprite = None
    _TextureName = None
    _z_index = 0
    _Scale = 1.0
    
    def __init__(self):
        Entity.__init__(self)
        
    def __getstate__(self):
        state = Entity.__getstate__(self)
        state.add_data(self, "_TextureName", self._TextureName)
        state.add_data(self, "_z_index", self._z_index)
        state.add_data(self, "_Scale", self._Scale)
        return state
    
    def __setstate__(self, state):
        Entity.__setstate__(self, state)
        self.set_texture_name(state.get_data(self, "_TextureName", "deco_tree.png" ))
        self.set_z_index(state.get_data(self, "_z_index"))
        self.set_scale(state.get_data(self, "_Scale", 1.0))
        
        # convert to new version
        if self._TextureName.startswith("path_") and not isinstance(self, Markable):
            street = Markable()
            street.__setstate__(state)
            self.delete() 
    
    def set_z_index(self, z_index):
        self._z_index = z_index
        if self._Sprite: self._Sprite.set_z_index(self._z_index)
        
    def set_texture_name(self, textureName):
        if self._Sprite: self._Sprite.delete()
        self._TextureName = textureName
        if not self._TextureName: return
        self._Sprite = Sprite()
        self.add_renderable(self._Sprite)
        self._Sprite.set_texture(data.load_texture(self._TextureName))
        self._Sprite.set_rotation(self.get_rotation())
        self._Sprite.set_position(self.get_position())
        self._Sprite.set_z_index(self._z_index)
        self.set_scale(self._Scale)
        
    def set_rotation(self, rotation):
        Entity.set_rotation(self, rotation)
        if self._Sprite: self._Sprite.set_rotation(rotation)
        
    def set_position(self, position):
        Entity.set_position(self, position)
        if self._Sprite: self._Sprite.set_position(position)
        
    def get_scale(self):
        return self._Scale
    
    def set_scale(self, scale):
        self._Scale = scale
        if self._Sprite: self._Sprite.set_scale(self._Scale)
    
    def set_color(self, *color):
        if self._Sprite: self._Sprite.set_color(*color)
                 
class BaseMarking:
    
    timeToLive= 0.0
    timeLeft = 0.0
    
    def __init__(self, timeToLive):
        self.timeToLive = timeToLive
        self.timeLeft = self.timeToLive
    
    def update(self, carrier, gameTime, deltaTime):
        self.timeLeft = max(0.0, self.timeLeft - deltaTime)
        norm = self.timeLeft / self.timeToLive
        invnorm = 1.0 - norm
        r = norm * 1.0   + invnorm * 1.0  
        g = norm * 0.298 + invnorm * 1.0  
        b = norm * 0.0   + invnorm * 1.0  
        carrier.set_color(r, g, b)
        if self.timeLeft <= 0.0:
            return True
        return False

    def on_creep_enter(self, creep):
        pass
        
    def on_creep_leave(self, creep):
        pass

class Markable(Beauty):
        
    _Markings = None
    addToGrid = True
    
    _ArcheType = ARCHETYPE.MARKABLE
    
    _Creeps = None
    
    def __init__(self):
        Beauty.__init__(self)
        self._Markings = []
        self._Creeps = set()
        
    def add_marking(self, marking):
        self._Markings.append(marking)
        for creep in self._Creeps:
            marking.on_creep_enter(creep)
    
    def update(self, gameTime, deltaTime):
        Beauty.update(self, gameTime, deltaTime)
        toRemove = []
        for marking in self._Markings:
            if marking.update(self, gameTime, deltaTime):
                toRemove.append(marking)
        for marking in toRemove:
            self._Markings.remove(marking)
            
    def set_position(self, position):
        Beauty.set_position(self, position)
        self.update_grid_pos()

    def on_creep_enter(self, creep):
        self._Creeps.add(creep)
        for marking in self._Markings:
            marking.on_creep_enter(creep)
        
    def on_creep_leave(self, creep):
        self._Creeps.remove(creep)
        for marking in self._Markings:
            marking.on_creep_leave(creep)
        
    def creeps(self):
        for creep in self._Creeps:
            yield creep


from pyglet.window import MouseCursor
from renderables import FastSprite
from renderables import BatchRenderer

class UfoCursor(MouseCursor):
    
    drawable = True
    
    _batch = None
    _sprite = None
    
    rotationSpeed = 50.0
        
    def __init__(self, image):
        self.texture = image.get_texture()
        
        self._batch = BatchRenderer(False)
        self._sprite = FastSprite(self._batch, image)
        self._sprite.set_anchor(0.5, 0.5)
        self._sprite.set_scale(1.25)
        
    def update(self, gameTime, deltaTime, position):
        self._sprite.rotation = self._sprite.rotation + deltaTime * self.rotationSpeed
        self._sprite.set_position(position.x, position.y)
        self._batch.render(gameTime, deltaTime)
        
    def draw(self, x, y):
        pass

            