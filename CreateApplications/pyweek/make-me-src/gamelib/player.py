#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import pyglet
from pyglet.window import key
from pyglet.gl import *

import anim
import collide
import globals
import sound

_debug = False

class PlayerMovement(object):
    GROUNDED_STATE = True
    MOVEMENT_REQUIRES_GROUND = False # for sound

    def update(self, dt, player):
        facing = player.facing
        moving = False
        if globals.keys[key.RIGHT]:
            facing = 'right'
            moving = True
        if globals.keys[key.LEFT]:
            facing = 'left'
            moving = True
        player.set_anim_variant(facing, moving, player.grounded)

    def collide(self, player):
        # Collide
        bbox = player.get_bbox()
        grounded = False

        if player.deity:
            return

        if _debug:
            globals.game.maps.clear_highlight()

        for map in globals.game.maps.get_maps_for_bbox(bbox):
            if not map.loaded:
                if not map.loading:
                    if _debug:
                        print 'Error: collision against map not loaded or loading.'
                    continue
                globals.game.wait_for_tasks()
                assert map.loaded

            # Show bbox intersecting map cells
            if _debug: 
                for cell in map.get_intersecting_cells(bbox):
                    map.highlight_cell(cell)

            # Bounce off walls/floors/ceilings
            for cell in map.get_intersecting_cells(bbox):
                if cell.tile and cell.tile.solid:
                    dx, dy = bbox.resolve_edges(map.get_cell_bbox(cell))
                    if abs(dx) > map.cell_width // 2 or \
                       abs(dy) > map.cell_height//2:
                        continue
                    player.x += dx
                    player.y += dy
                    if dy * player.dy < 0:
                        # Applied a normal force   
                        player.dy = 0
                    bbox = player.get_bbox()
                    if cell.tile.breakable and player.destructive:
                        player.dx = 0
                        cell.destroy()

        ground_check = bbox.get_ground_check()
        for map in globals.game.maps.get_maps_for_bbox(ground_check):
            # Find ground
            for cell in map.get_intersecting_cells(ground_check):
                if cell.tile and cell.tile.solid:
                    grounded = self.GROUNDED_STATE

        player.set_anim_variant(player.facing, player.moving, grounded)

        # Activate collisions with pickups
        last_influenced = player.influenced
        player.influenced = set()
        for layer in (globals.game.pickups_layer, globals.game.effects_layer):
            for placed in layer.get_intersecting_placed(bbox):
                placed.placeable.hit(placed, layer)

        for hit in player.influenced - last_influenced:
            hit.placeable.enter(hit)
        for hit in last_influenced - player.influenced:
            hit.placeable.leave(hit)

        # Check for water collision
        player.in_water = False
        for map in globals.game.foreground_maps.get_maps_for_bbox(bbox):
            for cell in map.get_intersecting_cells(bbox):
                if cell.tile and cell.tile.water:
                    if not player.waterproof:
                        globals.game.drown_player()
                    else:
                        player.in_water = True
                    return

class WalkPlayerMovement(PlayerMovement):
    MOVE_DY = 0

    FALL_DX = 75

    GRAVITY_DDY = -800
    MAX_GRAVITY_DY = -500

    STOP_ON_GROUND = True
    AIR_CONTROL = True

    def update(self, dt, player):
        if self.STOP_ON_GROUND:
            player.dx = 0
        if not player.grounded:
            player.dy = \
                max(player.dy + dt * self.GRAVITY_DDY, self.MAX_GRAVITY_DY)
            if self.AIR_CONTROL:
                if globals.keys[key.RIGHT]:
                    player.dx += self.FALL_DX
                if globals.keys[key.LEFT]:
                    player.dx -= self.FALL_DX

        player.x += player.dx * dt
        player.y += player.dy * dt

        super(WalkPlayerMovement, self).update(dt, player)

class JumpPlayerMovement(WalkPlayerMovement):
    JUMP_DY = 450

    def update(self, dt, player):
        if player.grounded:
            if globals.keys[key.UP]:
                player.dy = self.JUMP_DY
                sound.play('clunk.wav')
        
        super(JumpPlayerMovement, self).update(dt, player)

class CrabPlayerMovement(JumpPlayerMovement):
    JUMP_DY = 250

    MOVEMENT_REQUIRES_GROUND = True

class SpringPlayerMovement(JumpPlayerMovement):
    JUMP_DY = 430
    FALL_DX = 250

    def update(self, dt, player):
        if player.grounded:
            if globals.keys[key.RIGHT] or globals.keys[key.LEFT]:
                player.dy = self.JUMP_DY
                sound.play('clunk.wav')

        super(SpringPlayerMovement, self).update(dt, player)

class WheelPlayerMovement(JumpPlayerMovement):
    JUMP_DY = 300
    FALL_DX = 150
    ROLL_DDX = 250
    ROLL_FRICTION = 1.

    STOP_ON_GROUND = False
    AIR_CONTROL = False

    def update(self, dt, player):
        if player.grounded:
            moving = False
            if globals.keys[key.RIGHT]:
                player.dx += self.ROLL_DDX * dt
                #player.dx = min(player.dx, self.ROLL_DX)
                moving = True
            if globals.keys[key.LEFT]:
                player.dx -= self.ROLL_DDX * dt
                #player.dx = max(player.dx, -self.ROLL_DX)
                moving = True
            if not moving:
                player.dx -= player.dx * dt
            else:
                player.dx -= player.dx * dt * self.ROLL_FRICTION
            player.x += player.dx * dt

        super(WheelPlayerMovement, self).update(dt, player)

class FloatPlayerMovement(PlayerMovement):
    GROUNDED_STATE = False

    MOVE_DX = 150
    MOVE_DY = 150
          
    def update(self, dt, player):
        super(FloatPlayerMovement, self).update(dt, player)

        dx = 0
        dy = 0
        facing = player.facing
        if globals.keys[key.RIGHT]:
            dx += 1
        if globals.keys[key.LEFT]:
            dx -= 1
        if globals.keys[key.UP]:
            dy += 1
        if globals.keys[key.DOWN]:
            dy -= 1
        
        player.x += dx * dt * self.MOVE_DX
        player.y += dy * dt * self.MOVE_DY

class FlipperPlayerMovement(PlayerMovement):
    FALL_DX = 75

    GRAVITY_DDY = -800
    MAX_GRAVITY_DY = -500

    GROUNDED_STATE = True

    SWIM_DDX = 250
    SWIM_DDY = 250
    SWIM_FRICTION = 1.

    def update(self, dt, player):
        super(FlipperPlayerMovement, self).update(dt, player)
        if player.in_water:
            moving = False
            if globals.keys[key.RIGHT]:
                player.dx += self.SWIM_DDX * dt
                moving = True
            if globals.keys[key.LEFT]:
                player.dx -= self.SWIM_DDX * dt
                moving = True
            if globals.keys[key.UP]:
                player.dy += self.SWIM_DDY * dt
                moving = True
            if globals.keys[key.DOWN]:
                player.dy -= self.SWIM_DDY * dt
                moving = True
            if not moving:
                player.dx -= player.dx * dt
                player.dy -= player.dy * dt
            else:
                player.dx -= player.dx * dt * self.SWIM_FRICTION
                player.dy -= player.dy * dt * self.SWIM_FRICTION
            player.x += player.dx * dt
            player.y += player.dy * dt
        else:
            # Fall
            player.dx = 0
            if not player.grounded:
                player.dy = \
                    max(player.dy + dt * self.GRAVITY_DDY, self.MAX_GRAVITY_DY)
                if globals.keys[key.RIGHT]:
                    player.dx += self.FALL_DX
                if globals.keys[key.LEFT]:
                    player.dx -= self.FALL_DX

            player.x += player.dx * dt
            player.y += player.dy * dt


class DiePlayerMovement(PlayerMovement):
    def update(self, dt, player):
        pass

class DrownPlayerMovement(PlayerMovement):
    DY = -10.

    def update(self, dt, player):
        player.y += dt * self.DY

die_movement = DiePlayerMovement()
drown_movement = DrownPlayerMovement()
 
LOCO_PRIORITIES = dict(
    # Heads
    Head = 1,
    Snorkel = -1,
    Goggles = -1,
    Ninja = -1,
    Light = -1,
    TopHat = -1,
    JayneHat = -1,
    # Torsos
    Torso = -1,
    Balloon = 4,
    Spanner = -1,
    Crab = 2,
    # Legs
    Spring = 3,
    Plunger = 3,
    SmallWheel = 3,
    BigWheel = 3,
    Flipper = 3
)
        
LOCO_MOVEMENTS = dict(
    Head = WalkPlayerMovement(),
    Balloon = FloatPlayerMovement(),
    Crab = CrabPlayerMovement(),
    Spring = SpringPlayerMovement(),
    SmallWheel = WheelPlayerMovement(),
    BigWheel = WheelPlayerMovement(),
    Flipper = FlipperPlayerMovement()
)

LOCO_SOUNDS = dict(
    Head = 'slide.wav',
    Crab = 'click.wav',
    BigWheel = 'squeak.wav',
    SmallWheel = 'squeak.wav',
)

class BodyPart(object):
    def __init__(self, *anims):
        self.anims = anims

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.anims == other.anims

    def __ne__(self, other):
        return self.__class__ != other.__class__ or self.anims != other.anims

head_part = BodyPart('Head')
goggles_part = BodyPart('Head', 'Goggles', 'Snorkel')
ninja_part = BodyPart('Head', 'Ninja')
tophat_part = BodyPart('Head', 'TopHat')
jaynehat_part = BodyPart('Head', 'JayneHat')
light_part = BodyPart('Light')

crab_part = BodyPart('Crab')
torso_part = BodyPart('Torso')
balloon_part = BodyPart('Balloon')
spanner_part = BodyPart('Spanner')

spring_part = BodyPart('Spring')
smallwheel_part = BodyPart('SmallWheel')
flipper_part = BodyPart('Flipper')
bigwheel_part = BodyPart('BigWheel')

head_parts = [
    head_part,
    goggles_part,
    ninja_part,
    tophat_part,
    jaynehat_part,
    #light_part
]

torso_parts = [
    crab_part,
    torso_part,
    spanner_part,
    balloon_part
]

leg_parts = [
    spring_part,
    #smallwheel_part,
    flipper_part,
    bigwheel_part,
]

class Player(object):
    x = -850
    y = 300
    dx = 0
    dy = 0
    grounded = False
    facing = 'right'
    moving = False
    sound_moving = False
    in_water = False

    waterproof = False
    destructive = False
    ninja = False
    deity = False
    dead = False
    have_light = False
    bright = False

    input_disabled = False
    can_save = None

    visible = True

    def __init__(self):
        self.anim_set = anim.AnimSet('Final_P1.anim')
        self.influenced = set()

        self.head_parts = [head_part]
        self.head_part = head_part
        self.torso_parts = [None]
        self.torso_part = None
        self.leg_parts = [None]
        self.leg_part = None

    def update(self, dt):
        self.movement.update(dt, self)

        self.loco_tx, self.loco_ty, self.loco_tr, dx, dy = \
            self.loco_anim_sprite.update(dt, loco=True)
        self.x += dx
        self.y += dy

        for anim_sprite in self.anim_sprites:
            if anim_sprite is self.loco_anim_sprite:
                continue
            anim_sprite.update(dt)

        self.movement.collide(self)

    def save_state(self, d):
        assert 'player' not in d
        d['player'] = v = dict(
            x = self.x,
            y = self.y,
            dx = self.dx,
            dy  = self.dy,
            grounded = self.grounded,
            facing = self.facing,
            moving = self.moving,
            in_water = self.in_water,
            have_light = self.have_light,
            bright = self.bright,
            head_parts = self.head_parts[:],
            head_part = self.head_part,
            torso_parts = self.torso_parts[:],
            torso_part = self.torso_part,
            leg_parts = self.leg_parts[:],
            leg_part = self.leg_part)

    def restore_state(self, d):
        v = d['player']
        self.x = v['x']
        self.y = v['y']
        self.dx = v['dx']
        self.dy = v['dy']
        self.grounded = v['grounded']
        self.facing = v['facing']
        self.moving = v['moving']
        self.in_water = v['in_water']
        self.have_light = v['have_light']
        self.bright = v['bright']
        self.head_parts = v['head_parts'][:]
        self.head_part = v['head_part']
        self.torso_parts = v['torso_parts'][:]
        self.torso_part = v['torso_part']
        self.leg_parts = v['leg_parts'][:]
        self.leg_part = v['leg_part']
        self.visible = True
        self.can_save = True
        self.update_parts()

    def equip_part(self, part):
        if part in head_parts:
            if part not in self.head_parts:
                self.head_parts.append(part)
            self.head_part = part
        elif part in torso_parts:
            if part not in self.torso_parts:
                self.torso_parts.append(part)
            self.torso_part = part
            if not part or part == crab_part:
                self.leg_part = None
            elif self.torso_part == balloon_part:
                # Let's just assume it's equipped.
                self.leg_part = spring_part
            elif self.torso_part not in (crab_part, None) and not self.leg_part:
                self.equip_part(spring_part)
        elif part in leg_parts:
            if part not in self.leg_parts:
                self.leg_parts.append(part)
            if not self.torso_part or \
                    self.torso_part in (crab_part, balloon_part):
                self.equip_part(torso_part)
            self.leg_part = part
        elif part == light_part:
            self.have_light = True

    def equip_all(self):
        for part in head_parts + torso_parts + leg_parts:
            self.equip_part(part)
        #self.have_light = True

    def cycle_head_part(self, dir=1):
        if not self.head_parts:
            return
        index = self.head_parts.index(self.head_part)
        index = (index + dir) % len(self.head_parts)
        self.head_part = self.head_parts[index]
        self.update_parts()

    def cycle_torso_part(self, dir=1):
        if not self.torso_parts:
            return
        index = self.torso_parts.index(self.torso_part)
        index = (index + dir) % len(self.torso_parts)
        self.torso_part = self.torso_parts[index]
        if not self.torso_part or self.torso_part == crab_part:
            self.leg_part = None
        elif self.torso_part not in (crab_part, None) and not self.leg_part:
            self.equip_part(spring_part)
        elif self.torso_part == balloon_part:
            self.leg_part = spring_part
        self.update_parts()

    def cycle_leg_part(self, dir=1):
        if not self.leg_parts:
            return
        if not self.torso_part or self.torso_part == crab_part:
            return
        index = self.leg_parts.index(self.leg_part)
        index = (index + dir) % len(self.leg_parts)
        self.leg_part = self.leg_parts[index]
        if self.torso_part and self.torso_part != crab_part and \
           not self.leg_part:
            if spring_part not in self.leg_parts:
                self.equip_part(spring_part)
            else:
                self.cycle_leg_part(dir)
        if self.torso_part == balloon_part and self.leg_part != spring_part:
            self.torso_part = torso_part
        self.update_parts()

    def set_anim_variant(self, facing, moving, grounded):
        sound_moving = moving and self.move_sound
        if sound_moving and self.movement.MOVEMENT_REQUIRES_GROUND:
            sound_moving = grounded
        if sound_moving:
            sound.start_move(self.move_sound)
        elif not sound_moving:
            sound.stop_move()
        self.sound_moving = sound_moving

        if (facing == self.facing and 
            moving == self.moving and 
            grounded == self.grounded):
            return

        self.facing = facing
        self.moving = moving
        self.grounded = grounded
        self.update_anim_sprites()
        self.update(0)

    def update_parts(self):
        names = []
        if self.leg_part:
            names.extend(self.leg_part.anims)
        if self.torso_part:
            names.extend(self.torso_part.anims)
        if self.head_part:
            names.extend(self.head_part.anims)

        self.bright = False
        if self.have_light and \
           self.head_part not in (tophat_part, jaynehat_part):
            self.bright = True
            names.extend(light_part.anims)

        move_priorities = [(i, LOCO_PRIORITIES[name]) \
                           for i, name in enumerate(names)]
        move_priorities.sort(key=lambda (_, p): p, reverse=True)
        loco_index = move_priorities[0][0]
        self.loco_anim_sprite_index = loco_index
        self.movement = LOCO_MOVEMENTS[names[loco_index]]
        self.move_sound = LOCO_SOUNDS.get(names[loco_index])
        self.sound_moving = False

        self.part_names = names

        self.waterproof = self.head_part == goggles_part
        self.destructive = self.torso_part == spanner_part
        self.ninja = self.head_part == ninja_part

        globals.game.menu_update_flipbook()
        self.update_anim_sprites(check_weight=True)

    def update_anim_sprites(self, check_weight=False):
        self.anim_sprites = [
            anim.AnimSprite(self.anim_set.get(name, 
                                              self.facing, 
                                              self.moving,
                                              self.grounded)) \
            for name in self.part_names
        ]
        self.loco_anim_sprite = self.anim_sprites[self.loco_anim_sprite_index]
        self.loco_tx, self.loco_ty, self.loco_tr, dx, dy = \
            self.loco_anim_sprite.update(0, loco=True)
        self.bbox = self.loco_anim_sprite.anim.bbox

        if not check_weight:
            return

        # Give chance for small offset
        old_x, old_y = self.x, self.y
        self.movement.collide(self)

        # Check bbox against scenery, if we don't fit, start cutting off
        # limbs.
        bbox = self.get_bbox()
        for map in globals.game.maps.get_maps_for_bbox(bbox):
            if not map.loaded:
                if not map.loading:
                    if _debug:
                        print 'Error: collision against map not loaded or loading.'
                    continue
                globals.game.wait_for_tasks()
                assert map.loaded

            # Check for still intersecting, means we can't fit here.
            for cell in map.get_intersecting_cells(bbox):
                if cell.tile and cell.tile.solid:
                    if bbox.intersects(map.get_cell_bbox(cell)):
                        self.x, self.y = old_x, old_y
                        self.lose_weight()
                        return

    def lose_weight(self):
        # player didn't fit in map, cut off limbs and try again
        if self.leg_part and self.leg_part != spring_part:
            if self.torso_part and self.torso_part != crab_part:
                self.leg_part = spring_part
            else:
                self.leg_part = None
        elif self.torso_part:
            self.torso_part = None
            self.leg_part = None
        else:
            # Already just a head, have to abort and live with collision bug
            # (shouldn't happen).
            return
        self.update_parts()

    def try_save_game_state(self):
        if self.can_save:
            globals.game.save_state()
            placed = self.can_save
            placed.sprite.image = pyglet.resource.image('save2.png')
            def restore_flash(dt):
                placed.sprite.image = pyglet.resource.image('save1.png') 
            globals.game.clock.schedule_once(restore_flash, 1.)
            # TODO sound effect
        else:
            # TODO sound effect
            if _debug:
                print 'Cannot save here'
        
    def on_key_press(self, symbol, modifiers):
        if self.input_disabled:
            return pyglet.event.EVENT_UNHANDLED

        if symbol == key._1:
            self.cycle_head_part()
        elif symbol == key._2:
            self.cycle_torso_part()
        elif symbol == key._3:
            self.cycle_leg_part()
        elif symbol == key.S:
            self.try_save_game_state()
        elif symbol == key.D and modifiers & key.MOD_CTRL: # CHEAT
            self.deity = not self.deity
        elif symbol == key.G and modifiers & key.MOD_CTRL: # CHEAT
            self.equip_all()
            self.update_parts()
        else:
            return pyglet.event.EVENT_UNHANDLED
        return pyglet.event.EVENT_HANDLED


    def get_bbox(self):
        return self.bbox.get_translated(int(self.x), int(self.y))

    # layer interface

    def draw(self):
        if not self.visible:
            return

        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.loco_tr, 0, 0, 1)
        glTranslatef(self.loco_tx, self.loco_ty - 8, 0)
        for anim_sprite in self.anim_sprites:
            anim_sprite.draw()
        glPopMatrix()
        #self.get_bbox().draw()

    def update_visibility_bbox(self, bbox):
        pass

    def clear_highlight(self):
        pass

    def save(self):
        pass
