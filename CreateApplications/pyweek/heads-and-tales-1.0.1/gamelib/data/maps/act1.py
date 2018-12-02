def easy_encounter():
    return random.choice([  Team([monsters.cat, monsters.cat]),
                            Team([monsters.goat]),
                            Team([monsters.snake]),
                            Team([monsters.bigsnake]),
                         ])

def hard_encounter():
    return random.choice([  Team([monsters.cat, monsters.cat, monsters.goatcat]),
                            Team([monsters.goat, monsters.goat]),
                            Team([monsters.snake, monsters.snake]),
                            Team([monsters.snake, monsters.bigsnake, monsters.bigsnake]),
                         ])

@mapscript()
def script(g):
    if first(g, "act1map"):
        g.close_link("act1", "outsidetower", "village")
        g.close_link("act1", "field3", "port")
        setportrait('Heinrich', 'left')
        yield dialogue("Master, be careful!", "Assistant", 'right')
        yield dialogue("Last time you went outside, you were attacked by the wildlife.")
        yield dialogue("Don't belittle me, you piteous mongrel.", "Heinrich#point", 'left')
        yield dialogue("My monsters will protect me from anything that might present a threat.", 'Heinrich', 'left')
        yield endcutscene()
    elif flag(g, "act1forest1") and first(g, "act1forest1a"):
        setportrait('Assistant', 'right')
        yield dialogue("See? Not a problem. Now, don't let me catch you doubting me again.", "Heinrich", 'left')
        yield dialogue("If I obtain any useful parts from these monsters, I could even take them back to the lab to improve my army.")
        yield endcutscene()
    elif flag(g, "act1clearing") and first(g, "act1clearing2"):
        setportrait('Heinrich', 'right')
        yield dialogue("You monster!", "Cat Lady", 'left')
        yield dialogue("You'll pay for this one day! Mark my words!", "Cat Lady", 'left')
        yield endcutscene()
    elif flag(g, "act1village") and first(g, "act1village2"):
        setportrait('Peasant', 'right')
        yield dialogue("Once again, you owe me your lives and livelihoods!", 'Heinrich', 'left')
        yield dialogue("I expect material gratitude delivered to my tower forthwith!")
        yield dialogue("Now I must return to my research. I am expecting an important visitor, after all.")
        yield endcutscene()
        setflag(g, "villagedone")
        g.open_link("act1", "village", "outsidetower")
        
@locscript("forest1")
def script(g):
    if first(g, "act1forest1"):
        yield dialogue("Master, here it comes!", "Assistant", 'left')
        yield endcutscene()
        yield battle(Team([monsters.goat]))
    else:
        if random.random() < 0.5:
            yield battle(easy_encounter())

@locscript("forest2")
@locscript("forest3")
def script(g):
    if random.random() < 0.5:
        yield battle(easy_encounter())

@locscript("clearing")
def script(g):
    if first(g, "act1clearing"):
        yield dialogue("Do you like cats?", "Cat Lady", 'left')
        yield dialogue("What are you babbling about?", "Heinrich", 'right')
        yield dialogue("I love cats!", "Cat Lady", 'left')
        yield dialogue("Cats are the greatest of all this world's creatures!", "Cat Lady", 'left')
        yield dialogue("You might say they are ... purr-fect!", "Cat Lady", 'left')
        yield dialogue("Ha ha ha!", "Cat Lady", 'left')
        yield dialogue("Get out of my way, you senile crone, or my monsters and I will destroy you utterly.", "Heinrich#point", 'right')
        setportrait('Heinrich', 'right')
        yield dialogue("How dare you!", "Cat Lady", 'left')
        yield dialogue("Fluffles! Tibbles! Mr. Whiskers! Attack!", "Cat Lady", 'left')        
        yield endcutscene()
        yield battle(Team([monsters.cat, monsters.cat, monsters.cat]))

@locscript("field1")
@locscript("field2")
@locscript("field3")
def script(g):
    if random.random() < 0.5:
        yield battle(hard_encounter())

@locscript("act1lab")
def script(g):
    if first(g, "act1lab"):
        yield dialogue("How fortuitous!", "Heinrich", 'left')
        yield dialogue("This laboratory must have been abandoned by some other scientist.")
        yield dialogue("I could do some work on my monsters here, if necessary.")
        yield endcutscene()
    yield enterlab("act1", "clearing")

@locscript("tower")
def script(g):
    if flag(g, "villagedone"):
        setportrait('Heinrich', 'right')
        yield dialogue("Hello!", 'Becka', "left")
        yield dialogue("Oh, God, it's you.", "Heinrich", "right")
        yield dialogue("Why are you here?")
        yield dialogue("Didn't you get the letter?", "Becka", "left")
        yield dialogue("I'm here from the Committee for Extraordinary Research.")
        yield dialogue("I thought perhaps I might finally convince you to stop sending us all those overblown proclamations of how amazing you are.")
        yield dialogue("By the way, Mom says you never write.")
        yield endcutscene()
        yield changemap("tower2", "exit")
    else:
        yield enterlab("act1", "outsidetower")

@locscript("village")
def script(g):
    if first(g, "act1village"):
        yield dialogue("Fetid peasantry!", "Heinrich#point", 'left')
        yield dialogue("It has been four whole days since you brought me tribute!")
        yield dialogue("Need I remind you that I could crush you beneath my heel on a whim?")
        setportrait('Heinrich', 'left')
        yield dialogue("Our most abject apologies, your noble and benevolent lordship.", "Peasant", 'right')
        yield dialogue("Some malevolent scientist created a mad beast which has been destroying our crops.")
        yield dialogue("Ha!", 'Heinrich', 'left')
        yield dialogue("Some mad beast, the work of an inferior intellect to my own? I shall destroy it!")
        yield dialogue("Show me the beast, and it will know my wrath!")
        yield endcutscene()
        yield battle(Team([monsters.snakegoatboss]))