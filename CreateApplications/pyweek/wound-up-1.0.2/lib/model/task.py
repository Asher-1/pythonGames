'''task.py - things for elves to do'''

import path
import part
from constants import *


class Request(object):

    def __init__(self, positions):
        self.positions = positions
        self.elf = None
        self.rethink_timer = 0
        
    def find_free_elves(self, gs):
        return set([e for e in gs.schedulable_elves if e.task is None])
        
    def get_elf(self, gs):
        self.rethink_timer += 1
        old_elf = self.elf
        old_elf_set = set([old_elf])
        old_elf_set.discard(None)
        if self.rethink_timer > RETHINK_DELAY:
            self.rethink_timer = 0
            if self.elf:
                self.elf.task = None
                self.elf = None
        if self.elf is None:
            best_elf, best_path = None, None
            for e in old_elf_set | self.find_free_elves(gs):
                for dest in self.positions:
                    p = path.find_best_path(gs.pgrid, e.path[0], dest)
                    if p is not None and (best_path is None or len(best_path) > len(p)):
                        best_elf = e
                        best_path = p
            if best_elf is not None:
                best_elf.task = self
                self.elf = best_elf
                self.elf.set_path(best_path)
                if old_elf is not None and old_elf != self.elf:
                    old_elf.stop()
                if self.elf.path[0] in self.positions:
                    self.elf.task = None
                    return self.elf
                return None
            else:
                return None
        else:
            if self.elf.path[0] in self.positions:
                self.elf.task = None
                return self.elf
            else:
                return None

    def release(self):
        if self.elf:
            self.elf.task = None
            self.elf.stop()
            self.elf = None


class Task(object):
    
    def __init__(self):
        self.complete = False
        self.successful = False

    def update(self, gs):
        pass
        
    def release(self):
        pass

    def set_completed(self):
        self.complete = True
        self.release()
        
    def is_completed(self):
        return self.complete
        
    def abort(self, gs):
        self.set_completed()
        
    def find_free_elves(self, gs):
        return set([e for e in gs.elves if not e.is_falling and e.task is None])

    def find_nearest_elf(self, gs, pos):
        best_elf, best_path = None, None
        for e in self.find_free_elves(gs):
            p = path.find_best_path(gs.pgrid, e.path[0], pos)
            if p is not None:
                if best_path is None or len(best_path) > len(p):
                    best_elf = e
                    best_path = p
        return best_elf, best_path

    def elves_needed(self):
        return 1
        
    def get_metal_cost(self):
        return 0
        
    def get_rubber_cost(self):
        return 0
        
    @staticmethod
    def is_valid():
        return True
    

class GoTask(Task):
    
    def __init__(self, gs, pos):
        Task.__init__(self)
        self.pos = pos # for display purposes
        self.req = Request([pos])
    
    def update(self, gs):
        elf = self.req.get_elf(gs)
        if elf is not None:
            self.successful = True
            self.set_completed()

    def release(self):
        self.req.release()

    @staticmethod
    def is_valid(gs, pos):
        return True


class EnterSpringTask(Task):

    def __init__(self, gs):
        Task.__init__(self)
        self.req = Request([gs.spring.get_door_pos()])
        
    def update(self, gs):
        elf = self.req.get_elf(gs)
        if elf is not None:
            gs.acquire_winding_elf(elf)
            self.successful = True
            self.set_completed()
            
    def release(self):
        self.req.release()
        
    @staticmethod
    def is_valid(gs):
        return True


class CreateCogTask(Task):

    def __init__(self, gs, pos, diam):
        Task.__init__(self)
        self.pos = pos
        self.diam = diam
        self.req = Request([pos])
        self.cost = METAL_COST_COG[diam]

    def update(self, gs):
        if gs.metal < self.cost:
            self.req.release()
            return
        elf = self.req.get_elf(gs)
        if elf is not None:
            try:
                gs.add_cog(self.pos, self.diam)
                gs.metal -= self.cost
                self.successful = True
            except:
                pass
            gs.recalculate_ratios()
            self.set_completed()

    def get_metal_cost(self):
        return self.cost

    def release(self):
        self.req.release()
        
    @staticmethod
    def is_valid(gs, pos, diam):
        for xo, yo in part.Cog.get_region(diam):
            if gs.mgrid[pos[0]+xo, pos[1]+yo] is not None:
                return False
        return True


class RemoveCogTask(Task):

    def __init__(self, gs, cog):
        Task.__init__(self)
        if not isinstance(cog, part.Cog):
            raise ValueError("RemoveCogTask was given something not a cog")
        self.cog = cog
        self.req = Request([cog.pos])
        
    def update(self, gs):
        elf = self.req.get_elf(gs)
        if elf is not None:
            gs.destroy_cog(self.cog, refund=True)
            gs.recalculate_ratios()
            self.successful = True
            self.set_completed()

    def release(self):
        self.req.release()

    @staticmethod
    def is_valid(gs, cog):
        return isinstance(cog, part.Cog) and METAL_COST_COG.has_key(cog.diam)


class ConnectTask(Task):

    def __init__(self, gs, part1, part2):
        Task.__init__(self)
        self.part1 = part1
        self.part2 = part2
        self.req1 = Request([part1.pos])
        self.req2 = Request([part2.pos])
        self.elf1 = None
        self.elf2 = None
        self.phase = 0
        self.rendezvous = None
        self.cost = gs.belt_cost(part1, part2)

    def update(self, gs):
        if self.rendezvous is None:
            jpath = path.find_best_path(gs.pgrid, self.part1.pos, self.part2.pos)
            if jpath is None:
                # can't be done yet
                return
            else:
                self.rendezvous = jpath[len(jpath) // 2]

        # we haven't spent the rubber yet and now there isn't enough
        if gs.rubber < self.cost and self.phase == 0:
            self.req1.release()
            self.req2.release()
            return
    
        # don't try this if less than two elves are available
        if gs.get_num_worker_elves() >= 2:
            if self.elf1 is None:
                self.elf1 = self.req1.get_elf(gs)
                if self.elf1 is not None:
                    self.elf1.task = self
            if self.elf2 is None:
                self.elf2 = self.req2.get_elf(gs)
                if self.elf2 is not None:
                    self.elf2.task = self

        if self.elf1 is not None and self.elf2 is not None:
            # watch out! this task could currently technically lock elves
            # forever if parts of the map become disconnected while it is
            # executing!
            if self.phase == 0:
                self.phase = 1
                gs.rubber -= self.cost
                self.elf1.send_to(gs, self.rendezvous)
                self.elf2.send_to(gs, self.rendezvous)
            if self.phase == 1 and self.elf1.path[0] == self.rendezvous and \
                                    self.elf2.path[0] == self.rendezvous:
                self.phase = 2
                self.elf1.send_to(gs, self.part1.pos)
                self.elf2.send_to(gs, self.part2.pos)
            if self.phase == 2 and self.elf1.path[0] == self.part1.pos and \
                                    self.elf2.path[0] == self.part2.pos:
                gs.add_belt(self.part1, self.part2)
                gs.recalculate_ratios()
                self.phase = 3
                self.successful = True
                self.set_completed()
        
    def release(self):
        self.req1.release()
        self.req2.release()
        if self.elf1: self.elf1.task = None
        if self.elf2: self.elf2.task = None
        self.elf1 = None
        self.elf2 = None

    def abort(self, gs):
        if self.phase > 0:
            gs.rubber += self.cost
        Task.abort(self, gs)
        
    def elves_needed(self):
        return 2
        
    def get_rubber_cost(self):
        return self.cost

    @staticmethod
    def is_valid(gs, part1, part2):
        return part1 is not None and part2 is not None and part1 != part2 and part1 not in gs.connected_parts(part2)


class DisconnectTask(Task):

    def __init__(self, gs, belt):
        Task.__init__(self)
        self.belt = belt
        self.req = Request([belt.part1.pos, belt.part2.pos])

    def update(self, gs):
        elf = self.req.get_elf(gs)
        if elf is not None:
            gs.destroy_belt(self.belt, refund=True)
            gs.recalculate_ratios()
            self.successful = True
            self.set_completed()

    def release(self):
        self.req.release()
        
    @staticmethod
    def is_valid(gs, belt):
        return belt is not None


class BuildTask(Task):

    def __init__(self, gs, pos):
        Task.__init__(self)
        self.pos = pos
        self.req = Request(self.get_valid_locations(gs))
        self.dest = None
        
    def update(self, gs):
        if self.already_completed(gs):
            self.abort(gs)
            return
        if gs.metal < self.get_metal_cost():
            self.req.release()
            return
        vl = self.get_valid_locations(gs)
        if vl != self.req.positions:
            self.req.release()
            self.req = Request(vl)
        elf = self.req.get_elf(gs)
        if elf is not None:
            def t():
                gs.pgrid[self.pos] = self.transform(gs.pgrid[self.pos])
            gs.metal -= self.get_metal_cost()
            self.successful = True
            self.set_completed()
            return [t]
    
    def release(self):
        self.req.release()
    

class BuildPlatformTask(BuildTask):
    
    def get_valid_locations(self, gs):
        res = set()
        cx, cy = self.pos
        if gs.pgrid.cell_has_floor((cx-1, cy+1)): res.add((cx-1, cy+1))
        if gs.pgrid.cell_has_floor((cx+1, cy+1)): res.add((cx+1, cy+1))
        if gs.pgrid.cell_has_ladder((cx, cy+1)): res.add((cx, cy+1))
        if gs.pgrid.cell_has_ladder((cx, cy)): res.add((cx, cy))
        return res

    def get_metal_cost(self):
        return METAL_COST_PLATFORM

    def transform(self, (plat, ladder)):
        return (True, ladder)

    def already_completed(self, gs):
        return gs.pgrid[self.pos][0]

    @staticmethod
    def is_valid(gs, pos):
        return not gs.pgrid[pos][0]


class BuildLadderTask(BuildTask):

    def get_valid_locations(self, gs):
        res = set()
        cx, cy = self.pos
        if gs.pgrid.cell_has_ladder((cx,cy-1)): res.add((cx,cy-1))
        if gs.pgrid.cell_has_ladder((cx,cy+1)): res.add((cx,cy+1))
        if gs.pgrid.cell_has_floor((cx,cy)): res.add((cx,cy))
        if gs.pgrid.cell_has_floor((cx,cy+1)): res.add((cx,cy+1))
        return res

    def get_metal_cost(self):
        return METAL_COST_LADDER
        
    def transform(self, (plat, ladder)):
        return (plat, True)

    def already_completed(self, gs):
        return gs.pgrid[self.pos][1]

    @staticmethod
    def is_valid(gs, pos):
        return not gs.pgrid[pos][1]
