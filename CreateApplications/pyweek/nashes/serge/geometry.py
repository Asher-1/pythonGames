"""Geometric classes"""

import pygame
import math

import common
import serialize

# Some shapes
RECTANGLE = 1
CIRCLE = 2
FRAME = 3 # Rectangle with sides as walls and center is open


class NotClosed(Exception):
    """A shape was not closed"""


class OutOfRange(Exception):
    """A distance was outside of the range"""


class SimpleRect(list):
    """A simple rectangle implementation"""
    
    def __init__(self, *args):
        """Initialise the rectangle"""
        super(SimpleRect, self).__init__(args)
    
    def colliderect(self, other):
        """Return True if this rectangle collides with another"""
        r1 = pygame.rect.Rect(self)
        r2 = pygame.rect.Rect(other)
        return r1.colliderect(r2)
        
    def contains(self, other):
        """Return True if this rectangle contains another"""
        r1 = pygame.rect.Rect(self)
        r2 = pygame.rect.Rect(other)
        return r1.contains(r2)

    def collidepoint(self, x, y):
        """Return True if this rectangle collides with another"""
        r1 = pygame.rect.Rect(self)
        return r1.collidepoint(x, y)

    def inflate(self, w, h):
        """Inflate to new width and height staying in the same centered place"""
        if self[2] == 0 and self[3] == 0:
            return SimpleRect(0, 0, w, h)
        cx, cy = self[0] + 0.5*self[2], self[1] + 0.5*self[3]
        new = SimpleRect(0, 0, w, h)
        new[0] = cx-w/2
        new[1] = cy-h/2
        return new

    def inflate_ip(self, w, h):
        """Inflate current rectangle to new width and height staying in the same centered place"""
        if self[2] == 0 and self[3] == 0:
            self[2] = w
            self[3] = h
            return
        cx, cy = self[0] + 0.5*self[2], self[1] + 0.5*self[3]
        self[0] = cx-float(w)/2
        self[1] = cy-float(h)/2
        self[2] = w
        self[3] = h

    def move_ip(self, dx, dy):
        """Move in place"""
        self[0] += dx
        self[1] += dy
        
    @property
    def width(self): return self[2]
    @property
    def height(self): return self[3]
    @property
    def x(self): return self[0]
    @x.setter
    def x(self, v): self[0] = v
    @property
    def y(self): return self[1]
    @y.setter
    def y(self, v): self[1] = v
    left = x
    top = y


class SpatialObject(object):
    """Represents a spatial object"""

    is_rect_like = False

    def isInside(self, other):
        """Return True if this object is inside another"""
        raise NotImplemented

    def isOverlapping(self, other):
        """Return True if this object overlaps another"""
        raise NotImplemented
        
            
class Rectangle(SpatialObject, serialize.Serializable):
    """Represents a rectangle"""
    
    my_properties = (
        serialize.L('rect', (0, 0, 0, 0), 'the spatial extent of the actor'),
    )

    is_rect_like = True

    def __init__(self, x=0, y=0, w=0, h=0):
        """Return a new object based on top left, top right, width and height"""
        self.rect = SimpleRect(x, y, w, h)
    
    def init(self):
        """Initialize from serialized"""
        if not hasattr(self, 'rect'):
            self.rect = SimpleRect(0, 0, 0, 0)
        else:
            self.rect = SimpleRect(*self.rect)
        
    @classmethod
    def fromCenter(cls, cx, cy, w, h):
        """Return a new rectangle giving the center x, y and width, height"""
        return cls(cx-w/2, cy-h/2, w, h)
        
    def isInside(self, other):
        """Return True if this object is inside another"""
        return other.rect.contains(self.rect) == 1
    
    def isOverlapping(self, other):
        """Return True if this object overlaps another"""
        return other.rect.colliderect(self.rect) == 1

    def setSpatial(self, x, y, w, h):
        """Set the spatial details of ourself"""
        self.rect = SimpleRect(x, y, w, h)
    
    def setOrigin(self, x ,y):
        """Set the left and top coords"""
        self.moveTo(x+self.width/2, y+self.height/2)

    def getOrigin(self):
        """Get the left and top coords"""
        return self.rect[0], self.rect[1]
                
    def getSpatial(self):
        """Return spatial details"""
        return self.rect

    def setSpatialCentered(self, x, y, w, h):
        """Set the spatial details of ourself"""
        self.setSpatial(x-w/2, y-h/2, w, h)
        
    def getSpatialCentered(self):
        """Return spatial details"""
        x, y, w, h = self.getSpatial()
        return (x+w/2, y+h/2, w, h)
    
    def getRelativeLocation(self, other):
        """Return the relative location of another object"""
        return (other.rect.x - self.rect.x, other.rect.y - self.rect.y)

    def getRelativeLocationCentered(self, other):
        """Return the relative location of another object"""
        l1, l2 = self.getSpatialCentered(), other.getSpatialCentered()
        return (l2[0] - l1[0], l2[1] - l1[1])

    def getDistanceFrom(self, other):
        """Return the distance we are from another"""
        if isinstance(other, SpatialObject):
            return math.sqrt((self.x-other.x)**2 + (self.y-other.y)**2)
        else:
            return math.sqrt((self.x-other[0])**2 + (self.y-other[1])**2)
    
    def move(self, dx, dy):
        """Move the actor"""
        self.moveTo(self.x+dx, self.y+dy)
        
    def moveTo(self, x, y, override_lock=False):
        """Move the center of this object to the given location, unless it is locked
        
        This is the main method used to implement the position of the 
        shape. This is the one to override.
        
        """
        self.rect.x = x-self.rect.width/2
        self.rect.y = y-self.rect.height/2
        
    def resizeBy(self, w, h):
        """Resize the spatial by the given extent"""
        self.rect.inflate_ip(w+self.width, h+self.height)

    def resizeTo(self, w, h):
        """Resize the spatial by the given extent"""
        self.resizeBy(w-self.width, h-self.height)
        
    def scale(self, factor):
        """Rescale the spatial extent"""
        _, _, w, h = self.rect
        nw, nh = w*factor, h*factor
        self.resizeTo(nw, nh)

    def getArea(self):
        """Return the area of the shape"""
        return self.rect.width * self.rect.height
    
           
    ### Simple access ###
    
    @property
    def x(self): return self.rect.x+self.rect.width/2
    @x.setter
    def x(self, value): 
        self.moveTo(value, self.y)
    @property
    def y(self): return self.rect.y+self.rect.height/2
    @y.setter
    def y(self, value):
        self.moveTo(self.x, value)
    @property
    def width(self): return self.rect.width
    @property
    def height(self): return self.rect.height
    
    
class Point(Rectangle):
    """Represents a point"""

    @classmethod
    def __init__(self, x, y):
        """Return a new object based on a point"""
        self.rect = SimpleRect(x, y, 0, 0)
    
    def isInside(self, other):
        """Return True if this object is inside another"""
        if other.is_rect_like:
            return other.rect.collidepoint(self.rect[0], self.rect[1]) == 1
        else:
            return other.isPointInside(self)
        
    def isOverlapping(self, other):
        """Return True if this object overlaps another"""
        return self.isInside(other)


class Polyline(SpatialObject):
    """A line made of segments"""

    def __init__(self, points):
        """Initialise the polyline"""
        super(SpatialObject, self).__init__()
        #
        self.points = []
        self.lines = []
        self.rect = SimpleRect(0, 0, 0, 0)
        #
        self.setPoints(points)

    def setPoints(self, points):
        """Set the points for the line"""
        self.points = points
        #
        # Determine properties (ignore the first point as it is the same as the last one)
        xs, ys = zip(*self.points[1:])
        n = len(xs)
        x = float(sum(xs)) / n
        y = float(sum(ys)) / n
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        #
        self.rect = SimpleRect(x, y, width, height)
        #
        # Create lines
        self.lines = [Line(sx, sy, ex, ey) for (sx, sy), (ex, ey) in zip(self.points, self.points[1:])]

    def getPoints(self):
        """Return the points in the polygon"""
        return self.points

    def getLines(self):
        """Return the lines that make up the polygon"""
        return self.lines

    def moveTo(self, x, y):
        """Move the polygon to the new position"""
        dx = x - self.x
        dy = y - self.y
        self.move(dx, dy)

    def move(self, dx, dy):
        """Move the polygon relative to its current location"""
        self.setPoints([(px + dx, py + dy) for px, py in self.getPoints()])

    def getLength(self):
        """Return the perimeter"""
        return sum(line.length for line in self.lines)

    def getPointAtDistance(self, distance):
        """Return a point at a certain distance along the perimeter"""
        if distance < 0:
            raise OutOfRange('Distance %s cannot be negative' % distance)
        #
        to_go = distance
        for idx, line in enumerate(self.lines):
            if to_go <= line.length:
                fraction = 0 if to_go == 0 else to_go / line.length
                x = fraction * (line.x2 - line.x1) + line.x1
                y = fraction * (line.y2 - line.y1) + line.y1
                return x, y
            else:
                to_go -= line.length
        else:
            raise OutOfRange('Distance %s was beyond the length of the line' % distance)

    def getPointAtFraction(self, fraction):
        """Get a point at a certain fraction along the perimeter"""
        return self.getPointAtDistance(fraction * self.getLength())

    @property
    def x(self): return self.rect.x
    @x.setter
    def x(self, value):
        self.moveTo(value, self.y)
    @property
    def y(self): return self.rect.y
    @y.setter
    def y(self, value):
        self.moveTo(self.x, value)
    @property
    def width(self): return self.rect.width
    @property
    def height(self): return self.rect.height


class Polygon(Polyline):
    """Represents a polygonal shape comprising a series of points"""

    def __init__(self, points=None, auto_close=False):
        """Initialise the polygon"""
        #
        # Allow auto-closing
        if points and auto_close and points[0] != points[-1]:
            the_points = points + [points[0]]
        else:
            the_points = points
        #
        super(Polygon, self).__init__(the_points)

    def setPoints(self, points):
        """Set the points in the polygon"""
        #
        # Ensure that the shape is closed
        if len(points) < 2 or points[0] != points[-1]:
            raise NotClosed('The polygon is not closed')
        #
        super(Polygon, self).setPoints(points)

    def isPointInside(self, other):
        """Return True if the other point is inside this one"""
        #
        # Draw lines from the point in the NESW directions, if they all intersect
        # lines of this polygon then the point is inside it
        test_lines = [Line.fromRadial(other.x, other.y, angle, 1e6) for angle in (0, 90, 180, 270)]
        for test_line in test_lines:
            for line in self.lines:
                if test_line.intersectionWith(line):
                    break
            else:
                return False
        else:
            return True


class Line(object):
    """A line"""

    def __init__(self, x1, y1, x2, y2):
        """Initialise the line"""
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.vertical = abs(x1 - x2) < 0.00001
        self.m = None if self.vertical else float(y2 - y1) / float(x2 - x1)
        self.c = None if self.vertical else y1 - self.m * x1
        self.low_x, self.high_x = (x1, x2) if x1 < x2 else (x2, x1)
        self.low_y, self.high_y = (y1, y2) if y1 < y2 else (y2, y1)
        self.length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def intersectionWith(self, other):
        """Return the intersection point of two lines"""
        #
        # Same gradient, then no intersection
        if self.m == other.m:
            return None
        #
        # Calculate the x
        if self.m is None:
            x = self.x1
        elif other.m is None:
            x = other.x1
        else:
            x = float(other.c - self.c) / float(self.m - other.m)
        #
        # Now the y
        if self.m is not None:
            y = self.m * x + self.c
        else:
            y = other.m * x + other.c
        #
        # Make sure intersection is within the line
        if self.low_x <= x <= self.high_x and other.low_x <= x <= other.high_x and \
                self.low_y <= y <= self.high_y and other.low_y <= y <= other.high_y:
            return Point(x, y)
        else:
            return None

    def getIntersectingRay(self, other):
        """Return an intersecting ray"""
        point = self.intersectionWith(other)
        if not point:
            return None
        else:
            return Line(self.x1, self.y1, point.x, point.y)

    @classmethod
    def fromRadial(cls, x, y, angle, length):
        """Return a line from a radial"""
        x1 = x + length * math.cos(math.radians(angle))
        y1 = y + length * math.sin(math.radians(angle))
        return cls(x, y, x1, y1)

    def getEndPoint(self):
        """Return the end point"""
        return Point(self.x2, self.y2)

    def getStartPoint(self):
        """Return the start point"""
        return Point(self.x1, self.y1)