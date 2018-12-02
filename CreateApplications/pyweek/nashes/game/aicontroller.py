"""Controls the AI of the soldiers"""

import math
import random
import common
import serge.common
from serge.simplevecs import Vec2d
from serge.blocks import behaviourtree as bt
from theme import G, theme, M_FIXING, M_PATROLLING, M_GOING_TO_REST, M_SEARCHING, \
    M_NONE, M_INVESTIGATING, M_CHASING, M_RESTING


class AIController(serge.common.Loggable):
    """The AI controller"""

    def __init__(self, grid, mob, players):
        """Initialise the controller"""
        self.addLogger()
        #
        self.grid = grid
        self.mob = mob
        self.players = players
        self.name = mob.name
        #
        self.current_target = None
        self.current_path = None
        self.mode = M_NONE
        self.search_points = None
        self.max_search_locations = G('ai-max-search-locations')
        self.max_controllable_distance = G('ai-controllables-distance')
        self.max_tiredness = G('ai-max-tiredness')
        self.min_tiredness = G('ai-min-tiredness')
        self.fixable_items = []
        self.fixing_item = None
        self.tiredness = 0
        self.waiting_for_free_cell = 0
        #
        self.ai_timings = G('ai-timings')

    def tick(self, world_model):
        """Tick the tree"""
        #
        # Increase tiredness
        if self.mode == M_RESTING:
            self.tiredness -= 1
        else:
            self.tiredness = min(self.tiredness + 1, self.max_tiredness)
        #
        # Capture if we can
        for player in self.players:
            if self.mob.canCapture(player):
                self.mob.capturePlayer(player)
                return
        #
        # If we can see the player then give chase
        for player in self.players:
            if self.canSeePlayer(player):
                self.setMode(M_CHASING)
                if self.setDestination(player.cx, player.cy):
                    return
        #
        # Finished resting
        if self.mode == M_RESTING:
            if self.tiredness <= 0:
                self.tiredness = 0
                self.setMode(M_NONE)
                return
        #
        # If we are patrolling and tired then go to sleep
        if self.mode == M_PATROLLING and self.tiredness >= self.max_tiredness:
            if self.goToRest():
                return
        #
        # Put a mode in place
        if self.mode == M_NONE:
            if self.fixable_items:
                self.setMode(M_FIXING)
            else:
                self.goToPatrolling()
            return
        #
        # If we have fixable items then don't patrol
        if self.mode == M_PATROLLING and self.fixable_items:
            self.setMode(M_FIXING)
            self.current_target = None
        #
        # If we do not have a target then go into patrolling mode
        if not self.current_target:
            self.selectNewDestination()
            return
        #
        # Did we arrive
        if (self.mob.cx, self.mob.cy) == self.current_target:
            if self.mode == M_GOING_TO_REST:
                self.setMode(M_RESTING)
            else:
                self.log.debug('%s arrived at destination' % self.name)
            self.current_target = None
            return
        #
        # Do we have a path
        if not self.current_path or self.current_path[-1] != self.current_target:
            self.log.debug('%s no path - setting path to target' % self.name)
            self.pathToTarget()
            return
        #
        # Are we on the path
        if self.current_path[0] != (self.mob.cx, self.mob.cy):
            self.pathToTarget()
        #
        # Move towards the target
        self.moveTowardsTarget()
        #
        # Check controllables
        if self.mode in [M_PATROLLING, M_NONE, M_RESTING, M_SEARCHING]:
            self.checkBrokenItems()

    def setMode(self, new_mode):
        """Set the mode"""
        if self.mode != new_mode:
            self.mob.modeSwitch(self.mode, new_mode)
            self.log.debug('%s going to mode "%s"' % (self.name, new_mode))
            self.mode = new_mode
            if new_mode == M_CHASING:
                self.grid.event_pump.processEvent((common.E_AI_SAW_PLAYER, self))

    def selectNewDestination(self):
        """Select a new destination"""
        self.log.debug('%s selecting a new destination (%s)' % (self.name, self.mode))
        #
        if self.mode == M_PATROLLING:
            patrol_points = self.mob.patrol_points
            for idx, point in enumerate(patrol_points):
                if (self.mob.cx, self.mob.cy) == (point.cx, point.cy):
                    if idx == len(patrol_points) - 1:
                        self.setDestination(patrol_points[0].cx, patrol_points[0].cy)
                        return
                    else:
                        self.setDestination(patrol_points[idx + 1].cx, patrol_points[idx + 1].cy)
                        return
            else:
                if patrol_points:
                    self.setDestination(patrol_points[0].cx, patrol_points[0].cy)
                else:
                    self.log.debug('%s no good patrol points' % self.name)
                    self.setMode(M_NONE)
        elif self.mode == M_INVESTIGATING:
            self.goToSearch()
        elif self.mode == M_SEARCHING:
            if self.search_points:
                self.current_target = self.grid.getUnallocatedSearch(self, self.search_points)
            else:
                self.log.debug('%s no more search points. Returning to patrol' % self.name)
                self.setMode(M_NONE)
        elif self.mode == M_FIXING:
            if self.fixable_items:
                self.fixing_item = item = self.fixable_items.pop()
                if not item.isWorkingNormally():
                    self.setDestination(item.controlled_by_object.cx, item.controlled_by_object.cy)
            else:
                self.setMode(M_NONE)
        elif self.mode == M_GOING_TO_REST:
            if self.mob.rest_point:
                self.setDestination(self.mob.rest_point.cx, self.mob.rest_point.cy)
            else:
                self.log.info('%s does not have a rest point' % self.mob.name)
        elif self.mode == M_RESTING:
            pass
        elif self.mode == M_CHASING:
            self.goToSearch()
        else:
            self.log.info('%s no destination and invalid mode (%s)' % (self.name, self.mode))

    def goToSearch(self):
        """Start searching"""
        self.search_points = self.grid.getSearchWithinDistance(self.mob)
        # Constrain searches
        self.search_points = self.search_points[:self.max_search_locations]
        self.setMode(M_SEARCHING)

    def goToPatrolling(self):
        """Try to go to patrolling mode"""
        if self.mob.canPatrol():
            self.setMode(M_PATROLLING)
        else:
            self.setMode(M_GOING_TO_REST)

    def isResting(self):
        """Return True if we are resting and available for work"""
        return self.mode in (M_RESTING, M_NONE) and self.tiredness < self.min_tiredness

    def goToRest(self):
        """Switch to going to rest"""
        #
        # We need to find a resting compatriot
        resting = [ai for ai in self.grid.findRestingAIs() if ai != self]
        if resting:
            chosen = random.choice(resting)
            self.mob.switchPatrolsWith(chosen)
            self.setMode(M_GOING_TO_REST)
            self.current_target = None
            return True
        else:
            self.log.debug('%s tired but nobody to switch with' % self.name)
            return False

    def moveTowardsTarget(self):
        """Move towards the target"""
        self.current_path.pop(0)
        #
        # Did we get to our controller to fix a broken item?
        if self.mode == M_FIXING and len(self.current_path) == 1:
            # Arrived at controller
            control_item = self.grid.getObjectAt(*self.current_path[0])
            if self.fixing_item.isWorkingNormally():
                self.mob.modeSwitch('arrived-to-fix', 'already-fixed')
                self.log.debug('%s, %s is already fixed!' % (self.name, self.fixing_item.name))
            else:
                self.log.debug('%s, %s is still broken. Toggling %s' % (self.name, self.fixing_item.name, control_item.name))
                self.mob.modeSwitch('arrived-to-fix', 'fixed-it')
                control_item.interactWith()
            self.current_target = None
            self.current_path = None
        #
        elif self.current_path:
            #
            # Check if a door and if so then we should open it
            door = self.grid.getDoorAt(*self.current_path[0])
            if door and not door.is_open:
                self.log.info('Saw a door ahead of us (%s)' % door.name)
                door.is_open = True
                if door.is_locked:
                    self.mob.speech_hint = 'opening', 'door'
                return
            #
            # If cell is free, or we have been waiting a while
            if self.grid.nobodyAtLocation(self.current_path[0]) or self.waiting_for_free_cell > 2:
                nx, ny = self.current_path[0]
                self.mob.cx, self.mob.cy = nx, ny
                self.log.debug('%s moving to %s, %s' % (self.name, self.mob.cx, self.mob.cy))
                self.waiting_for_free_cell = 0
            else:
                self.log.debug('%s: somebody already in cell %s. Waiting' % (self.name, self.current_path[0]))
                self.waiting_for_free_cell += 1

    def pathToTarget(self):
        """Set a path to the target"""
        self.current_path = self.grid.getPath(
            (self.mob.cx, self.mob.cy), self.current_target
        )

    def setDestination(self, cx, cy):
        """Set a new destination point"""
        if not self.current_target or self.current_target != (cx, cy):
            self.log.debug('%s set destination to %s, %s' % (self.name, cx, cy))
            self.current_target = (cx, cy)
            self.current_path = None
            return True
        else:
            return False

    def canSeePlayer(self, player):
        """Return True if we can see the player"""
        return self.grid.hasLineOfSight(self.mob, player)

    def investigatePosition(self, cx, cy):
        """We found a reason to investigate the location"""
        if self.mode != M_CHASING:
            self.setMode(M_INVESTIGATING)
            self.current_target = (cx, cy)

    def checkBrokenItems(self):
        """Check any controllables near us are working"""
        in_range = self.grid.getBrokenItemsWithin(self.mob, self.max_controllable_distance)
        for item in in_range:
            if item not in self.fixable_items and not item.isWorkingNormally():
                self.log.debug('%s found a fixable item (%s)' % (self.name, item.name))
                self.fixable_items.append(item)


class WorldModel(object):
    """A place holder for the world"""

    me = None
    player = None
    grid = None


class CallMethod(bt.Action):
    """Call a method"""

    def __init__(self, name, method):
        """Initialise the action"""
        super(CallMethod, self).__init__(name)
        #
        self.method = method

    def doAction(self, world):
        """Capture"""
        result = self.method(world)
        if result:
            yield self.S_SUCCESS
        else:
            yield self.S_FAILURE