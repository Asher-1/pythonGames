import os

import pygame
from pygame.locals import *

from pgu import tilevid, timer, html, engine, text

import level , levels


class Title(engine.State):
	def __init__(self,game,value):
		self.game = game
		
		self.cur = 0
		self.options = [
			("Play < $l >",level.Level(self.game,None)),
			("High Scores",HighScores(self.game,None)),
			("Help",Help(self.game,None)),
			("Quit",engine.Quit(self.game,None)),
			]
		
	def init(self):
		if self.game.audio:
			pygame.mixer.music.load(os.path.join("data","music","music-intro.ogg"))
			pygame.mixer.music.play(-1)
		self.img = pygame.image.load(os.path.join("data","gfx","help.png"))
		
			
	def paint(self,screen):
		self.game.score = 0
		screen.blit(self.img,(0,0))
		
		g = self.game
		hi = (128,128,128)
		fg = (255,255,255)
		
		fnt = g.font_title
		text.write(screen,fnt,(125,10),fg,"dynamite",border=2)
		
		fnt = g.font_menu
		x,y = 180,160
		

		c = fg
		#text.write(screen,fnt,(x,y),c,"High: %05d"%g.high,border=1)
		text.write(screen,fnt,(x,y),c,"Name: %s_"%g.name,border=1)
		y += 70
		
		#x += 40

				
		n = 0
		self.rects = []
		for txt,st in self.options:
			c = fg
			if n == self.cur: c = hi
			txt = txt.replace("$l",levels.levels[g.level][1])
			text.write(screen,fnt,(x,y),c,txt,border=1)
			self.rects.append((pygame.Rect(0,y,640,45),n))
			y += 45
			n += 1
		
		fnt = g.font_small
		x = 80
		y += 28
		text.write(screen,fnt,(x,y),fg,"use left and right arrow keys to change level",border=1)
			
		pygame.display.flip()
		
	def event(self,e):
		lo = len(self.options)
		ll = len(levels.levels)
		if e.type is MOUSEMOTION:
			for rect, cur in self.rects:
				if rect.collidepoint(e.pos):
					if self.cur != cur:
						self.game.sfx['laybomb'].play()
						self.cur = cur
						self.repaint()
						
		if e.type is KEYDOWN:
			if e.key == K_UP:
				self.game.sfx['laybomb'].play()
				self.cur = (self.cur - 1 + lo) % lo
				self.repaint()
			if e.key == K_DOWN:
				self.game.sfx['laybomb'].play()
				self.cur = (self.cur + 1) % lo
				self.repaint()
			if e.key == K_LEFT:
				self.game.sfx['laybomb'].play()
				self.game.level = (self.game.level - 1 + ll) % ll
				self.repaint()
			if e.key == K_RIGHT:
				self.game.sfx['laybomb'].play()
				self.game.level = (self.game.level + 1) % ll
				self.repaint()
			if e.key in xrange(K_a,K_z+1):
				self.game.name = (self.game.name + str(e.unicode).lower())[0:8]
				self.repaint()
				
			if e.key in (K_BACKSPACE,K_DELETE):
				self.game.name = self.game.name[:-1]
				self.repaint()

		if (e.type == KEYDOWN and e.key == K_RETURN) or e.type is MOUSEBUTTONDOWN:
				if self.cur == 0 and self.game.name == '':
					return PauseFade(self.game,("please enter your name",self))
				self.game.sfx['deton-bomb'].play()
				txt,st = self.options[self.cur]
				return st
				
				
			
				
			
		
	
class Help(engine.State):
	def __init__(self,game,value):
		self.game = game
		
	def paint(self,screen):
		img = pygame.image.load(os.path.join("data","gfx","help.png"))
		screen.blit(img,(0,0))
		
		g = self.game
		fg = (255,255,255)
		bg = (0,0,0)
		
		fnt = g.font_title
		text.write(screen,fnt,(20,10),fg,"Help",border=2)
		
		x,y = 20,140
		
		txt = """The evil potentate is ruining everyone's lives!  Use the 
power of dynamite to destroy his strongholds.

Detonate dynamite by the blue load bearing pillars to bring down the castles.  Watch out for the guards.  Hide next to walls, but not too close to guards.  Escape via windows.

Controls:
Left Mouse Button - walk to a point
Numeric Keypad - walk in a direction
Right Mouse Button 1st Time - place dynamite
Right Mouse Button 2nd Time - detonate dynamite
Left CTRL - same as Right Mouse Button
Arrow Keys - peek around the level
Escape - quit;  Enter / p - pause;  F2 - toggle music
"""

		for dx,dy in [(-1,0),(1,0),(0,1),(0,-1),(2,2)]:
			text.writewrap(screen,self.game.font_small,pygame.Rect(x+dx,y+dy,600,1),bg,txt)	
		text.writewrap(screen,self.game.font_small,pygame.Rect(x,y,600,1),fg,txt)	
		
		pygame.display.flip()
		
	def event(self,e):
		if e.type is KEYDOWN:
			return Title(self.game,None)
		if e.type is MOUSEBUTTONDOWN:
			return Title(self.game,None)

class Win(engine.State):
	def __init__(self,game,value):
		self.game = game
		
	def init(self):
		if self.game.audio:
			pygame.mixer.music.load(os.path.join("data","music","music-intro.ogg"))
			pygame.mixer.music.play(-1)
		
	def paint(self,screen):
		img = pygame.image.load(os.path.join("data","gfx","help.png"))
		screen.blit(img,(0,0))
		
		g = self.game
		fg = (255,255,255)
		bg = (0,0,0)
		
		fnt = g.font_title
		text.write(screen,fnt,(20,10),fg,"You Won!",border=2)
		
		x,y = 20,140
		
		txt = """You have saved the people from the evil potentate.  Good job.
		
Now you can spend the rest of your life basking in the glow of your great accomplishment.  You are a true hero.

Huzzah.
"""

		for dx,dy in [(-1,0),(1,0),(0,1),(0,-1),(2,2)]:
			text.writewrap(screen,self.game.font_small,pygame.Rect(x+dx,y+dy,600,1),bg,txt)	
		text.writewrap(screen,self.game.font_small,pygame.Rect(x,y,600,1),fg,txt)	
		
		
		
		
		
		
		pygame.display.flip()
		
	def event(self,e):
		if e.type is KEYDOWN:
			return Title(self.game,None)
		if e.type is MOUSEBUTTONDOWN:
			return Title(self.game,None)
		
class Pause(engine.State):
	def __init__(self,game,value):
		self.game = game
		if len(value) == 2:
			self.text,self.next = value
			self.sub = ""
		else: self.text,self.sub,self.next = value
		
	def paint(self,screen):
		if self.game.audio and self.text == 'Pause': #HACK, bleckl!
			pygame.mixer.music.pause()
	
		self.screen = screen
		self.orig = pygame.Surface((screen.get_width(),screen.get_height()))
		self.orig.blit(screen,(0,0))
		c = (255,255,255)
		text.writec(screen,self.game.font_medium,c,self.text,border=2)
		
		bg = (0,0,0)
		if len(self.sub) > 40:
			for dx,dy in [(-1,0),(1,0),(0,1),(0,-1),(2,2)]:
				text.writewrap(screen,self.game.font_small,pygame.Rect(40+dx,270+dy,560,1),bg,self.sub)	
			text.writewrap(screen,self.game.font_small,pygame.Rect(40,270,560,1),c,self.sub)	
		else:
			img = self.game.font_small2.render(self.sub,1,bg)
			for dx,dy in [(-1,0),(1,0),(0,1),(0,-1),(2,2)]:
				screen.blit(img,((screen.get_width()-img.get_width())/2+dx,270+dy))
			img = self.game.font_small2.render(self.sub,1,c)
			screen.blit(img,((screen.get_width()-img.get_width())/2,270))
		pygame.display.flip()

	def event(self,e):
		if e.type is KEYDOWN:
			self.screen.blit(self.orig,(0,0))
			if self.game.audio:
				pygame.mixer.music.unpause()

			return self.next       
		if e.type is MOUSEBUTTONDOWN:
			self.screen.blit(self.orig,(0,0))
			if self.game.audio:
				pygame.mixer.music.unpause()
			return self.next       
			
class PauseFade(engine.State):
	def __init__(self,game,value):
		self.game = game
		if len(value) == 2:
			self.text,self.next = value
			self.sub = ""
		else: self.text,self.sub,self.next = value
		
	def paint(self,screen):
		self.screen = screen
		self.orig = pygame.Surface((screen.get_width(),screen.get_height()))
		self.orig.blit(screen,(0,0))
		screen.fill((0,0,0))
		self.orig.set_alpha(128)
		screen.blit(self.orig,(0,0))
		self.orig.set_alpha(255)
		c = (255,255,255)
		text.writec(screen,self.game.font_menu,c,self.text,border=2)
		
		bg = (0,0,0)
		if len(self.sub) > 40:
			for dx,dy in [(-1,0),(1,0),(0,1),(0,-1),(2,2)]:
				text.writewrap(screen,self.game.font_small,pygame.Rect(40+dx,270+dy,560,1),bg,self.sub)	
			text.writewrap(screen,self.game.font_small,pygame.Rect(40,270,560,1),c,self.sub)	
		else:
			img = self.game.font_small2.render(self.sub,1,bg)
			for dx,dy in [(-1,0),(1,0),(0,1),(0,-1),(2,2)]:
				screen.blit(img,((screen.get_width()-img.get_width())/2+dx,270+dy))
			img = self.game.font_small2.render(self.sub,1,c)
			screen.blit(img,((screen.get_width()-img.get_width())/2,270))
		pygame.display.flip()

	def event(self,e):
		if e.type is KEYDOWN:
			self.screen.blit(self.orig,(0,0))
			return self.next       
		if e.type is MOUSEBUTTONDOWN:
			self.screen.blit(self.orig,(0,0))
			return self.next       
			
class Prompt(engine.State):
	def __init__(self,game,value):
		self.game = game
		self.text,self.yes,self.no = value
		
	def paint(self,screen):
		self.screen = screen
		self.orig = pygame.Surface((screen.get_width(),screen.get_height()))
		self.orig.blit(screen,(0,0))
		c = (255,255,255)
		text.writec(screen,self.game.font_medium,c,self.text,border=2)
		pygame.display.flip()
 
	def event(self,e):
		if e.type is KEYDOWN and e.key == K_y: 
			self.screen.blit(self.orig,(0,0))
			return self.yes
		if e.type is KEYDOWN and e.key == K_n: 
			self.screen.blit(self.orig,(0,0))
			return self.no
		
class HighScores(engine.State):
	def __init__(self,game,value):
		self.game = game
	def paint(self,screen):
		g = self.game
		img = pygame.image.load(os.path.join("data","gfx","help.png"))
		screen.blit(img,(0,0))

		fnt = g.font_title
		fg = (255,255,255)
		text.write(screen,fnt,(80,10),fg,"High Scores",border=2)
		
		fnt = g.font_small
		
		cx = 20,60,220, 340,380,540
		
		cts = []
		cts.append(['','Overall Records','','','Your Records',''])
		cts.append(['','       ','','','        ',''])
		name = g.name
		for n in range(1,11):
			e = g.highs['_overall-%d'%n][0]
			
			h = g.highs['%s-%d'%(name,n)]
			if len(h) > 0: score = h[0].score
			else: score = 0
			
			cts.append(["%d."%n,e.name,"%05d"%e.score,"%d."%n,name,"%05d"%score])
		
		y = 170
		for ct in cts:		
			i = 0
			for t in ct:
				x,i = cx[i],i+1
				text.write(screen,fnt,(x,y),fg,t)
			y += 21
			
		y += 21
		text.write(screen,fnt,(120,y),fg,"high scores are on a per-level basis")
		
		pygame.display.flip()
		
	def event(self,e):
		if e.type is KEYDOWN:
			return Title(self.game,None)
		if e.type is MOUSEBUTTONDOWN:
			return Title(self.game,None)
