"""a basic gui system.  reference documentation incomplete.  please see tutorials."""
import os.path, re

import pygame
from pygame.locals import *

import layout

pygame.font.init()

ENTER = USEREVENT + 0
EXIT = USEREVENT + 1
BLUR = USEREVENT + 2
FOCUS = USEREVENT + 3
CLICK = USEREVENT + 4
CHANGE = USEREVENT + 5
OPEN = USEREVENT + 6
CLOSE = USEREVENT + 7
INIT = 'init'

class NOATTR: pass

class Object:
	def __init__(self):
		self.connects = {}
		self.__class__
		
	def connect(self,code,fnc,value):
		self.connects[code] = {'fnc':fnc,'value':value}
		
	def send(self,code,event=None):
		if code in self.connects:
			con = self.connects[code]
			con['fnc'](con['value'])
			
	def _event(self,e):
		self.send(e.type,e)
		self.event(e)
		
	def event(self,e): pass
	

def action_open(value):
	value.setdefault('x',None)
	value.setdefault('y',None)
	value['container'].open(value['window'],value['x'],value['y'])
	
def action_setvalue(value):
	a,b = value
	b.value = a.value
	
def action_quit(value):
	value.quit()
	
def action_exec(value):
	exec(value['script'],globals(),value['dict'])
	
class _theme:
	def __init__(self):
		self.config = {}
		self.dict = {}
		self._loaded = 0
		self.cache = {}
		
	def load(self,ds):
		if self._loaded: return 
		self._loaded = 1
		if not isinstance(ds, list):
			ds = [ds]
		for d in ds:
			self._load(d)

	def _load(self, name):
		#theme_dir = themes[name]
		
		#try to load the local dir, or absolute path
		dnames = [name]
		
		#if the package isn't installed and people are just
		#trying out the scripts or examples
		dnames.append(os.path.join(os.path.dirname(__file__),"..","data","themes",name))
		
		#if the package is installed, and the package is installed
		#in /usr/lib/python2.3/site-packages/pgu/
		#or c:\python23\lib\site-packages\pgu\
		#the data is in ... lib/../share/ ...
		dnames.append(os.path.join(os.path.dirname(__file__),"..","..","..","share","pgu","themes",name))
		dnames.append(os.path.join(os.path.dirname(__file__),"..","..","..","..","share","pgu","themes",name))
		
		for dname in dnames:
			if os.path.isdir(dname): break
		if not os.path.isdir(dname): 
			raise 'could not find theme '+name
			
		fname = os.path.join(dname, "config.txt")
		try:
			f = open(fname)
			for line in f.readlines():
				vals = line.strip().split()
				if len(vals) < 3: continue
				cls = vals[0]
				del vals[0]
				pcls = ""
				if cls.find(":")>=0:
					cls,pcls = cls.split(":")
				attr = vals[0]
				del vals[0]
				self.config[cls+":"+pcls+" "+attr] = (dname, vals)
		finally:
			f.close()
	
	is_image = re.compile('\.(gif|jpg|bmp|png|tga)$', re.I)
	def _get(self,key):
		if not key in self.config: return
		if key in self.dict: return self.dict[key]
		dvals = self.config[key]
		dname, vals = dvals
		#theme_dir = themes[name]
		v0 = vals[0]
		if v0[0] == '#':
			v = pygame.color.Color(v0)
		elif v0.endswith(".ttf") or v0.endswith(".TTF"):
			v = pygame.font.Font(os.path.join(dname, v0),int(vals[1]))
		elif self.is_image.search(v0) is not None:
			v = pygame.image.load(os.path.join(dname, v0))
		else:
			try: v = int(v0)
			except: v = pygame.font.SysFont(v0, int(vals[1]))
		self.dict[key] = v
		return v	
		
				
	def get(self,cls,pcls,attr):
		if not self._loaded: self.load("default")
		
		o = cls+":"+pcls+" "+attr
		
		#if not hasattr(self,'_count'):
		#	self._count = {}
		#if o not in self._count: self._count[o] = 0
		#self._count[o] += 1
		#print o,self._count[o]
		
		if o in self.cache: 
			return self.cache[o]
		
		v = self._get(cls+":"+pcls+" "+attr)
		if v: 
			self.cache[o] = v
			return v
		
		pcls = ""
		v = self._get(cls+":"+pcls+" "+attr)
		if v: 
			self.cache[o] = v
			return v
		
		cls = "default"
		v = self._get(cls+":"+pcls+" "+attr)
		if v: 
			self.cache[o] = v
			return v
		
		v = 0
		self.cache[o] = v
		return v
		

theme = _theme()

def _list_themes(dir):
	d = {}
	for entry in os.listdir(dir):
		if os.path.exists(os.path.join(dir, entry, 'config.txt')):
			d[entry] = os.path.join(dir, entry)
	return d



class _style:
	def __init__(self,o):
		self.obj = o
		self._cache = 0
				
	def __getattr__(self,k):
		v = theme.get(self.obj.cls, self.obj.pcls, k)
		#print 'style.get:%s:%s %s = %r'%(self.obj.cls, self.obj.pcls, k, v)
		if self._cache: self.__dict__[k] = v
		return v
		
	def cache(self,v):
		if v: self._cache += 1
		else: self._cache -= 1

	def __setattr__(self,k,v):
		self.__dict__[k] = v
	

class Group(Object):
	def __init__(self,name=None,value=None):
		Object.__init__(self)
		self.name = name
		if hasattr(Form,'form') and Form.form != None: 
			Form.form.add(self)
			self.form = Form.form
		self.value = value
		self.widgets = []
		
	def add(self,w):
		self.widgets.append(w)
	
	def __setattr__(self,k,v):
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k] = v
		if k == 'value' and _v != NOATTR and _v != v:
			self._change()
			
	def _change(self):
		self.send(CHANGE)
		for w in self.widgets:
			w.repaint()


class Widget(Object):
	def __init__(self,**params): 
		Object.__init__(self) 
		self.rect = pygame.Rect(params.get('x',0),params.get('y',0),params.get('width',0),params.get('height',0))
		self.style = _style(self)
		for att in ('align','valign','x','y','width','height','color','font','background'):
			if att in params: setattr(self.style,att,params[att])
		for k,v in params.get('style',{}).items():
			setattr(self.style,k,v)
			if k in ('border','margin','padding'):
				for kk in ('top','bottom','left','right'):
					setattr(self.style,'%s_%s'%(k,kk),v)
		
		self.cls = "default"
		if 'cls' in params: self.cls = params['cls']
		if 'name' in params:	
			self.name = params['name']
			if hasattr(Form,'form') and Form.form != None: 
				Form.form.add(self)
				self.form = Form.form
		if 'value' in params: self.value = params['value']
		self.pcls = ""
		
		if type(self.style.background) != int:
			self.background = Background(self)	

			

	#def hide(self): 
	#	if getattr(self,'container',None) != None: self.container.hide(self)
	#def show(self): 
	#	if getattr(self,'container',None) != None: self.container.show(self)

	def focus(self):
		if getattr(self,'container',None) != None: self.container.focus(self)
	def blur(self): 
		if getattr(self,'container',None) != None: self.container.blur(self)
	def close(self): 
		if getattr(self,'container',None) != None: self.container.close(self)
	def resize(self,width=None,height=None):
		"""resize this widget and any subwidgets"""
		self.rect.w = self.style.width
		self.rect.h = self.style.height
	def update(self,s): pass
	def paint(self,s): pass
	def repaint(self): 
		if getattr(self,'container',None) != None: self.container.repaint(self)
	def repaintall(self):
		if getattr(self,'container',None) != None: self.container.repaintall()
	def reupdate(self): 
		if getattr(self,'container',None) != None: self.container.reupdate(self)
	def next(self): 
		if getattr(self,'container',None) != None: self.container.next(self)
	def previous(self): 
		if getattr(self,'container',None) != None: self.container.previous(self)
	def open(self):
		if getattr(self,'container',None) != None: self.container.open(self)
	def getwidths(self):
		"""return the minimum and maximum widths of this widget
		
		this method may only be called after resize
		"""
		return self.rect.w,self.rect.w
		
	def getspacing(self):
		"""return the top, right, bottom, left spacing around the widget"""
		w = self
		if not hasattr(self,'_spacing'): #HACK: assume spacing doesn't change re pcls
			s = w.style
			s.cache(1)
			xt = s.margin_top+s.border_top+s.padding_top
			xr = s.padding_right+s.border_right+s.margin_right
			xb = s.padding_bottom+s.border_bottom+s.margin_bottom
			xl = s.margin_left+s.border_left+s.padding_left
			s.cache(0)
			self._spacing = xt,xr,xb,xl
		return self._spacing

	def _resize(self,width=None,height=None):
		"""calculate .rect_padding, .rect_border, .rect_margin
		
		width -- a required width
		height -- a required height
		
		the widget will be centered within its width, height according to
		style.align and style.valign.  this method may only be called after resize.
		"""
		w = self
		s = w.style
		
		s.cache(1)
		pt,pr,pb,pl = s.padding_top,s.padding_right,s.padding_bottom,s.padding_left
		bt,br,bb,bl = s.border_top,s.border_right,s.border_bottom,s.border_left
		mt,mr,mb,ml = s.margin_top,s.margin_right,s.margin_bottom,s.margin_left
		s.cache(0)
		
		xt = pt+bt+mt
		xr = pr+br+mr
		xb = pb+bb+mb
		xl = pl+bl+ml
		
		w.rect = pygame.Rect(w.style.x + xl, w.style.y + xt, w.rect.w, w.rect.h)
		
		if width == None: width = w.rect.w
		if height == None: height = w.rect.h
		#width,height = w.rect.w,w.rect.h
		r = pygame.Rect(w.rect.x,w.rect.y,width,height)
		
		w.rect_padding = pygame.Rect(r.x-pl,r.y-pt,r.w+pl+pr,r.h+pt+pb)
		r = w.rect_padding
		w.rect_border = pygame.Rect(r.x-bl,r.y-bt,r.w+bl+br,r.h+bt+bb)
		r = w.rect_border
		w.rect_margin = pygame.Rect(r.x-ml,r.y-mt,r.w+ml+mr,r.h+mt+mb)
		
		#align it within it's zone of power.	
		dx = width-w.rect.w
		dy = height-w.rect.h
		w.rect.x += (w.style.align+1)*dx/2
		w.rect.y += (w.style.valign+1)*dy/2

def render_box(s,box,r):
	x,y,w,h=r.x,r.y,r.w,r.h
	ww,hh=box.get_width()/3,box.get_height()/3
	xx,yy=x+w,y+h
	src = pygame.rect.Rect(0,0,ww,hh)
	dest = pygame.rect.Rect(0,0,ww,hh)
	
	
	s.set_clip(pygame.Rect(x+ww,y+hh,w-ww*2,h-hh*2))
	src.x,src.y = ww,hh
	for dest.y in xrange(y+hh,yy-hh,hh): 
		for dest.x in xrange(x+ww,xx-ww,ww): s.blit(box,dest,src)
	
	s.set_clip(pygame.Rect(x+ww,y,w-ww*3,hh))
	src.x,src.y,dest.y = ww,0,y
	for dest.x in xrange(x+ww,xx-ww*2,ww): s.blit(box,dest,src)
	dest.x = xx-ww*2
	s.set_clip(pygame.Rect(x+ww,y,w-ww*2,hh))
	s.blit(box,dest,src)
	
	s.set_clip(pygame.Rect(x+ww,yy-hh,w-ww*3,hh))
	src.x,src.y,dest.y = ww,hh*2,y+h-hh
	for dest.x in xrange(x+ww,xx-ww*2,ww): s.blit(box,dest,src)
	dest.x = xx-ww*2
	s.set_clip(pygame.Rect(x+ww,yy-hh,w-ww*2,hh))
	s.blit(box,dest,src)

	s.set_clip(pygame.Rect(x,y+hh,xx,h-hh*3))
	src.y,src.x,dest.x = hh,0,x
	for dest.y in xrange(y+hh,yy-hh*2,hh): s.blit(box,dest,src)
	dest.y = yy-hh*2
	s.set_clip(pygame.Rect(x,y+hh,xx,h-hh*2))
	s.blit(box,dest,src)

	s.set_clip(pygame.Rect(xx-ww,y+hh,xx,h-hh*3))
	src.y,src.x,dest.x=hh,ww*2,x+w-ww
	for dest.y in xrange(y+hh,yy-hh*2,hh): s.blit(box,dest,src)
	dest.y = yy-hh*2
	s.set_clip(pygame.Rect(xx-ww,y+hh,xx,h-hh*2))
	s.blit(box,dest,src)
	
	s.set_clip()
	src.x,src.y,dest.x,dest.y = 0,0,x,y
	s.blit(box,dest,src)
	
	src.x,src.y,dest.x,dest.y = ww*2,0,x+w-ww,y
	s.blit(box,dest,src)
	
	src.x,src.y,dest.x,dest.y = 0,hh*2,x,y+h-hh
	s.blit(box,dest,src)
	
	src.x,src.y,dest.x,dest.y = ww*2,hh*2,x+w-ww,y+h-hh
	s.blit(box,dest,src)
	
def _subsurface(s,r):
	r = pygame.Rect(r)
	if r.x < 0 or r.y < 0:
		raise "_subsurface: %d %d %s"%(s.get_width(),s.get_height(),r)
	w,h = s.get_width(),s.get_height()
	if r.right > w:
		r.w -= r.right-w
	if r.bottom > h:
		r.h -= r.bottom-h
	return s.subsurface(r)
	

class Container(Widget):
	def __init__(self,**params):
		Widget.__init__(self,**params)
		self.myfocus = 0
		self.mywindow = 0
		self.myhover = 0
		#self.background = 0
		self.widgets = []
		self.windows = []
		self.toupdate = {}
		self.topaint = {}
		
		
	def update(self,s):
		updates = []
		
		if self.myfocus: self.toupdate[self.myfocus] = self.myfocus
		
		for w in self.topaint:
			if w == self.mywindow:
				continue
			else:
				if hasattr(w,'background'):
					w.background.paint(_subsurface(s,w.rect_border))
				self._border(w,_subsurface(s,w.rect_border))
				w.paint(_subsurface(s,w.rect))
				updates.append(pygame.rect.Rect(w.rect_border))

		for w in self.toupdate:
			if w == self.mywindow:
				continue
			else:			
				us = w.update(_subsurface(s,w.rect))
			if us != None:
				for u in us:
					updates.append(pygame.rect.Rect(u.x + w.rect.x,u.y+w.rect.y,u.w,u.h))
		
		for w in self.topaint:
			if w == self.mywindow:
				w.paint(self.top_surface(s,w))
				updates.append(pygame.rect.Rect(w.rect))
			else:
				continue 

		for w in self.toupdate:
			if w == self.mywindow:
				us = w.update(self.top_surface(s,w))
			else:			
				continue 
			if us != None:
				for u in us:
					updates.append(pygame.rect.Rect(u.x + w.rect.x,u.y+w.rect.y,u.w,u.h))
		
		self.topaint = {}
		self.toupdate = {}
		
		return updates
			
	def repaint(self,w=None):
		if w == None:
			return Widget.repaint(self)
		self.topaint[w] = w
		self.reupdate()
	
	def reupdate(self,w=None):
		if w == None:
			return Widget.reupdate(self)
		self.toupdate[w] = w
		self.reupdate()

	def paint(self,s):
		self.toupdate = {}
		self.topaint = {}
		
		for w in self.widgets:
			if hasattr(w,'background'):
				w.background.paint(_subsurface(s,w.rect_border))
			self._border(w,_subsurface(s,w.rect_border))
			try:
				w.paint(_subsurface(s,w.rect))
			except: 
				print 'container.paint(): %s not in %s'%(w.__class__.__name__,self.__class__.__name__)
				print s.get_width(),s.get_height(),w.rect
			
		for w in self.windows:
			if hasattr(w,'background'):
				w.background.paint(_subsurface(s,w.rect_border))
			self._border(w,_subsurface(s,w.rect_border))
			w.paint(self.top_surface(s,w))
			
	def _border(self,w,s):
		style = w.style
		style.cache(1)
		
		c = (0,0,0)
		if style.border_color != 0: c = style.border_color
		w,h = s.get_width(),s.get_height()
		
		s.fill(c,(0,0,w,style.border_top))
		s.fill(c,(0,h-style.border_bottom,w,style.border_bottom))
		s.fill(c,(0,0,style.border_left,h))
		s.fill(c,(w-style.border_right,0,style.border_right,h))
		
		style.cache(0)
			
	def top_surface(self,s,w):
		x,y = s.get_abs_offset()
		s = s.get_abs_parent()
		return _subsurface(s,(x+w.rect.x,y+w.rect.y,w.rect.w,w.rect.h))
	
	def event(self,e):
		if self.mywindow and e.type is MOUSEBUTTONDOWN:
			w = self.mywindow
			if self.myfocus == w:
				if not w.rect.collidepoint(e.pos): self.blur(w)
			if not self.myfocus:
				if w.rect.collidepoint(e.pos): self.focus(w)
		
		if not self.mywindow:
			if e.type is FOCUS:
				self.first()
			elif e.type is EXIT:
				if self.myhover: self.exit(self.myhover)
			elif e.type is BLUR:
				if self.myfocus: self.blur(self.myfocus)
			elif e.type is MOUSEBUTTONDOWN:
				h = 0
				for w in self.widgets:
					if w.rect_border.collidepoint(e.pos):
						h = w
						if self.myfocus != w: self.focus(w)
				if not h and self.myfocus:
					self.blur(self.myfocus)
			elif e.type is MOUSEMOTION:
				h = 0
				for w in self.widgets:
					if w.rect_border.collidepoint(e.pos):
						h = w
						if self.myhover != w: self.enter(w)
				if not h and self.myhover:
					self.exit(self.myhover)
				w = self.myhover
				
				if w and w != self.myfocus:
					sub = pygame.event.Event(e.type,{
						'buttons':e.buttons,
						'pos':(e.pos[0]-w.rect.x,e.pos[1]-w.rect.y),
						'rel':e.rel})
					w._event(sub)

		w = self.myfocus
		if w:
			sub = e
			
			if e.type is MOUSEBUTTONUP or e.type is MOUSEBUTTONDOWN:
				sub = pygame.event.Event(e.type,{
					'button':e.button,
					'pos':(e.pos[0]-w.rect.x,e.pos[1]-w.rect.y)})
				w._event(sub)
			elif e.type is CLICK and self.myhover == w:
				sub = pygame.event.Event(e.type,{
					'button':e.button,
					'pos':(e.pos[0]-w.rect.x,e.pos[1]-w.rect.y)})
				w._event(sub)
			elif e.type is MOUSEMOTION:
				sub = pygame.event.Event(e.type,{
					'buttons':e.buttons,
					'pos':(e.pos[0]-w.rect.x,e.pos[1]-w.rect.y),
					'rel':e.rel})
				w._event(sub)
			else:
				w._event(sub)

	def remove(self,w):
		self.widgets.remove(w)
		self.repaint()
		
	def add(self,w,x,y):
		w.style.x = x
		w.style.y = y 
		w.container = self
		self.widgets.append(w)

	def open(self,w=None,x=None,y=None):
		if w == None:
			if (not hasattr(self,'container') or self.container == None) and self != App.app:
				self.container = App.app
			return Widget.open(self)

		if self.container != None:
			if x != None: return self.container.open(w,self.rect.x+x,self.rect.y+y)
			return self.container.open(w)
			
		w.container = self
		
		w.rect.w,w.rect.h = 0,0
		w.resize()
	
		if x == None or y == None: #auto center the window
			w.style.x,w.style.y = 0,0
			w._resize(self.rect.w,self.rect.h)
		else: #show it where we want it
			w.style.x = x
			w.style.y = y
			w._resize()
		
		#print self.rect	
		#print w.rect

		self.windows.append(w)
		self.mywindow = w
		self.focus(w)
		self.repaint(w)
		w.send(OPEN)

	def close(self,w=None):
		if w == None:
			return Widget.close(self)
			
		if self.container != None: #make sure we're in the App
			return self.container.close(w)
		
		if self.myfocus == w: self.blur(w)
		
		if w not in self.windows: return #no need to remove it twice! happens.
		
		self.windows.remove(w)
		
		self.mywindow = 0
		l = len(self.windows)
		if l:
			self.mywindow = self.windows[l-1]
			self.focus(self.mywindow)
		
		if not self.mywindow:
			self.myfocus = self.widget #HACK: should be done fancier, i think..
			if not self.myhover:
				self.enter(self.widget)
			
		self.repaintall()
		w.send(CLOSE)
		
	#def hide(self,w):
	#	w.style.hidden = 1
	#	self.repaint()
	
	#def show(self,w):
	#	w.style.hidden = 0
	#	self.repaint()
		
	def focus(self,w=None):
		if w == None:
			return Widget.focus(self)
		if self.myfocus: self.blur(self.myfocus)
		if self.myhover != w: self.enter(w)
		self.myfocus = w
		w._event(pygame.event.Event(FOCUS))
	
	def blur(self,w=None):
		if w == None:
			return Widget.blur(self)
		if self.myfocus and self.myfocus == w:
			if self.myhover == w: self.exit(w)
			self.myfocus = 0
			w._event(pygame.event.Event(BLUR))
			
	def enter(self,w):
		if self.myhover: self.exit(self.myhover)
		self.myhover = w
		w._event(pygame.event.Event(ENTER))

	def exit(self,w):
		if self.myhover and self.myhover == w:
			self.myhover = 0
			w._event(pygame.event.Event(EXIT))	
			
	def first(self):
		for w in self.widgets:
			if not w.style.disabled:
				self.focus(w)
				return
		if self.container: self.container.next(self)
			
	def next(self,w):
		i = self.widgets.index(w)
		l = len(self.widgets)
		for w in self.widgets[i+1:l]:
			if not w.style.disabled:
				self.focus(w)
				return
		if self.container: self.container.next(self)
		
	def previous(self,w):
		print 'Container.previous: n/a'
		
	def resize(self,width=None,height=None):
		r = self.rect
		r.w,r.h = 0,0
		if self.style.width: r.w = self.style.width
		if self.style.height: r.h = self.style.height
		
		for w in self.widgets:
			w.rect.w,w.rect.h = 0,0
			w.rect.x,w.rect.y = self.style.x,self.style.y
			w.resize()
			w._resize()
			
			r.w = max(r.w,w.rect_margin.right)
			r.h = max(r.h,w.rect_margin.bottom)

class App(Container):
	def __init__(self,**params):
		Container.__init__(self,**params)
		self._quit = 0
		self.widget = None
		self._repaint = 0
		self.screen = None
		self.container = None
	
	def init(self,widget = None,screen = None):
		if widget != None: self.widget = widget
		
		w = self.widget
		wsize = 0
		
		#5 cases
		
		#input screen is already set use its size
		if screen:
			#print 'input screen'
			self.screen = screen
			width,height = screen.get_width(),screen.get_height()
		
		#display.screen
		elif pygame.display.get_surface() != None:
			#print 'existing screen'
			screen = pygame.display.get_surface()
			self.screen = screen
			width,height = screen.get_width(),screen.get_height()
		
		#app has width,height
		elif self.style.width != 0 and self.style.height != 0:
			#print 'app style'
			screen = pygame.display.set_mode((self.style.width,self.style.height),SWSURFACE)
			self.screen = screen
			width,height = screen.get_width(),screen.get_height()
		
		#widget has width,height, or its own size..
		else:
			#print 'widget'
			wsize = 1
			w.resize()
			w._resize()
			width,height = w.rect_margin.w,w.rect_margin.h
			screen = pygame.display.set_mode((width,height),SWSURFACE)
			self.screen = screen
	
		#use screen to set up size of this widget
		self.style.width,height = width,height
		self.rect.w,self.rect.h = width,height
		self.rect.x,self.rect.y = 0,0
		
		xt,xr,xb,xl = w.getspacing()
		xw = xl + xr
		xh = xt + xb
		w.style.width = width-xw
		w.style.height = height-xh
		
		#print w.style.width,w.style.height
		
		if not wsize: 
			w.resize()
			w._resize()
		#print w.rect_margin
		
		self.widgets = []
		self.widgets.append(w)
		w.container = self
		self.focus(w)

		#print 'app.init()',width,height

		pygame.key.set_repeat(500,30)
		
		self._repaint = 1
		self._quit = 0
		
		App.app = self
		self.send(INIT)

		
	def event(self,e):
		App.app = self
		#NOTE: might want to deal with ACTIVEEVENT in the future.
		self.send(e.type,e)
		Container.event(self,e)
		if e.type is MOUSEBUTTONUP:
			sub = pygame.event.Event(CLICK,{
				'button':e.button,
				'pos':e.pos})
			self.send(sub.type,sub)
			Container.event(self,sub)
		
	def loop(self):
		App.app = self
		s = self.screen
		for e in pygame.event.get():
			self.event(e)
		if self._repaint:
			if hasattr(self,'background'):
				self.background.paint(s)
			self.paint(s)
			pygame.display.flip()
			self._repaint = 0
		else:
			us = self.update(s)
			#import random
			#c = (random.randrange(0,255),0,0)
			#for u in us: s.fill(c,u)
			pygame.display.update(us)
			
	def run(self,widget=None,screen=None):
		self.init(widget,screen)
		while not self._quit:
			self.loop()
			pygame.time.wait(10)

	def reupdate(self,w=None): pass
	def repaint(self,w=None): self._repaint = 1
	def repaintall(self): self._repaint = 1
	
	def quit(self,value=None): self._quit = 1

	
def _table_div(a,b):
	v,r = a/b, a%b
	if r != 0: v += 1
	return v

def _table_div_down(a,b):
	v,r = a/b, a%b
	#if r != 0: v += 1
	#if r == 0: v = max(0,v-1)
	return v

class Box(Container):
	def __init__(self,widget,**params):
		Container.__init__(self,**params)
		self.widget = widget
		self.add(widget,0,0)
		
		#self.style.disabled = self.widget.style.disabled #HACK
		
	def resize(self,width=None,height=None):
		w = self.widget
		
		xt,xr,xb,xl = w.getspacing()
		xw = xl + xr
		xh = xt + xb
		
		if width != None: width -= xw
		if height != None: height -= xh
		
		#print w.__class__.__name__
		#print width,height
		w.resize(width,height)
		#print w.rect
		#print w.style.width
		w._resize()
		self.rect.w,self.rect.h = w.rect_margin.w,w.rect_margin.h
		
	def getwidths(self):
		w = self.widget
		
		_min,_max = w.getwidths()
		
		xt,xr,xb,xl = w.getspacing()
		xw = xl + xr
		xh = xt + xb
			
		return _min+xw,_max+xw
		
	
class Table(Container):
	def __init__(self,**params):
		params.setdefault('cls','table')
		Container.__init__(self,**params)
		self._col = 0
		self._row = -1
			
	def add(self,w,col=None,row=None,colspan=None,rowspan=None,align=None,valign=None,width=None,height=None):
		if self._row == -1: self.tr() #auto tr()
		
		w.style.cell_width = width
		w.style.cell_height = height
		if col == None: col = self._col
		if row == None: row = self._row
		w.style.col = col
		w.style.row = row
		if colspan is not None: w.style.colspan = colspan
		if w.style.colspan == 0: w.style.colspan = 1
		if rowspan is not None: w.style.rowspan = rowspan
		if w.style.rowspan == 0: w.style.rowspan = 1
		if align is not None: w.style.align = align
		if valign is not None: w.style.valign = valign
		w.container = self
		self.widgets.append(w)
		self._col += w.style.colspan
		
	def tr(self):
		self._col,self._row = 0,self._row+1
		
	def td(self,w,col=None,row=None,colspan=None,rowspan=None,align=None,valign=None,width=None,height=None,**params):
		self.add(Box(w,**params),col,row,colspan,rowspan,align,valign,width,height)
		
	def resize(self,width=None,height=None):
		#calculate the minimum, maximum size for the table	
		min_w = 0
		min_h = 0
		max_w = width
		max_h = height
		if self.style.width: min_w,max_w = self.style.width,self.style.width
		if self.style.height: min_h,max_h = self.style.height,self.style.height
		
		#print min_w,max_w
		
		#calculate the number of rows, columns
		nrows,ncols = 0,0
		for w in self.widgets:
			nrows = max(nrows,w.style.row+w.style.rowspan)
			ncols = max(ncols,w.style.col+w.style.colspan)
		rows = [0 for i in xrange(0,nrows)]
		cols_min = [0 for i in xrange(0,ncols)]
		cols_max = [0 for i in xrange(0,ncols)]

		#Container.resize(self) #defines background, rects
		for w in self.widgets:
			w.rect.w,w.rect.h = 0,0
			w.resize()

		#we'll do this using the plan outlined here:
		#http://www.w3.org/TR/CSS21/tables.html#auto-table-layout

		#step 1: calc min/max width of all widgets		
		for w in self.widgets:
			_min,_max = w.getwidths()
			
			xt,xl,xb,xr = w.getspacing()
			xw = xl + xr

			w._width_min = max(_min+xw,w.style.cell_width)
			w._width_max = max(_max+xw,w.style.cell_width)
		
		#step 2: calc min/max width for each column (colspan=1)
		for w in self.widgets:
			if w.style.colspan > 1: continue
			
			i = w.style.col
			cols_max[i] = max(cols_max[i],w._width_max)
			cols_min[i] = max(cols_min[i],w._width_min)
			
		#step 3: calc min/max width for each column (colspan>1)
		for w in self.widgets:
			if w.style.colspan == 1: continue
			_min = 0
			_max = 0
			for i in xrange(w.style.col,w.style.col+w.style.colspan):
				_min += cols_min[i]
				_max += cols_max[i]
			add = _table_div(max(0,w._width_max-_max) , w.style.colspan)
			for i in xrange(w.style.col,w.style.col+w.style.colspan):
				cols_max[i] += add
			add = _table_div(max(0,w._width_min-_min) , w.style.colspan)
			for i in xrange(w.style.col,w.style.col+w.style.colspan):
				cols_min[i] += add
				
		#step 4: was already done in step 1
		
		#set all cols up with min widths
		cols = cols_min[:]
		
		#distribute the extra evenly
		_min_w = 0
		for v in cols_min: _min_w += v
		_max_w = 0
		for v in cols_max: _max_w += v
		
		#note down for getwidths
		self._widths = _min_w,_max_w
		
		#continue distributing the extra evenly
		final_w = _min_w
		if final_w < min_w: final_w = min_w
		if final_w < _max_w: final_w = _max_w
		if max_w != None and final_w > max_w: final_w = max_w
		
		extra_w = max(0,final_w - _min_w)
		
		if extra_w > 0:
			cols_bal = [] #balanced based on max
			for v in cols_max:
				cols_bal.append(v * final_w / _max_w)

			trim = 0
			total = 0
			for i in xrange(0,ncols):
				if cols_min[i] >= cols_bal[i]:
					#trim += cols_min[i] - cols_bal[i]
					trim += cols_min[i]
				else:
					total += cols_max[i]
				
			extra_w = final_w - trim
			#print 'extra_w',extra_w
			
			for i in xrange(0,ncols):
				if cols_min[i] < cols_bal[i]:
					cols[i] = cols_max[i] * extra_w / total
		#print self.style.width,cols
			
		#resize all the widgets to fit the new widths
		for w in self.widgets:
			xt,xl,xb,xr = w.getspacing()
			xw = xl + xr
			xx = 0
			for i in xrange(w.style.col,w.style.col+w.style.colspan): xx+=cols[i]
			nw = xx-xw
			if nw != w.rect.w:
				#print '---'
				#print w.rect.w,nw
				w.resize(width=nw)
				#print w.rect.w,nw

		#figure out row heights, this could be 2-pass and fancier...
		for w in self.widgets:	
			xt,xl,xb,xr = w.getspacing()
			xh = xt+xb
			v = _table_div(max(w.rect.h+xh,w.style.cell_height),w.style.rowspan)
			for i in xrange(w.style.row,w.style.row+w.style.rowspan):
				rows[i] = max(rows[i],v)
				
		#add some extra to thw rows, if needed, really basic..
		rows_min = rows
		
		_min_h = 0
		for v in rows_min: _min_h += v
		
		final_h = _min_h
		if final_h < min_h: final_h = min_h
		#if final_h < _max_h: final_h = _max_h
		if max_h != None and final_h > max_h: final_h = max_h
		
		extra_h = max(0,final_h - _min_h)
		
		for i in range(0,len(rows)):
			rows[i] += _table_div_down(extra_h * rows[i], _min_h)
			
		#calculate the row and column positions
		p = 0
		rowpos = [p]
		for v in rows:
			n = v+p
			rowpos.append(n)
			p = n
		p = 0
		colpos = [p]
		for v in cols:
			n = v+p
			colpos.append(n)
			p = n
			
		#do the final positioning of the widgets	
		for w in self.widgets:
			x,y,xx,yy=0,0,0,0
			y = rowpos[w.style.row]
			for i in xrange(w.style.row,w.style.row+w.style.rowspan): yy+=rows[i]
			x = colpos[w.style.col]
			for i in xrange(w.style.col,w.style.col+w.style.colspan): xx+=cols[i]
			
			xt,xl,xb,xr = w.getspacing()
			xw = xl + xr
			xh = xt + xb
			
			w.style.x = x
			w.style.y = y

			w._resize(xx-xw,yy-xh)
			
		w,h=0,0
		for i in cols: w+=i
		for i in rows: h+=i
		self.rect.w = w
		self.rect.h = h
		
	def getwidths(self):
		return self._widths

class _button(Widget):
	def __init__(self,**params):
		Widget.__init__(self,**params)
		self.state = 0
		
	def event(self,e):
		if e.type is ENTER: self.repaint()
		elif e.type is EXIT: self.repaint()
		elif e.type is FOCUS: self.repaint()
		elif e.type is BLUR: self.repaint()
		elif e.type is KEYDOWN:
			if e.key == K_SPACE:
				self.state = 1
				self.repaint()
			elif e.key == K_TAB:
				self.next()
		elif e.type is MOUSEBUTTONDOWN: 
			self.state = 1
			self.repaint()
		elif e.type is KEYUP:
			if self.state == 1: self.click()
			self.state = 0
			self.repaint()
		elif e.type is MOUSEBUTTONUP:
			self.state = 0
			self.repaint()
		elif e.type is CLICK:
			self.click()
			
		self.pcls = ""
		if self.state == 0 and self.container.myhover == self:
			self.pcls = "hover"
		if self.state == 1 and self.container.myhover == self:
			self.pcls = "down"
			
	def click(self): 
		pass

class Spacer(_button):
	def __init__(self,width,height,**params):
		_button.__init__(self,width=width,height=height,**params)
		#self..w,self.rect.h = width,height
		self.style.disabled = 1
		
		
		
class Color(Widget):
	def __init__(self,value=None,**params):
		if value != None: params['value']=value
		Widget.__init__(self,**params)
		#self.value = value
		
	def paint(self,s):
		#print ('Color.paint()',self.value)
		#print self.value
		#print 'hi there'
		#print s.get_width(),s.get_height()
		s.fill(self.value)

	def __setattr__(self,k,v):
		if k == 'value' and type(v) == str: v = pygame.Color(v)
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k]=v
		if k == 'value' and _v != NOATTR and _v != v: 
			self.send(CHANGE)
			self.repaint()
			#print v

			
	
class Image(Widget):
	def __init__(self,value,**params):
		Widget.__init__(self,**params)
		if type(value) == str: value = pygame.image.load(value)
		self.value = value
		self.style.width = self.value.get_width()
		self.style.height = self.value.get_height()
			
	def paint(self,s):
		s.blit(self.value,(0,0))
		
		
class Icon(_button):
	def __init__(self,cls,**params):
		_button.__init__(self,**params)
		self.cls = cls
		self.pcls = ""		
		s = self.style.image
		self.style.width = s.get_width()
		self.style.height = s.get_height()
		self.state = 0
			
	def paint(self,s):
		self.pcls = ""
		if self.state == 0 and hasattr(self.container,'myhover') and self.container.myhover == self: self.pcls = "hover"
		if self.state == 1 and hasattr(self.container,'myhover') and self.container.myhover == self: self.pcls = "down"
		s.blit(self.style.image,(0,0))


				
class Background(Widget):
	def __init__(self,value,**params):
		Widget.__init__(self,**params)
		self.value = value
		
	def paint(self,s):
		r = pygame.Rect(0,0,s.get_width(),s.get_height())
		v = self.value.style.background
		#print r,v
		if type(v) == tuple:
			s.fill(v)
		else: render_box(s,v,r)

class Button(_button):
	def __init__(self,value=None,**params):
		params.setdefault('cls','button')
		_button.__init__(self,**params)
		
		self.value = value
		
	def __setattr__(self,k,v):
		if k == 'value' and type(v) == str: v = Label(v)
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k]=v
		if k == 'value' and v != None:
			pass

		if k == 'value' and _v != NOATTR and _v != v:
			self.send(CHANGE)
			self.repaint()
			
	def resize(self,width=None,height=None):
		self.value.resize()
		self.value._resize()
		self.rect.w,self.rect.h = self.value.rect_margin.w,self.value.rect_margin.h

	def paint(self,s):
		self.value.paint(_subsurface(s,self.value.rect))


class Switch(_button):
	def __init__(self,value=False,**params):
		params.setdefault('cls','switch')
		_button.__init__(self,**params)
		self.value = value
		
		img = self.style.off
		self.style.width = img.get_width()
		self.style.height = img.get_height()
		
	def paint(self,s):
		self.pcls = ""
		if self.container.myhover == self: self.pcls = "hover"
		if self.value: img = self.style.on
		else: img = self.style.off
		s.blit(img,(0,0))
		
	def __setattr__(self,k,v):
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k]=v
		if k == 'value' and _v != NOATTR and _v != v: 
			self.send(CHANGE)
			self.repaint()

	def click(self):
		self.value = not self.value

class Checkbox(_button):
	def __init__(self,group,value=None,**params):
		params.setdefault('cls','checkbox')
		_button.__init__(self,**params)
		self.group = group
		self.group.add(self)
		if self.group.value == None:
			self.group.value = []
		self.value = value
		
		img = self.style.off
		self.style.width = img.get_width()
		self.style.height = img.get_height()
		
	def paint(self,s):
		self.pcls = ""
		if self.container.myhover == self: self.pcls = "hover"
		if self.value in self.group.value: img = self.style.on
		else: img = self.style.off
		
		#print self.cls,self.pcls
		
		s.blit(img,(0,0))


	def click(self):
		if self.value in self.group.value:
			self.group.value.remove(self.value)
		else:
			self.group.value.append(self.value)
		self.group._change()

			
class Radio(_button):
	def __init__(self,group=None,value=None,**params):
		params.setdefault('cls','radio')
		_button.__init__(self,**params)
		self.group = group
		self.group.add(self)
		self.value = value
		
		img = self.style.off
		self.style.width = img.get_width()
		self.style.height = img.get_height()
		
	def paint(self,s):
		self.pcls = ""
		if self.container.myhover == self: self.pcls = "hover"
		if self.group.value == self.value: img = self.style.on
		else: img = self.style.off
		s.blit(img,(0,0))
		
	def click(self):
		self.group.value = self.value
		
class Tool(_button):
	def __init__(self,group,widget=None,value=None,**params):
		params.setdefault('cls','tool')
		_button.__init__(self,**params)
		self.group = group
		self.group.add(self)
		self.value = value
		
		if widget != None:
			self.setwidget(widget)
			
	def setwidget(self,w):
		self.widget = w
	
	def resize(self,width=None,height=None):
		self.widget.resize()
		self.widget._resize()
		self.rect.w,self.rect.h = self.widget.rect_margin.w,self.widget.rect_margin.h
		
	def event(self,e):
		_button.event(self,e)
		if self.group.value == self.value: self.pcls = "down"

	def paint(self,s):
		if self.group.value == self.value: self.pcls = "down"
		self.widget.paint(_subsurface(s,self.widget.rect))
		
	def click(self):
		self.group.value = self.value
		for w in self.group.widgets:
			if w != self: w.pcls = ""
		

		
class Label(Widget):
	def __init__(self,value,**params):
		params.setdefault('cls','label')
		Widget.__init__(self,**params)
		self.value = value
		self.font = self.style.font
		self.style.width, self.style.height = self.font.size(self.value)
		self.style.disabled = 1
		
	def paint(self,s):
		s.blit(self.font.render(self.value, 1, self.style.color),(0,0))

class Input(Widget):
	def __init__(self,value="",size=20,**params):
		params.setdefault('cls','input')
		Widget.__init__(self,**params)
		self.value = value
		self.pos = None
		self.vpos = 0
		self.font = self.style.font
		w,h = self.font.size("e"*size)
		self.style.width,self.style.height = w,h
		#self.rect.w=w+self.style.padding_left+self.style.padding_right;
		#self.rect.h=h+self.style.padding_top+self.style.padding_bottom;
		
	def paint(self,s):
		if self.pos == None: self.pos = len(self.value)
			
		r = Rect(0,0,self.rect.w,self.rect.h)
		
		cs = 2 #NOTE: should be in a style
		
		w,h = self.font.size(self.value[0:self.pos])
		x = w-self.vpos
		if x < 0: self.vpos -= -x
		if x+cs > s.get_width(): self.vpos += x+cs-s.get_width()
		
		s.blit(self.font.render(self.value, 1, self.style.color),(-self.vpos,0))
		
		if self.container.myfocus == self:
			w,h = self.font.size(self.value[0:self.pos])
			r.x = w-self.vpos
			r.w = cs
			r.h = h
			s.fill(self.style.color,r)
			
	def _setvalue(self,v):
		self.__dict__['value'] = v
		self.send(CHANGE)
			
	def event(self,e):
		#print e.type
		if e.type is KEYDOWN:	
			if e.key == K_BACKSPACE:
				if self.pos:
					self._setvalue(self.value[:self.pos-1] + self.value[self.pos:])
					self.pos -= 1
			elif e.key == K_DELETE:
				if len(self.value) > self.pos:
					self._setvalue(self.value[:self.pos] + self.value[self.pos+1:])
			elif e.key == K_HOME: 
				self.pos = 0
			elif e.key == K_END:
				self.pos = len(self.value)
			elif e.key == K_LEFT:
				if self.pos > 0: self.pos -= 1
			elif e.key == K_RIGHT:
				if self.pos < len(self.value): self.pos += 1
			elif e.key == K_RETURN:
				self.next()
			elif e.key == K_TAB:
				self.next()	
			else:
				#c = str(e.unicode)
				c = (e.unicode).encode('latin-1')
				if len(c):
					self._setvalue(self.value[:self.pos] + c + self.value[self.pos:])
					self.pos += 1
			self.repaint()
		elif e.type is FOCUS:
			self.repaint()
		elif e.type is BLUR:
			self.repaint()
			
		self.pcls = ""
		if self.container.myfocus == self: self.pcls = "focus"

			
	def __setattr__(self,k,v):
		if k == 'value':
			if v == None: v = ''
			v = str(v)
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k]=v
		if k == 'value' and _v != NOATTR and _v != v: 
			self.pos = len(self.value)
			self.send(CHANGE)
			self.repaint()


_SLIDER_HORIZONTAL = 0
_SLIDER_VERTICAL = 1

class _slider(Widget):
	def __init__(self,value,orient,min,max,size,**params):
		params.setdefault('cls','slider')
		Widget.__init__(self,**params)
		self.min,self.max,self.value,self.orient,self.size = min,max,value,orient,size
		
	def paint(self,s):
		self.pcls = ""
		if self.container.myhover == self: self.pcls = "hover"
		
		r = pygame.rect.Rect(0,0,self.rect.w,self.rect.h)
		#render_box(s,self.style.background,r)
		if self.orient == _SLIDER_HORIZONTAL:
			r.x = (self.value-self.min) * (self.rect.w-self.size) / (self.max-self.min);
			r.w = self.size;
		else:
			r.y = (self.value-self.min) * (self.rect.h-self.size) / (self.max-self.min);
			r.h = self.size;
		render_box(s,self.style.bar,r)
		
	def event(self,e):
		adj = 0
		if e.type is ENTER: self.repaint()
		elif e.type is EXIT: self.repaint()
		elif e.type is KEYDOWN:
			if e.key == K_TAB:
				self.next()

		elif e.type is MOUSEBUTTONDOWN: 
			x,y,adj = e.pos[0],e.pos[1],1
		elif e.type is MOUSEBUTTONUP:
			x,y,adj = e.pos[0],e.pos[1],1
		elif e.type is MOUSEMOTION:
			if e.buttons[0] and self.container.myfocus == self:
				x,y,adj = e.pos[0],e.pos[1],1
		if adj:
			if self.orient == _SLIDER_HORIZONTAL:
				d = self.size/2 - (self.rect.w/(self.max-self.min+1))/2
				self.value = (x-d) * (self.max-self.min) / (self.rect.w-self.size) + self.min
			else:
				d = self.size/2 - (self.rect.h/(self.max-self.min+1))/2
				self.value = (y-d) * (self.max-self.min) / (self.rect.h-self.size) + self.min

	def __setattr__(self,k,v):
		if k == 'value':
			v = int(v)
			v = max(v,self.min)
			v = min(v,self.max)
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k]=v
		if k == 'value' and _v != NOATTR and _v != v: 
			self.send(CHANGE)
			self.repaint()

class VSlider(_slider):
	def __init__(self,value,min,max,size,**params):
		params.setdefault('cls','vslider')
		_slider.__init__(self,value,_SLIDER_VERTICAL,min,max,size,**params)
		
class HSlider(_slider):
	def __init__(self,value,min,max,size,**params):
		params.setdefault('cls','hslider')
		_slider.__init__(self,value,_SLIDER_HORIZONTAL,min,max,size,**params)


#// Top_dialog

class Dialog(Table):
	def __init__(self,title,main,**params):
		params.setdefault('cls','dialog')
		Table.__init__(self,**params)
		
		self.tr()
		
		t = Table(cls=self.cls+".bar")
		t.tr()
		t.td(title)
		clos = Icon(self.cls+".bar.close")
		t.td(clos,align=1)
		clos.connect(CLICK,self.close,None) 
		#self.td(t)
		self.add(t,0,0)

		main.resize()
		main._resize()
		t.style.width = main.rect_margin.w
		clos.resize()
		#title.style.cell_width = main.rect.w - clos.rect.w
		
		#t.background = Box(t.style.background)
		self.tr()
		self.td(main,cls=self.cls+".main")

#// Top_select

class Select(Table):
	def __init__(self,value=None,**params):
		params.setdefault('cls','select')
		Table.__init__(self,**params)
		
		self.top_selected = Button(cls=self.cls+".selected")
		Table.add(self,self.top_selected,0,0)
		self.top_selected.value = " "
				
		self.top_arrow = Button(Image(self.style.arrow),cls=self.cls+".arrow")
		Table.add(self,self.top_arrow,1,0)
		
		self.options = Table()
		
		self.options.tr()
		self.spacer = Spacer(0,0)
		self.options.add(self.spacer)
		
		self.options.tr()
		self._options = Table(cls=self.cls+".options")
		self.options.add(self._options)
		
		self.options.connect(BLUR,self.options.close,None)
		self.spacer.connect(CLICK,self.options.close,None)
		
		self.values = []
		self.value = value
		
		
	def resize(self,width=None,height=None):
		max_w,max_h = 0,0
		for w in self._options.widgets:
			w.resize()
			w._resize()
			max_w,max_h = max(max_w,w.rect_margin.w),max(max_h,w.rect_margin.h)
		
		xt,xr,xb,xl = self.top_selected.getspacing()
		self.top_selected.style.cell_width = max_w + xl + xr
		self.top_selected.style.cell_height = max_h + xt + xb
		
		Table.resize(self,width,height)
		
	def _resize(self,width=None,height=None):
		Table._resize(self,width,height)
		
		self.top_selected.connect(CLICK,action_open,{'container':self.container,'window':self.options,'x':self.rect.x,'y':self.rect.y})
		self.top_arrow.connect(CLICK,action_open,{'container':self.container,'window':self.options,'x':self.rect.x,'y':self.rect.y})

		self.spacer.style.width = self.rect.w
		self.spacer.style.height = self.rect.h
		
		xt,xr,xb,xl = self._options.getspacing()
		self._options.style.width = self.rect.w - (xl+xr)
	
		
	def _setvalue(self,value):
		self.value = value._value
		if hasattr(self,'container'): 
			self.resize() #to recenter the new value, etc.
			#self._resize()
		self.options.close()
		self.repaint() #this will happen anyways
		
	def __setattr__(self,k,v):
		mywidget = None
		if k == 'value':
			for w in self.values:
				if w._value == v:
					mywidget = w
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k]=v
		if k == 'value' and _v != NOATTR and _v != v: 
			self.send(CHANGE)
			self.repaint()
		if k == 'value':
			if mywidget == None:
				mywidget = Label(" ")
			self.top_selected.value = mywidget
			
	def add(self,w,value=None):
		if type(w) == str: w = Label(w)
		
		b = Button(w,cls=self.cls+".option")
		b.connect(CLICK,self._setvalue,w)
		
		self._options.tr()
		self._options.add(b, align=-1)
		
		if value != None: w._value = value
		if self.value == w._value:
			self.top_selected.value = w
		self.values.append(w)

#Top_menu
	
class Menu(Button):
	def __init__(self,widget=None,**params):
		params.setdefault('cls','menu')
		Button.__init__(self,widget,**params)
		
		self._cls = self.cls
		self.options = Table(cls=self.cls+".options")
		#self.options.background = Box(self.options.style.background)
		
		self.options.connect(BLUR,self._close,None)
		
		self.pos = 0
		
	def _open(self,value):
		self.cls = self._cls + "-open"
		self.repaint()
		action_open({'container':self.container,'window':self.options,'x':self.rect_margin.x,'y':self.rect_margin.bottom})
		
	def _close(self,value):
		self.cls = self._cls
		self.repaint()
		self.options.close()
		
	def _value(self,value):
		self.options.close()
		if value['fnc'] != None:
			value['fnc'](value['value'])

	def resize(self,width=None,height=None):
		Button.resize(self,width,height)
		
		self.connect(CLICK,self._open,None)
		self.options.resize()
		self.options._resize()
		
	def add(self,w,fnc=None,value=None):
		w.resize()
		
		w.style.align = -1
		b = Button(w,cls=self.cls+".option")
		b.style.hexpand = 1
		b.connect(CLICK,self._value,{'fnc':fnc,'value':value})
		
		self.options.add(b,0,self.pos,1,1,-1,0)
		self.pos += 1
		
		return b

#// Top_prompt

class Keysym(Widget):
	def __init__(self,value=None,**params):
		params.setdefault('cls','keysym')
		Widget.__init__(self,**params)
		self.value = value
		
		self.font = self.style.font
		w,h = self.font.size("Right Super") #"Right Shift")
		self.style.width,self.style.height = w,h
		#self.rect.w=w+self.style.padding_left+self.style.padding_right
		#self.rect.h=h+self.style.padding_top+self.style.padding_bottom
		
	def event(self,e):
		if e.type is FOCUS or e.type is BLUR: self.repaint()
		elif e.type is KEYDOWN:
			if e.key != K_TAB:
				self.value = e.key
				self.repaint()
				self.send(CHANGE)
			self.next()
		self.pcls = ""
		if self.container.myfocus == self: self.pcls = "focus"
			
	def paint(self,s):
		r = pygame.rect.Rect(0,0,self.rect.w,self.rect.h)
		#render_box(s,self.style.background,r)
		if self.value == None: return
		name = ""
		for p in pygame.key.name(self.value).split(): name += p.capitalize()+" "
		#r.x = self.style.padding_left;
		#r.y = self.style.padding_bottom;
		s.blit(self.style.font.render(name, 1, self.style.color), r)
		
	def __setattr__(self,k,v):
		if k == 'value' and v != None:
			v = int(v)
		_v = self.__dict__.get(k,NOATTR)
		self.__dict__[k]=v
		if k == 'value' and _v != NOATTR and _v != v: 
			self.send(CHANGE)
			self.repaint()


class Menus(Table):
	def __init__(self,data,menu_cls='menu',**params):
		params.setdefault('cls','menus')
		Table.__init__(self,**params)
		
		n,m,mt = 0,None,None
		for path,cmd,value in data:
			parts = path.split("/")
			if parts[0] != mt:
				mt = parts[0]
				m = Menu(Label(mt),cls=menu_cls)
				self.add(m,n,0)
				n += 1
			m.add(Label(parts[1]),cmd,value)
			m.resize()
			
class Toolbox(Table):
	def _change(self,value):
		self.value = self.group.value
		self.send(CHANGE)
	def __init__(self,data,cols=0,rows=0,tool_cls='tool',value=None,**params):
		params.setdefault('cls','toolbox')
		Table.__init__(self,**params)
		
		if cols == 0 and rows == 0: cols = len(data)
		if cols != 0 and rows != 0: rows = 0
		
		self.tools = {}
		self.value = value
		
		g = Group()
		g.value = value
		self.group = g
		g.connect(CHANGE,self._change,None)
		
		x,y,p,s = 0,0,None,1
		for icon,value in data:
			img = theme.get(tool_cls+"."+icon,"","image")
			#print tool_cls,icon,img
			if img:
				i = Image(img)
			else: i = Label(icon)
			p = Tool(g,i,value,cls=tool_cls)
			self.tools[icon] = p
			p.style.hexpand = 1
			p.style.vexpand = 1
			self.add(p,x,y)
			s = 0
			if cols != 0: x += 1
			if cols != 0 and x == cols: x,y = 0,y+1
			if rows != 0: y += 1
			if rows != 0 and y == rows: x,y = x+1,0

class Form(Object):
	def __init__(self):
		self._elist = []
		self._emap = {}
		self._dirty = 0
		Form.form = self
		
	def add(self,e,name=None,value=None):
		if name != None: e.name = name
		if value != None: e.value = value
		self._elist.append(e)
		self._dirty = 1
		
	def _clean(self):
		for e in self._elist[:]:
			if not hasattr(e,'name') or e.name == None:
				self._elist.remove(e)
		self._emap = {}
		for e in self._elist:
			self._emap[e.name] = e
		
	
	#def __setitem__(self,k,v):
	#	if self._dirty: self._clean()
	#	self._emap[k].value = v
	
	def __getitem__(self,k):
		if self._dirty: self._clean()
		#return self._emap[k].value
		return self._emap[k]
		
	def results(self):
		if self._dirty: self._clean()
		r = {}
		for e in self._elist:
			r[e.name] = e.value
		return r
		
	def items(self):
		return self.results().items()
		
	def start(self):
		Object.start(self,-1)

class _document_widget:
	def __init__(self,widget,align=None):
		self.widget = widget
		if align != None: self.align = align
		
class Document(Container):
	def __init__(self,**params):
		params.setdefault('cls','document')
		Container.__init__(self,**params)
		self.layout =  layout.Layout(pygame.Rect(0,0,self.rect.w,self.rect.h))
	
	def add(self,e,align=None):
		dw = _document_widget(e,align)
		self.layout.add(dw)
		e.container = self
		e._c_dw = dw
		self.widgets.append(e)
		
	def block(self,align):
		self.layout.add(align)
		
	def space(self,e):
		self.layout.add(e)
		
	def br(self,height):
		self.layout.add((0,height))
		
	def resize(self,width=None,height=None):
		min_w = 0
		min_h = 0
		max_w = width
		max_h = height
		if self.style.width: min_w,max_w = self.style.width,self.style.width
		if self.style.height: min_h,max_h = self.style.height,self.style.height
		
		if max_w == None: max_w = 65535 #HACK: a big number
		
		for w in self.widgets:
			w.rect.w,w.rect.h = 0,0
			xt,xl,xb,xr = w.getspacing()
			w.resize(width=max_w-(xl+xr))
			dw = w._c_dw
			dw.rect = pygame.Rect(0,0,w.rect.w+xl+xr,w.rect.h+xt+xb)
			
		self.layout.rect = pygame.Rect(0,0,max_w,0)
		self.layout.resize()
		
		_max_w = 0
		
		for w in self.widgets:
			xt,xl,xb,xr = w.getspacing()
			dw = w._c_dw
			w.style.x,w.style.y,w.rect.w,w.rect.h = dw.rect.x,dw.rect.y,dw.rect.w-(xl+xr),dw.rect.h-(xt+xb)
			w._resize()
			_max_w = max(_max_w,w.rect_margin.right)
		
		self.rect.w = _max_w #self.layout.rect.w
		self.rect.h = self.layout.rect.h

	def getwidths(self):
		v = self.style.width
		if v: return v,v
		r = self.layout.getwidths()
		#print r
		return r
		#return self.layout.getwidths()
		
class Desktop(App):
	def __init__(self,**params):
		params.setdefault('cls','desktop')
		App.__init__(self,**params)
		
# vim: set filetype=python ts=4 sw=4 noet si :
