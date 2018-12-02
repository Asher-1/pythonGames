import sys
import math
import random
import os

import pygame
from pygame.rect import Rect
from pygame.locals import *

from pgu import engine, tilevid

import isovid
import states
import levels

TW,TH = 32,32
FPS = 40
CALPHA = 196

#box = 32,16,32,64
#box = 32,64,32,16
box = 32+4,64-4,24,24
box128 = 52,74,24,24



idata = []

	
dirs = ['n','ne','e','se','s','sw','w','nw']
dmap = [
	('0000','s'),
	('0001','sw'),
	('0002','w'),
	('0003','nw'),
	('0004','n'),
	('0005','ne'),
	('0006','e'),
	('0007','se'),
	]

path = os.path.join("data","player")
name = 'player'
for d in dirs:
	for n in xrange(0,8):
		idata.append(('%s.walking.%s.%d'%(name,d,n),os.path.join(path,'walking %s%04d.bmp'%(d,n)),box))
for num,d in dmap:
	for n in xrange(0,1):
		idata.append(('%s.stopped.%s.%d'%(name,d,n),os.path.join(path,'stopped%s.bmp'%num),box))
for d in dirs:
	for n in xrange(0,10):
		idata.append(('%s.tipping.%s.%d'%(name,d,n),os.path.join(path,'tipping over %s%04d.bmp'%(d,n)),box128))

path = os.path.join("data","soldier")
name = 'soldier'
for d in dirs:
	for n in xrange(0,8):
		idata.append(('%s.walking.%s.%d'%(name,d,n),os.path.join(path,'walking %s%04d.bmp'%(d,n)),box))
for d in dirs:
	for n in xrange(0,8):
		idata.append(('%s.running.%s.%d'%(name,d,n),os.path.join(path,'running %s%04d.bmp'%(d,n)),box))
for d in dirs:
	for n in xrange(0,10):
		idata.append(('%s.shooting.%s.%d'%(name,d,n),os.path.join(path,'shooting %s%04d.bmp'%(d,n)),box))
for num,d in dmap:
	for n in xrange(0,1):
		idata.append(('%s.stopped.%s.%d'%(name,d,n),os.path.join(path,'stopped%s.bmp'%num),box))

path = os.path.join("data","explosion")
name = 'explosion'
mybox = (100,100,1,1)
for d in dirs:
	for n in xrange(0,9):
		idata.append(('%s.%d'%(name,n),os.path.join(path,'ani%04d.png'%(n+2)),mybox))

	
wallc = (255,255,255,CALPHA)
pilarc = (0,255,255,CALPHA)
winc = (255,0,0,CALPHA)	
tdata = {
	0x01:(None,None,{'color':wallc}),
	0x02:(None,None,{'color':wallc}),
	0x03:(None,None,{'color':wallc}),
	0x04:(None,None,{'color':pilarc}),
	0x05:(None,None,{'color':winc}),
	0x06:(None,None,{'color':winc}),
	0x07:(None,None,{'color':winc}),
	0x08:(None,None,{'color':wallc}),
	0x09:(None,None,{'color':wallc}),
	0x0a:(None,None,{'color':wallc}),
	0x0b:(None,None,{'color':wallc}),
	0x0c:(None,None,{'color':wallc}),
	0x0d:(None,None,{'color':wallc}),
	0x0e:(None,None,{'color':wallc}),
	0x0f:(None,None,{'color':wallc}),
	}
	
dd2facing = {
	(-1,-1):7,
	(0,-1):8,
	(1,-1):9,
	(-1,0):4,
	(0,0):5,
	(1,0):6,
	(-1,1):1,
	(0,1):2,
	(1,1):3, 
	}
	
facing2dd = {
	7:(-1,-1),
	8:(0,-1),
	9:(1,-1),
	4:(-1,0),
	5:(0,0),
	6:(1,0),
	1:(-1,1),
	2:(0,1),
	3:(1,1),
	}
	
facing2compass = {
	7:'n',
	8:'ne',
	9:'e',
	4:'nw',
	5:'se', #whatever
	6:'se',
	1:'w',
	2:'sw',
	3:'s',
	}
	
	
	
def player_new(g,t,value):
	g.clayer[t.ty][t.tx] = 0
	s = tilevid.Sprite(g.images['player.stopped.s.0'],t.rect)
	#print 'new player',t.rect
	g.sprites.append(s)
	
	g.player = s
	g.control = s
	s.color = (255,0,255,CALPHA)
	s.loop = player_loop
	s.path = []
	
	s.walking = 0
	s.facing = 6
	s.dd = facing2dd[s.facing]
	s.frame = 0
	s.speed = 8
	s.speedadd = 0
	s.alive = 1
	s.dead = 0
	s.type = 'player'
	
def player_death(g,s):
	s.alive = 0
	s.frame = 0
	#if s in g.sprites:
	#	g.sprites.remove(s)
	#s.dead = 1

def object_sprite(g,s,char,mode,n):
	c = facing2compass[s.facing]
	f = s.frame%n
	s.setimage(g.images['%s.%s.%s.%d'%(char,mode,c,f)])

	
def player_loop(g,s):
	tx,ty = s.rect.centerx/TW,s.rect.centery/TH
	if s.alive == 1 and g.slayer[ty][tx] != 0:
		g.sfx['arg-final'].play()
		s.alive = 0
		s.frame = 0
		
	if s.alive == 0 and s.frame == 10:
		s.dead = 1
		return
		#g.sprites.remove(s)
		
	if s.alive: followpath(g,s)
	
	name = 'player'
	if s.alive == 1 and s.walking == 1: object_sprite(g,s,name,'walking',8)
	elif s.alive == 0: object_sprite(g,s,name,'tipping',10)
	else: object_sprite(g,s,name,'stopped',1)
	
	s.frame += 1
	
"""
def player_event(g,e):
	s = g.player
	keys = pygame.key.get_pressed()
	dx,dy = 0,0
	if keys[K_UP]: dy -= 1
	if keys[K_RIGHT]: dx += 1
	if keys[K_DOWN]: dy += 1
	if keys[K_LEFT]: dx -= 1
	v = 4
	s.rect.x += dx*v
	s.rect.y += dy*v
"""	

def cursor_new(g):
	s = tilevid.Sprite(g.tiles[0].image,(0,0))
	s.color = (196,196,196)
	g.sprites.append(s)
	s.loop = cursor_loop
	s.type = 'cursor'
	
def cursor_loop(g,s):
	tv = g
	tx,ty = getpos(tv,pygame.mouse.get_pos())
	slayer = tv.slayer
	w,h = len(slayer[0]),len(slayer)

	if ty >= 1 and tx >= 1 and tx < w-1 and ty < h-1:
		n = 1
		if slayer[ty][tx]: n = 0
		if n == 1:
			for dx,dy in [(-1,0),(1,0),(0,1),(0,-1)]:
				if slayer[ty+dy][tx+dx]: n = 2
		s.setimage(g.tiles[0x11+n].image)
		s.rect.x,s.rect.y,s.rect.w,s.rect.h = tx*TW,ty*TH,TW,TH
		s.shape.x,s.shape.y,s.shape.w,s.shape.h = 0,64-16,TW,16
	else:
		s.setimage(g.tiles[0].image)
		
			
	

def soldier_new(g,t,value):
	#guard variables, eyesight wideness, distance, etc, speed of movement, regularity of patrol	

	g.clayer[t.ty][t.tx] = 0
	s = tilevid.Sprite(g.images['soldier.stopped.s.0'],t.rect)
	s.color = (0,255,0,CALPHA)
	g.sprites.append(s)
	s.path = []
	s.loop = soldier_loop
	s.path_n = 0
	s.paths = g.soldier_paths[value['sid']]
	s.walking = 0
	s.facing = 6
	s.dd = facing2dd[s.facing]
	s.frame = 0
	s.speed = 5
	s.speedadd = 0
	s.type = 'soldier'
	s.seeplayer = 0
	s.shooting = 0

def soldier_path(g,t,value):
	g.clayer[t.ty][t.tx] = 0
	g.soldier_paths[value['sid']][value['pid']] = t.tx,t.ty
	
def soldier_loop(g,s):
	tx,ty = s.rect.centerx/TW,s.rect.centery/TH
	if g.slayer[ty][tx] != 0:
		g.sprites.remove(s)
		#g.game.score += 0
		g.gkills += 1
		g.sfx['arg-final'].play()
		return

	if g.control != s: 
		if not len(s.path):
			s.speedadd = 0
			s.path_n = (s.path_n+1) % 8
			dest = s.paths[s.path_n]
			#print s.paths
			#print dest
			if dest != None:
				tx,ty = s.rect.centerx / TW, s.rect.centery/TH
				s.path = astar((tx,ty),dest,g.slayer)
				if len(s.path) == 0:
					s.paths[s.path_n] = None
				#print len(s.path)
				
	if s.shooting != 1:
		followpath(g,s)
	else: 
		sx,sy = s.rect.centerx,s.rect.centery
		px,py = g.player.rect.centerx,g.player.rect.centery
		dx,dy = px-sx,py-sy
		if dx != 0: dx /= abs(dx)
		if dy != 0: dy /= abs(dy)
		s.dd = dx,dy
		s.facing = dd2facing[s.dd]

	if cansee(g,s,g.player):
		s.seeplayer += 1
		if s.seeplayer > 5:
			if g.player.alive:
				g.sfx['shoot'].play()
				g.sfx['arg-final'].play()
				player_death(g,g.player)
				s.shooting = 1
	else: s.seeplayer = 0
	
		
		
	name = 'soldier'
	if s.shooting == 1: object_sprite(g,s,name,'shooting',10)
	elif s.walking == 1 and s.speedadd != 0: 
		object_sprite(g,s,name,'running',8)
		if random.randrange(0,40) == 0:
			g.sfx['whoop-final'].play()
	elif s.walking == 1: object_sprite(g,s,name,'walking',8)
	else: object_sprite(g,s,name,'stopped',1)
	
	s.frame += 1

def getline(a,b):
	path = []
	
	x1,y1 = a
	x2,y2 = b
	dx,dy = abs(x2-x1),abs(y2-y1)

	if x2 >= x1: xi1,xi2 = 1,1
	else: xi1,xi2 = -1,-1
	
	if y2 >= y1: yi1,yi2 = 1,1
	else: yi1,yi2 = -1,-1
	
	if dx >= dy:
		xi1,yi2 = 0,0
		d = dx
		n = dx/2
		a = dy
		p = dx
	else:
		xi2,yi1 = 0,0
		d = dy
		n = dy/2
		a = dx
		p = dy
		
	x,y = x1,y1
	c = 0
	while c <= p:
		path.append((x,y))
		n += a
		if n > d: 
			n -= d
			x += xi1
			y += yi1
		x += xi2
		y += yi2
		c += 1
	return path

#this one gives a line that doesn't use 7,9,1,3 facings
def getline2(a,b):
	path = []
	
	x1,y1 = a
	x2,y2 = b
	dx,dy = abs(x2-x1),abs(y2-y1)

	if x2 >= x1: xi1,xi2 = 1,1
	else: xi1,xi2 = -1,-1
	
	if y2 >= y1: yi1,yi2 = 1,1
	else: yi1,yi2 = -1,-1
	
	if dx >= dy:
		xi1,yi2 = 0,0
		d = dx
		n = dx/2
		a = dy
		p = dx
	else:
		xi2,yi1 = 0,0
		d = dy
		n = dy/2
		a = dx
		p = dy
		
	x,y = x1,y1
	c = 0
	while c <= p:
		path.append((x,y))
		n += a
		if n > d: 
			n -= d
			path.append((x+xi2,y+yi2)) #thicker
			x += xi1
			y += yi1
			path.append((x,y)) #thicker
		x += xi2
		y += yi2
		c += 1
	return path


def cansee(g,s,p): #can sprite a see sprite b?
	vlayer = g.vlayer
	
	tx,ty = s.rect.centerx/TW,s.rect.centery/TH
	px,py = p.rect.centerx/TW,p.rect.centery/TH
	
	dx,dy = px-tx,py-ty
	
	
	#calculate my semi dist
	dist = ( max(abs(dx),abs(dy)) + abs(dx)+abs(dy) )/2
	
	#if the player is far away, can't see 'em
	if dist > 15: return 0 #was 20
	
	#if the player is not moving and is next to a wall, can't see 'em...
	if dist > 1 and p.walking == 0:
		for ix,iy in [(-1,0),(1,0),(0,1),(0,-1)]:
			if vlayer[py+iy][px+ix]: return 0
			
	ok = 0
	
	#if the player is really near, and walking, we can hear 'em.. which is
	#as good as sight!
	if dist < 6 and p.walking == 1: ok = 1
	
	#check if we are in a good angle
	fa = math.atan2(s.dd[1],s.dd[0]) * 360 / (2.0*math.pi) #facing angle
	pa = math.atan2(dy,dx) * 360 / (2.0*math.pi) #
	if fa < 0: fa += 360
	if pa < 0: pa += 360
	if fa < pa and (pa-fa) > 180: fa += 360
	if pa < fa and (fa-pa) > 180: pa += 360
	if abs(fa-pa) < 60: ok = 1 #was 60
	
	#if they aren't really close, or the angle isn't good
	if not ok: return 0

	#check for obstructions between items	
	s = 8#4
	starts = [
		(p.rect.centerx,p.rect.centery),
		#(p.rect.left-s,p.rect.top-s),
		#(p.rect.right+s,p.rect.top-s),
		#(p.rect.left-s,p.rect.bottom+s),
		#(p.rect.right+s,p.rect.bottom+s),
		]
	
	for pos in starts:
		px,py = pos[0]/TW,pos[1]/TH
		path = getline2((tx,ty),(px,py))
		
		for x,y in path:
			if vlayer[y][x] != 0: return 0

	#if we made it this far, we can see the player	
	return 1
		

	
def followpath(g,s):
	path = s.path
	#print path
	if not len(path):
		s.walking = 0
		return
	s.walking = 1
	"""
	if len(path)>1: 
		next = path[1]
		dx,dy = next[0]-px,next[1]-py
		if slayer[py+dy][px+dx] != 0: next = path[0] 
	
	else: next = path[0]
	"""
	px,py = s.rect.centerx / TW, s.rect.centery/TH
	
	next = path[0]
	
	dx,dy = next[0]-px,next[1]-py
	if dx == 0 and dy == 0:
		s.path.pop(0)
		if len(s.path) == 0:
			s.rect.centerx,s.rect.centery = next[0]*TW+TW/2,next[1]*TH+TH/2
		return followpath(g,s)
	
	v = s.speed+s.speedadd
	if dx != 0 and dy != 0:
		v = v * 100 / 141 #sqrt 2
		
	nx,ny = s.rect.centerx+dx*v,s.rect.centery+dy*v
	
	ntx,nty = nx/TW,ny/TH
	slayer = g.slayer
	if slayer[nty][ntx] != 0:
		s.path = []
		s.walking = 0
		return
		
	s.rect.centerx = nx
	s.rect.centery = ny
	
	if dx != 0: dx /= abs(dx)
	if dy != 0: dy /= abs(dy)
	s.dd = dx,dy
	s.facing = dd2facing[s.dd]
	
	if dx == 0: s.rect.centerx = next[0]*TW+TW/2
	if dy == 0: s.rect.centery = next[1]*TH+TH/2
			
	
CODE_BOMB = 0x02	
BKGR_MARK = 0x18
TILE_BOMB = 0x19
TILE_CLOSED = 0x06
TILE_OPEN = 0x07
TILE_WINDOW = 0x05
TILE_PILAR = 0x04
def bomb_new(g,t,value):
	#blayer = g.blayer
	g.blayer[t.ty][t.tx] = BKGR_MARK
	g.tlayer[t.ty][t.tx] = TILE_PILAR
	#g.slayer[t.ty][t.tx] = 1
	
	
	#mlayer = g.mlayer
	#mlayer[t.ty][t.tx] = (255,0,0)


def btimer_new(g,pos):
	s = tilevid.Sprite(pygame.Surface((1,1)),(0,0))
	s.pos = pos
	s.timer = 60
	s.loop = btimer_loop
	s.color = 0,0,0,CALPHA
	g.sprites.append(s)
	
		
bmap = [(0,0,0,0,6,6,6,0,0,0,0),
	(0,0,6,6,5,5,5,6,6,0,0),
	(0,6,5,5,4,4,4,5,5,6,0),
	(0,6,5,4,3,3,3,4,5,6,0),
	(6,5,4,3,2,2,2,3,4,5,6),
	(6,5,4,3,2,1,2,3,4,5,6),
	(6,5,4,3,2,2,2,3,4,5,6),
	(0,6,5,4,3,3,3,4,5,6,0),
	(0,6,5,5,4,4,4,5,5,6,0),
	(0,0,6,6,5,5,5,6,6,0,0),
	(0,0,0,0,6,6,6,0,0,0,0),
	]

def explosion_new(g,pos):
	s = tilevid.Sprite(g.images['explosion.0'],(pos[0]*TW+TW/2,pos[1]*TH+TH/2))
	s.color = (255,255,255,CALPHA)
	g.sprites.append(s)
	s.loop = explosion_loop
	s.frame = 0
	s.pos = pos
	explosion_blast(g,s.pos,1)
	s.type = 'explosion'
	
def explosion_loop(g,s):
	if s.frame == 10:
		smap = [0,100,400,1200,3200,8000,19200]
		g.game.score += smap[g.gkills]
		g.sprites.remove(s)
		return
	s.setimage(g.images['explosion.%s'%min(8,s.frame)])
	explosion_blast(g,s.pos,(s.frame)/2+1)
	s.frame += 1
	
def explosion_blast(g,pos,l):
	tx,ty = pos
	tlayer = g.tlayer
	blayer = g.blayer
	slayer = g.slayer
	vlayer = g.vlayer
	mlayer = g.mlayer
	zlayer = g.zlayer
	
	w,h = len(tlayer[0]),len(tlayer)
	dy = -5
	for bline in bmap:
		dx = -5
		for v in bline:
			xx,yy = tx+dx,ty+dy
			if xx >= 0 and xx < w and yy >= 0 and yy < h:
				if v == l:
					#tlayer[yy][xx] = 0x1a+v-1
					if tlayer[yy][xx] == 4:
						g.pilars -= 1
						#g.game.score += 500
					tlayer[yy][xx] = 0
					blayer[yy][xx] = 0x1c #0x1a+v-1
					slayer[yy][xx] = 1
					vlayer[yy][xx] = 0
					mlayer[yy][xx] = (0,0,0)
					#mlayer[yy][xx] = 0
					#zlayer[yy][xx] = 1
				elif v == l+1:
					if blayer[yy][xx] not in (0,0x1e,0x1c,0x1b):
						blayer[yy][xx] = 0x1a
						#dd = dx+dy
						#if dd <= -2: blayer[yy][xx] = 0x1a
						#elif dd <= 0: blayer[yy][xx] = 0x1b
						#elif dd < 2: blayer[yy][xx] = 0x1c
						#else: blayer[yy][xx] = 0x1c #NOTE
					elif blayer[yy][xx] == 0x1e:
						blayer[yy][xx] = 0x1b
			
			dx += 1
		dy += 1
		
	g.level.minimap_draw()
	
	
def bomb_explode(g,pos):
	#g.sfx['bomb'].play()
	tx,ty = pos
	
	#get some guards running
	sp = []
	for s in g.sprites:
		if hasattr(s,'type') and s.type == 'soldier':
			#s.path = getpath(g,s,pos)
			px,py = s.rect.centerx/TW,s.rect.centery/TH
			sp.append((dist((px,py),(tx,ty)),s))
	sp.sort()
	#sp.reverse()
	n = 3
	if len(sp) < 3: n = len(sp)
	for d,s in sp[:n]:
		px,py = s.rect.centerx/TW,s.rect.centery/TH
		s.path = astar((px,py),(tx,ty),g.slayer)
		s.speedadd = 4
		
	g.gkills = 0

	explosion_new(g,pos)



	
		
def btimer_loop(g,s):
	s.timer -= 1
	#print 'bomb',s.timer
	if s.timer == 0:
		pos = s.pos
		bomb_explode(g,pos)		
		g.sprites.remove(s)
		
		for s in g.sprites:
			if hasattr(s,'type') and s.type == 'soldier':
				s.speed += 3
				
"""
def decor_new(g,t,v):
	g.clayer[t.ty][t.tx] = 0
	s = tilevid.Sprite(g.images['decor.%s'%v],t.rect)
	#s = tilevid.Sprite(g.images['player.walking.n.1'],t.rect)
	#print t.rect
	s.color = (0,0,0)
	g.sprites.append(s)
"""
"""	
	0x08:(decor_new,'armor-x'),
	0x09:(decor_new,'armor-y'),
	0x0a:(decor_new,'shield-x'),
	0x0b:(decor_new,'shield-y'),
	0x0c:(decor_new,'flag-x'),
	0x0d:(decor_new,'flag-y'),
	0x0e:(decor_new,'vase1'),
	0x0f:(decor_new,'vase2'),
"""

cdata = {
	0x01:(player_new,None),
	0x02:(bomb_new,None),
	0x10:(soldier_new,{'sid':0}),
	0x11:(soldier_path,{'sid':0,'pid':1}),
	0x12:(soldier_path,{'sid':0,'pid':2}),
	0x13:(soldier_path,{'sid':0,'pid':3}),
	0x14:(soldier_path,{'sid':0,'pid':4}),
	0x15:(soldier_path,{'sid':0,'pid':5}),
	0x16:(soldier_path,{'sid':0,'pid':6}),
	0x17:(soldier_path,{'sid':0,'pid':7}),

	0x18:(soldier_new,{'sid':1}),
	0x19:(soldier_path,{'sid':1,'pid':1}),
	0x1a:(soldier_path,{'sid':1,'pid':2}),
	0x1b:(soldier_path,{'sid':1,'pid':3}),
	0x1c:(soldier_path,{'sid':1,'pid':4}),
	0x1d:(soldier_path,{'sid':1,'pid':5}),
	0x1e:(soldier_path,{'sid':1,'pid':6}),
	0x1f:(soldier_path,{'sid':1,'pid':7}),
	
	0x20:(soldier_new,{'sid':2}),
	0x21:(soldier_path,{'sid':2,'pid':1}),
	0x22:(soldier_path,{'sid':2,'pid':2}),
	0x23:(soldier_path,{'sid':2,'pid':3}),
	0x24:(soldier_path,{'sid':2,'pid':4}),
	0x25:(soldier_path,{'sid':2,'pid':5}),
	0x26:(soldier_path,{'sid':2,'pid':6}),
	0x27:(soldier_path,{'sid':2,'pid':7}),

	0x28:(soldier_new,{'sid':3}),
	0x29:(soldier_path,{'sid':3,'pid':1}),
	0x2a:(soldier_path,{'sid':3,'pid':2}),
	0x2b:(soldier_path,{'sid':3,'pid':3}),
	0x2c:(soldier_path,{'sid':3,'pid':4}),
	0x2d:(soldier_path,{'sid':3,'pid':5}),
	0x2e:(soldier_path,{'sid':3,'pid':6}),
	0x2f:(soldier_path,{'sid':3,'pid':7}),
	
	0x30:(soldier_new,{'sid':4}),
	0x31:(soldier_path,{'sid':4,'pid':1}),
	0x32:(soldier_path,{'sid':4,'pid':2}),
	0x33:(soldier_path,{'sid':4,'pid':3}),
	0x34:(soldier_path,{'sid':4,'pid':4}),
	0x35:(soldier_path,{'sid':4,'pid':5}),
	0x36:(soldier_path,{'sid':4,'pid':6}),
	0x37:(soldier_path,{'sid':4,'pid':7}),

	0x38:(soldier_new,{'sid':5}),
	0x39:(soldier_path,{'sid':5,'pid':1}),
	0x3a:(soldier_path,{'sid':5,'pid':2}),
	0x3b:(soldier_path,{'sid':5,'pid':3}),
	0x3c:(soldier_path,{'sid':5,'pid':4}),
	0x3d:(soldier_path,{'sid':5,'pid':5}),
	0x3e:(soldier_path,{'sid':5,'pid':6}),
	0x3f:(soldier_path,{'sid':5,'pid':7}),

	}
	

def dist(a,b):
	return abs(a[0]-b[0]) + abs(a[1]-b[1])
	
class node:
	def __init__(self,prev,pos,dest):
		self.prev,self.pos,self.dest = prev,pos,dest
		if self.prev == None: self.g = 0
		else: self.g = self.prev.g + 1
		self.h = dist(pos,dest)
		self.f = self.g+self.h
		
def astar(start,end,layer):
	if layer[start[1]][start[0]]: return [] #start is blocked
	if layer[end[1]][end[0]]: return [] #end is blocked
	w,h = len(layer[0]),len(layer)
	if start[0] < 0 or start[1] < 0 or start[0] >= w or start[1] >= h: return [] #start outside of layer
	if end[0] < 0 or end[1] < 0 or end[0] >= w or end[1] >= h: return [] #end outside of layer

	opens = []
	open = {}
	closed = {}
	cur = node(None,start,end)
	open[cur.pos] = cur
	opens.append(cur)
	while len(open):
		cur = opens.pop(0)
		if cur.pos not in open: continue
		del open[cur.pos]
		closed[cur.pos] = cur
		if cur.pos == end: break
		for dx,dy in [(0,-1),(1,0),(0,1),(-1,0), (-1,-1),(1,-1),(-1,1),(1,1)]:
			x,y = pos = cur.pos[0]+dx,cur.pos[1]+dy
			if layer[y][x]: continue
			#check for blocks of diagonals
			if layer[cur.pos[1]+dy][cur.pos[0]]: continue
			if layer[cur.pos[1]][cur.pos[0]+dx]: continue
			new = node(cur,pos,end)
			if pos in open and new.f >= open[pos].f: continue
			if pos in closed and new.f >= closed[pos].f: continue
			if pos in open: del open[pos]
			if pos in closed: del closed[pos]
			open[pos] = new
			lo = 0
			hi = len(opens)
			while lo < hi:
				mid = (lo+hi)/2
				if new.f < opens[mid].f: hi = mid
				else: lo = mid + 1
			opens.insert(lo,new)
	
	if cur.pos != end: 
		return []
					
	path = []
	while cur.prev != None:
		path.append(cur.pos)
		cur = cur.prev
	path.reverse()
	return path

def getpos(tv,dest):
	
	return tv.screen2tile(dest)
	
	
def validpos(tv,pos):
	tx,ty = pos
	tlayer = tv.tlayer
	w,h = len(tlayer[0]),len(tlayer)
	
	if tx < 0 or tx >= w: return 0
	if ty < 0 or ty >= h: return 0
	return 1
	
	
def getpath(tv,p,dest):
	tx,ty = getpos(tv,dest)
	if not validpos(tv,(tx,ty)): return []	
	
	tlayer = tv.tlayer
	blayer = tv.blayer
	slayer = tv.slayer
	
	n = tlayer[ty][tx]
	
	
	if n == TILE_WINDOW:
		for dx,dy in [(-1,0),(1,0),(0,1),(0,-1)]:
			nx,ny = tx+dx,ty+dy
			if slayer[ny][nx] == 0 and blayer[ny][nx] != 0x1e:
				tx,ty = nx,ny
				break
	
	#print tx,ty
	#self.game.tv.blayer[ty][tx] = random.randrange(0,4)
	
	px,py = p.rect.centerx/TW,p.rect.centery/TH
	
	path = astar((px,py),(tx,ty),tv.slayer)

	"""
	slayer = tv.slayer
	blayer = tv.blayer
		
	for y in xrange(0,h):
		for x in xrange(0,w):
			blayer[y][x] = 0
			
	for x,y in path:
		blayer[y][x] = 1

	blayer[ty][tx] = 8
	"""
	
	return path
			
	
class Level(engine.State):
	def __init__(self,game,value):
		self.game = game
		
	def init(self):
		g = self.game
		if not hasattr(g,'tv'):
			tv = g.tv = isovid.Isovid()
			 
			#tilevid.Tilevid()
			#tv.screen = g.screen
			self.load()
			
		tv = g.tv
		tv.level = self
		
		#remove all sprites
		#for s in tv.sprites:
		#	tv.sprites.remove(s)
		tv.sprites = tilevid._Sprites()
		
		cursor_new(tv)
			
		#remove peeking so it resets the screen
		if hasattr(tv,'peeking'): delattr(tv,'peeking')
		
		if len(sys.argv) > 1:
			lvl = (sys.argv[1],'test','test','test',25,os.path.join("data","music","music1.ogg"),20*60)
		else: lvl = levels.levels[g.level]		
		
		self.lvl = lvl
		
		if self.game.audio:
			pygame.mixer.music.load(self.lvl[5])
			pygame.mixer.music.play(-1)
			
		self.time = self.lvl[6]
				
		tv.tga_load_level(lvl[0],1)
		tv.bounds = pygame.Rect(TW*2,TH*2,(len(tv.tlayer[0])-4)*TW,(len(tv.tlayer)-4)*TH)
		
		w,h = len(tv.tlayer[0]),len(tv.tlayer)
		tv.soldier_paths = [[None for m in xrange(0,8)] for n in xrange(0,8)]
		tv.run_codes(cdata,(0,0,w,h))

		tv.bombs = lvl[4]
		tv.pilars = 0
		
		self.game.score = 0

						
		v = self.game.tv
		tlayer = v.tlayer
		blayer = v.blayer
		w,h = len(tlayer[0]),len(tlayer)
		
		
		#solid layer, can't walk through
		slayer = v.slayer = [[0 for x in xrange(0,w)] for y in xrange(0,h)]
		#view layer, can't see through
		vlayer = v.vlayer = [[0 for x in xrange(0,w)] for y in xrange(0,h)]
		#map layer, colors of items
		mlayer = v.mlayer = [[0 for x in xrange(0,w)] for y in xrange(0,h)]
		#zlayer for falling blocks
		zlayer = v.zlayer = [[0 for x in xrange(0,w)] for y in xrange(0,h)]
		for ty in xrange(0,h):
			for tx in xrange(0,w):
				if tlayer[ty][tx] != 0:
					slayer[ty][tx] = 1
				#if tlayer[ty][tx] == 0x05: #a window
				#	slayer[ty][tx] = -1
				if tlayer[ty][tx] != 0:
					vlayer[ty][tx] = 1
				n = tlayer[ty][tx]
				t = tv.tiles[n]
				if hasattr(t,'config'):
					mlayer[ty][tx] = t.config.get('color')
				if blayer[ty][tx] == BKGR_MARK:
					mlayer[ty][tx] = pilarc #(255,0,0)
					tv.pilars += 1
		tv.bomb = None
		
		self.frames = 0
		self.getready = 0 
		
		self.minimap_draw()
		
		
	def load(self):
		tv = self.game.tv
		tv.sfx = self.game.sfx
		tv.game = self.game
		tv.tga_load_tiles(os.path.join("data","gfx","isotiles.tga"),(32,64),tdata)
		#HACK: to make the "tile size" 32x32:
		img = pygame.Surface((32,32)).convert()
		img.set_colorkey(img.get_at((0,0)))
		tv.tiles[0] = tilevid.Tile(img)
		tv.load_images(idata)
		
		
		#color key all the images
		#print tv.images
		for k,(img,shape) in tv.images.items():
			if 'explosion' in k or 'cursor' in k: continue
			#continue
			#print k,img.get_width(),img.get_height()
			
			img = img.convert()
			img.set_colorkey(img.get_at((0,0)))#,RLEACCEL)
			#img.set_alpha(128)
			
			#img.fill((255,255,255))
			#print img.get_colorkey()
			tv.images[k] = img,shape
		
		#colorkey all the tiles, seems to slow things down
		#"""
		#for n in (2,3):
		n = 0
		for t in tv.tiles:
			#t = tv.tiles[n]
			#print t
			if t != None and n in (0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f, 0x01,0x02,0x03,0x04,0x05,0x06,0x07):
				t.h = 64
				n += 1
				continue
				
			#print n
				
			if t != None:
				#print t.image
				#ck = (255,0,255)
				#HACK: make the colorkey almost black
				ck = (4,8,12)
				
				w = t.image.get_width()
				minh = 64
				maxh = 0
				for h in range(0,t.image.get_height()):
					c = t.image.get_at((w/2,h))
					if c[3] == 255:
						minh = min(h,minh)
						maxh = max(h+1,maxh)
						
				if n in (0x11,0x12,0x13,0x19,0x1c):
					minh = 0
					maxh = 64
				
				if maxh < minh: 
					t.image = None
					#print 'null image'

				else:				
					#print n,maxh-minh		
					img = pygame.Surface((t.image.get_width(),maxh-minh)).convert()
					img.fill(ck)
					img.blit(t.image,(0,-minh))
					img.set_colorkey(ck)
					img.set_alpha(255,RLEACCEL)
					#img.set_alpha(128)
					t.image = img
					t.h = maxh-minh
			n += 1
		#"""
		
			
	def paint(self,screen):
		tv = self.game.tv
		
		a = (128,0,0)
		b = (0,0,0)
		w,h = screen.get_width(),screen.get_height()
		inc = 20
		for y in range(0,h,inc):
			c = (b[0]*y+a[0]*(h-y))/h,(b[1]*y+a[1]*(h-y))/h,(b[2]*y+a[2]*(h-y))/h
			screen.fill(c,(0,y,w,inc))
			#screen.fill((0,0,255),(0,y,w,inc))
		
		
		
		tv.paint(screen)
		

		
		self.minimap(screen)
		
		self.stats(screen)
		
		pygame.display.flip()
		
		if self.getready == 0:
			self.getready = 1
			return states.Pause(self.game,(self.lvl[2],self.lvl[3],self))
		
	def stats(self,screen):
		x,y,s = 10,480-(20*4+10),1
		
		tv = self.game.tv
		g = self.game
		
		fg = (255,255,255)
		bg = (0,0,0)
		fnt = self.game.font_small
		
		text = "Level: %s"%self.lvl[1] #g.level
		img = fnt.render(text,1,bg);screen.blit(img,(x+s,y+s))
		img = fnt.render(text,1,fg);screen.blit(img,(x,y))
		y += 20
		
		text = "Time: %d:%02d"%(self.time/60,self.time%60)
		img = fnt.render(text,1,bg);screen.blit(img,(x+s,y+s))
		img = fnt.render(text,1,fg);screen.blit(img,(x,y))
		y += 20
		
		text = "Score: %05d"%g.score
		img = fnt.render(text,1,bg);screen.blit(img,(x+s,y+s))
		img = fnt.render(text,1,fg);screen.blit(img,(x,y))
		y += 20
		
		text = "Bombs: %d"%tv.bombs
		img = fnt.render(text,1,bg);screen.blit(img,(x+s,y+s))
		img = fnt.render(text,1,fg);screen.blit(img,(x,y))
		y += 20
		
		#print tv.pilars
		
	def minimap_draw(self):
		x,y = 0,0
		v = self.game.tv
		mlayer = v.mlayer
		
		w,h = len(mlayer[0]),len(mlayer)
		
		sz = 1
		
		img = pygame.Surface((w,h)).convert_alpha()
		img.fill((0,0,0,0))
		
		for ty in xrange(0,h):
			for tx in xrange(0,w):
				if mlayer[ty][tx]:
					img.fill((0,0,0,CALPHA),(tx-1,ty-1,3,3))
		
		for ty in xrange(0,h):
			for tx in xrange(0,w):
				if mlayer[ty][tx]: 
					c = mlayer[ty][tx]
					img.set_at((tx,ty),c)
					
				#x += sz
				
		self.minimap_image = img
				
		
		
	def minimap(self,screen):
		v = self.game.tv
		mlayer = v.mlayer
		w,h = len(mlayer[0]),len(mlayer)
		img_orig = self.minimap_image
		img = pygame.Surface((w,h)).convert_alpha()
		img.fill((0,0,0,0))
		img.blit(img_orig,(0,0))
		
		
		for s in v.sprites:
			tx,ty = s.rect.centerx/TW,s.rect.centery/TH
			img.fill((0,0,0,CALPHA),(tx-1,ty-1,3,3))
		
		for s in v.sprites:
			tx,ty = s.rect.centerx/TW,s.rect.centery/TH
			c = s.color
			if c != None:
				img.set_at((tx,ty),c)
				
		ww,hh = 120,120*h/w
		img = pygame.transform.scale(img,(ww,hh))
		screen.blit(img,(0,0))

		
		
	def loop(self):
		#player_event(self.game.tv,None)
		
		tv = self.game.tv

		#tv.peeking = 0
		keys = pygame.key.get_pressed()
		
		pspeed = 12
		
		#peeking
		if keys[K_LEFT]: 
			tv.view.x -= pspeed
			tv.peeking = 1
		if keys[K_RIGHT]: 
			tv.view.x += pspeed
			tv.peeking = 1
		if keys[K_UP]: 
			tv.view.y -= pspeed
			tv.peeking = 1
		if keys[K_DOWN]: 
			tv.view.y += pspeed
			tv.peeking = 1
		
		#walking	
		p = tv.player
		tx,ty = p.rect.centerx/TW,p.rect.centery/TH
		slayer = tv.slayer
		if keys[K_KP8]: #up
			nx,ny = tx-1,ty-1
			if not slayer[ny][nx]: p.path = [(nx,ny)]
			tv.peeking = 0
		if keys[K_KP6]: #right	
			nx,ny = tx+1,ty-1
			if not slayer[ny][nx]: p.path = [(nx,ny)]
			tv.peeking = 0
		if keys[K_KP2]: #down
			nx,ny = tx+1,ty+1
			if not slayer[ny][nx]: p.path = [(nx,ny)]
			tv.peeking = 0
		if keys[K_KP4]: #left
			nx,ny = tx-1,ty+1
			if not slayer[ny][nx]: p.path = [(nx,ny)]
			tv.peeking = 0
			
		if keys[K_KP9]: #up
			nx,ny = tx,ty-1
			if not slayer[ny][nx]: p.path = [(nx,ny)]
			tv.peeking = 0
		if keys[K_KP3]: #right	
			nx,ny = tx+1,ty
			if not slayer[ny][nx]: p.path = [(nx,ny)]
			tv.peeking = 0
		if keys[K_KP1]: #down
			nx,ny = tx,ty+1
			if not slayer[ny][nx]: p.path = [(nx,ny)]
			tv.peeking = 0
		if keys[K_KP7]: #left
			nx,ny = tx-1,ty
			if not slayer[ny][nx]: p.path = [(nx,ny)]
			tv.peeking = 0
		
		mx,my = pygame.mouse.get_pos()
		sw,sh = self.game.screen.get_width(),self.game.screen.get_height()
		border = 12
		if mx < border:
			tv.view.x -= pspeed
			tv.peeking = 1
		if my < border:
			tv.view.y -= pspeed
			tv.peeking = 1
		if mx >= sw-border:
			tv.view.x += pspeed
			tv.peeking = 1
		if my >= sh-border:
			tv.view.y += pspeed
			tv.peeking = 1
	
		
		
		
		#glayer = tv.glayer = [[0 for x in xrange(0,w)] for y in xrange(0,h)]
		
		
		for s in tv.sprites:
			if hasattr(s,'loop'): s.loop(tv,s)
		
		blayer = tv.blayer
		
		

		s = tv.player		
		tx,ty = s.rect.centerx/TW,s.rect.centery/TH
	
		if tv.pilars == 0 and tv.clayer[ty][tx] == 0x03: #code for window jumpin'
			tlayer = self.game.tv.tlayer
			w,h = len(tlayer[0]),len(tlayer)
			
			#self.game.score += self.game.tv.bombs * 125
			
			#self.game.score += min(0,(
			
			self.game.score = self.time * 25
			
			return Level_Win(self.game,None)
		
		

		
		"""
		for y in xrange(0,h):
			for x in xrange(0,w):
				if blayer[y][x] not in (0,4):
					if glayer[y][x] != 0: blayer[y][x] = 0x8
					else: blayer[y][x] = 0x1
		"""
		
		#check for reasons of death
		
		if s.dead == 1:
			self.game.score = 0
			return states.Pause(self.game,("Mission: Failure",states.Prompt(self.game,("Try Again? y/n",Level(self.game,None),states.Title(self.game,None)))))
		
		if self.frames % 24 == 23:
			self.time -= 1
			if self.time == 0:
				self.game.score = 0
				return states.Pause(self.game,("Mission: Failure","Out of time",states.Prompt(self.game,("Try Again? y/n",Level(self.game,None),states.Title(self.game,None)))))
		
		if self.game.tv.bombs == 0 and tv.pilars != 0 and tv.bomb == None:
			ok = 0
			for s in tv.sprites: 
				if s.type == 'explosion': ok = 1
				
			if not ok:
				self.game.score = 0
				return states.Pause(self.game,("Mission: Failure","No bombs left",states.Prompt(self.game,("Try Again? y/n",Level(self.game,None),states.Title(self.game,None)))))
		
		
		
	def update(self,screen):
		self.paint(screen)
		self.frames += 1
		#print self.frames
		#if self.frames == 100: return engine.Quit(self)
		
		
		
	def event(self,e):
		#print e
		tv = self.game.tv
		
		if e.type is KEYDOWN and e.key in (K_RETURN,K_SPACE,K_p):
			return states.Pause(self.game,("Pause",self))
	
		if e.type is KEYDOWN and e.key in (K_ESCAPE,K_q):
			#return states.Prompt(self.game,("Quit? y/n",states.Title(self.game,None),self))
			
			return states.Prompt(self.game,("Abort Mission? y/n",states.Prompt(self.game,("Try Again? y/n",Level(self.game,None),states.Title(self.game,None))),self))
			
		
		if not tv.player.alive: return
		
		drop = 0
		if e.type is MOUSEBUTTONDOWN and e.button == 3:
			drop = 1
		if e.type is KEYDOWN and e.key in (K_LCTRL,K_RCTRL):
			drop = 1
		
		if e.type is MOUSEBUTTONDOWN and e.button == 1:
			tv.peeking = 0
			pos = e.pos
			path = getpath(tv,tv.control,pos)
			if len(path):
				tv.control.path = path
				return
	
		elif drop:
			clayer = tv.clayer
			tlayer = tv.tlayer
			slayer = tv.slayer
			mlayer = tv.mlayer
			px,py = tv.control.rect.centerx/TW,tv.control.rect.centery/TH
			tx,ty = px,py
			
			if tv.bomb != None:
 				if (tx,ty) == tv.bomb:
					tv.bomb = None
					self.game.sfx['laybomb'].play()
					self.game.tv.bombs += 1
					tlayer[ty][tx] = 0
					mlayer[ty][tx] = None #(255,255,0)
					self.minimap_draw()
					return
				else:
					
					self.game.sfx['deton-bomb'].play()
					bomb_explode(tv,tv.bomb)
					tv.bomb = None
					return
				
			if self.game.tv.bombs == 0:
				return
				
			self.game.tv.bombs -= 1
			self.game.sfx['laybomb'].play()
					
			#pos = e.pos
				
			#tx,ty = getpos(tv,pos)
			px,py = tv.control.rect.centerx/TW,tv.control.rect.centery/TH
			tx,ty = px,py
			tlayer[ty][tx] = TILE_BOMB
			mlayer[ty][tx] = (255,255,0)
			self.minimap_draw()
			tv.bomb = (tx,ty)
			return
		"""			
		elif e.type is KEYDOWN and e.key == K_LEFT:
			tv.view.x -= 16
		elif e.type is KEYDOWN and e.key == K_RIGHT:
			tv.view.x += 16
		elif e.type is KEYDOWN and e.key == K_UP:
			tv.view.y -= 16
		elif e.type is KEYDOWN and e.key == K_DOWN:
			tv.view.y += 16
		"""
	
def drop_zlayer(tv):
	tlayer = tv.tlayer
	w,h = len(tlayer[0]),len(tlayer)
	zlayer = tv.zlayer
	zlayer2 = [[0 for x in xrange(0,w)] for y in xrange(0,h)]
	for y in xrange(1,h-1):
		for x in xrange(1,w-1):
			zlayer2[y][x] = min(1024,(zlayer[y][x-1]+zlayer[y-1][x]+zlayer[y][x+1]+zlayer[y+1][x])/3+min(1,zlayer[y][x]))
	tv.zlayer = zlayer2
			
class Level_Win(engine.State):
	def __init__(self,game,value):
		self.game = game
		self.frames = 0
		
	def init(self):
		#self.game.sfx['crumble'].play()
		if self.game.audio:
			pygame.mixer.music.load(os.path.join("data","sfx","crumble.ogg"))
			pygame.mixer.music.play()
		tv = self.game.tv
		tlayer = tv.tlayer
		w,h = len(tlayer[0]),len(tlayer)
		zlayer = tv.zlayer
		blayer = tv.blayer
		for y in xrange(0,h):
			for x in xrange(0,w):
				if blayer[y][x] == 0x1c: #base of explosion
					zlayer[y][x] = 1
				if blayer[y][x] == 0x1e: #grounds around castle
					blayer[y][x] = 0
					tlayer[y][x] = 0
		tv.sprites.remove(tv.player)
		
	def update(self,screen):
		screen.fill((0,0,0))
		drop_zlayer(self.game.tv)
		self.game.tv.paint(screen)
		pygame.display.flip()
		
		tv = self.game.tv
		tlayer = tv.tlayer
		w,h = len(tlayer[0]),len(tlayer)
		
		for s in tv.sprites:
			if s.type == 'explosion':
				s.loop(tv,s)
	
		if self.frames < 20:
			explosion_new(tv,(random.randrange(0,w),random.randrange(0,h)))
			#self.game.sfx['deton-bomb'].play()
		
		self.frames += 1
		if self.frames == 50:
			self.game.sfx['yeah-final'].play()
			l = len(levels.levels)
			if self.game.level == l-1: 
				return states.Win(self.game,None)
			else:
				l = self.game.level - 2
				#l = self.game.level + 1
				self.game.level += 1
				txt = "%05d"%self.game.score
				if l > 0:
					otxt = txt
					name = self.game.name
					score = self.game.score
					highs = self.game.highs
					n = highs["%s-%d"%(name,l)].submit(score,name)
					if n != None: txt = otxt + ", personal record!"
					n = highs["_overall-%d"%l].submit(score,name)
					if n != None: txt = otxt + ", overall record!"
					highs.save()
				return states.Pause(self.game,("Mission: Success",txt,Level(self.game,None)))