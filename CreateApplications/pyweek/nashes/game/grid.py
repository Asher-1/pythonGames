"""Represents the grid of squares that are the level"""

import os
import math
import pygame
import networkx
import serge.common
import serge.sound
from serge.simplevecs import Vec2d
import serge.blocks.tiled
import common
from theme import G, theme
import aicontroller


class LevelGrid(serge.common.Loggable):
    """Initialise the grid"""

    def __init__(self, level_file_name, event_pump):
        """Initialise the grid"""
        super(LevelGrid, self).addLogger()
        #
        LevelGrid.event_pump = event_pump
        #
        self.object_types = {
            'door': Door,
            'camera': Camera,
            'pressure-mat': PressurePad,
            'patrol-point': PatrolPoint,
            'controller': Controller,
            'ai': AI,
            'player': Player,
            'doomsday-device': DoomsdayDevice,
            'doomsday-switch': DoomsdaySwitch,
            'exit': Exit,
        }
        #
        self.initFromFile(level_file_name)
        #

    def initFromFile(self, filename):
        """Initialise the level from a tiled file"""
        self.tiled = serge.blocks.tiled.Tiled(filename)
        #
        # Create the images
        self.background = self.createImageFromLayer('Background')
        self.foreground = self.createImageFromLayer('Foreground')
        #
        self.objects = self.createObjectsFrom('Objects')
        self.doors = dict([((obj.cx, obj.cy), obj) for key, obj in self.objects.iteritems() if obj.type == 'door'])
        self.interactables = dict([((obj.cx, obj.cy), obj) for key, obj in self.objects.iteritems() if obj.interaction_name])
        self.breakables = [item for item in self.objects.values() if item.is_breakable]
        self.ais = self.createObjectsFrom('AIs')
        self.patrol_points = self.createPatrolPoints('Patrols')
        self.rest_points = self.createRestPoints('Rest points')
        self.search_points = self.createFromTiles('Searches', SearchPoint)
        self.not_walkable = self.createFromTiles('Walkable', WalkablePoint)
        self.detectors = dict([((obj.cx, obj.cy), obj) for key, obj in self.objects.iteritems() if obj.is_detector])
        self.controllers = [obj for obj in self.objects.values() if obj.type == 'controller']
        #
        # Hook up the controllers
        for obj in [item for item in self.objects.values() if item.isControllable()]:
            controller = self.objects[obj.controlled_by]
            self.log.info('Hooking controller "%s" to "%s"' % (controller.name, obj.name))
            controller.addControlledObject(obj)
        #
        for mat in self.getObjectsOfType('pressure-mat'):
            mat.locks = self.objects[mat.locks_name]
            self.log.info('Hooking mat "%s" to "%s"' % (mat.name, mat.locks_name))
        #
        # Get the player
        self.players = self.getObjectsOfType('player')
        active = [player for player in self.players if player.active]
        if len(active) == 1:
            self.player = player
        else:
            raise ValueError('Wrong number of active players (%s)' % len(active))
        #
        # Set the world model for all AI's
        for ai in self.ais.values():
            ai.setWorldModel(self, self.players)
        #
        # Create pathfinder
        self.createPathfinder()

    def getObjectsOfType(self, type_name):
        """Return all objects of the given type name"""
        return [obj for obj in self.objects.values() if obj.type == type_name]

    def createImageFromLayer(self, name):
        """Create an image from a layer"""
        layer = self.tiled.getLayer(name)
        #
        tile_width, tile_height = G('tile-width'), G('tile-height')
        image = pygame.Surface(
            (tile_width * G('tiles-wide'), tile_height * G('tiles-high')),
            pygame.SRCALPHA,
            32
        )
        image.convert_alpha()
        #
        for x, y in layer.getLocationsWithTile():
            px, py = x * tile_width, y * tile_height
            sprite = layer.getSpriteFor((x, y))
            sprite.renderTo(0, image, (px, py))
        #
        if common.OPTIONS.cheat:
            pygame.image.save(image, os.path.join('sandbox', '%s.png' % name))
        #
        return image

    def nobodyAtLocation(self, point):
        """Return True if the selected point has no AI's on it"""
        for mob in self.ais.values():
            if (mob.cx, mob.cy) == point:
                return False
        else:
            return True

    def createObjectsFrom(self, layer_name):
        """Create some more objects from a certain layer"""
        layer = self.tiled.getObjectLayer(layer_name)
        objects = {}
        for obj in layer.getObjects():
            try:
                cls = self.object_types[obj.properties['type']]
            except KeyError:
                raise ValueError('Unknow grid object type:"%s" in "%s"' % (obj.properties['type'], obj.name))
            #
            new_obj = cls(obj)
            if new_obj.name in objects:
                raise ValueError('Object named "%s" in layer "%s" already exists' % (
                    new_obj.name, layer_name
                ))
            objects[new_obj.name] = new_obj
        #
        return objects

    def createPatrolPoints(self, layer_name):
        """Create the patrol points for the AIs"""
        layer = self.tiled.getObjectLayer(layer_name)
        for obj in layer.getObjects():
            new_obj = PatrolPoint(obj)
            self.ais[new_obj.name].addPatrolPoint(new_obj)

    def createRestPoints(self, layer_name):
        """Create the rest points for the AIs"""
        layer = self.tiled.getObjectLayer(layer_name)
        for obj in layer.getObjects():
            new_obj = RestPoint(obj)
            self.ais[new_obj.ai_owner].addRestPoint(new_obj)

    def createFromTiles(self, layer_name, cls):
        """Create some items from tiles"""
        points = {}
        layer = self.tiled.getLayer(layer_name)
        for x, y in layer.getLocationsWithTile():
            new_obj = cls(x, y)
            points[(x, y)] = new_obj
        #
        return points

    def isWalkable(self, cx, cy, mob):
        """Return True if the cell is walkable"""
        if (cx, cy) in self.not_walkable:
            return False
        try:
            obj = self.doors[(cx, cy)]
        except KeyError:
            return True
        else:
            return obj.canPass(mob)

    def isVisible(self, cx, cy):
        """Return True if we can see through a cell"""
        if (cx, cy) in self.not_walkable:
            #
            # If not walkable then you cannot see
            return False
        else:
            #
            # But it could be an open door
            try:
                door = self.doors[(cx, cy)]
            except KeyError:
                #
                # Nope, not a door
                return True
            else:
                #
                # OK, is a door. Is it open?
                return door.is_open

    def getObjectAt(self, cx, cy):
        """Return the object at a location"""
        try:
            return self.interactables[(cx, cy)]
        except KeyError:
            return None

    def createPathfinder(self):
        """Create a pathfinding graph"""
        self.log.info('Creating pathfinding graph')
        #
        self.graph = networkx.Graph()
        width, height = G('tiles-wide'), G('tiles-high')
        for cx in range(width):
            for cy in range(height):
                #
                # Is this cell walkable?
                if (cx, cy) not in self.not_walkable:
                    self.graph.add_node((cx, cy))
                    #
                    # Then look for all cells around it
                    for dx, dy in [(-1, 0), (+1, 0), (0, -1), (0, +1)]:
                        nx, ny = cx + dx, cy + dy
                        #
                        # Is the new cell walkable?
                        if (nx, ny) not in self.not_walkable:
                            #
                            # Then add a movement piece if this is really in the world
                            if 0 <= nx < width and 0 <= ny < height:
                                self.graph.add_node((nx, ny))
                                self.graph.add_edge((cx, cy), (nx, ny))

    def getPath(self, (sx, sy), (tx, ty)):
        """Get the path from one cell to another"""
        try:
            path = networkx.shortest_path(
                self.graph, (sx, sy), (tx, ty))
        except (networkx.NetworkXError, networkx.NetworkXNoPath), err:
            raise ValueError('There was no path from %s to %s' % ((sx, sy), (tx, ty)))
        else:
            return path

    def checkForDetections(self, mob):
        """Check if a mob is detected"""
        for item in self.detectors.values():
            if item.canDetect(mob, self):
                self.event_pump.processEvent((common.E_ALARM_DETECTED, item))
                item.flagDetection(mob)
                self.reportDetections(mob)

    def reportDetections(self, mob):
        """Report that we saw the mob"""
        for ai in self.ais.values():
            ai.mobDetected(mob)

    def hasLineOfSight(self, from_object, to_object):
        """Return True if a certain object can see another one"""
        #
        # Get the direction from the object to the other object
        start = Vec2d(from_object.cx, from_object.cy)
        end = Vec2d(to_object.cx, to_object.cy)
        offset = end - start
        if offset.length == 0:
            return True
        #
        # Make sure we can see that far
        if offset.length > from_object.getSightDistance(offset.angle_degrees):
            return False
        #
        delta = offset.normalized()
        number = int(math.ceil(offset.length))
        #
        cx, cy = from_object.cx, from_object.cy
        #
        # Now move along the length
        for idx in range(1, number):
            dx, dy = idx * delta
            tx, ty = int(round(cx + dx)), int(round(cy + dy))
            if not self.isVisible(tx, ty):
                return False
        else:
            return True

    def iterCellLocations(self):
        """Iterate through the cell locations"""
        for cell in self.tiled.getLayer('Background').iterCellLocations():
            yield cell

    def getSearchWithinDistance(self, mob):
        """Get the search locations within a certain distance of a mob"""
        cx, cy = mob.cx, mob.cy
        items = []
        max_distance = G('ai-search-distance')
        for search in self.search_points:
            distance_appart = self.getDistance(search, (cx, cy))
            if distance_appart <= max_distance:
                items.append((distance_appart, search))
        #
        items.sort()
        return [item[1] for item in items]

    def getUnallocatedSearch(self, mob, search_points):
        """Return the next unallocated search location

        Go through all locations but do not choose one where another
        AI is using it as a search location.

        """
        while search_points:
            point = search_points.pop(0)
            for other_mob in self.ais.values():
                if other_mob.ai.current_target == point:
                    self.log.debug('%s: rejected search point %s, as %s is going there' % (
                        mob.name, point, other_mob.name
                    ))
                    break
            else:
                self.log.debug('%s: selected unallocated search point %s' % (mob.name, point))
                return point
        #
        self.log.debug('%s: no valid search locations' % mob.name)
        return None

    def getDistance(self, p1, p2):
        """Return the distance between two points"""
        return math.sqrt((p1[0] - p2[0]) ** 2+ (p1[1] - p2[1]) ** 2)

    def getBrokenItemsWithin(self, mob, distance):
        """Return the broken objects within a distance"""
        items = []
        for item in self.breakables:
            if self.getDistance((mob.cx, mob.cy), (item.cx, item.cy)) <= distance:
                items.append(item)
        return items

    def getAIWithin(self, point, distance):
        """Return the controllable objects within a distance"""
        items = []
        for item in self.ais.values():
            if self.getDistance((point.cx, point.cy), (item.cx, item.cy)) <= distance:
                items.append(item)
        return items

    def findRestingAIs(self):
        """Find all the AI's who are resting"""
        resting = []
        for ai in self.ais.values():
            if ai.isResting():
                resting.append(ai)
        #
        return resting

    def getDoorAt(self, cx, cy):
        """Return a door if there is one at cx, cy"""
        try:
            door = self.doors[(cx, cy)]
        except KeyError:
            return None
        else:
            return door


class BaseObject(serge.common.Loggable):
    """The base object in the game"""

    interaction_name = None
    is_detector = False
    is_breakable = False

    def __init__(self, obj):
        """Initialise from tiled object"""
        self.addLogger()
        #
        if obj is not None:
            self.name = obj.name
            self.type = obj.properties['type']
            self.px = obj.x
            self.py = obj.y
            self.cx = self.px // G('tile-width')
            self.cy = self.py // G('tile-height')
            self.angle = obj.properties.get('angle', 0)
            self.draw_line = obj.properties.get('draw-line', True)
            self.visible = obj.properties.get('visible', True)
        #
        # Screen offsets
        self.ox, self.oy = G('tile-offset')
        self.looking_direction = 0.0

    def getVisualCoords(self, cx, cy):
        """Return the visual coords"""
        return (cx + 0.5) * G('tile-width') + self.ox, (cy + 0.5) * G('tile-height') + self.oy

    def getInteraction(self):
        """Return the possible interactions"""
        return self.interaction_name

    def interactWith(self):
        """Interact with the object"""
        self.log.info('Interacting with %s' % self.name)

    def isControllable(self):
        """Return whether we are controllable"""
        return False

    def canBeInteractedWith(self):
        """Return True if we can interact with this"""
        return False

    def canDetect(self, mob, grid):
        """Return True if we can detect the mob"""
        return False

    def flagDetection(self, mob):
        """Flag that we detected a mob"""

    def isWorkingNormally(self):
        """Return if we are working normally"""
        return True

    def getSightDistance(self, angle):
        """Return the sign distance for an angle"""
        return self.max_sight_distance


class ControllableObject(BaseObject):
    """An object that can control something"""

    is_breakable = True

    def __init__(self, obj):
        """Initialise the object"""
        super(ControllableObject, self).__init__(obj)
        self.controlled_by = obj.properties['controlled-by']
        self.always_working = obj.properties.get('always-working', False)
        self.controlled_by_object = None
        self.normal = True

    def addController(self, obj):
        """Add a controller to us"""
        self.controlled_by_object = obj

    def isControllable(self):
        """Return True if we are controllable"""
        return self.controlled_by != ''

    def canBeInteractedWith(self):
        """Return True if we can interact with this"""
        interaction = self.getInteraction()
        return interaction

    def toggleControl(self):
        """Toggle the control signal"""
        self.log.info('"%s" control toggled' % self.name)
        self.normal = not self.normal

    def isWorkingNormally(self):
        """Return True if it is working normally"""
        return self.normal or self.always_working


class Door(ControllableObject):
    """A door"""

    interaction_name = 'Open'
    is_open = False
    is_locked = False

    def canPass(self, mob):
        """Return True if the mob can pass"""
        self.log.debug('Door pass test on %s, type %s' % (mob.name, mob.type))
        if mob.type == 'player':
            return self.is_open
        else:
            return True

    def getInteraction(self):
        """Return possible interactions"""
        if self.is_locked:
            return None
        else:
            return 'Open' if not self.is_open else 'Close'

    def interactWith(self):
        """Do an interaction"""
        super(Door, self).interactWith()
        #
        if self.is_open:
            self.is_open = False
        else:
            self.is_open = True

    def addController(self, obj):
        """Add a controller to the door - makes it locked"""
        super(Door, self).addController(obj)
        self.is_locked = obj.is_on

    def toggleControl(self):
        """Toggle control of the door"""
        super(Door, self).toggleControl()
        self.is_locked = not self.is_locked
        if self.is_locked:
            self.is_open = False


class OnOffControlledObject(ControllableObject):
    """A controllable that can be on and off"""

    is_on = True

    def toggleControl(self):
        """Toggle the control signal"""
        super(OnOffControlledObject, self).toggleControl()
        self.is_on = not self.is_on


class PressurePad(BaseObject):
    """A pressure pad"""

    is_detector = True
    is_on = True

    def __init__(self, obj):
        """Initialise the pad"""
        super(PressurePad, self).__init__(obj)
        #
        self.locks_name = obj.properties['locks']
        self.locks = None

    def canDetect(self, mob, grid):
        """When the mob is on us we still return false but we lock the door"""
        if mob.cx == self.cx and mob.cy == self.cy:
            if not self.locks.is_on:
                self.log.info('Mat "%s" is locking "%s"' % (self.name, self.locks_name))
                self.is_on = False
                if self.locks:
                    self.locks.interactWith()
                else:
                    raise ValueError('Mat "%s" was pressure but no door connected' % self.name)
        #
        return False

    def flagDetection(self, mob):
        """Flag detection"""
        self.log.info('%s detected %s' % (self.name, mob.name))


class Camera(OnOffControlledObject):
    """A camera"""

    is_detector = True
    max_sight_distance = G('camera-max-sight-distance')

    def canDetect(self, mob, grid):
        """Return True if we can see the mob"""
        if self.is_on:
            return grid.hasLineOfSight(self, mob)
        else:
            return False

    def flagDetection(self, mob):
        """Flag detection"""
        self.log.info('%s detected %s' % (self.name, mob.name))


class PatrolPoint(BaseObject):
    """A patrol point"""

    def __init__(self, obj):
        """Initialise the Patrol Point"""
        super(PatrolPoint, self).__init__(obj)
        #
        self.index = obj.properties['index']
        self.next_point = None


class RestPoint(BaseObject):
    """A rest point"""

    def __init__(self, obj):
        """Initialise the Rest Point"""
        super(RestPoint, self).__init__(obj)
        #
        self.ai_owner = obj.properties['ai-owner']


class Controller(BaseObject):
    """A controller"""

    interaction_name = 'Deactivate'

    def __init__(self, obj):
        """Initialise the controller"""
        super(Controller, self).__init__(obj)
        #
        self.controls = []
        self.is_on = obj.properties.get('initial-state', True)

    def addControlledObject(self, obj):
        """Add an object that we control"""
        self.controls.append(obj)
        obj.addController(self)

    def canBeInteractedWith(self):
        """Return True if we can be interacted with"""
        return True

    def interactWith(self):
        """Interacting with the controller"""
        super(Controller, self).interactWith()
        #
        LevelGrid.event_pump.processEvent((common.E_SWITCH_THROW, self))
        #
        self.is_on = not self.is_on
        for controlled in self.controls:
            controlled.toggleControl()
        #
        self.interaction_name = 'Deactivate' if self.is_on else 'Activate'

    def isWorkingNormally(self):
        """Return if we are working normally"""
        return True


class DoomsdayDevice(BaseObject):
    """A doomsday device"""

    interaction_name = 'Pick up'
    picked_up = False
    is_detector = True

    def canBeInteractedWith(self):
        """Return True if we can be interacted with"""
        return True

    def interactWith(self):
        """Interacting with the controller"""
        super(DoomsdayDevice, self).interactWith()
        #
        self.picked_up = True

    def canDetect(self, mob, grid):
        """Check if we can detect the mob"""
        if mob.cx == self.cx and mob.cy == self.cy:
            self.picked_up = True


class DoomsdaySwitch(BaseObject):
    """A doomsday switch"""

    interaction_name = 'Turn off'
    turned_off = False

    def canBeInteractedWith(self):
        """Return True if we can be interacted with"""
        return not self.turned_off

    def interactWith(self):
        """Interacting with the controller"""
        super(DoomsdaySwitch, self).interactWith()
        #
        self.turned_off = True


class Exit(BaseObject):
    """An exit for the level"""

    interaction_name = 'Exit level'
    used = False
    is_detector = True
    is_on = True

    def canBeInteractedWith(self):
        """Return True if we can be interacted with"""
        return False

    def interactWith(self):
        """Interacting with the controller"""
        super(Exit, self).interactWith()
        #
        self.used = True

    def canDetect(self, mob, grid):
        """Check if we can detect the mob"""
        if mob.cx == self.cx and mob.cy == self.cy:
            self.used = True


class AI(BaseObject):
    """The AI's"""

    def __init__(self, obj):
        """Initialise the AI"""
        super(AI, self).__init__(obj)
        #
        self.patrol_points = []
        self.rest_point = None
        self.world_model = aicontroller.WorldModel()
        self.ahead_sight_distance = G('ai-ahead-sight-distance')
        self.side_sight_distance = G('ai-side-sight-distance')
        self.ahead_angle = G('ai-ahead-angle')
        self.initial_state = obj.properties['initial-state']
        self.initial_tiredness = obj.properties['initial-tiredness']
        #
        self.speech_hint = None
        self.looking_direction = 0

    def setWorldModel(self, grid, player):
        """Set up the world model"""
        self.ai = aicontroller.AIController(grid, self, player)
        self.ai.mode = self.initial_state
        self.ai.tiredness = self.initial_tiredness

    def addPatrolPoint(self, point):
        """Add a patrol point"""
        self.patrol_points.append(point)
        self.patrol_points.sort(cmp=lambda a, b: cmp(a.index, b.index))
        #
        # Mark the next points
        for idx in range(len(self.patrol_points) - 1):
            self.patrol_points[idx].next_point = self.patrol_points[idx + 1]
        self.patrol_points[-1].next_point = self.patrol_points[0]

    def switchPatrolsWith(self, other):
        """Switch patrols with another AI"""
        self.log.info('Switching patrols for %s and %s' % (self.name, other.name))
        my_patrol_points = self.patrol_points
        self.patrol_points = other.patrol_points
        other.patrol_points = my_patrol_points
        self.speech_hint = 'switching', 'rester'
        other.speech_hint = 'switching', 'replacer'
        other.ai.setMode(aicontroller.M_PATROLLING)
        #
        other.ai.tiredness = 0

    def addRestPoint(self, point):
        """Add a rest point"""
        if self.rest_point:
            raise ValueError('Rest point already exists for "%s", object "%s"' % (
                self.name,
                point.name
            ))
        else:
            self.rest_point = point

    def tickAI(self):
        """Tick the AI along"""
        if self.name not in G('disable-ais'):
            self.ai.tick(self.world_model)

    def canCapture(self, player):
        """Return true if we can capture the player"""
        dist = abs(self.cx - player.cx) + abs(self.cy - player.cy)
        return dist <= 1

    def capturePlayer(self, player):
        """Capture the player"""
        player.capture()

    def mobDetected(self, player):
        """The player has been detected"""
        self.ai.investigatePosition(player.cx, player.cy)

    def modeSwitch(self, old_mode, new_mode):
        """Switch the mode"""
        self.speech_hint = old_mode, new_mode

    def getSightDistance(self, angle):
        """Return the max sight distance"""
        distance = self.ahead_sight_distance if abs(angle - self.looking_direction) <= self.ahead_angle else self.side_sight_distance
        # self.log.debug('%s angle and distance = %s, %s. Delta = %s, Looking = %s' % (
        #     self.name, angle, distance, abs(angle - self.looking_direction), self.looking_direction))
        return distance

    def isResting(self):
        """Return True if we are resting and available for patrolling"""
        return self.ai.isResting()

    def canPatrol(self):
        """Return True if we can patrol"""
        return self.patrol_points

    def getAITickTime(self):
        """Return the time to tick the AI"""
        return self.ai.ai_timings.get(self.ai.mode, self.ai.ai_timings['none'])


class Point(BaseObject):
    """A point"""

    def __init__(self, x, y):
        """Initialise the search point"""
        super(Point, self).__init__(None)
        self.x = self.cx = x
        self.y = self.cy = y


class SearchPoint(Point):
    """A search point"""


class WalkablePoint(Point):
    """A walkable point"""


class Player(BaseObject):
    """Represents the player start position"""

    is_captured = False

    def __init__(self, obj):
        """Initialise the AI"""
        super(Player, self).__init__(obj)
        #
        self.active = obj.properties['active']
        self.has_exited = False

    def capture(self):
        """Capture the player"""
        self.is_captured = True


class Distraction(Point):
    """A distraction device"""

    type = 'distraction'