DECAY_RATE = 0.1

class Mutation:
    def __init__(self):
        self.amount = 0

    def update(self, dt):
        self.amount = max(self.amount - dt * DECAY_RATE, 0)

    def mutate(self, magnitude):
        self.amount += magnitude
