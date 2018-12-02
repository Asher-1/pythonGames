#!/usr/bin/env python

# The basic area editor
#
# To edit an existing level, use
# editor levelname
#
# To create a new level:
#
# editor levelname <xsize> <ysize>
# (size specified in pixels
#

import os
import sys

import pygame
import pygame.locals as pgl

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pymunk

from albow.root import RootWidget
from albow.widget import Widget
from albow.controls import Button, Label, CheckBox
from albow.dialogs import alert, Dialog, ask
from albow.layout import Row
from albow.fields import TextField
from albow.table_view import TableView, TableColumn

from nagslang.options import parse_args
from nagslang.constants import SCREEN
from nagslang.level import Level, POLY_COLORS, LINE_COLOR
from nagslang.yamlish import load_s
import nagslang.enemies as ne
import nagslang.game_object as ngo
import nagslang.collectable as collectable
import nagslang.puzzle as np

# layout constants
MENU_BUTTON_HEIGHT = 35
MENU_PAD = 4
MENU_HALF_PAD = MENU_PAD // 2
MENU_LEFT = SCREEN[0] + MENU_HALF_PAD
MENU_WIDTH = 200 - MENU_PAD
MENU_HALF_WIDTH = MENU_WIDTH // 2 - MENU_HALF_PAD

BUTTON_RECT = pygame.rect.Rect(0, 0, MENU_WIDTH, MENU_BUTTON_HEIGHT)
HALF_BUTTON_RECT = pygame.rect.Rect(0, 0, MENU_HALF_WIDTH, MENU_BUTTON_HEIGHT)
CHECK_RECT = pygame.rect.Rect(0, 0, MENU_BUTTON_HEIGHT // 2,
                              MENU_BUTTON_HEIGHT // 2)


class TestWorld(object):

    def __init__(self):
        self.level_state = {}
        self.inventory = {}


def distance(tup1, tup2):
    return (tup1[0] - tup2[0]) ** 2 + (tup1[1] - tup2[1]) ** 2


class EditorLevel(Level):

    def __init__(self, name, x=800, y=600):
        world = TestWorld()
        super(EditorLevel, self).__init__(name, world)
        self.x = x
        self.y = y
        # Lookup initiliasition info from the objects
        self.lookup = {}
        self._move_poly = None

    def _in_bounds(self, pos):
        if pos[0] < 0 or pos[0] >= self.x:
            return False
        if pos[1] < 0 or pos[1] >= self.y:
            return False
        return True

    def load(self, space):
        super(EditorLevel, self).load(space)
        # Needed to fill in the lookup dict
        self.reset_objs()

    def point_to_pygame(self, pos):
        # inverse of point_to_pymunk
        # (this is also the same as point_to_pymunk, but an additional
        # function for sanity later in pyweek).
        return (pos[0], self.y - pos[1])

    def point_to_pymunk(self, pos):
        # inverse of point_to_pygame
        # (this is also the same as point_to_pygame, but an additional
        # function for sanity later in pyweek).
        return (pos[0], self.y - pos[1])

    def add_point(self, poly_index, pos):
        self.polygons.setdefault(poly_index, [])
        if not self._in_bounds(pos):
            return False
        if not self.polygons[poly_index]:
            point = self.point_to_pymunk(pos)
            self.polygons[poly_index].append(point)
        else:
            add_pos = self.point_to_pymunk(pos)
            self.polygons[poly_index].append(add_pos)
        return True

    def delete_point(self, index):
        if index in self.polygons and len(self.polygons[index]) > 0:
            self.polygons[index].pop()

    def close_poly(self, index):
        """Attempts to close the current polygon.

           We allow a small additional step to close the polygon, but
           it's limited as it's a magic point addition"""
        if len(self.polygons[index]) < 2:
            # Too small
            return False
        first = self.polygons[index][0]
        if self.add_point(index, self.point_to_pygame(first)):
            return True
        return False

    def add_line(self, start_pos, end_pos):
        startpoint = self.point_to_pymunk(start_pos)
        endpoint = self.point_to_pymunk(end_pos)
        self.lines.append([startpoint, endpoint])

    def draw(self, mouse_pos, mouse_poly, filled, draw_cand_line, start_pos,
             move_point_mode, move_poly_mode, move_point, zoom_factor,
             level_widget):
        self._draw_background(True)
        # Draw polygons as needed for the editor
        line_width = int(2 * zoom_factor)
        if filled:
            self._draw_exterior(True)
        for index, polygon in self.polygons.items():
            color = POLY_COLORS.get(index, pygame.color.THECOLORS['black'])
            if move_point_mode and index == self._move_poly and move_point:
                pointlist = [p for p in polygon]
                pointlist = [self.point_to_pygame(p) if p != move_point else
                             mouse_pos for p in pointlist]
                pygame.draw.lines(self._surface, color, False, pointlist,
                                  line_width)
                break
            if move_poly_mode and index == self._move_poly and move_point:
                new_point = self.point_to_pymunk(mouse_pos)
                pointlist = [self.point_to_pygame(p)
                             for p in self.translate_poly(
                                 polygon, move_point, new_point)]
                pygame.draw.lines(self._surface, color, False, pointlist,
                                  line_width)
                #break
            if len(polygon) > 1:
                pointlist = [self.point_to_pygame(p) for p in polygon]
                pygame.draw.lines(self._surface, color, False, pointlist,
                                  line_width)
            if index == mouse_poly and mouse_pos and len(polygon) > 0:
                endpoint = self.point_to_pymunk(mouse_pos)
                pygame.draw.line(self._surface, color,
                                 self.point_to_pygame(polygon[-1]),
                                 self.point_to_pygame(endpoint),
                                 line_width // 2)
        line_found = False  # Hack for sane behaviour if lines overlap
        for line in self.lines:
            pointlist = [self.point_to_pygame(p) for p in line]
            if move_point_mode and not self._move_poly and not line_found:
                if move_point in line:
                    line_found = True
                    pointlist.remove(self.point_to_pygame(move_point))
                    pointlist.append(mouse_pos)
            pygame.draw.lines(self._surface, LINE_COLOR, False, pointlist,
                              line_width)
        if draw_cand_line and start_pos and mouse_pos:
            endpoint = level_widget.snap_to_grid(mouse_pos)
            endpoint = self.point_to_pymunk(endpoint)
            pointlist = [start_pos,
                         self.point_to_pygame(endpoint)]
            pygame.draw.lines(self._surface, LINE_COLOR, False, pointlist, 1)
        return self._surface

    def reset_objs(self):
        # Reset the object state - needed when changing stuff
        self.drawables = []
        self.overlay_drawables = []
        self._glue = np.PuzzleGlue()
        for game_object_dict in self._game_objects:
            obj = self._create_game_object(pymunk.Space(), **game_object_dict)
            self.lookup[obj] = game_object_dict
        for enemy_dict in self._enemies:
            obj = self._create_enemy(pymunk.Space(), **enemy_dict)
            self.lookup[obj] = enemy_dict

    def get_class(self, classname, mod=None):
        # Get the class given the classname
        modules = {
            'game_object': ngo,
            'collectable': collectable,
            'enemies': ne,
            'puzzle': np,
        }
        if '.' in classname:
            modname, classname = classname.split('.')
            mod = modules[modname]
        if mod is None:
            mod = ngo
        return getattr(mod, classname)

    def try_new_object(self, classname, target, new, old=None):
        if old in target:
            target.remove(old)
        try:
            target.append(new)
            self.reset_objs()
            test_surface = pygame.surface.Surface((self.x, self.y))
            # Check for initialisation stuff that happens in render
            for thing in self.drawables:
                if not isinstance(thing, ne.Enemy):
                    thing.render(test_surface)
            return True
        except Exception as e:
            target.remove(new)
            if old is not None:
                target.append(old)
            self.reset_objs()
            alert("Failed to update object %s: %s" % (classname, e))
        return False

    def find_obj_at_pos(self, mouse_pos):
        pymunk_pos = self.point_to_pymunk(mouse_pos)
        # Search visible objects
        for obj in self.drawables:
            if obj.get_shape().point_query(pymunk_pos):
                return obj
        return None

    def find_vertex(self, mouse_pos):
        # search for vertexes closest to where we've killed
        mindist = 1000
        move_point = None
        search_point = self.point_to_pymunk(mouse_pos)
        for index, polygon in self.polygons.items():
            for point in polygon:
                dist = distance(point, search_point)
                if dist < mindist:
                    mindist = dist
                    move_point = point
                    self._move_poly = index
        # Also check lines
        for line in self.lines:
            for point in line:
                dist = distance(point, search_point)
                if dist < mindist:
                    mindist = dist
                    move_point = point
                    self._move_poly = None
        return move_point

    def translate_poly(self, poly, move_point, new_point):
        dx = new_point[0] - move_point[0]
        dy = new_point[1] - move_point[1]
        new_poly = [(p[0] + dx, p[1] + dy) for p in poly]
        return new_poly

    def replace_poly(self, move_point, new_point):
        new_point = self.point_to_pymunk(new_point)
        if self._move_poly:
            self.polygons[self._move_poly] = self.translate_poly(
                self.polygons[self._move_poly], move_point, new_point)

    def replace_vertex(self, old_point, new_point):
        new_point = self.point_to_pymunk(new_point)
        if self._move_poly:
            new_polygon = [p if p != old_point else new_point for p in
                           self.polygons[self._move_poly]]
            self.polygons[self._move_poly] = new_polygon
        else:
            for line in self.lines:
                if old_point in line:
                    line.remove(old_point)
                    line.append(new_point)
                    break


class ObjectTable(TableView):

    columns = [TableColumn("Object", 690, 'l', '%r')]

    def __init__(self, data):
        super(ObjectTable, self).__init__(height=450)
        self.data = sorted(data,
                           key=lambda d: (d.get('classname'), d.get('name')))
        self.selected_row = -1

    def num_rows(self):
        return len(self.data)

    def row_data(self, i):
        data = self.data[i]
        if 'name' in data:
            return ('%s (%s)' % (data['classname'], data['name']), )
        return (data['classname'], )

    def row_is_selected(self, i):
        return self.selected_row == i

    def click_row(self, i, ev):
        self.selected_row = i

    def get_selection(self):
        if self.selected_row >= 0:
            return self.data[self.selected_row]
        return None


class EditClassDialog(Dialog):

    def __init__(self, classname, cls, data, level_widget,
                 delete=False):
        super(EditClassDialog, self).__init__()
        self.level_widget = level_widget
        self.classname = classname
        self.rect = pygame.rect.Rect(0, 0, 900, 550)
        title = Label("Editing %s" % classname)
        title.rect = pygame.rect.Rect(100, 10, 600, 25)
        self.add(title)
        self.requires = cls.requires()
        y = 40
        self.fields = {}
        index = 0
        self.poly_field = None
        self.needs_cleanup = False
        for requirement, hint in self.requires:
            label = Label(requirement)
            label.rect = pygame.rect.Rect(40, y, 200, 25)
            self.add(label)
            field = TextField()
            field.rect = pygame.rect.Rect(220, y, 400, 25)
            self.add(field)
            if data is not None:
                if requirement in data:
                    field.set_text('%s' % data[requirement])
                elif 'args' in data and requirement != 'name':
                    # NB: The ordering assumptions in requires should make
                    # this safe, but it's really, really, really fragile
                    try:
                        field.set_text('%s' % data['args'][index])
                        index += 1
                    except IndexError:
                        # Assumed to be arguments with the default value
                        pass
            if hint.startswith('polygon'):
                self.poly_field = field
            self.fields[requirement] = field
            hintlabel = Label(hint)
            hintlabel.rect = pygame.rect.Rect(640, y, 250, 25)
            self.add(hintlabel)
            y += 30
        if self.poly_field:
            y += 40
            label = Label("Polygon to use:")
            label.rect = pygame.rect.Rect(40, y, 200, 25)
            self.add(label)
            self.poly_choice = TextField()
            self.poly_choice.rect = pygame.Rect(280, y, 400, 25)
            self.add(self.poly_choice)
            y += 30
            button = Button('Use Polygon X', action=self.get_poly)
            button.rect = pygame.rect.Rect(350, y, 250, 30)
            self.add(button)
        buttons = []
        if delete:
            labels = ['OK', 'Delete', 'Cancel']
        else:
            labels = ['OK', 'Cancel']
        for text in labels:
            but = Button(text, action=lambda x=text: self.dismiss(x))
            buttons.append(but)
        row = Row(buttons)
        row.rect = pygame.rect.Rect(250, 500, 700, 50)
        self.add(row)

    def get_poly(self):
        try:
            try:
                index = int(self.poly_choice.get_text())
            except ValueError:
                index = 0
            data = self.level_widget.level.polygons[index][:]
        except KeyError:
            data = []
        if data:
            # We unclose the polygon, because that's what pymunk
            # wants
            if data[0] == data[-1] and len(data) > 1:
                data.pop()
            data = [list(x) for x in data]
            self.needs_cleanup = True
            self.poly_field.set_text('%s' % data)

    def cleanup(self):
        if self.needs_cleanup:
            self.level_widget.level.polygons[6] = []
            self.level_widget.invalidate()

    def get_data(self):
        result = {}
        result['classname'] = self.classname
        args = []
        # We arrange to bounce this through yaml'ish to convert
        # stuff to the expected type
        for val, _ in self.requires:
            text = self.fields[val].get_text()
            if not text:
                # skip empty fields
                continue
            if val == 'name':
                result['name'] = text
            elif self.fields[val] == self.poly_field and text:
                # Evil, but faster than good
                try:
                    l = eval(text)
                except Exception:
                    alert("Invalid polygon %s" % text)
                    self.needs_cleanup = False
                    return None
                # Check for convexity
                if not pymunk.util.is_convex(l):
                    alert("Invalid polygon %s - not convex" % text)
                    return None
                if not pymunk.util.is_clockwise(l):
                    l.reverse()
                    if not pymunk.util.is_clockwise(l):
                        alert("Invalid polygon %s - unable to make clockwise"
                              % text)
                        return None
                args.append(' - - %s' % l[0])
                for coord in l[1:]:
                    args.append('   - %s' % coord)
            else:
                args.append(' - ' + text)
        data = "args:\n" + '\n'.join(args)
        result['args'] = load_s(data)['args']
        return result


class LevelWidget(Widget):

    def __init__(self, level, parent):
        super(LevelWidget, self).__init__(pygame.rect.Rect(0, 0,
                                          SCREEN[0], SCREEN[1]))
        self.level = level
        self.pos = (0, 0)
        self.filled_mode = False
        self.mouse_pos = None
        self.cur_poly = None
        self._mouse_drag = False
        self._draw_objects = False
        self._draw_enemies = False
        self._draw_lines = False
        self.grid_size = 1
        self.sel_mode = False
        self.move_obj_mode = False
        self.move_obj = None
        self._start_pos = None
        self._parent = parent
        self._move_point_mode = False
        self._move_poly_mode = False
        self._move_point = False
        self._zoom_factor = 1.0

    def _level_coordinates(self, pos):
        # Move positions to level values
        if not pos:
            return (0, 0)
        # Apply zoom_factor
        pos = pos[0] + self.pos[0], pos[1] + self.pos[1]
        zoomed = (pos[0] * self._zoom_factor, pos[1] * self._zoom_factor)
        return int(zoomed[0]), int(zoomed[1])

    def _move_view(self, offset):
        new_pos = [self.pos[0] + offset[0], self.pos[1] + offset[1]]
        if new_pos[0] < 0:
            new_pos[0] = self.pos[0]
        elif new_pos[0] > self.level.x - SCREEN[0]:
            new_pos[0] = self.pos[0]
        if new_pos[1] < 0:
            new_pos[1] = self.pos[1]
        elif new_pos[1] > self.level.y - SCREEN[1]:
            new_pos[1] = self.pos[1]
        self.pos = tuple(new_pos)

    def inc_grid_size(self, amount):
        self.grid_size = max(1, self.grid_size + amount)
        if self.grid_size > 1:
            self.grid_size = self.grid_size - (self.grid_size % 5)

    def snap_to_grid(self, pos):
        x = pos[0] - (pos[0] % self.grid_size)
        y = pos[1] - (pos[1] % self.grid_size)
        return (x, y)

    def set_objects(self, value):
        if self._draw_objects != value:
            self._draw_objects = value
            self.invalidate()

    def set_enemies(self, value):
        if self._draw_enemies != value:
            self._draw_enemies = value
            self.invalidate()

    def zoom_out(self):
        self._zoom_factor = self._zoom_factor * 2.0
        if self._zoom_factor > 8:
            self._zoom_factor = 8

    def zoom_in(self):
        self._zoom_factor = self._zoom_factor // 2.0
        if self._zoom_factor < 1:
            self._zoom_factor = 1

    def draw(self, surface):
        if (self.cur_poly is not None and self.cur_poly in self.level.polygons
                and len(self.level.polygons[self.cur_poly])):
            # We have an active polygon
            mouse_pos = self._level_coordinates(self.mouse_pos)
            mouse_pos = self.snap_to_grid(mouse_pos)
        elif self._draw_lines:
            # Interior wall mode
            mouse_pos = self._level_coordinates(self.mouse_pos)
            mouse_pos = self.snap_to_grid(mouse_pos)
        elif self._move_point_mode or self._move_poly_mode:
            mouse_pos = self._level_coordinates(self.mouse_pos)
            mouse_pos = self.snap_to_grid(mouse_pos)
        else:
            mouse_pos = None
        level_surface = level.draw(mouse_pos, self.cur_poly, self.filled_mode,
                                   self._draw_lines, self._start_pos,
                                   self._move_point_mode, self._move_poly_mode,
                                   self._move_point, self._zoom_factor, self)
        if self._draw_objects:
            for thing in self.level.drawables:
                if not isinstance(thing, ne.Enemy):
                    thing.render(level_surface)
        if self._draw_enemies:
            for thing in self.level.drawables:
                if isinstance(thing, ne.Enemy):
                    thing.render(level_surface)
        surface_area = pygame.rect.Rect(self.pos, SCREEN)
        zoomed_surface = level_surface.copy()
        if self._zoom_factor != 1:
            zoomed_surface = pygame.transform.scale(
                level_surface,
                (int(level_surface.get_width() / self._zoom_factor),
                 int(level_surface.get_height() / self._zoom_factor)))
        surface.blit(zoomed_surface, (0, 0), surface_area)

    def change_poly(self, new_poly):
        self.cur_poly = new_poly
        self._draw_lines = False
        self._move_point_mode = False
        if self.cur_poly is not None:
            self._parent.reset_lit_buttons()
            self.filled_mode = False

    def line_mode(self):
        self.cur_poly = None
        self._parent.reset_lit_buttons()
        self._draw_lines = True
        self.filled_mode = False
        self._start_pos = None
        self._move_point_mode = False
        self._move_poly_mode = False

    def key_down(self, ev):
        if ev.key == pgl.K_LEFT:
            self._move_view((-10, 0))
        elif ev.key == pgl.K_RIGHT:
            self._move_view((10, 0))
        elif ev.key == pgl.K_UP:
            self._move_view((0, -10))
        elif ev.key == pgl.K_DOWN:
            self._move_view((0, 10))
        elif ev.key in (pgl.K_1, pgl.K_2, pgl.K_3, pgl.K_4, pgl.K_5, pgl.K_6):
            self.change_poly(ev.key - pgl.K_0)
        elif ev.key == pgl.K_0:
            self.change_poly(None)
        elif ev.key == pgl.K_d and self.cur_poly:
            self.level.delete_point(self.cur_poly)
        elif ev.key == pgl.K_f:
            self.set_filled()
        elif ev.key == pgl.K_c:
            self.close_poly()

    def set_move_poly_mode(self):
        self._draw_lines = False
        self._move_point_mode = False
        self._move_poly_mode = True
        self.filled_mode = False
        self._parent.reset_lit_buttons()
        self._move_point = None

    def set_move_mode(self):
        self._draw_lines = False
        self._move_point_mode = True
        self._move_poly_mode = False
        self.filled_mode = False
        self._parent.reset_lit_buttons()
        self._move_point = None

    def set_filled(self):
        closed, _ = self.level.all_closed()
        if closed:
            self.cur_poly = None
            self._parent.reset_lit_buttons()
            self.filled_mode = True
            self._draw_lines = False
            self._move_point_mode = False
            self._move_poly_mode = False
        else:
            alert('Not all polygons closed, so not filling')

    def mouse_move(self, ev):
        old_pos = self.mouse_pos
        self.mouse_pos = ev.pos
        if self.move_obj:
            corrected_pos = self._level_coordinates(ev.pos)
            snapped_pos = self.snap_to_grid(corrected_pos)
            self._move_obj(self.move_obj, snapped_pos)
        if old_pos != self.mouse_pos and (self.cur_poly or self._draw_lines
                                          or self._move_point_mode
                                          or self._move_poly_mode):
            self.invalidate()

    def mouse_drag(self, ev):
        if self._mouse_drag:
            old_pos = self.mouse_pos
            self.mouse_pos = ev.pos
            diff = (-self.mouse_pos[0] + old_pos[0],
                    -self.mouse_pos[1] + old_pos[1])
            self._move_view(diff)
            self.invalidate()

    def mouse_down(self, ev):
        corrected_pos = self._level_coordinates(ev.pos)
        snapped_pos = self.snap_to_grid(corrected_pos)
        if self.sel_mode and ev.button == 1:
            obj = self.level.find_obj_at_pos(corrected_pos)
            if obj is not None:
                self._edit_selected(obj)
        elif self.move_obj_mode and ev.button == 1 and not self.move_obj:
            obj = self.level.find_obj_at_pos(corrected_pos)
            if obj is not None:
                if obj.movable():
                    self.move_obj = obj
        elif self.move_obj_mode and ev.button == 1 and self.move_obj:
            self._update_pos(self.move_obj, snapped_pos)
            self.move_obj = None
        elif self._move_poly_mode and ev.button == 1:
            if self._move_point:
                # Place the current point
                self.level.replace_poly(self._move_point, snapped_pos)
                self._move_point = None
                self.invalidate()
            else:
                # find the current point
                self._move_point = self.level.find_vertex(corrected_pos)
        elif self._move_point_mode and ev.button == 1:
            if self._move_point:
                # Place the current point
                self.level.replace_vertex(self._move_point, snapped_pos)
                self._move_point = None
                self.invalidate()
            else:
                # find the current point
                self._move_point = self.level.find_vertex(corrected_pos)
        elif ev.button == 1:
            if self._draw_lines:
                if self._start_pos is None:
                    self._start_pos = snapped_pos
                else:
                    self.level.add_line(self._start_pos, snapped_pos)
                    self._start_pos = None
            else:
                print "Click: %r" % (
                    self.level.point_to_pymunk(corrected_pos),)
        if ev.button == 4:  # Scroll up
            self._move_view((0, -10))
        elif ev.button == 5:  # Scroll down
            self._move_view((0, 10))
        elif ev.button == 6:  # Scroll left
            self._move_view((-10, 0))
        elif ev.button == 7:  # Scroll right
            self._move_view((10, 0))
        elif self.cur_poly and ev.button == 1:
            # Add a point
            if not self.level.add_point(self.cur_poly, snapped_pos):
                alert("Failed to place point")
        elif ev.button == 3:
            self._mouse_drag = True

    def mouse_up(self, ev):
        if ev.button == 3:
            self._mouse_drag = False

    def close_poly(self):
        if self.cur_poly is None:
            return
        if self.level.close_poly(self.cur_poly):
            alert("Successfully closed the polygon")
            self.change_poly(None)
        else:
            alert("Failed to close the polygon")

    def _edit_class(self, classname, cls, data):
        # Dialog for class properties
        dialog = EditClassDialog(classname, cls, data, self)
        if dialog.present() == 'OK':
            return dialog
        return None

    def _edit_selected(self, obj):
        data = self.level.lookup[obj]
        cls = obj.__class__
        classname = obj.__class__.__name__
        dialog = EditClassDialog(classname, cls, data, self, True)
        res = dialog.present()
        if res == 'OK':
            edited = dialog.get_data()
            if edited is not None:
                for target in [self.level._game_objects, self.level._enemies]:
                    if data in target:
                        if self.level.try_new_object(classname, target,
                                                     edited, data):
                            dialog.cleanup()
                        break
        elif res == 'Delete':
            for target in [self.level._game_objects, self.level._enemies]:
                if data in target:
                    target.remove(data)
                    self.level.reset_objs()
                    break

    def _make_edit_dialog(self, entries):
        # Dialog to hold the editor
        edit_box = Dialog()
        edit_box.rect = pygame.rect.Rect(0, 0, 700, 500)
        table = ObjectTable(entries)
        edit_box.add(table)
        buttons = []
        for text in ['OK', 'Delete', 'Cancel']:
            but = Button(text, action=lambda x=text: edit_box.dismiss(x))
            buttons.append(but)
        row = Row(buttons)
        row.rect = pygame.rect.Rect(250, 450, 700, 50)
        edit_box.add(row)
        edit_box.get_selection = lambda: table.get_selection()
        return edit_box

    def edit_objects(self):
        edit_box = self._make_edit_dialog(self.level._game_objects)
        res = edit_box.present()
        choice = edit_box.get_selection()
        if choice is None:
            return
        if res == 'OK':
            cls = self.level.get_class(choice['classname'])
            edit_dlg = self._edit_class(choice['classname'], cls, choice)
            if edit_dlg is not None:
                edited = edit_dlg.get_data()
                if self.level.try_new_object(choice["classname"],
                                             self.level._game_objects,
                                             edited, choice):
                    edit_dlg.cleanup()
        elif res == 'Delete':
            self.level._game_objects.remove(choice)
            self.level.reset_objs()

    def edit_enemies(self):
        edit_box = self._make_edit_dialog(self.level._enemies)
        res = edit_box.present()
        choice = edit_box.get_selection()
        if choice is None:
            return
        if res == 'OK':
            cls = self.level.get_class(choice['classname'], ne)
            edit_dlg = self._edit_class(choice['classname'], cls, choice)
            if edit_dlg is not None:
                edited = edit_dlg.get_data()
                if self.level.try_new_object(choice["classname"],
                                             self.level._enemies,
                                             edited, choice):
                    edit_dlg.cleanup()
        elif res == 'Delete':
            self.level._enemies.remove(choice)
            self.level.reset_objs()

    def _make_choice_dialog(self, classes):
        # Dialog to hold the editor
        data = []
        for cls_name, cls in classes:
            data.append({"classname": cls_name, "class": cls})
        choice_box = Dialog()
        choice_box.rect = pygame.rect.Rect(0, 0, 700, 500)
        table = ObjectTable(data)
        choice_box.add(table)
        buttons = []
        for text in ['OK', 'Cancel']:
            but = Button(text, action=lambda x=text: choice_box.dismiss(x))
            buttons.append(but)
        row = Row(buttons)
        row.rect = pygame.rect.Rect(250, 450, 700, 50)
        choice_box.add(row)
        choice_box.get_selection = lambda: table.get_selection()
        return choice_box

    def add_game_object(self):
        classes = ngo.get_editable_game_objects()
        classes.extend(("collectable.%s" % cls_name, cls)
                       for cls_name, cls
                       in collectable.get_editable_game_objects())
        choose = self._make_choice_dialog(classes)
        res = choose.present()
        choice = choose.get_selection()
        if res == 'OK' and choice is not None:
            classname = choice['classname']
            cls = choice['class']
            edit_dlg = self._edit_class(classname, cls, None)
            if edit_dlg is not None:
                new_cls = edit_dlg.get_data()
                if self.level.try_new_object(classname,
                                             self.level._game_objects,
                                             new_cls, None):
                    edit_dlg.cleanup()

    def add_enemy(self):
        classes = ne.get_editable_enemies()
        choose = self._make_choice_dialog(classes)
        res = choose.present()
        choice = choose.get_selection()
        if res == 'OK' and choice is not None:
            classname = choice['classname']
            cls = choice['class']
            edit_dlg = self._edit_class(classname, cls, None)
            if edit_dlg is not None:
                new_cls = edit_dlg.get_data()
                if self.level.try_new_object(classname, self.level._enemies,
                                             new_cls, None):
                    edit_dlg.cleanup()

    def add_puzzler(self):
        classes = np.get_editable_puzzlers()
        choose = self._make_choice_dialog(classes)
        res = choose.present()
        choice = choose.get_selection()
        if res == 'OK' and choice is not None:
            classname = choice['classname']
            cls = choice['class']
            edit_dlg = self._edit_class(classname, cls, None)
            if edit_dlg is not None:
                new_cls = edit_dlg.get_data()
                if self.level.try_new_object(classname,
                                             self.level._game_objects,
                                             new_cls, None):
                    edit_dlg.cleanup()

    def _move_obj(self, obj, new_pos):
        new_coords = self.level.point_to_pymunk(new_pos)
        shape = obj.get_shape()
        shape.body.position = (new_coords[0], new_coords[1])
        data = self.level.lookup[obj]
        args = data['args']
        old_coords = list(args[0])
        param_defs = obj.requires()[1:]  # chop off name
        for i, (key, key_type) in enumerate(param_defs):
            if i > len(args):
                break
            if key_type == "polygon (convex)":
                new_outline = self.level.translate_poly(
                    args[i], old_coords, new_coords)
                obj.update_image(new_outline)
            if key == 'end2':
                mid = shape.a + (shape.b - shape.a) / 2
                delta = new_coords - mid
                shape.unsafe_set_a(shape.a + delta)
                shape.unsafe_set_b(shape.b + delta)
                shape.update(new_pos, (0, 0))
        self.invalidate()

    def _update_pos(self, obj, new_pos):
        data = self.level.lookup[obj]
        new_coords = self.level.point_to_pymunk(new_pos)
        args = data['args']
        old_coords = list(args[0])
        args[0][0] = new_coords[0]
        args[0][1] = new_coords[1]
        param_defs = obj.requires()[1:]  # chop off name
        for i, (key, key_type) in enumerate(param_defs):
            if i > len(args):
                break
            if key_type == "polygon (convex)":
                args[i] = self.level.translate_poly(
                    args[i], old_coords, new_coords)
            if key == 'end2':
                # Horrible, horrible hackery
                shape = obj.get_shape()
                mid = shape.a + (shape.b - shape.a) / 2
                delta = - mid + new_coords
                point2 = list(args[i])
                mid = pymunk.Vec2d(old_coords) + (
                    pymunk.Vec2d(point2) - old_coords) / 2
                delta = new_coords - mid
                args[0][0] = old_coords[0] + delta.x
                args[0][1] = old_coords[1] + delta.y
                args[i][0] = point2[0] + delta.x
                args[i][1] = point2[1] + delta.y
        self.level.reset_objs()
        self.invalidate()


class HighLightButton(Button):
    """Button with highlight support"""
    def __init__(self, text, parent, **kwds):
        super(HighLightButton, self).__init__(text, **kwds)
        self._parent = parent

    def highlight(self):
        self.border_color = pygame.color.Color('red')

    def reset(self):
        self.border_color = self.fg_color


class PolyButton(HighLightButton):
    """Button for coosing the correct polygon"""

    def __init__(self, index, level_widget, parent):
        if index is not None:
            text = "P %s" % index
        else:
            text = 'Exit Draw Mode'
        super(PolyButton, self).__init__(text, parent)
        self.index = index
        self.level_widget = level_widget

    def action(self):
        self.level_widget.change_poly(self.index)
        self._parent.reset_lit_buttons()
        if self.index is not None:
            self.highlight()


class GridSizeLabel(Label):
    """Label and setter for grid size."""

    def __init__(self, level_widget, **kwds):
        self.level_widget = level_widget
        super(GridSizeLabel, self).__init__(self.grid_text(), **kwds)

    def grid_text(self):
        return "Grid size: %d" % self.level_widget.grid_size

    def inc_grid_size(self, amount):
        self.level_widget.inc_grid_size(amount)
        self.set_text(self.grid_text())


class SnapButton(Button):
    """Button for increasing or decreasing snap-to-grid size."""

    def __init__(self, grid_size_label, parent, inc_amount):
        self.grid_size_label = grid_size_label
        self.inc_amount = inc_amount
        text = "Grid %s%d" % (
            '-' if inc_amount < 0 else '+',
            abs(inc_amount))
        self._parent = parent
        super(SnapButton, self).__init__(text)

    def action(self):
        self.grid_size_label.inc_grid_size(self.inc_amount)


class EditorApp(RootWidget):

    def __init__(self, level, surface):
        super(EditorApp, self).__init__(surface)
        self.level = level
        self.level_widget = LevelWidget(self.level, self)
        self.add(self.level_widget)

        self._dMenus = {}

        self._light_buttons = []

        self._make_draw_menu()
        self._make_objects_menu()

        self._menu_mode = 'drawing'
        self._populate_menu()

        self._zoom = 1

    def _make_draw_menu(self):
        widgets = []

        white = pygame.color.Color("white")

        # Add poly buttons
        y = 5
        for poly in range(1, 10):
            but = PolyButton(poly, self.level_widget, self)
            but.rect = pygame.rect.Rect(0, 0, MENU_WIDTH // 3 - MENU_PAD,
                                        MENU_BUTTON_HEIGHT)
            index = poly % 3
            if index == 1:
                but.rect.move_ip(MENU_LEFT, y)
            elif index == 2:
                but.rect.move_ip(MENU_LEFT + MENU_WIDTH // 3 - MENU_HALF_PAD,
                                 y)
            else:
                left = MENU_LEFT + 2 * MENU_WIDTH // 3 - MENU_HALF_PAD
                but.rect.move_ip(left, y)
                y += MENU_BUTTON_HEIGHT + MENU_PAD
            self._light_buttons.append(but)
            widgets.append(but)

        end_poly_but = PolyButton(None, self.level_widget, self)
        end_poly_but.rect = BUTTON_RECT.copy()
        end_poly_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(end_poly_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        self.move_point_but = HighLightButton("Mv Point", self,
                                              action=self.move_point)
        self.move_point_but.rect = HALF_BUTTON_RECT.copy()
        self.move_point_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(self.move_point_but)
        self._light_buttons.append(self.move_point_but)

        self.move_poly_but = HighLightButton("Mv Poly", self,
                                             action=self.move_poly)
        self.move_poly_but.rect = HALF_BUTTON_RECT.copy()
        self.move_poly_but.rect.move_ip(MENU_LEFT + MENU_HALF_WIDTH, y)
        widgets.append(self.move_poly_but)
        self._light_buttons.append(self.move_poly_but)

        y += MENU_BUTTON_HEIGHT + MENU_PAD

        # grid size widgets
        grid_size_label = GridSizeLabel(
            self.level_widget, width=BUTTON_RECT.width,
            align="c", fg_color=white)
        grid_size_label.rect.move_ip(MENU_LEFT, y)
        widgets.append(grid_size_label)
        y += grid_size_label.rect.height + MENU_PAD
        inc_snap_but = SnapButton(grid_size_label, self, 5)
        inc_snap_but.rect = HALF_BUTTON_RECT.copy()
        inc_snap_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(inc_snap_but)
        dec_snap_but = SnapButton(grid_size_label, self, -5)
        dec_snap_but.rect = HALF_BUTTON_RECT.copy()
        dec_snap_but.rect.move_ip(
            MENU_LEFT + MENU_HALF_WIDTH, y)
        widgets.append(dec_snap_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        self.draw_line_but = HighLightButton("Draw interior wall", self,
                                             action=self.set_line_mode)
        self.draw_line_but.rect = BUTTON_RECT.copy()
        self.draw_line_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(self.draw_line_but)
        self._light_buttons.append(self.draw_line_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        fill_but = Button('Fill exterior', action=self.level_widget.set_filled)
        fill_but.rect = BUTTON_RECT.copy()
        fill_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(fill_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        close_poly_but = Button('Close Polygon',
                                action=self.level_widget.close_poly)
        close_poly_but.rect = BUTTON_RECT.copy()
        close_poly_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(close_poly_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        self.show_objs = CheckBox(fg_color=white)
        self.show_objs.rect = CHECK_RECT.copy()
        self.show_objs.rect.move_ip(MENU_LEFT, y)
        label = Label("Show Objects", fg_color=white)
        label.rect.move_ip(MENU_LEFT + MENU_BUTTON_HEIGHT // 2 + MENU_PAD, y)
        widgets.append(self.show_objs)
        widgets.append(label)
        y += label.rect.height + MENU_PAD

        self.show_enemies = CheckBox(fg_color=white)
        self.show_enemies.rect = CHECK_RECT.copy()
        self.show_enemies.rect.move_ip(MENU_LEFT, y)
        label = Label("Show enemy start pos", fg_color=white)
        label.rect.move_ip(MENU_LEFT + MENU_BUTTON_HEIGHT // 2 + MENU_PAD, y)
        widgets.append(self.show_enemies)
        widgets.append(label)
        y += label.rect.height + MENU_PAD

        y += MENU_PAD
        switch_but = Button('Switch to Objects', action=self.switch_to_objects)
        switch_but.rect = BUTTON_RECT.copy()
        switch_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(switch_but)
        y += switch_but.rect.height + MENU_PAD

        save_but = Button('Save Level', action=self.save)
        save_but.rect = BUTTON_RECT.copy()
        save_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(save_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        zoom_out = Button('Zoom out', action=self.level_widget.zoom_out)
        zoom_out.rect = BUTTON_RECT.copy()
        zoom_out.rect.width = zoom_out.rect.width // 2
        zoom_out.rect.move_ip(MENU_LEFT, y)
        widgets.append(zoom_out)

        zoom_in = Button('Zoom in', action=self.level_widget.zoom_in)
        zoom_in.rect = BUTTON_RECT.copy()
        zoom_in.width = zoom_in.width // 2
        zoom_in.rect.move_ip(MENU_LEFT + zoom_out.width, y)
        widgets.append(zoom_in)

        y = SCREEN[1] - MENU_BUTTON_HEIGHT - MENU_PAD
        quit_but = Button('Quit', action=self.do_quit)
        quit_but.rect = BUTTON_RECT.copy()
        quit_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(quit_but)

        self._dMenus['drawing'] = widgets

    def _make_objects_menu(self):
        widgets = []

        # Add poly buttons
        y = 15

        edit_objs_but = Button('Edit Objects',
                               action=self.level_widget.edit_objects)
        edit_objs_but.rect = BUTTON_RECT.copy()
        edit_objs_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(edit_objs_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        edir_enemies_but = Button('Edit Enemies',
                                  action=self.level_widget.edit_enemies)
        edir_enemies_but.rect = BUTTON_RECT.copy()
        edir_enemies_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(edir_enemies_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        add_obj_but = Button('Add Game Object',
                             action=self.level_widget.add_game_object)
        add_obj_but.rect = BUTTON_RECT.copy()
        add_obj_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(add_obj_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        add_puzzle_but = Button('Add Puzzler',
                                action=self.level_widget.add_puzzler)
        add_puzzle_but.rect = BUTTON_RECT.copy()
        add_puzzle_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(add_puzzle_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        add_enemy_but = Button('Add Enemy',
                               action=self.level_widget.add_enemy)
        add_enemy_but.rect = BUTTON_RECT.copy()
        add_enemy_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(add_enemy_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        y += MENU_PAD
        self.sel_mode_but = HighLightButton('Select Object', self,
                                            action=self.sel_mode)
        self.sel_mode_but.rect = BUTTON_RECT.copy()
        self.sel_mode_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(self.sel_mode_but)
        self._light_buttons.append(self.sel_mode_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        y += MENU_PAD
        self.move_obj_mode_but = HighLightButton('Move Object', self,
                                                 action=self.move_obj_mode)
        self.move_obj_mode_but.rect = BUTTON_RECT.copy()
        self.move_obj_mode_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(self.move_obj_mode_but)
        self._light_buttons.append(self.move_obj_mode_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        y += MENU_PAD
        switch_but = Button('Switch to Drawing', action=self.switch_to_draw)
        switch_but.rect = BUTTON_RECT.copy()
        switch_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(switch_but)
        y += switch_but.rect.height + MENU_PAD

        save_but = Button('Save Level', action=self.save)
        save_but.rect = BUTTON_RECT.copy()
        save_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(save_but)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        zoom_out = Button('Zoom out', action=self.level_widget.zoom_out)
        zoom_out.rect = BUTTON_RECT.copy()
        zoom_out.rect.width = zoom_out.rect.width // 2
        zoom_out.rect.move_ip(MENU_LEFT, y)
        widgets.append(zoom_out)

        zoom_in = Button('Zoom in', action=self.level_widget.zoom_in)
        zoom_in.rect = BUTTON_RECT.copy()
        zoom_in.width = zoom_in.width // 2
        zoom_in.rect.move_ip(MENU_LEFT + zoom_out.width, y)
        widgets.append(zoom_in)
        y += MENU_BUTTON_HEIGHT + MENU_PAD

        y = SCREEN[1] - MENU_BUTTON_HEIGHT - MENU_PAD
        quit_but = Button('Quit', action=self.do_quit)
        quit_but.rect = BUTTON_RECT.copy()
        quit_but.rect.move_ip(MENU_LEFT, y)
        widgets.append(quit_but)

        self._dMenus['objects'] = widgets

    def key_down(self, ev):
        if ev.key == pgl.K_ESCAPE:
            self.do_quit()
        elif ev.key == pgl.K_s:
            self.save()
        else:
            self.level_widget.key_down(ev)

    def do_quit(self):
        res = ask("Really Quit?")
        if res == "OK":
            self.quit()

    def save(self):
        closed, messages = self.level.all_closed()
        if closed:
            self.level.save()
            # display success
            alert("Level %s saved successfully." % self.level.name)
        else:
            # display errors
            alert("Failed to save level.\n\n%s" % '\n'.join(messages))

    def switch_to_draw(self):
        if self._menu_mode != 'drawing':
            self._clear_menu()
            self._menu_mode = 'drawing'
            self._populate_menu()

    def switch_to_objects(self):
        if self._menu_mode != 'objects':
            self._clear_menu()
            self._menu_mode = 'objects'
            self._populate_menu()

    def _clear_menu(self):
        for widget in self._dMenus[self._menu_mode]:
            self.remove(widget)

    def reset_lit_buttons(self):
        for but in self._light_buttons:
            but.reset()

    def _populate_menu(self):
        self.level_widget.change_poly(None)
        self.level_widget.sel_mode = False
        self.level_widget.move_obj_mode = False
        self.level_widget.move_obj = None
        for widget in self._dMenus[self._menu_mode]:
            self.add(widget)
        self.invalidate()

    def set_line_mode(self):
        self.level_widget.line_mode()
        self.draw_line_but.highlight()

    def sel_mode(self):
        self.level_widget.sel_mode = not self.level_widget.sel_mode
        if self.level_widget.sel_mode:
            self.move_obj_mode_but.reset()
            self.sel_mode_but.highlight()
            self.level_widget.move_obj_mode = False
            self.level_widget.move_obj = None
        else:
            self.sel_mode_but.reset()

    def move_obj_mode(self):
        self.level_widget.move_obj_mode = not self.level_widget.move_obj_mode
        if self.level_widget.move_obj_mode:
            self.sel_mode_but.reset()
            self.move_obj_mode_but.highlight()
            self.level_widget.sel_mode = False
        else:
            self.move_obj_mode_but.reset()

    def mouse_move(self, ev):
        self.level_widget.mouse_move(ev)

    def move_point(self):
        self.level_widget.set_move_mode()
        self.move_point_but.highlight()

    def move_poly(self):
        self.level_widget.set_move_poly_mode()
        self.move_poly_but.highlight()

    def draw(self, surface):
        # Update checkbox state
        if self._menu_mode == 'drawing':
            self.level_widget.set_objects(self.show_objs.value)
            self.level_widget.set_enemies(self.show_enemies.value)
        else:
            self.level_widget.set_objects(True)
            self.level_widget.set_enemies(True)
        super(EditorApp, self).draw(surface)


if __name__ == "__main__":
    if len(sys.argv) not in [2, 4]:
        print 'Please supply a levelname or levelname and level size'
        sys.exit()
    # Need to ensure we have defaults for rendering
    parse_args([])
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((SCREEN[0] + MENU_WIDTH, SCREEN[1]),
                            pgl.SWSURFACE)
    if len(sys.argv) == 2:
        level = EditorLevel(sys.argv[1])
        level.load(pymunk.Space())
    elif len(sys.argv) == 4:
        level = EditorLevel(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    pygame.display.set_caption('Nagslang Area Editor')
    pygame.key.set_repeat(200, 100)
    app = EditorApp(level, pygame.display.get_surface())
    app.run()
