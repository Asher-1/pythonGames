@mapscript()
def script(g):
    if first(g, "cutscene1"):
        g.close_link("tower1", "centre", "workbench")
        g.close_link("tower1", "igor", "floor2")
        yield help('click or press a key to continue the cutscene...', 1.0)
        yield dialogue("Assistant!", 'Heinrich', 'left')
        yield dialogue("Assistant! Where are you?")
        yield endcutscene()
        yield help('click on a location or use the arrow keys to move around...', 1.0)
    elif first(g, "cutscene3"):
        yield dialogue("I'm sorry, Master!", "Assistant", 'right')
        yield dialogue("I didn't mean to fail you!", "Assistant", 'right')
        yield dialogue("But I have good news!", "Assistant", 'right')
        yield dialogue("I created another chimera as well, just in case. And it much resembles yours!", "Assistant", 'right')
        yield dialogue("Double imbecile!", 'Heinrich#point', 'left')
        yield dialogue("Look how many parts you've added!", 'Heinrich#point', 'left')
        yield dialogue("The poor monster's heart will never cope!", 'Heinrich#point', 'left')
        yield dialogue("Let me put this one out of its misery, as well!", 'Heinrich', 'left')
        yield endcutscene()
        yield battle(Team([monsters.brokensnakegoat]), [GoatPosterior, SnakeTail])
    elif first(g, "cutscene4"):
        yield dialogue("That's the last time I let you handle the scalpel.", 'Heinrich', 'left')
        yield dialogue("Let me take these pieces to my laboratory and see what I can salvage from the mess you've made.", 'Heinrich', 'left')
        yield endcutscene()
        g.open_link("tower1", "centre", "workbench")
    elif flag(g, "used_workbench") and first(g, "cutscene5"):
        yield dialogue("Now let me show that idiot assistant what true creative genius looks like!", 'Heinrich', 'left')
        yield endcutscene()
        
@locscript("igor")
def script(g):
    if first(g, "cutscene2"):
        setportrait('Heinrich', 'left')
        yield dialogue("Here I am, Master.", "Assistant", 'right')
        yield dialogue("Have you assembled the chimera as I instructed?", 'Heinrich', 'left')
        yield dialogue("Better, Master!", "Assistant", 'right')
        yield dialogue("Instead of breaking down the second goat for parts, I added it onto the first one in its entirety!", "Assistant", 'right')
        yield dialogue("Now it has twice as many horns with which to butt those who defy you, and twice as many feet with which to trample them!", "Assistant", 'right')
        yield dialogue("Imbecile!", 'Heinrich#point', 'left')
        yield dialogue("Those extra feet won't do anything! They don't even touch the floor!", 'Heinrich#point', 'left')
        yield dialogue("Your pitiful creation won't last a minute in a fight.", 'Heinrich', 'left')
        yield dialogue("Let me show you!", 'Heinrich', 'left')
        yield endcutscene()
        yield battle(Team([monsters.brokendoublegoat]), [GoatHead, GoatAnterior])
    elif flag(g, "cutscene5") and first(g, "cutscene6"):
        setportrait('Assistant', 'right')
        yield dialogue("Pitiful assistant! Witness my genius, and quail!", "Heinrich#point", "left")
        setportrait('Heinrich', 'left')
        yield dialogue("Yes, Master. Your intellect knows no bounds.", "Assistant", 'right')
        yield dialogue("Now, with my army of monsters, I have business to attend to.", "Heinrich", "left")
        yield dialogue("No-one from the village has brought me food or gifts for several days now.", "Heinrich", "left")
        yield dialogue("I think they need to be reminded that they survive only through my magnanimity.", "Heinrich", "left")
        yield endcutscene()
        g.open_link("tower1", "igor", "floor2")

@locscript("floor2")
def script(g):
    if first(g, "prologuefloor2"):
        yield dialogue("Useless moron.", "Heinrich", 'left')
        yield dialogue("I am surrounded by fools who don't appreciate my genius.", "Heinrich", 'left')
        yield endcutscene()

@locscript("floor1")
def script(g):
    if first(g, "prologuefloor1"):
        yield dialogue("But not for too much longer, perhaps!", "Heinrich", 'left')
        yield dialogue("That letter said that a representative from the Committee for Extraordinary Research would be arriving today to review my corpus.")
        yield dialogue("Perhaps I shall finally find the recognition I deserve!")
        yield dialogue("But first, those upstart villagers ...")
        yield endcutscene()
        
@locscript("workbench")
def script(g):
    if first(g, "used_workbench"):
        yield dialogue("Right, let's see what I can put together ...", 'Heinrich', 'left')
        yield endcutscene()
    yield enterlab()
    
@locscript("exit")
def script(g):
    yield changemap("act1", "outsidetower")
