import collections
import pickle
import pyglet

from gamelib import app
from gamelib import vector
from gamelib import scriptfuncs
from gamelib.constants import *

scriptindex = scriptfuncs.locscript.index

class Map(object):

    def __init__(self):
        self.locations = {}
        self.scripts = {}
        self.mapscript = None
        self.paths = {}
        self.graph = {}
        self._reverse = {}
        self._globals = {}
        self.name = ''

    @classmethod
    def load(cls, name):
        self = Map()
        self.name = name
        self.realname = MAP_REPLACEMENTS.get(name, name)
        scriptindex.clear()
        # Load script.
        exec 'from gamelib.scriptfuncs import *' in self._globals
        exec pyglet.resource.file('maps/%s.py' % name, 'r') in self._globals
        # Load map data.
        data = pickle.load(pyglet.resource.file('maps/%s.dat' % self.realname))
        locations, paths, names = data
        # Add locations.
        for lpos in locations:
            lpos = vector.Vector(lpos)
            name = names[lpos]
            self._reverse[lpos] = name
            self.locations[name] = lpos
            self.scripts[name] = scriptindex.get(name)
            self.mapscript = scriptindex.get('__init__')
            self.graph[name] = set()
        # Add paths.
        for path in paths:
            path = map(vector.Vector, path)
            start = self._reverse[path[0]]
            end = self._reverse[path[-1]]
            path = self.bezier(path)
            self.paths[start, end] = list(path)
            self.paths[end, start] = list(reversed(path))
            if not app.game().link_closed(self.name, start, end):
                self.graph[start].add(end)
                self.graph[end].add(start)
        return self

    def bezier(self, path):
        return path
        res = [path[0]]
        for a, b in zip(path, path[1:]):
            center = (a + b) / 2
            normal = (b - a).normalised().perpendicular()
            c = center + normal * BEZIER_CURVINESS
            r1, r2, r3, r4 = [a, 3*c - 3*a, 3*a - 3*c, b - a]
            steps = int((b - a).length / BEZIER_STEP_LENGTH)
            for idx in xrange(steps):
                t = float(idx+1) / steps
                res.append(r1 + t * (r2 + t * (r3 + t * r4)))
        return res

    def distance(self, start, end):
        total = 0.0
        path = self.paths[start, end]
        for p1, p2 in zip(path, path[1:]):
            total += (p2 - p1).length
        return total

    def find_pos(self, start, end, progress):
        if (start, end) not in self.paths:
            return self.locations[start]
        path = self.paths[start, end]
        total = 0.0
        for p1, p2 in zip(path, path[1:]):
            total += (p2 - p1).length
        total *= progress
        for p1, p2 in zip(path, path[1:]):
            dist = (p2 - p1).length
            if dist > total:
                t = total / dist
                return p1 * (1-t) + p2 * t
            total -= dist
        return path[-1]

    def nearest_node(self, pos):
        key = lambda n: (self.locations[n] - pos).length
        return min(self.locations, key=key)
