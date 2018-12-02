'''
Created on 12.09.2011

@author: Archy
'''

import cPickle
import data
import math
import csv
import sound

from pyglet import event

from modes import Mode
from gui import Gui
from gui import Button

from globals import ARCHETYPE

from math2d import Vector2
from math2d import AARect2d

from renderables import BaseRenderable
from genericpath import exists

from santaslittlehelpers import EntityList

from application import GetApplication

class Entity(BaseRenderable):
    
    _position = Vector2()
    _rotation = 0.0
    _AttachedRenderables = None
    _IsDeleted = False
    _ArcheType = ARCHETYPE.UNKNOWN
    
    _LocalRect = None
    _LocalRectPick = None
    
    _BoundingRadius = -1.0
    _SqBoundingRadius = -1.0
    
    addToGrid = False
    
    def __init__(self):
        self._AttachedRenderables = []
        BaseRenderable.__init__(self, True)
        if GameState.get_main_gamestate():
            GameState.get_main_gamestate().add_entity(self)

    def delete(self):
        if self._IsDeleted:
            print "Deleting object twice!"
            return
        
        self.set_visible(False)
        if GameState.get_main_gamestate():
            GameState.get_main_gamestate().remove_entity(self)
        
        for renderable, _ in self._AttachedRenderables:
            renderable.delete()
        self._AttachedRenderables[:] = []
        self._IsDeleted = True
    
    def update_grid_pos(self):
        GameState.get_main_gamestate().entity_pos_changed(self, self.get_position())
        
    def remove_from_grid(self):
        if not self.addToGrid: return
        self.addToGrid = False
        GameState.get_main_gamestate().remove_from_grid(self)
    
    def is_deleted(self):
        return self._IsDeleted
    
    def is_archetype(self, archetype):
        return self._ArcheType == archetype
    
    def get_archetype(self):
        return self._ArcheType
    
    def __getstate__(self):
        state = BaseRenderable.__getstate__(self)
        state.add_data(self, "_position", self._position)
        state.add_data(self, "_rotation", self._rotation)
        return state
    
    def __setstate__(self, state):
        BaseRenderable.__setstate__(self, state)
        self.set_position(state.get_data(self, "_position"))
        self.set_rotation(state.get_data(self, "_rotation", 0.0))
    
    def add_renderable(self, renderable, pickable=True):
        self._clear_bound_cache()
        self._AttachedRenderables.append((renderable, pickable))
        return renderable
    
    def remove_renderable(self, renderable):
        self._clear_bound_cache()
        for index, entry in enumerate(self._AttachedRenderables):
            attached, _ = entry
            if attached == renderable:
                self._AttachedRenderables.pop(index)
                break
        
    def _register_render(self):
        BaseRenderable._register_render(self)
        
        # TODO: maintain visibility of attachable eg: if not visible it should 
        #       not be made visible when parent is made visible
        for renderable, _ in self._AttachedRenderables:
            renderable.set_visible(True)
        
    def _unregister_render(self):
        BaseRenderable._unregister_render(self)

        # TODO: maintain visibility of attachable eg: if not visible it should 
        #       not be made visible when parent is made visible        
        for renderable, _ in self._AttachedRenderables:
            renderable.set_visible(False)
            
    def set_position(self, position):
        self._position = Vector2(position)
        
    def get_position(self):
        return self._position
    
    def set_rotation(self, rotation):
        self._rotation = rotation
        
    def get_rotation(self):
        return self._rotation
    
    def get_rect_local(self, pickable=True):
        if pickable and self._LocalRectPick: return self._LocalRectPick
        elif self._LocalRect: return self._LocalRect
        
        rect = AARect2d()
        for renderable, isPickable in self._AttachedRenderables:
            if pickable and isPickable == pickable: 
                rect.integrate(renderable.get_rect_local())
        if pickable: self._LocalRectPick = rect
        else: self._LocalRect = rect
        return rect
    
    def hit_test(self, position):
        return (self._position - position).get_sq_length() <= self.get_sq_bounding_radius()
    
    def _clear_bound_cache(self):
        self._LocalRect = None
        self._LocalRectPick = None
        self._BoundingRadius = -1.0
        self._SqBoundingRadius = -1.0
        
    def get_bounding_radius(self):
        if self._BoundingRadius < 0.0:
            self._update_bounding_radius()
        return self._BoundingRadius
    
    def get_sq_bounding_radius(self):
        if self._BoundingRadius < 0.0:
            self._update_bounding_radius()
        return self._SqBoundingRadius
    
    def _update_bounding_radius(self):
        rect = self.get_rect_local(True)
        self._SqBoundingRadius = (rect.get_size() * 0.5).get_sq_length()
        self._BoundingRadius = math.sqrt(self._SqBoundingRadius)
    
    def get_size(self):
        return self.get_rect_local().get_size()
    
    def update(self, gameTime, deltaTime):
        pass
    
    def is_outside_screen(self, position, rect):
        base = position - rect.minimum
        if base.x >= 1280.0 or base.y >= 720.0:
            return True
        size = rect.get_size()
        if position.x < size.x or position.y < size.y:
            return True
        return False
    
    def set_highlight(self, state):
        for renderable, _ in self._AttachedRenderables:
            renderable.set_highlight(state)

    def is_interactable(self):
        return False
    
    def interact(self):
        pass

class GridCell:
    
    content = None
    _Observers = None
    
    def __init__(self):
        self.content = set()
        self._Observers = []
        
    def add_observer(self, observer):
        self._Observers.append(observer)
        
    def remove_observer(self, observer):
        self._Observers.remove(observer)
        
    def add_entry(self, entry):
        self.content.add(entry)
        for observer in self._Observers:
            observer.on_notify_add(entry)
    
    def remove_entry(self, entry):
        self.content.remove(entry)
        for observer in self._Observers:
            observer.on_notify_remove(entry)

class GridObserver:
    
    cells = None
    sq_radius = 0.0
    position = None
    typeFilter = ARCHETYPE.CREEP
    
    _content = None
    
    def __init__(self, cells, position, radius, typeFilter=ARCHETYPE.CREEP):
        self.cells = cells
        self.sq_radius = radius * radius
        self.position = Vector2(position)
        self.typeFilter = typeFilter
        
        for cell in self.cells:
            cell.add_observer(self)
        
        self._collect_all()
        
    def delete(self):
        for cell in self.cells:
            cell.remove_observer(self)
        
    def content(self):
        for entry in self._content:
            distance = (entry.get_position() - self.position).get_sq_length()
            if distance <= self.sq_radius: 
                yield (distance, entry)

    def content_creep(self):
        for entry in self._content:
            distance = (entry.get_walker_position() - self.position).get_sq_length()
            if distance <= self.sq_radius: 
                yield (distance, entry)

    def on_notify_add(self, entry):
        if entry.is_archetype(self.typeFilter):
            self._content.add(entry)
        
    def on_notify_remove(self, entry):
        if entry.is_archetype(self.typeFilter):
            self._content.remove(entry)
        
    def _collect_all(self):
        self._content = set()
        for cell in self.cells:
            for entry in cell.content:
                if entry.is_archetype(self.typeFilter):
                    self._content.add(entry)


class UniformGrid:
    
    _CellSize = 0.0
    _OneOverCellSize = 0.0
    _Width = 0
    _Height = 0
    _Count = 0
    
    _Cells = None
    
    UPDATE_INTERVAL = 60.0
    distanceOffset = None
    
    def __init__(self):
        # must be multiple of grid dimension (64) to make point sampled paths possible because all objects are only added by center
        self.create_grid(1280.0, 720.0, 2.0*64.0)
    
    def create_grid(self, width, height, size):
        self._CellSize = size
        self._OneOverCellSize = 1.0 / self._CellSize
        self._Width = int(math.ceil(width / size))
        self._Height = int(math.ceil(height / size))
        self._Count = self._Width * self._Height
        self._Cells = [[GridCell() for _ in range(self._Height)] for _ in range(self._Width)]
        self.distanceOffset = self.UPDATE_INTERVAL * self._OneOverCellSize + 0.5  
        
    def add_entry(self, entry):
        self._add_entry(self._get_index_no_check(entry.get_position()), entry)
    
    def remove_entry(self, entry):
        self._remove_entry(entry._GridIndex, entry)
    
    def move_entry(self, entry, position):
        index = self._get_index_no_check(position)
        if entry._GridIndex != index:
            self._remove_entry(entry._GridIndex, entry)
            self._add_entry(index, entry)
    
    def entities_at(self, position):
        x, y = self._get_index_no_check(position)
        for entity in self._Cells[x][y].content:
            yield entity
        
    def get_grid_observer(self, position, radius):
        celldist = int(math.ceil(radius * self._OneOverCellSize + self.distanceOffset))   
        startX, startY = self._get_index_no_check(position)
        endX = min(startX+celldist, self._Width)
        endY = min(startY+celldist, self._Height)
        startX = max(startX-celldist, 0)
        startY = max(startY-celldist, 0)
        
        cells = []
        for x, y in [(x,y) for x in range(startX, endX) for y in range(startY, endY)]:
            cells.append(self._Cells[x][y])
        return GridObserver(cells, position, radius)
    
    def _remove_entry(self, index, entry):
        self._Cells[index[0]][index[1]].remove_entry(entry)
    
    def _add_entry(self, index, entry):
        self._Cells[index[0]][index[1]].add_entry(entry)
        entry._GridIndex = index
    
    def _get_index(self, position):
        cellx = min(self._Width-1, max(0, int(math.floor(position.x * self._OneOverCellSize))))
        celly = min(self._Height-1, max(0, int(math.floor(position.y * self._OneOverCellSize))))
        return cellx, celly 
    
    def _get_index_no_check(self, position):
        cellx = int(math.floor(position.x * self._OneOverCellSize))
        celly = int(math.floor(position.y * self._OneOverCellSize))
        return cellx, celly
        

class GameState(event.EventDispatcher):
    
    _Entities = None
    _Hidden = None
    _sound_settings = None
    
    mainGameState = None
    
    _InputProvider = None
    
    _Selected = None
    _LastMousePosition = Vector2(0.0, 0.0)
    _Grid = None 
    _successfullCreeps = None
    _livingCreeps = 0
    _building_clicks = 0
    _still_can_loose = True
    
    _MapName = None
    
    LevelSettings = None
    
    def __init__(self):
        self._Entities = EntityList()
        self._Hidden = []
        self._successfullCreeps = {"ALL":0, "DRUNK":0, "ORPHAN":0, "FATSO":0}
        self.LevelSettings = {}
        self._livingCreeps = 0
        self._building_clicks = 0
        _still_can_loose = True
        self.set_visible(True)  
    
    def delete(self):
        self.clear()
        
    def update_spartial_assignment(self):
        pass
    
    def get_map_name(self):
        return self._MapName
    
    @staticmethod    
    def get_main_gamestate():
        return GameState.mainGameState
        
    def clear(self):
        activeGameState = GameState.get_main_gamestate()
        self.set_visible(True)
        
        # theoretically entities could spawn other entities in delete (eg particle) which they should not
        # but this way it should work  
        while len(self._Entities.get_unsafe_list()):
            for entity in self._Entities.get_safe_list():
                entity.delete()
                
        self._Entities.clear()
        self._Hidden = []
        self._Grid = UniformGrid()
        
        self.set_visible(False)
        if activeGameState and activeGameState != self:
            activeGameState.set_visible(True)
    
    def set_visible(self, status):
        self.clear_input()
        if status:
            GameState.mainGameState = self
            self._show_all()
        else:
            GameState.mainGameState = None
            self._hide_all()
        
    def _hide_all(self):
        for entity in self._Entities.get_unsafe_list():
            if entity.is_visible():
                entity.set_visible(False)
                self._Hidden.append(entity)
    
    def _show_all(self):
        for entity in self._Hidden:
            entity.set_visible(True)
        self._Hidden[:] = []
    
    def add_entity(self, entity):
        self._Entities.add_item(entity)
        if entity.addToGrid:
            self._Grid.add_entry(entity)
        return entity
        
    def remove_entity(self, entity):
        self._Entities.remove_item(entity)
        if entity.addToGrid:
            self._Grid.remove_entry(entity)
        
    def entity_pos_changed(self, entity, position):
        self._Grid.move_entry(entity, position)
    
    def remove_from_grid(self, entity):
        self._Grid.remove_entry(entity)
    
    def get_entity_at(self, position):
        for entity in self._Entities.get_unsafe_list():
            if entity.hit_test(position): return entity
        return None
    
    def entities_at(self, position):
        for entity in self._Entities.get_unsafe_list():
            if entity.hit_test(position): yield entity
            
    def get_entity_at_grid(self, position, archetype):
        for entity in self._Grid.entities_at(position):
            if entity.is_archetype(archetype) and entity.hit_test(position):
                return entity
            
    def entities_at_grid(self, position, archetype):
        for entity in self._Grid.entities_at(position):
            if entity.is_archetype(archetype) and entity.hit_test(position):
                yield entity
    
    def get_nearest_in_range(self, position, radius, archetype):
        sq_radius = radius * radius 
        bestEntity = None
        bestDistance = 10000.0 ** 2.0
        typeList = self._Entities.get_of_type(archetype)
        for entity in typeList:
            distance = (position - entity.get_position()).get_sq_length()
            if distance <= sq_radius and distance < bestDistance:
                bestEntity = entity
                bestDistance = distance
        return bestEntity
    
    def entities_in_radius(self, position, radius, archetype):
        sq_radius = radius * radius
        typeList = self._Entities.get_of_type(archetype) 
        for entity in typeList:
            distance = (position - entity.get_position()).get_sq_length()
            if distance <= sq_radius: 
                yield (distance, entity)
    
    def get_grid_observer(self, position, radius):
        return self._Grid.get_grid_observer(position, radius)            
    
    def entities_of_type(self, archetype):
        for entity in self._Entities.get_of_type(archetype): yield entity
    
    def update_living_creeps(self, change):
        if change:
            self._livingCreeps += 1
        else:
            self._livingCreeps -= 1
            
    def update_building_clicks(self, change):
        if change:
            self._building_clicks += 1
        else:
            self._building_clicks -= 1
    
    def get_building_clicks(self):
        return self._building_clicks
    
    def get_building_type_clicks(self, value):
        return int(self.LevelSettings[value])
    
    def get_max_building_clicks(self):
        return int(self.LevelSettings["CLICKS"])
    
    def set_success_Creep(self, creepType):
        self._successfullCreeps["ALL"] += 1
        self._livingCreeps -= 1
        if creepType in self._successfullCreeps:
            self._successfullCreeps[creepType] += 1
        else:
            self._successfullCreeps[creepType] = 1
        
        self.check_win()
            
    def check_win(self):
        if ((int(self._successfullCreeps["ALL"]) >= int(self.LevelSettings["ALL"])) and (int(self._successfullCreeps["FATSO"]) >= int(self.LevelSettings["FATSO"])) and (int(self._successfullCreeps["DRUNK"]) >= int(self.LevelSettings["DRUNK"])) and (int(self._successfullCreeps["ORPHAN"]) >= int(self.LevelSettings["ORPHAN"]))):
            self._still_can_loose = False
            return self.dispatch_event('on_game_end', True)            
        
    def update(self, gameTime, deltaTime):
        self.update_picking()
        for entity in self._Entities.get_safe_list():
            entity.update(gameTime, deltaTime)
            
        if (self._building_clicks >= self.get_max_building_clicks() and self._livingCreeps == 0 and self._still_can_loose):
            return self.dispatch_event('on_game_end', False)
            
    def load_map(self, mapName):
        self._MapName = mapName
        return self.load_from_disk(data.get_map_path(mapName))
    
    def save_map(self, mapName):
        self.save_to_disk(data.get_map_path(mapName))
        
    def save_to_disk(self, fileName):
        f = open(fileName, 'wb')
        pick = cPickle.Pickler(f, protocol=0)
        pick.dump(self._Entities.get_unsafe_list())
        f.close()
    
    def load_from_disk(self, fileName):       
        activeGameState = GameState.get_main_gamestate()
        self.clear()
        self.set_visible(True)
        
        fileNameSetting = fileName[:-4] + ".settings"
        self.load_map_settings(fileNameSetting)
        
        if not exists(fileName):
            return False
        
        f = open(fileName, 'rb')
        pick = cPickle.Unpickler(f)
        
        # entities are fully reconstructed and add themselve to the entities list
        self._Entities.clear()
        _ = pick.load()

        f.close()
        
        if activeGameState != self:
            self.set_visible(False)
            if activeGameState: activeGameState.set_visible(True)
        return True
    
    def load_map_settings(self, fileName):
        try:
            my_settings = csv.reader(open(fileName, "r"), delimiter=";")
        except:
            my_settings = csv.reader(open(data.concatpaths("maps", "default.settings"), "r"), delimiter=";")
            
        for _line in my_settings:
            self.LevelSettings[_line[0].replace("\"", "")] = _line[1].replace("\"", "")
            
    def update_picking(self):
        # todo: replace by grid method
        for entity in self.entities_at(self._LastMousePosition):
            if entity.is_interactable() or entity.is_archetype(ARCHETYPE.TOWER): 
                self.set_highlight(entity)
                break
        else:
            self.set_highlight(None)
    
    #highlighted = []
    #observer = None
    #def gridtest(self):
    #    for entity in self.highlighted:
    #        entity.set_highlight(False)
    #   
    #    self.highlighted = []
    #    
    #    self.observer = self._Grid.get_grid_observer(self._LastMousePosition, 100)  
    #    for _, entity in self.observer.content():
    #        entity.set_highlight(True)
    #        self.highlighted.append(entity)
    
    def set_highlight(self, entity):
        if self._Selected == entity: return
        if self._Selected: 
            self.set_entity_highlight(self._Selected, False)
            GetApplication().cursor.rotationSpeed = 50.0
        self._Selected = entity
        if self._Selected: 
            self.set_entity_highlight(self._Selected, True)
            GetApplication().cursor.rotationSpeed = 220.0
    
    def set_entity_highlight(self, entity, state):
        if entity.is_interactable():
            entity.set_highlight(state)
        elif entity.is_archetype(ARCHETYPE.TOWER):
            entity.show_radius(state)
    
    def clear_input(self):
        self.set_highlight(None)
    
    def register_input(self, provider):
        if provider == self._InputProvider: return        
        self.clear_input()
        if self._InputProvider: self._InputProvider.remove_handlers(self)
        self._InputProvider = provider 
        if self._InputProvider: self._InputProvider.push_handlers(self)
    
    def on_mouse_motion(self, x, y, dx, dy, buttons, modifiers):
        self._LastMousePosition = Vector2(x, y)
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self._Selected:
            self._Selected.interact()

GameState.register_event_type('on_game_end')


class Game(Mode):
    
    _GameGui = None
    _EndGameGui = None
    _GameState = None
    
    def __init__(self, application):
        Mode.__init__(self, application)
        self._GameGui = GameGui(self._app)
        self._GameGui.hide()

    def enter(self):
        Mode.enter(self)        
        self.activate_game()
    
    def leave(self):
        Mode.leave(self)        
        self.deactivate_game()
            
    def update(self, gameTime, deltaTime):
        Mode.update(self, gameTime, deltaTime)
        if self._EndGameGui:
            pass
        else:
            if self._GameState:
                self._GameState.update(gameTime, deltaTime)
                
                clicksleft = max(0, self._GameState.get_max_building_clicks() - self._GameState.get_building_clicks())
                self._GameGui.update_click_label(clicksleft)
                to_win_fatso = max(0, int(self._GameState.LevelSettings["FATSO"]) - int(self._GameState._successfullCreeps["FATSO"]))
                to_win_drunk = max(0, int(self._GameState.LevelSettings["DRUNK"]) - int(self._GameState._successfullCreeps["DRUNK"]))
                to_win_orphan = max(0, int(self._GameState.LevelSettings["ORPHAN"]) - int(self._GameState._successfullCreeps["ORPHAN"]))
                self._GameGui.update_all_label(to_win_fatso, to_win_drunk, to_win_orphan)        
    
    def load_map(self, mapName):
        if self._GameState: self._GameState.delete()
        self._GameState = GameState()
        if self._GameState.load_map(mapName):
            self.activate_game()
            return True
        return False
        
    def show_edit_button(self, visible):
        self._GameGui.show_edit_button(visible)
    
    def activate_game(self):
        if self._GameState: 
            self._GameState.set_visible(True)
            self._GameState.register_input(self._app)
            self._GameState.push_handlers(self)
        
            self._GameGui.show()        
            self._GameGui.reset_labels()        
            txt1 = str(self._GameState.LevelSettings["1"])
            txt2 = str(self._GameState.LevelSettings["2"])
            txt3 = str(self._GameState.LevelSettings["3"])
            txt4 = str(self._GameState.LevelSettings["4"])
            txt5 = str(self._GameState.LevelSettings["5"])
            txt6 = str(self._GameState.LevelSettings["6"])
            txt7 = str(self._GameState.LevelSettings["7"])
            txt8 = str(self._GameState.LevelSettings["8"])
            self._GameGui.set_story_labels(txt1, txt2, txt3, txt4, txt5, txt6, txt7, txt8)        
            txt1 = str(self._GameState.LevelSettings["CLICKS"])
            txt2 = str(self._GameState.LevelSettings["FATSO"])
            txt3 = str(self._GameState.LevelSettings["DRUNK"])
            txt4 = str(self._GameState.LevelSettings["ORPHAN"])
            self._GameGui.set_winning_conditions(txt1, txt2, txt3, txt4)        
        
    def deactivate_game(self):
        if self._GameState:
            self._GameState.register_input(None)
            self._GameState.set_visible(False)
            self._GameState.remove_handlers(self)
        self._GameGui.hide()
        
        if self._EndGameGui:
            self._EndGameGui.hide()
            self._EndGameGui = None
        
    def on_game_end(self, won):
        if self._GameState: self._GameState.register_input(None)
        if self._EndGameGui:
            self._EndGameGui.hide()
            self._EndGameGui = None
        self._EndGameGui = WinLooseGui(self._app)
        self._EndGameGui.set_won(won)
        self._GameGui.reset_labels()
        self._GameGui.hide()
        
        nextMap = None
        if self._GameState:
            currentMap = self._GameState.get_map_name()
            if not won:
                nextMap = currentMap
            else:
                try:
                    mapNumber = int(currentMap)
                    mapNumber += 1
                    nextMap = str(mapNumber)
                except:
                    pass
        
        self._EndGameGui.set_next_map(nextMap)
        
    def restart(self):
        if self._GameState:
            currentMap = self._GameState.get_map_name()
            self._app.start_map(currentMap)


from gui import Label

class GameGui(Gui):

    editButton = None
    _state_label_story_1 = None
    _state_label_story_2 = None
    _state_label_story_3 = None
    _state_label_story_4 = None
    _state_label_story_5 = None
    _state_label_story_6 = None
    _state_label_story_7 = None
    _state_label_story_8 = None
    
    _state_label_need = None
    _state_label_need_fatso = None
    _state_label_need_drunk = None
    _state_label_need_orphan = None
    _state_label_clicks_left = None
    
    def __init__(self, application):
        Gui.__init__(self, application)
        
        self._BackGround = self.add_element(BackgroundBox(Vector2(1180, 360), Vector2(190, 710), (0.0, 0.0, 0.0)))
        
        self.add_element(Button(Vector2(1105, 670), Vector2(150, 25), "MainMenu", lambda:self.on_mainmenu()))
        self.editButton = self.add_element(Button(Vector2(1105, 640), Vector2(150, 25), "Restart", lambda:self.on_restart()))
        self.editButton = self.add_element(Button(Vector2(1105, 610), Vector2(150, 25), "Edit", lambda:self.on_edit()))
        
        self._state_label_story_1 = self.add_element(Label(Vector2(1100, 600), Vector2(180, 20), "",)).set_text_color(1.0, 1.0, 1.0)
        self._state_label_story_2 = self.add_element(Label(Vector2(1100, 560), Vector2(180, 20), "",)).set_text_color(1.0, 1.0, 1.0)
        self._state_label_story_3 = self.add_element(Label(Vector2(1100, 535), Vector2(180, 20), "",)).set_text_color(1.0, 1.0, 1.0)
        self._state_label_story_4 = self.add_element(Label(Vector2(1100, 510), Vector2(180, 20), "",)).set_text_color(1.0, 1.0, 1.0)
        self._state_label_story_5 = self.add_element(Label(Vector2(1100, 485), Vector2(180, 20), "",)).set_text_color(1.0, 1.0, 1.0)
        self._state_label_story_6 = self.add_element(Label(Vector2(1100, 460), Vector2(180, 20), "",)).set_text_color(1.0, 1.0, 1.0)
        self._state_label_story_7 = self.add_element(Label(Vector2(1100, 435), Vector2(180, 20), "",)).set_text_color(1.0, 1.0, 1.0)
        self._state_label_story_8 = self.add_element(Label(Vector2(1100, 410), Vector2(180, 20), "",)).set_text_color(1.0, 1.0, 1.0)
        
        self._state_label_clicks_left = self.add_element(Label(Vector2(1100, 370), Vector2(150, 20), "")).set_text_color(1.0, 1.0, 1.0)
        
        self._state_label_need = self.add_element(Label(Vector2(1100, 345), Vector2(150, 20), "",)).set_text_color(1.0, 1.0, 1.0)
        self._state_label_need_fatso = self.add_element(Label(Vector2(1100, 320), Vector2(150, 20), "",)).set_text_color(1.0, 1.0, 1.0)
        self._state_label_need_drunk = self.add_element(Label(Vector2(1100, 295), Vector2(150, 20), "",)).set_text_color(1.0, 1.0, 1.0)
        self._state_label_need_orphan = self.add_element(Label(Vector2(1100, 270), Vector2(150, 20), "",)).set_text_color(1.0, 1.0, 1.0)
        
    
    def show_edit_button(self, visible):
        self.editButton.set_visible(visible)
        
    def on_mainmenu(self):
        self._app.set_mode('MainMenu')
        
    def on_edit(self):
        self._app.set_mode('Edit')
        
    def on_restart(self):
        self._app.restart_map()
        
    def update_click_label(self, clicks):
        self._state_label_clicks_left.set_text("Left: " + str(clicks))
        
    def update_all_label(self, txt1, txt2, txt3):
        self._state_label_need.set_text("HQ Need:")
        self._state_label_need_fatso.set_text("Fatso: " + str(txt1))
        self._state_label_need_drunk.set_text("Drunk: " + str(txt2))
        self._state_label_need_orphan.set_text("Orphan: " + str(txt3))
        
    def set_story_labels(self, txt1, txt2, txt3, txt4, txt5, txt6, txt7, txt8):
        self._state_label_story_1.set_text(txt1)
        self._state_label_story_2.set_text(txt2)
        self._state_label_story_3.set_text(txt3)
        self._state_label_story_4.set_text(txt4)
        self._state_label_story_5.set_text(txt5)
        self._state_label_story_6.set_text(txt6)
        self._state_label_story_7.set_text(txt7)
        self._state_label_story_8.set_text(txt8)
        
    def set_winning_conditions(self, txt1, txt2, txt3, txt4):
        self._state_label_clicks_left.set_text("Left: " + txt1)
        self._state_label_need.set_text("HQ Need:")
        self._state_label_need_fatso.set_text("Fatso: " + str(txt2))
        self._state_label_need_drunk.set_text("Drunk: " + str(txt3))
        self._state_label_need_orphan.set_text("Orphan: " + str(txt4))
        
    def reset_labels(self):
        self._state_label_story_1.set_text("")
        self._state_label_story_2.set_text("")
        self._state_label_story_3.set_text("")
        self._state_label_story_4.set_text("")
        self._state_label_story_5.set_text("")
        self._state_label_story_6.set_text("")
        self._state_label_story_7.set_text("")
        self._state_label_story_8.set_text("")
        self._state_label_need.set_text("")
        self._state_label_need_fatso.set_text("")
        self._state_label_need_drunk.set_text("")
        self._state_label_need_orphan.set_text("")
        self._state_label_clicks_left.set_text("")
        

from gui import BackgroundBox

class WinLooseGui(Gui):
    
    _BackGround = None
    _Label = None
    _NextMap = None
    _Button = None
    
    def __init__(self, application):
        Gui.__init__(self, application)
        
        self._BackGround = self.add_element(BackgroundBox(Vector2(640, 410), Vector2(400, 270), (0.0, 0.0, 0.0)))
        self._Label = self.add_element(Label(Vector2(640, 500), Vector2(350, 60), "You Won"))
        self._Label.set_text_anchor("center", "center")
        self._Button = self.add_element(Button(Vector2(640-175, 300), Vector2(350, 60), "Okay", lambda:self.on_okay()))
        
    def _update_label_text(self):
        if self._Won: 
            self._Label.set_text("You won")
            self._Button.set_text("Next")
            self._Label.set_text_color(0.0, 1.0, 0.25)
            self._BackGround.set_color(0.1, 0.2, 0.1)
            sound.play_sound("win")
        else: 
            self._Label.set_text("You lost")
            self._Button.set_text("Restart")
            self._Label.set_text_color(0.7, 0.1, 0.1)
            self._BackGround.set_color(0.75, 0.0, 0.0)
            sound.play_sound("lose")
        
    def set_won(self, state):
        self._Won = state
        self._update_label_text()
    
    def set_next_map(self, name):
        self._NextMap = name
        
    def on_okay(self):
        if self._NextMap:
            self._app.start_map(self._NextMap)
        else:
            self._app.set_mode("MainMenu")

