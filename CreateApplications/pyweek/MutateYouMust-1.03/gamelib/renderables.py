'''
Created on 11.09.2011

'''

from application import GetApplication

import data 
import pyglet.sprite
import math 

from pyglet import gl
from pyglet import graphics
from math2d import Vector2
from math2d import AARect2d

zLayers = {0:pyglet.graphics.OrderedGroup(0)}

def get_zlayer(z_index):
    global zLayers
    group = zLayers.get(z_index)
    if group == None:
        group = pyglet.graphics.OrderedGroup(z_index)
        zLayers[z_index] = group
    return group

class DebugRenderGroup(graphics.Group):
    
    def set_state(self):
        graphics.Group.set_state(self)
        gl.glLineWidth(3.0)
        gl.glPointSize(6)
        gl.glColor3f(0.0, 0.0, 1.0)
        
    def unset_state(self):
        graphics.Group.unset_state(self)        
        gl.glLineWidth(1.0)
        gl.glPointSize(1.0)
        gl.glColor3f(1.0, 1.0, 1.0)
        
debugRenderGroup = DebugRenderGroup()
        
class BaseRenderable:
    
    __visible = True
    __renderCallback = False
    
    def __init__(self, renderCallback=True):
        self.__renderCallback = renderCallback
        self.__visible = True
        if self.__visible:
            self._register_render()
    
    def __getinitargs__(self):
        return ()
    
    def __getstate__(self):
        state = data.SaveData()
        state.add_data(self, "__visible", self.__visible)
        state.add_data(self, "__renderCallback", self.__renderCallback)
        return state
    
    def __setstate__(self, state):
        self.__renderCallback = state.get_data(self, "__renderCallback")
        self.set_visible(state.get_data(self, "__visible"))
    
    def _set_rendercallback(self, state):
        if self.__renderCallback == state: return
        
        if self.__visible: self._unregister_render()
        self.__renderCallback = state
        if self.__visible: self._register_render()
        
    def delete(self):
        self.set_visible(False)
        
    def is_visible(self):
        return self.__visible
    
    def set_visible(self, visible):
        if self.__visible == visible:
            return
        self.__visible = visible
        if self.__visible:
            self._register_render()
        else:
            self._unregister_render()
        
    def _register_render(self):
        if self.__renderCallback:
            GetApplication().add_renderable(self)
    
    def _unregister_render(self):
        if self.__renderCallback:
            GetApplication().remove_renderable(self)
    
    def set_highlight(self, state):
        pass
    
    def render(self, gameTime, deltaTime):
        pass
    
    def get_size(self):
        pass

class BatchRenderer(BaseRenderable):
    
    _batch = None
    _dirtySpritesPosition = None
        
    _MainRenderBatch = None
    
    def __init__(self, renderCallback=False):
        BaseRenderable.__init__(self, renderCallback=renderCallback)
        
        self._batch = pyglet.graphics.Batch()
        self._dirtySpritesPosition = set()
        
    @staticmethod
    def get_main_renderbatch():
        global mainRenderBatch
        return mainRenderBatch
    
    @staticmethod
    def set_main_renderbatch(batch):
        global mainRenderBatch
        mainRenderBatch = batch
                
    def get_batch(self):
        return self._batch
    
    def render(self, gameTime, deltaTime):
        self._update_dirty()
        self._batch.draw()
    
    def _update_dirty(self):
        for sprite in self._dirtySpritesPosition:
            if not sprite.is_deleted():
                sprite.update_dirty_position()
        self._dirtySpritesPosition.clear()
    
    def set_dirty_sprite_position(self, sprite):
        self._dirtySpritesPosition.add(sprite)
            

class FastSprite(pyglet.sprite.Sprite):    
    
    _IsDeleted = False
    _batchRenderer = None
    
    _size = None
    _wasScaled = False
    
    _anchor = Vector2(0.0, 0.0)
    
    BASE_SCALE = Vector2(1280.0 / 1920.0, 720.0 / 1080.0) * 0.5
    
    def __init__(self, batchRenderer,
        img, x=0.0, y=0.0,
        blend_src=gl.GL_SRC_ALPHA,
        blend_dest=gl.GL_ONE_MINUS_SRC_ALPHA,
        group=None,
        usage='dynamic'):
        self._batchRenderer = batchRenderer
        
        if batchRenderer: batch = batchRenderer.get_batch()
        else: batch = None
        pyglet.sprite.Sprite.__init__(self, img, x=x, y=y, blend_src=blend_src, blend_dest=blend_dest, batch=batch, group=group, usage=usage)
    
    def delete(self):
        pyglet.sprite.Sprite.delete(self)
        self._IsDeleted = True
    
    def is_deleted(self):
        return self._IsDeleted
    
    def _set_visible(self, visible):
        if self.visible == visible:
            return
        if visible:
            self.batch = self._batchRenderer.get_batch()
        else:
            self.batch = None
            
        pyglet.sprite.Sprite._set_visible(self, visible)
    
    def set_anchor(self, fracX, fracY):
        self._anchor = Vector2(fracX, fracY)
        self._update_position()
    
    def get_anchor(self):
        return self._anchor
    
    def _set_texture(self, texture):
        reapplyScale = self._wasScaled 
        if reapplyScale:
            orgSize = self._texture.width * FastSprite.BASE_SCALE.x
            currentSize = self.get_size().x
            scale = currentSize / orgSize
        pyglet.sprite.Sprite._set_texture(self, texture)
        if reapplyScale: self.set_scale(scale)
            
    def set_scale(self, scale):
        orgSize = Vector2(self._texture.width * FastSprite.BASE_SCALE.x, self._texture.height * FastSprite.BASE_SCALE.y)
        self.set_size(orgSize * scale)
        self._wasScaled = scale != 1.0
        
    def set_size(self, size):
        self._size = size
        self._wasScaled = False
        self._update_position()
        
    def get_size(self):
        if self._size:
            return self._size
        else:
            return Vector2(self._texture.width * FastSprite.BASE_SCALE.x, self._texture.height * FastSprite.BASE_SCALE.y)
            
    def _update_position(self):
        if self._batchRenderer:
            self._batchRenderer.set_dirty_sprite_position(self)
        else:
            pyglet.sprite.Sprite._update_position(self)
        
    def _create_vertex_list(self):
        if self._batch is None:
            self._vertex_list = graphics.vertex_list(4,
                'v2f/%s' % self._usage,
                'c4B', ('t3f', self._texture.tex_coords))
        else:
            self._vertex_list = self._batch.add(4, gl.GL_QUADS, self._group,
                'v2f/%s' % self._usage,
                'c4B', ('t3f', self._texture.tex_coords))
        self._update_position()
        self._update_color()

    def update_dirty_position(self):
        size = self.get_size()
        anchor = self._anchor * size
        if not self._visible:
            self._vertex_list.vertices[:] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        elif self._rotation:
            x1 = -anchor.x * self._scale
            y1 = -anchor.y * self._scale
            x2 = x1 + size.x * self._scale
            y2 = y1 + size.y * self._scale
            x = self._x
            y = self._y

            r = -math.radians(self._rotation)
            cr = math.cos(r)
            sr = math.sin(r)
            ax = x1 * cr - y1 * sr + x
            ay = x1 * sr + y1 * cr + y
            bx = x2 * cr - y1 * sr + x
            by = x2 * sr + y1 * cr + y
            cx = x2 * cr - y2 * sr + x
            cy = x2 * sr + y2 * cr + y
            dx = x1 * cr - y2 * sr + x
            dy = x1 * sr + y2 * cr + y

            self._vertex_list.vertices[:] = [ax, ay, bx, by, cx, cy, dx, dy]
        elif self._scale != 1.0:
            x1 = self._x - anchor.x * self._scale
            y1 = self._y - anchor.y * self._scale
            x2 = x1 + size.x * self._scale
            y2 = y1 + size.y * self._scale
            self._vertex_list.vertices[:] = [x1, y1, x2, y1, x2, y2, x1, y2]
        else:
            x1 = self._x - anchor.x
            y1 = self._y - anchor.y
            x2 = x1 + size.x
            y2 = y1 + size.y
            self._vertex_list.vertices[:] = [x1, y1, x2, y1, x2, y2, x1, y2]

class Sprite(BaseRenderable):
    
    _sprite = None
    _LocalRect = None
    
    def __init__(self, renderCallback=False):
        BaseRenderable.__init__(self, renderCallback=renderCallback)
        self._prepare_sprite()        
        
    def delete(self):
        BaseRenderable.delete(self)
        self._sprite.delete()
    
    def set_highlight(self, state):
        if state: self._sprite.color = (128, 128, 128)
        else: self._sprite.color = (255, 255, 255)
        
    def _prepare_sprite(self):
        if not self._sprite:
            self._sprite = FastSprite(BatchRenderer.get_main_renderbatch(), data.load_texture("transparent.png"),
                                      blend_src=gl.GL_SRC_ALPHA,
                                      blend_dest=gl.GL_ONE_MINUS_SRC_ALPHA,
                                      group=get_zlayer(0))
            self._sprite.set_anchor(0.5, 0.5)
            self._sprite.visible = self.is_visible()
            
    def _register_render(self):
        BaseRenderable._register_render(self)
        self._prepare_sprite()            
        self._sprite.visible = True
    
    def _unregister_render(self):
        BaseRenderable._unregister_render(self)
        self._sprite.visible = False
    
    def set_size(self, size):
        self._LocalRect = None
        self._sprite.set_size(size)
    
    def get_size(self):
        return self._sprite.get_size()
    
    def get_org_size(self):
        return Vector2(self._sprite.image.width, self._sprite.image.height)
    
    # TODO: include rotation
    def get_rect_local(self):
        if self._LocalRect: return self._LocalRect
        size = self.get_size()
        minimum = Vector2(size.x * -self._sprite.get_anchor().x, size.x * -self._sprite.get_anchor().x)
        maximum = Vector2(size.x * (1.0 - self._sprite.get_anchor().x), size.x * (1.0 - self._sprite.get_anchor().x))
        self._LocalRect = AARect2d(minimum, maximum)
        return self._LocalRect
    
    def get_position(self):
        return Vector2(*self._sprite.position)
        
    def set_position(self, position):
        self._sprite.position = position.to_tuple()
            
    def set_z_index(self, z_index):
        newGroup = get_zlayer(z_index)
        if self._sprite.group != newGroup:
            self._sprite.group = newGroup
        
    def get_rotation(self):
        return self._sprite.rotation
    
    def set_rotation(self, rotation):
        self._sprite.rotation = rotation
    
    def set_scale(self, scale):
        self._LocalRect = None
        self._sprite.set_scale(scale)
        
    def set_texture(self, texture):
        self._sprite.image = texture
        
    def set_anchor(self, fracX, fracY):
        self._LocalRect = None
        self._sprite.set_anchor(fracX, fracY)
        
    def set_color(self, *color):
        self._sprite.color = map(lambda c: c*255.0, color)
        
    def set_alpha(self, alpha):
        self._sprite.opacity = int(alpha * 255.0)


class AnimatedSprite(Sprite):    
    
    fps = 30
    
    _Textures = None
    _StartTime = -1
    _LastTexture = -1
    _FirstRender = True
    _FirstRun = True    
    
    def __init__(self):
        Sprite.__init__(self, False)        
        self._Textures = []
    
    def set_animation(self, textures, fps=30.0):
        self.fps = fps
        self._Textures = textures
        self._StartTime = -1
        self._LastTexture = -1
        self._FirstRender = True
        self._FirstRun = True
        
        self._set_rendercallback(True)
        
        if len(self._Textures) == 0:
            self._set_rendercallback(False)
        else:
            self._set_rendercallback(True)
        
    def on_animation_end(self):
        pass
    
    def render(self, gameTime, deltaTime):
        if self._FirstRender:
            if self._StartTime < 0: 
                self._StartTime = gameTime
            self._FirstRender = False
        
        frame = int(float(gameTime - self._StartTime) * self.fps)
        if self._FirstRun and frame >= len(self._Textures):
            self.on_animation_end()
            self._FirstRun = False
            if len(self._Textures) == 0:
                self._set_rendercallback(False)
            
        currentTexture = frame % len(self._Textures)
        
        if self._LastTexture != currentTexture:
            self.set_texture(self._Textures[currentTexture])
            self._LastTexture = currentTexture
