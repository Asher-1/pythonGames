#!/usr/bin/python

"""
common.py - commonly used scene classes
"""

import os
import pygame
from pygame.locals import *
from gamedirector import *

class Camera(object):
    def __init__(self,screen_size,stickyness=0.33):
        self.x = -1
        self.y = -1
        self.w_view = screen_size[0]
        self.h_view = screen_size[1]
        self.stickyness = stickyness
    def UpdateCamera(self,focus):
        if (focus[0] - self.x) > self.stickyness*self.w_view/2:
            self.x = focus[0] - self.stickyness*self.w_view/2
        elif (focus[0] - self.x) < -self.stickyness*self.w_view/2:
            self.x = focus[0] + self.stickyness*self.w_view/2
        if (focus[1] - self.y) > self.stickyness*self.h_view/2:
            self.y = focus[1] - self.stickyness*self.h_view/2
        elif (focus[1] - self.y) < -self.stickyness*self.h_view/2:
            self.y = focus[1] + self.stickyness*self.h_view/2
        if self.x < self.w_view/2:
            self.x = self.w_view/2
        elif self.x > (self.xlim-self.w_view/2):
            self.x = self.xlim-self.w_view/2
        if self.y < self.h_view/2:
            self.y = self.h_view/2
        elif self.y > (self.ylim-self.h_view/2):
            self.y = self.ylim-self.h_view/2

class FadeInOut(object):
    def __init__(self,ticks,smooth=False):
        self.ticks = ticks
        self.ticks_elapsed = 0
        self.direction = 'none'
        self.alpha = 255
        self.finished_in = False
        self.finished_out = False
        self.musicfade = False
        self.smooth = smooth
        self.running = False
    
    def Update(self):
        if not self.running:
            return
        if self.direction == 'in' and not self.finished_in:
            self.ticks_elapsed += 1
            if self.ticks_elapsed > self.ticks:
                self.finished_in = True
            else:
                if self.smooth:
                    self.alpha = 255*(1.0-(self.ticks_elapsed/float(self.ticks)))
                else:
                    self.alpha = 255*(1.0-((5*(self.ticks_elapsed/5))/float(self.ticks)))
        elif self.direction == 'out' and not self.finished_out:
            self.ticks_elapsed += 1
            if self.ticks_elapsed > self.ticks:
                self.finished_out = True
            else:
                if self.smooth:
                    self.alpha = 255*(self.ticks_elapsed/float(self.ticks))
                else:
                    self.alpha = 255*((5*(self.ticks_elapsed/5))/float(self.ticks))
                if self.musicfade:
                    pygame.mixer.music.set_volume(0.5*(1.0 - (self.ticks_elapsed/float(self.ticks))))
    
    def FadeIn(self):
        self.direction = 'in'
        self.ticks_elapsed = 0
        self.finished_in = False
        self.finished_out = False
        self.running = True
        self.alpha = 255
    
    def FadeOut(self,musicfade=False):
        self.direction = 'out'
        self.ticks_elapsed = 0
        self.finished_out = False
        self.finished_in = False
        self.musicfade = musicfade
        self.running = True
    
    def Reset(self):
        self.ticks_elapsed = 0
        self.direction = 'none'
        self.alpha = 255
        self.finished_in = False
        self.finished_out = False
        self.musicfade = False
        self.running = False

class MenuButton(object):
    def __init__(self,pos,surf_on,surf_off,go_func=None):
        self.pos = pos
        self.on = False
        self.surf_on = surf_on
        self.surf_off = surf_off
        self.go_func = go_func
    
    def Draw(self, screen):
        if self.on:
            screen.blit(self.surf_on, self.pos)
        else:
            screen.blit(self.surf_off, self.pos)

class MenuList(object):
    def __init__(self,buttons,select_ind,controlmap):
        self.buttons = buttons
        self.select_ind = select_ind
        self.buttons[self.select_ind].on = True
        self.CM = controlmap
    
    def ProcessKeyEvent(self,event):
        if event.type == KEYDOWN:
            if event.key == self.CM["U"]:
                self.buttons[self.select_ind].on = False
                self.select_ind = (self.select_ind-1) % len(self.buttons)
                self.buttons[self.select_ind].on = True
            elif event.key == self.CM["D"]:
                self.buttons[self.select_ind].on = False
                self.select_ind = (self.select_ind+1) % len(self.buttons)
                self.buttons[self.select_ind].on = True
            if event.key == self.CM["Fire"] or event.key == K_RETURN:
                self.buttons[self.select_ind].go_func()
    
    def Draw(self, screen):
        for b in self.buttons:
            b.Draw(screen)

