def position_setter (object):
    def set_position (p):
        object.position = p
    return set_position


class BaseScroller(object):
    def __init__ (self):
        self.x = 0
        self.y = 0
        self.actions = []

    def add_action (self, action):
        self.actions.append (action)

class ScrollManager(BaseScroller):
    def __init__ (self, boundary):
        super (ScrollManager, self).__init__()
        self.rect = boundary

    def focus_on (self, node):
        changed = False
        x, y = self.x, self.y
        if node.position[0] < self.rect.left - x:
            x = node.position[0] - self.rect.left
            changed = True
        elif node.position[0] > self.rect.right - x:
            x = node.position[0] - self.rect.right
            changed = True
        if node.position[1] < self.rect.bottom - y:
            y = node.position[1] - self.rect.bottom
            changed = True
        elif node.position[1] > self.rect.top - y:
            y = node.position[1] - self.rect.top
            changed = True
        self.x, self.y = x, y
        if changed:
            for a in self.actions: a((-x, -y))

class ParallaxScroller(BaseScroller):
    def __init__ (self, other, factor):
        super (ParallaxScroller, self).__init__()
        self.factor = factor
        other.add_action (self.other_scroll)
    
    def other_scroll (self, p):
        x, y = p
        self.x, self.y = -x/self.factor, -y/self.factor
        for a in self.actions: a((x/self.factor, y/self.factor))
    
    def focus_on (self, node):
        raise NotImplementedError

