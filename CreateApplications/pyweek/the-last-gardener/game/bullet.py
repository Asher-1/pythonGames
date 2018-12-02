from __future__ import division, print_function, unicode_literals

import pyglet

from rect import Rect

SMALL_SIZE = 8
BIG_SIZE = 32

class Bullet(object):
    # hitbox = (w, h), pos = (x, y), vel = (x, y)
    def __init__(self, img, hitbox, pos, vel):
        # Always anchor the image at the center
        bullet_img = pyglet.resource.image(img)
        bullet_img.anchor_x = bullet_img.width // 2
        bullet_img.anchor_y = bullet_img.height // 2

        self.sprite = pyglet.sprite.Sprite(bullet_img, x=pos[0], y=pos[1])

        self.hitbox = Rect(0, 0, hitbox[0], hitbox[1])
        self.hitbox.center = self.sprite.position

        self.velocity = list(vel)

    def update(self, dt):
        new_x = self.sprite.x + self.velocity[0]
        new_y = self.sprite.y + self.velocity[1]

        self._move(new_x, new_y)

    def _move(self, x, y):
        self.sprite.position = (x, y)
        self.hitbox.center = (x, y)

    def delete(self):  # Call on deletion to remove it from the batch
        self.sprite.delete()

# Smaller bullets
RED_SMALL = 1
BLUE_SMALL = 2
CYAN_SMALL = 3
GREEN_SMALL = 4
PURPLE_SMALL = 5
YELLOW_SMALL = 6

# Bigger bullets
RED_BIG = 7
BLUE_BIG = 8
CYAN_BIG = 9
GREEN_BIG = 10
PURPLE_BIG = 11
YELLOW_BIG = 12

types = {
    RED_SMALL: {
        'img': 'bullet_red.png',
        'hitbox': (SMALL_SIZE, SMALL_SIZE)
    },
    BLUE_SMALL: {
        'img': 'bullet_blue.png',
        'hitbox': (SMALL_SIZE, SMALL_SIZE)
    },
    CYAN_SMALL: {
        'img': 'bullet_cyan.png',
        'hitbox': (SMALL_SIZE, SMALL_SIZE)
    },
    GREEN_SMALL: {
        'img': 'bullet_green.png',
        'hitbox': (SMALL_SIZE, SMALL_SIZE)
    },
    PURPLE_SMALL: {
        'img': 'bullet_purple.png',
        'hitbox': (SMALL_SIZE, SMALL_SIZE)
    },
    YELLOW_SMALL: {
        'img': 'bullet_yellow.png',
        'hitbox': (SMALL_SIZE, SMALL_SIZE)
    },
    RED_BIG: {
        'img': 'bullet_big_red.png',
        'hitbox': (BIG_SIZE, BIG_SIZE)
    },
    BLUE_BIG: {
        'img': 'bullet_big_blue.png',
        'hitbox': (BIG_SIZE, BIG_SIZE)
    },
    CYAN_BIG: {
        'img': 'bullet_big_cyan.png',
        'hitbox': (BIG_SIZE, BIG_SIZE)
    },
    GREEN_BIG: {
        'img': 'bullet_big_green.png',
        'hitbox': (BIG_SIZE, BIG_SIZE)
    },
    PURPLE_BIG: {
        'img': 'bullet_big_purple.png',
        'hitbox': (BIG_SIZE, BIG_SIZE)
    },
    YELLOW_BIG: {
        'img': 'bullet_big_yellow.png',
        'hitbox': (BIG_SIZE, BIG_SIZE)
    }
}
