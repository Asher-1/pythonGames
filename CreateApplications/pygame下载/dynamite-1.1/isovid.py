from pgu import tilevid
import pygame

class Isovid(tilevid.Tilevid):
	def paint(self,screen):
		sw,sh = screen.get_width(),screen.get_height()
		
		tlayer = self.tlayer
		blayer = self.blayer
		zlayer = self.zlayer
		w,h = len(tlayer[0]),len(tlayer)
		
		tw = 32
		th = 32
		
		div = 8
		bot = 8
		todo_max = sh/div+bot
		todo = [[] for y in xrange(0,todo_max)]
		
		#adj = self.adj = pygame.Rect(-self.view.x,-self.view.y,0,0)
		for s in self.sprites:
			x,y = self.iso2view((s.rect.centerx,s.rect.centery))
			tx,ty = s.rect.centerx/tw,s.rect.centery/th
			z = 0
			if ty >= 0 and ty < h and tx >= 0 and tx < w:
				z = zlayer[ty][tx]
			
			
			#s.irect.x, s.irect.y = x - s.shape.centerx, y -s.shape.centery + z
			
			nx,ny = x - s.shape.centerx, y -s.shape.centery + z
			
			s.dx,s.dy = nx-s.irect.x,ny-s.irect.y
			s.irect.x,s.irect.y = nx,ny
			
		self.view.w,self.view.h = sw,sh
		view = self.view
		
		pr = self.player.irect
		p = self.player
		
		moveby = 12
		if not hasattr(self,'peeking'): 
			self.peeking = -1
			moveby = 16384 #big number, first frame, probably...
		if self.peeking < 1:
			#dx,dy = p.dd
			#print p.dd
			#f = p.facing
			dx,dy = p.dx,p.dy
			#print dx,dy
			if dx < 0 or self.peeking==-1:
				self.view.left = min(self.view.left,max(self.view.left-moveby,pr.left-200))
			if dy < 0 or self.peeking==-1:
				self.view.top = min(self.view.top,max(self.view.top-moveby,pr.top-150))
			if dx > 0 or self.peeking==-1:
				self.view.right = max(self.view.right,min(self.view.right+moveby,pr.right+200))
			if dy > 0 or self.peeking==-1:
				self.view.bottom = max(self.view.bottom,min(self.view.bottom+moveby,pr.bottom+150))
		if self.peeking==-1: self.peeking=0
		
		#self.view.x,self.view.y = 0,0
		adj = self.adj = pygame.Rect(-self.view.x,-self.view.y,0,0)
		
		for s in self.sprites:
			x,y = self.iso2view((s.rect.centerx,s.rect.centery))
			v = (y+adj.y)/div - 1
			if v >= 0 and v < todo_max:
				todo[v].append((s.image,s.irect))
				
		w,h = len(tlayer[0]),len(tlayer)
		tiles = self.tiles
		
		ox,oy = self.screen2tile((0,0))
		sx,sy = self.iso2view((ox*tw,oy*th))
		dx,dy = sx - self.view.x,sy - self.view.y
		
		for i2 in xrange(-bot,self.view.h/8+bot):
			tx,ty = ox + i2/2 + i2%2,oy + i2/2
			x,y = (i2%2)*16 + dx,i2*8 + dy
			
			#to adjust for the -1 in i1
			x,tx,ty = x-32,tx-1,ty+1
			for i1 in xrange(-1,self.view.w/32+1):
				if ty >= 0 and ty < h and tx >= 0 and tx < w:
					z = zlayer[ty][tx]
					n = blayer[ty][tx]
					if n != 0:
						t = tiles[n]
						if t != None and t.image != None:
							screen.blit(t.image,(x-16,y+z))
							#print t.image.get_height()
							pass
					n = tlayer[ty][tx]
					if n != 0:
						t = tiles[n]
						if t != None and t.image != None:
							screen.blit(t.image,(x-16,y-(t.h-16)+z))
							pass
			
				tx += 1
				ty -= 1
				x += 32
			for img,irect in todo[y/div]:
				screen.blit(img,(irect.x+adj.x,irect.y+adj.y))

		return	
		"""
		for ty in xrange(0,h):
			x,y = sw/2 - ty*tw/2,0 + ty*th/4
			bl = blayer[ty]
			tl = tlayer[ty]
			zl = zlayer[ty]
			for tx in xrange(0,w):
				n = bl[tx]
				if n != 0:
					t = tiles[n]
					if t != None and t.image != None:
						ww,hh = 32,64
						irect = pygame.Rect(x,y+zl[tx],ww,hh)
						if irect.colliderect(view):
							todo[y/div].append((t.image,irect))
				
				n = tl[tx]
				if n != 0:
					t = tiles[n]
					if t != None and t.image != None:
						ww = 32
						hh = t.h
						irect = pygame.Rect(x,y-hh+16+zl[tx],ww,hh)
						if irect.colliderect(view):
							todo[y/div].append((t.image,irect))
				
				x += tw/2
				y += th/4
		"""		
		
		#blits = 0
		for ys in todo:
			for img,irect in ys:
				screen.blit(img,(irect.x+adj.x,irect.y+adj.y))
		
	def iso2view(tv,pos):
		x,y = pos
		
		TW,TH = 32,32
		
		tlayer = tv.tlayer
		w,h = len(tlayer[0]),len(tlayer)
		
		nx,ny = h*TW + x - y, 0 + x + y
		
		return nx/2,ny/4

	def view2iso(tv,pos):
		
		x,y = pos
		
		tlayer = tv.tlayer
		w,h = len(tlayer[0]),len(tlayer)
		
		TW,TH = 32,32
		
		x -= TW/2 * h
		y *= 2
		
		nx = (x+y) / 2
		ny = y-nx
	
		nx = nx*2
		ny = ny*2
		
		return nx,ny
	
	def screen2tile(tv,dest):
		x,y = dest
		x += tv.view.x
		y += tv.view.y
		
		x,y = tv.view2iso((x,y))
		TW,TH = 32,32
		
		return x/TW,y/TH
	

	def tga_load_level(self,fname,bg=0):
		"""Load a TGA level.  
		
		g		-- a Tilevid instance
		fname	-- tga image to load
		bg		-- set to 1 if you wish to load the background layer
		"""
		
		sp = 5
		db = 0x1e
		
		img = pygame.image.load(fname)
		w,h = img.get_width(),img.get_height()
		self.resize((w+sp*2,h+sp*2),bg)
		for y in range(0,h+sp*2):
			for x in range(0,w+sp*2):
				self.blayer[y][x] = db
				
		for y in range(0,h):
			for x in range(0,w):
				t,b,c,_a = img.get_at((x,y))
				self.tlayer[y+sp][x+sp] = t
				#if bg: self.blayer[y][x] = b
				if b != 0: self.blayer[y+sp][x+sp] = b
				self.clayer[y+sp][x+sp] = c
