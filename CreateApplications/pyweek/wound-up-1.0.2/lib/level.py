'''level.py - levels for the game, hardcoded, but nicely so'''

import model


directory = {}
def menulevel(level_cls):
    global directory
    directory[level_cls.name] = (len(directory), level_cls)
    return level_cls


class Level(object):
    name = 'Default'
    desc = 'A default level template.'
    size = (50, 25)
    camera = (None, None)
    tutorial = False
    prereqs = []
    
    @classmethod
    def load(cls):
        return cls.camera, cls.size, cls.tutorial, cls.build_state()

    @classmethod
    def build_state(cls):
        state = model.gamestate.Gamestate(*cls.size)
        return state


class TutorialLevel(Level):
    name = 'Beginner'
    desc = 'A tutorial level for beginners.'
    size = (20, 30)
    camera = (None, None)
    tutorial = True
 
    @classmethod
    def build_state(cls):
        state = model.gamestate.Gamestate(*cls.size)
        
        state.add_spring((7, 1))
        
        state.pgrid.lock()
        state.pgrid.add_platform((4,0), 7)
        state.pgrid.add_ladder((4,0), 5)
        state.pgrid.add_platform((10, 2), 9)
        state.pgrid.add_ladder((10, 1), 2)
        state.pgrid.add_platform((5, 10), 8)
        state.pgrid.unlock()
        
        rubber_factory = model.device.RubberFactory((16, 3))
        metal_factory = model.device.MetalFactory((12, 3))
        gumball_machine = model.device.GumballMachine((12, 11))

        state.add_device(rubber_factory)
        state.add_device(metal_factory)
        state.add_device(gumball_machine)

        state.add_belt(state.spring, metal_factory)
        state.add_belt(metal_factory, rubber_factory)
        
        state.add_elf((11, 1))
        state.add_elf((12, 1))
        state.add_elf((13, 1))
        
        state.recalculate_ratios()

        return state

TutorialLevel = menulevel(TutorialLevel)


class SimpleLevel(Level):
    name = 'First Steps'
    desc = 'Even as you set out, you encounter\nsome of your friends trapped in\nthe Doctor\'s accursed contraptions.'
    size = (50, 25)
    camera = (None, None)

    @classmethod
    def build_state(cls):
        state = model.gamestate.Gamestate(*cls.size)

        state.add_spring((5, 1))

        state.pgrid.lock()
        state.pgrid.add_platform((5,0),8)
        state.pgrid.add_ladder((7,0),1)
        state.pgrid.add_platform((16,2),10)
        state.pgrid.add_ladder((22,0),3)
        state.pgrid.add_platform((32, 0), 6)
        state.pgrid.add_ladder((33,0), 1)
        state.pgrid.unlock()
        
        state.add_device(model.device.GumballMachine((20, 3)))
        state.add_device(model.device.GumballMachine((25, 3)))
        state.add_device(model.device.RubberFactory((29, 0)))
        state.add_device(model.device.MetalFactory((33, 1)))
        
        state.add_elf((8,1))
        state.add_elf((9,1))

        state.recalculate_ratios()
        
        return state

SimpleLevel = menulevel(SimpleLevel)


class DonkeyLevel(Level):
    name = 'Steady Climb'
    desc = 'Approaching the putrid lands Doctor McEvilpant\'s\ncares to call home you find a steady slope\ndotted with members of your charge.'
    size = (33,36)
    camera = (None, None)
    
    @classmethod
    def build_state(cls):
        state = model.gamestate.Gamestate(*cls.size)
        
        state.add_spring((9,0))
        
        state.pgrid.lock()
        
        state.pgrid.add_platform((6,5),18)
        state.pgrid.add_platform((4,11),16)
        state.pgrid.add_platform((23,11),9)
        state.pgrid.add_platform((10,17),11)
        state.pgrid.add_platform((10,23),21)
        state.pgrid.add_platform((8,29),22)
        
        state.pgrid.add_ladder((21,0),6)
        state.pgrid.add_ladder((8,6),6)
        state.pgrid.add_ladder((18,12),6)
        state.pgrid.add_ladder((11,18),6)
        state.pgrid.add_ladder((28,24),6)
        
        state.pgrid.unlock()
        
        state.add_device(model.device.GumballMachine((15,12), gumballs=2))
        state.add_device(model.device.GumballMachine((9,30), gumballs=2))
        state.add_device(model.device.GumballMachine((25,30), gumballs=2))

        state.add_device(model.device.RubberFactory((4,0)))
        state.add_device(model.device.RubberFactory((26,0)))
        state.add_device(model.device.MetalFactory((6,12)))
        state.add_device(model.device.MetalFactory((25,12)))
        state.add_device(model.device.MetalFactory((29,12)))
        
        state.add_elf((10,0))
        state.add_elf((11,0))
        state.add_elf((12,0))
        state.add_elf((13,0))
        
        return state

DonkeyLevel = menulevel(DonkeyLevel)


class SpaciousLevel(Level):
    name = "The Cave"
    desc = "Dr McEvilpants' subterranean lair is host\nto several of your elfy chums."
    size = (40, 40)

    @classmethod
    def build_state(cls):
        state = model.gamestate.Gamestate(*cls.size)

        state.add_spring((2, 36))

        state.pgrid.lock()
        state.pgrid.add_platform((1,35), 6)
        state.pgrid.add_platform((37,34), 1)
        state.pgrid.add_ladder((37,35), 1)
        state.pgrid.unlock()

        state.add_device(model.device.GumballMachine((2,1), gumballs=3))
        state.add_device(model.device.GumballMachine((37,1), gumballs=3))
        state.add_device(model.device.GumballMachine((37,36), gumballs=3))

        state.add_device(model.device.RubberFactory((20,22)))
        state.add_device(model.device.RubberFactory((20,17)))

        state.add_device(model.device.MetalFactory((33,35)))
        state.add_device(model.device.MetalFactory((24,17)))
        state.add_device(model.device.MetalFactory((16,22)))
        state.add_device(model.device.MetalFactory((24,22)))
        state.add_device(model.device.MetalFactory((16,17)))

        state.add_elf((1,36))
        state.add_elf((2,36))

        state.metal = 3200.0
        state.rubber = 1200.0
        
        return state
 
SpaciousLevel = menulevel(SpaciousLevel)


class MonsterLevel(Level):
    name = 'Deeper Inside'
    desc = "Further inside the Evil Doctor's lair\nsome more of the tribe are trapped."
    size = (40, 40)
    
    @classmethod
    def build_state(cls):
        state = model.gamestate.Gamestate(*cls.size)
        
        state.add_spring((4,1))
        
        state.pgrid.lock()
        state.pgrid.add_platform((3,0), 5)
        state.pgrid.add_platform((37,3), 3)
        state.pgrid.add_platform((37,7), 3)
        state.pgrid.add_platform((37,11), 3)
        state.pgrid.add_platform((26,15), 14)
        state.pgrid.add_platform((0,15), 5)
        state.pgrid.add_platform((0,27), 33)

        state.pgrid.add_ladder((7,0), 1)
        state.pgrid.add_ladder((37,0), 4)
        state.pgrid.add_ladder((39,4), 4)
        state.pgrid.add_ladder((37,8), 4)
        state.pgrid.add_ladder((39,12), 4)
        state.pgrid.add_ladder((1,23), 5)
        state.pgrid.unlock()
        
        state.add_device(model.device.GumballMachine((2,34), gumballs=4))
        state.add_device(model.device.GumballMachine((10,36), gumballs=2))
        state.add_device(model.device.GumballMachine((25,4), gumballs=1))
        state.add_device(model.device.GumballMachine((31,6), gumballs=1))

        state.add_device(model.device.RubberFactory((17,0)))
        state.add_device(model.device.RubberFactory((33,16)))
        
        state.add_device(model.device.MetalFactory((28,28)))
        state.add_device(model.device.MetalFactory((32,28)))
        state.add_device(model.device.MetalFactory((37,16)))
        state.add_device(model.device.MetalFactory((1,0)))
        
        state.add_cog((10,1), 1)
        state.add_cog((12,1), 1)
        state.add_cog((14,1), 3)
        state.add_cog((14,3), 1)
        state.add_cog((1,16), 1)
        state.add_cog((27,16), 1)
        state.add_cog((14,29), 1)
        state.add_cog((14,16), 25) # omfg
        
        state.add_elf((10,0))
        state.add_elf((11,0))
        
        cog = state.mgrid[10,1]
        state.add_belt(state.spring, cog)
        
        state.recalculate_ratios()
        
        return state
    
MonsterLevel = menulevel(MonsterLevel)


class RandomLevel(Level):
    name = "The Workshop"
    desc = "You've made it to the Doctor's workshop\nbut can you free the remaining elves?"
    size = (30, 30)
    prereqs = [MonsterLevel]

    @classmethod
    def build_state(cls):
        state = model.gamestate.Gamestate(*cls.size)

        state.add_spring((3, 0))

        state.pgrid.lock()
        state.pgrid.add_platform((2, 10), 10)
        state.pgrid.add_platform((15, 18), 7)
        state.pgrid.add_ladder((27, 6), 7)
        state.pgrid.add_ladder((10, 13), 4)
        state.pgrid.add_ladder((3, 13), 5)
        state.pgrid.unlock()

        state.add_cog((7, 0), 3)
        state.add_cog((20, 4), 1)
        state.add_cog((20, 8), 7)
        state.add_cog((10, 27), 3)
        state.add_cog((16, 27), 5)
        
        cog1 = state.mgrid[10, 27]
        cog2 = state.mgrid[16, 27]

        state.add_belt(cog1, cog2)

        state.add_device(model.device.MetalFactory((16, 1)))
        state.add_device(model.device.MetalFactory((24, 14)))
        state.add_device(model.device.RubberFactory((4, 11)))
        state.add_device(model.device.GumballMachine((8, 11)))
        state.add_device(model.device.GumballMachine((26, 27)))

        state.add_elf((5, 0))
        state.add_elf((6, 0))
        
        state.metal = 2000.0

        return state

RandomLevel = menulevel(RandomLevel)


class TallLevel(Level):
    name = 'Tower'
    desc = 'In the highest room of the tallest\ntower, the Doctor has trapped a\nsmall cadre of your charge.'
    size = (15, 40)
    prereqs = [RandomLevel]

    @classmethod
    def build_state(cls):
        state = model.gamestate.Gamestate(*cls.size)

        state.add_spring((2, 0))

        state.pgrid.lock()
        state.pgrid.add_platform((0, 35), 15)
        state.pgrid.add_ladder((12, 0), 5)
        state.pgrid.unlock()

        state.add_device(model.device.MetalFactory((12, 6)))
        state.add_device(model.device.MetalFactory((4, 16)))
        state.add_device(model.device.MetalFactory((12, 27)))
        state.add_device(model.device.GumballMachine((7, 36)))

        state.add_elf((4, 0))
        state.add_elf((5, 0))
        state.add_elf((6, 0))
        
        state.metal = 1500.0

        return state

TallLevel = menulevel(TallLevel)


class BigRubberLevel(Level):
    name = 'Rubber Rubber'
    desc = 'Deep inside the Evil Doctor\'s realm\nyou encounter new and exciting\nmachines.'
    size = (39, 40)
    prereqs = [TallLevel]

    @classmethod
    def build_state(cls):
        state = model.gamestate.Gamestate(*cls.size)

        state.add_spring((3, 2))

        state.pgrid.lock()
        state.pgrid.add_platform((2, 1), 5)
        state.pgrid.add_ladder((6, 0), 2)
        state.pgrid.add_platform((16, 11), 5)
        state.pgrid.add_ladder((18, 0), 12)
        state.pgrid.add_platform((27, 0), 12)
        state.pgrid.add_platform((30, 4), 9)
        state.pgrid.add_platform((33, 8), 6)
        state.pgrid.add_platform((36, 12), 3)
        state.pgrid.add_ladder((38, 0), 13)
        state.pgrid.unlock()

        state.add_cog((12, 0), 1)
        state.add_cog((18, 10), 1)

        cog1 = state.mgrid[12, 0]
        cog2 = state.mgrid[18, 10]
        
        metal_factory = model.device.MetalFactory((10, 1))
        heavy_rubber_factory = model.device.HeavyRubberFactory((17, 12))
        
        state.add_device(metal_factory)
        state.add_device(heavy_rubber_factory)
        state.add_device(model.device.GumballMachine((28, 1), gumballs=1))
        state.add_device(model.device.GumballMachine((31, 1), gumballs=1))
        state.add_device(model.device.GumballMachine((31, 5), gumballs=1))
        state.add_device(model.device.GumballMachine((34, 1), gumballs=1))
        state.add_device(model.device.GumballMachine((34, 5), gumballs=1))
        state.add_device(model.device.GumballMachine((34, 9), gumballs=1))
        state.add_device(model.device.GumballMachine((37, 1), gumballs=1))
        state.add_device(model.device.GumballMachine((37, 5), gumballs=1))
        state.add_device(model.device.GumballMachine((37, 9), gumballs=1))
        state.add_device(model.device.GumballMachine((37, 13), gumballs=1))

        state.add_belt(state.spring, metal_factory)
        state.add_belt(cog1, metal_factory)
        state.add_belt(cog2, heavy_rubber_factory)

        state.add_elf((5, 0))
        state.add_elf((6, 0))
        state.add_elf((7, 0))

        state.metal = 0.0
        state.rubber = 0.0

        state.recalculate_ratios()

        return state

BigRubberLevel = menulevel(BigRubberLevel)


class ChoiceLevel(Level):
    name = 'Final Choice'
    desc = 'Victory is close at hand, but will\nyou give in to temptation?'
    size = (70, 60)
    prereqs = [BigRubberLevel]

    @classmethod
    def build_state(cls):
        state = model.gamestate.Gamestate(*cls.size)

        state.add_spring((35, 25))

        state.pgrid.lock()
        state.pgrid.add_platform((31, 24), 9)
        state.pgrid.unlock()

        state.add_device(model.device.HeavyMetalFactory((5, 20)))
        state.add_device(model.device.HeavyRubberFactory((66, 20)))
        state.add_device(model.device.MetalFactory((32, 25)))
        state.add_device(model.device.RubberFactory((38, 25)))
        state.add_device(model.device.GumballMachine((35, 29), gumballs=1))
        state.add_device(model.device.GumballMachine((35, 34), gumballs=1))
        state.add_device(model.device.GumballMachine((35, 39), gumballs=1))
        state.add_device(model.device.GumballMachine((35, 44), gumballs=1))
        state.add_device(model.device.GumballMachine((35, 49), gumballs=1))
        state.add_device(model.device.GumballMachine((35, 54), gumballs=1))

        state.add_elf((33, 25))
        state.add_elf((34, 25))
        state.add_elf((36, 25))
        state.add_elf((37, 25))

        return state

ChoiceLevel = menulevel(ChoiceLevel)


class TitleLevel(Level):
    name = 'TITLE_LEVEL'
    desc = 'TITLE_LEVEL'
    size = (70, 50)
    camera = ((26, 22), 30)

    @classmethod
    def build_state(cls):
        state = model.gamestate.Gamestate(*cls.size)
    
        state.add_spring((21, 33))
        
        state.pgrid.lock()
        state.pgrid.add_platform((21,32), 2)
        state.pgrid.add_platform((20,31), 5)
        state.pgrid.add_platform((21,25), 9)
        state.pgrid.add_ladder((22, 32), 1)
        state.pgrid.add_ladder((24, 26), 6)
        state.pgrid.unlock()
        
        state.add_cog((26,34), 1)
        state.add_cog((27,34), 1)
        state.add_cog((29,34), 3)
        state.add_cog((26,28), 3)
        state.add_cog((26,26), 1)
        state.add_cog((25,26), 1)
        state.add_cog((23,26), 3)
        state.add_cog((23,24), 1)
        state.add_cog((23,20), 7)
        state.add_elf((20,32))

        cog1 = state.mgrid[26,34]
        cog2 = state.mgrid[26,28]
        cog3 = state.mgrid[29,34]
        
        state.add_belt(state.spring, cog1)
        state.add_belt(cog2, cog3)
        
        state.recalculate_ratios()
        state.winding_elves = [model.elf.Elf(state)]
        state.desired_winding_elves = 1
        
        state.random_destinations = [(20,32), (21,33), (21,26), (29,26)]
        
        return state
