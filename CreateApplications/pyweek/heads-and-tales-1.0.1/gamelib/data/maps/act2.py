def easy_encounter():
    return random.choice([  Team([monsters.lion]),
                            Team([monsters.bear]),
                            Team([monsters.zebra]),
                            Team([monsters.giraffe]),
                         ])

def nest_encounter():
    return random.choice([  Team([monsters.owlbear]),
                            Team([monsters.bear, monsters.owlbear]),
                            Team([monsters.owlbear, monsters.owlbear]),
                         ])
                         
def hard_encounter():
    return random.choice([  Team([monsters.lion, monsters.leobear]),
                            Team([monsters.bear, monsters.lionfistbear]),
                            Team([monsters.zebra, monsters.giraffe, monsters.leoraffe]),
                            Team([monsters.zebra, monsters.owlbra]),
                         ])

@mapscript()
def script(g):
    if first(g, "act2start"):
        g.close_link("act2", "hills1", "cabin")
    elif g.current_world_node == 'cabin' and first(g, "act2eaglekilled"):    
        yield dialogue("Oh, thank you!", "Alchemist", 'right')
        yield dialogue("I thought I had found a nice safe place to settle down and observe the wildlife, and then that terrible monster came!")
        yield dialogue("Your snivelling thanks mean little to me.", "Heinrich#point", 'left')
        setportrait("Heinrich", 'left')
        yield dialogue("However, the head of this beast is a fine trophy.")
        yield dialogue("I'm so grateful!", "Alchemist", 'right')
        yield dialogue("There's a little path back down the hill over there, if you want to get away from this terrible place.", "Alchemist", 'right')
        yield dialogue("So, you've found another grotesque piece of monster meat to cart around.", "Becka", 'right')
        yield dialogue("Did you ever see that psychologist Mom recommended?", "Becka#facepalm", 'right')
        yield endcutscene()
        g.open_link("act2", "cabin", "hills1")
    elif g.current_world_node == 'volcano' and first(g, "act2dragonkilled"):
        yield dialogue("Haha! My chimeras are invincible! And the head of that dragon will only add to their majesty!", "Heinrich#laugh", 'right')
        yield dialogue("Who's laughing now, o doubting relative of mine?", "Heinrich#point", 'right')
        setportrait("Heinrich", 'right')
        yield dialogue("So now we cart the head back to your tower?", "Becka", 'left')
        yield dialogue("Let's go. I'm still waiting to see some real science.")
        yield endcutscene()

@locscript("outcrop")
def script(g):
    if first(g, "act2outcrop"):
        yield dialogue("The view from up that mountain is fantastic!", "Engineer", "right")
        yield dialogue("Be on your guard, though. To climb up, you'd have to cross through the owlbear nesting grounds.")
        yield dialogue("Those things are fierce!")
        yield dialogue("I shall glory in their destruction, and claim their organs as my own!", "Heinrich#laugh", "left")
        setportrait('Heinrich', 'left')
        yield dialogue("Do you have any idea how nuts you sound?", "Becka#facepalm", "right")
        yield endcutscene()

@locscript("outcroplab")
def script(g):
    yield enterlab("act2", "outcrop")
    
@locscript("mountainlab")
def script(g):
    yield enterlab("act2", "mountain2")
    
@locscript("prairielab")
def script(g):
    yield enterlab("act2", "prairie")
    
@locscript("prairie")
def script(g):
    if first(g, "act2prairie"):
        yield dialogue("So let me get this straight.", "Becka", 'left')
        yield dialogue("You probably can't defeat this dragon yet.")
        yield dialogue("But you're going to have your monsters battle with the local fauna until you can collect enough parts to build something powerful enough to beat it?")
        yield dialogue("Ah, sister.", "Heinrich", 'right')
        yield dialogue("I may despise you, but at least you understand me.")
        yield dialogue("In the same way that I understand that bacteria breed in excrement, yes.", "Becka#facepalm", 'left')
        yield endcutscene()
    
@locscript("cabin")
def script(g):
    if first(g, "cabin"):
        yield dialogue("Help! Help!", "Alchemist", 'right')
        yield dialogue("This monster has me cornered! I'm done for!")
        yield dialogue("My God! Look at that magnificent beast!", "Heinrich", 'left')
        yield dialogue("I'll have its head for my chimeras!", 'Heinrich#laugh', 'left')
        yield endcutscene()
        yield battle(Team([monsters.eaglebear]), [EagleHead])

@locscript("volcano")
def script(g):
    if first(g, "volcano"):
        yield dialogue("There it is! The dragon awaits!", "Heinrich", 'left')
        yield dialogue("So you're really going through with this?", "Becka", 'right')
        yield dialogue("Forward, my glorious chimeras! Charge!", "Heinrich#laugh", 'left')
        setportrait("Heinrich", 'left')
        yield dialogue("If you die now, do I inherit that crumbling old tower?", 'Becka#facepalm', 'right')
        yield endcutscene()
        yield battle(Team([monsters.dragon]), [DragonHead])
    
@locscript("hills1")
@locscript("hills2")
@locscript("hills3")
def script(g):
    if random.random() < 0.5:
        yield battle(easy_encounter())
        
@locscript("nests1")
@locscript("nests1")
def script(g):
    yield battle(nest_encounter())

@locscript("mountain1")
@locscript("mountain2")
def script(g):
    if random.random() < 0.5:
        yield battle(hard_encounter())
        
@locscript("tower")
def script(g):
    if flag(g, "act2dragonkilled"):
        yield changemap("tower3", "exit")
    else:
        yield enterlab("act2", "outsidetower")