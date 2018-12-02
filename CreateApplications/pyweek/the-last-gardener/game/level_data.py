from __future__ import division, print_function, unicode_literals

import bullet
import enemy
from enemy import Enemy
from level import Level

import pattern
from pattern import Pattern

# Constants for common skill settings
EASY_PLUS = (Level.EASY, Level.NORMAL, Level.HARD)
NORMAL_PLUS = (Level.NORMAL, Level.HARD)

EASY_ONLY = (Level.EASY,)
NORMAL_ONLY = (Level.NORMAL,)
HARD_ONLY = (Level.HARD,)

EASY_NORMAL = (Level.EASY, Level.NORMAL)
EASY_HARD = (Level.EASY, Level.HARD)

class EnemyData(object):
    def __init__(self, skills, enemy_id, start_pos,
                 speed, movement, patterns):
        self.skills = skills  # Read by Level
        self.enemy_id = enemy_id
        self.start_pos = start_pos
        self.speed = speed
        self.movement = movement
        self.patterns = patterns

    def make_enemy(self, level):
        enemy_dict = enemy.types[self.enemy_id]

        return Enemy(level, img=enemy_dict['img'],
                     speed=self.speed, pos=self.start_pos,
                     anchor=enemy_dict['anchor'], hitbox=enemy_dict['hitbox'],
                     movement=self.movement, patterns=self.patterns)


class PatternData(object):
    def __init__(self, skills, cooldown, bullet_id, active,
                 on_time, time_args, on_fire, fire_args, toggle):
        self.skills = skills  # Read by Enemy
        self.cooldown = cooldown
        self.bullet_id = bullet_id
        self.active = active
        self.on_time = on_time
        self.time_args = time_args
        self.on_fire = on_fire
        self.fire_args = fire_args
        self.toggle = toggle  # Read by Enemy, percent to toggle at

    def make_pattern(self):
        return Pattern(cooldown=self.cooldown, active=self.active,
                       bullet_id=self.bullet_id,
                       on_time=self.on_time, time_args=self.time_args,
                       on_fire=self.on_fire, fire_args=self.fire_args)

# Note: for the y-coordinate, do not add the status bar's height to it

level_dict = {
    1: {
        'number': 1,
        'lives': (3, 3, 2),
        'goal': (75.00, 90.00, 90.00),
        'time': (120, 90, 60),
        'story_before': 'intro',
        'story_clear': None,
        'enemies': (
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.RED_ENEMY,
                start_pos=(150, 440), speed=3,

                movement=(
                    (650, 440), (650, 100), (150, 100), (150, 440),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=180, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(120,),
                        on_fire=pattern.aimed, fire_args=(4,),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(90,),
                        on_fire=pattern.n_way, fire_args=(4, 8),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=30, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(30,),
                        on_fire=pattern.multi_aimed, fire_args=((6, 3),),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=30, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(40,),
                        on_fire=pattern.n_way, fire_args=(5, 16),
                        toggle=None
                    )
                )
            ),
        )
    },
    2: {
        'number': 2,
        'lives': (3, 3, 2),
        'goal': (75.00, 90.00, 90.00),
        'time': (120, 90, 75),
        'story_before': None,
        'story_clear': None,
        'enemies': (
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.BLUE_ENEMY,
                start_pos=(170, 480), speed=4,

                movement=(
                    (170, 60), (120,), (170, 480), (120,),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.direction, fire_args=(4, 0),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.random_time, time_args=(60, 90),
                        on_fire=pattern.n_way, fire_args=(3, 8),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(4,),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.random_time, time_args=(60, 90),
                        on_fire=pattern.n_way, fire_args=(3, 16),
                        toggle=None
                    ),
                )
            ),

            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.PURPLE_ENEMY,
                start_pos=(630, 60), speed=4,

                movement=(
                    (630, 480), (120,), (630, 60), (120,),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.PURPLE_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.direction, fire_args=(4, 180),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.PURPLE_SMALL, active=True,
                        on_time=pattern.random_time, time_args=(60, 90),
                        on_fire=pattern.n_way, fire_args=(3, 8),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(4,),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.PURPLE_SMALL, active=True,
                        on_time=pattern.random_time, time_args=(60, 90),
                        on_fire=pattern.n_way, fire_args=(3, 16),
                        toggle=None
                    ),
                )
            ),
        )
    },
    3: {
        'number': 3,
        'lives': (3, 3, 2),
        'goal': (75.00, 85.00, 90.00),
        'time': (120, 90, 90),
        'story_before': None,
        'story_clear': None,
        'enemies': (
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.RED_ENEMY,
                start_pos=(400, 480), speed=2,

                movement=(
                    (60, 270), (60,), (400, 60), (60,),
                    (740, 270), (60,), (400, 480), (60,),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.n_random, fire_args=(1, 3, 6),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_SMALL, active=False,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.n_way, fire_args=(3, 8),
                        toggle=50.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.burst_time, time_args=(10, 5, 80),
                        on_fire=pattern.inc_n_way, fire_args=(3, 8, 2, 1),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_SMALL, active=False,
                        on_time=pattern.random_time, time_args=(50, 70),
                        on_fire=pattern.n_random, fire_args=(2, 4, 20),
                        toggle=50.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.burst_time, time_args=(8, 5, 60),
                        on_fire=pattern.inc_n_way, fire_args=(3, 8, 4, 1),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=80, bullet_id=bullet.PURPLE_SMALL, active=True,
                        on_time=pattern.burst_time, time_args=(8, 5, 60),
                        on_fire=pattern.inc_n_way, fire_args=(3, 8, 4, -1),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_SMALL, active=False,
                        on_time=pattern.random_time, time_args=(90, 110),
                        on_fire=pattern.n_way, fire_args=(1, 32),
                        toggle=30.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.CYAN_SMALL, active=False,
                        on_time=pattern.burst_time, time_args=(2, 10, 40),
                        on_fire=pattern.aimed, fire_args=(5,),
                        toggle=60.0
                    ),
                )
            ),
        )
    },
    4: {
        'number': 4,
        'lives': (3, 3, 2),
        'goal': (70.00, 80.00, 90.00),
        'time': (120, 90, 90),
        'story_before': None,
        'story_clear': None,
        'enemies': (
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.BLUE_ENEMY,
                start_pos=(400, 440), speed=3,

                movement=(
                    (700, 440), (60,), (700, 100), (60,), (100, 100), (60,),
                    (400, 270), (120,), (100, 440), (60,),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.inc_n_way, fire_args=(3, 8, 4, 1),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.burst_time, time_args=(10, 4, 60),
                        on_fire=pattern.n_random, fire_args=(2, 3, 1),
                        toggle=50.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.random_time, time_args=(70, 90),
                        on_fire=pattern.inc_n_way, fire_args=(2, 16, 2, 1),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.same_time, time_args=(10,),
                        on_fire=pattern.n_random, fire_args=(2, 3, 1),
                        toggle=50.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.random_time, time_args=(80, 100),
                        on_fire=pattern.circles, fire_args=(1, 16, 4, 0, 10),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.same_time, time_args=(5,),
                        on_fire=pattern.spiral, fire_args=(3, 24, 1, 1),
                        toggle=40.0
                    ),
                )
            ),

            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.RED_ENEMY,
                start_pos=(400, 440), speed=2,

                movement=(
                    (100, 440), (60,), (100, 100), (60,), (700, 100), (60,),
                    (700, 440), (60,),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(4,),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.burst_time, time_args=(10, 4, 60),
                        on_fire=pattern.n_random, fire_args=(2, 3, 1),
                        toggle=50.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.burst_time, time_args=(10, 5, 60),
                        on_fire=pattern.aimed, fire_args=(4,),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.same_time, time_args=(10,),
                        on_fire=pattern.n_random, fire_args=(2, 3, 1),
                        toggle=50.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=30, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.burst_time, time_args=(5, 6, 60),
                        on_fire=pattern.multi_aimed, fire_args=((5, 4, 3, 2),),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.same_time, time_args=(5,),
                        on_fire=pattern.spiral, fire_args=(3, 24, 1, -1),
                        toggle=40.0
                    ),
                )
            ),
        )
    },
    5: {
        'number': 5,
        'lives': (3, 3, 2),
        'goal': (70.00, 80.00, 90.00),
        'time': (120, 90, 90),
        'story_before': None,
        'story_clear': 'halfway',
        'enemies': (
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.RED_ENEMY,
                start_pos=(100, 440), speed=3,

                movement=(
                    (700, 440), (60,), (100, 100), (60,), (700, 100), (60,),
                    (100, 440), (60,),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.burst_time, time_args=(40, 2, 80),
                        on_fire=pattern.inc_n_way, fire_args=(2, 12, 2, -1),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_SMALL, active=False,
                        on_time=pattern.same_time, time_args=(10,),
                        on_fire=pattern.spiral, fire_args=(3, 12, 2, 1),
                        toggle=50.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.burst_time, time_args=(30, 2, 60),
                        on_fire=pattern.n_way, fire_args=(2, 12),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.burst_time, time_args=(20, 3, 60),
                        on_fire=pattern.n_way, fire_args=(2, 16),
                        toggle=None
                    ),
                )
            ),
            EnemyData(
                skills=NORMAL_PLUS, enemy_id=enemy.RED_ENEMY,
                start_pos=(400, 500), speed=3,

                movement=(
                    (400, 40), (400, 500),
                ),

                patterns=(
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(30,),
                        on_fire=pattern.n_way, fire_args=(4, 2),
                        toggle=50.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_SMALL, active=False,
                        on_time=pattern.burst_time, time_args=(10, 16, 60),
                        on_fire=pattern.spiral, fire_args=(3, 16, 3, 1),
                        toggle=50.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(20,),
                        on_fire=pattern.spiral, fire_args=(3, 32, 4, 1),
                        toggle=30.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_SMALL, active=False,
                        on_time=pattern.same_time, time_args=(10,),
                        on_fire=pattern.spiral, fire_args=(3, 32, 4, 1),
                        toggle=30.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.burst_time, time_args=(5, 5, 60),
                        on_fire=pattern.multi_aimed, fire_args=((4, 3, 2),),
                        toggle=60.0
                    ),
                )
            ),
        )
    },
    6: {
        'number': 6,
        'lives': (4, 3, 2),
        'goal': (70.00, 80.00, 90.00),
        'time': (120, 90, 90),
        'story_before': None,
        'story_clear': None,
        'enemies': (
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.BLUE_ENEMY,
                start_pos=(760, 270), speed=2,

                movement=(
                    (40, 270), (60,), (760, 270), (60,),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_BIG, active=False,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=5.0
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_SMALL, active=False,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.inc_n_way, fire_args=(3, 8, 2, 1),
                        toggle=30.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_BIG, active=False,
                        on_time=pattern.same_time, time_args=(40,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=5.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_SMALL, active=False,
                        on_time=pattern.random_time, time_args=(50, 70),
                        on_fire=pattern.inc_n_way, fire_args=(3, 16, 2, 1),
                        toggle=30.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.random_time, time_args=(80, 120),
                        on_fire=pattern.inc_n_way, fire_args=(1, 24, 3, 1),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.CYAN_BIG, active=False,
                        on_time=pattern.random_time, time_args=(60, 100),
                        on_fire=pattern.inc_n_way, fire_args=(2.5, 6, 3, 1),
                        toggle=30.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.YELLOW_BIG, active=False,
                        on_time=pattern.same_time, time_args=(120,),
                        on_fire=pattern.aimed, fire_args=(2,),
                        toggle=60.0
                    ),
                )
            ),
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.PURPLE_ENEMY,
                start_pos=(400, 500), speed=2,

                movement=(
                    (400, 40), (60,), (400, 500), (60,),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_BIG, active=False,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=5.0
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.inc_n_way, fire_args=(3, 8, 2, 1),
                        toggle=30.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_BIG, active=False,
                        on_time=pattern.same_time, time_args=(40,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=5.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.random_time, time_args=(50, 70),
                        on_fire=pattern.inc_n_way, fire_args=(3, 16, 2, 1),
                        toggle=30.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.PURPLE_SMALL, active=True,
                        on_time=pattern.random_time, time_args=(80, 120),
                        on_fire=pattern.inc_n_way, fire_args=(1, 24, 3, 1),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.CYAN_BIG, active=False,
                        on_time=pattern.random_time, time_args=(60, 100),
                        on_fire=pattern.inc_n_way, fire_args=(2.5, 6, 3, 1),
                        toggle=30.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.YELLOW_BIG, active=False,
                        on_time=pattern.same_time, time_args=(120,),
                        on_fire=pattern.aimed, fire_args=(2,),
                        toggle=60.0
                    ),
                )
            ),
        )
    },
    7: {
        'number': 7,
        'lives': (4, 3, 2),
        'goal': (70.00, 80.00, 90.00),
        'time': (120, 90, 90),
        'story_before': None,
        'story_clear': None,
        'enemies': (
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.RED_ENEMY,
                start_pos=(60, 480), speed=3,

                movement=(
                    (740, 480), (60,), (400, 60), (60,), (60, 480), (60,),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_BIG, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.inc_n_way, fire_args=(1, 4, 4, 1),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.same_time, time_args=(30,),
                        on_fire=pattern.aimed, fire_args=(4,),
                        toggle=40.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_BIG, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.inc_n_way, fire_args=(1, 7, 4, 1),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.burst_time, time_args=(2, 10, 60),
                        on_fire=pattern.n_random, fire_args=(3, 4, 1),
                        toggle=40.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_BIG, active=False,
                        on_time=pattern.burst_time, time_args=(3, 5, 60),
                        on_fire=pattern.aimed, fire_args=(4,),
                        toggle=40.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_BIG, active=True,
                        on_time=pattern.random_time, time_args=(50, 70),
                        on_fire=pattern.inc_n_way, fire_args=(1, 9, 4, 1),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.burst_time, time_args=(3, 5, 60),
                        on_fire=pattern.spread_aimed, fire_args=(3, 5, 90),
                        toggle=40.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_SMALL, active=False,
                        on_time=pattern.random_time, time_args=(25, 35),
                        on_fire=pattern.n_way, fire_args=(3, 8),
                        toggle=40.0
                    )
                )
            ),

            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.RED_ENEMY,
                start_pos=(60, 60), speed=3,

                movement=(
                    (400, 480), (60,), (700, 60), (60,), (60, 60), (60,),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_BIG, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.inc_n_way, fire_args=(1, 4, 3, -1),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.same_time, time_args=(30,),
                        on_fire=pattern.aimed, fire_args=(4,),
                        toggle=40.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_BIG, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.inc_n_way, fire_args=(1, 7, 4, 1),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.burst_time, time_args=(2, 10, 60),
                        on_fire=pattern.n_random, fire_args=(3, 4, 1),
                        toggle=40.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_BIG, active=False,
                        on_time=pattern.burst_time, time_args=(3, 5, 60),
                        on_fire=pattern.aimed, fire_args=(4,),
                        toggle=40.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_BIG, active=True,
                        on_time=pattern.random_time, time_args=(50, 70),
                        on_fire=pattern.inc_n_way, fire_args=(1, 9, 4, 1),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.PURPLE_SMALL, active=False,
                        on_time=pattern.burst_time, time_args=(3, 5, 60),
                        on_fire=pattern.spread_aimed, fire_args=(3, 5, 90),
                        toggle=40.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_SMALL, active=False,
                        on_time=pattern.random_time, time_args=(25, 35),
                        on_fire=pattern.n_way, fire_args=(3, 8),
                        toggle=40.0
                    )
                )
            )
        )
    },
    8: {
        'number': 8,
        'lives': (4, 3, 2),
        'goal': (75.00, 80.00, 90.00),
        'time': (180, 120, 120),
        'story_before': None,
        'story_clear': None,
        'enemies': (
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.RED_ENEMY,
                start_pos=(740, 480), speed=5,

                movement=(
                    (60, 480), (60, 60), (740, 60), (740, 375), (230, 375),
                    (230, 165), (570, 165), (570, 270), (400, 270), (300,),
                    (570, 270), (570, 165), (230, 165), (230, 375), (740, 375),
                    (740, 60), (60, 60), (60, 480), (740, 480), (740, 60),
                    (60, 60), (60, 375), (570, 375), (570, 165), (230, 165),
                    (230, 270), (400, 270), (300,), (230, 270), (230, 165),
                    (570, 165), (570, 375), (60, 375), (60, 60), (740, 60),
                    (740, 480),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.inc_n_way, fire_args=(2, 16, 4, -1),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.RED_BIG, active=False,
                        on_time=pattern.random_time, time_args=(50, 70),
                        on_fire=pattern.n_random, fire_args=(2, 3, 8),
                        toggle=40.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(40,),
                        on_fire=pattern.inc_n_way, fire_args=(2, 16, 4, -1),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.RED_BIG, active=False,
                        on_time=pattern.random_time, time_args=(50, 70),
                        on_fire=pattern.inc_n_way, fire_args=(2, 8, 3, 1),
                        toggle=30.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_BIG, active=False,
                        on_time=pattern.random_time, time_args=(25, 35),
                        on_fire=pattern.inc_n_way, fire_args=(0.5, 1, 4, 1),
                        toggle=60.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.same_time, time_args=(20,),
                        on_fire=pattern.inc_n_way, fire_args=(2, 24, 3, -1),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.RED_BIG, active=False,
                        on_time=pattern.random_time, time_args=(25, 35),
                        on_fire=pattern.spiral, fire_args=(2, 16, 6, 1),
                        toggle=30.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_SMALL, active=False,
                        on_time=pattern.burst_time, time_args=(2, 10, 60,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=60.0
                    ),
                )
            ),
        )
    },
    9: {
        'number': 9,
        'lives': (4, 3, 2),
        'goal': (50.00, 60.00, 90.00),
        'time': (120, 120, 120),
        'story_before': None,
        'story_clear': None,
        'enemies': (
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.RED_ENEMY,
                start_pos=(30, 30), speed=3,

                movement=(
                    (30, 510), (770, 510), (770, 30), (30, 30),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(60, 60 * 90),
                        on_fire=pattern.n_way, fire_args=(3, 4),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.YELLOW_BIG, active=False,
                        on_time=pattern.same_time, time_args=(90,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=30.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(60, 60 * 90),
                        on_fire=pattern.n_way, fire_args=(3, 6),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.YELLOW_BIG, active=False,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=30.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_BIG, active=True,
                        on_time=pattern.until_time, time_args=(60, 60 * 90),
                        on_fire=pattern.n_way, fire_args=(3, 8),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=600, bullet_id=bullet.PURPLE_BIG, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=None
                    ),
                )
            ),
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.BLUE_ENEMY,
                start_pos=(30, 510), speed=3,

                movement=(
                    (770, 510), (770, 30), (30, 30), (30, 510),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(60, 60 * 90),
                        on_fire=pattern.n_way, fire_args=(3, 4),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_BIG, active=False,
                        on_time=pattern.same_time, time_args=(90,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=30.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(60, 60 * 90),
                        on_fire=pattern.n_way, fire_args=(3, 6),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_BIG, active=False,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=30.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_BIG, active=True,
                        on_time=pattern.until_time, time_args=(60, 60 * 90),
                        on_fire=pattern.n_way, fire_args=(3, 8),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=600, bullet_id=bullet.PURPLE_BIG, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=None
                    ),
                )
            ),
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.RED_ENEMY,
                start_pos=(770, 510), speed=3,

                movement=(
                    (770, 30), (30, 30), (30, 510), (770, 510),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(60, 60 * 90),
                        on_fire=pattern.n_way, fire_args=(3, 4),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.YELLOW_BIG, active=False,
                        on_time=pattern.same_time, time_args=(90,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=30.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(60, 60 * 90),
                        on_fire=pattern.n_way, fire_args=(3, 6),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.YELLOW_BIG, active=False,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=30.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_BIG, active=True,
                        on_time=pattern.until_time, time_args=(60, 60 * 90),
                        on_fire=pattern.n_way, fire_args=(3, 8),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=600, bullet_id=bullet.PURPLE_BIG, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=None
                    ),
                )
            ),
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.BLUE_ENEMY,
                start_pos=(770, 30), speed=3,

                movement=(
                    (30, 30), (30, 510), (770, 510), (770, 30),
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(60, 60 * 90),
                        on_fire=pattern.n_way, fire_args=(3, 4),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_BIG, active=False,
                        on_time=pattern.same_time, time_args=(90,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=30.0
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(60, 60 * 90),
                        on_fire=pattern.n_way, fire_args=(3, 6),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=1, bullet_id=bullet.BLUE_BIG, active=False,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=30.0
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.BLUE_BIG, active=True,
                        on_time=pattern.until_time, time_args=(60, 60 * 90),
                        on_fire=pattern.n_way, fire_args=(3, 8),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=600, bullet_id=bullet.PURPLE_BIG, active=True,
                        on_time=pattern.same_time, time_args=(60,),
                        on_fire=pattern.aimed, fire_args=(3,),
                        toggle=None
                    ),
                )
            ),
        )
    },
    10: {
        'number': 10,
        'lives': (5, 5, 5),
        'goal': (100.00, 100.00, 100.00),
        'time': (1000, 1000, 1000),
        'story_before': 'finale',
        'story_clear': 'ending',
        'enemies': (
            EnemyData(
                skills=EASY_PLUS, enemy_id=enemy.BOSS,
                start_pos=(400, 540), speed=4,

                movement=(
                    # Have the boss fly out after two minutes
                    (400, 440), (60 * 120,), (400, 800), (60 * 1000,)
                ),

                patterns=(
                    PatternData(skills=EASY_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.until_burst, time_args=(20, 3, 60, 60 * 30),
                        on_fire=pattern.inc_n_way, fire_args=(3, 24, 4, 1),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=60*11, bullet_id=bullet.RED_BIG, active=True,
                        on_time=pattern.until_time, time_args=(90, 60 * 20),
                        on_fire=pattern.aimed, fire_args=(4,),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=60*31, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(5, 60 * 40),
                        on_fire=pattern.spiral, fire_args=(3, 24, 2, 1),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=60*41, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(5, 60 * 30),
                        on_fire=pattern.spiral, fire_args=(3, 32, 2, -1),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=60*51, bullet_id=bullet.RED_BIG, active=True,
                        on_time=pattern.until_time, time_args=(120, 60 * 20),
                        on_fire=pattern.aimed, fire_args=(2,),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=60*51, bullet_id=bullet.PURPLE_BIG, active=True,
                        on_time=pattern.until_time, time_args=(90, 60 * 20),
                        on_fire=pattern.inc_n_way, fire_args=(3, 8, 8, 1),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=60*71, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(5, 60 * 50),
                        on_fire=pattern.n_random, fire_args=(3, 4, 3),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=60*86, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(5, 60 * 35),
                        on_fire=pattern.n_random, fire_args=(3, 4, 2),
                        toggle=None
                    ),
                    PatternData(skills=EASY_ONLY,
                        cooldown=60*101, bullet_id=bullet.PURPLE_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(5, 60 * 20),
                        on_fire=pattern.n_random, fire_args=(3, 4, 2),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.until_burst, time_args=(20, 5, 60, 60 * 40),
                        on_fire=pattern.inc_n_way, fire_args=(3, 32, 4, 1),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60*11, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.until_burst, time_args=(20, 5, 60, 60 * 30),
                        on_fire=pattern.inc_n_way, fire_args=(3, 24, 4, -1),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60*21, bullet_id=bullet.CYAN_BIG, active=True,
                        on_time=pattern.until_burst, time_args=(10, 3, 90, 60 * 20),
                        on_fire=pattern.aimed, fire_args=(2,),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60*41, bullet_id=bullet.PURPLE_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(120, 60 * 29),
                        on_fire=pattern.circles, fire_args=(3, 24, 6, 0, 60),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60*41, bullet_id=bullet.YELLOW_BIG, active=True,
                        on_time=pattern.until_burst, time_args=(5, 3, 60, 60 * 29),
                        on_fire=pattern.inc_n_way, fire_args=(2, 8, 8, 1),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60*71, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(5, 60 * 50),
                        on_fire=pattern.n_random, fire_args=(3, 4, 5),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60*71, bullet_id=bullet.BLUE_BIG, active=True,
                        on_time=pattern.until_time, time_args=(20, 60 * 50),
                        on_fire=pattern.spiral, fire_args=(3, 5, 4, -1),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60*81, bullet_id=bullet.RED_SMALL, active=True,
                        on_time=pattern.until_burst, time_args=(2, 5, 60, 60 * 40),
                        on_fire=pattern.spread_aimed, fire_args=(3, 5, 90),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60*91+40, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.until_burst, time_args=(2, 5, 60, 60 * 30),
                        on_fire=pattern.spread_aimed, fire_args=(3, 4, 90),
                        toggle=None
                    ),
                    PatternData(skills=NORMAL_ONLY,
                        cooldown=60*101, bullet_id=bullet.PURPLE_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(5, 60 * 20),
                        on_fire=pattern.n_random, fire_args=(3, 4, 5),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(20, 60 * 40),
                        on_fire=pattern.inc_n_way, fire_args=(4, 32, 8, 1),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60*11, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(20, 60 * 30),
                        on_fire=pattern.inc_n_way, fire_args=(4, 24, 6, -1),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60*21, bullet_id=bullet.RED_BIG, active=True,
                        on_time=pattern.until_burst, time_args=(10, 3, 90, 60 * 50),
                        on_fire=pattern.multi_aimed, fire_args=((4, 3, 2),),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60*41, bullet_id=bullet.PURPLE_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(90, 60 * 29),
                        on_fire=pattern.circles, fire_args=(4, 24, 8, 0, 60),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60*41, bullet_id=bullet.YELLOW_BIG, active=True,
                        on_time=pattern.until_burst, time_args=(5, 3, 60, 60 * 29),
                        on_fire=pattern.inc_n_way, fire_args=(3, 8, 8, -1),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60*51, bullet_id=bullet.CYAN_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(90, 60 * 65),
                        on_fire=pattern.inc_n_way, fire_args=(1, 32, 2, 1),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60*71, bullet_id=bullet.YELLOW_SMALL, active=True,
                        on_time=pattern.until_time, time_args=(6, 60 * 50),
                        on_fire=pattern.n_random, fire_args=(3, 4, 3),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60*71, bullet_id=bullet.BLUE_BIG, active=True,
                        on_time=pattern.until_time, time_args=(20, 60 * 50),
                        on_fire=pattern.spiral, fire_args=(3, 10, 8, -1),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60*81, bullet_id=bullet.RED_SMALL, active=True,
                        on_time=pattern.until_burst, time_args=(2, 5, 60, 60 * 40),
                        on_fire=pattern.spread_aimed, fire_args=(3, 7, 90),
                        toggle=None
                    ),
                    PatternData(skills=HARD_ONLY,
                        cooldown=60*91, bullet_id=bullet.BLUE_SMALL, active=True,
                        on_time=pattern.until_burst, time_args=(2, 5, 60, 60 * 30),
                        on_fire=pattern.spread_aimed, fire_args=(3, 6, 90),
                        toggle=None
                    ),
                ),
            ),
        )
    }
}

# Below is a commented example
#1: {  # Data for level 1
#    'number': 1,
#    'lives': (3, 3, 2),  # easy, medium, and hard lives
#    'goal': (75.00, 85.00, 90.00),  # easy, medium, and hard goals
#    'time': (120, 120, 60),  # easy, medium, and hard time limit
#    'enemies': (  # n-tuple of EnemyData objects
#        EnemyData(
#            # These are self-explanatory mostly
#            # Enemy type will be constants for each type of enemy
#            skills=EASY_PLUS, enemy_id=1,
#            start_pos=(400, 440), speed=3,
#
#            # Tuple of coords; if a 1-tuple, defines wait time, otherwise,
#            # defines coords to move to
#            # Note: if you get 'tuple object is not callable' make sure
#            # you're not missing a comma
#            # Do not take the status bar into account; the adjustment will
#            # be done in enemy.py
#            movement=(
#                (700, 440), (60,), (700, 100), (100, 100), (300, 240),
#                (120,), (100, 440),
#            ),
#
#            # n-tuple of PatternData objects
#            patterns=(
#                PatternData(skills=EASY_PLUS,
#                    cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
#                    on_time=pattern.same_time, time_args=(240,),
#                    on_fire=pattern.n_way, fire_args=(5, 8),
#                    toggle=None  # Whether to toggle this pattern at a %
#                ),
#                PatternData(skills=HARD_ONLY,
#                    cooldown=1, bullet_id=bullet.YELLOW_SMALL, active=False,
#                    on_time=pattern.same_time, time_args=(5,),
#                    on_fire=pattern.spammy, fire_args=(),
#                    toggle=50.0  # When 50% grass is mowed, turn this on
#                ),
#            )
#        ),
#
#        EnemyData(
#            skills=EASY_PLUS, enemy_id=1,
#            start_pos=(400, 440), speed=2,
#
#            movement=(
#                (100, 440), (60,), (100, 100), (700, 100), (700, 440),
#            ),
#
#            patterns=(
#                PatternData(skills=EASY_PLUS,
#                    cooldown=60, bullet_id=bullet.YELLOW_SMALL, active=True,
#                    on_time=pattern.random_time, time_args=(120, 160),
#                    on_fire=pattern.aimed, fire_args=(4,),
#                    toggle=None
#                ),
#            )
#        ),
#    )
#}
