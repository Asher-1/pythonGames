'''
Created on 15.09.2011

@author: Archy

'''

import data

from game import Entity
from renderables import Sprite

from globals import Z_INDICES
from random import Random

from math2d import Vector2

class Particle(Sprite):
    
    spawned = False
    oneOverInitial = 0.0
    liveTime = 0.0
    speed = 0.0
    direction = Vector2()
    
    rnd = Random()
    
    def __init__(self, renderCallback=False):
        Sprite.__init__(self, renderCallback=renderCallback)
        
        self.set_z_index(Z_INDICES.PARTICLES)
        self.set_visible(False)
    
    def clear(self):
        self.spawned = False
        self.oneOverInitial = 0.0
        self.liveTime = 0.0
        self.speed = 0.0
        
    def set_livetime(self, minimum, maximum):
        self.oneOverInitial = 1.0 / minimum + (maximum - minimum) * self.rnd.random()
    
    def init_rotation(self, minimum, maximum):
        offset = minimum + (maximum - minimum) * self.rnd.random()
        self.set_rotation(self.get_rotation() + offset)
    
    def set_rotation(self, rotation):
        Sprite.set_rotation(self, rotation)
        self.direction = Vector2.from_rotation(rotation)
        
    def init_speed(self, minimum, maximum):
        self.speed = minimum + (maximum - minimum) * self.rnd.random()
    
    
class ParticleSystem(Entity):
    
    _Running = False
    
    _Texture = None
    _SpawnCount = 10
    _SpawnLength = 1.0
    _Looped = False
    _LiveTime_Min = 0.5
    _LiveTime_Max = 1.0
    _Rotation_Min = -180.0
    _Rotation_Max = 180.0
    
    _Speed_Min = 20.0
    _Speed_Max = 40.0
    
    _Particles = None
    _Spawned = None
    _Free = None
    
    _SpawnedCount = 0
    _Runtime = 0.0
    
    def __init__(self):
        Entity.__init__(self)
            
    def start(self):
        self._Particles = [Particle() for _ in range(self._SpawnCount)]
        for particle in self._Particles:
            particle.set_texture(self._Texture)
        self._Spawned = []
        self._Free = []
        self._Free[:] = self._Particles
        
        self._Running = True
        self._Runtime = 0.0 
    
    def stop(self):
        if not self._Running: return
        self._Running = False
        for particle in self._Spawned:
            self.despawn_particle(particle)
        for particle in self._Particles:
            particle.delete()
        self._Particles[:] = []
        self._Spawned[:] = []
        self._Free[:] = []
    
    def update(self, gameTime, deltaTime):
        Entity.update(self, gameTime, deltaTime)
        
        if not self._Running: return
        
        for i in range(len(self._Spawned)-1, -1, -1):
            particle = self._Spawned[i]
            if particle.spawned:
                self.think_particle(particle, gameTime, deltaTime)
                
        self._Runtime += deltaTime
        
        if self._SpawnLength <= 0.0 : 
            fullRequired = 1.0        
        else:
            fullRequired = (self._Runtime / self._SpawnLength)
        
        if not self._Looped: 
            fullRequired = min(fullRequired, 1.0)
        
        required = int(fullRequired * self._SpawnCount)
        toSpawn = min(required - self._SpawnedCount, len(self._Free))
        
        if fullRequired >= 1.0 and not self._Looped and toSpawn == 0:
            if len(self._Spawned) == 0:
                self.stop()
                self.delete()
                return
                    
        for _ in range(toSpawn):
            particle = self._Free.pop()
            self._Spawned.append(particle)
            self._SpawnedCount += 1
            self.spawn_particle(particle)
    
    def spawn_particle(self, particle):
        self.add_renderable(particle)
        particle.clear()
        particle.set_position(self.get_position())
        particle.set_rotation(self.get_rotation())
        particle.set_livetime(self._LiveTime_Min, self._LiveTime_Max)
        particle.init_rotation(self._Rotation_Min, self._Rotation_Max)
        particle.init_speed(self._Speed_Min, self._Speed_Max)
        particle.set_visible(True)
        particle.spawned = True
        self.think_particle(particle, 0.0, 0.0)
    
    def despawn_particle(self, particle):
        particle.spawned = False
        particle.set_visible(False)
        self.remove_renderable(particle)
        self._Spawned.remove(particle)
        self._Free.append(particle)
    
    def think_particle(self, particle, gameTime, deltaTime):
        particle.liveTime += deltaTime
        lifeTime = particle.liveTime * particle.oneOverInitial
        sqLifeTime = lifeTime*lifeTime 
        if lifeTime > 1.0:
            self.despawn_particle(particle)
            return False
        else:
            invSqLifeTime = 1.0 - sqLifeTime
            speed = particle.speed * invSqLifeTime
            particle.set_position(particle.get_position() + particle.direction * (speed * deltaTime))
            particle.set_alpha(invSqLifeTime)
            return True


class AlienThingy(ParticleSystem):

    _LiveTime_Min = 1.0
    _LiveTime_Max = 1.0
    
    _Rotation_Min = 90.0
    _Rotation_Max = 90.0
    
    _Speed_Min = -180.0
    _Speed_Max = -180.0
    
    _Alternating = 1.0
    
    def __init__(self):
        ParticleSystem.__init__(self)
        self._Looped = True
        
        self._Texture = data.load_texture("alieny.png")
        self._SpawnCount = 20
        self._SpawnLength = 1.0 
    
    def spawn_particle(self, particle):
        ParticleSystem.spawn_particle(self, particle)
        position = particle.get_position()        
        
        self._Alternating *= -1.0 
        random = particle.rnd.random()
        random = random**1.6
        
        particle.speed += random * 100.0
        position.y += self._Alternating * random * 15.0
        particle.set_position(position)
        particle.set_scale(1.0 + particle.rnd.random())
        particle.set_color(0.1, 0.6, 1.7)
    
    def think_particle(self, particle, gameTime, deltaTime):
        if not ParticleSystem.think_particle(self, particle, gameTime, deltaTime):
            return False
        
        lifeTime = particle.liveTime * particle.oneOverInitial
        lifeTime = ((lifeTime - 0.5) * 2) ** 2
        particle.set_alpha(1.0 - lifeTime)
        
class SmokeExplosion(ParticleSystem):

    _LiveTime_Min = 0.725
    _LiveTime_Max = 1.2
    
    _Rotation_Min = -180.0
    _Rotation_Max = 180.0
    
    _Speed_Min = 30.0
    _Speed_Max = 80.0
    
    _Color = (255,255,255)
    
    def __init__(self):
        ParticleSystem.__init__(self)
        self._Looped = False
        
        self._Texture = data.load_texture("smoke.png")
        self._SpawnCount = 10
        self._SpawnLength = 0.2 
    
    def set_color(self, color):
        self._Color = color
    
    def spawn_particle(self, particle):
        ParticleSystem.spawn_particle(self, particle)
        particle.set_color(*self._Color)
        
    def think_particle(self, particle, gameTime, deltaTime):
        if not ParticleSystem.think_particle(self, particle, gameTime, deltaTime):
            return
        lifeTime = particle.liveTime * particle.oneOverInitial
        invLiveTime = 1.0 - lifeTime
        particle.set_scale(0.25 + 1.5 * invLiveTime)        
        
        
class Explosion(ParticleSystem):

    _LiveTime_Min = 0.425
    _LiveTime_Max = 0.7
    
    _Rotation_Min = -180.0
    _Rotation_Max = 180.0
    
    _Speed_Min = 100.0
    _Speed_Max = 200.0
    
    def __init__(self):
        ParticleSystem.__init__(self)
        self._Looped = False
        
        self._Texture = data.load_texture("bullet_grenade.png")
        self._SpawnCount = 10
        self._SpawnLength = 0.2        
        
        
class ArtilleryHit(Explosion):
    
    _Rotation_Min = -15.0
    _Rotation_Max = 15.0
    
    def __init__(self):
        Explosion.__init__(self)
        
        self._Texture = data.load_texture("bullet_gatling.png")
        self._SpawnCount = 10
        self._SpawnLength = 0.0
