from __future__ import division, print_function, unicode_literals

import pyglet

from pyglet.sprite import Sprite
from pyglet.text import Label

from constants import *

class StatusBar(object):
    HEIGHT = 60

    SPACING = 2
    HEART_WIDTH = 14
    FIRST_HEART = 290

    def __init__(self, level):
        self.level = level

        self.bg = pyglet.resource.image('status_bar.png')

        self.progress = Label('Progress: ',
                              font_name=DEFAULT_FONT, font_size=16,
                              x=10, y=8)
        self.progress_nums = Label('', font_name=DEFAULT_FONT, font_size=16,
                                   x=500, y=8)
        self.progress_outline = pyglet.resource.image('progress_outline.png')
        self.progress_cutoff = pyglet.resource.image('progress_cutoff.png')
        self.progress_bar = pyglet.resource.image('progress_bar.png')
        self.progress_sprite = Sprite(self.progress_bar, x=115, y=6)

        self.time = Label('Time left: 0.00',
                          font_name=DEFAULT_FONT, font_size=16,
                          x=10, y=36)
        self.level_num = Label('Level ' + str(self.level.number),
                               font_name=DEFAULT_FONT, font_size=16,
                               anchor_x='right', x=790, y=36)
        skills = ('Easy', 'Normal', 'Hard')
        self.skill_name = Label(skills[self.level.skill],
                               font_name=DEFAULT_FONT, font_size=16,
                               anchor_x='right', x=790, y=8)

        # Handles lives and hearts
        self.lives = Label('Lives: ',
                           font_name=DEFAULT_FONT, font_size=16,
                           x=220, y=36)

        self.heart_img = pyglet.resource.image('heart.png')

    def update(self, dt):
        level = self.level  # Make the typing easier
        done = level.percent_done
        goal = level.percent_goal

        def round_str(x):
            return '{:.2f}'.format(x)

        self.time.text = 'Time left: ' + round_str(level.time_left / 60)

        if level.time_left == 0:
            self.time.color = RED
        elif level.time_left < 10 * 60:  # 60 FPS
            self.time.color = YELLOW

        if level.player.lives == 0:
            self.lives.color = RED
        elif level.player.lives == 1:
            self.lives.color = YELLOW

        self.progress_nums.text = round_str(done) + ' / ' + round_str(goal)

        if done == 100.0:
            if level.player.lives == level.start_lives:
                self.progress_sprite.color = GOLD[:3]  # Don't include alpha
            else:
                self.progress_sprite.color = SILVER[:3]
        elif done >= goal:
            self.progress_sprite.color = LIGHT_BLUE[:3]
        else:
            self.progress_sprite.color = RED[:3]

    def draw(self):
        level = self.level  # Make the typing easier
        done = level.percent_done
        goal = level.percent_goal

        self.bg.blit(0, 0) # Bottom left corner

        self.time.draw()
        self.lives.draw()

        for i in range (0, level.player.lives):
            self.heart_img.blit(x=self.FIRST_HEART + i *
                                (self.SPACING + self.HEART_WIDTH), y=33)

        self.level_num.draw()
        self.skill_name.draw()

        # Most inefficient progress bar ever
        inner_width = self.progress_outline.width - 2  # Left and right pixels
        bar_width = int((done / 100.0) * inner_width)
        region = self.progress_bar.get_region(x=0, y=0, width=bar_width,
                                              height=self.progress_bar.height)
        self.progress_sprite.image = region

        cutoff_x = int(115 + (goal / 100.0) * inner_width)

        self.progress.draw()
        self.progress_nums.draw()
        self.progress_outline.blit(114, 5)  # How magical
        self.progress_sprite.draw()
        self.progress_cutoff.blit(cutoff_x, 6)
