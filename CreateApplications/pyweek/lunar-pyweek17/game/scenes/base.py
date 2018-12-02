class State(object):

    def __init__(self, scene):
        self.scene = scene
        self.prev_state = None

    def on_resize(self, width, height):
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass

class Scene(object):

    START = State # used as first state of the scene
    STATES = (State, ) # set to a real game state list
    state = None

    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.width = self.parent.width
        self.height = self.parent.height
        self._states = dict((cls, cls(self)) for cls in self.STATES)
        self.set_state(self.START)

    def set_state(self, next_state):
        assert issubclass(next_state, State), "%r is not a State" % next_state
        state = self._states[next_state]
        state.prev_state = self.state
        self.state = state
        self.state.on_resize(self.width, self.height)

    def on_resize(self, width, height):
        self.width = width
        self.height = height
        self.state.on_resize(width, height)

    def update(self, dt):
        self.state.update(dt)

    def draw(self):
        self.state.draw()

    def delete(self):
        pass

