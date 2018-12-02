'''game.py - the interface to the game as a whole, instances are launched from
the menu'''

import random

import pygame
from pygame.locals import *
from pygame.constants import *

import data
import level
import model
import sound
import tutorial
import gl
from constants import *


class Game(object):
    
    def __init__(self, level_name, renderer=None, musicman=None, soundman=None):
        self.camera_pos, self.map_size, self.tutorial, self.state = \
                level.directory[level_name][1].load()
        
        self.renderer = renderer
        self.musicman = musicman
        self.soundman = soundman
        self.keymap = self.load_keymap()

        if self.tutorial: self.tutorial = 1

        self.setup_pygame()
        self.font_name = data.filepath("font/Tuffy_Bold.ttf")
        self.old_text_overlay_lines = []
        self.state.reset_sound_flags()
        
        pos, zoom = self.camera_pos
        if pos is not None: self.renderer.camera.setPosition(pos)
        else: self.renderer.camera.setPosition(self.state.spring.pos)
        if zoom is not None: self.renderer.camera.setZoom(zoom)
        else: self.renderer.camera.setZoom(10)

        self.renderer.set_map_size(self.map_size)
        self.update_ticks = 25
        self.frame_ticks = 25

        self.is_valid = True

        self.p_cursor = (0, 0)
        self.c_cursor = (0, 0)

        self.numelves = None
        self.tutorial_action_map = [
            ((193, 307), (0, 114), self.next_tutorial, (), 'Next page of tutorial'),
            ((0, 110), (0, 114), self.prev_tutorial, (), 'Previous page of tutorial'),
            ((395, 512), (0, 114), self.close_tutorial, (), 'Close tutorial'),
        ]
            
        self.menu_action_map = [
            (( 32,  72), ( 90, 130), self.state.dec_desired_winding_elves, (), 'Release elves from winding the spring. [Q]'),
            ((160, 200), ( 90, 130), self.state.inc_desired_winding_elves, (), 'Send more elves to wind the spring. [W]'),
            (( 10, 112), (170, 272), self.set_mode, ('remove cog task',), 'Send elves to remove a cog. [D]'),
            ((119, 221), (169, 271), self.set_mode, ('unhook task',), 'Send elves to unhook a belt. [U]'),
            (( 10, 112), (279, 381), self.set_mode, ('platform task',), 'Send elves to build platforms (50M). [P]'),
            ((119, 221), (279, 381), self.set_mode, ('ladder task',), 'Send elves to build ladders (100M). [L]'),
            ((229, 321), (279, 381), self.set_mode, ('belt task',), 'Send elves to belt two components together. [B]'),
            (( 10, 112), (390, 492), self.set_mode, ('cog task', 1), 'Send elves to place a number I cog (50M). [1]'),
            ((119, 221), (389, 491), self.set_mode, ('cog task', 3), 'Send elves to place a number II cog (100M). [2]'),
            ((229, 321), (390, 492), self.set_mode, ('cog task', 5), 'Send elves to place a number III cog (150M). [3]'),
            ((339, 441), (391, 493), self.set_mode, ('cog task', 7), 'Send elves to place a number IV cog (200M). [4]'),
        ]

        self.mode = None
        self.mode_param = None
        self.renderer.update_tutorial()
    def load_keymap(self):
        return {
            K_ESCAPE: (self.close_game, ()),
            K_1: (self.set_mode, ('cog task', 1)),
            K_2: (self.set_mode, ('cog task', 3)),
            K_3: (self.set_mode, ('cog task', 5)),
            K_4: (self.set_mode, ('cog task', 7)),
            K_l: (self.set_mode, ('ladder task',)),
            K_p: (self.set_mode, ('platform task',)),
            K_b: (self.set_mode, ('belt task',)),
            K_d: (self.set_mode, ('remove cog task',)),
            K_u: (self.set_mode, ('unhook task',)),
            K_q: (self.state.dec_desired_winding_elves, ()),
            K_w: (self.state.inc_desired_winding_elves, ()),
            K_LEFTBRACKET: (self.musicman.change_vol, (-0.1,)),
            K_RIGHTBRACKET: (self.musicman.change_vol, (0.1,)),
            K_EQUALS: (self.renderer.zoom_in, ()),
            K_MINUS: (self.renderer.zoom_out, ()),

            # testing functions
            #K_g: (self.set_mode, ('go task',)),
            #K_r: (self.report_cell, ()),
            #K_i: (self.print_inv, ()),
            #K_x: (self.dump_elf_info, ()),
            #K_c: (self.cheat, ()),
            #K_a: (self.renderer.report, ()),
            #K_z: (self.report_fps, ()),
            #K_e: (self.create_elf, ()),
        }

    def setup_pygame(self):
        #pygame.init()
        #self.renderer.setup_pygame()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.get_surface()
        self.scr_w, self.scr_h = self.screen.get_size()
        self.menu_map = pygame.image.load(data.filepath("image/menufinal-map.png"))
        self.tutorial_map = pygame.image.load(data.filepath("image/tutorial-map.png"))

    def update_cursor(self):
        self.p_cursor = pygame.mouse.get_pos()
        self.c_cursor = self.renderer.update_cursor(self.p_cursor)
        self.is_valid = self.context_action(lmb=True, ispossible=True)
        self.update_text_overlay()
    
    def handle_events(self):
        for evt in pygame.event.get():
            if evt.type == QUIT:
                self.abort = True
            elif evt.type == MOUSEBUTTONDOWN:
                if evt.button == 1:
                    self.context_action(lmb=True)
                elif evt.button == 2 or evt.button == 3:
                    self.context_action(rmb=True)
                elif evt.button == 4:
                    self.renderer.zoom_in()
                elif evt.button == 5:
                    self.renderer.zoom_out()
            elif evt.type == MOUSEBUTTONUP:
                if evt.button == 1:
                    self.context_action(lmb=True, release=True)
                elif evt.button == 2 or evt.button == 3:
                    self.context_action(rmb=True, release=True)
            elif evt.type == KEYDOWN:
                if evt.key in self.keymap:
                    func, args = self.keymap[evt.key]
                    func(*args)
            elif evt.type == SOUND_EVENT:
                self.soundman.handle_sound_event(evt)
    
    def update_sounds(self):
        if self.state.elf_emerged:
            sound.post_sound(ELF_GREETING)
        if self.state.task_added:
            sound.post_sound(ELF_ACK)
        if self.state.elves_needed:
            sound.post_sound(SCOTT_ELVES_NEEDED)
        if self.state.metal_low:
            sound.post_sound(SCOTT_METAL_NEEDED)
        if self.state.rubber_low:
            sound.post_sound(SCOTT_RUBBER_NEEDED)
        self.state.reset_sound_flags()

    def blank_text(self):
        surf = self.renderer.gametext_overlay.surf
        surf.fill((0, 0, 0, 0))
        return surf

    def textbreak(self, line, limit):
        result = []
        frags = (len(line) // limit) + 1
        fragsize = len(line) // frags
        while len(line) > fragsize:
            breakat = fragsize
            while line[breakat] != ' ' and breakat < len(line):
                breakat -= 1
            result.append(line[:breakat])
            line = line[breakat+1:]
        result.append(line)
        return result

    def update_text_overlay(self):
        resources = "Metal: %d Rubber: %d" % (self.state.metal, self.state.rubber)
        ma = self.get_menu_action()
        if ma is not None:
            lines = [ma[2]]
        else:
            lines = []
            for line in self.state.get_text(self.c_cursor):
                lines.extend(self.textbreak(line, OVERLAY_LINE_LENGTH))
        if self.mode == 'belt task':
            cost = self.add_belt_task(True, calculate=True)
            if cost is not None:
                lines = ["Belt cost: %dR" % cost] + lines
        newlines = lines + [resources]
        if newlines != self.old_text_overlay_lines:
            self.old_text_overlay_lines = newlines
            newlines.reverse()
            surf = self.blank_text()
            s_width, s_height = surf.get_size()
            font = pygame.font.Font(self.font_name, 14)

            baseline = 5
            for line in newlines:
                if line:
                    text = font.render(line, True, GAME_TEXT_COLOUR)
                    t_width, t_height = text.get_size()
                    surf.blit(text, (s_width - t_width - 5, s_height - t_height - baseline))
                    baseline += t_height

            self.renderer.gametext_overlay.updateTexture()

    def update_interface_overlay(self):
        new_numelves = self.state.desired_winding_elves
        if new_numelves <= 12: new_numelves = "0123456789X?+"[new_numelves]
        else: new_numelves = "!"

        if new_numelves == self.numelves: return
        self.numelves = new_numelves

        font = pygame.font.Font(self.font_name, 36)
        text = font.render(str(new_numelves), True, GAME_TEXT_COLOUR)
        t_width, t_height = text.get_size()
        t_pos = (92 + (46 - t_width)/2, 74 + (78 - t_height)/2)

        overlay = self.renderer.interface_overlay
        overlay.surf.fill((0, 0, 0, 0))
        overlay.surf.blit(pygame.image.load(data.filepath("image/menufinal.png")), (0, 0))
        overlay.surf.blit(text, t_pos)
        overlay.updateTexture()

    def scroll_map(self):
        pcx, pcy = self.p_cursor
        
        if pcy > self.scr_h - 256:
            if pcx < 2:
                self.renderer.scroll_left()
        elif pcx < SCROLL_MARGIN_SIZE:
            self.renderer.scroll_left()
        elif pcx > self.scr_w - SCROLL_MARGIN_SIZE:
            self.renderer.scroll_right()
        
        if pcy < SCROLL_MARGIN_SIZE:
            self.renderer.scroll_up()
        elif pcx < 256:
            if pcy > self.scr_h - 2:
                self.renderer.scroll_down()
        elif pcy > self.scr_h - SCROLL_MARGIN_SIZE:
            self.renderer.scroll_down()

    def main_loop(self):
        while not self.abort:
            cur_ticks = pygame.time.get_ticks()
            frame_step = cur_ticks - self.last_frame
            update_step = cur_ticks - self.last_update
            
            if frame_step > self.frame_ticks and update_step < self.update_ticks:
                self.update_cursor()
                #self.renderer.update_tutorial()
                self.renderer.draw()
                self.clock.tick()
                self.last_frame = cur_ticks

            self.handle_events()
            
            for i in xrange(update_step // self.update_ticks):
                self.state.tick()
                self.scroll_map()
                self.musicman.update()
                self.update_interface_overlay()
                self.last_update = cur_ticks

            self.update_sounds()
            
            if self.state.won:
                if cur_ticks >= self.next_cheer:
                    self.soundman.play(random.choice(ELF_CHEER))
                    self.next_cheer = cur_ticks + random.randint(400, 600)
                if self.state.ticks - self.state.win_time > POST_VICTORY_PAUSE:
                    self.abort = True

    def run(self):
        cur_ticks = pygame.time.get_ticks()
        self.last_update = cur_ticks
        self.last_frame = cur_ticks
        self.next_cheer = 0
        self.abort = False
        self.main_loop()
        self.renderer.device_bag.objs[self.state.spring].light.destroy() #Horrible horrible horrible
        if gl.GLState.particles:
            self.renderer.pmanager.particles = [] #Horrible horrible horrible
        return self.state.win_time
     
    # functions below are for the interface
    def get_menu_action(self):
        px, py = self.p_cursor
        if px >= 256 or py <= self.scr_h - 256:
            return None
        px, py = px * 2, 512 - (self.scr_h - py) * 2

        pxl = self.menu_map.get_at((px, py))
        if sum(pxl[:3]) > 0:
            return None

        for xr, yr, func, args, tooltip in self.menu_action_map:
            if xr[0] <= px <= xr[1] and yr[0] <= py <= yr[1]:
                return func, args, tooltip

    def get_tutorial_action(self):
        px, py = map(lambda x: x * 512.0 / (self.scr_h / 2), self.p_cursor)
        if px >= 512 or py >= 512:
            return None
        pxl = self.tutorial_map.get_at((int(px), int(py)))
        if sum(pxl[:3]) > 0:
            return None

        for xr, yr, func, args, tooltip in self.tutorial_action_map:
            if xr[0] <= px <= xr[1] and yr[0] <= py <= yr[1]:
                return func, args, tooltip


    def menu_action(self):
        action = self.get_menu_action()
        if action is None:
            action = self.get_tutorial_action()
        if action is None:
            return False
        else:
            func, args, tooltip = action
        sound.post_sound("sfx/Interface-Click.ogg")
        func(*args)
        return True
    
    def context_action(self, lmb=False, rmb=False, release=False, ispossible=False):
        if lmb and not release and not ispossible and self.menu_action():
            return
        elif self.mode == 'cog task':
            if lmb and not release:
                return self.add_cog_task(self.mode_param, ispossible)
            elif rmb and not release:
                self.set_mode(None)
        elif self.mode == 'platform task':
            if rmb and not release and self.mode_param is None:
                self.set_mode(None)
            elif lmb and (not release or self.mode_param is not None):
                return self.add_platform_task(ispossible)
            elif rmb and not release:
                self.mode_param = None
        elif self.mode == 'ladder task':
            if rmb and not release and self.mode_param is None:
                self.set_mode(None)
            elif lmb and (not release or self.mode_param is not None):
                return self.add_ladder_task(ispossible)
            elif rmb and not release:
                self.mode_param = None
        elif self.mode == 'belt task':
            if rmb and not release and self.mode_param is None:
                self.set_mode(None)
            elif lmb and (not release or self.mode_param is not None):
                return self.add_belt_task(ispossible)
            elif rmb and not release:
                self.mode_param = None
        elif self.mode == 'remove cog task':
            if lmb and not release:
                return self.add_remove_cog_task(ispossible)
            elif rmb and not release:
                self.set_mode(None)
        elif self.mode == 'unhook task':
            if lmb and not release:
                return self.add_unhook_task(ispossible)
            elif rmb and not release:
                self.set_mode(None)
        elif self.mode is None:
            if rmb and not release:
                self.remove_task()
    
    def remove_task(self):
        def overlaps(pos, region):
            x, y = pos
            for xo, yo in region:
                if self.c_cursor == (x + xo, y + yo):
                    return True
            return False

        for task in self.state.tasks:
            if isinstance(task, model.task.BuildTask):
                if task.pos == self.c_cursor:
                    task.abort(self.state)
            if isinstance(task, model.task.CreateCogTask):
                if overlaps(task.pos, model.part.Cog.get_region(task.diam)):
                    task.abort(self.state)
            if isinstance(task, model.task.ConnectTask):
                if overlaps(task.part1.pos, task.part1.region) or \
                        overlaps(task.part2.pos, task.part2.region):
                    task.abort(self.state)
            if isinstance(task, model.task.RemoveCogTask):
                if overlaps(task.cog.pos, task.cog.region):
                    task.abort(self.state)
            if isinstance(task, model.task.DisconnectTask):
                if overlaps(task.belt.part1.pos, task.belt.part1.region) or \
                        overlaps(task.belt.part2.pos, task.belt.part2.region):
                    task.abort(self.state)

    def add_cog_task(self, diam, ispossible):
        possible = model.task.CreateCogTask.is_valid(self.state, self.c_cursor, diam)
        if ispossible:
            return possible
        if not possible:
            return
        new_task = model.task.CreateCogTask(self.state, self.c_cursor, diam)
        self.state.add_task(new_task)

    def add_platform_task(self, ispossible):
        if ispossible:
            return True
        if self.mode_param is None:
            self.mode_param = self.c_cursor
        else:
            y_pos = self.mode_param[1]
            x_pos1 = self.mode_param[0]
            x_pos2 = self.c_cursor[0]
            if x_pos1 > x_pos2:
                x_pos1, x_pos2 = x_pos2, x_pos1
            for x_pos in xrange(x_pos1, x_pos2+1):
                new_task = model.task.BuildPlatformTask(self.state, (x_pos, y_pos))
                self.state.add_task(new_task)
                self.mode_param = None

    def add_ladder_task(self, ispossible):
        if ispossible:
            return True
        if self.mode_param is None:
            self.mode_param = self.c_cursor
        else:
            x_pos = self.mode_param[0]
            y_pos1 = self.mode_param[1]
            y_pos2 = self.c_cursor[1]
            if y_pos1 > y_pos2:
                y_pos1, y_pos2 = y_pos2, y_pos1
            for y_pos in xrange(y_pos1, y_pos2+1):
                new_task = model.task.BuildLadderTask(self.state, (x_pos, y_pos))
                self.state.add_task(new_task)
                self.mode_param = None

    def add_belt_task(self, ispossible, calculate=False):
        selected_part = self.state.mgrid[self.c_cursor]
        if isinstance(selected_part, model.part.Part):
            if not self.mode_param:
                if calculate:
                    return None
                if ispossible:
                    return True
                self.mode_param = selected_part
            else:
                possible =  model.task.ConnectTask.is_valid(self.state, selected_part, self.mode_param)
                if calculate:
                    if not possible:
                        return None
                    return self.state.belt_cost(selected_part, self.mode_param)
                if ispossible:
                    return possible
                if not possible:
                    return
                new_task = model.task.ConnectTask(self.state, selected_part,
                        self.mode_param)
                self.state.add_task(new_task)
                self.mode_param = None
        else:
            if not ispossible:
                self.mode_param = None
            if calculate:
                return None
            return False 

    def add_go_task(self, ispossible):
        if ispossible:
            return True
        new_task = model.task.GoTask(self.state, self.c_cursor)
        self.state.add_task(new_task)

    def add_remove_cog_task(self, ispossible):
        part = self.state.mgrid[self.c_cursor]
        if isinstance(part, model.part.Cog):
            possible = model.task.RemoveCogTask.is_valid(self.state, part)
            if ispossible:
                return possible
            if not possible:
                return
            new_task = model.task.RemoveCogTask(self.state, part)
            self.state.add_task(new_task)

    def add_unhook_task(self, ispossible):
        if ispossible:
            return True
        cog = self.state.mgrid[self.c_cursor]
        belts = [b for b in self.state.belts if b.part1 == cog or b.part2 == cog]
        for b in belts:
            new_task = model.task.DisconnectTask(self.state, b)
            self.state.add_task(new_task)
   
    def next_tutorial(self):
        self.tutorial += 1
        if self.tutorial > len(tutorial.text):
            self.tutorial = len(tutorial.text)
        self.renderer.update_tutorial()

    def prev_tutorial(self):
        self.tutorial -= 1
        if self.tutorial < 1:
            self.tutorial = 1
        self.renderer.update_tutorial()
    
    def close_tutorial(self):
        self.tutorial = False
        self.renderer.update_tutorial()

    # functions below are loaded into the keymap
    def close_game(self):
        self.abort = True

    def create_elf(self):
        self.state.add_elf(self.c_cursor)
    
    def set_mode(self, mode, param=None):
        self.mode = mode
        self.mode_param = param

    def report_cell(self):
        p_item = self.state.pgrid[self.c_cursor]
        m_item = self.state.mgrid[self.c_cursor]
        print "Cell: (%i, %i)" % self.c_cursor
        print "  platform = %s" % str(p_item[0])
        print "  ladder = %s" % str(p_item[1])
        if m_item is not None:
            print "  part = %r" % m_item.__class__.__name__
            if isinstance(m_item, model.part.Part):
                print "  angle = %f" % m_item.angle
                print "  gear_ratio = %f" % m_item.g_ratio
                print "  angular_speed = %f" % \
                        m_item.get_angular_speed(self.state)
            if isinstance(m_item, model.part.Spring) or \
                    isinstance(m_item, model.device.Device):
                print "  energy = %f" % m_item.energy
        print "global_load_factor = %f" % self.state.load_factor

    def print_inv(self):
        print "Metal: %d\tRubber: %d" % (self.state.metal, self.state.rubber)

    def dump_elf_info(self):
        print "elf tasklist: --"
        for elf in self.state.elves:
            print elf.task

    def cheat(self):
        self.state.metal += 10000
        self.state.rubber += 10000
        self.state.spring.energy += 10000

    def report_fps(self):
        print "FPS:", self.clock.get_fps()
