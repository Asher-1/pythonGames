'''
Contains code for different levels of the game.
Levels render in a window, handle input, and update
the entities they contain.

'''

import pyglet
from pyglet.window import key
from pyglet.gl import *
import joystick
from entities import *
from constants import *
import config
import levels
import data
import math
from numpy import arange
if DEBUG:
    from debug import *

PATH_POINTS = 50.0

# hit box helpers.
HITBOX_X = lambda hitbox: hitbox[0]
HITBOX_Y = lambda hitbox: hitbox[1]
HITBOX_WIDTH = lambda hitbox: hitbox[2]
HITBOX_HEIGHT = lambda hitbox: hitbox[3]

class Hud(Entity):
    entity_type = None
    def __init__(self, parent_level):
        self.x = 0
        self.y = SIZE_OF_GAMESPACE_Y
        self._scale = 1

        self._lables = []
        self._hud_background = None

        Entity.__init__(self, parent_level)

    def ConstructHud(self, contents):

        max_x = 0
        y = 5
        self._lables = []
        contents.reverse()
        for line in contents:
            label = pyglet.text.Label(line, font_size=20*self._scale)
            max_x = max(max_x, label.content_width)
            self._lables.append((label, 0, y))
            y = y + label.content_height + 5
     
        hud_texture = pyglet.image.SolidColorImagePattern((0, 0, 0, 255))
        hud_image = pyglet.image.create(max_x, y, hud_texture)
        self._hud_background = pyglet.sprite.Sprite(hud_image)
        self._hud_background.image.anchor_y = self._hud_background.image.height
        self._hud_background.scale = float(self._scale)
        
    def Rescale(self, NewScaleFactor):
        Entity.Rescale(self, NewScaleFactor)
        self._scale = NewScaleFactor
        if self._hud_background is not None:
            self._hud_background.scale = float(NewScaleFactor)
        for label, x, y in self._lables:
            label.font_size = 20*self._scale
                    
    def Tick(self, delta_t):
        ships = self.parent_level.get_objects_of_interest(TYPE_PLAYER_SHIP)
        if len(ships) > 0:
            contents = ships[0].getHudContents()
            self.ConstructHud(contents)
        Entity.Tick(self, delta_t)
        
    def draw(self):
        Entity.draw(self)
        if self._hud_background is not None:
            self._hud_background.x = self.GetScaledX(self.x)
            self._hud_background.y = self.GetScaledY(self.y)
            self._hud_background.draw()
        
        for label, x, y in self._lables:
            label.x = self.GetScaledX(self.x + x)
            label.y = self.GetScaledY(self.y - self._hud_background.image.height + y)
            label.draw()

class Player(Actor, Oscillator):
    '''
    The main player object. This derives from Oscillator and adds in sprite rendering capabilities.
    This is the rendering side of the Oscillator object.
    '''
    
    entity_type = TYPE_PLAYER_SHIP
    
    def __init__(self, parent_level):
        sprite_image = data.load_image('Ship.png')
        sprite_image.anchor_y = sprite_image.height/2
        Actor.__init__(self, sprite_image, parent_level)
        Oscillator.__init__(self)
        self.x = PLAYER_OFFFSET_FROM_RIGHT_SCREEN_BOUND
        self.y = SIZE_OF_GAMESPACE_Y//2
        self.z = 1 #draw this above other stuff

        self._original_color = self.sprite.color
        self.line_color = (1,1,1,1)
        self.shield = STARTING_SHIELDS
        self.collision_cooldown = 0
        self._hitting_terrain = False
        self.dpad = joystick.DPad()

    def getHudContents(self):
        timeleft = self.parent_level.endtime - self.parent_level.timeline._current_time
        return ["Shields:{0}".format(int(self.shield)),
                "Next Level In {0}".format(int(timeleft))]

    def Rescale(self, NewScaleFactor):
        super(Player, self).Rescale(NewScaleFactor)

    def Tick(self, dt):
        Oscillator.Tick(self, dt)
        shipPos = self.GetCurrentValue()
        self.y  = SIZE_OF_GAMESPACE_Y//2 + (shipPos * SIZE_OF_GAMESPACE_Y//2)
        if self.hitting_terrain:
            self.shield -= SHIELD_TERRAIN_DRAIN_RATE
        self.shield = min(self.shield + SHIELD_CHARGE_RATE * dt * self._Omega,  MAX_SHIELDS)
        if self.shield < 0:
            self.die()
        if (self.collision_cooldown > 0):
            self.collision_cooldown = max(self.collision_cooldown - dt, 0)
        
    def handle_input(self, keys):
        self.dpad.update()
        if keys[key.UP] and not keys[key.DOWN] or self.dpad.axis1 < 0:
            self.AmplitudeAdjust = INCREASE
        elif keys[key.DOWN] and not keys[key.UP] or self.dpad.axis1 > 0:
            self.AmplitudeAdjust = DECREASE
        else:
            self.AmplitudeAdjust = CONSTANT

        if keys[key.LEFT] and not keys[key.RIGHT] or self.dpad.axis0 < 0:
            if config.reverse_frequency_keys:
                self.FrequencyAdjust = DECREASE
            else:
                self.FrequencyAdjust = INCREASE
        elif keys[key.RIGHT] and not keys[key.LEFT] or self.dpad.axis0 > 0:
            if config.reverse_frequency_keys:
                self.FrequencyAdjust = INCREASE
            else:
                self.FrequencyAdjust = DECREASE
        else:
            self.FrequencyAdjust = CONSTANT

        #=======================================================================
        # if keys[key.SPACE]:
        #    self.frozen = True
        # else: 
        #    self.frozen = False
        #=======================================================================


    def get_hitting_terrain(self):
        return self._hitting_terrain
    def set_hitting_terrain(self, hit):
        if not hit and self._hitting_terrain:
            self.on_terrain_depart()
        if hit and not self._hitting_terrain:
            self.on_terrain_contact()
        self._hitting_terrain = hit

    hitting_terrain = property(get_hitting_terrain, set_hitting_terrain)

    def on_terrain_contact(self):
        pass
    def on_terrain_depart(self):
        pass

    def reset_color(self):
        if self.hitting_terrain:
            self.sprite.color = (255,128,0)
        elif (self.collision_cooldown > 0):
            self.sprite.color = (255, 0, 0)
        else:
            self.sprite.color = self._original_color

    def on_collision(self):
        if (self.collision_cooldown > 0):
            return
        self.sprite.color = (255, 0, 0)
        self.shield -= 500
        self.collision_cooldown = COLLISION_COOLDOW

    def die(self):
        self.parent_level.ChangeSplash('ShipExploded.png')

    def get_collidable(self):
        return SpriteCollision(self.sprite)

    def draw(self):
        self.sprite.x = self.GetScaledX(self.x)
        self.sprite.y = self.GetScaledY(self.y)
        self.draw_path()
        Actor.draw(self)
        if DEBUG:
            draw_bounding_box(self.sprite)
        
    def draw_path(self):
        glColor4f(*self.line_color) 
        glLineWidth(2)
        glBegin(GL_LINE_STRIP)
        for time in arange(0, SECONDS_TO_CROSS_GAMESPACE, 0.2/self._Omega):
            t, y, a = self.GetPredictiveCoordinate(time)
            x = self.GetScaledX(SIZE_OF_GAMESPACE_X * t/float(SECONDS_TO_CROSS_GAMESPACE) + self.x + self.sprite.width/2)
            y = self.GetScaledY(SIZE_OF_GAMESPACE_Y//2 + (y * SIZE_OF_GAMESPACE_Y//2))
            glVertex2f(x,y)
        glEnd()
        glLineWidth(1)
        glColor4f(1, 1, 1, 1) 

