#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: baddies.py 419 2008-04-20 18:49:14Z aholkner $'

import math

import pyglet

import globals
import particles
import placeable
import sound

class StaticBaddie(placeable.ImagePlaceable):
    KILL_ON_HIT = True
    DESTROY_ON_HIT = False

class PlacedMovingBaddie(placeable.AnimPlaced):
    GROUNDED_STATE = True

    dx = dy = 0
    facing_int = -1

    BOUNCE_X = False
    BOUNCE_Y = False
    DESTROY_ON_COLLIDE = False

    NEEDS_WATER = False
    HATES_WATER = False

    def load(self, batch):
        if self.loaded:
            return

        globals.game.clock.schedule(self.update)
        return super(PlacedMovingBaddie, self).load(batch)

    def unload(self):
        if not self.loaded:
            return

        super(PlacedMovingBaddie, self).unload()
        globals.game.clock.unschedule(self.update)

    def update(self, dt):
        grounded = False

        self.x += self.dx * dt 
        self.y += self.dy * dt 
        self.update_bbox()
        bbox = self.bbox

        for map in globals.game.maps.get_maps_for_bbox(bbox):
            if not map.loaded:
                return

            # Bounce off walls/floors/ceilings
            for cell in map.get_intersecting_cells(bbox):
                if cell.tile and cell.tile.solid:
                    dx, dy = bbox.resolve_edges(map.get_cell_bbox(cell))
                    if (dx or dy) and self.DESTROY_ON_COLLIDE:
                        self.destroy()
                    if abs(dx) > map.cell_width // 2 or \
                       abs(dy) > map.cell_height//2:
                        continue
                    self.x += dx
                    self.y += dy
                    if dy * self.dy < 0:
                        # Applied a normal force   
                        if self.BOUNCE_Y:
                            self.dy = -self.dy
                        else:
                            self.dy = 0
                    if dx * self.dx < 0:
                        self.facing_int *= -1
                        self.update_anim()
                        if self.BOUNCE_X:
                            self.dx = -self.dx
                    self.update_bbox()
                    bbox = self.bbox
        
        ground_check = bbox.get_ground_check()
        for map in globals.game.maps.get_maps_for_bbox(ground_check):
            # Find ground
            for cell in map.get_intersecting_cells(ground_check):
                if cell.tile and cell.tile.solid:
                    grounded = self.GROUNDED_STATE

        self.grounded = grounded

        if self.HATES_WATER or self.NEEDS_WATER:
            # Check for water
            water = False
            for map in globals.game.foreground_maps.get_maps_for_bbox(bbox):
                for cell in map.get_intersecting_cells(bbox):
                    water = cell.tile and cell.tile.water
                    break
                if water:
                    break

            if water and self.HATES_WATER:
                self.dy = abs(self.dy)
            elif not water and self.NEEDS_WATER:
                self.dy = -abs(self.dy)

class MovingBaddie(placeable.AnimPlaceable):
    DESTROY_ON_HIT = False
    KILL_ON_HIT = True

    placed_class = PlacedMovingBaddie

class PlacedFallingBaddie(PlacedMovingBaddie):
    GRAVITY_DDY = -800
    MAX_GRAVITY_DY = -800

    def update(self, dt):
        if not self.grounded:
            self.dy = max(self.dy + dt * self.GRAVITY_DDY, self.MAX_GRAVITY_DY)

        super(PlacedFallingBaddie, self).update(dt)

class PlacedWalkingBaddie(PlacedFallingBaddie):
    DX = 30

    def update(self, dt):
        if self.grounded:
            self.dx = self.facing_int * self.DX

        super(PlacedWalkingBaddie, self).update(dt) 

class PlacedFloatingBaddie(PlacedMovingBaddie):
    BOUNCE_X = True
    BOUNCE_Y = True
    dx = -30
    dy = 30

    def update(self, dt):
        super(PlacedFloatingBaddie, self).update(dt) 

class CrabBaddie(MovingBaddie):
    anim_name = 'Crab'
    placed_class = PlacedWalkingBaddie

class PlacedJellyBaddie(PlacedFloatingBaddie):
    NEEDS_WATER = True

class JellyBaddie(MovingBaddie):
    anim_name = 'Jelly'
    placed_class = PlacedJellyBaddie

class PlacedBirdBaddie(PlacedFloatingBaddie):
    HATES_WATER = True

class BirdBaddie(MovingBaddie):
    anim_name = 'Bird'
    placed_class = PlacedBirdBaddie

class PlacedBigDaddyBaddie(PlacedFloatingBaddie):
    BOUNCE_X = False
    dx = 0

    def update(self, dt):
        super(PlacedBigDaddyBaddie, self).update(dt)
        d = self.x - globals.game.player.x 
        if d <= 0:
            facing = -1
        else:
            facing = 1
        if facing != self.facing_int:
            self.facing_int = facing
            self.update_anim()

        self.update_anim

class BigDaddyBaddie(MovingBaddie):
    anim_name = 'Daddy'
    placed_class = PlacedBigDaddyBaddie

class GlarentBaddie(MovingBaddie):
    anim_name = 'Glarent'

    INFLUENCE = True
    KILL_ON_HIT = False

    ROCKET_SPEED = 1000

    placed = None

    def enter(self, placed):
        if globals.game.player.ninja:
            return
        self.x = placed.x
        self.y = placed.y
        self.cake_time()

    def leave(self, placed):
        if self.placed:
            try:
                globals.game.effects_layer.remove_placed(self.placed)
            except ValueError:
                pass
        globals.game.clock.unschedule(self.start_rocket_time)
        globals.game.clock.unschedule(self.rocket_time)
        #globals.game.clock.unschedule(self.cake_time)
    
    def cake_time(self, dt=None):
        globals.game.clock.schedule_once(self.start_rocket_time, 1.5)
        self.placed = placeable.get_placeable('cake.png', 1, 1).place(
            self.x - 200, self.y + 100)
        globals.game.effects_layer.add_placed(self.placed)
        sound.play('bleep.wav')

    def start_rocket_time(self, dt=None):
        globals.game.clock.schedule_interval(self.rocket_time, 0.4)

    def rocket_time(self, dt=None):
        globals.game.effects_layer.remove_placed(self.placed)
        y = self.y + 200
        rocket = rocket_baddie.place(self.x, y)
        dx = globals.game.player.x - self.x
        dy = globals.game.player.y - y
        m = math.sqrt(dx ** 2 + dy ** 2)
        dx *= self.ROCKET_SPEED / m
        dy *= self.ROCKET_SPEED / m
        rocket.dx = dx
        rocket.dy = dy
        rocket.r = math.degrees(math.atan2(dy, dx)) - 90
        globals.game.effects_layer.add_placed(rocket)

class PlacedRocketBaddie(PlacedMovingBaddie):
    DESTROY_ON_COLLIDE = True

    def destroy(self):
        if self.visible:
            globals.game.effects_layer.remove_placed(self)
            globals.game.add_effect(particles.explosion_effect, self.x, self.y)
            sound.play("explosion.wav")
        self.visible = False

class RocketBaddie(MovingBaddie):
    anim_name = 'Rocket'

    KILL_ON_HIT = True

    placed_class = PlacedRocketBaddie

rocket_baddie = RocketBaddie('rocket.png', 'rocket2.anim', 64, 64)

class PlacedTapBaddie(placeable.Placed):
    def load(self, batch):
        if self.sprite: 
            return

        super(PlacedTapBaddie, self).load(batch)
        globals.game.clock.schedule_interval_soft(self.update, 5.)

    def unload(self):
        super(PlacedTapBaddie, self).unload()
        globals.game.clock.unschedule(self.update)

    def update(self, dt):
        if not self.sprite:
            return
        placed = drop_baddie.place(self.x + self.sprite.width//2, self.y - 10)
        placed.dy = -600
        globals.game.effects_layer.add_placed(placed)

class TapBaddie(StaticBaddie):
    KILL_ON_HIT = False

    placed_class = PlacedTapBaddie

class PlacedDropBaddie(PlacedMovingBaddie):
    DESTROY_ON_COLLIDE = True

    def destroy(self):
        if self.visible:
            globals.game.add_effect(particles.splash_effect, self.x, self.y)
            globals.game.effects_layer.remove_placed(self)
            sound.play('drip.wav')
        self.visible = False

class DropBaddie(MovingBaddie):
    anim_name = 'Drop'

    KILL_ON_HIT = True

    placed_class = PlacedDropBaddie

drop_baddie = DropBaddie('drop.png', 'drop.anim', 64, 64)
