#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: map.py 359 2008-04-10 15:02:29Z aholkner $'

import pyglet
from pyglet.gl import *

import collide
import globals
import particles

_debug = False

class Tile(object):
    solid = True
    water = False
    breakable = False
    broken = False

    color = (255, 255, 255, 255)

    def __init__(self, name, image):
        self.name = name
        self.image = image

    def __repr__(self):
        return self.name

    def get_destroyed(self):
        tile = Tile('!' + self.name, None)
        tile.solid = False
        tile.breakable = False
        tile.broken = True
        tile.water = False
        tile.color = (0, 0, 0, 0)
        return tile
    
no_tile = Tile('no_tile', None)
no_tile.solid = False
no_tile.color = (0, 0, 0, 0)

def add_to_tileset(tileset, atlas, filename, location):
    image = pyglet.image.load(filename=filename,
                              file=location.open(filename))
    try:
        image = atlas.add(image)
        tile = Tile(filename, image)
        tileset[filename] = tile
        return tile
    except pyglet.image.atlas.AllocatorException:
        print 'Out of texture space for tileset'
        raise

def get_tileset_tile(tileset, name):
    try:
        return tileset[name]
    except KeyError:
        if name == 'no_tile':
            return no_tile
        if name.startswith('!'):
            tile = tileset[name] = tileset[name[1:]].get_destroyed()
            return tile
        else:
            raise

def load_tileset(name, atlas):
    tileset = {}
    for line in pyglet.resource.file(name, 'rt'):
        if not line.strip():
            continue
        if line[:1] in ' \t':
            key, value = line.strip().split(' ', 1)
            value = int(value)
            setattr(tile, key, value)
            if key == 'water':
                tile.color = (255, 255, 255, 150)
        else:
            filename = line.strip()
            try:
                location = pyglet.resource.location(filename)
                tile = add_to_tileset(tileset, atlas, filename, location)
            except Exception, e:
                print 'Error loading %s:' % filename, e
                image = None

    # Look for new tiles in tiles resource directory
    location = pyglet.resource.location(name)
    if isinstance(location, pyglet.resource.FileLocation):
        import os
        for filename in os.listdir(location.path):
            if filename not in tileset and filename.endswith('.png'):
                tile = add_to_tileset(tileset, atlas, filename, location)
                print >> pyglet.resource.file(name, 'a'), filename

    return tileset

class Cell(object):
    def __init__(self, map, col, row):
        self.map = map
        self.col = col
        self.row = row
        assert self.map.col1 <= col and self.map.row1 <= row
        assert col < self.map.col1 + self.map.cols
        assert row < self.map.row1 + self.map.rows

    def set_tile(self, tile):
        i = (self.row - self.map.row1) * self.map.cols + \
            (self.col - self.map.col1)
        if tile:
            self.map.data[(self.col, self.row)] = tile.name
        else:
            try:
                del self.map.data[(self.col, self.row)]
            except KeyError:
                pass
            tile = no_tile

        if tile.image:
            self.map.vertex_list.tex_coords[i * 12:(i + 1) * 12] = \
                tile.image.tex_coords
        self.map.vertex_list.colors[i * 16:(i + 1) * 16] = tile.color * 4

    def get_tile(self):
        try:
            name = self.map.data[(self.col, self.row)]
            return get_tileset_tile(self.map.tileset, name)
        except KeyError:
            return no_tile

    tile = property(get_tile, set_tile)

    def destroy(self):
        self.set_tile(self.get_tile().get_destroyed())
        x = self.col * self.map.cell_width
        y = self.row * self.map.cell_height
        globals.game.add_effect(particles.dirt_effect, x, y)
        # TODO sound
        if _debug:
            print 'destroy', self

        data = self.map.data
        ts = self.map.tileset

        for r in range(self.row - 1, self.row + 2):
            for c in range(self.col - 1, self.col + 2):
                bbox = self.map.mapset.get_bbox_for_cell_if_loaded(c, r)
                down = data.get((c, r-1))
                left = data.get((c-1, r))
                up = data.get((c, r+1))
                right = data.get((c+1, r))
                bbox.bottom = not (down and get_tileset_tile(ts, down).solid)
                bbox.left = not (left and get_tileset_tile(ts, left).solid)
                bbox.top = not (up and get_tileset_tile(ts, up).solid)
                bbox.right = not (right and get_tileset_tile(ts, right).solid)

    def __repr__(self):
        return 'Cell(%d, %d from %r)' % (self.col, self.row, self.map)

class Map(object):
    x = 0
    y = 0

    loaded = False
    loading = False
    unloading = False

    highlight_image = None
    highlight_image_x = 0
    highlight_image_y = 0

    def __init__(self, col1, row1, cols, rows, cell_width, cell_height, 
                 data, tileset, batch):
        self.highlight_cells = []
        self.col1 = col1
        self.row1 = row1
        self.cols = cols
        self.rows = rows
        self.cell_height = cell_height
        self.cell_width = cell_width

        self.data = data
        self.tileset = tileset
        self.batch = batch

        self.x = col1 * self.cell_width
        self.y = row1 * self.cell_height

    def __repr__(self):
        return 'Map(%d, %d)' % (self.col1, self.row1)

    def load(self):
        if self.unloading:
            globals.game.wait_for_tasks()
        if not self.loaded and not self.loading:
            self.loading = True
            globals.game.add_task(self.load_task())
            globals.game.add_task(self.update_cell_boundaries_task())

    def load_task(self):
        c1 = self.col1
        r1 = self.row1

        self.bboxes = [[] for i in range(self.rows)]
        vertex_data = []
        texture_data = []
        color_data = []
        y1 = self.y
        for row in range(self.rows):
            y2 = y1 + self.cell_height
            x1 = self.x
            for col in range(self.cols):
                x2 = x1 + self.cell_width
                self.bboxes[row].append(collide.BBox(x1, y1, x2, y2))
                vertex_data.extend([x1, y1, x2, y1, x2, y2, x1, y2])
                try:
                    name = self.data[(col+c1, row+r1)]
                    tile = get_tileset_tile(self.tileset, name)
                    if tile.image:
                        texture_data.extend(tile.image.tex_coords)
                    else:
                        texture_data.extend((0, 0, 0) * 4)
                    color_data.extend(tile.color * 4)
                except KeyError:
                    texture_data.extend((0, 0, 0) * 4)
                    color_data.extend((0, 0, 0, 0) * 4)
                x1 = x2
            y1 = y2
        
        vl = self.batch.add(self.cols * self.rows * 4, GL_QUADS, None,
            ('v2i', vertex_data),
            ('t3f', texture_data),
            ('c4B', color_data))
        self.vertex_list = vl

        yield

        self.loaded = True
        self.loading = False

    def unload(self):
        if (self.loaded or self.loading) and not self.unloading:
            self.unloading = True
            globals.game.add_task(self.unload_task())

    def unload_task(self):
        assert self.loaded
        self.vertex_list.delete()
        self.vertex_list = None
        self.clear_highlight()
        self.loaded = False
        self.unloading = False
        yield

    def get_bbox(self):
        return collide.BBox(self.x, self.y, 
                            self.x + self.cols * self.cell_width,
                            self.y + self.rows * self.cell_height)

    def get_cell(self, col, row):
        return Cell(self, col, row)

    # PERF: don't need to do this per-map
    def get_cell_at(self, x, y):
        col = x // self.cell_width
        row = y // self.cell_height
        if self.col1 <= col < self.col1 + self.cols and \
           self.row1 <= row < self.row1 + self.rows:
            return Cell(self, col, row)

    # PERF: don't need to do this per-map
    def get_intersecting_cells(self, bbox):
        col1 = int((bbox.x1 - 1) // self.cell_width)
        row1 = int((bbox.y1 - 1) // self.cell_height)
        col2 = int(bbox.x2 // self.cell_width)
        row2 = int(bbox.y2 // self.cell_height)
        for row in range(max(row1, self.row1), 
                         min(row2+1, self.row1+self.rows)):
            for col in range(max(col1, self.col1), 
                             min(col2+1, self.col1 + self.cols)):
                yield Cell(self, col, row)

    def get_cell_bbox(self, cell):
        return self.bboxes[cell.row - self.row1][cell.col - self.col1]

    def update_cell_boundaries(self):
        globals.game.add_task(self.update_cell_boundaries_task())
        
    def update_cell_boundaries_task(self):
        if not self.loaded:
            return
        cw = self.cell_width
        ch = self.cell_height
        ts=  self.tileset
        for r, row in enumerate(self.bboxes):
            r += self.row1
            for c, bbox in enumerate(row):
                c += self.col1

                # Remove interior boundaries   
                down = self.data.get((c, r-1))
                left = self.data.get((c-1, r))
                up = self.data.get((c, r+1))
                right = self.data.get((c+1, r))
                bbox.bottom = not (down and get_tileset_tile(ts, down).solid)
                bbox.left = not (left and get_tileset_tile(ts, left).solid)
                bbox.top = not (up and get_tileset_tile(ts, up).solid)
                bbox.right = not (right and get_tileset_tile(ts, right).solid)
        yield


    def highlight_cell(self, cell):
        if cell:
            self.highlight_cells.append(cell)

    def highlight_cell_at(self, x, y):
        self.highlight_cell(self.get_cell_at(x, y))
        
    def highlight_image_at(self, image, x, y):
        self.highlight_image = image
        self.highlight_image_x = x
        self.highlight_image_y = y

    def clear_highlight(self):
        self.highlight_cells = []
        self.highlight_image = None

class MapSet(object):
    CELL_WIDTH = 64
    CELL_HEIGHT = 32
    MAP_COLS = 16
    MAP_ROWS = 16

    def __init__(self, name, tileset, texture):
        self.name = name
        self.tileset = tileset
        self.texture = texture
        self.maps = {}
        self.data = {}
        self.visible_maps = set()
        self.batch = pyglet.graphics.Batch()

    def get_map_for_cell(self, col, row):
        map_col = col // self.MAP_COLS
        map_row = row // self.MAP_ROWS
        try:
            return self.maps[(map_col, map_row)]
        except KeyError:
            map = self.maps[(map_col, map_row)] = \
                Map(map_col * self.MAP_COLS, map_row * self.MAP_ROWS,
                    self.MAP_COLS, self.MAP_ROWS, 
                    self.CELL_WIDTH, self.CELL_HEIGHT, 
                    self.data, self.tileset, self.batch)
            map.mapset = self
            return map

    def get_bbox_for_cell_if_loaded(self, col, row):
        map_col = col // self.MAP_COLS
        map_row = row // self.MAP_ROWS
        try:
            map = self.maps[(map_col, map_row)]
        except KeyError:
            return

        return map.bboxes[row - map.row1][col - map.col1]

    def get_maps_for_bbox(self, bbox):
        col1 = int(bbox.x1 // self.CELL_WIDTH // self.MAP_COLS)
        row1 = int(bbox.y1 // self.CELL_HEIGHT // self.MAP_ROWS)
        col2 = int((bbox.x2 // self.CELL_WIDTH) // self.MAP_COLS)
        row2 = int((bbox.y2 // self.CELL_HEIGHT) // self.MAP_ROWS)
        for row in range(row1, row2+1):
            for col in range(col1, col2+1):
                try:
                    yield self.maps[(col, row)]
                except KeyError:
                    pass

    def get_map_at(self, x, y):
        col = int(x // self.CELL_WIDTH)
        row = int(y // self.CELL_HEIGHT)
        return self.get_map_for_cell(col, row)

    @classmethod
    def load(cls, name, tileset_name, texture_width, texture_height):
        atlas = pyglet.image.atlas.TextureAtlas(texture_width, texture_height)
        tileset = load_tileset(tileset_name, atlas)
        mapset = cls(name, tileset, atlas.texture)
        map = None
        for line in pyglet.resource.file(name, 'rt'):
            line = line.strip()
            if not line:
                continue
            key, value = line.split(' ', 1)
            if key == 'cell':
                col, row, tile_name = value.split(' ', 2)
                col = int(col)
                row = int(row)
                mapset.data[(col, row)] = tile_name
                mapset.get_map_for_cell(col, row)
        return mapset

    def save(self):
        location = pyglet.resource.location(self.name)
        file = location.open(self.name, 'wt')
        for (col, row), name in self.data.items():
            if name.startswith('!'):
                name = name[1:]
            print >> file, 'cell %d %d %s' % (
                col, row, name)

    def draw(self):
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor3f(1, 1, 1)
        self.batch.draw()
        glDisable(self.texture.target)

        if _debug or globals.game.editing:
            for map in self.visible_maps:
                for cell in map.highlight_cells:
                    map.get_cell_bbox(cell).draw()

    def update_visibility_bbox(self, bbox):
        visible_maps = set(self.get_maps_for_bbox(bbox))
        for map in self.visible_maps - visible_maps:
            if globals.game.camera.follow:
                # Don't unload maps when follow is off, or editor breaks
                if _debug:
                    print 'Unload', map
                map.unload()
        for map in visible_maps - self.visible_maps:
            if _debug:
                print 'Load', map
            map.load()
        self.visible_maps = visible_maps

    def get_cell_at(self, x, y):
        map = self.get_map_at(x, y)
        map.load()
        globals.game.wait_for_tasks()
        return map.get_cell_at(x, y)

    def highlight_cell_at(self, x, y):
        map = self.get_map_at(x, y)
        map.load()
        globals.game.wait_for_tasks()
        map.highlight_cell(map.get_cell_at(x, y))

    def clear_highlight(self):
        for map in self.visible_maps:
            map.clear_highlight()

    def __iter__(self):
        for map in self.maps.values():
            yield map

    def save_state(self, d):
        assert self.name not in d
        v = d[self.name] = []
        for (col, row), name in self.data.items():
            tile = get_tileset_tile(self.tileset, name)
            if tile.breakable or tile.broken:
                v.append((col, row, name))

    def restore_state(self, d):
        v = d[self.name]
        for col, row, name in v:
            self.data[(col, row)] = name
        for map in self.visible_maps:
            map.unload()
        globals.game.wait_for_tasks()
        self.visible_maps = set()

class DarknessMapSet(MapSet):
    def draw(self):
        glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT | GL_COLOR_BUFFER_BIT)
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        glEnable(GL_BLEND)
        glBlendFuncSeparate(GL_ZERO, GL_ONE, GL_ZERO, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1, 1, 1, 1)
        self.batch.draw()
        glDisable(self.texture.target)
        glPopAttrib()
