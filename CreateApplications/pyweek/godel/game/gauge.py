"""A gauge that is used to show water, food, health etc"""

from pgzero import actor
from pgzero import animation
from game import group
from game import rectangle


class Gauge(group.Group):
    """A gauge to show a value as a percentage"""


    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'

    def __init__(self, name, foreground, back_colour, front_colour,
                 size, value=100, orientation=None, bar_offset=None):
        """Initialise the gauge"""
        super(Gauge, self).__init__(name)
        #
        self.size = size
        self.orientation = orientation if orientation else self.VERTICAL
        self.foreground = actor.Actor(foreground) if foreground else None
        self.background = rectangle.Rectangle(back_colour, size)
        self.bar = rectangle.Rectangle(front_colour, size)
        if bar_offset:
            self.bar.center = bar_offset
            self.background.center = bar_offset
        self._value = value
        self.value = value
        #
        self.append(self.background)
        self.append(self.bar)
        if foreground:
            self.append(self.foreground)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        """Set the new value"""
        self._value = new_value
        if self.orientation == self.VERTICAL:
            new_size = (self.size[0], self.size[1] * new_value / 100.0)
            position = self.bar.midbottom
        else:
            new_size = (self.size[0] * new_value / 100.0, self.size[1])
            position = self.bar.midleft
        #
        self.bar.resize(new_size)
        if self.orientation == self.VERTICAL:
            self.bar.midbottom = position
        else:
            self.bar.midleft = position

    @property
    def new_value(self):
        return self._value

    @new_value.setter
    def new_value(self, new_value):
        """Set new value animating"""
        animation.Animation(self, value=new_value, tween='bounce_end')