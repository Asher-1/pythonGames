"""Clock that shows on the screen"""

from pgzero import actor
from pgzero import clock
from pgzero import animation
from pgzero.loaders import sounds
from game import group
from game.settings import SETTINGS as S


class Clock(group.Group):
    """Represents the clock on the screen"""

    def __init__(self, name, state):
        """Initialise the clock"""
        super(Clock, self).__init__(name)
        #
        self.state = state
        self.label = actor.Actor('clock_label', center=(0, 0))
        self.back = actor.Actor('clock_back', center=(0, 0))
        self.middle = actor.Actor('clock_middle', center=(0, 0))
        self.front = actor.Actor('clock_front', center=(0, 0))
        #
        self.back._fix_pos = S['clock-pos']
        self.middle._fix_pos = S['clock-pos']
        self.front._fix_pos = S['clock-pos']
        #
        self.extend([self.label, self.back, self.middle, self.front])
        #
        self.day = self.state.options.initial_day
        self.time = self.state.options.initial_time

    def start(self):
        """Start clock running"""
        sounds.clock_tick.play()
        animation.Animation(
            self.back,
            angle=-(self.time * 360 / 12),
            on_finished=self.next_tick,
            tween=S['clock-tween'],
            duration=S['clock-tween-time'],
        )

    def next_tick(self):
        """Finished a tick"""
        self.time += 1
        if self.time == 13:
            self.time = 0
            self.day += 1
            sounds.gong.play()
            animation.Animation(
                self.front,
                angle=-(self.day * 360 / 12),
                tween=S['clock-tween'],
                duration=S['clock-tween-time'],
            )
            self.state.mark_end_of_day(self.day)
        else:
            clock.schedule(self.start, S['clock-wait-time'] if not self.state.options.fast else 1)
