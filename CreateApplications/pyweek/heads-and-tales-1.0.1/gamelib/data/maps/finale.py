@mapscript()
def script(g):
    # swap around images
    changeimage("igor", "dummy_warehouse")
    changeimage("workbench", "igor")
    if flag(g, "winnerwinnerchickendinner"):
    
    
        setportrait("Igor", 'right')
        yield dialogue("Ha ha ha! Once again, the genius wins the day!", "Heinrich#laugh", 'left')    
        setportrait("Heinrich", "left")
        yield dialogue("Urgh ...", "Igor", 'right')
        yield dialogue("Now, just explain to me ... what were you thinking?", "Heinrich#point", 'left')
        setportrait("Heinrich", "left")
        yield dialogue("Uhh ...", "Igor", 'right')
        yield dialogue("Look at you ... you're a pathetic snivelling wreck!", 'Heinrich', 'left')
        yield dialogue("Have mercy, Master! Please!", "Igor", 'right')
        yield dialogue("Mercy?", "Heinrich#point", 'left')
        yield dialogue("Mercy?", "Heinrich#laugh", 'left')
        yield dialogue("I should fire you on the spot, and send you to live in the village with those filthy peasants!", "Heinrich#point", 'left')
        setportrait("Heinrich", 'left')
        yield dialogue("Brother, dear ... aren't you being a bit hard on him?", "Becka", 'right')
        yield dialogue("What do you mean?", "Heinrich", 'left')
        yield dialogue("Well, he may have lost to your pathe-", "Becka", 'right')
        yield dialogue("I mean, he may have lost in the face of your otherworldly genius, but that's only to be expected.")
        yield dialogue("After all, you are a prodigy ...")
        yield dialogue("I am!", "Heinrich", 'left')
        yield dialogue("But anyway, don't you think his works were rather impressive?", "Becka", "right")
        yield dialogue("Think how it reflects on you, that even your assistant can build such terrifying creations!")
        yield dialogue("You know ... you might have a point there, sister.", "Heinrich", 'left')
        yield dialogue("If I kick him out now, he might decide to go and work for some other scientist ... and maybe one day, learn enough to properly challenge me.")
        yield dialogue("Exactly!", "Becka", 'right')
        yield dialogue("Alright, Igor! I've changed my mind. You can continue working for me ... for now.", "Heinrich", 'left')
        yield dialogue("I can?", "Igor", 'right')
        yield dialogue("Oh, thank you, Master!")
        yield dialogue("You won't regret this!")
        yield dialogue("I'd better not!", "Heinrich", 'left')
        yield dialogue("Now clean up this mess!", "Heinrich#point", 'left')
        yield dialogue("Put those fires out!", "Heinrich", 'left')
        yield dialogue("Get rid of those stupid robots!", "Heinrich", 'left')
        yield dialogue("... sigh ...", "Becka#facepalm", 'right')
        yield dialogue("And find somewhere to put that dragon head! I want everyone in the village to see it!", "Heinrich#laugh", 'left')
        setportrait(None, 'right')
        yield dialogue("FIN", None, 'right')
        yield endcutscene()
        yield changemap("credits", "dummy")
    else:
        if first(g, "finale__intro"):
            yield dialogue("Back at last!", "Heinrich", 'right')
            yield dialogue("Soon I shall be able to resume my momentous research!")
            yield dialogue("As soon as I've expunged that overblown research monkey and his delusions of grandeur ...")
            yield endcutscene()
    
@locscript("exit")
def script(g):
    setflag(g, "finalelefttower")
    yield changemap("act4", "outsidetower")
    
@locscript("floor2")
def script(g):
    if first(g, "finalefloor2"):
        yield dialogue("What travesties has Igor perpetrated in my absence?", "Heinrich", 'left')
        yield dialogue("Whatever they are, my perfect chimeras will crush them beneath their feet!")
        yield endcutscene()
        yield battle(Team([monsters.zebratitan]))
        
@locscript("igor")
def script(g):
    if first(g, "finalefloor3"):
        yield dialogue("Flee before me, abominable creations!", "Heinrich", 'left')
        yield dialogue("Soon your creator shall be undone, and I shall see him humbled before me!")
        yield endcutscene()
        yield battle(Team([monsters.crocodiletitan]))
        
@locscript("centre")
def script(g):
    if first(g, "finalefloor4"):
        yield dialogue("Is there no end to Igor's madness? What monstrosity will I be forced to exterminate next?", "Heinrich", 'left')
        yield endcutscene()
        yield battle(Team([monsters.aviantitan]))
        
@locscript("workbench")
def script(g):
    setportrait("Igor", 'right')
    yield dialogue("Igor!", "Heinrich", 'left')
    yield dialogue("This madness ends now!")
    yield dialogue("Yes, with your destruction.", 'Igor', 'right')
    yield dialogue("I always thought you were an idiot, full of ambitious ideas but incapable of following through.")
    yield dialogue("But it turns out, you weren't ambitious enough.")
    yield dialogue("You claimed you had genius. You sought the perfect chimera.")
    yield dialogue("Did you not see the missing link?")
    yield dialogue("You can't mean ...", 'Heinrich', 'left')
    yield dialogue("Witness the culmination of MY great work, Master.", 'Igor', 'right')
    yield dialogue("Witness my perfection, and despair!")
    yield endcutscene()
    setflag(g, "winnerwinnerchickendinner")
    yield battle(Team([monsters.igor]), [])
        
