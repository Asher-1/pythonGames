"""Simple state machine to handle long running UI processes"""

import game.common


class StateMachine(game.common.Loggable):
    """Simple state machine for long running processes"""

    initial_state = 'initial'

    def __init__(self):
        """Initialise the machine"""
        self.addLogger()
        self.state = getattr(self, self.initial_state)()
        self.generators = [(0, None)]

    def update(self, dt):
        """Update the state-machine"""
        new_generators = []
        for waiting_for, generator in self.generators:
            waiting_for -= dt
            actual_generator = generator if generator else self.state
            #
            finished = False
            if waiting_for <= 0:
                try:
                    wait_for_next = next(actual_generator)
                except StopIteration:
                    finished = True
                else:
                    waiting_for = wait_for_next
            #
            if not finished or generator is None:
                new_generators.append((waiting_for, generator))
            #
            self.generators = new_generators

    def nextState(self, state):
        """Set the next state"""
        self.state = state

    def addGenerator(self, generator):
        """Add another generator"""
        self.generators.append((0, generator))