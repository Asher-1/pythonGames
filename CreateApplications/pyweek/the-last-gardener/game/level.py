from __future__ import division, print_function, unicode_literals

import pyglet
from pyglet.sprite import Sprite

from bullet import Bullet, BIG_SIZE
from enemy import Enemy
from player import Player
from rect import Rect
import sounds
from util import get_tile_pos

class Level(object):
    WIDTH = 800
    HEIGHT = 540
    Y_OFFSET = 60  # from the bottom
    TOP_BOUND = 600

    TILE_SIZE = 20
    ROWS = HEIGHT // TILE_SIZE
    COLS = WIDTH // TILE_SIZE

    GRASS_HP = 60  # should be 0.33 second at full speed
    BEGIN_HP = ROWS * COLS * GRASS_HP
    HALF_HP = GRASS_HP // 2

    ONGOING = 0
    PASSED = 1
    GRASS_CLEAR = 2
    PERFECT_CLEAR = 3
    DIED = 4
    TIME_UP = 5

    EASY = 0
    NORMAL = 1
    HARD = 2

    def __init__(self, data, skill):
        self.number = 0
        self.skill = skill

        self.time_elapsed = 0  # in frames; yes we have dt but lazy :\
        self.time_left = 0

        self.start_lives = 0

        self.percent_done = 0.00
        self.percent_goal = 0.00

        self.state = Level.ONGOING

        self.player = None

        self.enemies = []
        self.bullets = []

        # From not mowed to mowed
        self.grass_imgs = [pyglet.resource.image('grass1.png'),
                           pyglet.resource.image('grass2.png'),
                           pyglet.resource.image('grass3.png')]

        self.grass_batch = pyglet.graphics.Batch()
        self.enemy_batch = pyglet.graphics.Batch()
        self.bullet_batch = pyglet.graphics.Batch()
        self.big_batch = pyglet.graphics.Batch()

        # Initialize the tile arrays
        self.tile_health = []
        self.tile_sprites = []
        self.tile_rects = []

        for row in range(Level.ROWS):
            # Create a new row.
            self.tile_health.append([Level.GRASS_HP] * Level.COLS)

            self.tile_sprites.append([])
            self.tile_rects.append([])

            for col in range(Level.COLS):
                temp_x = col * Level.TILE_SIZE
                temp_y = row * Level.TILE_SIZE + Level.Y_OFFSET

                temp = Sprite(self.grass_imgs[0],
                              x=temp_x, y=temp_y,
                              batch=self.grass_batch)
                self.tile_sprites[row].append(temp)

                rect = Rect(temp_x, temp_y, Level.TILE_SIZE, Level.TILE_SIZE)
                self.tile_rects[row].append(rect)

        self._parse_dict(data)

    def _parse_dict(self, data):
        self.number = data['number']
        self.percent_goal = data['goal'][self.skill]
        self.start_lives = data['lives'][self.skill]
        self.time_left = data['time'][self.skill] * 60  # 60 FPS

        self.player = Player(self.start_lives)

        for enemy in data['enemies']:
            if self.skill in enemy.skills:
                self.add_enemy(enemy.make_enemy(self))

    def add_enemy(self, enemy):
        enemy.sprite.batch = self.enemy_batch
        self.enemies.append(enemy)

    def add_bullet(self, bullet):
        # Draw bigger bullets below smaller ones
        if bullet.hitbox.width == BIG_SIZE:
            bullet.sprite.batch = self.big_batch
        else:
            bullet.sprite.batch = self.bullet_batch

        self.bullets.append(bullet)

    @property
    def was_passed(self):
        return self.state in (Level.PASSED, Level.GRASS_CLEAR,
                              Level.PERFECT_CLEAR)

    @property
    def was_failed(self):
        return self.state in (Level.DIED, Level.TIME_UP)

    def update(self, dt):
        # Stupid if-statement, but prevents the player moving on level clear
        if self.state == Level.ONGOING:
            self.player.update(dt)

        for bullet in self.bullets:
            bullet.update(dt)

        for enemy in self.enemies:
            enemy.update(dt)

        self._player_bounds()
        self._bullet_bounds()

        if self.state == Level.ONGOING:
            self._bullet_collision()
            self._enemy_collision()

            # Do it twice to avoid that awkward possibility of dying and
            # getting 100% at the same time
            self._check_for_end()

        # If this is true the first time, the player died; the mowing sound
        # will be stopped in self.player.damage()
        if self.state != Level.ONGOING:
            return

        self._mow_lawn()
        self.time_elapsed += 1
        self.time_left -= 1

        if 0 < self.time_left <= 600 and self.time_left % 60 == 0:
            sounds.play_sound('time_countdown')

        # Check again after the grass was 'damaged'
        self._check_for_end()

        # If this is the case, the player won or ran out of time; stop the
        # sound in this case
        if self.state != Level.ONGOING:
            self.player.stop_sound()

    def _player_bounds(self):
        rect = self.player.sprite_rect
        margin = 16

        if rect.centerx < margin:
            self.player.move(margin, rect.centery)
        if rect.centerx > Level.WIDTH - margin - 1:
            self.player.move(Level.WIDTH - margin - 1, rect.centery)
        if rect.centery < Level.Y_OFFSET + margin:
            self.player.move(rect.centerx, Level.Y_OFFSET + margin)
        if rect.centery > Level.TOP_BOUND - margin - 1:
            self.player.move(rect.centerx, Level.TOP_BOUND - margin - 1)

    def _bullet_bounds(self):
        temp_list = []

        # Past these coordinates, bullets should be deleted
        left = -20
        right = Level.WIDTH + 20
        bottom = Level.Y_OFFSET - 20
        top = Level.TOP_BOUND + 20

        for bullet in self.bullets:
            pos = bullet.sprite.position

            if (pos[0] < left or pos[0] > right or
                    pos[1] < bottom or pos[1] > top):
                temp_list.append(bullet)

        for bullet in temp_list:
            bullet.delete()
            self.bullets.remove(bullet)

    def _bullet_collision(self):
        if not self.player.alive:
            return

        temp_bullet = None

        for bullet in self.bullets:
            if self.player.hitbox.intersects(bullet.hitbox):
                self.player.damage()
                bullet.delete()
                temp_bullet = bullet
                break  # Only one bullet should hit per frame

        if temp_bullet is not None:
            self.bullets.remove(temp_bullet)

    def _enemy_collision(self):
        if not self.player.alive:
            return

        for enemy in self.enemies:
            # We're using the graze hitbox since it's bigger but not too big
            if self.player.enemy_hitbox.intersects(enemy.hitbox):
                self.player.damage()
                break  # Only one enemy should collide per frame

    def _mow_lawn(self):
        if not self.player.alive:
            return

        player_rect = self.player.sprite_rect
        center_x, center_y = get_tile_pos(player_rect.center,
           Level.TILE_SIZE, Level.Y_OFFSET)

        # 18.0 // 4 = 4.0, but range expects integers
        center_x = int(center_x)
        center_y = int(center_y)

        # Search all rects in a 5x5 area around the player's center
        start_x = center_x - 2
        start_y = center_y - 2
        end_x = center_x + 3  # range goes from m to n-1
        end_y = center_y + 3

        # Avoid out of bounds errors
        if start_x < 0:
            start_x = 0

        if start_y < 0:
            start_y = 0

        if end_x > Level.COLS:
            end_x = Level.COLS

        if end_y > Level.ROWS:
            end_y = Level.ROWS

        damage = self._grass_damage()

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_rect = self.tile_rects[y][x]

                if (self.tile_health[y][x] > 0 and
                        tile_rect.intersects(player_rect)):
                    self.tile_health[y][x] -= damage

                    if self.tile_health[y][x] <= 0:
                        self.tile_health[y][x] = 0
                        self.tile_sprites[y][x].image = self.grass_imgs[2]
                    elif (self.tile_health[y][x] <= Level.HALF_HP and
                            self.tile_sprites[y][x].image != self.grass_imgs[1]):
                        self.tile_sprites[y][x].image = self.grass_imgs[1]

        health = sum([sum(row) for row in self.tile_health])
        self.percent_done = (Level.BEGIN_HP - health) / Level.BEGIN_HP * 100

    # Determine damage to apply to the grass based on its movement
    def _grass_damage(self):
        result = 0

        # If it moved at all, it is rotating slightly
        if self.player.has_started:
            result = 1
        else:
            # Otherwise, since the player hasn't moved yet, don't kill the
            # tiles below the player
            return 0

        # Do more damage if the player is moving faster
        if self.player.moved:
            result = 2 if self.player.focus else 4

        return result

    def _check_for_end(self):
        if not self.player.alive:
            if self.percent_done >= self.percent_goal:
                self.state = Level.PASSED
            else:
                self.state = Level.DIED

        elif self.percent_done == 100.0:
            if self.player.lives == self.start_lives:
                self.state = Level.PERFECT_CLEAR
            else:
                self.state = Level.GRASS_CLEAR

        elif self.time_left == 0:
            # Play the player death sound here to signal out of time
            sounds.play_sound('player_death')

            if self.percent_done >= self.percent_goal:
                self.state = Level.PASSED
            else:
                self.state = Level.TIME_UP

    def draw(self):
        self.grass_batch.draw()

        self.player.draw()

        self.enemy_batch.draw()
        self.big_batch.draw()
        self.bullet_batch.draw()
