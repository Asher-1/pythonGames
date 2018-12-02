from pyglet import window
from pyglet import clock
from pyglet import font
from pyglet import resource
from pyglet import sprite
from pyglet import graphics
from pyglet import gl
from pyglet import text
from pyglet import event
from pyglet import image
from pyglet.window import key
from pyglet import media

import sys

import random
import math
import time

from LinkedParticles import LinkedParticles

MENU_FONT = 'PALIMPUS'
GUI_FONT = 'Arial'

KEY_PAUSE = key.P

GROUND_HEIGHT = 40
BUG_HEIGHT = 60
MIN_BLADE_WIDTH = 20
MAX_BLADE_WIDTH = 30
MIN_BLADE_HEIGHT = 100
MAX_BLADE_HEIGHT = 250
BLADE_SEGMENTS = 8
BLADE_PARTICLES = 2 * BLADE_SEGMENTS + 1
HALF_BLADE_PARTICLES = BLADE_PARTICLES / 2
BLADE_REGENERATE_RATE = 0.001
NUM_BLADES = 8


FAIRY_ROTATE = 45
FAIRY_ACCEL = 2.5
FAIRY_DRAG = 0.85
FAIRY_MAX_BLOW_POWER = 20.0
FAIRY_BLOW_RESERVE =  FAIRY_MAX_BLOW_POWER * 3.0
FAIRY_BLOW_INC = 1

#Ants are fast but light and slow-eaters
ANT_ACCEL = 1.0
ANT_DRAG = 0.9
ANT_CLIMBSPEED = 1.0
ANT_HUNGER = 0.001
ANT_WEIGHT = 0.3 * FAIRY_MAX_BLOW_POWER

#Ladybugs are balanced
LADYBUG_ACCEL = 0.5
LADYBUG_DRAG = 0.9
LADYBUG_CLIMBSPEED = 0.75
LADYBUG_HUNGER = 0.002
LADYBUG_WEIGHT = 0.45 * FAIRY_MAX_BLOW_POWER


#Snails are slow but heavy and fast-eaters
SNAIL_ACCEL = 0.25
SNAIL_DRAG = 0.9
SNAIL_CLIMBSPEED = 0.5
SNAIL_HUNGER = 0.003
SNAIL_WEIGHT = 0.6 * FAIRY_MAX_BLOW_POWER


MAX_NUM_ANTS = 9
MAX_NUM_LADYBUGS = 5
MAX_NUM_SNAILS = 4

BUG_WANDER = 0
BUG_CLIMB = 1
BUG_EAT = 2
BUG_FLY = 3

tick = 0

def load_image(name):
    img = resource.image(name)
    img.anchor_x = img.width*0.5
    img.anchor_y = 0
    return img

class SimpleMenu(event.EventDispatcher, graphics.Batch):
    def __init__(self, parent, x, y, title_text, options):
        super(SimpleMenu, self).__init__()
	
        self.parent = parent
        self.x, self.y = x, y

	self.title_text = text.Label(title_text,
                    font_name=MENU_FONT,
                    font_size=48,
                    x=x, 
                    y=y,
                    color=(255, 255, 255, 255),
                    anchor_x='left',
                    anchor_y='center')

        title_height = self.title_text.content_height;
        y -= title_height

        self.options = []
        self.width = 0
        for option in options:
            l = text.Label(option,
                        font_name=MENU_FONT,
                        font_size=22,
                        x=x, y=y,
                        color=(0, 128, 0, 255), anchor_y='top', batch=self)
            self.options.append(l)
            self.width = max(self.width, l.content_width)
            y -= l.content_height


        self.created_time = time.time()
    
        parent.push_handlers(self)

    def on_mouse_motion(self, x, y, dx, dy):
        ret = ""
        for option in self.options:
            if (option.x < x < option.x + self.width and
                    option.y - option.content_height < y < option.y):
                option.color = (0, 255, 0, 255)
                ret = option
            elif option.color != (0, 200, 0, 255):
                option.color = (0,200, 0, 255)
        return ret

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        return self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, buttons, modifiers):
        # determine action to take
        selected_option = None
        for option in self.options:
            if (option.x < x < option.x + self.width and
                    option.y - option.content_height < y < option.y):
                selected_option = option.text
                break
	
        if selected_option != None:
            self.parent.dispatch_events()
            self.parent.remove_handlers(self)
            self.options = None
            self.parent.overlay = None
            self.parent.menu_option(selected_option)

    def draw(self):
	self.parent.objects.backgrb.blit(0,0)
	self.title_text.draw()      
	for option in self.options:
	    option.draw()
	

        
    
class Blade(LinkedParticles, graphics.Batch):
    def __init__(self, xpos, blade_width, blade_height, width, height, batch_id, batch_group):
        super(Blade, self).__init__(width, height)
        
        self.health = 1.0
        
        self.max_width = blade_width
        self.max_height = blade_height
        self.x = xpos 
        
        side_segment_length = math.sqrt(blade_width*blade_width/4 + blade_height*blade_height) / BLADE_SEGMENTS
        
        self.half_point = BLADE_PARTICLES / 2
        

        for i in range(0, BLADE_PARTICLES):
            self.AddParticle(xpos, GROUND_HEIGHT)
            if (i == self.half_point or i-1 == self.half_point):
                self.AddConstraint(i, i-1, side_segment_length/2)
            else:
                if (i > 0):
                    self.AddConstraint(i, i-1, side_segment_length)
        self.AddConstraint(self.half_point-1, self.half_point+1, side_segment_length/2)
        
        self.mass[0] = 0
        self.pos[0][0] = self.x - blade_width
        self.pos[BLADE_PARTICLES - 1][0] = self.x + blade_width
        self.mass[BLADE_PARTICLES - 1] = 0
        
        self.vertex_list = graphics.vertex_list(2*(( BLADE_SEGMENTS * 2 + 1) / 2)*3, 'v2f' )
        
        self.suffered_wind = 0
        self.wind_height = 0
  

        
    def AccumulateForces(self, wind):
        for p in range(0, self.n_particles):
            self.accel[p][0] = 0           
            self.accel[p][1] = 0.1 + 4.5*self.health
        
        self.accel[HALF_BLADE_PARTICLES][0] = wind
        
        
    def TimeStep(self, wind, wind_height):
        self.suffered_wind = wind
        self.wind_height = wind_height
        
        if 0.25 < self.health < 1.0:
            self.health = self.health + BLADE_REGENERATE_RATE
            
        self.AccumulateForces( wind )
        self.Verlet()
        self.SatisfyConstraints()
        
	
    def draw(self):
        vertices = []
        gl.glColor3f(0.5 *(1.0 - self.health), 0.25 + 0.75*self.health, 0.1*self.health)
        
        if self.n_constraints > 0:            
                for c in range(0, HALF_BLADE_PARTICLES ):
                  
                    #Use triangles
                    posA = self.pos[c]
                    posB = self.pos[self.n_particles-c-1]
                    posC = self.pos[c + 1]                             
                    vertices = vertices + [posA[0], posA[1], posB[0], posB[1], posC[0], posC[1]]
                    
                    posA = self.pos[c+1]
                    posB = self.pos[self.n_particles-c-2]
                    posC = self.pos[self.n_particles-c-1]
                    vertices = vertices + [posA[0], posA[1], posB[0], posB[1], posC[0], posC[1]]
                    
        self.vertex_list.vertices = vertices
        self.vertex_list.draw(gl.GL_TRIANGLES)
        
        
        

class Grass():
    def __init__(self, parent):
        self.parent = parent
        self.blades = []
        for i in range(100, parent.width-100, (parent.width - 200) / (NUM_BLADES-1)):
            new_blade = Blade(i  + random.random()*MIN_BLADE_WIDTH,
                              MIN_BLADE_WIDTH + random.random()*MAX_BLADE_WIDTH,
                              MIN_BLADE_HEIGHT + random.random()*MAX_BLADE_HEIGHT,
                              parent.width, parent.height, parent.batch, parent.foreground)
            self.blades.append(new_blade)
	    
	self.healthy_blades = 0
            
       
    def draw(self):       
        vertices = []
        for blade in self.blades:
            blade.draw()
        gl.glColor3f(1.0,1.0,1.0)

        
            
    def update(self, wind, origin):
        vertices = []
	self.healthy_blades = 0
        for blade in self.blades:
            dist = abs(blade.x - origin[0])
            blow = wind * 1.0 / (1.0 + dist*dist*0.0001)
            if wind > 0 and origin[0] > blade.x:
                blow = 0
            if wind < 0 and origin[0] < blade.x:
                blow = 0
            blade.TimeStep(blow, origin[1])
	    if blade.health > 0:
		self.healthy_blades += 1
    


class Fairy(graphics.Batch, key.KeyStateHandler):
    def __init__(self, parent):

        #.........................................................Create sprites
        #Flying
        imgFly1 = load_image("mainPose1.png")
        imgFly2 = load_image("mainPose2.png")
        imgFly3 = load_image("mainPose3.png")
        self.fly_left_anim = image.Animation(
            [
                image.AnimationFrame(imgFly1, 0.1),
                image.AnimationFrame(imgFly2, 0.1),
                image.AnimationFrame(imgFly3, 0.1),
                image.AnimationFrame(imgFly2, 0.1)
            ])
        self.fly_right_anim = self.fly_left_anim.get_transform(flip_x = True)
        
        #Blowing
        imgBlow1 = load_image("blowing1.png")
	imgBlow2 = load_image("blowing2.png")
	imgBlow3 = load_image("blowing3.png")
        self.blow_left_anim = image.Animation(
            [
                image.AnimationFrame(imgBlow1, 0.1),
		image.AnimationFrame(imgBlow2, 0.1),
		image.AnimationFrame(imgBlow3, 0.1),
		image.AnimationFrame(imgBlow2, 0.1)
            ])
        self.blow_right_anim = self.blow_left_anim.get_transform(flip_x = True)
	
	#Upskirt
        imgUpskirt1 = load_image("upskirt1.png")
	imgUpskirt2 = load_image("upskirt2.png")
	imgUpskirt3 = load_image("upskirt3.png")
        self.upskirt_left_anim = image.Animation(
            [
                image.AnimationFrame(imgUpskirt1, 0.1),
		image.AnimationFrame(imgUpskirt2, 0.1),
		image.AnimationFrame(imgUpskirt3, 0.1),
		image.AnimationFrame(imgUpskirt2, 0.1)
            ])
        self.upskirt_right_anim = self.upskirt_left_anim.get_transform(flip_x = True)
    
        self.sprite = sprite.Sprite(self.fly_left_anim, batch=parent.batch, group=parent.playerlayer)
        self.sprite.x = 400
        self.sprite.y = 400
        
        self.parent = parent
    
        #Movement
        self.pos = [400.0,400.0]
        self.old_pos = [400.0,400.0]
        self.accel = [0.0,0.0]
	self.power = 1
	self.blow_reserve = FAIRY_BLOW_RESERVE
        
        self.facing_left = True
        
        self.wind = 0
	self.wind_sound = None
        

    def update(self):
        global tick
        
        self.accel[0] = 0
        self.accel[1] = 0
        
        # Update rotation
	
	prev_orientation = self.facing_left
        if self[key.LEFT]:
            self.accel[0] = -FAIRY_ACCEL
            self.facing_left = True
        if self[key.RIGHT]:
            self.accel[0] = FAIRY_ACCEL
            self.facing_left = False
        if self[key.UP]:
            self.accel[1] = FAIRY_ACCEL
        if self[key.DOWN]:
            self.accel[1] = -FAIRY_ACCEL
            
        pos = self.pos[:]
        tmp_pos = pos[:]
        old_pos = self.old_pos[:]
        accel = self.accel[:]
            
        pos[0] = pos[0] + (pos[0] - old_pos[0]) * FAIRY_DRAG  + self.accel[0] 
        pos[1] = pos[1] + (pos[1] - old_pos[1]) * FAIRY_DRAG  + self.accel[1] 
        
        #world limits
        if pos[0] < 0:
            pos[0] = 0
            tmp_pos[0] = pos[0]
            self.accel[0] *= -1
            
        if pos[0] > 800:
            pos[0] = 800
            tmp_pos[0] = pos[0]
            self.accel[0] *= -1
	    
	if pos[1] < 0:
	    pos[1] = 00
	    tmp_pos[1] = pos[1]
	    self.accel[1] *= -1
	    
	if pos[1] > 450:
	    pos[1] = 450
	    tmp_pos[1] = pos[1]
	    self.accel[1] *= -1
        
	#Blow!
        if self[key.SPACE] and (-FAIRY_MAX_BLOW_POWER < self.wind < FAIRY_MAX_BLOW_POWER):
            if self.facing_left:
                self.wind = self.wind - FAIRY_BLOW_INC
		
            if not self.facing_left:
                self.wind = self.wind + FAIRY_BLOW_INC
		
	    if self.wind_sound == None:
		self.wind_sound = self.parent.audio.wind.play()
		
	#if blowing, decrease blow reserve. If blow reserve is depleated, stop blowing
	if self[key.SPACE] and self.blow_reserve > 0:
	    self.blow_reserve = self.blow_reserve - FAIRY_BLOW_INC
	else:
            self.wind = 0        
	       

        
        #if we do not blow or we are blowing and we move, stop wind
        if not self[key.SPACE] or self[key.LEFT] or self[key.RIGHT] or self[key.UP] or self[key.DOWN]:
            self.wind = 0
	    #recover blow_reserve
	    if self.blow_reserve < FAIRY_BLOW_RESERVE:	    
		self.blow_reserve = self.blow_reserve + FAIRY_BLOW_INC
        else:
	    #if blowing, draw little clouds
            if self.wind != 0 and len(self.parent.objects.timed_visuals) < 10:
                offset = 0
                min_wind = 0
                if self.wind < 0:
                    offset = -75
                    min_wind = -10
                else:
                    offset = 75
                    min_wind = 10
                self.parent.objects.timed_visuals.append(TimedVisual("viento.png",
                    self.parent, [pos[0] + offset, pos[1] + 75], "move",
                    [self.wind*random.random()*0.5 + min_wind, 5.0*(random.random()-0.5)], 10))

        #.....................................................Control animations
         
        current_animation = self.sprite.image
        
        if self.facing_left:
            if self.wind != 0 and self.sprite.image != self.blow_left_anim:
                self.sprite.image = self.blow_left_anim
		
	    if (self.old_pos[1] - self.pos[1] > 5):
		if self.sprite.image != self.upskirt_left_anim:
		    self.sprite.image = self.upskirt_left_anim
	    else:
		if self.wind == 0 and self.sprite.image != self.fly_left_anim:		    
		    self.sprite.image = self.fly_left_anim
	    if prev_orientation != self.facing_left:
		pos[0] = pos[0] + self.sprite.width / 3.5
		tmp_pos = pos[:]
    
            
        if not self.facing_left:
            if self.wind != 0 and self.sprite.image != self.blow_right_anim:
                self.sprite.image = self.blow_right_anim
	    if (self.old_pos[1] - self.pos[1] > 5):
		if self.sprite.image != self.upskirt_right_anim:
		    self.sprite.image = self.upskirt_right_anim
	    else:
		if self.wind == 0 and self.sprite.image != self.fly_right_anim:
		    self.sprite.image = self.fly_right_anim
	    if prev_orientation != self.facing_left:
		pos[0] = pos[0] - self.sprite.width / 3.5
		tmp_pos = pos[:]
	
	
	
        self.sprite.x = pos[0]
        self.sprite.y = pos[1]
        
        self.pos = pos[:]
        self.old_pos = tmp_pos[:]
	
	#Stop wind sound
	if self.wind == 0 and self.wind_sound != None:
	    # self.wind_sound.stop()
	    self.wind_sound = None
        
        return self.wind
        


class Bug():
    def __init__(self, parent, pos):
        self.parent = parent
        
        #Movement
        self.pos = pos
        self.old_pos = pos
        self.accel = [0.0,0.0]
        
        self.dir = 1
        
        self.state = BUG_WANDER
    
        self.hungry = 100.0 + 50.0*random.random()
        self.blade = None
        self.current_segment = 0
        self.goal_segment = 0
        self.origin = [0,0]
        self.goal = [0,0]
        self.completed = 0
        
        self.climb_speed = 0
	self.drag = 0
	self.speed = 0
        self.hunger = 0
        
	 #Flying
        self.walk_left_anim = None
	self.walk_right_anim = None
        self.eat_left_anim = None
	self.eat_right_anim = None
        self.sprite = None
	
	#Munch player

	self.munch_player = media.Player()
	self.munch_player.eos_action = 'loop'
	
	self.step_player = media.Player()
	self.step_player.eos_action = 'loop'
	self.step_player.volume = 0.15
	
        
    
    def get_closest_blade(self):
        for blade in self.parent.objects.grass.blades:
            if abs(blade.x - self.pos[0] ) < 50 and blade.health > 0:
                return blade
        return None
        
    def get_half_segment_point(self, blade, segment):
        origin_left = blade.pos[segment]
        origin_right = blade.pos[BLADE_PARTICLES - segment -1]
        x = int(origin_left[0] + origin_right[0]) >> 1
        y = int(origin_left[1] + origin_right[1]) >> 1
        return [x, y]
        
        
    def IA(self):
        
        score_mod = (max(1.0, self.parent.objects.score / 500))
      
          
        #decide when to stop for a kitkat
        if self.state == BUG_WANDER:
            if self.hungry > 0:
                self.hungry = self.hungry - 1.0
            else:
                #find blade to climb
                blade = self.get_closest_blade()
                if blade != None:
                    self.state = BUG_CLIMB
                    self.blade = blade
                    self.current_segment = 0
                    self.goal_segment = random.randint(BLADE_SEGMENTS*0.25, BLADE_SEGMENTS*0.75)
                    self.origin = self.get_half_segment_point(blade, self.current_segment)
                    self.goal = self.get_half_segment_point(blade, self.current_segment+1)
                    self.completed = 0
                    if self.sprite.image == self.walk_left_anim:
                        self.sprite.rotation = 90
                    else:
                        self.sprite.rotation = -90

        
        #handle climbing!
        if self.state == BUG_CLIMB or self.state == BUG_EAT:
            self.origin = self.get_half_segment_point(self.blade, self.current_segment)
            self.goal = self.get_half_segment_point(self.blade, self.current_segment+1)
        
            self.pos[0] =  self.origin[0] + (self.goal[0] - self.origin[0]) / 2
            self.pos[1] =  self.origin[1] + (self.goal[1] - self.origin[1]) * self.completed
            
            if self.state != BUG_EAT:
                self.completed = self.completed + self.climb_speed * score_mod / (int(self.blade.max_height) >> 4)

                if self.completed > 1.0:
                    self.completed = 0               
                    self.current_segment = self.current_segment + 1
                    self.origin = self.get_half_segment_point(self.blade, self.current_segment)
                    self.goal = self.get_half_segment_point(self.blade, self.current_segment+1)
                    if self.current_segment == self.goal_segment:
                        self.state = BUG_EAT
                
		
                
        if self.state in [BUG_EAT, BUG_CLIMB]:
            #If wind is strong enough and the fairy is nearby the bug will be knocked down
	    if abs(self.pos[1] - (self.blade.wind_height + 90)) < 100:
		if abs(self.blade.suffered_wind) > self.weight:
		    self.state = BUG_FLY
		    self.old_pos[0] = self.pos[0] - self.blade.suffered_wind*2
		    self.old_pos[1]= self.pos[1] - 25
		    self.parent.score_points(5)
		    self.hungry = 100.0 + 50.0*random.random()
                    
                    #wind strength gets weaker
                    self.blade.suffered_wind = self.blade.suffered_wind * 0.5

                    
		
	    #If eating, damage blade
	    if self.state == BUG_EAT:  
		if self.blade.health > 0:
		    self.blade.health = self.blade.health - self.hunger
	
	    #If blade is eaten, jump
	    if self.blade.health < 0:
		self.sprite.rotation = 0
		self.state = BUG_WANDER
		self.hungry = 100.0 + 50.0*random.random()
		self.old_pos[0] = self.pos[0] + 5.0*(random.random() - 0.5)
		self.old_pos[1]= self.pos[1] - (20.0 + (20.0*random.random()))
		
        
        if self.state == BUG_WANDER:
            if self.dir == 1:
                self.accel[0] = self.speed * score_mod
            else:
                self.accel[0] = -self.speed * score_mod
        else:
            self.accel[0] = 0
           
        self.accel[1] = -0.98
            
        
        
    def update(self):
        global tick
        
        self.IA()
        
        
        if self.state in [BUG_WANDER, BUG_FLY]:
            
            pos = self.pos[:]
            tmp_pos = pos[:]
            old_pos = self.old_pos[:]
            accel = self.accel[:]
                
            pos[0] = pos[0] + (pos[0] - old_pos[0]) * self.drag  + self.accel[0]
            pos[1] = pos[1] + (pos[1] - old_pos[1]) * self.drag  + self.accel[1]
            
            if pos[0] < 0:
                pos[0] = 0
                self.dir = 1
            if pos[0] > 800:
                pos[0] = 800
                self.dir = -1
                
            if pos[1] < GROUND_HEIGHT:
                pos[1] = GROUND_HEIGHT
                if self.state == BUG_FLY:
                    self.sprite.rotation = 0
                    self.state = BUG_WANDER
                
            self.pos = pos[:]
            self.old_pos = tmp_pos[:]
        
        
        if self.state == BUG_WANDER:
	    if self.accel[0] > 0 and self.sprite.image != self.walk_right_anim:
		self.sprite.image = self.walk_right_anim
	    if self.accel[0] < 0 and self.sprite.image != self.walk_left_anim:
		self.sprite.image = self.walk_left_anim
		
	    if not self.step_player.playing and random.random() < 0.5:
		self.step_player.play()
	else:
	    self.step_player.pause()

		
	if self.state == BUG_EAT:
	    if self.sprite.rotation == -90 and self.sprite.image != self.eat_right_anim:
	        self.sprite.image = self.eat_right_anim
	    if self.sprite.rotation == 90 and self.sprite.image != self.eat_left_anim:
	        self.sprite.image = self.eat_left_anim
		
	    if not self.munch_player.playing:
		self.munch_player.play()
	else:
	    if self.munch_player.playing:
		self.munch_player.pause()
                
		
        if self.state == BUG_FLY:
            if self.sprite == self.walk_right_anim:
                self.sprite.rotation = (self.sprite.rotation - 30) % 360
            else:
                self.sprite.rotation = (self.sprite.rotation + 30) % 360
         
        
        self.sprite.x = self.pos[0]
	self.sprite.y = self.pos[1]
    
            
        
class LadyBug(Bug):
    def __init__(self, parent, pos):
        Bug.__init__(self, parent, pos)
        
        #Create sprites
	imgWalk = load_image("mariquita2.png")
        self.walk_left_anim = image.Animation(
            [
                image.AnimationFrame(imgWalk, 1000),
            ])
        self.walk_right_anim = self.walk_left_anim.get_transform(flip_x = True)
	
	imgEat = load_image("mariquita2Come.png")
        self.eat_left_anim = image.Animation(
            [
                image.AnimationFrame(imgEat, 1000),
            ])
	self.eat_right_anim = self.eat_left_anim.get_transform(flip_x = True)
      
	self.sprite = sprite.Sprite(self.walk_left_anim, batch=parent.batch, group=parent.foreground)
    	
	self.sprite.x = self.pos[0]
        self.sprite.y = self.pos[1]
	
	self.speed = LADYBUG_ACCEL
	self.drag = LADYBUG_DRAG
        self.climb_speed = LADYBUG_CLIMBSPEED
        self.hunger = LADYBUG_HUNGER
        self.weight = LADYBUG_WEIGHT
	
	munch_noise =  resource.media('comiendo2.wav', streaming=False)
	self.munch_player.queue(munch_noise)
	
	step_noise  =  resource.media('patas1.wav', streaming=False)
	self.step_player.queue(step_noise)


                
class Ant(Bug):
    def __init__(self, parent, pos):
        Bug.__init__(self, parent, pos)
        
        #Create sprites
	imgWalk1 = load_image("hormiga1.png")
        imgWalk2 = load_image("hormiga2.png")
        imgWalk3 = load_image("hormiga3.png")
        imgWalk4 = load_image("hormiga4.png")
        self.walk_left_anim = image.Animation(
            [
                image.AnimationFrame(imgWalk1, 0.1),
                image.AnimationFrame(imgWalk2, 0.1),
                image.AnimationFrame(imgWalk3, 0.1),
                image.AnimationFrame(imgWalk4, 0.1),
                image.AnimationFrame(imgWalk3, 0.1),
                image.AnimationFrame(imgWalk2, 0.1),
            ])
        self.walk_right_anim = self.walk_left_anim.get_transform(flip_x = True)
	
        imgEat = load_image("hormigaCome.png")
        self.eat_left_anim = image.Animation(
            [
                image.AnimationFrame(imgEat, 1000),
            ])
	self.eat_right_anim = self.eat_left_anim.get_transform(flip_x = True)

      
	self.sprite = sprite.Sprite(self.walk_left_anim, batch=parent.batch, group=parent.foreground)
    	
	self.sprite.x = self.pos[0]
        self.sprite.y = self.pos[1]
	
	self.speed = ANT_ACCEL
	self.drag = ANT_DRAG
        self.climb_speed = ANT_CLIMBSPEED
        self.hunger = ANT_HUNGER
        self.weight = ANT_WEIGHT
        
	munch_noise =  resource.media('comiendo1.wav', streaming=False)
	self.munch_player.queue(munch_noise)
	
	step_noise  =  resource.media('patas1.wav', streaming=False)
	self.step_player.queue(step_noise)

class Snail(Bug):
    def __init__(self, parent, pos):
        Bug.__init__(self, parent, pos)
        
        #Create sprites
	imgWalk1 = load_image("caracol1.png")
        imgWalk2 = load_image("caracol2.png")
        imgWalk3 = load_image("caracol3.png")
        imgWalk4 = load_image("caracol4.png")
        self.walk_left_anim = image.Animation(
            [
                image.AnimationFrame(imgWalk1, 0.3),
                image.AnimationFrame(imgWalk2, 0.3),
                image.AnimationFrame(imgWalk3, 0.3),
                image.AnimationFrame(imgWalk4, 0.3),
                image.AnimationFrame(imgWalk3, 0.3),
                image.AnimationFrame(imgWalk2, 0.3),
            ])
        self.walk_right_anim = self.walk_left_anim.get_transform(flip_x = True)
	
        imgEat = load_image("caracolCome.png")
        self.eat_left_anim = image.Animation(
            [
                image.AnimationFrame(imgEat, 1000),
            ])
	self.eat_right_anim = self.eat_left_anim.get_transform(flip_x = True)
      
	self.sprite = sprite.Sprite(self.walk_left_anim, batch=parent.batch, group=parent.foreground)
    	
	self.sprite.x = self.pos[0]
        self.sprite.y = self.pos[1]
	
	self.speed = SNAIL_ACCEL
	self.drag = SNAIL_DRAG
        self.climb_speed = SNAIL_CLIMBSPEED
        self.hunger = SNAIL_HUNGER
        self.weight = SNAIL_WEIGHT
	
	munch_noise =  resource.media('comiendo3.wav', streaming=False)
	self.munch_player.queue(munch_noise)
        

class TimedVisual():

    def __init__(self, image, parent, pos, effect, velocity, lifetime):        
        self.effect = effect
        self.velocity = velocity
        self.lifetime = lifetime
        
        img = resource.image(image)
        img.anchor_x = img.width/2
        img.anchor_y = img.width/2
        self.sprite = sprite.Sprite(img, batch = parent.batch, group = parent.visualeffects)
        self.sprite.x = pos[0]
        self.sprite.y = pos[1]
        
        if effect == "move":
            self.sprite.scale = 0.5            
        
        
    def update(self):        
        self.lifetime = self.lifetime-1
        
        if self.effect == "move":
            self.sprite.x = self.sprite.x + self.velocity[0]
            self.sprite.y = self.sprite.y + self.velocity[1]
            self.sprite.opacity = int(self.lifetime*25)
            self.sprite.scale = self.sprite.scale + 0.025
            if self.velocity[0] > 0:
                self.sprite.rotation = (self.sprite.rotation + 50) % 360
            else:
                self.sprite.rotation = (self.sprite.rotation - 50) % 360
            
            
        if self.effect == "rise":
            self.sprite.y = self.sprite.y + 1
            self.sprite.opacity = int(255 - self.lifetime)
            
        if self.effect == "grow":
            if self.lifetime > 40:
                self.sprite.scale = self.sprite.scale + 0.025
                self.sprite.x = self.sprite.x - 1
                self.sprite.y = self.sprite.y - 1
                
        if self.effect == "shake":
            self.sprite.rotation = random.randint(-5, 5)

    def draw(self):
        pass
    
    
        
class GameObjects():
    def __init__(self, parent):
        
        self.grass = None
        self.player = None
        self.bugs = None
        
        #load background chunks
        self.backgr = resource.image("background.png")
	self.backgrb = resource.image("backgroundb.png")
        self.front = resource.image("suelo.png")
        
        self.wind = resource.image("viento.png")
	
	self.dot = resource.image("dot.png")
        self.timed_visuals = []
	
	self.game_over = load_image("GameOver.png")
        
        self.score = 0
        self.next_level = 15
        
        self.n_ants = 0
        self.n_ladybugs = 0
        self.n_snails = 0
        
        
    def update_timed_visuals(self):
        # Update timed visuals
        dummy_list = self.timed_visuals[:]

        for timed_visual in dummy_list:
            timed_visual.update()
            if timed_visual.lifetime <= 0:                                     
                self.timed_visuals.remove(timed_visual)
                del timed_visual


class Audio ():
    def __init__(self, *args, **kwargs):
	self.music_player = media.Player()
	background_music = resource.media('Lawn Fairy Theme.wav', streaming=False)
	self.music_player.eos_action = 'loop'
        self.music_player.queue(background_music)
					       
	self.wind = resource.media('viento1.wav', streaming=False)

        


class GameWindow(window.Window):
       
    def __init__(self, *args, **kwargs):
        
        #Let all of the standard stuff pass through
        window.Window.__init__(self, *args, **kwargs)
        platform = window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()   
        window.Window.set_location(self, screen.width/2 - args[0]/2, screen.height/2 - args[1]/2);
        #gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        #gl.glEnable(gl.GL_BLEND)

        
        #Add DATA directory to resource path
        resource.path.append('./data')
        resource.path.append('./data/sound')
        resource.reindex()
        resource.add_font('PALIMPUS.TTF')
        self.overlay = None
        
        #Batch rendering
        self.batch_bkg = graphics.Batch()
        self.batch = graphics.Batch()
        self.playerlayer = graphics.OrderedGroup(3)
        self.foreground = graphics.OrderedGroup(2)
        self.background = graphics.OrderedGroup(1)
        self.visualeffects = graphics.OrderedGroup(0)
        
        #Game objects
        self.objects = GameObjects(self)
	self.audio = Audio()
    
        self.ft = font.load('Arial', 18)
        self.fps_text = font.Text(self.ft, y=10)
        
        #self.score_text = font.Text(self.ft, x = 20, y=565)
	self.score_text = text.Label('Score:',
            font_name='Arial',
            font_size=18,
            x = 20, 
            y = 575,
            color=(153, 202, 213, 255),
            anchor_x='left',
            anchor_y='center')
        
        self.has_exit = False
	

    
        

    def menu_option(self, option):
        if option == 'Quit':
            #stop sound
            self.has_exit = True
            
        if option == 'Start Game':
	    self.set_mouse_visible(False)
	    self.audio.music_player.play()
            self.start_game()
            
        if option == 'Instructions':
            pass
    
    
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
	    #stop sounds
	    if self.objects.player.wind_sound:
		self.objects.player.wind_sound.stop()
		self.objects.player.wind_sound = None
	    for bug in self.objects.bugs:
		bug.munch_player.pause()
		bug.step_player.pause()
	    self.set_mouse_visible(True)
	    self.audio.music_player.pause()
            if self.overlay == None:
                self.overlay = SimpleMenu(self, 100, 200, 'Lawn Fairy', ['Start Game', 'Quit'])
                
    
    def start_game(self):
        self.clear()
        
        if self.objects.player != None:
            dummy_list = self.objects.grass.blades[:]        
            for blade in dummy_list:
                self.objects.grass.blades.remove(blade)
                del blade
            
            dummy_list = self.objects.bugs[:]        
            for bug in dummy_list:
                self.objects.bugs.remove(bug)
                del bug
            
            self.objects.score = 0
                
            del self.objects.grass
            del self.objects.bugs
            del self.objects.player
        
             #Batch rendering
            self.batch_bkg = graphics.Batch()
            self.batch = graphics.Batch()
            self.playerlayer = graphics.OrderedGroup(3)
            self.foreground = graphics.OrderedGroup(2)
            self.background = graphics.OrderedGroup(1)
            self.visualeffects = graphics.OrderedGroup(0)
        
        
        self.objects.grass = Grass(self)
        self.objects.player = Fairy(self)
        self.objects.bugs = []
        

	
	self.objects.bugs.append (Ant(self, [0,50]))
	
        self.objects.n_ants = 1
        self.objects.n_ladybugs = 0
        self.objects.n_snails = 0
        
        self.score = 0
        self.next_level = 15

        
        self.push_handlers(self.objects.player)
        
          
    
    def game_objects_update(self, tick):
        wind = self.objects.player.update()
        
        self.objects.grass.update(wind, self.objects.player.pos) #pasar posicion completa
        
        for bug in self.objects.bugs:
            bug.update()
            
        self.objects.update_timed_visuals()
        
        self.objects.backgr.blit(0,0)
        self.objects.grass.draw()
        self.batch.draw()
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_BLEND)
        self.objects.front.blit(0,0)
	
	#draw wind reserve
	n_dots = int(self.objects.player.blow_reserve)
	for i in range(0, n_dots):
	   self.objects.dot.blit(700 + i, 560)
	
	
        
        
    def score_points(self, score):        
        self.objects.score = self.objects.score + score
        
        #if score increases, there will be more bugs, and harder
        if self.objects.score >= self.objects.next_level:
            self.objects.next_level = self.objects.next_level * 1.5
            
            if self.objects.n_ants < MAX_NUM_ANTS and self.objects.n_ants / (1 + self.objects.n_ladybugs) < 2:
                self.objects.bugs.append (Ant(self, [0,0]))
                self.objects.n_ants = self.objects.n_ants + 1
            else:
                if  self.objects.n_ladybugs < MAX_NUM_LADYBUGS and self.objects.n_ladybugs / (1 + self.objects.n_snails) < 1: 
                    self.objects.bugs.append (LadyBug(self, [0,0]))
                    self.objects.n_ladybugs = self.objects.n_ladybugs + 1
                else:
                    if self.objects.n_snails < MAX_NUM_SNAILS:
                        self.objects.bugs.append (Snail(self, [0,0]))
                        self.objects.n_snails = self.objects.n_snails + 1
                                    
        
        
    
    def main_loop(self):
        global tick 
        self.overlay = SimpleMenu(self, 100, 200, 'Lawn Fairy', ['Start Game', 'Quit'])
        clock.set_fps_limit(25)
        
        while not self.has_exit:   
            self.clear()
                              
            self.dispatch_events()                         
            
            if self.overlay:
                self.overlay.draw()
            else:
                if not self.has_exit:
                    self.game_objects_update(tick)

            clock.tick()

	    if self.overlay == None and self.objects.player != None:
		self.score_text.text = "Score: " + str(self.objects.score)
                self.score_text.draw()
		
		if self.objects.grass.healthy_blades == 0:
		    self.objects.game_over.blit(self.width/2, self.height/2.5)
            
            #Gets fps and draw it    
            self.flip()
            
        if self.objects.player:
            if self.objects.player.wind_sound:
                self.objects.player.wind_sound.stop()
                del self.objects.player.wind_sound
              
            for bug in self.objects.bugs:
                bug.munch_player.pause()
                del bug.munch_player
                bug.step_player.pause()
                del bug.step_player
              
        self.audio.music_player.pause()
        del self.audio.music_player
