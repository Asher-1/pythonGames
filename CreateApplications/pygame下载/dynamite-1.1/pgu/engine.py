"""a state engine.  reference not complete, please see example"""
import pygame
from pygame.locals import *

class State:
	def __init__(self,game,value=None):
		self.game,self.value = game,value
	def init(self): pass
	def paint(self,screen): pass
	def repaint(self): self._paint = 1
	def update(self,screen): pass
	def loop(self): pass
	def event(self,e): pass

class Quit(State):
	def init(self): 
		self.game.quit = 1

class Game:
	def fnc(self,f,v=None):
		s = self.state
		if not hasattr(s,f): return 0
		f = getattr(s,f)
		if v != None: r = f(v)
		else: r = f()
		if r != None:
			self.state = r
			self.state._paint = 1
			return 1
		return 0
		
	def run(self,state,screen=None):
		self.quit = 0
		self.state = state
		self.screen = screen
		
		self.init()
		
		while not self.quit:
			self.loop()

	def loop(self):
		s = self.state
		if not hasattr(s,'_init') or s._init:
			s._init = 0
			if self.fnc('init'): return
		else: 
			if self.fnc('loop'): return
		if not hasattr(s,'_paint') or s._paint:
			s._paint = 0
			if self.fnc('paint',self.screen): return
		else: 
			if self.fnc('update',self.screen): return
		
		for e in pygame.event.get():
			if self.event(e): return
			if self.fnc('event',e): return
			
		self.tick()
		return
			
	def init(self): pass
		
	def tick(self):
		pygame.time.wait(10)
	
	def event(self,e):
		if e.type is QUIT: 
			self.state = Quit(self)
			return 1

# vim: set filetype=python sts=4 sw=4 noet si :
