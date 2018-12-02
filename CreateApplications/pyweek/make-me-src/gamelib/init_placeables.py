#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: init_placeables.py 418 2008-04-20 18:28:58Z aholkner $'

import pyglet

import baddies
import globals
import particles
import player
import placeable
import sound

class EquipBodyPart(placeable.ImagePlaceable):
    def __init__(self, name, part):
        width = height = 64 # HACK
        super(EquipBodyPart, self).__init__(name, width, height)
        self.part = part

    def hit(self, placed, cell):
        super(EquipBodyPart, self).hit(placed, cell)
        globals.game.player.equip_part(self.part)
        globals.game.player.update_parts()

def add_part(name, part):
    placeable.placeables[name] = EquipBodyPart(name, part)

add_part('pu_balloon.png', player.balloon_part)
add_part('pu_bigwheel.png', player.bigwheel_part)
add_part('pu_body.png', player.torso_part)
add_part('pu_crablegs.png', player.crab_part)
add_part('pu_lamp.png', player.light_part)
add_part('pu_ninja.png', player.ninja_part)
add_part('pu_swimming.png', player.goggles_part)
add_part('pu_weapon.png', player.spanner_part)
add_part('pu_wheel.png', player.smallwheel_part)
add_part('pu_tail.png', player.flipper_part)
add_part('pu_tophat.png', player.tophat_part)
add_part('pu_winterhat.png', player.jaynehat_part)

class SavePlaceable(placeable.ImagePlaceable):
    DESTROY_ON_HIT = False
    INFLUENCE = True

    def enter(self, placed):
        globals.game.player.can_save = placed

    def leave(self, placed):
        globals.game.player.can_save = None

placeable.placeables['save1.png'] = SavePlaceable('save1.png', 128, 128)

class LightPlaced(placeable.Placed):
    def load(self, batch):
        super(LightPlaced, self).load(batch)
        #self.sprite.scale = 256. / self.placeable.get_image().width

class Light1Placeable(placeable.ImagePlaceable):
    placed_class = LightPlaced

placeable.placeables['lamp.png'] = \
    Light1Placeable('lamp.png', 128, 128)

class TallyPlaceable(placeable.ImagePlaceable):
    def __init__(self, image_name, width, height, tally, sound=None):
        super(TallyPlaceable, self).__init__(image_name, width, height)
        self.tally = tally
        self.sound = sound

    def hit(self, placed, cell):
        super(TallyPlaceable, self).hit(placed, cell)
        globals.game.incr_tally(self.tally)
        x = placed.x + placed.placeable.width // 2
        y = placed.y + placed.placeable.height // 2
        if self.tally == 'box':
            globals.game.add_effect(particles.purple_star_effect, x, y)
        else:
            globals.game.add_effect(particles.star_effect, x, y)
        if self.sound:
            sound.play(self.sound)

    def place(self, x, y):
        if self.tally == 'flower':
            globals.flower_total += 1
        elif self.tally == 'coin':
            globals.coin_total += 1
        return super(TallyPlaceable, self).place(x, y)

placeable.placeables['pu_flowers.png'] = TallyPlaceable(
    'pu_flowers.png', 69, 68, 'flower', 'bell.wav')
placeable.placeables['pu_money.png'] = TallyPlaceable(
    'pu_money.png', 64, 61, 'coin', 'coin.wav')
placeable.placeables['pu_heart.png'] = TallyPlaceable(
    'pu_heart.png', 64, 57, 'box', 'heart.wav')

placeable.placeables['crab.png'] = \
    baddies.CrabBaddie('crab.png', 'crab.anim', 64, 64)
placeable.placeables['jelly.png'] = \
    baddies.JellyBaddie('jelly.png', 'jelly.anim', 64, 64)
placeable.placeables['bird.png'] = \
    baddies.BirdBaddie('bird.png', 'bird.anim', 64, 64)
placeable.placeables['daddy.png'] = \
    baddies.BigDaddyBaddie('daddy.png', 'daddy.anim', 64, 64)
placeable.placeables['tap.png'] = \
    baddies.TapBaddie('tap.png', 64, 64)
placeable.placeables['glarent.png'] = \
    baddies.GlarentBaddie('glarent.png', 'glarent.anim', 64, 64)

placeable.placeables['flipbook_light'] = \
    placeable.AnimPlaceable('flipbook_light', 'robotprint.anim', 64, 64)
placeable.placeables['flipbook_light'].anim_name = 'Light'
placeable.placeables['flipbook_head'] = \
    placeable.AnimPlaceable('flipbook_head', 'robotprint.anim', 64, 64)
placeable.placeables['flipbook_head'].anim_name = 'Head'
placeable.placeables['flipbook_torso'] = \
    placeable.AnimPlaceable('flipbook_torso', 'robotprint.anim', 64, 64)
placeable.placeables['flipbook_torso'].anim_name = 'Torso'
placeable.placeables['flipbook_leg'] = \
    placeable.AnimPlaceable('flipbook_leg', 'robotprint.anim', 64, 64)
placeable.placeables['flipbook_leg'].anim_name = 'BigWheel'

placeable.placeables['flipbook_head_left'] = \
    placeable.ImagePlaceable('arrow_left.png', 64, 64, 'flipbook_head_left')
placeable.placeables['flipbook_torso_left'] = \
    placeable.ImagePlaceable('arrow_left.png', 64, 64, 'flipbook_torso_left')
placeable.placeables['flipbook_leg_left'] = \
    placeable.ImagePlaceable('arrow_left.png', 64, 64, 'flipbook_leg_left')
placeable.placeables['flipbook_head_right'] = \
    placeable.ImagePlaceable('arrow_right.png', 64, 64, 'flipbook_head_right')
placeable.placeables['flipbook_torso_right'] = \
    placeable.ImagePlaceable('arrow_right.png', 64, 64, 'flipbook_torso_right')
placeable.placeables['flipbook_leg_right'] = \
    placeable.ImagePlaceable('arrow_right.png', 64, 64, 'flipbook_leg_right')

placeable.placeables['circle_sound_off'] = \
    placeable.ImagePlaceable('circle.png', 64, 64, 'circle_sound_off')
placeable.placeables['circle_sound_on'] = \
    placeable.ImagePlaceable('circle.png', 64, 64, 'circle_sound_on')
placeable.placeables['circle_music_off'] = \
    placeable.ImagePlaceable('circle.png', 64, 64, 'circle_music_off')
placeable.placeables['circle_music_on'] = \
    placeable.ImagePlaceable('circle.png', 64, 64, 'circle_music_on')
