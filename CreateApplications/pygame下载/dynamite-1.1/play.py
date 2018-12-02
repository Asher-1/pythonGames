#"""
try:
	import psyco
	psyco.full()
	print 'psyco installed'
except: 
	print 'psyco not installed'
#"""

import os
	
import pygame
from pygame.locals import *


from pgu import tilevid, timer, html, engine

import states
import high

SW,SH = 640,480#800,600 #1024,768 #800,600#640,480
FPS = 24

class _sound:
	def play(self):
		pass

class Init(engine.State):
	def __init__(self,game,value):
		self.game = game
	def init(self):
		g = self.game
		
		pygame.display.init()
		pygame.display.set_icon(pygame.image.load("icon.tga"))
		pygame.display.set_caption("Dynamite")
		g.screen = pygame.display.set_mode((SW,SH),SWSURFACE|FULLSCREEN)
		
		pygame.font.init()
		g.font_small = pygame.font.Font(os.path.join("data","fonts","zeroes_1.ttf"),20)
		g.font_small2 = pygame.font.Font(os.path.join("data","fonts","zeroes_1.ttf"),30)
		g.font_medium = pygame.font.Font(os.path.join("data","fonts","zeroes_1.ttf"),60)
		g.font_menu = pygame.font.Font(os.path.join("data","fonts","zeroes_1.ttf"),45)
		g.font_title = pygame.font.Font(os.path.join("data","fonts","Squealer.ttf"),100)
		
		g.level = 0
		g.high = 0
		g.score = 0
		g.name = ''
		
		g.highs = high.Highs("hs.dat",1)
		
		try:
			#0/0
			pygame.mixer.init()
			g.audio = 1
			g.music = 1
		except:
			g.audio = 0
		
		g.sfx = {}
		for name in ['yeah-final','whoop-final','arg-final','deton-bomb','laybomb','shoot']:
			if g.audio: g.sfx[name] = pygame.mixer.Sound(os.path.join("data","sfx","%s.wav"%name))
			else: g.sfx[name] = _sound()
		
		#return level.Level(g,None)
		return states.Title(g,None)
		
class Game(engine.Game):
	def event(self,e):
		if e.type is QUIT: 
			self.state = engine.Quit(self)
			return 1
		if e.type is KEYDOWN and e.key == K_F10:
			pygame.display.toggle_fullscreen()
			return 1
		if e.type is KEYDOWN and e.key == K_F12: #screen shots
			self.state = states.Pause(self,("",self.state))
			return 1
		if e.type is KEYDOWN and e.key == K_F2:
			if self.audio:
				self.music ^= 1
				pygame.mixer.music.set_volume(self.music)
			
			
			
	def init(self):
		self.timer = timer.Timer(FPS)
		#self.timer = timer.Speedometer()
		
	def tick(self):
		self.timer.tick() 
		game = self
		if game.score > game.high: game.high = game.score
		

	


_game = Game()
_game.run(Init(_game,None))

pygame.quit()

#import profile
#profile.run('_game.run(Init(_game,None))')