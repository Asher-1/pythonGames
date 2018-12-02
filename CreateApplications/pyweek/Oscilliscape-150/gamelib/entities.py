
import pyglet

from constants import *
import levels
import random
import data
import math
from collide import *
from pyglet.window import key
from constants import *
if DEBUG:
    import debug

TWOPI = (2*math.pi)

# calculates the amp movement of the ship
AMPLITUDE_ACCEL_FUNC = lambda t, accel: min(MAX_AMPLITUDE_VELOCITY * t + accel, MAX_AMPLITUDE_VELOCITY)
FREQUENCY_ACCEL_FUNC = lambda t, accel: min(MAX_FREQUENCY_VELOCITY * t + accel, MAX_FREQUENCY_VELOCITY)

def SinusoidToCartesian(A, omega, t , phi):
    """
        A = Amplitude
        omega = angular frequency, (1/omega gives period)
        phi = phase
    """
    y = A * math.sin(omega * t + phi)
    x = A * math.cos(omega * t + phi)
    return (x,y)

class Entity(object):
    entity_type = None
    def __init__(self, parent_level, layer = 2):
        self.parent_level = parent_level

        self._scaleFactor = 1
        self._x_offset = 0
        self._y_offset = 0

        self.parent_level.register_entity(self, layer, self.entity_type)


    def Rescale(self, NewScaleFactor):
        self._scaleFactor = NewScaleFactor

    def SetOffsets(self, x, y):
        self._x_offset = x
        self._y_offset = y

    def GetScaledX(self, x):
        return x * self._scaleFactor + self._x_offset

    def GetScaledY(self, y):
        return y * self._scaleFactor + self._y_offset

    def delete(self):
        self.parent_level.remove_entity(self, self.entity_type)

    def draw(self):
        pass

    def Tick(self, delta_t):
        pass
    
class Actor(Entity):
    entity_type = None
    def __init__(self, sprite_image, parent_level, layer = 2):
        self.sprite = pyglet.sprite.Sprite(sprite_image)
        self.collider = SpriteCollision(self.sprite) 
        Entity.__init__(self, parent_level, layer)

    def Rescale(self, NewScaleFactor):
        Entity.Rescale(self, NewScaleFactor)
        self.sprite.scale = float(NewScaleFactor)

    def draw(self):
        self.sprite.draw()
        
    # Return the sprite for this entity, if any
    def get_collidable(self):
        pass
        
class Oscillator(object):
    def __init__(self):

        self._Amplitude = .5
        self._Omega = math.pi
        self._Phase = 0.0
        self._t = 0.0

        self.AmplitudeVelocity = 0
        self.FrequencyVelocity = 0

        self.frozen = False

        self.AmplitudeAdjust = CONSTANT
        self.FrequencyAdjust = CONSTANT

    def Tick(self, delta_t):
        """
        Simulate the passage of time on the ships sinusodial position.

        We mod t by 2pi/omega to keep it small. Anytime we
        would adjust the angularFrequency we end up zeroing t anyway.

        One more step along the inevitable march of time
        One more step closer to the heat-death of the universe
        """
        if not self.frozen:
            self._t = (self._t + delta_t) % (TWOPI/self._Omega)

        if self.AmplitudeAdjust == INCREASE:
            self.AmplitudeVelocity = AMPLITUDE_ACCEL_FUNC(delta_t, self.AmplitudeVelocity)
            self.AdjustAmplitude(self.AmplitudeVelocity)
        elif self.AmplitudeAdjust == DECREASE:
            self.AmplitudeVelocity = -AMPLITUDE_ACCEL_FUNC(delta_t, abs(self.AmplitudeVelocity))
            self.AdjustAmplitude(self.AmplitudeVelocity)
        else:
            self.AmplitudeVelocity = 0


        if self.FrequencyAdjust == INCREASE:
            self.FrequencyVelocity = FREQUENCY_ACCEL_FUNC(delta_t, self.FrequencyVelocity)
            self.AdjustAngularFrequency(self.FrequencyVelocity)
        elif self.FrequencyAdjust == DECREASE:
            self.FrequencyVelocity = -FREQUENCY_ACCEL_FUNC(delta_t, abs(self.FrequencyVelocity))
            self.AdjustAngularFrequency(self.FrequencyVelocity)
        else:
            self.FrequencyVelocity = 0


    def AdjustAmplitude(self, deltaAmp):
        """
        Adjust the Amplitude of the ships waveform while maintaining its current position.

        Unfortunately this is a nasty operation. We need to compute a new Phase/Time such
        that the ships new position within the waveform with the higher amplitude matches
        its current position. This means inverse trig (arcSin in particular).

        The formula is pretty strait forward though:

        given: Theta = Omega * t + Phi

        A1 * Sin(Theta1) = A2 * Sin(Theta2)

        becomes

        Theta2 = ArcSin((A1 * Sin(Theta1))/A2)

        Of course, we have a problem here, there are actually TWO solutions to this equation
        one for the ascending edge, and one for the falling edge (there is only one solution
        at the peaks and valleys of course).

        Once we have Theta2, we can set time to 0 and calculate a new phase offset, modding
        the phase by TWOPI to keep it small.

        I know I don't need all these intermediate variables, but for readability and
        ease of development I'll leave them this way for now.

        NOTE: Since we check that the current position is farther from 0 than the new
        amplitude we can avoid those nasty situations where ArcSin does not exist.

        """

        currentPos = self.GetCurrentValue()
        oldTheta = (self._Omega * self._t + self._Phase) % (2 * math.pi)
        
        # Cap the change in amplitude to our current velocity
        current_velocity = self._Amplitude * math.cos(oldTheta)
        if (((deltaAmp > 0) and (current_velocity > 0) and (deltaAmp > current_velocity))
            or((deltaAmp < 0) and (current_velocity < 0) and (deltaAmp < current_velocity))):
                deltaAmp = self._Amplitude * math.cos(oldTheta)
            

        newAmp = self._Amplitude + deltaAmp
        if (abs(currentPos) > newAmp):
            if(currentPos > 0):
                currentPos = newAmp
            else:
                currentPos = -newAmp

        if (newAmp > MAX_AMPLITUDE) or (newAmp < MIN_AMPLITUDE):
            self.AmplitudeVelocity = 0
            return
#===============================================================================
# 
#        # lim (x -> inf) asin(x) = 0
#        if (newAmp != 0):
#            newPhase = math.asin(currentPos/newAmp)
#        else:
#            newPhase = 0
# 
#        # asin returns values between -pi/2 and pi/2, we use values between 0 and 2*pi
#        if (newPhase < 0):
#            newPhase += (2*math.pi)
# 
#        # asin has multiple solutions everywhere that isn't a peak or a trough
#        # by default, asin always returns the solution between -pi/2 and pi/2
#        # (quadrants 0 and 3), to maintain continuity we want to use the solutions
#        # from pi/2 to 3pi/2 (quadrants 1 and 2) if that was where the original
#        # position was located
#        if ( (math.pi/2) < oldTheta <= (math.pi) ):
#            #Adjust the new phase to be in quadrant 1
#            newPhase = math.pi - newPhase
#        elif ( (math.pi) < oldTheta <= ((math.pi*3)/2) ):
#            #Adjust the new phase to be in quadrant 2
#            newPhase = math.pi + (2*math.pi - newPhase)
#        newt = 0.0
#
#        self._Amplitude, self._Phase, self._t = newAmp, newPhase, newt
#
#===============================================================================

        self._Amplitude = newAmp

    def AdjustAngularFrequency(self, deltaFreq):
        """
        Adjust the angular frequency of the ships waveform while maintaining its current position.

        While adjusting the Angular Frequency we need to adjust the Time t) and phase such
        that:

        Omega1 * t1 = Phi1 = Omega2 * t2 = Phi2

        To make this easy, we just reset time to 0 and calculate the new phase offset.

        t2 = 0
        Phi2 = Omega1 * t1 = Phi1

        Finally, we mod Phi2 by TWOPI to keep it small.

        I know I don't need all these intermediate variables, but for readbility and
        ease of development I'll leave them this way for now.
        """
        oldFreq, oldPhase, oldt = self._Omega, self._Phase, self._t

        newFreq = oldFreq + deltaFreq

        if (newFreq > MAX_FREQUENCY) or (newFreq < MIN_FREQUENCY):
            self.FrequencyVelocity = 0
            return

        newPhase = (oldFreq * oldt + oldPhase) % TWOPI
        newt = 0.0

        self._Omega, self._Phase, self._t = newFreq, newPhase, newt


    def AdjustPhase(self, deltaPhase):
        """
        Adjust the phase of the ships waveform. By definition this operation SHOULD alter the ships position.

        I actually don't know if we will need this
        """
        self._Phase += deltaPhase % TWOPI

    def GetCurrentValue(self):
        return self.GetFutureValue(0)

    def GetFutureValue(self, t_future):
        return self._Amplitude * math.sin(self.GetFutureTheta(t_future))

    def GetTheta(self):
        return self.GetFutureTheta(0)

    def GetFutureTheta(self, t_future):
        return ((self._Omega * (self._t + t_future)) + self._Phase)
    
    def GetAngle(self):
        return self.GetFutureAngle(0)

    def GetFutureAngle(self, t_future):
        return self._Amplitude * math.cos(self.GetFutureTheta(t_future)) * 90.0

    def GetPredictiveCoordinate(self, t_future):
        return (t_future, self.GetFutureValue(t_future), self.GetFutureAngle(t_future))

    def GetPredictivePath(self, t_start, t_stop, t_step):

        assert(t_start < t_stop)
        assert(t_step > 0)
        path = []
        t_cursor = t_start

        while(t_cursor < t_stop):
            path.append(self.GetPredictiveCoordinate(t_cursor))
            t_cursor += t_step
        return path

class HostileShip(Actor):
    
    entity_type = TYPE_HOSTILE_SHIP
    def __init__(self, starting_x, starting_y, speed, parent_level, sprite_number = 1):
        if sprite_number == 1:
            sprite_image = data.load_image('Enemy1.png')
        elif sprite_number == 2:
            sprite_image = data.load_image('Enemy2.png')
        elif sprite_number == 3:
            sprite_image = data.load_image('Enemy3.png')
        elif sprite_number == 3:
            sprite_image = data.load_image('Enemy4.png')
        else:
            sprite_image = data.load_image('enemy.png')
            
        sprite_image.anchor_y = sprite_image.height/2  
        Actor.__init__(self, sprite_image, parent_level)

        self._x = starting_x
        self._y = starting_y
        self.speed = speed
                
    def Rescale(self, NewScaleFactor):
        Actor.Rescale(self, NewScaleFactor)
        self.sprite.scale = float(NewScaleFactor)

    def Tick(self, delta_t):
        self._x = self._x - (SIZE_OF_GAMESPACE_X * (delta_t / SECONDS_TO_CROSS_GAMESPACE) + (self.speed * delta_t/abs(delta_t)))

        Actor.Tick(self, delta_t)
        
        if self._x <= 0:
            self.delete()
        
    def draw(self):
        self.sprite.x = self.GetScaledX(self._x)
        self.sprite.y = self.GetScaledY(self._y)
        Actor.draw(self)
        if DEBUG:
            debug.draw_bounding_box(self.sprite)
            
    def get_collidable(self):
        return SpriteCollision(self.sprite) 

class Debris(Actor):
    entity_type = TYPE_DEBRIS
    def __init__(self, starting_x, starting_y, parent_level):
        # this should mb come in as a parameter 
        # or we should choose at random, but we need to know from what set
        sprite_image = data.load_image('Level1Debris1.png')
        sprite_image.anchor_x = sprite_image.width/2
        sprite_image.anchor_y = sprite_image.height/2
        Actor.__init__(self, sprite_image, parent_level)
        self.x = starting_x
        self.y = starting_y
        self.vx = 0
        self.vy = 0

    def Tick(self, dt):
        self.x = self.x - (SIZE_OF_GAMESPACE_X * (dt / SECONDS_TO_CROSS_GAMESPACE))

    def draw(self):
        self.sprite.x = self.GetScaledX(self.x)
        self.sprite.y = self.GetScaledY(self.y)
        Actor.draw(self)

    def get_collidable(self):
        return SpriteCollision(self.sprite)

