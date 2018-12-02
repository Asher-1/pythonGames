"""A timer for games with set-rate FPS.
"""

import pygame

class Timer:
	"""A timer for games with set-rate FPS"""
	
	def __init__(self,fps):
		"""Initialize the timer with the desired FPS."""
		self.wait = 1000/fps
		self.nt = pygame.time.get_ticks()
		
	def tick(self):
		"""Wait correct amount of time each frame.  Call this once per frame."""
		self.ct = pygame.time.get_ticks()
		if self.ct < self.nt:
			pygame.time.wait(self.nt-self.ct)
			self.nt+=self.wait
		else: 
			self.nt = pygame.time.get_ticks()+self.wait


class Speedometer:
	"""A timer replacement that prints out FPS once a second."""
	def __init__(self):
		self.frames = 0
		self.st = pygame.time.get_ticks()
		
	def tick(self):
		""" Call this once per frame."""
		self.frames += 1
		self.ct = pygame.time.get_ticks()
		if (self.ct - self.st) >= 1000: 
			print "%s: %d fps"%(self.__class__.__name__,self.frames)
			self.frames = 0
			self.st += 1000
		pygame.time.wait(0) #NOTE: not sure why, but you gotta call this now and again
			

# vim: set filetype=python sts=4 sw=4 noet si :
