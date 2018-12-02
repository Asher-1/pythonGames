def easy_encounter():
    return random.choice([  Team([monsters.shark]),
                            Team([monsters.mollusc]),
                            Team([monsters.pliosaur]),
                         ])

def jungle_encounter():
    return random.choice([  Team([monsters.elephant]),
                            Team([monsters.crocodile, monsters.crocodile]),
                         ])

def hard_encounter():
    return random.choice([  Team([monsters.mirrorshark, monsters.shark, monsters.shark]),
                            Team([monsters.shark, monsters.pliosaur, monsters.seabeast]),
                            Team([monsters.quadracroc, monsters.mollusc]),
                            Team([monsters.crocodouble, monsters.crocodile]),
                            Team([monsters.crocodouble, monsters.crocoshark, monsters.sealion]),
                            Team([monsters.sealion, monsters.sealion, monsters.sealion]),
                         ])

@mapscript()
def script(g):
    if flag(g, "moveadmiral") and not flag(g, "defeatelephant"):
        changeimage("jungle1", "dummy_admiral")
    if flag(g, "defeatelephant"):
        changeimage("marina", "dummy_admiral")
    if first(g, "act3start"):
        yield dialogue("What ... where am I?", "Heinrich", 'right')
        yield dialogue("That assistant! Oglor, or whatever he calls himself! He'll pay for this!")
        yield dialogue("Just as soon as I can find him ...")
        yield dialogue("Don't hold your breath, old bean.", "Commodore", 'left')
        yield dialogue("You'll not get off this island in a hurry.")
        yield dialogue("There's not a soul around, save for me, and not a boat can take you, save for mine.")
        yield dialogue("You have a boat?", "Heinrich", 'right')
        yield dialogue("I demand you take me away from here at once!", 'Heinrich#point')
        setportrait('Heinrich', 'right')
        yield dialogue("Can't say I fancy it, old chap.", "Commodore", 'left')
        yield dialogue("No, you can stay here and take in the sunshine.")
        yield dialogue("I'm off to attend to nautical matters.")
        setportrait(None, 'left')
        yield dialogue("Outrageous!", "Heinrich", 'right')
        yield dialogue("I've never met anyone so self-centred!")
        yield dialogue("I'll show him!")
        setflag(g, 'moveadmiral')
        changeimage("jungle1", "dummy_admiral")
        yield endcutscene()
    elif g.current_world_node == 'jungle1' and first(g, "defeatelephant"):
        changeimage("marina", "dummy_admiral")
        changeimage("jungle1", "jungle1")
        yield dialogue("What a creature!", "Heinrich", 'left')
        yield dialogue("It's a shame I probably can't drag the carcass to one of these abandoned laboratories.")
        yield dialogue("And it looks like that infuriating uniformed oaf has taken off in the commotion.")
        yield endcutscene()
    elif g.current_world_node == 'marina':
        setportrait("Commodore", 'right')
        yield dialogue("Science beats seamanship once again!", "Heinrich#laugh", 'left')
        setportrait('Heinrich', 'left')
        yield dialogue("Now while I leave you to lick your salty wounds, I'm taking your boat back home to deal with my treacherous lackey.")
        yield endcutscene()
        g.reset_inventory()
        yield changemap("act4", "port")
        
@locscript("beachlab")
def script(g):
    yield enterlab("island", "beach")

@locscript("shore1")
@locscript("shore2")
@locscript("shore3")
def script(g):
    if random.random() < 0.5:
        yield battle(easy_encounter())

@locscript("junglelab")
def script(g):
    yield enterlab("island", "jungle1")

@locscript("jungle1")
def script(g):
    if first(g, "act3jungle"):
        setportrait("Heinrich", 'right')
        yield dialogue("Thought you'd follow me through the jungle, old chap?", "Commodore", 'left')
        yield dialogue("Wouldn't recommend it. Elephants, don't you know?")
        yield dialogue("Ferocious blighters, they are.")
        yield dialogue("Look! Here comes one now!")
        yield endcutscene()
        yield battle(Team([monsters.elephant]))
    else:
        if random.random() < 0.5:
            yield battle(jungle_encounter())

@locscript("jungle2")
def script(g):
    if random.random() < 0.5:
        yield battle(jungle_encounter())

@locscript("shore4")
@locscript("shore5")
@locscript("shore6")
def script(g):
    if random.random() < 0.5:
        yield battle(hard_encounter())
    
@locscript("shorelab")
def script(g):
    yield enterlab("island", "shore6")
    
@locscript("marina")
def script(g):
    setportrait("Commodore", 'right')
    yield dialogue("You! I demand that you hand over your vessel!", "Heinrich#point", 'left')
    setportrait('Heinrich', 'left')
    yield dialogue("Never! A captain goes down with his ship!", "Commodore", 'right')
    yield dialogue("I'll fight to the last! Beast of the sea, come to my aid!", "Commodore", 'right')
    yield endcutscene()
    yield battle(Team([monsters.sharktron]), [RocketEngine, RobotArm, FLaser])
