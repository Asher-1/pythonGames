"""A screen or area in which action happens."""

import sys

from pygame import event
import pymunk


class Screen(object):

    def __init__(self, name, world):
        self.name = name
        self.world = world
        self.space = pymunk.Space()

    def setup(self):
        """Perform setup based on the world state."""
        pass

    def teardown(self):
        pass

    def post_event(self, ev):
        event.post(ev)

    def handle_event(self, ev):
        pass

    def render(self, surface):
        pass

    def tick(self, seconds):
        """Step the given amount of time."""
        try:
            self.space.step(seconds)
        except AssertionError:
            # TODO: Find the source of these
            print >> sys.stderr, (
                'Caught a pymunk assertion error. '
                "We don't know what causes these on level change. "
                "Hopefully we can ignore them...")
