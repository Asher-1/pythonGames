import sys, random
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
import math

def draw_ball(screen, ball):
    """Draw a ball shape"""
    #import pdb; pdb.set_trace()
    p = int(ball.body.position.x+ball.offset.x), 600-int(ball.body.position.y+ball.offset.y)
    pygame.draw.circle(screen, THECOLORS["blue"], p, int(ball.radius), 2)

def add_ball(space, add=True):
    """Add a ball to the given space at a random position"""
    radius = 15 if add else 3
    mass = 10 if add else pymunk.inf
    inertia = pymunk.moment_for_circle(mass, 0, radius, (20,0)) + pymunk.moment_for_circle(mass, 0, radius, (-20,0))
    print inertia
    body = pymunk.Body(mass, inertia)

    body.position = random.randint(120,130),random.randint(620,680)
    shape1 = pymunk.Circle(body, radius, (20,0))
    shape2 = pymunk.Circle(body, radius, (-20,5))
    space.add(body, shape1, shape2)
    shape1.collision_type = 2
    shape1.elasticity = 0.9
    shape2.collision_type = 2
    shape2.elasticity = 0.9
    return shape1, shape2

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Springy")
    clock = pygame.time.Clock()
    running = True
    
    pymunk.init_pymunk()
    space = pymunk.Space()
    
    b1, b3 = add_ball(space)
    b1.body.position = (110, 600)
    b1.body.force = ((0,-100))
    b2, b4 = add_ball(space,False)
    b2.body.position = (100,650)
    #c = pymunk.DampedSpring(b1.body, b2.body, (0,0), (0,0), 100, 200, 2.0)
    c = pymunk.PinJoint(b1.body, b2.body, (0,0), (0,0))
    #c = pymunk.PivotJoint(b1.body, b2.body, (5,100), (0,0))
    #space.add(c)
    
    i = pymunk.moment_for_box(pymunk.inf, 200,20)
    b = pymunk.Body(pymunk.inf, i)
    b.position = (0,0)
    s = pymunk.Poly(b, [(0,0), (200,0), (200,50), (0,50)])
    s.collision_type = 2
    s.elasticity = 0.9

    b1.angular_velocity = 0.1
    b2.angular_velocity = 0.1

    space.add(b, s)
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == KEYDOWN and event.key == K_RIGHT:
                #b2.body.position = b2.body.position + pymunk.Vec2d((30,0))
                b2.body.slew(b2.body.position + pymunk.Vec2d((100,0)), 1/50.0)
                space.step(1/50.0)
                b2.body.slew(b2.body.position, 1/50.0)
                
            elif event.type == KEYDOWN and event.key == K_LEFT:
                #b2.body.position = b2.body.position - pymunk.Vec2d((30,0))
                b2.body.slew(b2.body.position - pymunk.Vec2d((100,0)), 1/50.0)
                space.step(1/50.0)
                b2.body.slew(b2.body.position, 1/50.0)

        screen.fill(THECOLORS["white"])
        
        draw_ball(screen, b1)
        draw_ball(screen, b2)
        draw_ball(screen, b3)
        draw_ball(screen, b4)
        #import pdb; pdb.set_trace()
        space.step(1/50.0)
        
        pygame.display.flip()
        clock.tick(500)

        print (b1.body.position - b2.body.position).length, b1.body.angle, b2.body.angle
        
if __name__ == '__main__':
    sys.exit(main())
