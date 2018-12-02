'''
Created on 12.09.2011

'''

# rtti, dont now if isinstance is fast
class ARCHETYPE:
    UNKNOWN = 0
    TOWER = 1
    CREEP = 2
    SPAWNER = 3
    BULLET = 4
    MARKABLE = 5

class DAMAGETYPE:
    UNKNOWN = 0
    GATLING = 1
    TANK = 2
    ARTILLERY = 3
    
class BASE_TOWER:
    SHOTS_PER_SECOND = 4.0
    RADIUS = 150.0
    TEXTURE_BODY = "tower_bunker_body.png"
    TEXTURE_TOWER = "tower_bunker_tower.png"
    
class BUNKER:
    SHOTS_PER_SECOND = 6.0
    RADIUS = 100.0
    TEXTURE_BODY = "tower_bunker_body.png"
    TEXTURE_TOWER = "tower_bunker_tower.png"

class GATLINGBALL:
    TEXTURE = "bullet_gatling.png"
    SHOT_SOUND = "tower_bunker_shoot"
    IMPACT_SOUND = "tower_bunker_shoot"
    BULLET_SPEED = 650
    BULLET_DAMAGE = 168
    DAMAGE_TYPE = DAMAGETYPE.GATLING
    
class TANK:
    SHOTS_PER_SECOND = 1
    RADIUS = 100.0
    TEXTURE_BODY = "tower_tank_body.png"
    TEXTURE_TOWER = "tower_tank_tower.png"

class CANNONBALL:
    TEXTURE = "bullet_cannonball.png"
    SHOT_SOUND = "tower_tank_shoot_01"
    IMPACT_SOUND = "tower_tank_hit_01"
    BULLET_SPEED = 550
    BULLET_DAMAGE = 1008
    DAMAGE_TYPE = DAMAGETYPE.TANK
    
class ARTILLERY:
    SHOTS_PER_SECOND = 1
    RADIUS = 166.0
    TEXTURE_BODY = "tower_artillery_body.png"
    TEXTURE_TOWER = "tower_artillery_tower.png"

class GRENADE:
    TEXTURE = "bullet_grenade.png"
    SHOT_SOUND = "tower_artillery_shoot"
    IMPACT_SOUND = "tower_tank_hit_01"
    BULLET_SPEED = 500
    BULLET_DAMAGE = 1008
    DAMAGE_TYPE = DAMAGETYPE.ARTILLERY

class BASE_BULLET:
    TEXTURE = ""
    SHOT_SOUND = ""
    HIT_SOUND = ""
    BULLET_SPEED = 1
        
class BASE_SPAWNER:
    TEXTURE = "building_beergarden.png"
    SPAWN_COUNT = 1
    SPAWN_LIMIT = 50000
    SPAWN_SOUND = "building_fastfood_01"
    
class FASTFOOD:
    TEXTURE = "building_fastfood.png"
    SPAWN_COUNT = 1
    SPAWN_SOUND = "building_fastfood_01"
    ZONK_SOUND = "zonk"
    SPAWN_LIMIT_TYPE = "FASTFOOD"

class FATSO:
    TEXTURE = "creep_fatso.png"
    DIE_COLOR = (0.0,0.42,0.18)
    DIE_SOUND = "fatso_die"
    SPEED = 60
    WALK_CYCLE_LENGTH_SPEED = 90.0
    WALK_CYCLE_STRENGTH = 30.0
    LIFE = 5040
    CREEPTYPE = "FATSO"
    SPECIAL_MAX_CARRY = 4
    SPECIAL_USE_THRESHOLD = 0.50 # percent
    SPECIAL_HEALTH_PER_USE = 0.25 # percent
    EAT_SOUND = "fatso_eat"
    DAMAGE_RESISTANCE = { DAMAGETYPE.GATLING    : 0.5,
                          DAMAGETYPE.TANK       : 0.0,
                          DAMAGETYPE.ARTILLERY  : 0.33 }

class ORPHANAGE:
    TEXTURE = "building_orphanage.png"
    SPAWN_COUNT = 4
    SPAWN_SOUND = "building_orphanage"
    ZONK_SOUND = "zonk"
    SPAWN_LIMIT_TYPE = "ORPHANAGE"

class ORPHAN:
    TEXTURE = "creep_orphan.png"
    DIE_COLOR = (0.71,0.79,1.0)
    DIE_SOUND = "orphan_die"
    SPEED = 90
    WALK_CYCLE_LENGTH_SPEED = 35.0
    WALK_CYCLE_STRENGTH = 15.0
    LIFE = 840
    CREEPTYPE = "ORPHAN"
    DAMAGE_RESISTANCE = { DAMAGETYPE.GATLING    : 0.0,
                          DAMAGETYPE.TANK       : 0.55,
                          DAMAGETYPE.ARTILLERY  : 0.30 }

class BEERGARDEN:
    TEXTURE = "building_beergarden.png"
    SPAWN_COUNT = 2
    SPAWN_SOUND = "building_beergarden_01"
    ZONK_SOUND = "zonk"
    SPAWN_LIMIT_TYPE = "BEERGARDEN"

class DRUNK:
    TEXTURE = "creep_drunk.png"
    DIE_COLOR = (0.89,1.0,0.388)
    DIE_SOUND = "drunk_die"
    SPEED = 90
    WALK_CYCLE_LENGTH_SPEED = 75.0
    WALK_CYCLE_STRENGTH = 30.0
    LIFE = 1680
    CREEPTYPE = "DRUNK"
    SPECIAL_MARK_DURATION = 2.0
    SPECIAL_SPEEDUP_FACTOR = 1.5
    EAT_SOUND = "drunk_drink"
    SPECIAL_USE_THRESHOLD = 0.50 # percent
    SPECIAL_HEALTH_PER_USE = 0.25 # percent
    DAMAGE_RESISTANCE = { DAMAGETYPE.GATLING    : 0.33,
                          DAMAGETYPE.TANK       : 0.35,
                          DAMAGETYPE.ARTILLERY  : 0.33 }

class BASE_CREEP:
    TEXTURE = "creep_fatso.png"
    SPEED = 30
    LIFE = 100
    WALK_CYCLE_LENGTH_SPEED = 90.0
    WALK_CYCLE_STRENGTH = 30.0
    CREEPTYPE = "ALL"
    
class FONTS:
    # TODO: change this, not necessarily included in linux and mac i think
    DEFAULT = "AddElectricCity"
    GUI_BUTTON = DEFAULT

class Z_INDICES:
    BACKGROUND = 0
    STREETS = 10
    BUILDING = 12
    TOWER_BODY = 12
    CREEP = 13
    TOWER_BULLET = 14
    TOWER_GUN = 15
    TOWER_BULLET_FLY = 16
    PARTICLES = 17
    BEAUTY = 18
    GUI_OVERLAYS = 254
    GUI_BACK = 255
    GUI_FRONT = 256
    GUI_TEXT = 257