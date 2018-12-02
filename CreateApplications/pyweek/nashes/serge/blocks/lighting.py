"""Implements a lighting approach"""

import pygame
import math
import random
import serge.actor
import serge.common
import serge.engine
import serge.visual
import serge.geometry
import serge.blocks.utils
from serge.simplevecs import Vec2d
from serge.geometry import Line, Point


C_LOOP_NONE = 'none'
C_LOOP_PING_PONG = 'ping-pong'
C_LOOP_LOOP = 'loop'


class LightField(serge.actor.Actor):
    """Represents a field of light that will be drawn on top of the screen"""

    blend_mode = pygame.BLEND_RGBA_MULT
    particle_blend_mode = 0
    fade_lights = True
    is_baked = False

    def __init__(self, tag, name, field_size_ratio, fade_amount=0.9):
        """Initialise the light field"""
        super(LightField, self).__init__(tag, name)
        screen_width, screen_height = serge.engine.CurrentEngine().getRenderer().getScreenSize()
        width, height = field_size_ratio * screen_width, field_size_ratio * screen_height
        self.visual = serge.visual.SurfaceDrawing(width, height)
        #
        self.fade_amount = fade_amount
        self.screen_width, self.screen_height = serge.engine.CurrentEngine().getRenderer().getScreenSize()
        #
        self.polygons = []
        self.addPolygon(serge.geometry.Polygon(
            [[0, 0], [screen_width, 0], [screen_width, screen_height], [0, screen_height], [0, 0]]
        ))
        self.lights = []
        self.visual.getSurface().fill((0, 0, 0))
        self.ambient_light = None
        self.baked_light_field = None

    def addPolygon(self, polygon):
        """Set the lines used for geometry"""
        self.polygons.append(polygon)

    def addLight(self, light):
        """Add some lights to the field"""
        self.lights.append(light)

    def addLights(self, lights):
        """Add a number of lights to the screen"""
        for light in lights:
            self.addLight(light)

    def setAmbientLight(self, light):
        """Set an ambient light"""
        self.ambient_light = light

    def clearAmbientLight(self):
        """Clear the ambient light"""
        self.ambient_light = None

    def setBakedLightField(self, baked_lights):
        """Set the visual field of baked lights"""
        scaled_surface = pygame.transform.smoothscale(baked_lights, (self.width, self.height))
        self.baked_light_field = scaled_surface

    def clearBakedLightField(self):
        """Clear the baked lights"""
        self.baked_light_field = None

    def addedToWorld(self, world):
        """The actor was added to the world"""
        super(LightField, self).addedToWorld(world)
        #
        self.world = world
        self.time = 0

    def updateActor(self, interval, world):
        """Update the actor"""
        if not self.is_baked:
            self.updateLightField()

    def updateLightField(self):
        """Update the overlal light field"""
        #
        # Light fade
        if self.fade_lights:
            self.visual.getSurface().fill((
                (255 * self.fade_amount),
                (255 * self.fade_amount),
                (255 * self.fade_amount)),
                special_flags=pygame.BLEND_RGB_MULT
            )
        else:
            self.visual.getSurface().fill((0, 0, 0))
        #
        if self.ambient_light:
            self.visual.getSurface().fill(
                self.ambient_light,
                special_flags=pygame.BLEND_RGB_ADD,
            )
        #
        # Randomly update lights
        for light in self.lights:
            light.drawTo(self)
        #
        if self.baked_light_field:
            self.visual.getSurface().blit(
                self.baked_light_field,
                (0, 0),
                special_flags=pygame.BLEND_RGBA_ADD,
            )

    def renderTo(self, renderer, interval):
        """Render to a surface"""
        surface = renderer.getLayer(self.layer).getSurface()
        enlarged = pygame.transform.smoothscale(self.visual.getSurface(), (self.screen_width, self.screen_height))
        surface.blit(enlarged, (0, 0), special_flags=self.blend_mode)

    def addLightParticle(self, particle_sprite, x, y):
        """Add a light particle at screen coordinates x and y"""
        width, height = particle_sprite.get_size()
        px = x * self.width / self.screen_width - width / 2
        py = y * self.height / self.screen_height - height / 2
        self.visual.getSurface().blit(particle_sprite, (px, py), special_flags=self.particle_blend_mode)

    def drawLines(self):
        """Draw the lines on the screen"""
        self.log.info('Drawing all the object lines to the screen')
        #
        world = serge.engine.CurrentEngine().getCurrentWorld()
        self.lines_display = serge.blocks.utils.addVisualActorToWorld(
            world, 'spike', 'lines-display',
            serge.visual.SurfaceDrawing(self.screen_width, self.screen_height),
            'debug',
            (self.screen_width / 2, self.screen_height / 2),
        )
        for item in self.polygons:
            for line in item.lines:
                pygame.draw.line(
                    self.lines_display.visual.getSurface(),
                    (0, 255, 0),
                    (line.x1, line.y1),
                    (line.x2, line.y2),
                )

    def traceRay(self, ray, particle, distance):
        """Trace a ray to its destination"""
        lx, ly = ray.x1, ray.y1
        #
        intersections = []
        for polygon in self.polygons:
            for line in polygon.getLines():
                intersection = ray.getIntersectingRay(line)
                if intersection:
                    intersections.append((intersection.length, intersection, line))
        #
        # Find the closest intersection
        if intersections:
            intersections.sort()
            end = intersections[0][1].getEndPoint()
            self.drawLightRay(Vec2d(lx, ly), Vec2d(end.x, end.y), particle, distance)

    def drawLightRay(self, start, end, light_particle, distance_range):
        """Draw a light ray"""
        delta = end - start
        number_steps = int(min(delta.length, distance_range) / light_particle.step_size)
        pos = start
        step = delta.normalized() * light_particle.step_size
        #
        for i in range(number_steps):
            fraction = float(i) * light_particle.step_size / distance_range
            self.addLightParticle(light_particle.getSurfaceForDistanceFraction(fraction), pos.x, pos.y)
            pos += step


class Light(serge.common.Loggable):
    """A light that can be added to the display"""

    def __init__(self):
        """Initialise the light"""
        self.addLogger()

    def drawTo(self, light_field):
        """Draw this light to a light field"""
        raise NotImplementedError


class DirectionalLight(Light):
    """Represents a light that shines in a direction"""

    def __init__(self, x, y, intensity, distance, angle, beam_width, particle, randomize_rays=False):
        """Initialise the particle"""
        super(DirectionalLight, self).__init__()
        #
        self.x = x
        self.y = y
        self.particle = particle
        self.intensity = intensity
        self.distance = distance
        self.angle = angle
        self.beam_width = beam_width
        self.randomize_rays = randomize_rays
        self.screen_width, self.screen_height = serge.engine.CurrentEngine().getRenderer().getScreenSize()
        self.particle.calculateParticleSteps(self.intensity)

    def drawTo(self, light_field):
        """Draw this light to a light field"""
        min_angle, max_angle = self.angle - self.beam_width / 2.0, self.angle + self.beam_width / 2.0
        rays_per_frame = max(1, int(float(self.beam_width) / self.particle.degrees_per_ray))
        #
        for i in range(rays_per_frame):
            if self.randomize_rays:
                direction = random.uniform(min_angle, max_angle)
            else:
                direction = float(min_angle + (max_angle - min_angle) * i / rays_per_frame)
            light_ray = Line.fromRadial(self.x, self.y, direction, 10 * self.screen_width)
            light_field.traceRay(light_ray, self.particle, self.distance)

    def setAngle(self, angle):
        """Set the angle of the light"""
        self.angle = angle

    def setIntensity(self, intensity):
        """Set the light intensity"""
        self.intensity = intensity
        self.particle.calculateParticleSteps(intensity)


class Pointlight(Light):
    """A point of light"""

    def __init__(self, x, y, particle, intensity=1.0):
        """Initialise the light"""
        super(Pointlight, self).__init__()
        #
        self.x = x
        self.y = y
        self.particle = particle
        self.intensity = intensity

    def drawTo(self, light_field):
        """Draw to the light field"""
        surface = self.particle.getSurfaceForDistanceFraction(0)
        width, height = surface.get_size()
        light_field.addLightParticle(
            surface,
            self.x - width / 2, self.y - height / 2)

    def setIntensity(self, intensity):
        """Set the intensity"""
        self.intensity = intensity
        self.particle.calculateParticleSteps(intensity)


class LightParticle(serge.visual.Drawing):
    """A particle of light to draw on the screen"""

    def __init__(self, base_sprite_name, size_range=(1.0, 1.0),
                 alpha_range=(1.0, 0.0), max_steps=15, step_size=20, degrees_per_ray=10):
        """Initialise the particle"""
        super(LightParticle, self).__init__()
        #
        self.size_range = size_range
        self.alpha_range = alpha_range
        self.max_steps = max_steps
        self.step_size = step_size
        self.degrees_per_ray = degrees_per_ray
        #
        self.base_sprite = serge.visual.Sprites.getItem(base_sprite_name)
        self.calculateParticleSteps()

    def calculateParticleSteps(self, intensity=1.0):
        """Calculate the images for the particle steps"""
        #
        # Calculate images
        self.images = []
        for i in range(self.max_steps):
            factor = float(i) / (self.max_steps - 1)
            size = factor * (self.size_range[1] - self.size_range[0]) + self.size_range[0]
            fade = intensity * max(0.0, min(1.0, factor * (self.alpha_range[1] - self.alpha_range[0]) + self.alpha_range[0]))
            self.base_sprite.setScale(size)
            surface = self.base_sprite.getSurface().copy()
            surface.fill((255, 255, 255, int(fade * 255)), special_flags=pygame.BLEND_RGBA_MULT)
            self.images.append(surface)

    def getSurfaceForDistanceFraction(self, fraction):
        """Return the surface for the given step"""
        step = int(fraction * (len(self.images) - 1))
        return self.images[step]



class GlowingPointLight(Pointlight):
    """A point light that varies its glow level"""

    def __init__(self, x, y, particle, intensity=1.0, min_intensity=0.0, max_intensity=1.0):
        """Initialise the light"""
        super(GlowingPointLight, self).__init__(x, y, particle, intensity)
        #
        self.min_intensity = min_intensity
        self.max_intensity = max_intensity

    def updateLight(self, interval):
        """Update the light"""
        new_intensity = self.intensity * 0.9 + 0.1 * random.uniform(self.min_intensity, self.max_intensity)
        self.setIntensity(new_intensity)


class LightDolly(serge.actor.Actor):
    """A dolly to move a light along a path"""

    def __init__(self, name, light, path, path_traversal_time, spring_strength, damping,
                 mass=1.0, loop=C_LOOP_NONE, face_velocity=False):
        """Initialise the dolly"""
        super(LightDolly, self).__init__('dolly', name)
        #
        self.path = path
        self.path_traversal_time = path_traversal_time
        self.spring_strength = spring_strength
        self.light = light
        self.damping = damping
        self.mass = mass
        self.loop = loop
        self.face_velocity = face_velocity
        #
        self.velocity = Vec2d(0, 0)
        self.elapsed_time = 0.0

    def updateActor(self, interval, world):
        """Update the path motion"""
        self.elapsed_time += interval / 1000.0
        if self.loop == C_LOOP_NONE:
            path_time = self.elapsed_time
        elif self.loop == C_LOOP_LOOP:
            path_time = self.elapsed_time % self.path_traversal_time
        elif self.loop == C_LOOP_PING_PONG:
            path_time = self.elapsed_time % (2 * self.path_traversal_time)
            if path_time >= self.path_traversal_time:
                path_time = self.path_traversal_time * 2.0 - path_time
        else:
            raise ValueError('Unknown loop type: %s' % self.loop)
        #
        end_point = self.path.getPointAtFraction(min(1.0, path_time / self.path_traversal_time))
        #
        offset = Vec2d(*end_point) - Vec2d(self.light.x, self.light.y)
        force = self.spring_strength * offset - self.damping * self.velocity
        acceleration = force / self.mass
        #
        self.velocity += acceleration * interval / 1000.0
        self.light.x += self.velocity.x * interval / 1000.0
        self.light.y += self.velocity.y * interval / 1000.0
        #
        # Face the way we are going
        if self.face_velocity:
            self.light.setAngle(math.degrees(self.velocity.angle))
