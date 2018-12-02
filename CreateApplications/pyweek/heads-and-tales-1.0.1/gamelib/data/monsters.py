from gamelib.monsterparts import *

# prologue monsters

brokendoublegoat=((GoatAnterior, 0, None, None), [((GoatPosterior, 0, 0, None), [((GoatHead, 1, 0, None), [], {})], {}), ((GoatPosterior, 1, 1, None), [((GoatAnterior, 0, 0, None), [((GoatHead, 1, 0, None), [], {})], {})], {})], {'name': "Assistant's Goat"})

brokensnakegoat=((GoatAnterior, 0, None, None), [((GoatPosterior, 0, 0, None), [((SnakeSegment, 1, 0, None), [((CatBody, 1, 0, None), [], {})], {})], {}), ((SnakeCoil, 1, 0, None), [((SnakeCoil, 1, 0, None), [((SnakeHead, 1, 0, None), [], {})], {})], {})], {'name': "Assistant's Hybrid"})

improvedgoat = ((GoatAnterior, 0, None, None), [((GoatPosterior, 0, 0, None), [((SnakeTail, 1, 0, True), [], {})], {}), ((SnakeSegment, 1, 0, None), [((GoatHead, 1, 0, None), [], {})], {})], {'name': 'Improved Goat'})

# act 1 monsters

cat=((CatBody, 0, None, None), [((CatHead, 0, 0, None), [], {})], {'name': u'Cat'})

bigsnake = ((SnakeHead, 0, None, None), [((SnakeCoil, 0, 0, None), [((SnakeCoil, 1, 0, None), [((SnakeSegment, 1, 0, None), [((SnakeTail, 1, 0, None), [], {})], {})], {})], {})], {'name': u'Big Snake'}) # possibly weaker than normal snake

goatcat = ((CatBody, 0, None, None), [((GoatHead, 0, 0, None), [], {})], {'name': u'Goat Cat'})

goat = ((GoatAnterior, 0, None, None), [((GoatPosterior, 0, 0, None), [((GoatTail, 1, 0, None), [], {})], {}), ((GoatHead, 1, 0, None), [], {})], {'name': u'Goat'})

snake = ((SnakeHead, 0, None, None), [((SnakeCoil, 0, 0, None), [((SnakeSegment, 1, 0, None), [((SnakeTail, 1, 0, None), [], {})], {})], {})], {'name': u'Snake'})

snakegoatboss = ((GoatAnterior, 0, None, None), [((GoatPosterior, 0, 0, None), [((SnakeSegment, 1, 0, None), [((GoatHead, 1, 0, None), [], {})], {})], {}), ((SnakeCoil, 1, 0, True), [((GoatHead, 1, 0, None), [], {})], {})], {'name': u'Mutant Snake-goat'})

goatlion = ((LionAnterior, 0, None, None), [((LionHead, 0, 0, None), [], {}), ((GoatPosterior, 1, 0, None), [((GoatTail, 1, 0, None), [], {})], {})], {'name': u'Goatlion'})

# act 2

bear = ((BearBody, 0, None, None), [((BearHead, 0, 0, None), [], {}), ((BearArm, 1, 0, None), [], {}), ((BearLeg, 2, 0, None), [], {}), ((BearLeg, 3, 0, None), [], {}), ((BearArm, 4, 0, None), [], {})], {'name': u'Bear'})

giraffe = ((GiraffeAnterior, 0, None, None), [((GiraffeHead, 0, 0, None), [], {}), ((GiraffePosterior, 1, 0, None), [((GiraffeTail, 1, 0, None), [], {})], {})], {'name': u'Giraffe'})

zebra = ((ZebraAnterior, 0, None, None), [((ZebraPosterior, 0, 0, None), [((ZebraTail, 1, 0, None), [], {})], {}), ((ZebraHead, 1, 0, None), [], {})], {'name': u'Zebra'})

lion = ((LionAnterior, 0, None, None), [((LionHead, 0, 0, None), [], {}), ((LionPosterior, 1, 0, None), [((LionTail, 1, 0, None), [], {})], {})], {'name': u'Lion'})

dragon=((DragonBody, 0, None, None), [((DragonHead, 0, 0, None), [], {}), ((DragonWing, 1, 0, True), [], {}), ((DragonArm, 2, 0, None), [], {}), ((DragonTail, 3, 0, None), [], {}), ((DragonFoot, 4, 0, None), [], {}), ((DragonFoot, 5, 0, None), [], {}), ((DragonArm, 6, 0, None), [], {}), ((DragonWing, 7, 0, None), [], {})], {'name': u'Dragon'})

owlbear = ((BearBody, 0, None, None), [((OwlHead, 0, 0, None), [], {}), ((BearArm, 1, 0, None), [], {}), ((BearLeg, 2, 0, None), [], {}), ((BearLeg, 3, 0, None), [], {}), ((BearArm, 4, 0, None), [], {})], {'name': u'Owlbear'})

eaglebear = ((BearBody, 0, None, None), [((EagleHead, 0, 0, None), [], {}), ((BearArm, 1, 0, None), [], {}), ((BearLeg, 2, 0, None), [], {}), ((BearLeg, 3, 0, None), [], {}), ((BearArm, 4, 0, None), [], {})], {'name': u'Eaglebear'})

owlbra = ((LionAnterior, 0, None, None), [((OwlHead, 0, 0, None), [], {}), ((ZebraPosterior, 1, 0, None), [((ZebraHead, 1, 0, False), [], {})], {})], {'name': u'Owlbra'})

leobear = ((LionAnterior, 0, None, None), [((AngeyBearHead, 0, 0, None), [], {}), ((LionPosterior, 1, 0, None), [((ZebraTail, 1, 0, None), [], {})], {})], {'name': u'Leobear'})

lionfistbear = ((BearBody, 0, None, None), [((AngeyBearHead, 0, 0, None), [], {}), ((LionHead, 1, 0, None), [], {}), ((BearLeg, 2, 0, None), [], {}), ((BearLeg, 3, 0, None), [], {}), ((LionHead, 4, 0, None), [], {})], {'name': u'Lionfist Bear'})

leoraffe = ((LionAnterior, 0, None, None), [((LionHead, 0, 0, None), [], {}), ((ZebraAnterior, 1, 0, None), [((GiraffeHead, 1, 0, True), [], {})], {})], {'name': u'Leoraffe'})

igorboss1 = ((LionAnterior, 0, None, None), [((SharkHead, 0, 0, None), [], {}), ((GiraffePosterior, 1, 0, None), [((CrocodileTail, 1, 0, None), [], {})], {})], {'name': u"Igor's Hound"})

igorboss2 = ((BossBearBody, 0, None, None), [((LionHead, 0, 0, True), [], {}), ((ZebraAnterior, 1, 0, None), [((ZebraHead, 1, 0, None), [], {})], {}), ((DragonFoot, 2, 0, None), [], {}), ((DragonFoot, 3, 0, None), [], {}), ((GiraffePosterior, 4, 0, None), [((GiraffeHead, 1, 0, None), [], {})], {})], {'name': u"Igor's Beast"})

# act 3

crocodile = ((CrocodileAnterior, 0, None, None), [((CrocodilePosterior, 0, 1, None), [((CrocodileTail, 0, 0, None), [], {})], {}), ((CrocodileHead, 1, 0, None), [], {})], {'name': u'Crocodile'})

mollusc = ((QuadropusBody, 0, None, None), [((Tentacle2, 0, 0, None), [], {}), ((Tentacle1, 1, 0, None), [], {}), ((Tentacle1, 2, 0, None), [], {}), ((Tentacle2, 3, 0, None), [], {})], {'name': u'Mollusc'})

shark = ((SharkBody, 0, None, None), [((SharkTail, 0, 0, None), [], {}), ((SharkHead, 1, 0, None), [], {})], {'name': u'Shark'})

pliosaur = ((MoshieAnterior, 0, None, None), [((MoshiePosterior, 0, 1, None), [((MoshieTail, 0, 0, None), [], {})], {}), ((MoshieHead, 1, 0, None), [], {})], {'name': u'Pliosaur'})

elephant = ((ElephantBody, 0, None, None), [((ElephantHead, 0, 0, None), [((ElephantTrunk, 1, 0, None), [], {})], {}), ((ElephantLegFL, 1, 0, None), [], {}), ((ElephantLegFR, 2, 0, None), [], {}), ((ElephantLegBL, 3, 0, None), [], {}), ((ElephantLegBR, 4, 0, None), [], {}), ((ElephantTail, 5, 0, None), [], {})], {'name': u'Elephant'})

quadracroc = ((QuadropusBody, 0, None, None), [((CrocodileHead, 0, 0, None), [], {}), ((CrocodileHead, 1, 0, None), [], {}), ((CrocodileHead, 2, 0, None), [], {}), ((CrocodileHead, 3, 0, None), [], {})], {'name': u'Quadracroc'})

seabeast = ((MoshieAnterior, 0, None, None), [((SharkBody, 0, 1, None), [((Tentacle2, 0, 0, None), [], {})], {}), ((CrocodileHead, 1, 0, None), [], {})], {'name': u'Seabeast'})

crocodouble = ((CrocodileAnterior, 0, None, None), [((CrocodilePosterior, 0, 1, None), [((CrocodileAnterior, 0, 1, None), [((CrocodilePosterior, 0, 1, None), [((CrocodileTail, 0, 0, None), [], {})], {})], {})], {}), ((CrocodileHead, 1, 0, None), [], {})], {'name': u'Crocodouble'})

mirrorshark = ((SharkBody, 0, None, None), [((SharkBody, 0, 0, None), [((SharkHead, 1, 0, None), [], {})], {}), ((SharkHead, 1, 0, None), [], {})], {'name': u'Mirror Shark'})

sealion = ((SharkBody, 0, None, None), [((SharkTail, 0, 0, None), [], {}), ((LionAnterior, 1, 1, False), [((LionHead, 0, 0, None), [], {})], {})], {'name': u'Sealion'})

crocoshark = ((CrocodileAnterior, 0, None, None), [((SharkBody, 0, 1, None), [((SharkTail, 0, 0, None), [], {})], {}), ((CrocodileHead, 1, 0, None), [], {})], {'name': u'Crocoshark'})

sharktron = ((ElephantBody, 0, None, None), [((Connector, 0, 0, None), [((TConnector, 1, 1, None), [((SharkHead, 0, 0, None), [], {}), ((FLaser, 2, 1, False), [((PipeLarge, 0, 0, None), [((RocketEngine, 1, 0, None), [], {})], {})], {})], {})], {}), ((Connector, 1, 0, None), [((Tentacle1, 1, 0, None), [], {})], {}), ((Connector, 2, 0, None), [((Tentacle2, 1, 0, True), [], {})], {}), ((Connector, 3, 0, None), [((Tentacle1, 1, 0, True), [], {})], {}), ((Connector, 4, 0, None), [((Tentacle2, 1, 0, None), [], {})], {}), ((Pipe, 5, 0, None), [((RobotArm, 1, 0, False), [], {})], {})], {'name': u'Sharktron'})

# act 4

crushotron = ((RobotBody, 0, None, None), [((RobotHead, 0, 0, None), [], {}), ((RobotArmLarge, 1, 0, None), [], {}), ((RobotStructure, 2, 0, None), [((RobotFoot, 1, 0, None), [], {})], {}), ((RobotStructure, 3, 0, None), [((RobotFoot, 1, 0, None), [], {})], {}), ((RobotArmLarge, 4, 0, None), [], {})], {'name': u'Crushotron'})

pincertron = ((RobotBody, 0, None, None), [((RobotHead, 0, 0, None), [], {}), ((Connector, 1, 0, None), [((RobotArm, 1, 0, False), [], {})], {}), ((RobotStructure, 2, 0, None), [((RobotFoot, 1, 0, None), [], {})], {}), ((RobotStructure, 3, 0, None), [((RobotFoot, 1, 0, None), [], {})], {}), ((Connector, 4, 0, None), [((RobotArm, 1, 0, None), [], {})], {})], {'name': u'Pincertron'})

hovertron = ((RobotBody, 0, None, None), [((RobotHead, 0, 0, None), [], {}), ((Connector, 1, 0, None), [((ConnectorCorner, 1, 0, True), [((RocketEngine, 1, 0, None), [], {})], {})], {}), ((CoverLarge, 2, 0, None), [], {}), ((CoverLarge, 3, 0, None), [], {}), ((Connector, 4, 0, None), [((ConnectorCorner, 1, 0, None), [((RocketEngine, 1, 0, None), [], {})], {})], {})], {'name': u'Hovertron'})

robear = ((BossBearBody, 0, None, None), [((BearHead, 0, 0, None), [], {}), ((BearArm, 1, 0, None), [], {}), ((FLaser, 2, 0, None), [((ElephantLegFL, 1, 0, None), [], {})], {}), ((BearLeg, 3, 0, None), [], {}), ((ConnectorCorner, 4, 1, None), [((Fuse, 0, 0, None), [((RobotArm, 1, 0, False), [], {})], {})], {})], {'name': u'Ro-bear'})

rocketshark = ((SharkBody, 0, None, None), [((Connector, 0, 1, None), [((RocketEngine, 0, 0, None), [], {})], {}), ((TConnector, 1, 0, None), [((CoverSmall, 1, 0, None), [], {}), ((SharkHead, 2, 0, None), [], {})], {})], {'name': u'Rocket Shark'})

robotaberration = ((ZebraAnterior, 0, None, None), [((PipeLarge, 0, 0, None), [((LionPosterior, 1, 0, None), [((Spring, 1, 0, None), [((CrocodileHead, 1, 0, None), [], {})], {})], {})], {}), ((TriConnector, 1, 0, None), [((ZebraHead, 1, 0, True), [], {}), ((GiraffeHead, 2, 0, None), [], {})], {})], {'name': u'Robot Aberration'})

swissarmysquid = ((QuadropusBody, 0, None, None), [((RobotArm, 0, 0, True), [], {}), ((Fuse, 1, 0, None), [((Tentacle2, 1, 0, None), [], {})], {}), ((Pipe, 2, 0, None), [((CoverSmall, 1, 0, None), [], {})], {}), ((Spring, 3, 0, None), [((MoshieHead, 1, 0, None), [], {})], {})], {'name': u'Swiss Army Squid'})

# finale

zebratitan = ((CrappyRobotBody, 0, None, None), [((PipeLarge, 0, 0, None), [((RobotHead, 1, 0, None), [], {})], {}), ((ZebraPosterior, 1, 0, None), [((RobotArm, 1, 0, None), [], {})], {}), ((RobotStructure, 2, 0, None), [((RobotFoot, 1, 0, None), [], {})], {}), ((RobotStructure, 3, 0, None), [((RobotFoot, 1, 0, None), [], {})], {}), ((ZebraPosterior, 4, 0, None), [((RobotArm, 1, 0, False), [], {})], {})], {'name': u'Zebra Titan'})

crocodiletitan = ((CrappyRobotBody, 0, None, None), [((PipeLarge, 0, 0, None), [((RobotHead, 1, 0, None), [], {})], {}), ((LionAnterior, 1, 1, False), [((ConnectorCorner, 0, 1, None), [((CrocodileHead, 0, 0, None), [], {})], {})], {}), ((RobotStructure, 2, 0, None), [((RobotFoot, 1, 0, None), [], {})], {}), ((RobotStructure, 3, 0, None), [((RobotFoot, 1, 0, None), [], {})], {}), ((LionAnterior, 4, 1, True), [((ConnectorCorner, 0, 1, True), [((CrocodileHead, 0, 0, None), [], {})], {})], {})], {'name': u'Crocodile Titan'})

aviantitan = ((CrappyRobotBody, 0, None, None), [((PipeLarge, 0, 0, None), [((RobotHead, 1, 0, None), [], {})], {}), ((GiraffeAnterior, 1, 1, None), [((Connector, 0, 1, None), [((EagleHead, 0, 0, None), [], {})], {})], {}), ((RobotStructure, 2, 0, None), [((RobotFoot, 1, 0, None), [], {})], {}), ((RobotStructure, 3, 0, None), [((RobotFoot, 1, 0, None), [], {})], {}), ((GiraffeAnterior, 4, 1, None), [((Connector, 0, 1, None), [((OwlHead, 0, 0, None), [], {})], {})], {})], {'name': u'Avian Titan'})

igor = ((IgorHead, 0, None, None), [((DragonBody, 0, 0, None), [((Connector, 1, 1, None), [((LionHead, 0, 0, None), [], {})], {}), ((GiraffeAnterior, 2, 0, None), [((FLaser, 1, 0, None), [((RobotStructure, 1, 0, None), [((CrocodileAnterior, 1, 0, None), [((CrocodileHead, 1, 0, None), [], {})], {})], {})], {})], {}), ((SharkHead, 3, 0, None), [], {}), ((BearLeg, 4, 0, None), [], {}), ((BearLeg, 5, 0, None), [], {}), ((ZebraAnterior, 6, 1, False), [((FLaser, 0, 0, None), [((RobotStructure, 1, 0, None), [((MoshieAnterior, 1, 0, None), [((RobotArm, 1, 0, True), [], {})], {})], {})], {})], {}), ((Connector, 7, 1, None), [((DragonHead, 0, 0, True), [], {})], {})], {})], {'name': u'Igor'})

