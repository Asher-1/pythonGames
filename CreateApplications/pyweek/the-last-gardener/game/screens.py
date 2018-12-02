from __future__ import division, print_function, unicode_literals

import pyglet
from pyglet import resource
from pyglet.text import Label
from pyglet.window import key

from constants import *
from level import Level
from level_data import level_dict
import sounds
import story
from status_bar import StatusBar

class ScreenManager(object):
    """Manages the various screens (or states) within the game."""
    def __init__(self, game):
        self.game = game
        self.screens = {}
        self._current = None

    @property
    def current(self):
        return self._current

    def add(self, identifier, screen):
        """Adds a screen. Does not switch to the added screen."""
        self.screens[identifier] = screen

    def change(self, identifier):
        """Changes the current screen."""
        if self._current:
            self._current.on_inactive()

        self._current = self.screens[identifier]
        self._current.on_active()

    def remove(self, identifier):
        """Remove a screen.

        If the screen being removed is the current one, there will be no
        current screen, so make sure to switch to another screen immediately
        afterwards.
        """
        target = self.screens[identifier]
        if target == self._current:
            self._current.on_inactive()
            self._current = None

        del self.screens[identifier]

    def update(self, dt):
        self._current.update(dt)

    def draw(self):
        self._current.draw()


class Screen(object):
    def __init__(self, game):
        self.game = game

    def on_active(self):
        """Called when the screen is switched to.

        Implementors should add event handlers here.
        """
        raise NotImplementedError('implement on_active')

    def on_inactive(self):
        """Called when the screen is switched from or removed.

        Implementors should remove event handlers here.
        """
        raise NotImplementedError('implement on_inactive')


    def update(self, dt):
        """Update the game logic associated with this screen."""
        raise NotImplementedError('implement update')

    def draw(self):
        """Render the screen."""
        raise NotImplementedError('implement draw')


class MainMenuScreen(Screen):
    def __init__(self, game):
        super(MainMenuScreen, self).__init__(game)

        # Note: the title's words and the 'A PyWeek entry...' are in the
        # background image itself

        # 0: left white, 1: right white, 2: left yellow, 3: right yellow
        self.arrows = [resource.image('left_arrow.png'),
                       resource.image('right_arrow.png'),
                       resource.image('left_selected.png'),
                       resource.image('right_selected.png')]

        for i, arrow in enumerate(self.arrows):
            # Anchor to the right any arrows that face left
            if i % 2 == 0:
                arrow.anchor_x = arrow.width

            arrow.anchor_y = arrow.height // 2

        # Arrow Cursor
        self.cursor = resource.image('menu_cursor.png')
        self.cursor.anchor_x = self.cursor.width
        self.cursor.anchor_y = self.cursor.height // 2

        #Background image
        self.background = resource.image('background_1.png')

        option_names = ('Start Game', 'Music:', 'Sound:', 'Exit Game')
        self.options = []
        self._option_index = 0
        self._on_select = (self._start, self._toggle_music,
                           self._toggle_sound, self._exit)
        self._on_arrow = (None, self._toggle_music, self._toggle_sound, None)

        # For centered main menu: y = 200 + ...
        for i, name in enumerate(option_names):
            temp_y = 60 + 50 * (len(option_names) - i - 1)

            # For centered main menu: x = 302
            temp = Label(name, font_name=DEFAULT_FONT, font_size=20,
                         anchor_x='left', anchor_y='center',
                         x=540, y=temp_y)
            self.options.append(temp)

        # More hardcoding whee
        # For centered main menu: x = 452
        self._music = Label('', font_name=DEFAULT_FONT, font_size=20,
                                anchor_x='center', anchor_y='center',
                                x=690, y=self.options[1].y)
        self._sound = Label('', font_name=DEFAULT_FONT, font_size=20,
                                anchor_x='center', anchor_y='center',
                                x=690, y=self.options[2].y)

    def on_active(self):
        self._option_index = 0

        sounds.play_music('menu')

        self.game.window.push_handlers(self.on_key_press)

    def on_inactive(self):
        self.game.window.pop_handlers()

        # Save changed music and sound preferences
        self.game.profile.save()

    def on_key_press(self, symbol, modifiers):
        if symbol in (key.SPACE, key.ENTER):
            on_select = self._on_select[self._option_index]
            if on_select is not None:
                sounds.play_sound('menu_select')
                on_select()

        elif symbol == key.UP:
            if self._option_index != 0:
                sounds.play_sound('menu_move')
                self._option_index -= 1

        elif symbol == key.DOWN:
            if self._option_index != len(self.options) - 1:
                sounds.play_sound('menu_move')
                self._option_index += 1

        elif symbol in (key.LEFT, key.RIGHT):
            on_arrow = self._on_arrow[self._option_index]
            if on_arrow is not None:
                sounds.play_sound('menu_move')
                on_arrow()

    def update(self, dt):
        self._music.text = 'On' if sounds.music_on else 'Off'
        self._sound.text = 'On' if sounds.sound_on else 'Off'

    def _start(self):
        self.game.screens.add('levels', LevelSelectScreen(self.game))
        self.game.screens.change('levels')

    def _toggle_sound(self):
        sounds.toggle_sound()
        self.game.profile['sound'] = sounds.sound_on

    def _toggle_music(self):
        sounds.toggle_music('menu')
        self.game.profile['music'] = sounds.music_on

    def _exit(self):
        self.game.screens.remove('main')
        self.game.window.close()

    def draw(self):
        # Background image
        self.background.blit(0,0)

        for i, option in enumerate(self.options):
            option.color = YELLOW if i == self._option_index else WHITE

            # For centered main menu, x = 302 - 10
            if i == self._option_index:
                self.cursor.blit(540 - 10, option.y)
            option.draw()

        self._draw_value(self._music, 1, 30)
        self._draw_value(self._sound, 2, 30)


    def _draw_value(self, label, label_index, x_offset):
        if self._option_index == label_index:
            label.color = YELLOW
            self.arrows[2].blit(label.x - x_offset, label.y)
            self.arrows[3].blit(label.x + x_offset, label.y)
        else:
            label.color = WHITE
            self.arrows[0].blit(label.x - x_offset, label.y)
            self.arrows[1].blit(label.x + x_offset, label.y)

        label.draw()

class LevelSelectScreen(Screen):
    def __init__(self, game):
        super(LevelSelectScreen, self).__init__(game)

        # Note: the words of the title are in the background itself

        # Background
        self.background = resource.image('background_2.png')
        # 0: left white, 1: right white, 2: left yellow, 3: right yellow
        self.arrows = [resource.image('left_arrow.png'),
                       resource.image('right_arrow.png'),
                       resource.image('left_selected.png'),
                       resource.image('right_selected.png')]

        for i, arrow in enumerate(self.arrows):
            # Anchor to the right any arrows that face left
            if i % 2 == 0:
                arrow.anchor_x = arrow.width

            arrow.anchor_y = arrow.height // 2

        self.cursor = resource.image('menu_cursor.png')
        self.cursor.anchor_x = self.cursor.width
        self.cursor.anchor_y = self.cursor.height // 2

        # Yay copy and paste
        option_names = ('Level:', 'Difficulty:', 'Start Level',
                        'Back To Main Menu')
        self.options = []
        self._option_index = 0
        self._on_select = (None, None, self._play, self._go_back)
        self._on_left = (self._level_left, self._skill_left, None, None)
        self._on_right = (self._level_right, self._skill_right, None, None)

        self._level_nums = None
        self._level_index = min(len(level_dict),
                            self.game.profile.get('unlocked', 1)) - 1
        self._skills = ('Easy', 'Normal', 'Hard')  # Matches w/ Level constants
        self._skill_index = self.game.profile.get('cur_skill', 1)

        for i, name in enumerate(option_names):
            # For centered level select: y = 200 + ...
            temp_y = 57 + 50 * (len(option_names) - i - 1)

            # For centered level select: x = 250
            temp = Label(name, font_name=DEFAULT_FONT, font_size=20,
                         anchor_x='left', anchor_y='center',
                         x=482, y=temp_y)
            self.options.append(temp)

        # For centered level select: x = 385
        self._cur_level = Label('', font_name=DEFAULT_FONT, font_size=20,
                                anchor_x='center', anchor_y='center',
                                x=617, y=self.options[0].y)

        #For centered level select: x = 475
        self._cur_skill = Label('', font_name=DEFAULT_FONT, font_size=20,
                                anchor_x='center', anchor_y='center',
                                x=707, y=self.options[1].y)

        self.medals = {Level.PASSED: resource.image('medal_bronze.png'),
                       Level.GRASS_CLEAR: resource.image('medal_silver.png'),
                       Level.PERFECT_CLEAR: resource.image('medal_gold.png')}
        self.result = None

        for img in self.medals.itervalues():
            img.anchor_x = img.width // 2
            img.anchor_y = img.height // 2

    def on_active(self):
        self._option_index = 0

        # FIXME: self._level_index should be the last level played
        if self.game.profile.last_played is not None:
            self._level_index = self.game.profile.last_played - 1

        # Recreate the list of unlocked levels based on the highest
        # unlocked level (if 11, it's 10 instead)
        max_num = min(len(level_dict), self.game.profile.get('unlocked', 1))
        self._level_nums = [i + 1 for i in range(max_num)]

        sounds.play_music('menu')

        self.game.window.push_handlers(self.on_key_press)

    def on_inactive(self):
        self.game.window.pop_handlers()

        self.game.profile['cur_skill'] = self._skill_index
        self.game.profile.save()

    def on_key_press(self, symbol, modifiers):
        if symbol in (key.SPACE, key.ENTER):
            on_select = self._on_select[self._option_index]
            if on_select is not None:
                sounds.play_sound('menu_select')
                on_select()

        elif symbol == key.UP:
            if self._option_index != 0:
                sounds.play_sound('menu_move')
                self._option_index -= 1

        elif symbol == key.DOWN:
            if self._option_index != len(self.options) - 1:
                sounds.play_sound('menu_move')
                self._option_index += 1

        elif symbol == key.LEFT:
            on_left = self._on_left[self._option_index]
            if on_left is not None:
                on_left()

        elif symbol == key.RIGHT:
            on_right = self._on_right[self._option_index]
            if on_right is not None:
                on_right()

        elif symbol == key.ESCAPE:
            sounds.play_sound('menu_select')
            self._go_back()

            # Escape, by default, exits the program, so don't propogate the
            # event further
            return True

    def _level_left(self):
        if self._level_index == 0:
            return

        sounds.play_sound('menu_move')
        self._level_index -= 1

    def _level_right(self):
        if self._level_index == len(self._level_nums) - 1:
            return

        sounds.play_sound('menu_move')
        self._level_index += 1

    def _skill_left(self):
        if self._skill_index == 0:
            return

        sounds.play_sound('menu_move')
        self._skill_index -= 1

    def _skill_right(self):
        if self._skill_index == len(self._skills) - 1:
            return

        sounds.play_sound('menu_move')
        self._skill_index += 1

    def _play(self):
        level = self._level_nums[self._level_index]
        skill = self._skill_index  # See level.py

        gameplay = GameplayScreen(self.game, level, skill)

        story_key = level_dict[level]['story_before']
        if story_key is not None:
            story = StoryScreen(self.game, story_key, 'gameplay', gameplay)

            self.game.screens.add('story', story)
            self.game.screens.change('story')
        else:
            self.game.screens.add('gameplay', gameplay)
            self.game.screens.change('gameplay')

    def _go_back(self):
        self.game.screens.remove('levels')
        self.game.screens.change('main')

    def update(self, dt):
        level_num = self._level_nums[self._level_index]
        skill_name = self._skills[self._skill_index]
        skill_num = self._skill_index

        self._cur_level.text = str(level_num)
        self._cur_skill.text = skill_name
        self.result = self.game.profile.get_result(level_num, skill_num)

    def draw(self):
        # Background
        self.background.blit(0,0)

        for i, option in enumerate(self.options):
            option.color = YELLOW if i == self._option_index else WHITE

            # For centered level select: x = 250-10
            if i == self._option_index:
                self.cursor.blit(482 - 10, option.y)
            option.draw()

        # Yay hardcoding...
        self._draw_value(self._cur_level, 0, self._level_index,
                         len(self._level_nums) - 1, 30)
        self._draw_value(self._cur_skill, 1, self._skill_index,
                         len(self._skills) - 1, 60)

        if self.result is not None:
            self.medals[self.result].blit(self.options[0].x + 220,
                                          self.options[0].y)

    # label = label to draw, label_index = index of associated option,
    # selected = index of currently selected value
    # max_index =  highest possible index
    # x_offset = controls arrow spacing
    def _draw_value(self, label, label_index, selected, max_index, x_offset):
        if self._option_index == label_index:
            label.color = YELLOW

            # Don't draw an arrow if it is at the leftmost or rightmost pos
            if selected != 0:
                self.arrows[2].blit(label.x - x_offset, label.y)
            if selected != max_index:
                self.arrows[3].blit(label.x + x_offset, label.y)
        else:
            label.color = WHITE

            if selected != 0:
                self.arrows[0].blit(label.x - x_offset, label.y)
            if selected != max_index:
                self.arrows[1].blit(label.x + x_offset, label.y)

        label.draw()


class StoryScreen(Screen):
    def __init__(self, game, data_key, screen_key, new_screen=None):
        super(StoryScreen, self).__init__(game)

        self.data = story.slides[data_key]
        self._index = -1  # _advance() will make it 0

        self.label = Label(text='', multiline=True,
                           font_name=DEFAULT_FONT, font_size=16,
                           x=10, y=75, width=self.game.window.width - 20)
        self.text_box = resource.image('story_bar.png')

        controls_text = 'Space or Enter to advance, Escape to skip'
        self.controls_label = Label(text=controls_text,
                                    font_name=DEFAULT_FONT, font_size=12,
                                    anchor_x='right', x=790, y=5)

        self.image = None

        self.screen_key = screen_key
        self.new_screen = new_screen  # Required if key doesn't exist yet

        self._advance()

    def on_active(self):
        sounds.play_music('menu')

        self.game.window.push_handlers(self.on_key_press)

    def on_inactive(self):
        self.game.window.pop_handlers()

    def _advance(self):
        self._index += 1

        if self._index == len(self.data):
            self._finish()
            return

        new_slide = self.data[self._index]

        self.label.text = new_slide[0]
        if new_slide[1] is not None:
            self.image = resource.image(new_slide[1])

    def on_key_press(self, symbol, modifiers):
        if symbol in (key.SPACE, key.ENTER):
            sounds.play_sound('menu_select')
            self._advance()

        elif symbol == key.ESCAPE:
            sounds.play_sound('menu_select')
            self._finish()

            # Escape, by default, exits the program, so don't propogate the
            # event further
            return True

    def _finish(self):
        self.game.screens.remove('story')

        if self.new_screen is not None:
            self.game.screens.add(self.screen_key, self.new_screen)

        self.game.screens.change(self.screen_key)

    def update(self, dt):
        pass

    def draw(self):
        if self.image is not None:
            self.image.blit(0, 0)

        self.text_box.blit(0, 0)
        self.controls_label.draw()
        self.label.draw()


class GameplayScreen(Screen):
    def __init__(self, game, level_num, skill):
        super(GameplayScreen, self).__init__(game)

        self.level = Level(level_dict[level_num], skill)
        self.player = self.level.player
        self.status_bar = StatusBar(self.level)
        self.paused = False

        self.finished = False
        self.show_story = False  # For after-level story events
        self.popup = None

        # Arguments to pass to the Popup constructor
        self._popup_info = {  # text, color
            Level.PASSED: ('Level Clear!', LIGHT_BLUE, 'ribbon_bronze.png'),
            Level.GRASS_CLEAR: ('Fully Mowed!', SILVER, 'ribbon_silver.png'),
            Level.PERFECT_CLEAR: ('Perfect!', GOLD, 'ribbon_gold.png'),
            Level.DIED: ('Level Failed!', RED, None),
            Level.TIME_UP: ('Time Up!', RED, None),
        }

        # lol hardcoding
        self._music_key = 'boss' if level_num == len(level_dict) else 'gameplay'

    def on_active(self):
        sounds.play_music(self._music_key, True)

        self.game.profile.last_played = self.level.number

        self.game.window.push_handlers(self.level.player.on_key_press,
                                       self.level.player.on_key_release)
        self.game.window.push_handlers(self.on_key_press)

    def on_inactive(self):
        # Do it twice for both levels of event handlers
        self.game.window.pop_handlers()
        self.game.window.pop_handlers()

    def on_key_press(self, symbol, modifiers):
        if (symbol == key.ESCAPE and self.level.state == Level.ONGOING and
                self.popup is None):
            if not self.paused:
                self._pause()

            # Escape, by default, exits the program, so don't propogate the
            # event further
            return True

        if self.popup is not None:
            if symbol == key.UP:
                self.popup.go_up()
            elif symbol == key.DOWN:
                self.popup.go_down()
            elif symbol in (key.SPACE, key.ENTER):
                self.popup.select()
            elif symbol == key.ESCAPE:
                self.popup.on_escape()
                return True

            # Don't propogate any keypresses to the player while a popup is
            # currently active, unless it's the screenshot key
            if symbol != key.HOME:
                return True

    def _pause(self):
        self.paused = True

        # Stop the mowing sounds if the player is moving
        self.level.player.stop_sound()
        sounds.pause_music()

        options = ('Continue', 'Retry', 'Level Select')
        handlers = (self._unpause, self._restart, self._go_back)

        self.popup = Popup('Paused', WHITE, options, handlers, 0, self._unpause)

    def _unpause(self):
        self.popup = None
        self.paused = False

        sounds.play_music(self._music_key)

    def update(self, dt):
        if not self.paused:
            self.level.update(dt)
            self.status_bar.update(dt)

        # Crappy hack to change the music once the battle is over
        if (self.level.number == len(level_dict) and not self.paused and
                self.level.time_left < 875 * 60 and not self.finished):
            self._music_key = 'gameplay'
            sounds.play_music(self._music_key)

        # If the level ended in some way, act on it
        if self.level.state != Level.ONGOING and not self.finished:
            self._check_state()

    def _next_level(self):
        next_num = self.level.number + 1
        if next_num > len(level_dict):
            self._go_back()
            return

        self.game.screens.remove('gameplay')  # Remove this screen

        gameplay = GameplayScreen(self.game, next_num, self.level.skill)

        story = None

        # First check if there is a before-level cutscene that needs to be
        # played; if so, attach the gameplay screen to that
        story_key = level_dict[next_num]['story_before']
        if story_key is not None:
            story = StoryScreen(self.game, story_key, 'gameplay', gameplay)

        story_key = level_dict[self.level.number]['story_clear']
        if story_key is not None:
            # Check if there is a before-level cutscene that needs to be
            # played after this level's after-level cutscene
            if story is not None:
                story = StoryScreen(self.game, story_key, 'story', story)
            # If not, attach the gampley to this one
            else:
                story = StoryScreen(self.game, story_key, 'gameplay', gameplay)

        if self.show_story and story is not None:
            self.game.screens.add('story', story)
            self.game.screens.change('story')
        else:
            self.game.screens.add('gameplay', gameplay)
            self.game.screens.change('gameplay')

    def _restart(self):
        screen = GameplayScreen(self.game, self.level.number, self.level.skill)
        # If the player previously passed the level and wants to retry, make
        # sure to still show the after-level cutscene if the player quits
        screen.show_story = self.show_story

        self.game.screens.remove('gameplay')
        self.game.screens.add('gameplay', screen)
        self.game.screens.change('gameplay')

    def _go_back(self):
        self.game.screens.remove('gameplay')

        story_key = level_dict[self.level.number]['story_clear']
        if self.show_story and story_key is not None:
            story = StoryScreen(self.game, story_key, 'levels')

            self.game.screens.add('story', story)
            self.game.screens.change('story')
        else:
            self.game.screens.change('levels')

    def _check_state(self):
        self.finished = True

        sounds.pause_music()

        fail_options = ('Retry', 'Level Select')
        fail_handlers = (self._restart, self._go_back)

        pass_options = ('Next Level', 'Retry', 'Level Select')
        pass_handlers = (self._next_level, self._restart, self._go_back)

        on_esc = self._go_back

        options = pass_options if self.level.was_passed else fail_options
        handlers = pass_handlers if self.level.was_passed else fail_handlers

        popup_info = self._popup_info[self.level.state]
        text = popup_info[0]
        color = popup_info[1]
        medal = popup_info[2]

        self.popup = Popup(text, color, options, handlers, 0, on_esc, medal)

        if self.level.was_failed:
            sounds.play_sound('failure')
        elif self.level.state in (Level.PASSED, Level.GRASS_CLEAR):
            sounds.play_sound('victory')
        elif self.level.state == Level.PERFECT_CLEAR:
            sounds.play_sound('big_victory')
        else:
            # We should never get here
            raise ValueError('this is bad')

        if self.level.was_passed:
            # Even if you retry and then quit, still show the story
            self.show_story = True

            # update_result() saves as well
            self.game.profile.update_result(self.level.number, self.level.skill,
                                            self.level.state)

    def draw(self):
        self.level.draw()
        self.status_bar.draw()

        if self.popup is not None:
            self.popup.draw()


class Popup(object):
    X = 400
    Y = 270 + 60
    HEIGHT = 200

    # 'options' supports three items at most
    def __init__(self, main_msg, main_color, options, handlers,
                 default_opt, on_escape, medal=None):
        # Background
        self.bg = resource.image('level_popup.png')
        self.bg.anchor_x = self.bg.width // 2
        self.bg.anchor_y = self.bg.height // 2

        # Arrow
        self.arrow = resource.image('menu_cursor.png')
        self.arrow.anchor_x = self.arrow.width
        self.arrow.anchor_y = self.arrow.height // 2

        self.main_label = Label(main_msg, font_name=DEFAULT_FONT, font_size=48,
                                color=main_color, x=Popup.X, y=Popup.Y + 50,
                                anchor_x='center', anchor_y='center')

        self.options = []
        interval = 90 // len(options)

        for i, option in enumerate(options):
            temp_y = (Popup.Y - 60) + interval * (len(options) - i - 1)
            temp = Label(option, font_name=DEFAULT_FONT, font_size=20,
                         x=Popup.X - 80, y=temp_y,
                         anchor_x='left', anchor_y='center')
            self.options.append(temp)

        self._option_index = default_opt
        self._handlers = handlers

        self.on_escape = on_escape

        self.medal = None
        if medal is not None:
            self.medal = resource.image(medal)
            self.medal.anchor_x = self.medal.width // 2
            self.medal.anchor_y = self.medal.height  # Hang it from the top

    def go_up(self):
        sounds.play_sound('menu_move')

        self._option_index -= 1
        if self._option_index < 0:
            self._option_index = len(self.options) - 1

    def go_down(self):
        sounds.play_sound('menu_move')
        self._option_index = (self._option_index + 1) % len(self.options)

    def select(self):
        sounds.play_sound('menu_select')
        self._handlers[self._option_index]()

    def draw(self):
        self.bg.blit(Popup.X, Popup.Y)

        self.main_label.draw()

        for i, option in enumerate(self.options):
            option.color = YELLOW if i == self._option_index else WHITE

            # Draw the arrow.
            # 85 = 80 + spacing between arrow and text
            if i == self._option_index:
                self.arrow.blit(Popup.X - 90, option.y)

            option.draw()

        if self.medal is not None:
            self.medal.blit(Popup.X + 150, Popup.Y + 10)
