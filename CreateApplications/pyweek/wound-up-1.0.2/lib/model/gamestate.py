'''gamestate.py - central state class definition'''

import device
import elf
import grid
import part
import task
from constants import *


class Gamestate(object):
    '''Main state object for the game.'''

    def __init__(self, width, height):
        '''width, height - dimensions of the grid'''

        self.pgrid = grid.PlatformGrid(width, height)
        self.mgrid = grid.MachineGrid()
        
        # collections of game objects
        self.cogs = set()
        self.belts = set()
        self.elves = set()
        self.winding_elves = set()
        self.desired_winding_elves = 0
        self.devices = set()
        self.tasks = [] # needs to be ordered
        self.spring = None
        self.deadtasks = set()
        self.deadbelts = set()

        self.rubber = 1000.0
        self.metal = 1000.0

        self.spring_speed = 0.0
        self.load_factor = 1.0
        self.power_share = {}
        self.power_total = 0.0
        
        self.ticks = 0
        self.won = False
        self.win_time = None
        
        self.metal_warning = False
        self.last_warning = -SCOTT_RESOURCE_WARNING_INTERVAL
        
        self.reset_sound_flags()
        
    def tick(self):
        '''update game objects'''
        self.ticks += 1
        
        self.spring.energy += len(self.winding_elves)
        output_energy = self.spring.energy * ENERGY_DECAY_FACTOR
        self.spring.energy -= output_energy
        
        self.power_total = 0.0
        for d in self.devices:
            self.power_share[d] = abs(d.g_ratio * d.get_load())
            self.power_total += self.power_share[d]
        if self.power_total > 0.0:
            for d in self.devices:
                d.add_energy(output_energy * self.power_share[d] / self.power_total)
        
        self.spring.tick(self)
        self.spring_speed = self.spring.get_angular_speed(self)
        # self.master_angle = self.spring.angle / self.spring.get_angular_speed(self)
        for c in self.cogs:
            c.tick(self)
        for d in self.devices:
            d.tick(self)
        for e in self.elves:
            e.tick(self)
        
        entertasks = [t for t in self.tasks if isinstance(t, task.EnterSpringTask)]
        destined_winding_elves = len(self.winding_elves) + len(entertasks)
        delta = self.desired_winding_elves - destined_winding_elves
        if delta > 0:
            for i in xrange(delta):
                self.add_task(task.EnterSpringTask(self))
        elif delta < 0:
            if -delta < len(entertasks):
                self.cancel_tasks(entertasks[delta:])
            else:
                self.cancel_tasks(entertasks)
                for i in xrange(-delta - len(entertasks)):
                    self.release_winding_elf()
        
        self.schedulable_elves = set([e for e in self.elves if e.task is None and not e.is_falling])
        transforms = []
        for t in self.tasks:
            if t.is_completed():
                self.deadtasks.add(t)
            else:
                result = t.update(self)
                if result is not None:
                    transforms += result
        for t in transforms:
            t()
        self.tasks = filter(lambda x: x not in self.deadtasks, self.tasks)

        if self.ticks % SCOTT_RESOURCE_WARNING_CHECK == 0:
            self.check_shortages()

        if self.elves_remaining() == 0 and self.win_time is None:
            self.won = True
            self.win_time = self.ticks

    # adding game objects
    def add_task(self, task):
        if self.get_num_eventual_worker_elves() < task.elves_needed():
            self.elves_needed = True
        else:
            self.task_added = True
        self.tasks.append(task)

    def add_belt(self, part1, part2):
        newbelt = part.Belt(part1, part2)
        self.belts.add(newbelt)

    def add_cog(self, pos, diam):
        newcog = part.Cog(pos, diam)
        self.mgrid.add_part(newcog)
        self.cogs.add(newcog)
    
    def add_spring(self, pos):
        newspring = part.Spring(pos)
        self.mgrid.add_part(newspring)
        self.spring = newspring

    def add_elf(self, pos):
        newelf = elf.Elf(self, pos)
        self.elves.add(newelf)
        self.elf_emerged = True
    
    def add_device(self, device):
        self.mgrid.add_part(device)
        self.devices.add(device)

    # belt operations
    def belt_cost(self, part1, part2):
        return RUBBER_COST_BELT * (((part1.pos[0] - part2.pos[0]) ** 2) +
                                   ((part1.pos[1] - part2.pos[1]) ** 2))
    
    def destroy_belt(self, belt, refund=False):
        '''remove the belt from the game'''
        if refund:
            self.rubber += self.belt_cost(belt.part1, belt.part2) / 2
        self.belts.discard(belt)
        self.deadbelts.add(belt)

    def snap_belts(self, start):
        '''destroy all belts in the same system as a given part'''
        old = set()
        new = set([start])
        belts = set()
        while len(new) > 0:
            part = new.pop()
            belts.update(self.connected_belts(part))
            new.update(self.interlocking_cogs(part))
            new.update(self.connected_parts(part))
            old.add(part)
            new -= old
        for b in belts:
            self.destroy_belt(b)

    
    # cog operations
    def destroy_cog(self, cog, refund=False):
        '''remove a cog, optionally refunding the metal'''
        for belt in [b for b in self.belts if b.part1 == cog or b.part2 == cog]:
            self.destroy_belt(belt, refund=refund)
        if refund:
            self.metal += METAL_COST_COG[cog.diam] / 2
        self.mgrid.remove_part(cog)
        self.cogs.discard(cog)
    
    def cogs_interlock(self, cog1, cog2):
        '''returns true of two cogs interlock'''
        dx = abs(cog1.pos[0] - cog2.pos[0])
        dy = abs(cog1.pos[1] - cog2.pos[1])
        reqdist = (cog1.diam / 2) + (cog2.diam / 2) + 1
        return (dx == reqdist and dy == 0) or (dx == 0 and dy == reqdist)

    def interlocking_cogs(self, mycog):
        '''returns a set of cogs interlocking with a given cog'''
        if not isinstance(mycog, part.Cog):
            return set()
        cx, cy = mycog.pos
        s = (mycog.diam / 2) + 1
        res = set()
        for hotspot in [(cx-s, cy), (cx+s, cy), (cx, cy-s), (cx, cy+s)]:
            othercog = self.mgrid[hotspot]
            if isinstance(othercog, part.Cog) and self.cogs_interlock(mycog, othercog):
                res.add(othercog)
        return res
    
    def connected_parts(self, mypart):
        '''returns a set of parts connect to a given cog by belts'''
        res = set()
        res.update([b.part2 for b in self.belts if b.part1 == mypart])
        res.update([b.part1 for b in self.belts if b.part2 == mypart])
        return res
        
    def connected_belts(self, mypart):
        '''returns a list of belts connected to a given cog'''
        return set([b for b in self.belts if b.part1 == mypart or b.part2 == mypart])
    

    # speed operations
    def reset_ratios(self):
        '''set the gearing ratios of all parts to zero'''
        for c in self.cogs:
            c.g_ratio = 0.0
        for d in self.devices:
            d.g_ratio = 0.0

    def _recalculate_ratios_i(self, current_parts, old_parts, load):
        '''recursively distribute gearing_ratios to all parts'''
        new_parts = set()

        def ratios_differ(speed1, speed2):
            return abs(speed1 - speed2) > 0.00000001

        for p, s in current_parts:
            p.g_ratio = s
            load += p.get_load()
            geared_cogs = [(p2, -s*p.diam/p2.diam) for p2 in self.interlocking_cogs(p)]
            driven_parts = [(p2, s) for p2 in self.connected_parts(p)]
            new_parts.update(geared_cogs)
            new_parts.update(driven_parts)
            old_parts.add(p)

        for p, s in new_parts:
            if p.g_ratio != 0 and ratios_differ(s, p.g_ratio):
                raise part.BrokenBeltException

        new_parts = [(p, s) for (p, s) in new_parts if p not in old_parts ]
        if new_parts:
            return self._recalculate_ratios_i(new_parts, old_parts, load)
        return load

    def recalculate_ratios(self):
        '''try to set the part gearing ratios, snap belts if it doesn't work'''
        self.reset_ratios()

        try:
            load = self._recalculate_ratios_i(set([(self.spring, 1.0)]), set(), 0.0)
        except part.BrokenBeltException:
            self.snap_belts(self.spring)
            self.reset_ratios()
            load = self._recalculate_ratios_i(set([(self.spring, 1.0)]), set(), 0.0)

        # NB. Load is never zero because the spring itself has a load of 1.0
        self.load_factor = 1.0 / load

    def get_power_share(self, device):
        if device not in self.power_share:
            return 0
        ps = self.power_share[device]
        if ps == 0: # avoid dividing by 0
            return 0
        return ps / self.power_total

    # elf-related operations
    def recalculate_paths(self):
        '''find all elves' paths again'''
        for e in self.elves:
            if len(e.path) > 1:
                dest = e.path[-1]
                e.send_to(self, dest)
                
    def get_num_worker_elves(self):
        '''get number of elves eventually available for completing tasks'''
        return len(self.elves)

    def get_num_eventual_worker_elves(self):
        entertasks = [t for t in self.tasks if isinstance(t, task.EnterSpringTask)]
        return self.get_num_worker_elves() - len(entertasks)

    def acquire_winding_elf(self, elf):
        '''put elf in the spring'''
        self.elves.remove(elf)
        self.winding_elves.add(elf)
        
    def release_winding_elf(self):
        '''release an elf from the spring'''
        if len(self.winding_elves) > 0:
            elf = self.winding_elves.pop()
            self.elves.add(elf)
            elf.path = [self.spring.get_door_pos()]
            elf.task = None

    def elves_remaining(self):
        tally = 0
        for d in self.devices:
            if isinstance(d, device.GumballMachine):
                tally += d.gumballs
        return tally
        
    def inc_desired_winding_elves(self):
        self.desired_winding_elves += 1
    
    def dec_desired_winding_elves(self):
        self.desired_winding_elves = max(self.desired_winding_elves - 1, 0)
        
    def get_desired_winding_elves(self):
        return self.desired_winding_elves
        
    def cancel_tasks(self, tasks):
        for t in tasks:
            t.abort(self)
            self.tasks.remove(t)
        
    # interface operations
    def reset_sound_flags(self):
        self.elf_emerged = False
        self.task_added = False
        self.elves_needed = False
        self.metal_low = False
        self.rubber_low = False

    def get_text(self, pos):
        elf_text, part_text = [], ""
        elves = [e for e in self.elves if e.path[0] == pos]
        if len(elves) > 0:
            elf_text = [elves[0].name, elves[0].bio]
        part = self.mgrid[pos]
        if part is not None:
            part_text = part.get_description(self)
        return elf_text + [part_text]
        
    def check_shortages(self):
        if self.ticks < self.last_warning + SCOTT_RESOURCE_WARNING_INTERVAL:
            return
        metal_needed = 0
        rubber_needed = 0
        for t in self.tasks:
            metal_needed += t.get_metal_cost()
            rubber_needed += t.get_rubber_cost()
        metal_warning = metal_needed > self.metal
        rubber_warning = rubber_needed > self.rubber
        if metal_warning and rubber_warning:
            if self.metal_warning:
                metal_warning = False
            else:
                rubber_warning = False
        if metal_warning:
            self.metal_low = True
            self.metal_warning = True
            self.last_warning = self.ticks
        if rubber_warning:
            self.rubber_low = True
            self.metal_warning = False
            self.last_warning = self.ticks
