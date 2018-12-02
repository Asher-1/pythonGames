import os
import logging
import json

import pyglet
from pyglet.graphics import OrderedGroup
from pyglet.sprite import Sprite
from pyglet import gl

from .utils import get_texture_sequence

log = logging

__all__ = ['Map',]

class BaseLayer(object):

    # ordered group
    groups = 0

    def __init__(self, data, map):

        self.data = data
        self.map = map

        if self.data["visible"]:
            self.sprites = {}
            self.group = OrderedGroup(BaseLayer.groups)
            BaseLayer.groups += 1

class TileLayer(BaseLayer):

    def __iter__(self):
        return iter(self.data)

    def __contains(self, index):
        if type(index) != tuple:
            raise TypeError("tuple expected")

        x, y = index
        return int(x+y*self.map.data["width"]) in self.data["data"]

    def __getitem__(self, index):
        if type(index) != tuple:
            raise TypeError("tuple expected")

        x, y = index
        return self.data["data"][int(x+y*self.map.data["width"])]

    def set_viewport(self, x, y, w, h):
        tw = self.map.data["tilewidth"]
        th = self.map.data["tileheight"]

        def yrange(f, t, s):
            while f < t:
                yield f
                f += s

        in_use = []
        for j in yrange(y, y+h+th, th):
            py = j//th
            for i in yrange(x, x+w+tw, tw):
                px = i//tw
                in_use.append((px, py))
                if (px, py) not in self.sprites:
                    try:
                        texture = self.map.get_texture(self[px, py])
                    except (KeyError, IndexError):
                        self.sprites[(px, py)] = None
                    else:
                        self.sprites[(px, py)] = Sprite(texture,
                                                        x=(px*tw),
                                                        y=h-(py*th)-th,
                                                        batch=self.map.batch,
                                                        group=self.group,
                                                        usage="static",
                                                        )
        for key in self.sprites.keys():
            if key not in in_use:
                if self.sprites[key] is not None:
                    self.sprites[key].delete()
                del self.sprites[key]

class ObjectGroup(BaseLayer):

    def __init__(self, data, map):
        super(ObjectGroup, self).__init__(data, map)

        self.h = 0
        self.objects = []
        self._index = {}
        self._index_type = {}
        self._xy_index = {}

        for obj in data["objects"]:
            self.objects.append(obj)

            name = obj.get("name", "?")
            if name not in self._index:
                self._index[name] = []

            otype = obj.get("type", "?")
            if otype not in self._index_type:
                self._index_type[otype] = []

            x = int(obj["x"])//self.map.data["tilewidth"]
            y = int(obj["y"])//self.map.data["tileheight"]-1
            if (x, y) not in self._xy_index:
                self._xy_index[x, y] = []

            self._index[name].append(self.objects[-1])
            self._index_type[otype].append(self.objects[-1])
            self._xy_index[x, y].append(self.objects[-1])

        # is this useful AT ALL?
        self.objects.sort(key=lambda obj: obj["x"]+obj["y"]*self.map.data["width"])

    def __iter__(self):
        return iter(self.objects)

    def __contains__(self, name):
        if isinstance(name, tuple):
            x, y = name
            return (int(x), int(y)) in self._xy_index
        return nsame in self._index

    def __getitem__(self, name):
        if isinstance(name, tuple):
            x, y = name
            # XXX: if there are several objects, expect the first one
            return self._xy_index[int(x), int(y)][0]
        return self._index[name]

    def get_by_type(self, otype):
        return self._index_type[otype]

    def set_sprite(self, obj):
        gid = obj.get("gid", 0)

        try:
            texture = self.map.get_texture(gid)
            tileoffset = self.map.get_tileoffset(gid)
        except (IndexError, KeyError):
            sprite = None
        else:
            sprite = Sprite(texture,
                            x=obj["x"]+tileoffset[0],
                            y=self.h-obj["y"]+tileoffset[1],
                            batch=self.map.batch,
                            group=self.group,
                            usage="static",
                            )

        self.sprites[(obj["x"], obj["y"])] = sprite

    def set_viewport(self, x, y, w, h):
        self.h = h
        tw = self.map.data["tilewidth"]
        th = self.map.data["tileheight"]

        in_use = []
        for obj in self.objects:
            if x-tw < obj["x"] < x+w+tw and y-th < obj["y"] < y+h+th:
                if not obj["visible"]:
                    continue
                if "gid" in obj:
                    in_use.append((obj["x"], obj["y"]))
                    self.set_sprite(obj)

        for key in self.sprites.keys():
            if key not in in_use:
                self.sprites[key].delete()
                del self.sprites[key]

class Tileset(object):

    def __init__(self, data):
        self.data = data

        # used to convert coordinates of the grid
        self.columns = (self.data["imagewidth"]-self.data["spacing"]*2)//(self.data["tilewidth"]-self.data["margin"])
        self.rows = (self.data["imageheight"]-self.data["spacing"]*2)//(self.data["tileheight"]-self.data["margin"])

        # the image will be accessed using pyglet resources
        self.image = os.path.basename(self.data["image"])
        self.texture = get_texture_sequence(self.image, self.data["tilewidth"], self.data["tileheight"], self.data["margin"], self.data["spacing"])

    def __getitem__(self, index):
        return self.texture[index]

    def __len__(self):
        return len(self.texture)

class Map(object):

    def __init__(self, data):
        self.data = data

        self.tilesets = {} # the order is not important

        self.layers = []
        self.tilelayers = {}
        self.objectgroups = {}

        for tileset in data["tilesets"]:
            self.tilesets[tileset["name"]] = Tileset(tileset)

        for layer in data["layers"]:
            # TODO: test this!
            if layer['name'] in (self.tilelayers, self.objectgroups):
                raise ValueError("Duplicated layer name %s" % layer["name"])

            if layer["type"] == "tilelayer":
                self.layers.append(TileLayer(layer, self))
                self.tilelayers[layer["name"]] = self.layers[-1]
            elif layer["type"] == "objectgroup":
                self.layers.append(ObjectGroup(layer, self))
                self.objectgroups[layer["name"]] = self.layers[-1]
            else:
                log.warning("unsupported layer type %s, skipping" % layer["type"])

        self.batch = pyglet.graphics.Batch()

        # viewport
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

        # focus
        self.fx = None
        self.fy = None

        # useful (size in pixels)
        self.p_width = self.data["width"]*self.data["tilewidth"]
        self.p_height = self.data["height"]*self.data["tileheight"]

        # build a texture index converting pyglet indexing of the texture grid
        # to tiled coordinate system
        self.tileoffset_index = {}
        self.texture_index = {}
        for tileset in self.tilesets.values():
            for y in range(tileset.rows):
                for x in range(tileset.columns):
                    self.texture_index[x+y*tileset.columns+tileset.data["firstgid"]] = \
                            tileset[(tileset.rows-1-y),x]

                    # TODO: test this!
                    if "tileoffset" in tileset.data:
                        self.tileoffset_index[x+y*tileset.columns+tileset.data["firstgid"]] = \
                                (tileset.data["tileoffset"]["x"], tileset.data["tileoffset"]["y"])

    def invalidate(self):
        self.set_viewport(self.x, self.y, self.w, self.h, True)

    def set_viewport(self, x, y, w, h, force=False):
        # x and y can be floats
        vx = max(x, 0)
        vy = max(y, 0)
        vx = min(vx, (self.p_width)-w)
        vy = min(vy, (self.p_height)-h)
        vw = int(w)
        vh = int(h)

        if not any([force, vx!=self.x, vy!=self.y, vw!=self.w, vh!=self.h]):
            return

        self.x = vx
        self.y = vy
        self.w = vw
        self.h = vh

        for layer in self.layers:
            if layer.data["visible"]:
                layer.set_viewport(self.x, self.y, self.w, self.h)

    def set_focus(self, x, y):
        x = int(x)
        y = int(y)
        if self.fx == x and self.fy == y:
            return

        self.fx = x
        self.fy = y

        vx = max(x-(self.w//2), 0)
        vy = max(y-(self.h//2), 0)

        if vx+(self.w//2) > self.p_width:
            vx = self.p_width-self.w

        if vy+(self.h//2) > self.p_height:
            vy = self.p_height-self.h

        self.set_viewport(vx, vy, self.w, self.h)

    def viewport_to_screen(self, x, y):
        return x-self.x, self.h-(y-self.y)

    def get_texture(self, gid):
        # if not found will raise a KeyError or IndexError
        return self.texture_index[gid]

    def get_tileoffset(self, gid):
        return self.tileoffset_index.get(gid, (0, 0))

    @property
    def last_group(self):
        return BaseLayer.groups-1

    def is_free(self, x, y):
        free_gid = int(self.data["properties"].get("free_gid", 0))
        mx = x//self.data["tilewidth"]
        my = y//self.data["tileheight"]
        for layer in self.tilelayers.values():
            try:
                if layer[mx, my] != free_gid:
                    return False
            except KeyError:
                return False
        for layer in self.objectgroups.values():
            if (mx, my) not in layer:
                return True
            obj = layer[mx, my]
            return not (obj["visible"] and "properties" in obj and obj["properties"].get("solid", "0") == "1")
        return True

    def on_screen_type(self, otype):
        found = []
        for layer in self.objectgroups.values():
            for obj in layer.get_by_type(otype):
                if not obj["visible"]:
                    continue
                x, y = self.viewport_to_screen(int(obj["x"]), int(obj["y"]))
                if -self.data["tilewidth"] < x < self.w and -self.data["tileheight"] < y < self.h:
                    found.append(obj)
        return found

    @staticmethod
    def load_json(fileobj):
        """Load the map in JSON format (it will close the file!)"""
        data = json.load(fileobj)
        fileobj.close()
        return Map(data)

    def draw(self):
        gl.glPushMatrix()
        gl.glTranslatef(-self.x, self.y, 0)
        self.batch.draw()
        gl.glPopMatrix()

