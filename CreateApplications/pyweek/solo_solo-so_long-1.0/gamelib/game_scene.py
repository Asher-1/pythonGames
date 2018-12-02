# std lib
import math
import random

# pyglet
import pyglet
from pyglet.gl import *
from pyglet.window.key import *

# cocos
import cocos
from cocos.director import director
from cocos.sprite import *
from cocos import euclid

# pymunk
import pymunk as pm

# locals
from primitives import *
from state import state
import levels
import soundex
import HUD
import gameover

COLL_TYPE_IGNORE, COLL_TYPE_HEAD, COLL_TYPE_BODY, COLL_TYPE_TAIL, COLL_TYPE_GOAL = range(5)


def drawCircle(x, y, r, a):
    segs = 15
    coef = 2.0*math.pi/segs;
    
    glBegin(GL_LINE_LOOP)
    for n in range(segs):
        rads = n*coef
        glVertex2f(r*math.cos(rads + a) + x, r*math.sin(rads + a) + y)
    glVertex2f(x,y)
    glEnd()


def drawCircleShape(circle):
    body = circle.body
    c = body.position + circle.center.cpvrotate(body.rotation_vector)
    drawCircle(c.x, c.y, circle.radius, body.angle)



class GameLayer(cocos.layer.Layer):

    def __init__(self, demo=False, start_level=state.start_level):
        super(GameLayer,self).__init__()

        self.schedule( self.step )

        self.demo_mode = demo

        state.set_level( start_level )
        self.level = state.level

        pm.init_pymunk()
        self.space = pm.Space( iterations=10)

        self.space.gravity = self.level.gravity
        self.space.damping = 0.8

        self.chain = []
        self.goals = []

        self.add_segments()
        self.add_balls()
        
        if not self.demo_mode:
            self.add_goal()
            self.space.add_collisionpair_func( COLL_TYPE_TAIL, COLL_TYPE_GOAL, self.collision_tail_goal, None)
            self.space.add_collisionpair_func( COLL_TYPE_HEAD, COLL_TYPE_GOAL, self.collision_head_goal, None)


    def step(self, dt):

        for elem in self.space.shapes:
            if isinstance(elem, pm.Circle):
                elem.data.position = elem.body.position
                elem.data.rotation = -math.degrees( elem.body.angle )

        self.space.step(dt)

        for body in self.chain:
            body.reset_forces()

        for i,b in enumerate( self.chain):
            if i > 0:
                self.chain[i-1].damped_spring( self.chain[i], (0,0), (0,0), 27.0, 200.0, 50.0, dt)

        for i,goal in enumerate(self.goals):
            goal.reset_forces()
            goal.apply_force( self.level.goals_forces[i], (0,0) )


    # collision detection
    def collision_tail_goal(self, shapeA, shapeB, contacts, normal_coef, data):
#        print shapeA, shapeB
        body,shape,sprite = self.create_body_ball()
        body.position = self.chain[-2].position + (5,5)
        self.attach_ball(body)
        self.chain.insert(-1,body)

        # XXX - removing doesn't work
        shapeB.body.reset_forces()
        shapeB.body.position = (-500,-500)

        self.touched_goal_tail()
        return True

    def collision_head_goal(self, shapeA, shapeB, contacts, normal_coef, data):
#        print shapeA, shapeB
        self.touched_goal_head()
        return True

#    def draw( self ):
#        for elem in self.space.shapes:
#            if isinstance(elem, pm.Circle):
#                self.draw_ball( elem )
#            elif isinstance(elem, pm.Segment):
#                self.draw_segment( elem )
#        pass

    def draw_ball( self, ball ):
#        d = ball.body.position + ball.center.cpvrotate(ball.body.rotation_vector)
#        Circle( d.x, d.y, width=ball.radius*2, color=(1.0,1.0,1.0,1.0)).render()
#        Line( ball.body.position, d, color=(0.5,0.5,1.0,1.0), rotation=0.0 ).render()
        drawCircleShape(ball)

    def draw_segment( self, s ):
        a = s.body.position + s.a 
        b = s.body.position + s.b
        glPushAttrib(GL_CURRENT_BIT)
        Polygon( v=[ a, b ], color=(1.0,0.5,0.5,1.0), stroke=1.0 ).render()
        glPopAttrib()

    def add_segments(self):
        x,y = director.get_window_size()
        
        body = pm.Body(pm.inf, pm.inf)           # mass, inertia
        body.position = (0,0)               #     

        l0 = pm.Segment(body, (-2,-2), (x+2,-2), 5.0)
        l1 = pm.Segment(body, (-2,-2), (-2,y+2), 5.0)
        l2 = pm.Segment(body, (x,-2), (x+2,y+2), 5.0)
        l3 = pm.Segment(body, (-2,y), (x+2,y+2), 5.0)
        l0.friction = 0.2
        l1.friction = 0.2
        l2.friction = 0.2
        l3.friction = 0.2
        l0.elasticity = 0.9
        l1.elasticity = 0.9
        l2.elasticity = 0.9
        l3.elasticity = 0.9
        
        self.space.add_static(l0,l1,l2,l3)

    def add_balls(self):
        """Add a ball to the space space at a random position"""

        if self.demo_mode:
            number_of_balls = 6
        else:
            number_of_balls = self.level.balls
        for i in xrange(number_of_balls):
            if i==0:
                body,shape,sprite = self.create_head_ball()
            elif i==number_of_balls-1:                
                body,shape,sprite = self.create_tail_ball()
            else:
                body,shape,sprite = self.create_body_ball()
            x,y = self.level.head_pos
            body.position = (x+i*10,y)


            if len( self.chain) > 0:
                self.attach_ball( body )

            self.chain.append( body )

    def attach_ball( self, body ):
#        joint = pm.SlideJoint(self.chain[-1], body, (0,0), (0,0), 5, 50)
#        self.space.add( joint )
        pass

    def add_goal(self):
        for goal in self.level.goals_pos:
            body,shape,sprite = self.create_goal_ball()
            body.position = goal
            self.add( sprite, z=-1)
            self.space.add(body, shape)
            self.goals.append( body )

    def create_body_ball(self):
        mass = 2
        radius = 12
        inertia = pm.moment_for_circle(mass, 0, radius, (0,0))
        body = pm.Body(mass, inertia)
        shape = pm.Circle(body, radius, (0,0))
        shape.friction  = 1.5
        shape.elasticity = 1.0
        sprite = Sprite('ball.png')
        shape.collision_type = COLL_TYPE_BODY
        shape.data = sprite

        self.space.add(body, shape)
        self.add( sprite, z=-1 )
        return (body,shape,sprite)

    def create_head_ball(self):
        mass = 5
        radius = 15
        inertia = pm.moment_for_circle(mass, 0, radius, (0,0))
        body = pm.Body(mass, inertia)
        shape = pm.Circle(body, radius, (0,0))
        shape.friction  = 1.0
        shape.elasticity = 0.9
        sprite = Sprite('ball_head.png')
        shape.collision_type = COLL_TYPE_HEAD
        shape.data = sprite

        self.space.add(body, shape)
        self.add( sprite, z=-1 )
        return (body,shape,sprite)

    def create_tail_ball(self):
        mass = 5
        radius = 13
        inertia = pm.moment_for_circle(mass, 0, radius, (0,0))
        body = pm.Body(mass, inertia)
        shape = pm.Circle(body, radius, (0,0))
        shape.friction  = 1.0
        shape.elasticity = 0.9
        sprite = Sprite('ball_tail.png')
        shape.collision_type = COLL_TYPE_TAIL
        shape.data = sprite

        self.space.add(body, shape)
        self.add( sprite, z=-1 )
        return (body,shape,sprite)

    def create_goal_ball(self):
        mass = 20
        radius = 45/2
        inertia = pm.moment_for_circle(mass, 0, radius, (0,0))
        body = pm.Body(mass, inertia)
        shape = pm.Circle(body, radius, (0,0))
        shape.friction  = 1.0
        shape.elasticity = 0.9
        sprite = Sprite('ball_goal.png')
        shape.data = sprite
        shape.collision_type = COLL_TYPE_GOAL

        self.space.add(body, shape)
        self.add( sprite, z=-1 )
        return (body,shape,sprite)


    def touched_goal_tail( self ):
        state.touched_goals += 1
        state.score += 1
        if state.touched_goals == self.level.goals:
            self.next_level()
        soundex.play('Gong_do.mp3')

    def touched_goal_head( self ):
        self.parent.get('ctrl').game_over()

    def next_level( self ):
        if state.state == state.STATE_PLAY:
            if state.level_idx == len( levels.levels) -1:
                self.parent.get('ctrl').you_win()
            else:
                self.parent.get('ctrl').next_level()


class ControlLayer( cocos.layer.Layer ):

    is_event_handler = True     #: enable pyglet's events
   
    def __init__(self, model):
        super(ControlLayer,self).__init__()
        self.model = model

        self.schedule_interval( self.delay_start, 1.1 )
        self.schedule_interval( self.time_callback, 1.0 )

        self.keys_pressed = set()

    def time_callback( self, dt ):
        if state.state == state.STATE_PLAY:
            state.time = state.time - 1
            if state.time < 0:
                state.time = 0
                self.game_over()

    def delay_start( self, dt ):
        if state.state == state.STATE_PAUSE:
            self.unschedule( self.delay_start )
            soundex.set_music('Sick Ted.mp3')
            soundex.play_music()
            state.state = state.STATE_PLAY

    def game_over(self):
        if state.state == state.STATE_PLAY:
            state.state = state.STATE_OVER
            self.parent.add( gameover.GameOver( win=False) , z=10 )

    def you_win(self):
        if state.state == state.STATE_PLAY:
            state.state = state.STATE_WIN
            self.parent.add( gameover.GameOver( win=True) , z=10 )

    def on_exit(self):
        super(ControlLayer,self).on_exit()
        soundex.stop_music()

    def update_keys(self):
        v = euclid.Vector2( 0, 0)
        
        for key in self.keys_pressed:
            if key == LEFT:
                v += (-1,0)
            elif key == RIGHT:
                v += (1,0)
            elif key == UP:
                v += (0,1)
            elif key == DOWN:
                v += (0,-1)

        v = v.normalize()
        v = v * 50
        self.model.chain[0].apply_impulse(v, (0,0) )

    def on_key_press (self, key, modifiers):
        if state.state == state.STATE_PLAY:
            if key in (LEFT, RIGHT, UP, DOWN):
                self.keys_pressed.add(key)
                self.update_keys()
                return True 
        return False 

    def on_key_release (self, key, modifiers):
        if state.state == state.STATE_PLAY:
            if key in (LEFT, RIGHT, UP, DOWN):
                try:
                    self.keys_pressed.remove(key)
                    self.update_keys()
                except KeyError:
                    self.keys_pressed = set()
                return True 
        return False 


    def on_text_motion(self, motion):
        if state.state == state.STATE_PLAY:
            if motion in ( MOTION_UP, MOTION_DOWN, MOTION_LEFT, MOTION_RIGHT ):
                self.update_keys()
                return True
        return False

    def next_level( self ):
        state.score += 5 + state.time // 2
        self.parent.remove( self.model )
        self.model = GameLayer(demo=False, start_level=state.level_idx + 1)
        self.parent.add( self.model )
        self.parent.get('hud').show_message( 'Lvl %d: %s' % (state.level_idx, state.level.title) )

        state.start_level = max( state.start_level, state.level_idx )

    def restart_level( self ):
        state.score = 0
        self.parent.remove( self.model )
        self.model = GameLayer(demo=False, start_level=state.level_idx )
        self.parent.add( self.model )
        self.parent.get('hud').show_message( 'Lvl %d: %s' % (state.level_idx, state.level.title) )
        state.state = state.STATE_PLAY
        self.keys_pressed = set()


def get_game_scene():
    state.reset()

    s = cocos.scene.Scene()
    s.add( HUD.BackgroundLayer(), z=-1 )
    hud = HUD.HUD()
    s.add( hud, z=1, name='hud' )
    gameModel = GameLayer(demo=False, start_level=state.start_level)
    s.add( gameModel, z=0 )
    s.add( ControlLayer( gameModel), z=0, name='ctrl' )
    hud.show_message( 'Lvl %d: %s' % (state.level_idx, state.level.title) )
    return s
