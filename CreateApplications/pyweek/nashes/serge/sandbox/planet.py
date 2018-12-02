"""Model of a simple planet"""

import serge.engine
import serge.world
import serge.actor
import serge.zone
import serge.render
import serge.builder.builder

import pygame
import random

class PhysicalObject(serge.actor.Actor):
    """A layer on the planet"""



class Plant(PhysicalObject):
    """A plant that grows"""
    
    def __init__(self, colours, rate, grow_prob, spawn_prob, spawn_dist, blue):
        """Initialise the plant"""
        super(PhysicalObject, self).__init__('grass')
        self.colours = colours
        self.growth = 0
        self.rate = rate
        self.grow_prob = grow_prob
        self.spawn_prob = spawn_prob
        self.spawn_dist = spawn_dist
        self.visual = Circular(self.colours, 0, blue)
        self.blue = blue
        
    def updateActor(self, interval, world):
        """Update the actor"""
        #
        self.growth += float(interval)/self.rate
        if self.growth >= len(self.colours):
            # We have died
            self.log.info('Removing dead guy at %d, %d. Left is %d' % (self.x, self.y, len(world.getActors())-1))
            world.removeActor(self)
            return
        #
        self.visual.growth = self.growth
        self.visual.size = self.width
        self.visual.x = self.x
        self.visual.y = self.y
        #
        #if random.random() < self.grow_prob:
        #    self.resizeTo(self.width+1, self.height+1)
        if random.random() < self.spawn_prob*interval:
            new_x = self.x + random.randint(-self.spawn_dist, self.spawn_dist)
            new_y = self.y + random.randint(-self.spawn_dist, self.spawn_dist)
            new = self.__class__(self.colours, self.rate, self.grow_prob, self.spawn_prob, self.spawn_dist, self.blue)
            new.setSpatial(new_x, new_y, random.randint(1, 5), 20)
            new.setLayerName('base')
            world.addActor(new)
            


class Circular(serge.visual.Drawing):
    """Draw things as a circle"""
    
    def __init__(self, colours, size, blue):
        """Initialise the plant"""
        super(serge.visual.Drawing, self).__init__()
        self.colours = colours
        self.growth = 0
        self.size = size
        self.zoom = 1.0
        self.blue = blue
    
    def renderTo(self, interval, surface, (x, y)):
        """Render to the layer"""
        colour_index = min(int(self.growth), len(self.colours)-1)
        colour = list(self.colours[colour_index])
        colour[2] = self.blue
        pygame.draw.circle(surface, tuple(colour), (x, y), self.size*self.zoom)
    
    def scaleBy(self, factor):
        """Scale the image by a factor"""
        self.zoom *= factor
    
engine = serge.engine.Engine()
renderer = engine.getRenderer()
layer = serge.render.Layer('base', 0)
renderer.addLayer(layer)
camera = renderer.getCamera()
camera.setSpatial(0, 0, 600, 600)

world = serge.world.World('surface')
main = serge.zone.Zone()
main.setSpatial(-6000, -6000, 12000, 12000)
main.active = True
world.addZone(main)

engine.addWorld(world)
engine.setCurrentWorld(world)

gc = [(0, i, 0, i) for i in range(255)] + \
     [(i, 255, 0, 255) for i in range(255)] + \
     [(255, 255, 0, 255-i) for i in range(255)]
     
for i in range(20):
    grass = Plant(gc, random.randint(10, 50), 0.01, 0.001/10.0, 10, 100)
    grass.setSpatial(random.randint(200, 400), random.randint(100, 300), random.randint(1, 5), 20)
    grass.setLayerName('base')
    world.addActor(grass)

#engine.run(60)
serge.builder.builder.main(engine)

