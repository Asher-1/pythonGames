'''Simple data loader module.

Loads data files from the "data" directory shipped with a game.

Enhancing this to handle caching etc. is left as an exercise for the reader.
'''

import os
from pyglet import image
from pyglet import media
from pyglet import font
from pyglet.image.atlas import TextureAtlas
from random import Random

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))

_textureCache = {}
_rnd = Random()

def create_default_atlases():
    # Creeps
    create_atlas(512, 512, [ "creep_drunk.png", "creep_fatso.png", "creep_orphan.png" ] )
    create_atlas(512, 512, [ "editlabel_focused.png", "editlabel_unfocused.png", "button_click_00.png", "button_hover_00.png", "button_idle_00.png"  ] )
    create_atlas(1024, 1024, [ "building_beergarden.png", "building_fastfood.png", "building_hq.png", "building_orphanage.png", 
                               "tower_artillery_body.png", "tower_bunker_body.png", "tower_tank_body.png" ] )
    
    create_atlas(512, 512, [ "tower_artillery_tower.png", "tower_bunker_tower.png", "tower_tank_tower.png" ] )
    create_atlas(512, 512, [ "path_corner.png", "path_straight.png", "path_T.png", "path_X.png" ] )
    create_atlas(512, 512, [ "deco_tree.png", "beam.png", "cursor.png"] )

    create_atlas(256, 256, [ "bullet_cannonball.png", "bullet_gatling.png", "bullet_grenade.png", "smoke.png", "alieny.png"] )

def load_fonts():
    #fullPath = concatpaths(data_dir, "fonts", "Action_Force.ttf")
    font.add_directory(concatpaths(data_dir, "fonts"))

def preload(filename):
    _load_sound(filename, concatpaths(data_dir, "audio", filename+".wav"), False)
    
def load_sounds():
    preload("building_orphanage_01")
    preload("building_orphanage_02")
    preload("building_orphanage_03")
    preload("building_orphanage_04")
    preload("building_orphanage_05")
    preload("building_orphanage_06")
    preload("building_orphanage_07")
    preload("building_orphanage_08")
    preload("building_orphanage_09")
    preload("building_orphanage_10")
    preload("building_orphanage_11")
    preload("building_orphanage_12")
    preload("building_orphanage_13")
    preload("building_orphanage_14")
    
    preload("building_fastfood_01")
    preload("building_fastfood_02")
    preload("building_fastfood_03")
    preload("building_fastfood_04")
    preload("building_fastfood_05")
    preload("building_fastfood_06")
    preload("building_fastfood_07")
    preload("building_fastfood_08")
    preload("building_fastfood_09")
    preload("building_fastfood_10")
    preload("building_fastfood_11")
    preload("building_fastfood_12")
    preload("building_fastfood_13")
    
    preload("building_beergarden_01")
    preload("building_beergarden_02")
    preload("building_beergarden_03")
    preload("building_beergarden_04")
    preload("building_beergarden_05")
    preload("building_beergarden_06")
    preload("building_beergarden_07")
    preload("building_beergarden_08")
    preload("building_beergarden_09")
            
    preload("click_01")
    preload("click_02")
    preload("click_03")
            
    preload("drunk_die")
    preload("drunk_drink_01")
    preload("drunk_drink_02")
    preload("drunk_drink_03")
    preload("fatso_eat_01")
    preload("fatso_eat_02")
    preload("fatso_eat_03")
    preload("fatso_eat_04")
    preload("fatso_eat_05")
    preload("lose")
    preload("orphan_die")
    preload("tower_artillery_shoot")
    preload("tower_bunker_shoot")
    preload("tower_tank_hit_01")
    preload("tower_tank_shoot_01")
    preload("win")
    preload("zonk")
    
    
#class Z_INDICES:
#    BACKGROUND = 0
#    STREETS = 10
#    BUILDING = 12
#    TOWER_BODY = 12
#    CREEP = 13
#    TOWER_BULLET = 14
#    TOWER_GUN = 15
#    TOWER_BULLET_FLY = 16
#    PARTICLES = 17
#    BEAUTY = 18
#    GUI_OVERLAYS = 254
#    GUI_BACK = 255
#    GUI_FRONT = 256
#    GUI_TEXT = 257
    
def create_atlas(width, height, names):
    atlas = TextureAtlas(width, height)
    for name in names:
        image = load_texture(name)
        texture = atlas.add(image)
        _textureCache[name] = texture
    
def get_map_path(mapName):
    return concatpaths("maps", mapName + ".map")
    
def concatpaths(*parts):
    path = ""
    for part in parts:
        path = os.path.join(path, part)
    return path

def cache_check(filename):
    return _textureCache.get(filename)

def cache_add(filename, resource):
    _textureCache[filename] = resource

def _load_sound(filename, fullpath, streaming):
    static = cache_check(filename)
    if static: return static
    audio = media.load(fullpath, streaming=streaming)
    if not streaming: cache_add(filename, audio)
    return audio
    
def _load_texture(filename, fullpath):
    loadedImage = cache_check(filename)
    if loadedImage:
        return loadedImage
    
    loadedImage = image.load(fullpath)
    cache_add(filename, loadedImage)
    return loadedImage

def load_texture(filename):
    path = concatpaths(data_dir, "textures", filename)
    return _load_texture(filename, path)

def load_sound(filename, streaming = False):
    global _rnd
    srchPath = concatpaths(data_dir, "audio")
    tmp_name = filename[:-6]
    sound_list = []
    for f in os.listdir(srchPath):
        if f.startswith(tmp_name):
            sound_list.append(f)
    filename = sound_list[_rnd.randint(0, len(sound_list)-1)]
    variation = filename[:-4]
    path = concatpaths(data_dir, "audio", filename)
    return _load_sound(filename, path, streaming), variation

def load_csv_file(filename):
    path = concatpaths(data_dir, "audio", filename + ".csv")
    return path

def filepath(filename):
    '''Determine the path to a file in the data directory.
    '''
    return os.path.join(data_dir, filename)

def load(filename, mode='rb'):
    '''Open a file in the data directory.

    "mode" is passed as the second arg to open().
    '''
    return open(os.path.join(data_dir, filename), mode)

class SaveData:
    
    classes = None
    
    def __init__(self):
        self.classes = dict()
        
    def __getinitargs__(self):
        return ()
    
    def add_data(self, owner, key, value):
        ownerKey = type(owner).__name__
        sub = self.classes.get(ownerKey)
        if not sub:
            sub = dict()
            self.classes[ownerKey] = sub
        sub[key] = value
    
    def get_data(self, owner, key, default = None):
        ownerKey = type(owner).__name__
        sub = self.classes.get(ownerKey)
        if not sub: return default
        val = sub.get(key)
        if val == None: return default
        return val