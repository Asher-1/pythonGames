from pyglet import text
from pyglet import resource
from pyglet.gl import *
from pyglet.window import key



FONT_NAME = 'Saved By Zero'
ARENA_WIDTH = 480
ARENA_HEIGHT = 480

BEGIN_GAME = 0
SHOW_OPTIONS = 1
SHOW_INSTRUCTIONS = 2

dt=1/60.

class Overlay(object):
    def update(self, dt):
        pass

    def draw(self):
        pass

class Banner(Overlay):
    def __init__(self, label, dismiss_func=None, timeout=None):
        self.text = text.Label(label,
                                      font_name=FONT_NAME,
                                      font_size=36,
                                      x=ARENA_WIDTH / 2, 
                                      y=ARENA_HEIGHT / 2,
                                      anchor_x='center',
                                      anchor_y='center')

        self.dismiss_func = dismiss_func
        self.timeout = timeout
        if timeout and dismiss_func:
            pyglet.clock.schedule_once(dismiss_func, timeout)

    def draw(self):
        self.text.draw()

    def on_key_press(self, symbol, modifiers):
        if self.dismiss_func and not self.timeout:
            self.dismiss_func()
        return True

class Menu(Overlay):
    def __init__(self, title):
        self.items = []
        self.title_text = text.Label(title, 
                                            font_name=FONT_NAME,
                                            font_size=36,
                                            x=ARENA_WIDTH // 2, 
                                            y=350,
                                            anchor_x='center',
                                            anchor_y='center')

    def reset(self):
        self.selected_index = 0
        self.items[self.selected_index].selected = True

    def on_key_press(self, symbol, modifiers):
        return_value = None
        if symbol == key.DOWN:
            self.selected_index += 1
        elif symbol == key.UP:
            self.selected_index -= 1
        else:
            return_value = self.items[self.selected_index].on_key_press(symbol, modifiers)

        self.selected_index = min(max(self.selected_index, 0), 
                                  len(self.items) - 1)
                                 

        #if symbol in (key.DOWN, key.UP) and enable_sound:
        #   bullet_sound.play()
        if return_value:
            return return_value

    def draw(self):
        self.title_text.draw()
        for i, item in enumerate(self.items):
            item.draw(i == self.selected_index)

class MenuItem(object):
    pointer_color = (.46, 0, 1.)
    inverted_pointers = False

    def __init__(self, label, y, return_value):
        self.y = y
        self.text = text.Label(label,
                                      font_name=FONT_NAME,
                                      font_size=14,
                                      x=ARENA_WIDTH // 2, 
                                      y=y,
                                      anchor_x='center',
                                      anchor_y='center')
        self.return_value = return_value
        resource.path.append('./data')
        resource.reindex()
        
        self.pointer_image = resource.image('pointer.png')
        self.pointer_image.anchor_x = self.pointer_image.width // 2
        self.pointer_image.anchor_y = self.pointer_image.height // 2
        self.pointer_image_flip = resource.image('pointer.png', flip_x=True)

    def draw_pointer(self, x, y, color, flip=False):
        # Tint the pointer image to a color
        glPushAttrib(GL_CURRENT_BIT)
        glColor3f(*color)
        if flip:
            self.pointer_image_flip.blit(x, y)
        else:
            self.pointer_image.blit(x, y)
        glPopAttrib()

    def draw(self, selected):
        self.text.draw()

        if selected:
            self.draw_pointer(
                self.text.x - self.text.content_width / 2 - 
                    self.pointer_image.width / 2,
                self.y, 
                self.pointer_color,
                self.inverted_pointers)
            self.draw_pointer(
                self.text.x + self.text.content_width / 2 + 
                    self.pointer_image.width / 2,
                self.y,
                self.pointer_color,
                not self.inverted_pointers)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
           # if enable_sound:
            #    bullet_sound.play()
            return self.return_value

class ToggleMenuItem(MenuItem):
    pointer_color = (.27, .82, .25)
    inverted_pointers = True

    def __init__(self, label, value, y, toggle_func):
        self.value = value
        self.label = label
        self.toggle_func = toggle_func
        super(ToggleMenuItem, self).__init__(self.get_label(), y, None)

    def get_label(self):
        return self.label + (self.value and ': ON' or ': OFF')

    def on_key_press(self, symbol, modifiers):
        if symbol == key.LEFT or symbol == key.RIGHT:
            self.value = not self.value
            self.text.text = self.get_label()
            self.toggle_func(self.value)
            if enable_sound:
                bullet_sound.play()

class DifficultyMenuItem(MenuItem):
    pointer_color = (.27, .82, .25)
    inverted_pointers = True

    def __init__(self, y):
        super(DifficultyMenuItem, self).__init__(self.get_label(), y, None)

    def get_label(self):
        if difficulty == 0:
            return 'DIFFICULTY: PEBBLES'
        elif difficulty == 1:
            return 'DIFFICULTY: STONES'
        elif difficulty == 2:
            return 'DIFFICULTY: ASTEROIDS'
        elif difficulty == 3:
            return 'DIFFICULTY: METEORS'
        else:
            return 'DIFFICULTY: %d' % difficulty

    def on_key_press(self, symbol, modifiers):
        global difficulty
        if symbol == key.LEFT:
            difficulty -= 1
        elif symbol == key.RIGHT:
            difficulty += 1
        difficulty = min(max(difficulty, 0), MAX_DIFFICULTY)
        self.text.text = self.get_label()

        if symbol in (key.LEFT, key.RIGHT) and enable_sound:
            bullet_sound.play()

class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('Astraea')

        self.items.append(MenuItem('New Game', 240, BEGIN_GAME))
        self.items.append(MenuItem('Instructions', 200, SHOW_INSTRUCTIONS))
        self.items.append(MenuItem('Options', 160, SHOW_OPTIONS))
        self.items.append(MenuItem('Quit', 120, None))
        self.reset()
    


class OptionsMenu(Menu):
    def __init__(self):
        super(OptionsMenu, self).__init__('Options')

        self.items.append(DifficultyMenuItem(280))
        def set_enable_sound(value):
            global enable_sound
            enable_sound = value
        self.items.append(ToggleMenuItem('Sound', enable_sound, 240,
                                         set_enable_sound))
                                
        self.items.append(ToggleMenuItem('Vsync', win.vsync, 200, 
                                         win.set_vsync))

        def set_show_fps(value):
            global show_fps
            show_fps = value
        self.items.append(ToggleMenuItem('FPS', show_fps, 160, set_show_fps))
        self.items.append(MenuItem('Ok', 100, begin_main_menu))
        self.reset()

class InstructionsMenu(Menu):
    def __init__(self):
        super(InstructionsMenu, self).__init__('Instructions')

        self.items.append(MenuItem('Ok', 50, begin_main_menu))
        self.reset()

        self.instruction_text = text.Label(INSTRUCTIONS,
                                                  font_name=FONT_NAME,
                                                  font_size=14,
                                                  x=20, y=300,
                                                  width=ARENA_WIDTH - 40,
                                                  anchor_y='top',
                                                  multiline=True)

    def draw(self):
        super(InstructionsMenu, self).draw()
        self.instruction_text.draw()

class PauseMenu(Menu):
    def __init__(self):
        super(PauseMenu, self).__init__('Paused')

        self.items.append(MenuItem('Continue Game', 240, resume_game))
        self.items.append(MenuItem('Main Menu', 200, end_game))
        self.reset()
        
class MenuControl():
    def __init__(self, win):
        self.overlay = None
        self.paused = False
        self.win = win
     
    def begin_main_menu(self):
        print self.set_overlay(MainMenu())

    def begin_game(self):
        self.set_overlay(Banner('Get Ready', None, GET_READY_DELAY))
        
    def begin_options_menu(self):
        self.set_overlay(OptionsMenu())

    def begin_instructions_menu(self):
        self.set_overlay(InstructionsMenu())        

    def next_round(self,*args):
        self.set_overlay(Banner('Get Ready', begin_round, GET_READY_DELAY))

    def game_over(self):
        self.set_overlay(Banner('Game Over', end_game))

    def pause_game(self):
        self.paused = True
        self.set_overlay(PauseMenu())

    def resume_game(self):
        self.paused = False
        self.set_overlay(None)

    def end_game(self):
        self.paused = False
        self.in_game = False
        self.set_overlay(MainMenu())

    def set_overlay(self, new_overlay):
        if self.overlay:
            self.win.remove_handlers(self.overlay)
        self.overlay = new_overlay
        if self.overlay:
            self.win.push_handlers(self.overlay)