import os
import pymunk
import pygame

import serge.engine
import serge.blocks.utils
import serge.physical
import serge.visual
import serge.sound
import serge.geometry
import serge.events
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors

import theme
G = theme.get
S = theme.theme.setProperty

log = serge.common.getLogger('Game')

engine = serge.engine.Engine()
serge.blocks.utils.createWorldsForEngine(engine, 
['start-screen', 'court-screen', 'end-screen'])
serge.blocks.utils.createVirtualLayersForEngine(engine,
	['background', 'court', 'players', 'objects', 'ui'])

serge.visual.Sprites.setPath(os.path.join('sandbox', 'graphics'))
serge.visual.Sprites.registerItem('ball', 'ball.png')
serge.visual.Sprites.registerItem('ball-a', 'balla.png')
serge.visual.Sprites.registerItem('ball-b', 'ballb.png')
serge.visual.Sprites.registerItem('ball-c', 'ballc.png')
serge.visual.Sprites.registerItem('ball-d', 'balld.png')


world = engine.setCurrentWorldByName('court-screen')

'''
bat = serge.blocks.utils.addVisualActorToWorld(world, 'bat', 'player',
    serge.blocks.visualblocks.Rectangle(G('bat-size'), G('bat-colour')),
    'players', G('bat-initial-position'),
    serge.physical.PhysicalConditions(fixed=True, visual_size=serge.geometry.RECTANGLE, layers=2))
ball = serge.blocks.utils.addSpriteActorToWorld(world, 'ball', 'ball',
    'ball',
    'objects', G('ball-colour'),
    serge.physical.PhysicalConditions(mass=G('ball-mass'), visual_size=serge.geometry.CIRCLE, 
        velocity=G('ball-initial-velocity'), layers=3, update_angle=True,
        force=(G('gravity-x'), G('gravity-y'))))
'''
floor = serge.blocks.utils.addVisualActorToWorld(world, 'wall', 'floor',
    serge.blocks.visualblocks.Rectangle(G('floor-size'), G('floor-colour')),
    'court', G('floor-position'),
    serge.physical.PhysicalConditions(fixed=True, visual_size=serge.geometry.RECTANGLE, layers=1))
ceiling = serge.blocks.utils.addVisualActorToWorld(world, 'wall', 'ceiling',
    serge.blocks.visualblocks.Rectangle(G('ceiling-size'), G('ceiling-colour')),
    'court', G('ceiling-position'),
    serge.physical.PhysicalConditions(fixed=True, visual_size=serge.geometry.RECTANGLE, layers=1))
l_wall = serge.blocks.utils.addVisualActorToWorld(world, 'wall', 'l-wall',
    serge.blocks.visualblocks.Rectangle(G('wall-size'), G('wall-colour')),
    'court', G('wall-l-position'),
    serge.physical.PhysicalConditions(fixed=True, visual_size=serge.geometry.RECTANGLE, layers=1))
r_wall = serge.blocks.utils.addVisualActorToWorld(world, 'wall', 'r-wall',
    serge.blocks.visualblocks.Rectangle(G('wall-size'), G('wall-colour')),
    'court', G('wall-r-position'),
    serge.physical.PhysicalConditions(fixed=True, visual_size=serge.geometry.RECTANGLE, layers=1))
ai_bat = serge.blocks.utils.addVisualActorToWorld(world, 'bat', 'ai',
    serge.blocks.visualblocks.Rectangle(G('bat-size'), G('bat-colour')),
    'players', G('ai-bat-initial-position'),
    serge.physical.PhysicalConditions(fixed=True, visual_size=serge.geometry.RECTANGLE, layers=2))

manager = serge.blocks.behaviours.BehaviourManager('manager')
world.addActor(manager)

S('gravity-x', 100.0)
S('gravity-y', 9800.0)
S('gravity-x', 0.0)
S('gravity-y', 0.0)

b = serge.actor.PhysicallyMountableActor('b', 'b', mass=.0010)
b.visual = serge.blocks.visualblocks.Circle(2, (255,255,255,255))
b.setLayerName('court')
b.moveTo(200,200)

b1 = serge.actor.Actor('b1', 'b1')
b1.setSpriteName('ball-a')
b1.setLayerName('court')
b1.setPhysical(serge.physical.PhysicalConditions(group=1, mass=G('ball-mass'), update_angle=True, 
    visual_size=serge.geometry.CIRCLE, force=(G('gravity-x'), G('gravity-y'))))
b2 = serge.actor.Actor('b2', 'b2')
b2.setSpriteName('ball-b')
b2.setLayerName('court')
b2.setPhysical(serge.physical.PhysicalConditions(group=1, mass=G('ball-mass'), update_angle=True, 
    visual_size=serge.geometry.CIRCLE, force=(G('gravity-x'), G('gravity-y'))))
b3 = serge.actor.Actor('b3', 'b3')
b3.setSpriteName('ball-c')
b3.setLayerName('court')
b3.setPhysical(serge.physical.PhysicalConditions(group=1, mass=G('ball-mass'), update_angle=True, 
    visual_size=serge.geometry.CIRCLE, force=(G('gravity-x'), G('gravity-y'))))
b4 = serge.actor.Actor('b4', 'b4')
b4.setSpriteName('ball-d')
b4.setLayerName('court')
b4.setPhysical(serge.physical.PhysicalConditions(group=1, mass=G('ball-mass'), update_angle=True, 
    visual_size=serge.geometry.CIRCLE, force=(G('gravity-x'), G('gravity-y'))))

b.mountActor(b1, (+30, 0))
b.mountActor(b2, (-30, 0))
b.mountActor(b3, (+80, +20))
b.mountActor(b4, (+40, -40))


world.addActor(b)
world.setPhysicsStepsize(10)
#list(world.zones)[0]._rtf = 0.001

for actor in b.getChildren():
    print actor.name, actor.getPhysical().velocity
    
#j = pymunk.RotaryLimitJoint(b1.getPhysical().body, b2.getPhysical().body, 0, 0)
#b1.getPhysical().space.add(j)
'''
ai_1 = serge.blocks.behaviours.TwoOptions(
    serge.blocks.behaviours.TwoOptions(
        serge.blocks.behaviours.MoveTowardsActor(ball, x_speed=0, y_speed=G('ai-bat-speed')),
        serge.blocks.behaviours.AvoidActor(ball, x_speed=0, y_speed=G('ai-bat-speed'), 
            distance=G('ai-bat-avoid-distance')),
        (ball, ai_bat),
        lambda (ball, ai_bat) : ball.x < ai_bat.x
    ),
    serge.blocks.behaviours.MoveTowardsPoint(G('ai-bat-initial-position'), x_speed=0, y_speed=G('ai-bat-speed')),
    (ball, ai_bat),
    lambda (ball, ai_bat) : abs(ball.x - ai_bat.x) < G('ai-bat-return-distance')
)
ai_2 = serge.blocks.behaviours.TwoOptions(
    serge.blocks.behaviours.TwoOptions(
        serge.blocks.behaviours.MoveTowardsActor(ball, x_speed=0, y_speed=G('ai-bat-speed')),
        serge.blocks.behaviours.AvoidActor(ball, x_speed=0, y_speed=G('ai-bat-speed'), 
            distance=G('ai-bat-avoid-distance')),
        (ball, bat),
        lambda (ball, bat) : ball.x > bat.x
    ),
    serge.blocks.behaviours.MoveTowardsPoint(G('ai-bat-initial-position'), x_speed=0, y_speed=G('ai-bat-speed')),
    (ball, bat),
    lambda (ball, bat) : abs(ball.x - bat.x) < G('ai-bat-return-distance')
)

manager.assignBehaviour(ai_bat, ai_1, 'ball-follow')
manager.assignBehaviour(bat, ai_2, 'ball-follow')
manager.assignBehaviour(bat, serge.blocks.behaviours.KeyboardNSEW(G('bat-speed'), e=None, w=None), 'player-move')

def doBounce(obj, arg):
    if obj.tag == 'wall':
        sound = 'bounce'
    else:
        sound = 'hit'
    
ball.linkEvent(serge.events.E_COLLISION, doBounce)
'''

manager.assignBehaviour(None, serge.blocks.behaviours.KeyboardQuit(), 'quit')


class DoIt(serge.blocks.actors.ScreenActor):
    
    def updateActor(self, interval, world):
        """Update ourself"""
        if self.keyboard.isClicked(pygame.K_LEFT):
            b.setAngle(b.getAngle()+15, True)
            #b1.getPhysical().body.angle += 0.2
            self.log.debug('Moving angle + %d' % b.getAngle())
            #list(world.zones)[0]._rtf = 0.001
        if self.keyboard.isClicked(pygame.K_RIGHT):
            b.setAngle(b.getAngle()-15, True)
            #b1.getPhysical().body.angle += 0.2
            self.log.debug('Moving angle + %d' % b.getAngle())
            #list(world.zones)[0]._rtf = 0.001
        if self.keyboard.isClicked(pygame.K_UP):
            b.move(20,0)
            self.log.debug('Moving %s' % b.x)
        if self.keyboard.isClicked(pygame.K_DOWN):
            b.move(-20,0)
            self.log.debug('Moving %s' % b.x)
        if self.keyboard.isClicked(pygame.K_SPACE):
            for a in b.getChildren():
                self.log.debug('Added gravity to %s' % a)
                a.getPhysical().body.apply_force((10000,90000))
            b.getPhysical().body.apply_force((10000,90000))
            
        self.log.debug('%s, %s, (%s, %s)' % (b.getAngle(), b1.getAngle(), b.getPhysical().body.angle, b1.getPhysical().body.angle))
              
d = DoIt('doit', 'doit')
world.addActor(d)

#import pdb; pdb.set_trace()
engine.run(60)
