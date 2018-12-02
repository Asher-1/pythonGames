@mapscript()
def script(g):
    yield dialogue('This is the map script.')
    if first(g, 'intro'):
        yield dialogue('This will only be displayed once.')
    yield endcutscene()

@locscript('town')
def script(g):
    g.close_link('testmap', 'village', 'secret')
    g.close_link('testmap', 'secret', 'fork')

@locscript('dungeon')
def script(g):
    yield dialogue('I have arrived!', 'Heinrich', 'right')
    yield dialogue('Aha! I am an X!', 'Devious X', 'left')
    yield dialogue('How devious!', side='right')
    yield dialogue('Behold my secret weapon...')
    yield dialogue('Mr Fluffles, attack!', 'Mad Cat Lady')
    yield endcutscene()
    yield battle(Team([monsters.brokendoublegoat]))

@locscript('lab')
def script(g):
    yield dialogue('Aha! I can use this laboratory!', 'Protagonist', 'left')
    yield endcutscene()
    yield enterlab()

@locscript('village')
def script(g):
    if g.link_closed('testmap', 'village', 'secret'):
        yield dialogue("Wait, this isn't so hard to figure out ...")
        yield endcutscene()
        g.open_link('testmap', 'village', 'secret')
        g.open_link('testmap', 'secret', 'fork')
@locscript('secret')
def script(g):
    yield dialogue('Suddenly, EVERYTHING CHANGES', 'Narrator', 'left')
    yield endcutscene()
    yield changemap('test2', 'start')
