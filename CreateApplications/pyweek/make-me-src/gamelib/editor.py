#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import math
import pyglet
from pyglet.window import key
from pyglet.window import mouse
from pyglet.gl import *

import globals
import map
import placeable

class Editor(object):
    def __init__(self):
        self.tool = None

        self.tile_window = TileWindow(globals.game.maps, self) 
        self.water_tile_window = TileWindow(
            globals.game.foreground_maps, self) 
        self.darkness_tile_window = TileWindow(
            globals.game.darkness_maps, self) 
        self.background_window = PlaceableWindow(self, 
                                                globals.game.background_layer,
                                                'Backgrounds')
        self.placeable_window = PlaceableWindow(self, 
                                                globals.game.pickups_layer,
                                                'Pickups') 
        self.menu_window = PlaceableWindow(self, globals.game.menu_layer,
                                                'Menus') 
        self.fixed_lights_window = PlaceableWindow(self, 
                                               globals.game.fixed_lights_layer,
                                               'Fixed lights') 
        globals.game.active_camera.locked = True
        globals.game.editing = True
        undo = None
        print 'In editor'

    def on_key_press(self, symbol, modifiers):
        if symbol == key.S and modifiers & key.MOD_ACCEL and \
                modifiers & key.MOD_SHIFT:
            self.commit()
            globals.game.maps.save()
            globals.game.fixed_lights_layer.save()
            for layer in globals.game.layers:
                if layer is not globals.game.effects_layer:
                    layer.save()
            print 'Saved all maps and placeables'
        elif symbol == key.S and modifiers & key.MOD_ACCEL:
            self.commit()
            globals.game.maps.save()
            globals.game.foreground_maps.save()
            globals.game.darkness_maps.save()
            globals.game.fixed_lights_layer.save()
            print 'Saved tile map only'
        elif symbol == key.ESCAPE:
            self.select_tool(None)
        elif symbol == key.E and modifiers & key.MOD_ACCEL:
            self.commit()
            self.tile_window.close()
            self.water_tile_window.close()
            self.darkness_tile_window.close()
            self.fixed_lights_window.close()
            self.placeable_window.close()
            self.background_window.close()
            self.menu_window.close()
            self.select_tool(None)
            globals.window.remove_handlers(self)
            globals.game.active_camera.locked = False
            globals.game.editing = False
            print 'Leaving editor'
        elif symbol == key.Z and modifiers & key.MOD_ACCEL:
            if self.undo:
                self.undo()
        elif symbol == key.C:
            print globals.game.active_camera.x,
            print globals.game.active_camera.y
        elif symbol == key.D and modifiers & key.MOD_ACCEL:
            globals.game.lamp_layer.enabled = \
                not globals.game.lamp_layer.enabled
        return pyglet.event.EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if (buttons & mouse.LEFT and modifiers & key.MOD_CTRL) or \
           buttons & mouse.MIDDLE:
            globals.game.active_camera.x -= dx
            globals.game.active_camera.y -= dy
            globals.game.active_camera.update_visibility()
            return pyglet.event.EVENT_HANDLED

    def select_tool(self, tool):
        self.undo = None
        if self.tool:
            globals.window.remove_handlers(self.tool)
        self.tool = tool
        self.clear_highlight()
        if tool:
            globals.window.push_handlers(self.tool)

    def commit(self):
        for map in globals.game.maps:
            map.update_cell_boundaries()
            globals.game.wait_for_tasks()

    # "Editor" interface for tools

    def translate_coords(self, x, y):
        return globals.game.active_camera.window_to_world(x, y)

    def get_map_at(self, x, y, modify=True):
        map = globals.game.maps.get_map_at(x, y)
        map.load()
        globals.game.wait_for_tasks()
        if modify:
            map.edited = True
        return map

    def get_cell_at(self, x, y, modify=True):
        map = self.get_map_at(x, y, modify=modify)
        map.load()
        globals.game.wait_for_tasks()
        return map.get_cell_at(x, y)

    def highlight_cell_at(self, x, y):
        map = self.get_map_at(x, y, modify=False)
        map.load()
        globals.game.wait_for_tasks()
        map.highlight_cell_at(x, y)

    '''
    def highlight_image_at(self, image, x, y):
        map = self.get_map_at(x, y, modify=False)
        map.highlight_image_at(image, x, y)
    '''
        
    def clear_highlight(self):
        for layer in globals.game.layers:
            layer.clear_highlight()

class CellTool(object):
    image = None

    def __init__(self, editor, mapset):
        self.editor = editor
        self.mapset = mapset

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = self.editor.translate_coords(x, y)
        self.mapset.clear_highlight()
        self.mapset.highlight_cell_at(x, y)
        cell = self.mapset.get_cell_at(x, y)
        #if self.image and cell:
        #    self.editor.highlight_image_at(self.image, cell.x, cell.y)
        if cell:
            if cell.tile and cell.tile is not map.no_tile:
                self.editor.tile_window.label.text = cell.tile.name
            else:
                self.editor.tile_window.label.text = ''

    def on_mouse_press(self, x, y, button, modifiers):
        if button not in (mouse.LEFT, mouse.RIGHT):
            return
        x, y = self.editor.translate_coords(x, y)
        if not modifiers & (key.MOD_CTRL | key.MOD_SHIFT | key.MOD_ALT):
            self.mapset.highlight_cell_at(x, y)
            cell = self.mapset.get_cell_at(x, y)
            if cell:
                if button == mouse.LEFT:
                    self.apply(cell)
                elif button == mouse.RIGHT:
                    self.apply_alt(cell)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mapset.clear_highlight()
        self.on_mouse_press(x, y, buttons, modifiers)

    def on_mouse_leave(self, x, y):
        self.mapset.clear_highlight()

    def apply(self, cell):
        print '%r.apply(%r)' % (self, cell)

    def apply_alt(self, cell):
        pass

class QueryCellTool(CellTool):
    def apply(self, cell):
        print cell

class ClearCellTool(CellTool):
    def apply(self, cell):
        cell.tile = None

class SetCellTileTool(CellTool):
    def __init__(self, editor, mapset, tile):
        super(SetCellTileTool, self).__init__(editor, mapset)
        self.tile = tile
        self.image = tile.image

    def apply(self, cell):
        last_tile = cell.tile
        self.editor.undo = lambda: setattr(cell, 'tile', last_tile)
        cell.tile = self.tile

    def apply_alt(self, cell):
        cell.tile = None


class TileWindow(pyglet.window.Window):
    def __init__(self, mapset, editor):
        self.mapset = mapset
        self.editor = editor

        tiles = mapset.tileset.values()
        tiles.sort(key=lambda a:a.name)
        n = len(tiles)
        rows = int(math.sqrt(n))
        cols = n // rows + 1
        cell_width = max([t.image.width for t in tiles])
        cell_height = max([t.image.height for t in tiles])

        data = {}
        tile_iter = iter(tiles)
        try:
            for row in range(rows):
                for col in range(cols):
                    data[(col, row)] = tile_iter.next().name
        except StopIteration:
            pass

        self.batch = pyglet.graphics.Batch()
        self.map = map.Map(0, 0, cols, rows, cell_width, cell_height, data,
            mapset.tileset, self.batch)
        self.map.load()

        self.label = pyglet.text.Label('', x=4, y=4)
        
        super(TileWindow, self).__init__(
            width=cell_width*cols, height=cell_height*rows,
            style='tool',
            caption='Tiles')

    def on_mouse_motion(self, x, y, dx, dy):
        self.map.clear_highlight()
        self.map.highlight_cell_at(x, y)
        cell = self.map.get_cell_at(x, y)
        if cell:
            if cell.tile and cell.tile is not map.no_tile:
                self.label.text = cell.tile.name
            else:
                self.label.text = ''

    def on_mouse_press(self, x, y, button, modifiers):
        cell = self.map.get_cell_at(x, y)
        if cell:
            tool = SetCellTileTool(self.editor, self.mapset, cell.tile)
            self.editor.select_tool(tool)

    def on_mouse_leave(self, x, y):
        self.map.clear_highlight()
        self.label.text = ''

    def on_draw(self):
        glLoadIdentity()
        self.clear()
        glEnable(self.mapset.texture.target)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBindTexture(self.mapset.texture.target, self.mapset.texture.id)
        glColor3f(1, 1, 1)
        self.batch.draw()
        glDisable(self.mapset.texture.target)
        for cell in self.map.highlight_cells:
            self.map.get_cell_bbox(cell).draw()
        self.label.draw()

    # "Editor" interface for tools

    def translate_coords(self, x, y):
        return x, y

    def get_map_at(self, x, y, modify):
        return self.map

    def get_cell_at(self, x, y, modify):
        return self.map.get_cell_at(x, y)

    def highlight_cell_at(self, x, y):
        return self.map.highlight_cell_at(x, y)

    def highlight_image_at(self, x, y, image):
        pass
        
    def clear_highlight(self):
        self.map.clear_highlight()

class PlaceableTool(object):
    def __init__(self, editor, layer, placeable):
        self.editor = editor
        self.layer = layer
        self.placeable = placeable
        self.image = placeable.get_image()

    def translate(self, x, y):
        x, y = self.editor.translate_coords(x, y)
        return x, y

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = self.translate(x, y)
        x -= self.image.width // 2
        y -= self.image.height // 2
        self.layer.clear_highlight()
        self.layer.highlight_image_at(self.image, x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if not modifiers & (key.MOD_CTRL | key.MOD_SHIFT | key.MOD_ALT):
            x, y = self.translate(x, y)
            if button == mouse.LEFT:
                x -= self.image.width // 2
                y -= self.image.height // 2
                self.layer.add_placeable_at(self.placeable, x, y)
            elif button == mouse.RIGHT:
                self.layer.remove_placeable_at(self.placeable, x, y)
        
    def on_mouse_leave(self, x, y):
        self.layer.clear_highlight()
 
class PlaceableWindow(pyglet.window.Window):
    def __init__(self, editor, layer, caption='Placeables'):
        location = pyglet.resource.location(layer.name)
        self.placeables = []

        if isinstance(location, pyglet.resource.FileLocation):
            import os
            for filename in os.listdir(location.path):
                if filename.lower().endswith('.png') or \
                   filename.lower().endswith('.jpg'):
                    print filename
                    self.placeables.append(placeable.get_placeable(filename))

        if not self.placeables:
            self.placeables = [placeable.get_placeable('crab.png')]

        self.editor = editor
        self.layer = layer

        self.placeable_index = 0
        self.image = None

        super(PlaceableWindow, self).__init__(
            width=256, height=256,
            style='tool',
            resizable=True,
            caption=caption)

    def on_mouse_press(self, x, y, button, modifiers):
        if modifiers & key.MOD_CTRL:
            if modifiers & key.MOD_SHIFT:
                self.placeable_index -= 1
            else:
                self.placeable_index += 1
            self.placeable_index = self.placeable_index % len(self.placeables)
            self.image = self.placeables[self.placeable_index].get_image()
        self.editor.select_tool(
            PlaceableTool(self.editor, 
                          self.layer,
                          self.placeables[self.placeable_index]))

    def on_draw(self):
        if not self.image:
            self.image = self.placeables[self.placeable_index].get_image()
        image = self.image
        scale = min(self.width / float(image.width), 
                    self.height / float(image.height))
        scale = min(scale, 1.)
        width = image.width * scale
        height = image.height * scale

        glClearColor(.5, .5, .5, 1)
        self.clear()
        glColor3f(1, 1, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        image.blit(0, 0, width=width, height=height)

        
