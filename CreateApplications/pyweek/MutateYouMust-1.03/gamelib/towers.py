'''
Created on 11.09.2011

'''

import math
import data

from game import Entity
from renderables import Sprite
from math2d import Vector2
from math2d import interpolate_rotation

from globals import Z_INDICES

from globals import BASE_TOWER
from globals import BUNKER
from globals import TANK
from globals import ARTILLERY

from globals import BASE_BULLET
from globals import CANNONBALL
from globals import GRENADE
from globals import GATLINGBALL
from globals import ARCHETYPE

from effects import ArtilleryHit
from effects import Explosion

from game import GameState

import sound

class BaseTower(BASE_TOWER, Entity):
    
    _SpriteBody = None
    _SpriteTower = None
    _SpriteRadius = None
    
    _last_rotation_dir = 1.0
    _rotation_speed_idle = 60
    _rotation_speed_aim = 240
    
    _cool_down = 0.0
    _target = None
    _AimTarget = None

    SQ_RADIUS = 0.0
    
    _ArcheType = ARCHETYPE.TOWER
    
    _GridObserver = None

    def __init__(self):
        Entity.__init__(self)
        self.SQ_RADIUS = self.RADIUS * self.RADIUS        
        self.create_sprites(self.TEXTURE_BODY, self.TEXTURE_TOWER)
    
    def delete(self):
        Entity.delete(self)
        if self._GridObserver: 
            self._GridObserver.delete()
            self._GridObserver = None
    
    def show_radius(self, state):
        if state:
            if self._SpriteRadius:
                return
            self._SpriteRadius = Sprite()
            self.add_renderable(self._SpriteRadius, pickable = False)
            self._SpriteRadius.set_texture(data.load_texture("radius.png"))
            self._SpriteRadius.set_position(self.get_position())
            self._SpriteRadius.set_size(Vector2(self.RADIUS*2.0, self.RADIUS*2.0))
            self._SpriteRadius.set_z_index(Z_INDICES.GUI_OVERLAYS)
        else:
            if not self._SpriteRadius:
                return
            self.remove_renderable(self._SpriteRadius)
            self._SpriteRadius.delete()
            self._SpriteRadius = None
    
    def set_position(self, position):
        Entity.set_position(self, position)
        if self._SpriteBody: self._SpriteBody.set_position(position)
        if self._SpriteTower: self._SpriteTower.set_position(position)
        if self._SpriteRadius: self._SpriteRadius.set_position(position)
        if self._GridObserver: 
            self._GridObserver.delete()
            self._GridObserver = None
            
    def set_rotation(self, rotation):
        Entity.set_rotation(self, rotation)
        if self._SpriteBody:
            self._SpriteBody.set_rotation(rotation)
        if self._SpriteTower:    
            self._SpriteTower.set_rotation(rotation)
            
    def update(self, gameTime, deltaTime):
        self._cool_down -= deltaTime
                    
        if not self.check_target():
            self.idle_rotation(gameTime, deltaTime)
        elif self.aim_at_target(self._AimTarget, gameTime, deltaTime) and self._AimTarget == self._target and self._cool_down <= 0.0:
            self.release_bullet()   
    
    def check_target(self):
        if (not self._target) or ( self._target.is_deleted() or self._target.dead_man_walking() or self._out_of_range(self._target) ):
            self._find_new_target()
        return self._AimTarget != None
    
    def _find_new_target(self):
        if not self._GridObserver:
            gameState = GameState.get_main_gamestate()             
            self._GridObserver = gameState.get_grid_observer(self.get_position(), self.RADIUS + 50.0)
            
        bestCreep = None
        bestDist = 10000.0**2.0
        for sqdist, creep in self._GridObserver.content_creep():
            if creep.dead_man_walking():
                continue
            if sqdist < bestDist:
                bestCreep = creep
                bestDist = sqdist
        
        self._AimTarget = bestCreep
        if bestDist <= self.SQ_RADIUS:
            self._target = bestCreep
        else:
            self._target = None
    
    def _out_of_range(self, creep):
        return (self._target.get_walker_position() - self.get_position()).get_sq_length() > self.SQ_RADIUS
        
    #def _soon_dead(self, creep):
    #    gameState = GameState.get_main_gamestate()
    #    damageDone = 0
    #    for bullet in gameState.entities_of_type(ARCHETYPE.BULLET):
    #        if bullet.get_target() == creep:
    #            damageDone += bullet.BULLET_DAMAGE
    #    
    #    return creep.get_life() <= damageDone
    
    def aim_at_target(self, target, gameTime, deltaTime):
        position = self._SpriteTower.get_position()
        rotation = self._SpriteTower.get_rotation()
        rotationReq = (target.get_position() - position).to_rotation()
        
        rotationChange, targetReached = interpolate_rotation(rotation, rotationReq, self._rotation_speed_aim, deltaTime)
        self._last_rotation_dir = math.copysign(1.0, rotationChange)               
        self._SpriteTower.set_rotation(rotation + rotationChange)
        
        return targetReached
    
    def idle_rotation(self, gameTime, deltaTime):
        rotation = self._SpriteTower.get_rotation() + (self._rotation_speed_idle * self._last_rotation_dir * deltaTime)
        self._SpriteTower.set_rotation(rotation)
           
    def create_sprites(self, fileBody, fileTower):
        self._SpriteBody = self.add_renderable(Sprite())
        self._SpriteBody.set_texture(data.load_texture(fileBody))
        self._SpriteBody.set_position(Vector2(0, 0))
        self._SpriteBody.set_z_index(Z_INDICES.TOWER_BODY)
        
        self._SpriteTower = self.add_renderable(Sprite())
        self._SpriteTower.set_texture(data.load_texture(fileTower))
        self._SpriteTower.set_position(Vector2(0, 0))
        self._SpriteTower.set_z_index(Z_INDICES.TOWER_GUN)
    
    def reset_cooldown(self):
        self._cool_down = 1.0 / self.SHOTS_PER_SECOND
        
    def release_bullet(self):
        my_position = self._SpriteTower.get_position()
        CannonBall(my_position, self._target)
        self.reset_cooldown()
    
        
class Tank(TANK, BaseTower):
    
    def __init__(self):
        BaseTower.__init__(self)
        
    def reset_cooldown(self):
        self._cool_down = 1.0 / self.SHOTS_PER_SECOND
        
    def release_bullet(self):
        my_position = self._SpriteTower.get_position()
        CannonBall(my_position, self._target)
        self.reset_cooldown()

    def render(self, gameTime, deltaTime):
        BaseTower.render(self, gameTime, deltaTime)


class Bunker(BUNKER, BaseTower):
    
    _Alternating_State = 1.0
    _LastSoundEmit = 0
    _SoundLen = 0.5
    
    def __init__(self):
        BaseTower.__init__(self)
        
    def reset_cooldown(self):
        self._cool_down = 1.0 / self.SHOTS_PER_SECOND
        
    def release_bullet(self):
        bulletPosition = self._SpriteTower.get_position()
        bulletRotation = self._SpriteTower.get_rotation()
        off_set = Vector2.from_rotation(bulletRotation).right_vector()
        
        self._Alternating_State *= -1.0
        off_set *= self._Alternating_State * 9.0
        bulletPosition += off_set
        GattlingBall(bulletPosition, self._target, targetPosition=self._target.get_position() + off_set, muteSound=True)
        self.reset_cooldown()
    
    def update(self, gameTime, deltaTime):
        BaseTower.update(self, gameTime, deltaTime)
        if self._target:
            self.update_sound(gameTime, deltaTime)
    
    def update_sound(self, gameTime, deltaTime):
        if gameTime - self._LastSoundEmit < self._SoundLen:
            return
        self._LastSoundEmit = gameTime
        sound.play_sound(GATLINGBALL.SHOT_SOUND)
        
    def render(self, gameTime, deltaTime):
        BaseTower.render(self, gameTime, deltaTime)
                

class Artillery(ARTILLERY, BaseTower):
        
    def __init__(self):
        BaseTower.__init__(self)
    
    def reset_cooldown(self):
        self._cool_down = 1.0 / self.SHOTS_PER_SECOND
    
    def release_bullet(self):
        my_position = self._SpriteTower.get_position()
        Grenade(my_position, self._target)
        self.reset_cooldown()
        
    def render(self, gameTime, deltaTime):
        BaseTower.render(self, gameTime, deltaTime)


class BaseBullet(BASE_BULLET, Entity):
    
    _sprite_bullet = None
    _TargetPosition = None
    _TargetEntity = None
    _PathDone = 0.0
    _PathToDo = 0.0
    
    _speed = None
    _movedir = None
    
    _ArcheType = ARCHETYPE.BULLET
    _PlaySound = True
    
    _z_depth_fly = False
    
    def __init__(self, position, targetEntity, targetPosition = None, muteSound = False):
        Entity.__init__(self)
        self.create_sprites(self.TEXTURE)
        self.set_position(position)
        self._TargetEntity = targetEntity
        
        if not targetPosition: targetPosition = targetEntity.get_position()
        self._TargetPosition = targetPosition
        self._PlaySound = not muteSound
    
        self._movedir = self._TargetPosition - position
        self._PathToDo = self._movedir.get_length()
        self._movedir *= 1.0 / self._PathToDo
        
        self.set_rotation(self._movedir.to_rotation())
        self.on_release()
            
    def get_target(self):
        return self._TargetEntity
        
    def set_position(self, position):
        Entity.set_position(self, position)
        if self._sprite_bullet:
            self._sprite_bullet.set_position(position)
            
    def set_rotation(self, rotation):
        Entity.set_rotation(self, rotation)
        if self._sprite_bullet:
            self._sprite_bullet.set_rotation(rotation)
        
    def update(self, gameTime, deltaTime):
        Entity.update(self, gameTime, deltaTime)
        
        framePath = self.BULLET_SPEED * deltaTime
        
        hit = False
        if framePath >= self._PathToDo:
            framePath = self._PathToDo
            hit = True
            
        self._PathDone += framePath
        self._PathToDo -= framePath        
        if self._PathDone > 35.0 and not self._z_depth_fly:
            self._sprite_bullet.set_z_index(Z_INDICES.TOWER_BULLET_FLY)
            self._z_depth_fly = True
        
        self.set_position(self.get_position() + self._movedir * framePath)
        if hit:
            self.on_hit()
    
    def create_sprites(self, fileBullet):
        self._sprite_bullet = self.add_renderable(Sprite())
        self._sprite_bullet.set_texture(data.load_texture(fileBullet))
        self._sprite_bullet.set_position(self.get_position())
        self._sprite_bullet.set_rotation(self.get_rotation())
        self._sprite_bullet.set_z_index(Z_INDICES.TOWER_BULLET)
        
    def on_release(self):
        if self._PlaySound: sound.play_sound(self.SHOT_SOUND)
        self._TargetEntity.register_incoming_damage(self.BULLET_DAMAGE, self.DAMAGE_TYPE)
        
    def on_hit(self):
        if not self._TargetEntity.is_deleted():
            self._TargetEntity.deal_damage(self.BULLET_DAMAGE, self.DAMAGE_TYPE)
        self.delete()


class CannonBall(CANNONBALL, BaseBullet):
    
    def __init__(self, position, targetEntity, targetPosition = None, muteSound=False):
        BaseBullet.__init__(self, position, targetEntity, targetPosition=targetPosition, muteSound=muteSound)
        
    def on_hit(self):
        BaseBullet.on_hit(self)
        sound.play_sound(self.IMPACT_SOUND)
        effect = ArtilleryHit()
        effect.set_position(self.get_position())
        effect.set_rotation(self.get_rotation())
        effect.start()
        
class GattlingBall(GATLINGBALL, BaseBullet):
    
    def __init__(self, position, targetEntity, targetPosition = None, muteSound=False):
        BaseBullet.__init__(self, position, targetEntity, targetPosition=targetPosition, muteSound=muteSound)
        

class Grenade(GRENADE, BaseBullet):
    
    def __init__(self, position, targetEntity, targetPosition = None, muteSound=False):
        BaseBullet.__init__(self, position, targetEntity, targetPosition=targetPosition, muteSound=muteSound)
        
    def on_hit(self):
        BaseBullet.on_hit(self)
        sound.play_sound(self.IMPACT_SOUND)
        effect = ArtilleryHit()
        effect.set_position(self.get_position())
        effect.set_rotation(self.get_rotation())
        effect.start()
        #effect = Explosion()
        #effect.set_position(self.get_position())
        #effect.set_rotation(self.get_rotation())
        #effect.start()