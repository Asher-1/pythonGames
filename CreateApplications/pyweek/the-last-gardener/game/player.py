from __future__ import division, print_function, unicode_literals

import pyglet
import math
from pyglet.window import key

from rect import Rect

import sounds

class Player(object):
    ENEMY_HIT_SIZE = 40  # Also used for enemy collision
    HITBOX_SIZE = 6  # For bullets only
    HITBOX_SPRITE_SIZE = 10  # Sprite is bigger to account for floating point
    NORMAL_SPEED = 5
    FOCUS_SPEED = 2

    SIZE = 64
    HALF_SIZE = 32

    def __init__(self, lives):
        # The sprite is anchored at the center
        player_img = pyglet.resource.image('spinner.png')
        player_img.anchor_x = Player.HALF_SIZE
        player_img.anchor_y = Player.HALF_SIZE
        self.sprite = pyglet.sprite.Sprite(player_img, x=400, y=200)

        # The dead sprite is anchored at the center
        self.player_img_dead = pyglet.resource.image('spinner_dead.png')
        self.player_img_dead.anchor_x = Player.HALF_SIZE
        self.player_img_dead.anchor_y = Player.HALF_SIZE

        # For collision with bullets
        self.hitbox = Rect(0, 0, Player.HITBOX_SIZE, Player.HITBOX_SIZE)
        self.hitbox.center = self.sprite.position

        # The hitbox sprite is also anchored at the center
        hitbox_img = pyglet.resource.image('hitbox.png')
        hitbox_img.anchor_x = Player.HITBOX_SPRITE_SIZE // 2
        hitbox_img.anchor_y = Player.HITBOX_SPRITE_SIZE // 2
        self.hitbox_sprite = pyglet.sprite.Sprite(hitbox_img,
            x=self.hitbox.centerx, y=self.hitbox.centery)

        # For collision with enemies
        self.enemy_hitbox = Rect(0, 0, Player.ENEMY_HIT_SIZE,
                                       Player.ENEMY_HIT_SIZE)
        self.enemy_hitbox.center = self.sprite.position

        # For collision with grass and the walls
        self.sprite_rect = Rect(0, 0, Player.SIZE, Player.SIZE)
        self.sprite_rect.center = self.sprite.position

        self.has_started = False  # Over the course of the level
        self.moved = False  # During this frame
        self.focus = False
        self._draw_hitbox = False
        self.lives = lives
        self._invul_timer = 0

        self.directions = {key.LEFT: False, key.RIGHT: False,
                           key.UP: False, key.DOWN: False}

        # Prepare the mowing sound loops
        sounds.init_loop('mowing')
        sounds.init_loop('mowing_idle')

    @property
    def alive(self):
        return self.lives >= 1

    def on_key_press(self, symbol, modifiers):
        if not self.alive:
            return

        if symbol in self.directions:
            self.directions[symbol] = True

        if symbol in [key.LSHIFT, key.RSHIFT]:
            self.focus = True

    def on_key_release(self, symbol, modifiers):
        if not self.alive:
            return

        if symbol in self.directions:
            self.directions[symbol] = False

        # FIXME (maybe): hitbox disappears even if the other shift is being held
        if symbol in [key.LSHIFT, key.RSHIFT]:
            self.focus = False

    def stop_sound(self):
        sounds.pause_loop('mowing')
        sounds.pause_loop('mowing_idle')

    def stop_movement(self):
        # Reset the movement
        for key in self.directions.iterkeys():
            self.directions[key] = False
            self.focus = False

    def update(self, dt):
        if not self.alive:
            self.stop_sound()
            return

        # Workaround for hitbox being toggled while paused
        self._draw_hitbox = self.focus

        if self._invul_timer > 0:
            self._invul_timer -= 1

            if self._invul_timer == 0:
                self.sprite.opacity = 255

        self.moved = False

        dx = 0
        dy = 0

        speed = Player.FOCUS_SPEED if self.focus else Player.NORMAL_SPEED

        # Counts how many keys are currently pressed down.
        truth_counter = self.directions.values().count(True)

        # If truth_counter is even, set it to 2, if odd, set it to 1
        truth_counter = ((truth_counter + 1) % 2) + 1

        # The math behind this line is too long to write here.
        # Just trust that it works.
        # Ask me if you need an explanation
        speed = speed / math.sqrt(truth_counter)

        if self.directions[key.LEFT]:
            dx -= speed
        if self.directions[key.RIGHT]:
            dx += speed
        if self.directions[key.DOWN]:
            dy -= speed
        if self.directions[key.UP]:
            dy += speed

        self.moved = not (dx == 0 and dy == 0)

        # "Start" the mower if this is the first movement
        if not self.has_started:
            self.has_started = self.moved

        if self.moved:
            angle_delta = 6 if self.focus else 10
        else:
            # If the "mower" started up, rotate slightly
            angle_delta = 2 if self.has_started else 0

        if angle_delta > 0:
            # The hitbox will be a bit off-center due to the rotation, but I'm
            # not sure if I can really do anything about that
            self.sprite.rotation = (self.sprite.rotation + angle_delta) % 360

        if not self.moved:
            #Pauses playing the mowing noise if you don't move this update.
            #Then plays the idle sound.
            sounds.pause_loop('mowing')

            if self.has_started:
                sounds.play_sound('mowing_idle')

            return

        new_x = self.sprite.x + dx
        new_y = self.sprite.y + dy

        self.move(new_x, new_y)

    def move(self, x, y): # (x, y) is the center
        if not self.alive:
            return

        # Center the sprites being used (the anchor is the center)
        self.sprite.position = (x, y)
        self.hitbox_sprite.position = (x, y)

        # Centers rects
        self.hitbox.center = (x, y)
        self.enemy_hitbox.center = (x, y)
        self.sprite_rect.center = (x, y)

        #If you move, play the moving sound and pause the idle.
        sounds.play_sound('mowing')
        sounds.pause_loop('mowing_idle')

    def damage(self):
        if not self.alive or self._invul_timer > 0:
            return

        self.lives -= 1
        sounds.play_sound('player_hit')

        if self.lives == 0:
            self.stop_movement()

            # Sets image to the dead image.
            self.sprite.image = self.player_img_dead

            # Pauses any sounds and then plays the death
            sounds.pause_loop('mowing')
            sounds.pause_loop('mowing_idle')
            sounds.play_sound('player_death')
        else:
            self._invul_timer = 30
            self.sprite.opacity = 128

    def draw(self):
        self.sprite.draw()

        if self._draw_hitbox:
            self.hitbox_sprite.draw()
