"""
Load a TMX map in JSON format as exported/saved by Tiled 0.9.

Needs testing / Here be dragons!
"""
import logging
import json
import ctypes

import pyglet
from pyglet import gl

from ext.obj import OBJ

class ObjectData(object):
    PROPERTIES = () # set in the derived class

    def __init__(self, data):
        """Set the object properties from JSON data"""
        for prop in self.PROPERTIES:
            try:
                setattr(self, prop, data[prop])
            except KeyError:
                logging.warning("property %s not found in data" % prop)

class BaseLayer(ObjectData):
    """
    Base class for map layers.

    Use TileLayer and ObjectGroup.
    """
    PROPERTIES = ("name", "opacity", "visible", "type",)

    # ordered group
    groups = 0

    def __init__(self, data, map):
        super(BaseLayer, self).__init__(data)

        self.map = map

        if self.visible:
            self.sprites = {}
            BaseLayer.groups += 1

class TileLayer(BaseLayer):
    """Map tile layer."""
    def __init__(self, data, map):
        super(TileLayer, self).__init__(data, map)

        self.data = data['data']
        self.local = {}

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index):
        return self.data[index]

class Object(ObjectData):
    """Object group layer object."""
    PROPERTIES = ("name", "visible", "type", "properties",
                  "x", "y", "width", "height", "gid", )

class ObjectGroup(BaseLayer):
    """Map object group layer."""
    def __init__(self, data, map):
        super(ObjectGroup, self).__init__(data, map)

        self.objects = []
        self._index = {}

        for obj in data['objects']:
            self.objects.append(Object(obj))
            if obj.get("name", None):
                # FIXME: objects with no name
                if not obj["name"] in self._index:
                    self._index[obj["name"]] = []
                self._index[obj["name"]].append(self.objects[-1])

    def __iter__(self):
        return iter(self.objects)

    def __getitem__(self, name):
        return self._index[name]

class Tileset(ObjectData):
    """Map tile set."""
    PROPERTIES = ("name", "firstgid", "tileproperties",
                  # "spacing", "margin", UNSUPPORTED!
                  )

class Map(ObjectData):
    PROPERTIES = ("version", "orientation", "width", "height",
                  "tilewidth", "tileheight", # "backgroundcolor",
                  "properties",
                  )

    # global storage for models, shared by all the maps
    models = {}

    def __init__(self, data, extra=None):
        super(Map, self).__init__(data)

        self.extra = extra

        self.lists = None

        self.tilesets = {} # the order is not important

        self.layers = []
        self.tilelayers = {}
        self.objectgroups = {}
        self.rotate = {}
        self.start_x = 0.5-self.width // 2
        self.start_y = -self.height // 2

        for tileset in data['tilesets']:
            self.tilesets[tileset["name"]] = Tileset(tileset)

        for layer in data['layers']:
            # TODO: test this!
            if layer['name'] in (self.tilelayers, self.objectgroups):
                raise ValueError("Duplicated layer name %s" % layer['name'])

            if layer['type'] == "tilelayer":
                self.layers.append(TileLayer(layer, self))
                self.tilelayers[layer['name']] = self.layers[-1]
            elif layer['type'] == "objectgroup":
                self.layers.append(ObjectGroup(layer, self))
                self.objectgroups[layer['name']] = self.layers[-1]
            else:
                logging.warning("unsupported layer type %s, skipping" % layer['type'])

        for _, tileset in self.tilesets.iteritems():
            for key, prop in tileset.tileproperties.iteritems():
                if "model" in prop:
                    mkey = int(key)+tileset.firstgid
                    if mkey not in Map.models:
                        Map.models[mkey] = OBJ.from_resource(prop["model"])
                if "rotate" in prop:
                    self.rotate[mkey] = json.loads(prop["rotate"])

        self.compile()

    @staticmethod
    def load_json(filename):
        """Load the map in JSON format"""
        with pyglet.resource.file(filename, "rt") as fd_json:
            data = json.load(fd_json)
        try:
            with pyglet.resource.file("ext_" + filename, "rt") as fd_json:
                extra = json.load(fd_json)
        except pyglet.resource.ResourceNotFoundException:
            extra = {}
        return Map(data, extra)

    def to_screen(self, x, y):
        return (self.start_x+x, self.start_y+self.height-y)

    def cell_coord(self, x, y):
        cx = int(x-self.start_x)
        cy = int(self.start_y+self.height-y)
        return (cx, cy)

    def screen_cell(self, name, x, y):
        cx, cy = self.cell_coord(x, y)
        return self.cell(name, cx, cy)

    def is_blocked(self, x, y):
        bg = self.screen_cell("Bg", x, y)
        fg = self.screen_cell("Fg", x, y)
        return (bg and bg.get("blocked", False)) or (fg and not fg.get("open", False))

    def update_cell(self, name, x, y, props):
        """update the cell properties"""
        self.tilelayers[name].local[(x, y)] = props

    def cell(self, name, x, y):
        """return the cell properties based on the tileset props + the local cell props"""
        try:
            tile = self.tilelayers[name][x+y*self.width]
        except IndexError:
            return None

        local = self.tilelayers[name].local.get((x,y), None)
        if local:
            return local

        for _, tileset in self.tilesets.iteritems():
            props = tileset.tileproperties.get(str(tile-tileset.firstgid))
            if props:
                props = dict(props)
                return props
        return None

    def cell_event(self, x, y):
        if self.extra is None:
            return None
        info = self.extra.get("info", {}).get("%d,%d" % (x, y), None)
        action = self.extra.get("action", {}).get("%d,%d" % (x, y), None)
        if info:
            return ("info", info)
        elif action:
            return ("action", action)
        else:
            return (None, None)

    def cell_exit(self, x, y):
        if self.extra is None:
            return None
        return self.extra.get("exit", {}).get("%d,%d" % (x, y), None)

    def compile(self, partial=None):
        if self.lists is None:
            n = gl.glGenLists(len(self.tilelayers))
            self.lists = range(n, n+len(self.tilelayers))

        if partial is None:
            layers = self.tilelayers.values()
            partial = 0
        else:
            layers = [self.tilelayers.values()[partial],]

        i = partial
        for layer in layers:
            gl.glNewList(self.lists[i], gl.GL_COMPILE)
            gl.glLoadIdentity()
            cells = iter(layer)
            for y in xrange(self.height):
                for x in xrange(self.width):
                    cell = cells.next()
                    try:
                        model = Map.models[cell]
                    except KeyError:
                        pass
                    else:
                        z = self.cell(layer.name, x, y).get("z", 0.0)
                        gl.glPushMatrix()
                        gl.glTranslatef(self.start_x+x,
                                        self.start_y+self.height-y,
                                        z,)
                        gl.glRotatef(90, 1, 0, 0)
                        if cell in self.rotate:
                            params = map(float, self.rotate[cell])
                            gl.glRotatef(*params)
                        model.draw()
                        gl.glPopMatrix()
            gl.glEndList()
            i += 1

    def draw(self):
        lists = ctypes.c_uint * len(self.lists)
        gl.glCallLists(len(self.lists), gl.GL_UNSIGNED_INT, lists(*self.lists))

