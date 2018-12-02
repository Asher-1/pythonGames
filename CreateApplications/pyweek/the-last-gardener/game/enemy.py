from __future__ import division, print_function, unicode_literals

from random import randint, uniform

import pyglet

from bullet import Bullet
from util import direction, get_angle, get_velocity
from rect import Rect

import sounds

HITBOX_WIDTH = 30
HITBOX_HEIGHT = 44

class Enemy(object):
    # pos = (centerx, centery),
    # size = (w, h), anchor = (x, y), hitbox = (w, h)
    # coords = list of coordinates to cycle through
    # patterns = iterable of patterns
    def __init__(self, level, img, pos, anchor, hitbox,
                 speed, movement, patterns):
        self.level = level

        enemy_img = pyglet.resource.image(img)
        enemy_img.anchor_x = anchor[0]
        enemy_img.anchor_y = anchor[1]

        # Add 60 to account for the status bar
        self.sprite = pyglet.sprite.Sprite(enemy_img, x=pos[0], y=pos[1] + 60)
        self.speed = speed
        self.velocity = (0, 0)
        self.direction = (0, 0)

        self.hitbox = Rect(0, 0, hitbox[0], hitbox[1])
        self.hitbox.center = self.sprite.position

        self.movement = []

        for i, item in enumerate(movement):
            # Add 60 to account for the status bar
            if len(item) == 2:
                self.movement.append((item[0], item[1] + 60))
            else:
                self.movement.append(item)

        self._move_index = 0
        self._pause_time = 0

        self.patterns = []  # (Pattern, toggle); toggle = None if not specified
        self._parse_patterns(patterns)

        if len(self.movement) > 0:
            self._calc_velocity()

            # The first entry could be wait time
            if len(self.movement[self._move_index]) == 2:
                self.direction = direction(self.sprite.position,
                                           self.movement[self._move_index])

    def _parse_patterns(self, patterns):
        for pattern in patterns:
            if self.level.skill in pattern.skills:
                temp = (pattern.make_pattern(), pattern.toggle)
                self.patterns.append(temp)

    def update(self, dt):
        self._move(dt)
        self._fire(dt)

    def _move(self, dt):
        def change_direction():
            old_item = self.movement[self._move_index]
            self._move_index = (self._move_index + 1) % len(self.movement)
            new_item = self.movement[self._move_index]

            self._calc_velocity()

            # If len == 1, it's already handled
            if len(new_item) == 2:
                if len(old_item) == 2:
                    self.direction = direction(old_item, new_item)
                else:
                    self.direction = direction(self.sprite.position, new_item)

        if len(self.movement) == 0:
            return

        if self._pause_time > 0:
            self._pause_time -= 1

            if self._pause_time == 0:
                change_direction()

            return

        cur = self.sprite.position
        new = (cur[0] + self.velocity[0], cur[1] + self.velocity[1])

        dest = self.movement[self._move_index]
        old_d = self.direction
        new_d = direction(new, dest)

        def axis_passed(a, b):
            # Either there is no movement on the axis anyway or the destination
            # was passed on that axis
            return abs(b - a) > 0 or (a == 0 and b == 0)

        if axis_passed(old_d[0], new_d[0]) and axis_passed(old_d[1], new_d[1]):
            self.sprite.position = dest
            change_direction()
            # FIXME: add the leftover here
        else:
            self.sprite.position = new

        self.hitbox.center = self.sprite.position

    def _calc_velocity(self):
        item = self.movement[self._move_index]
        if len(item) == 1:
            self._pause_time = item[0]
            self.velocity = (0, 0)
            self.direction = (0, 0)
            return

        angle = get_angle(self.sprite.position, item)
        self.velocity = get_velocity(self.speed, angle)

    def _fire(self, dt):
        for i, pattern in enumerate(self.patterns):
            done = self.level.percent_done
            obj = pattern[0]
            toggle = pattern[1]

            if toggle is not None and done >= toggle:
                obj.active = not obj.active
                # Don't toggle again
                self.patterns[i] = (obj, None)

            bullets = obj.generate_bullets(self.sprite.position,
                                           self.level.player)

            for bullet in bullets:
                sounds.play_sound('enemy_fire')
                self.level.add_bullet(bullet)

    def delete(self):  # Call on deletion to remove it from the batch
        self.sprite.delete()

RED_ENEMY = 1
BLUE_ENEMY = 2
CYAN_ENEMY = 3
GREEN_ENEMY = 4
PURPLE_ENEMY = 5
BOSS = 6

# Holds information about every enemy type
types = {
    # Tried to make these the same order as the bullets.
    # Only note is that 1 = red, do with that what you will.
    RED_ENEMY: {
        'img': 'alien_red.png',
        'anchor': (23, 35),
        'hitbox': (HITBOX_WIDTH, HITBOX_HEIGHT)
    },
    BLUE_ENEMY: {
        'img': 'alien_blue.png',
        'anchor': (23, 35),
        'hitbox': (HITBOX_WIDTH, HITBOX_HEIGHT)
    },
    CYAN_ENEMY: {
        'img': 'alien_cyan.png',
        'anchor': (23, 35),
        'hitbox': (HITBOX_WIDTH, HITBOX_HEIGHT)
    },
    GREEN_ENEMY: {
        'img': 'alien_green.png',
        'anchor': (23, 35),
        'hitbox': (HITBOX_WIDTH, HITBOX_HEIGHT)
    },
    PURPLE_ENEMY: {
        'img': 'alien_purple.png',
        'anchor': (23, 35),
        'hitbox': (HITBOX_WIDTH, HITBOX_HEIGHT)
    },
    BOSS: {
        'img': 'boss.png',
        'anchor': (100, 78),
        'hitbox': (132, 77)
    }
}
