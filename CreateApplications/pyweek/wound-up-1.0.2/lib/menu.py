'''menu.py - the interface for the game menu, loaded at startup'''

import random

import pygame
from pygame.locals import *
from pygame.constants import *

import data
import level
import game
import music
import model
import display
import time
import times
import sound
from constants import *


c_menutext = (115, 64, 26)

neutral_modes = ['normal', 'show credits', 'show times', 'show controls']


class Menu(object):
    
    def __init__(self, renderer, options):
        self.camera_pos, self.map_size, self.tutorial, self.state = level.TitleLevel.load()

        self.renderer = renderer(self.state, self, options["renderer"])
        self.musicman = music.MusicMan(vol=0.5)
        self.soundman = sound.SoundMan()
        self.setup_pygame()

        self.times = times.BestTimes()
        
        self.position_camera()

        self.update_ticks = 25
        self.frame_ticks = 25

        self.p_cursor = (0, 0)

        self.set_mode('normal')
        self.is_valid = None
        
        self.state.elves_remaining = lambda: 1 # what a hack!

    def position_camera(self):
        pos, zoom = self.camera_pos
        if pos is not None: self.renderer.camera.setPosition(pos)
        else: self.renderer.camera.setPosition(self.state.spring.pos)
        if zoom is not None: self.renderer.camera.setZoom(zoom)
        else: self.renderer.camera.setZoom(10)

    def setup_pygame(self):
        pygame.init()
        self.font_name = data.filepath("font/Tuffy_Bold.ttf")
        self.renderer.setup_pygame()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.get_surface()
        self.scr_w, self.scr_h = self.screen.get_size()
        self.musicman.new_song(TITLE_MUSIC, loop=-1)

    def update_cursor(self):
        self.p_cursor = pygame.mouse.get_pos()

    def handle_events(self):
        for evt in pygame.event.get():
            if evt.type == QUIT:
                self.abort = True

            if evt.type == MOUSEBUTTONDOWN:
                if evt.button == 1 and self.mode == 'select level':
                    self.start_game()

                elif evt.button == 1 and self.mode == 'normal':
                    action = self.get_text_block(self.menu_areamap)
                    if action is not None:
                        func, args = action
                        func(*args)

                elif evt.button == 1 and self.mode == 'show times':
                    self.switch_page()

                elif evt.button == 1 and self.mode in neutral_modes:
                    self.set_mode('normal')

                elif (evt.button == 2 or evt.button == 3):
                    self.set_mode('normal')

            elif evt.type == KEYDOWN:
                if evt.key == K_LEFTBRACKET:
                    self.musicman.change_vol(-0.1)

                if evt.key == K_RIGHTBRACKET:
                    self.musicman.change_vol(0.1)

                if evt.key == K_ESCAPE:
                    if self.mode == 'normal':
                        self.abort = True
                    else:
                        self.set_mode('normal')

                elif evt.key == K_RETURN:
                    if self.mode == 'select level':
                        self.switch_page()
                    elif self.mode == 'show times':
                        self.switch_page()
                    elif self.mode in neutral_modes:
                        self.set_mode('select level')
                    elif self.mode == 'name entry':
                        self.save_best_time()
                        self.set_mode('normal')

                elif self.mode == 'name entry':
                    char = evt.unicode.upper()
                    n = self.current_best_time_name
                    if char in BEST_TIME_NAME_VALID:
                        if len(n) == BEST_TIME_NAME_LENGTH:
                            n = n[:-1] + char
                        else:
                            n += char
                    elif evt.key == K_BACKSPACE:
                        n = n[:-1]
                    self.current_best_time_name = n
                    self.draw_name_entry()

                elif evt.key == K_c:
                    if self.mode in neutral_modes:
                        self.set_mode('show credits')

                elif evt.key == K_t:
                    if self.mode in neutral_modes:
                        self.set_mode('show times')

                elif evt.key == K_i:
                    if self.mode in neutral_modes:
                        self.set_mode('show controls')

            elif evt.type == SOUND_EVENT:
                self.soundman.handle_sound_event(evt)
    
    def main_loop(self):
        wandering_elf = list(self.state.elves)[0]
    
        while not self.abort:
            cur_ticks = pygame.time.get_ticks()
            frame_step = cur_ticks - self.last_frame
            update_step = cur_ticks - self.last_update
            
            if frame_step > self.frame_ticks and update_step < self.update_ticks:
                self.update_cursor()
                self.renderer.draw()
                self.clock.tick()
                self.last_frame = cur_ticks
            
            for i in xrange(update_step // self.update_ticks):
                self.state.tick()
                self.musicman.update()
                self.last_update = cur_ticks
                
            self.handle_events()
            
            if len(wandering_elf.path) == 1:
                new_dest = random.choice(self.state.random_destinations)
                wandering_elf.send_to(self.state, new_dest)

    def run(self):
        cur_ticks = pygame.time.get_ticks()
        self.last_update = cur_ticks
        self.last_frame = cur_ticks
        self.abort = False
        self.main_loop()

    def blank_text(self):
        surf = self.renderer.menutext_overlay.surf
        surf.fill((0,0,0,0))
        return surf

    def clear_text(self):
        self.blank_text()
        self.renderer.menutext_overlay.updateTexture()

    def draw_main_menu(self):
        surf = self.blank_text()
        s_width, s_height = surf.get_size()
        font = pygame.font.Font(self.font_name, 10)

        x_pos, y_pos = 20, 20
        
        lines = [
            ("* Start Game", (self.set_mode, ('select level',))),
            ("* High Scores", (self.set_mode, ('show times',))),
            ("* Controls", (self.set_mode, ('show controls',))),
            ("* Credits", (self.set_mode, ('show credits',))),
            ("* Quit", (self.close_game, ())),
        ]

        self.menu_areamap = []
        for line, action in lines:
            new_y_pos = y_pos
            text = font.render(line, True, c_menutext)
            t_width, t_height = text.get_size()
            surf.blit(text, (x_pos, new_y_pos))
            block_width = t_width
            new_y_pos += t_height

            self.menu_areamap.append((action, (x_pos, y_pos, block_width, new_y_pos - y_pos)))
            y_pos = new_y_pos + t_height / 2
        
        self.renderer.menutext_overlay.updateTexture()

    def draw_level_list(self):
        surf = self.blank_text()
        s_width, s_height = surf.get_size()
        font = pygame.font.Font(self.font_name, 10)
        
        x_pos, y_pos = 20, 20
        numpages = self.get_num_level_select_pages()
        text = font.render("Page %d of %d. Click on a level to start." % (self.page+1, numpages), True, c_menutext)
        t_width, t_height = text.get_size()
        surf.blit(text, (x_pos, y_pos))
        y_pos += t_height*2

        levels = self.get_levels()
        levels = levels[self.page * LEVELS_PER_PAGE : (self.page+1) * LEVELS_PER_PAGE]

        self.level_areamap = []
        for lvl in levels:
            new_y_pos = y_pos
            unlocked = self.level_unlocked(lvl)
            if unlocked:
                text = font.render(lvl.name, True, c_menutext)
            else:
                text = font.render("???", True, c_menutext)
            t_width, t_height = text.get_size()
            surf.blit(text, (x_pos, new_y_pos))
            block_width = t_width
            new_y_pos += t_height

            text = "This level has not yet been unlocked."
            if unlocked:
                text = lvl.desc
            
            for line in text.split("\n"):
                text = font.render(line, True, c_menutext)
                t_width, t_height = text.get_size()
                surf.blit(text, (x_pos, new_y_pos))
                block_width = max(block_width, t_width)
                new_y_pos += t_height

            if unlocked:
                self.level_areamap.append((lvl.name, (x_pos, y_pos, block_width, new_y_pos - y_pos)))
            y_pos = new_y_pos + t_height

        y_pos += t_height
        
        if self.page > 0:
            text = font.render("Previous page", True, c_menutext)
            t_width, t_height = text.get_size()
            surf.blit(text, (x_pos, y_pos))
            self.level_areamap.append((1, (x_pos, y_pos, t_width, t_height)))
            y_pos += t_height
        
        if self.page < numpages - 1:
            text = font.render("Next page", True, c_menutext)
            t_width, t_height = text.get_size()
            surf.blit(text, (x_pos, y_pos))
            self.level_areamap.append((2, (x_pos, y_pos, t_width, t_height)))

        self.renderer.menutext_overlay.updateTexture()

    def render_text(self, lines):
        surf = self.blank_text()
        font = pygame.font.Font(self.font_name, 10)
        
        y_pos = 20
        for line in lines:
            text = font.render(line, True, c_menutext)
            t_width, t_height = text.get_size()
            surf.blit(text, (20, y_pos))
            y_pos += t_height

        self.renderer.menutext_overlay.updateTexture()

    def draw_controls(self):
        main_lines = [
            "Menu controls:",
            "<enter> - display level list",
            "C - display credits",
            "T - display best times",
            "I - display controls",
            "[, ] - change music volume",
            "<esc> - back/quit",
            "RMB - back",
            "",
            "Game controls:",
            "1, 2, 3, 4 - place cogs",
            "P - place platforms",
            "L - place ladders",
            "B - place belts",
            "W/Q - add/remove elves from spring",
            "U - unhook belts",
            "D - destroy cogs",
            "[, ] - change music volume",
            "-, = - zoom out/in",
            "mouse wheel - zoom out/in",
        ]
        self.render_text(main_lines)


    def draw_credits(self):
        credit_lines = data.load("personality.duck").read().split("\n")
        self.render_text(credit_lines)

    def level_unlocked(self, lev):
        for p in lev.prereqs:
            if not self.times.level_completed(p.name):
                return False
        return True

    def get_levels(self):
        levels = level.directory.values()
        levels.sort()
        return map(lambda x: x[1], levels)

    def get_unlocked_levels(self):
        return [x for x in self.get_levels() if self.level_unlocked(x)]

    def get_num_level_select_pages(self):
        numlevs = len(self.get_levels())
        return -(-numlevs // LEVELS_PER_PAGE)

    def get_num_best_times_pages(self):
        numtimes = len(self.get_unlocked_levels())
        return -(-numtimes // LEVELS_PER_PAGE)

    def draw_best_times(self):
        lines = ["Page %d of %d" % (self.page + 1, self.get_num_best_times_pages()), ""]
        levels = self.get_unlocked_levels()
        levels = levels[self.page * LEVELS_PER_PAGE : (self.page+1) * LEVELS_PER_PAGE]
        for lev in levels:
            times = self.times.get_best_times(lev.name)
            lines.append(lev.name + ":")
            i = 1
            for t, n in times:
                lines.append("#%d: %s %s" % (i, n, self.times.format_time(t, self.update_ticks)))
                i += 1
            lines.append("")
        self.render_text(lines)

    def draw_name_entry(self):
        n = self.current_best_time_name
        nstr = n + '_' * (BEST_TIME_NAME_LENGTH-len(n))
        lines = ["You got a record time!",
                 "",
                 "Level: %s" % self.current_best_time_level,
                 "Time: %s" % self.current_best_time_text,
                 "",
                 "Initials: %s" % " ".join(list(nstr))]
        self.render_text(lines)

    def get_text_block(self, areamap):
        px, py = map(lambda x: x * 512.0 / self.scr_h, self.p_cursor)
        for name, area in areamap:
            x, y, w, h = area
            if x <= px <= x+w and y <= py <= y+h:
                return name
        return None
    
    def close_game(self):
        self.abort = True

    def set_mode(self, mode, param=None):
        self.mode = mode
        self.mode_param = None
        if mode == 'normal':
            self.draw_main_menu()
        elif mode == 'select level':
            self.page = 0
            self.draw_level_list()
        elif mode == 'show credits':
            self.draw_credits()
        elif mode == 'show times':
            self.page = 0
            self.draw_best_times()
        elif mode == 'show controls':
            self.draw_controls()
        elif mode == 'name entry':
            self.draw_name_entry()
        else:
            self.clear_text()

    def switch_page(self, backwards=False):
        if backwards:
            self.page = max(self.page - 1, 0)
            if self.mode == 'show times':
                self.draw_best_times()
            elif self.mode == 'select level':
                self.draw_level_list()
        else:
            self.page += 1
            if self.mode == 'show times':
                if self.page >= self.get_num_best_times_pages():
                    self.set_mode('normal')
                    return
                self.draw_best_times()
            elif self.mode == 'select level':
                if self.page >= self.get_num_level_select_pages():
                    self.set_mode('normal')
                    return
                self.draw_level_list()

    def start_game(self):
        level_name = self.get_text_block(self.level_areamap)
        if level_name is None: return
        if level_name == 1:
            self.switch_page(backwards=True)
            return
        if level_name == 2:
            self.switch_page()
            return

        new_game = game.Game(level_name, renderer=self.renderer,
                musicman=self.musicman, soundman=self.soundman)

        self.renderer.interface = new_game
        self.renderer.state = new_game.state
        self.renderer.menu_mode = False
        self.renderer.update_tutorial()

        self.musicman.random_new_song(fadeout=1000)
        time = new_game.run()
        
        self.renderer.interface = self
        self.renderer.state = self.state
        self.renderer.menu_mode = True

        self.last_frame = pygame.time.get_ticks()
        self.last_update = pygame.time.get_ticks()

        # at least some of these should be replaced with a call to
        # renderer.set_state() if that ever exists
        self.position_camera()
        self.renderer.set_map_size((self.state.pgrid.w, self.state.pgrid.h))
        self.renderer.update_cursor((0, 0))
        self.state.pgrid.dirty = True

        self.musicman.new_song(TITLE_MUSIC, loop=-1)

        if time is not None and self.times.is_qualifying_time(level_name, time):
            self.current_best_time = time
            self.current_best_time_text = self.times.format_time(time, self.update_ticks)
            self.current_best_time_level = level_name
            self.current_best_time_name = 'XXX'
            self.set_mode('name entry')
        else:
            self.set_mode('normal')
            
    def save_best_time(self):
        self.times.add_time(self.current_best_time_level,\
                            self.current_best_time,\
                            self.current_best_time_name)
        self.times.save()
