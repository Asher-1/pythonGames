'''
Created on 13.09.2011

@author: Archy
'''

import math
import data

from math2d import Vector2

from gui import Gui
from gui import Label
from gui import Button
from gui import EditLabel

from modes import Mode

from pyglet.window import key
from pyglet.window import mouse

from game import GameState

from pathfinding import Path
from pathfinding import Waypoint

from towers import Bunker
from towers import Tank
from towers import Artillery

from misc import Beauty

from buildings import HQ
from buildings import Spawner
from buildings import FastFood
from buildings import Orphanage
from buildings import Beergarden

from globals import Z_INDICES
from random import Random

class EditGui(Gui):
    
    mapNameInput = None
    
    rnd = Random()
    
    def __init__(self, application):
        Gui.__init__(self, application)
        
        spacing = 5
        buttonSize = Vector2(150, 25)
        menuPosition = Vector2(1105, 670)
        
        self.add_element(Button     (menuPosition, buttonSize, "MainMenu",lambda:self.on_mainmenu()))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        
        self.mapNameInput = self.add_element(EditLabel  (menuPosition, buttonSize, ".default"))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button     (menuPosition, buttonSize * Vector2(0.5, 1.0), "Save",    lambda:self.on_save_click()))
        self.add_element(Button     (menuPosition + buttonSize * Vector2(0.5, 0.0), buttonSize * Vector2(0.5, 1.0), "Load",    lambda:self.on_load_click()))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button     (menuPosition, buttonSize, "Save&Play",    lambda:self.on_save_and_play_click()))
                
        buttonSize = Vector2(150, 15)
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        
        self.add_element(Label(menuPosition, buttonSize, "View"))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "Paths",       lambda:self.on_paths_click()))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        
        self.add_element(Label(menuPosition, buttonSize, "Buildings"))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "HQ",          lambda:self.on_create_hq(HQ)))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "FastFood",    lambda:self.on_create_spawner(FastFood)))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "Orphanage",   lambda:self.on_create_spawner(Orphanage)))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "Beergarden",   lambda:self.on_create_spawner(Beergarden)))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        
        self.add_element(Label(menuPosition, buttonSize, "Towers"))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "Bunker",      lambda:self.on_create_tower(Bunker)))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "Tank",        lambda:self.on_create_tower(Tank)))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "Artillery",   lambda:self.on_create_tower(Artillery)))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        
        self.add_element(Label(menuPosition, buttonSize, "Street"))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "Straight",      lambda:self.on_create_street('path_straight.png', Z_INDICES.STREETS)))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "Corner",      lambda:self.on_create_street('path_corner.png', Z_INDICES.STREETS)))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "T",      lambda:self.on_create_street('path_T.png', Z_INDICES.STREETS)))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "X",      lambda:self.on_create_street('path_X.png', Z_INDICES.STREETS)))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        
        self.add_element(Label(menuPosition, buttonSize, "Deco"))
        menuPosition -= Vector2(0, buttonSize.y + spacing)
        self.add_element(Button(menuPosition, buttonSize, "Tree",      lambda:self.on_create_beauty('deco_tree.png', Z_INDICES.BEAUTY)))
        
    
    def on_mainmenu(self):
        self._app.set_mode('MainMenu')
    
    def on_save_click(self):
        self.dispatch_event('on_save', self.mapNameInput.get_text())
    
    def on_save_and_play_click(self):
        mapName = self.mapNameInput.get_text()
        self.dispatch_event('on_save', mapName)
        self._app.start_map(mapName, editButton=True)
    
    def on_load_click(self):
        self.dispatch_event('on_load', self.mapNameInput.get_text())
    
    def on_paths_click(self):
        self.dispatch_event('on_toggle_paths')
        
    def on_create_hq(self, constructor):
        self.dispatch_event('on_build_new', constructor)
    
    def on_create_spawner(self, constructor):
        self.dispatch_event('on_build_new', constructor)
        
    def on_create_tower(self, constructor):
        self.dispatch_event('on_build_new', constructor)
        
    def on_create_beauty(self, texture, z_index):
        self.dispatch_event('on_build_new', lambda: self.build_beauty(texture, z_index, True, True) )
    
    def on_create_street(self, texture, z_index):
        self.dispatch_event('on_build_new', lambda: self.build_beauty(texture, z_index) )

    def build_beauty(self, texture, z_index, randomRotation = False, randomScale = False):
        beauty = Beauty()
        beauty.set_texture_name(texture)
        if randomRotation:
            beauty.set_rotation(self.rnd.random() * 360.0)
        if randomScale:
            beauty.set_scale(0.45 + self.rnd.random() * 1.5)
        
        beauty.set_z_index(z_index)
        return beauty        

EditGui.register_event_type('on_save')
EditGui.register_event_type('on_load')
EditGui.register_event_type('on_toggle_paths')
EditGui.register_event_type('on_build_new')


class EditMode(Mode):
        
    _Gui = None
    _GameState = None
    
    _CurrentBuild = None
    _CurrentPath = None
    _DragWaypoint = None
    _PathEntity = None
    
    _LastMouse = Vector2(0.0, 0.0)
    
    _LastBuildRotation = 0.0
    _LastBuildConstructor = None
    
    _EntityHighlight = None
    _RotationStep = 22.5
    
    showPaths = True 
    
    DEFAULT_MAP = "default"
    
    def __init__(self, application):
        Mode.__init__(self, application)
        
        self._Gui = EditGui(application)
        self._Gui.hide()
        self._Gui.push_handlers(self)
        
    def enter(self):
        Mode.enter(self) 
        self._Gui.show()
        
        if self._GameState:
            self._GameState.set_visible(True)
        else:
            self.on_load(self.DEFAULT_MAP)
    
    def leave(self):
        Mode.leave(self)
        self._Gui.hide()
        self._GameState.set_visible(False)

    def update(self, gameTime, deltaTime):
        Mode.update(self, gameTime, deltaTime)
        
        if self.showPaths: 
            for entity in self._GameState._Entities.get_unsafe_list():
                if isinstance(entity, Spawner) and entity.path:
                    entity.path.visualize()
        
        if self._CurrentPath:
            self._CurrentPath.visualize(True)
    
    def on_toggle_paths(self):
        self.showPaths = not self.showPaths
        
    def on_save(self, mapName):
        self.cancel_all()
        self.get_gamestate().save_map(mapName)
        
    def on_play(self, mapName):
        self.on_save
    
    def on_load(self, mapName):
        self.cancel_all()
        if self._GameState: self._GameState.delete()
        self._GameState = GameState()
        self._GameState.load_map(mapName)
        self._Gui.mapNameInput.set_text(mapName)
    
    def set_gamestate(self, gamestate):
        self._GameState = gamestate
        
    def get_gamestate(self):
        return self._GameState
    
    def any_mode_active(self):
        return self._CurrentBuild or self._CurrentPath
        
    def cancel_all(self):
        self.cancel_build()
        self.finish_path()
        
    def cancel_build(self):
        if not self._CurrentBuild: return
        self._LastBuildRotation = self._CurrentBuild.get_rotation()
        self._LastBuildConstructor = None
        self._CurrentBuild.delete()
        self._CurrentBuild = None
    
    def finish_build(self):
        if not self._CurrentBuild: return
        self._LastBuildRotation = self._CurrentBuild.get_rotation()
        self._CurrentBuild = None
        if self._LastBuildConstructor:
            self.on_build_new(self._LastBuildConstructor)
        
    def on_mouse_motion(self, x, y, dx, dy, buttons, modifiers):
        self._LastMouse = Vector2(x, y)
        if self._CurrentBuild:
            self.build_on_mouse_motion(Vector2(x, y))
        elif self._CurrentPath:
            self.path_on_mouse_motion(Vector2(x, y))
        elif not self.any_mode_active():
            entity = self._GameState.get_entity_at(Vector2(x, y))
            self.entity_set_highlight(entity)
    
    def build_on_mouse_motion(self, position):
        if self._app.keyMap.is_pressed(key.SPACE):
            position = self.align_to_grid(position)
        self._CurrentBuild.set_position(position)        
    
    def align_to_grid(self, position):
        grid = 64.0 #math.floor(100.0 * 720.0 / 1080.0)  #66.0
        x = (math.floor(position.x / grid) + 0.5) * grid
        y = (math.floor(position.y / grid) + 0.5) * grid
        return Vector2(x, y)
    
    def entity_set_highlight(self, entity):
        if self._EntityHighlight: self._EntityHighlight.set_highlight(False)
        self._EntityHighlight = entity;
        if self._EntityHighlight: self._EntityHighlight.set_highlight(True)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._CurrentBuild:
            self._CurrentBuild.set_rotation(self._CurrentBuild.get_rotation() + math.copysign(self._RotationStep, scroll_y))
    
    def clamp_to_rotationstep(self, rotation):
        return rotation - (rotation % self._RotationStep)
        
    def on_build_new(self, constructor):
        self.cancel_all()
        self._LastBuildConstructor = constructor
        self._CurrentBuild = constructor()
        self._CurrentBuild.set_position(self._LastMouse)
        if self._CurrentBuild.get_rotation() == 0.0:
            self._CurrentBuild.set_rotation(self.clamp_to_rotationstep(self._LastBuildRotation))

    def on_mouse_release(self, x, y, button, modifiers):
        if self._CurrentBuild:
            if button == mouse.LEFT:
                self.build_on_click_right()
            elif button == mouse.RIGHT:
                self.build_on_click()
        elif self._CurrentPath:
            if button == mouse.LEFT:
                self.path_on_click(Vector2(x,y))
            elif button == mouse.RIGHT:
                self.path_on_click_right(Vector2(x,y))
        else:
            entity = self._GameState.get_entity_at(self._LastMouse)
            if button == mouse.LEFT:                
                self.entity_on_click(entity)
            elif button == mouse.RIGHT:
                self.entity_on_click_right(entity)
                
    def on_key_press(self, symbol, modifiers):
        if symbol == key.DELETE:
            if not self.any_mode_active():
                entity = self._GameState.get_entity_at(self._LastMouse)
                if entity: entity.delete()
            elif self._CurrentPath:
                self.path_on_delete()
            elif self._CurrentBuild:
                self.cancel_build()
        elif symbol == key.PAGEUP and self._CurrentBuild and isinstance(self._CurrentBuild, Beauty):
            self._CurrentBuild.set_scale(self._CurrentBuild.get_scale() + 0.10)
        elif symbol == key.PAGEDOWN and self._CurrentBuild and isinstance(self._CurrentBuild, Beauty):
            self._CurrentBuild.set_scale(self._CurrentBuild.get_scale() - 0.10)
        elif symbol == key.ESCAPE:        
            self.cancel_all()
    
    def build_on_click(self):
        return self.cancel_build()

    def build_on_click_right(self):
        return self.finish_build()
    
    def entity_on_click(self, entity):
        self._CurrentBuild = entity
                        
    def entity_on_click_right(self, entity):
        if isinstance(entity, Spawner):
            self.spawner_on_click_right(entity)

    def path_on_mouse_motion(self, position):
        if self._DragWaypoint:
            self._DragWaypoint.set_position(position)
        else:
            waypoint = self.path_get_selected_wp()
            self.path_set_hightlight_waypoint(waypoint)
    
    def path_on_click(self, position):
        waypoint = self.path_get_selected_wp()
        if self._DragWaypoint:
            self._DragWaypoint = None
        elif waypoint:
            self._DragWaypoint = waypoint
        else:
            self._CurrentPath.add_waypoint(Waypoint(position))        
    
    def path_on_click_right(self, position):
        waypoint = self.path_get_selected_wp()
        if waypoint:
            self.path_set_base_waypoint(waypoint)
        else:
            self.finish_path()
            
    def path_set_base_waypoint(self, waypoint):
        self._BaseWaypoint = waypoint
        self._CurrentPath.editBasePoint = waypoint
    
    def path_set_hightlight_waypoint(self, highlight):
        self._CurrentPath.editHighlight = highlight

    def path_on_delete(self):
        waypoint = self.path_get_selected_wp()
        self._CurrentPath.remove_waypoint(waypoint)
        self._CurrentPath.editHighlight = None
        self._CurrentPath.editBasePoint = None
    
    def path_get_selected_wp(self):
        waypoint = self._CurrentPath.get_start()
        nearest = waypoint
        nearestDist = 10000.0        
        while waypoint:
            distance = (self._LastMouse - waypoint.get_position()).get_length()
            if distance < nearestDist: 
                nearest = waypoint
                nearestDist = distance
            waypoint = waypoint.get_neighbour(True)
        
        if nearestDist < 30.0: return nearest
        return None
    
    def spawner_on_click_right(self, entity):
        if not entity.path:
            entity.path = Path()
        self._PathEntity = entity
        self._CurrentPath = entity.path
    
    def finish_path(self):
        if not self._CurrentPath: return
        
        self._CurrentPath.editHighlight = None
        if self._CurrentPath.get_start() == None:
            self._PathEntity.path = None

        self._PathEntity = None
        self._CurrentPath = None
        self.entity_set_highlight(None)
        