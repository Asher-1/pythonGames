import random

from vector import Rectangle
import monster

MAX_MONSTERS = 3


class Team(object):

    def __init__(self, monsters):
        self.monsters = []
        for m in monsters:
            if isinstance(m, tuple):
                self.monsters.append(monster.MonsterPart.deserialise(m))
            else:
                self.monsters.append(m)
        while len(self.monsters) < MAX_MONSTERS:
            self.monsters.append(None)

    def __getitem__(self, idx):
        assert 0 <= idx < MAX_MONSTERS
        return self.monsters[idx]

    def __setitem__(self, idx, value):
        assert 0 <= idx < MAX_MONSTERS
        self.monsters[idx] = value

    def __iter__(self):
        for monster in self.monsters:
            if monster is not None:
                yield monster

    def random(self):
        return random.choice(list(self))
    def random_active(self):
        return random.choice(self.active)

    def refresh(self):
        for member in self:
            member.refresh()

    @property
    def bounding_box(self):
        boxes = [m.bounding_box for m in self if m]
        return Rectangle.union(boxes)

    @property
    def active(self):
        return filter(lambda m: m and not m.disabled, self)

    @property
    def defeated(self):
        return len(self.active) == 0
