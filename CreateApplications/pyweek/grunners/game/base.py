class State(object):

    def __init__(self, scene, prev_state=None):
        self.scene = scene
        self.prev_state = prev_state
        if self.prev_state:
            self.prev_state.on_exit()
        self.on_enter()

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass

class Scene(object):

    START = State # used as first state of the scene
    state = None

    def __init__(self, window, **kwargs):
        self.window = window
        self.set_state(self.START)

    def set_state(self, next_state):
        self.state = next_state(self, self.state)

    def set_prev_state(self):
        if self.state and self.state.prev_state:
            self.state = self.state.prev_state

    def update(self, dt):
        self.state.update(dt)

    def draw(self):
        self.state.draw()

    def delete(self):
        pass

