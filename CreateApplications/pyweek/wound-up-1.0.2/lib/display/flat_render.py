'''flat_render.py - simplistic 2d renderer, simple and good for test work'''

import math

import pygame
from pygame.locals import *
from pygame.constants import *

import renderer
import model


cell_size = 16
map_w, map_h = 50, 25

c_belt                  = (255, 255,   0)
c_cursor                = (255, 255, 255)
c_elf_body              = (255, 255,   0)
c_elf_head              = (255, 200, 200)
c_ladder                = ( 50, 200,  50)
c_cog_neutral           = (150,  50,  50)
c_cog_positive          = (150,   0, 100)
c_cog_negative          = (150, 100,   0)
c_path                  = (  0,   0, 255)
c_platform              = (200,  50,  50)
c_spring                = ( 20,  40, 100)
c_device                = (100,  80,  20)
c_task                  = (100, 100, 100)

pfromc = lambda (cx, cy): (cx * cell_size, (map_h - cy - 1) * cell_size)
mpfromc = lambda (cx, cy): (cx * cell_size + cell_size / 2,
    (map_h - cy - 1) * cell_size + cell_size / 2)
cfromp = lambda (px, py): (px / cell_size, map_h - (py / cell_size) - 1)

class FlatRenderer(renderer.Renderer):
    
    def __init__(self, state, interface):
        global map_w, map_h
        self.state = state
        self.interface = interface
        map_w, map_h = self.interface.map_size

    def setup_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((map_w * cell_size,
            map_h * cell_size), HWSURFACE)
        pygame.display.set_caption(DISPLAY_CAPTION_FLAT)
    
    def update_cursor(self, pos):
        self.cursor = cfromp(pos)
        return self.cursor

    def get_elf_pixelpos(self, elf):
        px, py = pfromc(elf.path[0])
        if elf.is_falling:
            py += cell_size * elf.offset
        else:
            try:
                pxnext, pynext = pfromc(elf.path[1])
                px += (pxnext - px) * elf.offset
                py += (pynext - py) * elf.offset
            except:
                pass
        return px, py

    def draw_spring(self):
        spring = self.state.spring
        corner = (spring.pos[0]-1, spring.pos[1]+1)
        pygame.draw.rect(self.screen, c_spring, pygame.Rect(
            pfromc(corner), (3 * cell_size, 3 * cell_size)), 0)

    def draw_device(self, device):
        cx, cy = device.pos
        for xo, yo in device.region:
            px, py = pfromc((cx + xo, cy + yo))
            pygame.draw.rect(self.screen, c_device, \
                    Rect(px, py, cell_size, cell_size))
        cog = model.part.Cog(device.pos, 1.5)
        cog.angle = device.angle
        self.draw_cog(cog)

    def draw_ladder(self, pos, colour=c_ladder):
        px, py = pfromc(pos)
        for i in [6, 9]:
            pygame.draw.line(self.screen, colour, (px+i, py), (px+i, py+15))
        for i in [2, 6, 10, 14]:
            pygame.draw.line(self.screen, colour, (px+6, py+i), (px+9, py+i))

    def draw_platform(self, pos, colour=c_platform):
        px, py = pfromc(pos)
        pygame.draw.rect(self.screen, colour, Rect(px, py, cell_size,
            cell_size / 4))

    def draw_belt(self, pos1, pos2):
        px1, py1 = mpfromc(pos1)
        px2, py2 = mpfromc(pos2)
        pygame.draw.line(self.screen, c_belt, (px1, py1), (px2, py2))
    
    def draw_cog(self, cog):
        px, py = mpfromc(cog.pos)
        prad = cog.diam * cell_size / 2
        px2 = px + prad * math.cos(cog.angle*math.pi/180)
        py2 = py + prad * math.sin(cog.angle*math.pi/180)

        colour = c_cog_neutral
        if cog.g_ratio > 0:
            colour = c_cog_positive
        if cog.g_ratio < 0:
            colour = c_cog_negative

        pygame.draw.circle(self.screen, colour, (px, py), prad, 3)
        pygame.draw.line(self.screen, colour, (px, py), (px2, py2), 2)

    def draw_elf(self, elf):
        px, py = self.get_elf_pixelpos(elf)
        if elf.is_falling:
            pygame.draw.circle(self.screen, c_elf_body, (px+8, py+8), 4)
            pygame.draw.circle(self.screen, c_elf_head, (px+8, py+14), 2)
        else:
            pygame.draw.circle(self.screen, c_elf_body, (px+8, py+12), 4)
            pygame.draw.circle(self.screen, c_elf_head, (px+8, py+6), 2)

    def draw_task(self, task):
        if isinstance(task, model.task.GoTask):
            px, py = pfromc(task.pos)
            pygame.draw.lines(self.screen, c_task, True, [(px+2, py+2),
                (px+12, py+2), (px+7, py+12)])
        
        elif isinstance(task, model.task.CreateCogTask):
            px, py = mpfromc(task.pos)
            prad = task.diam * cell_size / 2 - 3
            pygame.draw.circle(self.screen, c_task, (px, py), prad, 1)

        elif isinstance(task, model.task.ConnectTask):
            px1, py1 = mpfromc(task.part1.pos)
            px2, py2 = mpfromc(task.part2.pos)
            pygame.draw.line(self.screen, c_task, (px1, py1), (px2, py2))

        elif isinstance(task, model.task.BuildPlatformTask):
            self.draw_platform(task.pos, colour=c_task)
        
        elif isinstance(task, model.task.BuildLadderTask):
            self.draw_ladder(task.pos, colour=c_task)

    def draw_cursor(self):
        if self.interface.placing_belt is not None:
            px1, py1 = mpfromc(self.interface.placing_belt.pos)
            px2, py2 = mpfromc(self.cursor)
            pygame.draw.line(self.screen, c_cursor, (px1, py1), (px2, py2))
            
        elif self.interface.placing_platform is not None:
            cx1, cy = self.interface.placing_platform
            cx2 = self.cursor[0]
            if cx1 > cx2:
                cx1, cx2 = cx2, cx1
            for cx in xrange(cx1, cx2+1):
                self.draw_platform((cx, cy), colour=c_cursor)

        elif self.interface.placing_ladder is not None:
            cx, cy1 = self.interface.placing_ladder
            cy2 = self.cursor[1]
            if cy1 > cy2:
                cy1, cy2 = cy2, cy1
            for cy in xrange(cy1, cy2+1):
                self.draw_ladder((cx, cy), colour=c_cursor)
        else:
            pygame.draw.rect(self.screen, c_cursor, Rect(pfromc(self.cursor),
            (cell_size, cell_size)), 1)

    def draw(self):
        self.screen.lock()
        self.screen.fill((0, 0, 0))

        self.draw_spring()

        for cog in self.state.cogs:
            self.draw_cog(cog)

        for device in self.state.devices:
            self.draw_device(device)
        
        for belt in self.state.belts:
            self.draw_belt(belt.part1.pos, belt.part2.pos)

        for pos, cell in self.state.pgrid:
            platform, ladder = cell
            if platform: self.draw_platform(pos)
            if ladder: self.draw_ladder(pos)

        for elf in self.state.elves:
            self.draw_elf(elf)

        for task in self.state.tasks:
            self.draw_task(task)

        for task in self.state.tasks:
            if isinstance(task, model.task.ConnectTask) and task.phase == 2:
                px1, py1 = tuple(map(lambda x: x + cell_size / 2,
                    self.get_elf_pixelpos(task.elf1)))
                px2, py2 = tuple(map(lambda x: x + cell_size / 2,
                    self.get_elf_pixelpos(task.elf2)))
                pygame.draw.line(self.screen, c_belt, (px1, py1), (px2, py2))
        
        self.draw_cursor()
        self.screen.unlock()
        pygame.display.flip()
