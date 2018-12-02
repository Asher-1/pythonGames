'''gl_render.py - pretty 3d renderer'''

import pygame
from pygame.locals import *
from pygame.constants import *

import renderer
import model
import objbags
import globjects
import gl
import data

from constants import *
import tutorial

class GLRenderer(renderer.Renderer):

    def __init__(self, state, interface, options):
        self.state = state
        self.interface = interface
        self.options = options
        self.menu_mode = True

    def setup_pygame(self):
        pygame.init()
        
        if self.options["res"] is None: self.screen_mode = pygame.display.list_modes()[0]
        else: self.screen_mode = self.options["res"]

        display_flags = OPENGL | DOUBLEBUF
        if not self.options["win"]: display_flags |= FULLSCREEN
        self.screen = pygame.display.set_mode(self.screen_mode, display_flags)
        pygame.display.set_icon(pygame.image.load(data.filepath("image/icon64.png")))
        
        pygame.display.set_caption(DISPLAY_CAPTION)
        if not gl.GLState.inited: 
            gl.init(*self.screen_mode, **self.options["gl"])
        self.setup_gl()

    def setup_gl(self):
        self.camera = gl.Camera((5, 5), 10)
        self.camera.setCurrent()
        
        self.cog_bag = objbags.CogBag()
        self.plat_bag = objbags.PlatBag()
        self.ladder_bag = objbags.LadderBag()
        self.elf_bag = objbags.ElfBag()
        self.belt_bag = objbags.BeltBag()
        self.device_bag = objbags.DeviceBag()
        self.task_bag = objbags.TaskBag(self.elf_bag)

        self.boundary = globjects.Boundary(self.state.pgrid.w, self.state.pgrid.h)
        self.lights = []
        self.lights.append(gl.Light((10, 10, 5)))
        self.pmanager = gl.ParticleManager()
        
        self.interface_overlay = gl.Overlay(512, (0,0), 256)
        self.interface_overlay.surf.blit(pygame.image.load(data.filepath("image/menufinal.png")), (0, 0))
        self.interface_overlay.updateTexture()

        self.tutorial_overlay = gl.Overlay(512, (0, self.screen_mode[1] / 2), self.screen_mode[1] / 2)

        # please, please, please don't fiddle with the title graphic, title level or this code!
        def position_title():
            x, y = self.screen_mode
            cph, t, p, q = 28.0, 0.198, 0.374, 0.641
            cs = y / cph
            x2, y2 = x/2.0 - 2*cs, y/2.0 - 3*cs
            r = 7.0 * cs / 2.0
            w = r / t
            tp = (x2 - p * w, y2 - q * w)
            return tp, w

        pos, width = position_title()
        self.title_overlay = gl.Overlay(512, pos, width)
        self.title_overlay.surf.blit(pygame.image.load(data.filepath("image/title.png")), (0, 0))
        self.title_overlay.updateTexture()
        
        self.menutext_overlay = gl.Overlay(512, (0, 0), self.screen_mode[1])
        self.gametext_overlay = gl.Overlay(512, (self.screen_mode[0]-512, 0))
        
        size = min(min(self.screen_mode), max(self.screen_mode) / 2)
        x_pos = (self.screen_mode[0] - size) / 2
        y_pos = (self.screen_mode[1] - size) / 2
        self.victory_overlay = gl.Overlay(512, (x_pos, y_pos), size)
        self.victory_overlay.surf.blit(pygame.image.load(data.filepath("image/victory.png")), (0, 0))
        self.victory_overlay.updateTexture()

        self.cursor = globjects.Cursor(self.state)

    def update_cursor(self, pos):
        px, py = self.camera.getIntPos(pos)
        if px < 0: px = 0
        if px >= self.state.pgrid.w: px = self.state.pgrid.w - 1
        if py < 0: py = 0
        if py >= self.state.pgrid.h: py = self.state.pgrid.h - 1
        self.cursor.setPosition((px, py))
        self.cursor.setMode(self.interface.mode, self.interface.mode_param, self.interface.is_valid)
        self.cursor.state = self.state
        return (px, py)
   
    def update_tutorial(self):
        overlay = self.tutorial_overlay.surf
        overlay.fill((0, 0, 0, 0))

        if self.interface.tutorial:
            overlay.blit(pygame.image.load(data.filepath("image/tutorialnav.png")), (0, 0))
            font = pygame.font.Font(self.interface.font_name, 24)
            text_lines = self.interface.textbreak(tutorial.text[self.interface.tutorial - 1], 45)
            x_pos, y_pos = 20, 128
            
            for line in text_lines:
                text = font.render(line, True, GAME_TEXT_COLOUR)
                t_width, t_height = text.get_size()
                overlay.blit(text, (x_pos, y_pos))
                y_pos += t_height
            
            string = tutorial.labels[self.interface.tutorial]
            text = font.render(string, True, GAME_TEXT_COLOUR)
            t_width, t_height = text.get_size()
            x, y, w, h = 128, 18, 45, 76
            overlay.blit(text, (x + (w - t_width) / 2, y + (h - t_height) / 2))
        
        self.tutorial_overlay.updateTexture()

    def draw(self):
        self.camera.setCurrent()
        if self.state.won:
            for device in self.device_bag.objs:
                self.pmanager.addSystem(gl.ParticleSystem(device.pos + (.1,), globjects.Firework, 10, 0))
        for task in self.state.deadtasks:
            if not task.successful:
                continue
            if isinstance(task, model.task.CreateCogTask):
                self.pmanager.addSystem(gl.ParticleSystem(task.pos + (1,),
                    globjects.SmokePuff, 5 * task.diam ** 2, task.diam * .25))
            elif isinstance(task, model.task.RemoveCogTask):
                self.pmanager.addSystem(gl.ParticleSystem(task.cog.pos + (1,),
                    globjects.SmokePuff, 5 * task.cog.diam ** 2, task.cog.diam * .25))
            elif isinstance(task, model.task.BuildPlatformTask):
                self.pmanager.addSystem(gl.ParticleSystem(
                    (task.pos[0], task.pos[1] + .4, 1.2),
                    globjects.SmokePuff, 5, .25))
            elif isinstance(task, model.task.BuildLadderTask):
                self.pmanager.addSystem(gl.ParticleSystem(
                    (task.pos[0], task.pos[1], 1.2),
                    globjects.SmokePuff, 10, .25))
        self.state.deadtasks.clear()
        
        for belt in self.state.deadbelts:
            self.pmanager.addSystem(globjects.SnappedBelt(belt.part1.pos + (.1,), belt.part2.pos + (.1,)))
        self.state.deadbelts.clear()
        
        self.pmanager.tick()
        self.cog_bag.update(self.state.cogs)
        if self.state.pgrid.dirty:
            self.plat_bag.update(self.state.pgrid.platform_dict())
            self.ladder_bag.update([x for x, y in self.state.pgrid if y[1]])
        self.elf_bag.update(self.state.elves)
        self.belt_bag.update(self.state.belts)
        self.device_bag.update(self.state.devices | set([self.state.spring]))
        self.task_bag.update(self.state.tasks)

        gl.clear()
        for bag in [self.elf_bag, self.cog_bag, self.belt_bag,
                self.plat_bag, self.ladder_bag, self.device_bag,
                self.task_bag]:
            bag.render()
        self.boundary.render()
        self.cursor.render()
        self.pmanager.render()
        
        if not self.menu_mode:
            self.interface_overlay.render()
            self.gametext_overlay.render()
            if self.interface.tutorial:
                self.tutorial_overlay.render()
            if self.state.won:
                self.victory_overlay.render()
        else:
            self.title_overlay.render()
            self.menutext_overlay.render()

        self.state.pgrid.mark_clean()
        
        pygame.display.flip()

    def scroll_left(self):
        self.camera.move((-SCROLL_RATE, 0.0))

    def scroll_right(self):
        self.camera.move((SCROLL_RATE, 0.0))

    def scroll_up(self):
        self.camera.move((0.0, SCROLL_RATE))

    def scroll_down(self):
        self.camera.move((0.0, -SCROLL_RATE))

    def zoom_in(self):
        self.camera.zoom(-1)

    def zoom_out(self):
        self.camera.zoom(1)
    def set_map_size(self, map_size):
        self.camera.topright = map_size
        self.boundary.setSize(map_size)
    def report(self):
        for bag in [self.elf_bag, self.cog_bag, self.belt_bag, self.plat_bag, self.ladder_bag, self.device_bag]:
            print bag.__class__.__name__, bag.numPolys()
