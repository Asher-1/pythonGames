from __future__ import division, print_function, unicode_literals

from functools import partial
from random import randint, uniform
import math

import bullet
from bullet import Bullet

from util import get_angle, get_velocity

class Pattern(object):
    """Base class for a bullet pattern."""
    # on_time = func to call when time runs out
    # time_args = tuple of arguments for on_time
    # on_fire = func to call to generate bullets
    # fire_args = tuple of arguments for on_fire
    def __init__(self, cooldown, bullet_id, active,
                 on_time, time_args, on_fire, fire_args):
        self.active = active

        self._cooldown = cooldown
        self._bullet_id = bullet_id

        self._time = partial(on_time, *time_args)
        self._fire = partial(on_fire, *fire_args)

        # Patterns can store whatever in here
        self._state = {}

    def generate_bullets(self, pos, player):
        if not self.active:
            return

        self._state['bullet_id'] = self._bullet_id
        self._state['pos'] = pos
        self._state['player'] = player

        self._cooldown -= 1
        if self._cooldown == 0:
            for bullet in self._fire(self._state):
                yield bullet

            self._cooldown = self._time(self._state)

def same_time(time, state):
    return time

def random_time(min_time, max_time, state):
    return randint(min_time, max_time)

# Fire 'count' bullets with 'time' between them, then wait 'delay'
def burst_time(time, count, delay, state):
    cur = state.get('time_count', 0)
    cur += 1

    result = None

    # If that was the x-th time we fired, wait for the delay
    if cur == count:
        cur = 0
        result = delay
    else:
        result = time

    state['time_count'] = cur

    return result

# Continue a pattern for 'timeout' seconds
def until_time(time, timeout, state):
    cur = state.get('time_accum', 0)

    cur += time
    state['time_accum'] = cur

    if cur > timeout:
        return 10 ** 7  # some really high number
    else:
        return time

def until_burst(time, count, delay, timeout, state):
    cur = state.get('time_count', 0)
    accum = state.get('time_accum', 0)

    cur += 1
    result = None

    # If that was the x-th time we fired, wait for the delay
    if cur == count:
        cur = 0
        result = delay
    else:
        result = time

    accum += result

    if accum > timeout:
        result = 10 ** 7  # some really high number

    state['time_accum'] = accum
    state['time_count'] = cur

    return result

# The state dict will have 'bullet_id', 'pos', and 'player'
def n_way(speed, count, state):
    bullet_id = state['bullet_id']
    pos = state['pos']

    angle_inc = math.pi * 2 / count

    for i in range(count):
        vel = get_velocity(speed, angle_inc * i)

        yield create_bullet(bullet_id, pos, vel)

# Same as n_way, but offset the angle every time
def inc_n_way(speed, count, inc, sign, state):
    bullet_id = state['bullet_id']
    pos = state['pos']

    cur = state.get('fire_inc', 0)

    angle_inc = math.pi * 2 / count  # Angle between bullets
    slice_inc = angle_inc / inc  # Angle between bullets divided into parts
    start_angle = slice_inc * cur  # Angle to use as offset

    for i in range(count):
        vel = get_velocity(speed, start_angle + angle_inc * i)

        yield create_bullet(bullet_id, pos, vel)

    cur += sign * 1
    state['fire_inc'] = cur

# Create 'circles' circles with 'count' bullets, starting at 'degrees'
def circles(speed, count, circles, degrees, radius, state):
    bullet_id = state['bullet_id']
    pos = state['pos']

    base_angle = math.radians(degrees)
    angle_inc = math.pi * 2 / circles
    circle_inc = math.pi * 2 / count

    for i in range(circles):
        angle = base_angle + i * angle_inc
        x = pos[0] + (radius * math.cos(angle))
        y = pos[1] + (radius * math.sin(angle))
        circle_pos = (x, y)

        for j in range(count):
            vel = get_velocity(speed, circle_inc * j)

            yield create_bullet(bullet_id, circle_pos, vel)

# Create a spiral of bullets; basically same as inc_n_way except one at a time
# Starting angle is random
def spiral(speed, count, spokes, sign, state):
    bullet_id = state['bullet_id']
    pos = state['pos']

    cur = state.get('fire_inc', 0)
    start = state.get('start', uniform(0, math.pi * 2))

    angle_inc = math.pi * 2 / count  # Angle between bullets
    angle = angle_inc * cur  # Angle to use as offset
    spoke_inc = math.pi * 2 / spokes

    for spoke in range(spokes):
        vel = get_velocity(speed, start + angle + spoke_inc * spoke)

        yield create_bullet(bullet_id, pos, vel)

    cur += sign * 1
    state['fire_inc'] = cur
    state['start'] = start

# Fire a single bullet at a given direction
def direction(speed, degrees, state):  # In degrees: 0 = right
    bullet_id = state['bullet_id']
    pos = state['pos']

    angle = math.radians(degrees)
    vel = get_velocity(speed, angle)

    yield create_bullet(bullet_id, pos, vel)

def aimed(speed, state):
    bullet_id = state['bullet_id']
    pos = state['pos']
    player = state['player']

    angle = get_angle(pos, player.sprite.position)
    vel = get_velocity(speed, angle)

    yield create_bullet(bullet_id, pos, vel)

def spread_aimed(speed, count, degrees, state):
    bullet_id = state['bullet_id']
    pos = state['pos']
    player = state['player']

    rad = math.radians(degrees)

    player_angle = get_angle(pos, player.sprite.position)
    angle_inc = rad / (count - 1)
    start_angle = player_angle - (rad / 2)

    for i in range(count):
        vel = get_velocity(speed, start_angle + angle_inc * i)

        yield create_bullet(bullet_id, pos, vel)


# For firing multiple aimed bullets at different speeds
def multi_aimed(speeds, state):
    for speed in speeds:
        # Even though aimed() only yields one bullet, it's still a generator
        for bullet in aimed(speed, state):
            yield bullet

# Fire n bullets randomly
def n_random(min_speed, max_speed, count, state):
    bullet_id = state['bullet_id']
    pos = state['pos']

    for i in range(count):
        angle = uniform(0, math.pi * 2)
        vel = get_velocity(uniform(min_speed, max_speed), angle)

        yield create_bullet(bullet_id, pos, vel)

# Useful for stress testing, but don't use this one in a real level
def spammy(state):
    bullet_id = state['bullet_id']
    pos = state['pos']

    for i in range(randint(10, 50)):
        vel = (uniform(-9.0, 9.0), uniform(-9.0, 9.0))

        yield create_bullet(bullet_id, pos, vel)

# Should be used by patterns only
def create_bullet(bullet_id, pos, vel):
    bullet_dict = bullet.types[bullet_id]

    return Bullet(img=bullet_dict['img'], hitbox=bullet_dict['hitbox'],
                  pos=pos, vel=vel)
