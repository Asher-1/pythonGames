'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import pyglet
#pyglet.options['debug_graphics_batch'] = True

instance = None

def GetApplication():
    return instance

import sys
import data
import modes
import edit
import game
import sound

from math2d import Vector2

from pyglet import gl
from pyglet import app
from pyglet import window
from pyglet import graphics
from pyglet import clock
from pyglet import text
from pyglet import event

from globals import Z_INDICES
from renderables import FastSprite
from renderables import BatchRenderer
from renderables import get_zlayer

from santaslittlehelpers import SaferList

from sound import MusicPlayer

from misc import UfoCursor

modeConstructors = { 'MainMenu' : lambda app:modes.MainMenu(app),
                     'Game'     : lambda app:game.Game(app),
                     'Edit'     : lambda app:edit.EditMode(app) }

class Application(event.EventDispatcher):
    
    appName = "Mutate You Must!"
    window = None
    fullScreen = False
    vSync = False
    virtualSize = (1280,720)

    deltaTime = 0
    gameTime = 0
    gameLoop = None
    
    keyMap = None
    
    _CurrentMode = None
    _Modes = None
    _ExitRequested = False
    _Background = None
    
    __ToRender = None
    
    _Mouse_Frame_Pos = Vector2()
    _Mouse_Frame_Delta = Vector2()
    
    music = None

    cursor = None
    
    def __init__(self):
        global instance
        instance = self
        
        self.read_options()
    
        self._Modes = {}
        self.__ToRender = SaferList()
        
        data.create_default_atlases()        
        data.load_fonts()
        data.load_sounds()
        BatchRenderer.set_main_renderbatch(BatchRenderer())

        self.create_window()
        clock.set_fps_limit(None)
        self.gameLoop = GameLoop()
        self.keyMap = KeyMap(self)
        
        self.create_modes()
        self.window.set_background(data.load_texture("background.jpg"))
        
        texture = data.load_texture("cursor.png")
        self.cursor = UfoCursor(texture)
        self.window.set_mouse_cursor(self.cursor)
        
        sound.read_csv("definitions")
        
        self.music = MusicPlayer()
        self.music.set_music("mutate_music")
        
        self.set_mode('MainMenu')

    def read_options(self):
        for entry in sys.argv:
            if len(entry) > 1:
                if entry == "-f":
                    self.fullScreen = True
                if entry == "-s":
                    sound.no_sound()
                if entry == "-e":
                    sound.no_effects()

    def request_exit(self):
        self._ExitRequested = True
    
    def create_modes(self):
        self._Modes.clear()
        for name in modeConstructors.keys():
            self._Modes[name] = modeConstructors[name](self)
        
    def set_mode(self, modeId):
        mode = self._Modes.get(modeId)
        if self._CurrentMode:
            self._CurrentMode.leave()
        self._CurrentMode = mode
        if self._CurrentMode:
            self._CurrentMode.enter()
        return self._CurrentMode
    
    def start_map(self, mapName, editButton = False):
        gameMode = self.set_mode('Game')
        if not gameMode.load_map(mapName):
            menu = self.set_mode('MainMenu')
            menu.activate_credits()            
        else:
            gameMode.show_edit_button(editButton)        
    
    def restart_map(self):
        mode = self._Modes.get('Game')
        mode.restart()
    
    def run(self):
        self.gameLoop.run()
    
    def add_renderable(self, renderable):
        self.__ToRender.add_item(renderable)
    
    def remove_renderable(self, renderable):
        self.__ToRender.remove_item(renderable)
    
    def dispatch_mouse_move(self):
        x = self._Mouse_Frame_Pos.x
        y = self._Mouse_Frame_Pos.y
        dx = self._Mouse_Frame_Delta.x
        dy = self._Mouse_Frame_Delta.y
        self.dispatch_event('on_mouse_motion', x, y, dx, dy, 0, 0)
        self._Mouse_Frame_Delta = Vector2()
        
    def do_frame(self):
        self.dispatch_mouse_move()
    
        if self._CurrentMode:
            self._CurrentMode.update(self.gameTime, self.deltaTime)
        
        # do all batched rendering before immediate renderings which
        # could be done in __ToRender loop.
        BatchRenderer.get_main_renderbatch().render(self.gameTime, self.deltaTime)
        
        for renderable in self.__ToRender.get_safe_list():
            renderable.render(self.gameTime, self.deltaTime)
        
        self.cursor.update(self.gameTime, self.deltaTime, self._Mouse_Frame_Pos)
        
        if self._ExitRequested:
            self.gameLoop.exit()
    
    def create_window(self):
        template = gl.Config(buffer_size=32, red_size=8, green_size=8, blue_size=8, alpha_size=8,
                             double_buffer=True)
        
        display = window.get_platform().get_default_display()
        screen = display.get_default_screen()
        try:
            glConfig = screen.get_best_config(template)
        except window.NoSuchConfigException:
            print "Failed to get requested bit-depth, will take what I get"
            glConfig = screen.get_best_config()
        
        if self.fullScreen:
            width, height = None, None
        else:
            height = min(720.0, screen.height)
            gameAspect = float(self.virtualSize[0]) / float(self.virtualSize[1])
            width, height = int(height * gameAspect), int(height)
            if width > screen.width:
                width, height = int(width), int(width / gameAspect)
            
        self.window = GameWindow(   self, self.virtualSize, 
                                    width, height, self.appName, 
                                    resizable=True,
                                    fullscreen=self.fullScreen, 
                                    visible=True,
                                    vsync=self.vSync,
                                    config=glConfig)
        
        self.register_handlers()
    
    def set_handler(self, name, handler):
        # fix: calling remove_handler empties the event stack if nothing else is on it.
        #      -> using set_handlers/remove_handlers without pop/pushs does not work
        #      ->-> make sure at least one entry is present
        if type(self._event_stack) is tuple or len(self._event_stack) == 0:
            self._event_stack = [{}]
        event.EventDispatcher.set_handler(self, name, handler)
        
    def register_handlers(self):
        self.window.push_handlers(  on_mouse_press = lambda x,y,button,modifiers: self.win_on_mouse_press(x, y, button, modifiers),
                                    on_mouse_release = lambda x,y,button,modifiers: self.win_on_mouse_release(x, y, button, modifiers),
                                    on_mouse_motion = lambda x,y,dx,dy: self.win_on_mouse_motion(x, y, dx, dy),
                                    on_mouse_drag = lambda x,y,dx,dy,buttons,modifiers: self.win_on_mouse_drag(x, y, dx, dy, buttons, modifiers),
                                    on_mouse_scroll = lambda x,y,scroll_x,scroll_y: self.win_on_mouse_scroll(x, y, scroll_x, scroll_y),
                                    on_key_press = lambda symbol,modifiers: self.win_on_key_press(symbol, modifiers), 
                                    on_key_release = lambda symbol,modifiers: self.win_on_key_release(symbol, modifiers),
                                    on_text = lambda text: self.win_on_text(text),
                                    on_text_motion = lambda motion: self.win_on_text_motion(motion) )
    
    def unregister_handlers(self):
        self.window.pop_handlers()
    
    def convert_window_to_game(self, x, y):
        x = (x - self.window.convertOffset[0]) * self.window.convertScale[0]
        y = (y - self.window.convertOffset[1]) * self.window.convertScale[0]
        return x, y
    
    def win_on_text(self, text):
        return self.dispatch_event('on_text', text)
    
    def win_on_text_motion(self, motion):
        return self.dispatch_event('on_text_motion', motion)
    
    def win_on_mouse_press(self, x, y, button, modifiers):
        x, y = self.convert_window_to_game(x, y)
        return self.dispatch_event('on_mouse_press', x, y, button, modifiers)
    
    def win_on_mouse_release(self, x, y, button, modifiers):
        x, y = self.convert_window_to_game(x, y)
        return self.dispatch_event('on_mouse_release', x, y, button, modifiers)
    
    def win_on_mouse_motion(self, x, y, dx, dy):
        self.win_on_mouse_drag(x, y, dx, dy, 0, 0)
    
    def win_on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x, y = self.convert_window_to_game(x, y)
        dx, dy = self.convert_window_to_game(dx, dy)
        self._Mouse_Frame_Pos = Vector2(x, y)
        self._Mouse_Frame_Delta += Vector2(dx, dy)        
    
    def win_on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        x, y = self.convert_window_to_game(x, y)
        return self.dispatch_event('on_mouse_scroll', x, y, scroll_x, scroll_y)

    def win_on_key_press(self, symbol, modifiers):
        return self.dispatch_event('on_key_press', symbol, modifiers)
    
    def win_on_key_release(self, symbol, modifiers):
        return self.dispatch_event('on_key_release', symbol, modifiers)

Application.register_event_type('on_text')
Application.register_event_type('on_text_motion')
Application.register_event_type('on_mouse_press')
Application.register_event_type('on_mouse_release')
Application.register_event_type('on_mouse_motion')
Application.register_event_type('on_mouse_scroll')
Application.register_event_type('on_key_press')
Application.register_event_type('on_key_release')


class KeyMap:
    
    _app = None
    keyMap = None
    
    def __init__(self, application):
        self.keyMap = {}
        self._app = application
        self._app.push_handlers(self)
        self._app.window.push_handlers( on_deactivate = lambda: self.on_deactivate() )

    def is_pressed(self, symbol):
        pressTime = self.keyMap.get(symbol)
        return pressTime and pressTime > 0
    
    def release_all(self):
        self.keyMap.clear()
        
    def on_deactivate(self):
        self.release_all()
        
    def on_key_press(self, symbol, modifiers):
        self.keyMap[symbol] = self._app.gameTime
    
    def on_key_release(self, symbol, modifiers):
        if self.is_pressed(symbol):
            del(self.keyMap[symbol])
    
    
class GameWindow(window.Window):
    
    convertOffset = (0.0,0.0)
    convertScale = (1.0,1.0)
    
    parentApp = None
    virtualSize = None
    aspect = None
    showFps = False
    
    fpsLabel = None
    
    backgroundColor = (0.0, 0.0, 0.0, 1.0)
    borderColor = (0.0, 0.0, 0.0, 1.0)
    border = (0, 0)

    _BackgroundSprite = None

    def __init__(self, parentApp, virtualSize=(1280,720), width=None, height=None, caption=None, resizable=False, 
                 style=window.Window.WINDOW_STYLE_DEFAULT, fullscreen=False, visible=True, 
                 vsync=True, display=None, screen=None, config=None, context=None):
        window.Window.__init__(self, width=width, height=height, caption=caption, resizable=resizable, 
                               style=style, fullscreen=fullscreen, visible=visible, 
                               vsync=vsync, display=display, screen=screen, config=config, context=context)
        self.parentApp = parentApp
        self.virtualSize = virtualSize
        self.aspect = float(self.virtualSize[0]) / float(self.virtualSize[1])
        self.set_default_states()
    
    def set_background(self, texture):
        self._BackgroundSprite = FastSprite(BatchRenderer.get_main_renderbatch(), texture, 0.0, 0.0, group=get_zlayer(Z_INDICES.BACKGROUND))
        self._BackgroundSprite.set_size(Vector2(1280, 720))
        
    def on_draw(self):
        self.clear()
        self.parentApp.do_frame()        
        
        if self.showFps:
            self.draw_fps()
            
    def clear(self):
        gl.glClear(gl.GL_STENCIL_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        if self._BackgroundSprite:
            pass
        else:
            gl.glColor4f(*self.backgroundColor)
            graphics.draw(4, gl.GL_QUADS, ("v2f", ( 0.0,                  0.0,
                                                    self.virtualSize[0],  0.0,                  
                                                    self.virtualSize[0],  self.virtualSize[1],
                                                    0.0,                  self.virtualSize[1]) ) )
            gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        
    def draw_fps(self):
        fps = clock.get_fps();
        if self.fpsLabel == None:
            self.fpsLabel = text.Label('',
                          font_name='Times New Roman',
                          font_size=20,
                          x=0, y=0,
                          color=(0,0,0,255) )
        self.fpsLabel.text = "FPS: " + str(fps)
        self.fpsLabel.draw()
        
    def on_resize(self, width, height):
        if width == 0 or height == 0:
            self.set_size(width, height)
            return
        
        # temporary using a 16:9 aspect ratio adding black borders
        # if there is time think of a more beautiful solution, at least graphical borders from our skilled artist        
        # calculate border
        windowAspect = float(width) / float(height)
        if windowAspect > self.aspect:
            border = (int(( windowAspect - self.aspect ) * height * 0.5), 0)
            scale = float(self.virtualSize[1]) / float(height)
        elif windowAspect < self.aspect:
            border = (0, int(( 1.0 / windowAspect - 1.0 / self.aspect ) * width * 0.5))
            scale = float(self.virtualSize[0]) / float(width)
        else:
            border = (0, 0)
            scale = float(self.virtualSize[0]) / float(width)        
        
        self.convertOffset = (float(border[0]), float(border[1]))
        self.convertScale =  (scale, scale)
        
        gl.glViewport(border[0], border[1], width - 2*border[0], height - 2*border[1])
        
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-0.5, self.virtualSize[0] - 0.5, 
                   -0.5, self.virtualSize[1] - 0.5, 
                   -1.0, 1.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
            
    def set_default_states(self):
        gl.glClearColor(*self.borderColor)
        gl.glClearDepth(1.0)
        gl.glDisable(gl.GL_CULL_FACE)
        
        #gl.glDepthFunc(gl.GL_LESS)
        #gl.glDepthMask(gl.GL_TRUE)
        #gl.glEnable(gl.GL_DEPTH_TEST)
    
    def on_key_press(self, symbol, modifiers):
        pass
    
    
class GameLoop(app.EventLoop):
    _allow_polling = True
    _next_idle_time = 0.0
    
    def idle(self):
        global Instance
        
        dt = clock.tick(False)
        GetApplication().deltaTime = dt
        GetApplication().gameTime += dt
        
        # Redraw all windows
        for window in app.windows:
            if window.invalid:
                window.switch_to()
                window.dispatch_event('on_draw')
                window.flip()

        # update timout
        return clock.get_sleep_time(False)

if __name__ == '__main__':
    import run_game
    if run_game.marvellousFakeUseVariableToShutupCompiler:
        pass