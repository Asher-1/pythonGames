"""Implementation of a group"""

from game import common

class Group(list, common.Loggable):
    """A group of actors"""

    def __init__(self, name, values=None):
        """Initialise the group"""
        self.name = name
        super(Group, self).__init__(values if values else [])
        self.addLogger()
        #
        self._pos = (0, 0)
        self.ready_for_removal = False

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def pos(self):
        """Return the position"""
        return self._pos

    @pos.setter
    def pos(self, new_pos):
        """Set the position - all objects move with us"""
        x, y = new_pos
        dx, dy = x - self.pos[0], y - self.pos[1]
        self._pos = (x, y)
        for actor in self:
            actor.pos = (actor.x + dx, actor.y + dy)

    def update(self, dt):
        """Update the actors"""
        remove_actors = []
        for actor in self:
            actor.update(dt)
            if actor.ready_for_removal:
                remove_actors.append(actor)
        #
        # Remove dead actors
        for actor in remove_actors:
            self.remove(actor)

    def draw(self, surface):
        """Draw the actors"""
        for actor in self:
            actor.draw(surface)