def silly_robot():
    return random.choice([  monsters.robear,
                            monsters.rocketshark,
                            monsters.swissarmysquid,
                            monsters.robotaberration,
                         ])

def tough_robot():
    return random.choice([  monsters.crushotron,
                            monsters.pincertron,
                            monsters.hovertron,
                         ])

def easy_encounter():
    return random.choice([  Team([silly_robot()]),
                            Team([tough_robot()]),
                            Team([silly_robot(), silly_robot()]),
                         ])

def hard_encounter():
    return random.choice([  Team([monsters.crushotron, monsters.crushotron]),
                            Team([monsters.pincertron, monsters.pincertron]),
                            Team([monsters.hovertron, monsters.hovertron]),
                            Team([tough_robot(), tough_robot(), silly_robot()]),
                            Team([silly_robot(), silly_robot(), silly_robot()]),
                         ])

@mapscript()
def script(g):
    changeimage("tower", "dummy_eviltower")
    if first(g, "act4start"):
        g.close_link("act4", "village", "outsidetower")
        yield dialogue("Right, I'm back.", "Heinrich", 'left')
        yield dialogue("Time to find that arrogant assistant and put him in his place.")
        yield endcutscene()
    elif g.current_world_node == 'village' and first(g, 'act4savedvillage'):
        setportrait('Peasants', 'right')
        yield dialogue("Thus is the fate of all who oppose me!", "Heinrich#point", 'right')
        yield dialogue("And don't let me catch you referring to my worthless assistant as a tyrant again.", 'Heinrich', 'right')
        yield dialogue("The only one who will tyrannize you is me!", "Heinrich#point", 'right')
        yield endcutscene()
    elif g.current_world_node == 'outsidetower' and flag(g, 'finalelefttower'):
        # came here from inside the tower
        setportrait('Heinrich', 'left')
        if first(g, "act4beckabackout"):
            yield dialogue("Backing out, dear brother?", "Becka", 'right')
        yield dialogue("Do you need to work on your monsters?", "Becka", 'right')
        yield endcutscene()
        setflag(g, 'finalelefttower', False) # avoid infinite loop!
        yield enterlab("act4", "outsidetower")

@locscript("field3")
def script(g):
    if first(g, "act4field3"):
        yield dialogue("What?", "Heinrich", 'left')
        yield dialogue("What kind of monstrosity is that?")
        yield dialogue("This must be Igor's work!")
        yield endcutscene()
        yield battle(Team([monsters.robear]))
    else:
        if random.random() < 0.5:
            yield battle(easy_encounter())

@locscript("field1")
@locscript("field2")
def script(g):
    if random.random() < 0.5:
        yield battle(easy_encounter())

@locscript("village")
def script(g):
    if first(g, "act4village"):
        setportrait('Heinrich', 'left')
        yield dialogue('Noble master! Save us!', 'Peasants', 'right')
        yield dialogue('The tyrant Igor has sent monsters to burn our crops and carry away our children!')
        yield dialogue('You expect me to come to your aid yet again?', 'Heinrich', 'left')
        yield dialogue('I should have allowed you to be destroyed the first time and saved all this bother!')
        yield endcutscene()
        yield battle(Team([monsters.robear, monsters.crushotron]), [RobotBody, RobotHead])

@locscript("portlab")
def script(g):
    yield enterlab("act4", "port")
    
@locscript("act1lab")
def script(g):
    yield enterlab("act4", "clearing")
    
@locscript("clearing")
def script(g):
    if first(g, "act4clearing"):
        setportrait('Heinrich', 'right')
        yield dialogue("There you are!", "Becka", 'left')
        yield dialogue("This has got completely out of hand, you know.")
        yield dialogue("Igor is acting entirely inappropriately, and as far as I'm concerned, it's your fault.")
        yield dialogue("Ha! Why should I care who you blame?", "Heinrich#point", 'right')
        setportrait('Heinrich', 'right')
        yield dialogue("Well, you wouldn't want a censure from the Committee for Extraordinary Research, would you?", "Becka", 'left')
        yield dialogue("You wouldn't!", "Heinrich", 'right')
        yield endcutscene()

@locscript("forest3")
def script(g):
    if first(g, "act4forest3"):
        yield dialogue("Stupid sister ...", "Heinrich", 'left')
        yield dialogue("This is none of her business anyway ...")
        yield dialogue("But Igor will pay. Oh yes, he will pay!")
        yield endcutscene()
    else:
        if random.random() < 0.5:
            yield battle(hard_encounter())
        
@locscript("forest1")
@locscript("forest2")
def script(g):
    if random.random() < 0.5:
        yield battle(hard_encounter())
        
@locscript("outsidetower")
def script(g):
    setportrait('Heinrich', 'left')
    if first(g, "act4outsidetower"):
        yield dialogue("Well, Heinrich, it's time to go and sort this out.", 'Becka', 'right')
        yield dialogue("You were the one who filled Igor's head with all this nonsense about chimeras and tyranny.")
        yield dialogue("You'd better go and put it right.")
        yield dialogue("Look, I brought my portable workbench.")
    yield dialogue("Do you need to work on your monsters?", "Becka", 'right')
    yield endcutscene()
    yield enterlab("act4", "outsidetower")
    
@locscript("tower")
def script(g):
    yield changemap("finale", "floor1")