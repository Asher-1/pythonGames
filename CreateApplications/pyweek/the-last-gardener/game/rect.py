from __future__ import division, print_function, unicode_literals

class Rect(object):
    """Represents a rectangle in which the bottom-left corner is the origin
    since Pyglet has the y-axis going upwards, just like in algebra.

    For collision-related methods, the top and right edges aren't considered
    part of the collision. (Trust me, it's better this way.)

    Setting width and height resizes the Rect. Setting any other property
    moves it. For properties representing a position, such as bottomleft, a
    tuple with (x, y) must be provided as the argument.
    """
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def left(self):
        return self.x

    @left.setter
    def left(self, value):
        self.x = value

    @property
    def right(self):
        return self.x + self.width

    @right.setter
    def right(self, value):
        self.x = value - self.width

    @property
    def bottom(self):
        return self.y

    @bottom.setter
    def bottom(self, value):
        self.y = value

    @property
    def top(self):
        return self.y + self.height

    @top.setter
    def top(self, value):
        self.y = value - self.height

    @property
    def bottomleft(self):
        return (self.left, self.bottom)

    @bottomleft.setter
    def bottomleft(self, value):
        self.left, self.bottom = value

    @property
    def bottomright(self):
        return (self.right, self.bottom)

    @bottomright.setter
    def bottomright(self, value):
        self.right, self.bottom = value

    @property
    def topleft(self):
        return (self.left, self.top)

    @topleft.setter
    def topleft(self, value):
        self.left, self.top = value

    @property
    def topright(self):
        return (self.right, self.top)

    @topright.setter
    def topright(self, value):
        self.right, self.top = value

    @property
    def center(self):
        return (self.x + (self.width / 2), self.y + (self.height / 2))

    @center.setter
    def center(self, value):
        self.x = value[0] - self.width / 2
        self.y = value[1] - self.height / 2

    @property
    def centerx(self):
        return self.left + (self.width / 2)

    @centerx.setter
    def centerx(self, value):
        self.left = value - self.width / 2

    @property
    def centery(self):
        return self.bottom + (self.height / 2)

    @centery.setter
    def centery(self, value):
        self.bottom = value - self.height / 2

    def copy(self):
        return Rect(self.x, self.y, self.width, self.height)

    def intersects(self, other):
        """Check if two rectangles are colliding."""
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

    def contains_point(self, x, y):
        """Check if a point is within a rectangle.

        A point being in the right or top edges doesn't count.
        """
        return (x >= self.x and x < self.x + self.width
            and y >= self.y and y < self.y + self.height)

    def __repr__(self):
        return '({0}, {1}, {2}, {3})'.format(self.x, self.y,
                                             self.width, self.height)


# Tests follow.
if __name__ == '__main__':
    a = Rect(10, 20, 50, 50)

    a.right = 80
    assert a.x == 30

    a = Rect(10, 20, 50, 50)

    a.left = 40
    assert a.x == 40 and a.right == 90

    a = Rect(10, 20, 50, 50)

    a.top = 200
    assert a.y == 150

    a = Rect(10, 20, 50, 50)

    a.bottom = 60
    assert a.y == 60 and a.top == 110

    # TODO: add tests for bottomleft, etc.

    a.center = (125, 125)
    assert a.left == 100 and a.right == 150 and a.bottom == 100 and a.top == 150

    print('positional attributes tested')

    b = Rect(100, 50, 100, 200) # goes from (100, 50) to (200, 250)

    assert b.contains_point(100, 50)
    assert b.contains_point(120, 70)
    assert not b.contains_point(300, 70)
    assert not b.contains_point(100, 250) # on the top edge
    assert not b.contains_point(200, 50) # on the right edge

    print('contains_point tested')

    c = Rect(20, 30, 50, 50)
    d = Rect(40, 60, 50, 50)

    assert c.intersects(d)
    assert d.intersects(c)

    c.x = 100

    assert not c.intersects(d)
    assert not d.intersects(c)

    c.x = 90
    c.y = 110

    assert not c.intersects(d) # on the edge
    assert not d.intersects(c)

    print('intersects tested')

    print('tests passed!')
