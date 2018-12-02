'''
Created on 12.09.2011

@author: Archy
'''

import math

def interpolate_rotation(fromRotation, toRotation, rotationSpeed, deltaTime):
    rotationDiff = toRotation - fromRotation
    sign = math.copysign(1.0, rotationDiff)
    rotationDiff = sign * rotationDiff
    
    rotationDiff %= 360.0
    if rotationDiff > 180.0: 
        rotationDiff = 360.0 - rotationDiff
        sign *= -1.0
    
    rotationDone = deltaTime * rotationSpeed
    return sign * min(rotationDiff, rotationDone), rotationDone >= rotationDiff  

class Vector2:
    x, y = 0.0, 0.0
    
    def __init__(self, x = 0.0, y = 0.0):
        if isinstance(x, Vector2):
            self.x = x.x
            self.y = x.y
        else:
            self.x = float(x)
            self.y = float(y)
            
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def get_length(self):
        return math.sqrt(self.dot(self))
    
    def get_sq_length(self):
        return self.dot(self)
    
    def normalize(self):
        return Vector2(self) * (1.0 / self.get_length())
    
    def clamp(self, lower, upper):
        newVector = Vector2(self)
        newVector.x = max(min(newVector.x, upper.x), lower.x)
        newVector.y = max(min(newVector.y, upper.y), lower.y)
        return newVector
    
    def to_rotation(self):
        """Uses this vector as a direction vector and returns the cw rotation around z"""
        norm = self.normalize()
        
        rotation = math.copysign(math.acos(norm.y), norm.x)
        rotation = 180.0 * rotation / math.pi
        
        return rotation
    
    def rotate(self, rotation):
        norm = self.normalize()
        currentRad = math.atan2(norm.y, norm.x)
        currentRad += rotation / 180.0 * math.pi
        return self.from_rotation(currentRad)
    
    @staticmethod
    def from_rotation(rotation):
        rad = rotation / 180.0 * math.pi
        x = math.sin(rad)
        y = math.cos(rad)
        return Vector2(x, y)
    
    def right_vector(self):
        return Vector2(self.y, -self.x)
        
    def to_tuple(self):
        return (self.x, self.y)
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x * other.x, self.y * other.y)
        else:
            x = self.x * other
            y = self.y * other
            return Vector2(x, y)
        

class AARect2d:
    
    isZero = False
    minimum = Vector2()
    maximum = Vector2()
    
    def __init__(self, minimum = None, maximum = None):
        if minimum == None: self.isZero = True
        self.minimum = minimum
        self.maximum = maximum
    
    def integrate(self, rect):
        if self.isZero:
            self.minimum = rect.minimum
            self.maximum = rect.maximum
            self.isZero = False
        else:
            self._integrate_point(rect.minimum)
            self._integrate_point(rect.maximum)
            
    def _integrate_point(self, point):
        self.minimum.x = min(self.minimum.x, point.x)
        self.minimum.y = min(self.minimum.y, point.y)
        self.maximum.x = max(self.maximum.x, point.x)
        self.maximum.y = max(self.maximum.y, point.y)
    
    def contains(self, point):
        if self.isZero: return False
        if point.x < self.minimum.x or point.y < self.minimum.y or point.x >= self.maximum.x or point.y >= self.maximum.y:
            return False
        return True
    
    def intersects(self, rect):
        if self.isZero: return False
        if self.maximum.x < rect.minimum.x or self.minimum.x > rect.maximum.x or self.maximum.y < rect.minimum.y or self.minimum.y > rect.maximum.y:
            return False
        return True
    
    def get_size(self):
        if self.isZero: return Vector2()
        return self.maximum - self.minimum
    
    
    