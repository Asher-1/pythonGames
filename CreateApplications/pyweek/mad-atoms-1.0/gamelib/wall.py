from pymunk import Body, Segment, moment_for_segment

from gamelib.collision import C_WALL, C_STRONGHOLD, G_STRONGHOLD


MASS = 1000


class Wall(object):
    def __init__(self, a, b):
        self.body = Body(MASS, moment_for_segment(MASS, a, b))
        self.shape = Segment(self.body, a, b, 1)
        self.shape.collision_type = C_WALL


class StrongholdWall(Wall):
    def __init__(self, a, b):
        super(StrongholdWall, self).__init__(a, b)
        self.shape.collision_type = C_STRONGHOLD
        self.shape.group = G_STRONGHOLD
