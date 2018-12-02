from monster import MonsterPart
from vector import v

class Connector(MonsterPart):
    imagename = "connector"
    fullname = "articulated connector"
    can_be_root = True
    heart_strength = 500
    blood_use = 5
    max_damage = 30
    speed = -1

# Act 1, The green and pleasant land of rubbish monsters.
# Cat, snake, goat.

class CatHead(MonsterPart):
    imagename = "cat_head"
    fullname = "cat head"
    force_down = 270
    blood_use = 20
    max_damage = 5
    mystery = 2
    jaws = 1
    eyes = 2

class CatBody(MonsterPart):
    imagename = "cat_body"
    fullname = "cat body"
    force_down = 270
    can_be_root = True
    heart_strength = 100
    blood_use = 50
    max_damage = 10
    speed = 5
    power = 3
    vitality = 1
    mystery = 1
    legs = 4

class GoatHead(MonsterPart):
    imagename = "goat_head"
    fullname = "goat head"
    force_down = 270
    blood_use = 50
    max_damage = 10
    ideal_angle = 0
    angle_range = 90
    power = 8
    vitality = 2
    jaws = 1
    horns = 2
    eyes = 2

class GoatAnterior(MonsterPart):
    imagename = "goat_anterior"
    fullname = "goat anterior"
    force_down = 270
    can_be_root = True
    heart_strength = 300
    angle_range = 45
    blood_use = 60
    max_damage = 10
    speed = 2
    power = 2
    vitality = 6
    mystery = 2
    legs = 2
    
class GoatPosterior(MonsterPart):
    imagename = "goat_posterior"
    fullname = "goat posterior"
    force_down = 270
    blood_use = 60
    angle_range = 45
    max_damage = 10
    speed = 4
    power = 2
    vitality = 4
    mystery = 2
    legs = 2
    
class GoatTail(MonsterPart):
    imagename = "goat_tail"
    fullname = "goat tail"
    force_down = 270
    blood_use = 10
    max_damage = 5
    mystery = 2
    tails = 0 # not suitable for whipping or otherwise attacking with

class SnakeHead(MonsterPart):
    imagename = "snake_head"
    fullname = "snake head"
    can_be_root = True
    force_down = 270
    blood_use = 50
    max_damage = 10
    heart_strength = 200
    power = 1
    speed = 5
    mystery = 4
    heads = 1
    jaws = 1
    eyes = 1

class SnakeSegment(MonsterPart):
    imagename = "snake_body"
    fullname = "snake segment"
    blood_use = 20
    max_damage = 5
    speed = 4
    coils = 1

class SnakeCoil(MonsterPart):
    imagename = "snake_coil"
    fullname = "snake coil"
    blood_use = 50
    max_damage = 10
    speed = 3
    power = 4
    vitality = 2
    mystery = 1
    coils = 1

class SnakeTail(MonsterPart):
    imagename = "snake_tail"
    fullname = "snake tail"
    blood_use = 40
    max_damage = 5
    speed = 6
    power = 2
    tails = 1
    force_down = 270

# Act 2, The volcano of awesome monsters.
# Bear, Giraffe, Zebra, Lion. Eagle and Owl head.

class BearHead(MonsterPart):
    imagename = "bear_head"
    fullname = "bear head"
    blood_use = 70
    max_damage = 20
    power = 5
    vitality = 9
    heads = 1
    jaws = 1
    eyes = 2

class AngeyBearHead(MonsterPart):
    imagename = "angry_bear_head"
    fullname = "angry bear head"
    blood_use = 80
    max_damage = 20
    power = 7
    vitality = 9
    heads = 1
    jaws = 1
    eyes = 2

class BearBody(MonsterPart):
    imagename = "bear_body"
    fullname = "bear torso"
    can_be_root = True
    blood_use = 80
    max_damage = 30
    heart_strength = 500
    speed = 4
    power = 6
    vitality = 6
    
class BossBearBody(BearBody):
    heart_strength = 1000
    loot_chance = 0
    max_damage = 100
    speed = 14

class BearArm(MonsterPart):
    imagename = "bear_arm"
    fullname = "bear arm"
    force_down = 270
    blood_use = 60
    max_damage = 10
    power = 4
    vitality = 5
    speed = 3
    arms = 1
    hands = 1

class BearLeg(MonsterPart):
    imagename = "bear_leg"
    fullname = "bear foot"
    force_down = 270
    blood_use = 40
    max_damage = 10
    vitality = 1
    power = 3
    speed = 4
    legs = 1

class GiraffeHead(MonsterPart):
    imagename = "giraffe_head"
    fullname = "giraffe head"
    force_down = 270
    blood_use = 80
    max_damage = 20
    power = 3
    speed = 2
    vitality = 3
    mystery = 8
    jaws = 1
    horns = 2
    eyes = 2

class GiraffeAnterior(MonsterPart):
    imagename = "giraffe_anterior"
    fullname = "giraffe anterior"
    force_down = 270
    can_be_root = True
    heart_strength = 400
    blood_use = 80
    max_damage = 30
    speed = 6
    power = 3
    vitality = 3
    mystery = 4
    legs = 2
    
class GiraffePosterior(MonsterPart):
    imagename = "giraffe_posterior"
    fullname = "giraffe posterior"
    force_down = 270
    blood_use = 80
    max_damage = 30
    mystery = 2
    power = 4
    vitality = 4
    speed = 6
    legs = 2
    
class GiraffeTail(MonsterPart):
    imagename = "giraffe_tail"
    fullname = "giraffe tail"
    force_down = 270
    blood_use = 30
    max_damage = 5
    mystery = 6
    tails = 0 # not suitable for whipping or otherwise attacking with

class ZebraHead(MonsterPart):
    imagename = "zebra_head"
    fullname = "zebra head"
    force_down = 270
    blood_use = 30
    max_damage = 20
    power = 1
    vitality = 2
    mystery = 3
    jaws = 1
    eyes = 2

class ZebraAnterior(MonsterPart):
    imagename = "zebra_anterior"
    fullname = "zebra anterior"
    force_down = 270
    can_be_root = True
    heart_strength = 400
    blood_use = 80
    max_damage = 30
    speed = 6
    power = 4
    vitality = 4
    mystery = 2
    legs = 2
    
class ZebraPosterior(MonsterPart):
    imagename = "zebra_posterior"
    fullname = "zebra posterior"
    force_down = 270
    blood_use = 80
    max_damage = 30
    power = 4
    vitality = 4
    mystery = 2
    speed = 6
    legs = 2
    
class ZebraTail(MonsterPart):
    imagename = "zebra_tail"
    fullname = "zebra tail"
    force_down = 270
    blood_use = 30
    max_damage = 5
    mystery = 4
    vitality = 2
    tails = 0 # not suitable for whipping or otherwise attacking with

class LionHead(MonsterPart):
    imagename = "lion_head"
    fullname = "lion head"
    force_down = 270
    blood_use = 80
    max_damage = 30
    power = 6
    vitality = 6
    speed = 4
    jaws = 1
    eyes = 2

class LionAnterior(MonsterPart):
    imagename = "lion_anterior"
    fullname = "lion anterior"
    force_down = 270
    can_be_root = True
    heart_strength = 500
    blood_use = 100
    max_damage = 30
    speed = 4
    power = 8
    mystery = 2
    vitality = 6
    legs = 2
    
class LionPosterior(MonsterPart):
    imagename = "lion_posterior"
    fullname = "lion posterior"
    force_down = 270
    blood_use = 100
    max_damage = 30
    power = 10
    vitality = 6
    speed = 4
    legs = 2
    
class LionTail(MonsterPart):
    imagename = "lion_tail"
    fullname = "lion tail"
    force_down = 270
    blood_use = 40
    max_damage = 5
    vitality = 4
    power = 2
    mystery = 2
    tails = 0 # not suitable for whipping or otherwise attacking with

class EagleHead(MonsterPart):
    imagename = "eagle_head"
    fullname = "eagle head"
    blood_use = 80
    max_damage = 30
    speed = 4
    mystery = 4
    power = 4
    vitality = 4
    beaks = 1
    eyes = 2
    
class OwlHead(MonsterPart):
    imagename = "owl_head"
    fullname = "owl head"
    blood_use = 80
    max_damage = 30
    mystery = 16
    beaks = 1
    eyes = 2

class DragonHead(MonsterPart):
    imagename = "dragon_head"
    fullname = "dragon head"
    blood_use = 150
    max_damage = 50
    power = 10
    vitality = 10
    mystery = 10
    heads = 1
    jaws = 1
    eyes = 2
    horns = 3
    fins = 2

class DragonWing(MonsterPart):
    imagename = "dragon_wing"
    fullname = "dragon wing"
    blood_use = 0
    max_damage = 30
    speed = 8
    draw_layer = -1
    
class DragonBody(MonsterPart):
    imagename = "dragon_body"
    fullname = "dragon torso"
    can_be_root = True
    blood_use = 0
    max_damage = 100
    heart_strength = 2000
    speed = 10
    power = 10
    vitality = 10
    mystery = 10

class DragonArm(MonsterPart):
    imagename = "dragon_arm"
    fullname = "dragon arm"
    force_down = 270
    blood_use = 0
    max_damage = 40
    power = 5
    arms = 1
    hands = 1

class DragonFoot(MonsterPart):
    imagename = "dragon_foot"
    fullname = "dragon foot"
    force_down = 270
    blood_use = 0
    max_damage = 30
    vitality = 5
    legs = 1

class DragonTail(MonsterPart):
    imagename = "dragon_tail"
    fullname = "dragon tail"
    force_down = 270
    blood_use = 0
    max_damage = 20
    mystery = 10
    tails = 1
    
# Act 3, The island of aquatic monsters, and also elephants!
# Crocodile, Octopus, Moshie, Shark, Elephant

class CrocodileHead(MonsterPart):
    imagename = "crocodile_head"
    fullname = "crocodile head"
    force_down = 270
    #force_scale = 4
    blood_use = 100
    max_damage = 50
    power = 15
    vitality = 5
    heads = 1
    jaws = 1
    eyes = 2

class CrocodileAnterior(MonsterPart):
    imagename = "crocodile_anterior"
    fullname = "crocodile anterior"
    force_down = 270
    #force_scale = 4
    can_be_root = True
    blood_use = 200
    max_damage = 100
    heart_strength = 700
    vitality = 10
    power = 10
    speed = 10
    mystery = 10
    legs = 2

class CrocodilePosterior(MonsterPart):
    imagename = "crocodile_posterior"
    fullname = "crocodile posterior"
    force_down = 270
    #force_scale = 4
    blood_use = 150
    max_damage = 100
    power = 10
    speed = 10
    mystery = 5
    vitality = 5
    legs = 2

class CrocodileTail(MonsterPart):
    imagename = "crocodile_tail"
    fullname = "crocodile tail"
    force_down = 270
    #force_scale = 4
    blood_use = 50
    max_damage = 50
    speed = 5
    mystery = 5
    tails = 1

class QuadropusBody(MonsterPart):
    imagename = "quadropus_body"
    fullname = "purple mollusc body"
    blood_use = 150
    can_be_root = True
    heart_strength = 600
    max_damage = 100
    speed = 8
    power = 6
    vitality = 6
    mystery = 10
    eyes = 2
    
class Tentacle1(MonsterPart):
    imagename = "tentacle_long"
    fullname = "tentacle"
    blood_use = 100
    max_damage = 50
    power = 8
    speed = 4
    mystery = 8
    coils = 1
    tendrils = 1
    
class Tentacle2(MonsterPart):
    imagename = "tentacle_short"
    fullname = "tentacle"
    blood_use = 50
    max_damage = 30
    power = 4
    speed = 4
    mystery = 2
    coils = 1
    tendrils = 1

class SharkHead(MonsterPart):
    imagename = "shark_head"
    fullname = "shark head"
    force_down = 270
    blood_use = 150
    max_damage = 80
    power = 10
    vitality = 5
    mystery = 10
    speed = 5
    jaws = 1
    eyes = 2

class SharkBody(MonsterPart):
    imagename = "shark_body"
    fullname = "shark body"
    force_down = 270
    can_be_root = True
    heart_strength = 700
    blood_use = 200
    max_damage = 100
    speed = 15
    power = 15
    mystery = 5
    vitality = 5
    fins = 2
    
class SharkTail(MonsterPart):
    imagename = "shark_tail"
    fullname = "shark tail"
    force_down = 270
    blood_use = 150
    max_damage = 80
    power = 5
    vitality = 8
    speed = 10
    mystery = 7
    tails = 1

class MoshieHead(MonsterPart):
    imagename = "moshie_head"
    fullname = "pliosaur head"
    force_down = 270
    blood_use = 150
    max_damage = 80
    power = 5
    vitality = 10
    mystery = 10
    speed = 5
    jaws = 1
    eyes = 2

class MoshieAnterior(MonsterPart):
    imagename = "moshie_anterior"
    fullname = "pliosaur body"
    force_down = 270
    can_be_root = True
    heart_strength = 600
    blood_use = 200
    max_damage = 100
    speed = 15
    power = 5
    vitality = 10
    mystery = 10
    fins = 1

class MoshiePosterior(MonsterPart):
    imagename = "moshie_posterior"
    fullname = "pliosaur posterior"
    force_down = 270
    blood_use = 100
    max_damage = 50
    speed = 5
    power = 5
    vitality = 5
    mystery = 5
    fins = 1
    
class MoshieTail(MonsterPart):
    imagename = "moshie_tail"
    fullname = "pliosaur tail"
    force_down = 270
    blood_use = 80
    max_damage = 40
    speed = 8
    power = 4
    vitality = 2
    mystery = 2
    tails = 1

class ElephantHead(MonsterPart):
    imagename = "elephant_head"
    fullname = "elephant head"
    force_down = 270
    blood_use = 100
    max_damage = 50
    power = 5
    vitality = 10
    mystery = 3
    speed = 2
    jaws = 1
    eyes = 2

class ElephantTrunk(MonsterPart):
    imagename = "elephant_trunk"
    fullname = "elephant trunk"
    force_down = 270
    blood_use = 20
    max_damage = 20
    power = 1
    coils = 1  

class ElephantBody(MonsterPart):
    imagename = "elephant_body"
    fullname = "elephany body"
    force_down = 270
    can_be_root = True
    loot_chance = 0 # never drop
    heart_strength = 1000
    blood_use = 200
    max_damage = 100
    speed = 20
    vitality = 20
    power = 10
    mystery = 10

class ElephantLeg(MonsterPart):
    force_down = 270
    blood_use = 100
    max_damage = 50
    power = 5
    vitality = 8
    speed = 4
    mystery = 3
    legs = 1
    
class ElephantLegBL(ElephantLeg):
    imagename = "elephant_leg_bl"
    fullname = "back left elephant leg"
    
class ElephantLegBR(ElephantLeg):
    imagename = "elephant_leg_br"
    fullname = "back right elephant leg"

class ElephantLegFL(ElephantLeg):
    imagename = "elephant_leg_fl"
    fullname = "front left elephant leg"

class ElephantLegFR(ElephantLeg):
    imagename = "elephant_leg_fr"
    fullname = "front right elephant leg"
    
class ElephantTail(MonsterPart):
    imagename = "elephant_tail"
    fullname = "elephant tail"
    force_down = 270
    blood_use = 100
    max_damage = 60
    mystery = 8
    power = 4
    vitality = 5
    speed = 3
    tails = 0 # not suitable for whipping or otherwise attacking with

# Act 4, The green and pleasant land of HOLY COW THERE ARE ROBOTS EVERYWHERE
# All the robot pieces ever.

class RobotHead(MonsterPart):
    imagename = "robot_head"
    fullname = "robot head"
    blood_use = 75
    max_damage = 100
    power = 8
    vitality = 8
    speed = 8
    heads = 1
    jaws = 1
    eyes = 5

class RobotBody(MonsterPart):
    imagename = "robot_body"
    fullname = "robot torso"
    can_be_root = True
    blood_use = 100
    max_damage = 150
    heart_strength = 1000
    speed = 8
    power = 8
    vitality = 8
    mystery = 8
    power = 1

class CrappyRobotBody(RobotBody):
    speed = -10
    loot_chance = 0
    
class RobotArmLarge(MonsterPart):
    imagename = "robot_arm_large"
    fullname = "robot smasher arm"
    force_down = 270
    blood_use = 60
    max_damage = 80
    power = 8
    vitality = 4
    mystery = 4
    arms = 1
    hands = 1

class RobotStructure(MonsterPart):
    imagename = "robot_structure"
    fullname = "mechanical structure"
    force_down = 270
    blood_use = 50
    max_damage = 60
    power = 4
    vitality = 4
    mystery = 4

class RobotFoot(MonsterPart):
    imagename = "robot_foot"
    fullname = "robot foot"
    force_down = 270
    blood_use = 40
    max_damage = 50
    vitality = 3
    power = 3
    speed = 6
    legs = 1

class RobotArm(MonsterPart):
    imagename = "robot_arm"
    fullname = "robotic claw"
    force_down = 45
    blood_use = 30
    max_damage = 40
    power = 2
    speed = 8
    vitality = 2
    hands = 1
    arms = 1
    spikes = 1

class RocketEngine(MonsterPart):
    imagename = "rocket_engine"
    fullname = "rocket engine"
    force_down = 270
    blood_use = 100
    max_damage = 80
    speed = 10
    power = 8
    mystery = 8

class FLaser(MonsterPart):
    imagename = "f_laser"
    fullname = "pulse laser"
    force_down = 270
    blood_use = 100
    max_damage = 80
    speed = 8
    sparks = 5

class Pipe(MonsterPart):
    imagename = "pipe"
    fullname = "metal pipe"
    blood_use = 80
    max_damage = 60
    vitality = 8
    power = 8
    mystery = -1

class Fuse(MonsterPart):
    imagename = "fuse"
    fullname = "87-amp fuse"
    blood_use = 100
    max_damage = 80
    power = 6
    vitality = 12
    mystery = 6
    sparks = 1

class Spring(MonsterPart):
    imagename = "spring"
    fullname = "hyper tension spring"
    blood_use = 50
    max_damage = 40
    power = 4
    speed = 8
    mystery = 4
    coils = 1

class TriConnector(MonsterPart):
    imagename = "tri_connector"
    fullname = "triple connector"
    blood_use = 80
    max_damage = 40
    mystery = 1

class PipeLarge(MonsterPart):
    imagename = "pipe_large"
    fullname = "mega pipe"
    blood_use = 100
    max_damage = 30
    power = 5
    vitality = 8
    speed = 5

class TConnector(MonsterPart):
    imagename = "t_connector"
    fullname = "T-connector"
    blood_use = 80
    max_damage = 30

class ConnectorT(MonsterPart):
    imagename = "connector_t"
    fullname = "T-connector"
    blood_use = 80
    max_damage = 30

class ConnectorCorner(MonsterPart):
    imagename = "connector_corner"
    fullname = "corner connector"
    blood_use = 60
    max_damage = 30
    power = 5
    
class CoverLarge(MonsterPart):
    imagename = "cover_large"
    fullname = "large cover"
    blood_use = 10
    max_damage = 10
    vitality = 2
    
class CoverSmall(MonsterPart):
    imagename = "cover_small"
    fullname = "small cover"
    blood_use = 10
    max_damage = 10
    power = 2
    
class IgorHead(MonsterPart):
    imagename = "igor"
    fullname = "transplanted head of upstart assistant"
    blood_use = 200
    max_damage = 200
    heart_strength = 50000
    can_be_root = True
    speed = -30
    mystery = 100
