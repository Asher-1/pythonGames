'''
Created on 12.09.2011

'''

import data
import sound

from globals import Z_INDICES
from globals import FONTS

from math2d import Vector2
from math2d import AARect2d

from renderables import get_zlayer
from renderables import AnimatedSprite
from renderables import BatchRenderer

from pyglet import text
from pyglet.window import key
from pyglet import event
from application import GetApplication

class Gui(event.EventDispatcher):
    
    _app = None
    _elements = None
    _mouseOver = None
    _visible = True
    _focusElement = None
    
    def __init__(self, application):
        self._elements = set()
        self._mouseOver = []
        
        self._app = application
        if self._visible:
            self._register_handlers()
    
    def _register_handlers(self):
        self._app.push_handlers(self)
        
    def _unregister_handlers(self):
        self._app.remove_handlers(self)
        
    def hide(self):
        if not self._visible:
            return
        
        for element in self._elements:
            element.set_visible(False)
            
        for element in self._mouseOver:
            element.on_mouse_leave()
        
        if self._focusElement:
            self._focusElement.focus_lost()
            self._focusElement = None
            
        self._mouseOver[:] = []
        
        self._unregister_handlers()    
        self._visible = False
        
        self.dispatch_event('on_hide', self)
        
    def show(self):
        if self._visible:
            return
        
        for element in self._elements:
            element.set_visible(True)
            
        self._register_handlers()
        self._visible = True
        self.dispatch_event('on_show', self)
        
    def add_element(self, element):
        self._elements.add(element)
        return element
    
    def on_mouse_release(self, x, y, button, modifiers):
        for element in self._mouseOver:
            element.on_click()
            
            if self._focusElement != element:
                if self._focusElement:
                    self._focusElement.focus_lost()
                self._focusElement = element
                self._focusElement.focus()
                break
        else:
            if self._focusElement:
                self._focusElement.focus_lost()
                self._focusElement = None
                
        return len(self._mouseOver) > 0
    
    def on_mouse_motion(self, x, y, dx, dy, buttons, modifiers):
        for element in self._elements:
            wasMouseOver = element in self._mouseOver
            if element.hit_test(Vector2(x, y)):                
                if not wasMouseOver:
                    self._mouseOver.append(element)
                    element.on_mouse_enter()
            elif wasMouseOver:
                element.on_mouse_leave()
                self._mouseOver.remove(element)
                
    def on_text(self, text):
        if self._focusElement:
            self._focusElement.on_text(text)
            return True
        
    def on_text_motion(self, motion):
        if self._focusElement:
            self._focusElement.on_text_motion(motion)
            return True            

Gui.register_event_type('on_hide')
Gui.register_event_type('on_show')


class MainMenuGui(Gui):

    _SubGui = None
    
    def __init__(self, application):
        Gui.__init__(self, application)
        
        self.add_element(Button(Vector2(640-175, 325), Vector2(350, 40), "Start Game", lambda:self.on_start_game()))
        self.add_element(Button(Vector2(640-175, 250), Vector2(350, 40), "Editor", lambda:self.on_editor()))
        self.add_element(Button(Vector2(640-175, 200), Vector2(350, 40), "Credits", lambda:self.on_credits()))
        self.add_element(Button(Vector2(640-175, 125), Vector2(350, 40), "Exit", lambda:self.on_exit()))
        
    def on_start_game(self):
        self.set_sub_gui(LevelSelection(self._app))        
    
    def on_editor(self):
        self._app.set_mode('Edit')
    
    def on_credits(self):
        self.set_sub_gui(CreditsGui(self._app))

    def set_sub_gui(self, gui):
        if self._SubGui:
            self._SubGui.remove_handlers(self)
            self._SubGui.hide()
        
        self._SubGui = gui
        
        if self._SubGui: 
            self._SubGui.push_handlers(self)
            self.hide()
        else: 
            self.show()
    
    def on_exit(self):
        self._app.request_exit()
        
    def on_hide(self, gui):
        if gui == self._SubGui:
            self.set_sub_gui(None)
    
    def on_show(self, gui):
        pass
    
    
class CreditsGui(Gui):
    
    def __init__(self, application):
        Gui.__init__(self, application)
        
        self.add_element(BackgroundBox(Vector2(640, 290), Vector2(530, 420), (0.0, 0.0, 0.0)))
        self.add_element(Label(Vector2(640, 460), Vector2(350, 20), unicode("Coding"))).set_text_anchor('center', 'center').set_text_color(1.0, 1.0, 1.0)    
        self.add_element(Label(Vector2(640, 430), Vector2(350, 40), unicode("Julian Moschuering"))).set_text_anchor('center', 'center').set_text_color(1.0, 1.0, 1.0)
        self.add_element(Label(Vector2(640, 390), Vector2(350, 40), unicode("Robert Schrader"))).set_text_anchor('center', 'center').set_text_color(1.0, 1.0, 1.0)
        
        self.add_element(Label(Vector2(640, 330), Vector2(350, 20), unicode("Game Design & Graphics"))).set_text_anchor('center', 'center').set_text_color(1.0, 1.0, 1.0)    
        self.add_element(Label(Vector2(640, 300), Vector2(350, 40), unicode("Thomas Blickling"))).set_text_anchor('center', 'center').set_text_color(1.0, 1.0, 1.0)
        
        self.add_element(Label(Vector2(640, 240), Vector2(350, 20), unicode("Sound"))).set_text_anchor('center', 'center').set_text_color(1.0, 1.0, 1.0)    
        self.add_element(Label(Vector2(640, 210), Vector2(350, 40), unicode("Florian Jindra"))).set_text_anchor('center', 'center').set_text_color(1.0, 1.0, 1.0)
        
        self.add_element(Button(Vector2(640-175, 125), Vector2(350, 40), "Back", lambda:self.button_on_back())).set_text_anchor('center', 'center')
    
    def button_on_back(self):
        self.hide()


class LevelSelection(Gui):
    
    def __init__(self, application):
        Gui.__init__(self, application)
        
        self.add_element(BackgroundBox(Vector2(640, 310), Vector2(640, 430), (0.0, 0.0, 0.0)))
        
        y = 420
        j = 1
        for i in range(1, 15):
            func = lambda mapNumber=i:self.button_on_start(str(mapNumber-1))
            self.add_element(Button(Vector2(640-4*95 + (j * 95), y), Vector2(90, 70), str(i), func)).set_text_anchor('center', 'center')
            if i % 6 == 0:
                y -= 80
                j = 0
            j += 1
            
        self.add_element(Button(Vector2(640-175, 125), Vector2(350, 40), "Back", lambda:self.button_on_back())).set_text_anchor('center', 'center')
    
    def button_on_back(self):
        self.hide()
    
    def button_on_start(self, mapnumber):
        self.hide()
        self._app.start_map(str(mapnumber))
        

class Element(AnimatedSprite):
    
    isHovering = False
    _Box = None
    
    def __init__(self):
        AnimatedSprite.__init__(self)
        self.set_z_index(Z_INDICES.GUI_FRONT)
        self.set_anchor(0.0, 0.0)
    
    def _update_hit_box(self):
        self._Box = AARect2d(self.get_position(), self.get_position() + self.get_size())
    
    def set_position(self, position):
        AnimatedSprite.set_position(self, position)
        self._update_hit_box()
    
    def set_size(self, size):
        AnimatedSprite.set_size(self, size)
        self._update_hit_box()
        
    def hit_test(self, point):
        return self._Box.contains(point)
    
    def render(self, gameTime, deltaTime):
        AnimatedSprite.render(self, gameTime, deltaTime)
        
    def on_mouse_enter(self):
        self.isHovering = True
    
    def on_mouse_leave(self):
        self.isHovering = False
    
    def on_click(self):
        pass
        
    def focus(self):
        pass
    
    def focus_lost(self):
        pass
    
    def on_text(self, text):
        pass
        
    def on_text_motion(self, motion):
        pass


class BackgroundBox(Element):
    
    def __init__(self, position, size, color):
        Element.__init__(self)
        self.set_position(position)
        self.set_size(size)
        self.set_color(*color)
        self.set_texture(data.load_texture("backgroundbox.png"))
        self.set_anchor(0.5, 0.5)
        

class Label(Element):
    
    _Text = "Text"
    _label = None
    _color = (0, 0, 0, 255)
    _anchor_x = "left"
    _anchor_y = "bottom"

    def __init__(self, position, size, text):
        Element.__init__(self)
        self.set_position(position)
        self.set_size(size)
        self.set_text(text)
        
        self._update_label()
            
    def _register_render(self):
        Element._register_render(self)
        
        # label does not allow removing it from its batch like it is done when hiding sprites
        # -> delete/create
        self._label = text.Label(self._Text, FONTS.GUI_BUTTON,
            anchor_x = self._anchor_x, anchor_y = self._anchor_y, bold = False, color = self._color, 
            batch = BatchRenderer.get_main_renderbatch().get_batch(), group = get_zlayer(Z_INDICES.GUI_TEXT))
        self._update_label()
    
    def _unregister_render(self):
        Element._unregister_render(self)
        
        # label does not allow removing it from its batch like it is done when hiding sprites
        # -> delete/create
        if self._label:
            self._label.delete()
            self._label = None
    
    def set_position(self, position):
        Element.set_position(self, position)
        self._update_label()
    
    def set_size(self, size):
        Element.set_size(self, size)
        self._update_label()
    
    def _update_label(self):
        if not self._label:
            return
        
        self._label.x = self.get_position().x
        self._label.y = self.get_position().y
        self._label.font_size = int(self.get_size().y * 0.7)
    
    def set_text_anchor(self, x, y):
        self._label.anchor_x = x
        self._label.anchor_y = y
        self._anchor_x = x
        self._anchor_y = y
        return self
        
    def set_text_color(self, r, g, b, a = 1.0):
        self._color = map(int, (r * 255, g * 255, b * 255, a * 255))
        self._label.color = self._color
        return self
        
    def set_text(self, text):
        self._Text = text
        if self._label:
            self._label.text = text


class EditLabel(Label):
    
    _EditText = ""
    _CaretPos = 0
    _Focused = []
    _Unfocused = []
    
    __myUpdate = False
    
    def __init__(self, position, size, text):
        Label.__init__(self, position, size, text)        
        self._Focused = [data.load_texture("editlabel_focused.png")]
        self._Unfocused = [data.load_texture("editlabel_unfocused.png")]
        self.set_animation(self._Unfocused)
    
    def get_text(self):
        return self._EditText
    
    def _set_text_caret(self, text):
        text = text[:self._CaretPos] + "|" + text[self._CaretPos:]
        self.__myUpdate = True
        self.set_text(text)
        self.__myUpdate = False
        
    def focus(self):
        self._set_text_caret(self._EditText)
        self.set_animation(self._Focused)
    
    def focus_lost(self):
        self.set_text(self._EditText)
        self.set_animation(self._Unfocused)
    
    def set_text(self, text):
        Label.set_text(self, text)
                
        if not self.__myUpdate:
            self._EditText = text      
            self._CaretPos = len(self._EditText)
        
    def on_text(self, text):
        text = text.replace('\r', '')
        lastText = self._EditText
        lastCaret = self._CaretPos
        
        self._EditText = self._EditText[:self._CaretPos] + text + self._EditText[self._CaretPos:]
        self._CaretPos += len(text)
        self._set_text_caret(self._EditText)
        
        if self._label.content_width > self.get_size().x:
            self._CaretPos = lastCaret
            self._EditText = lastText
            self._set_text_caret(self._EditText)
    
    def shorten_text(self):
        while self._label.content_width > self.get_size().x:
            if self._CaretPos == len(self._EditText):
                self._CaretPos -= 1
            self._EditText = self._EditText[:-1]
            self._set_text_caret(self._EditText)
   
    def on_text_motion(self, motion):
        if motion == key.MOTION_LEFT:
            self._CaretPos = max(0, self._CaretPos - 1)
        elif motion == key.MOTION_RIGHT:
            self._CaretPos = max(0, self._CaretPos + 1)
        elif motion == key.MOTION_BEGINNING_OF_LINE:
            self._CaretPos = 0
        elif motion == key.MOTION_END_OF_LINE:
            self._CaretPos = len(self._EditText)
        elif motion == key.MOTION_BACKSPACE:
            if self._CaretPos > 0:
                self._EditText = self._EditText[:self._CaretPos-1] + self._EditText[self._CaretPos:]
                self._CaretPos -= 1
        elif motion == key.MOTION_DELETE:
            if self._CaretPos < len(self._EditText):
                self._EditText = self._EditText[:self._CaretPos] + self._EditText[self._CaretPos+1:]
        else:
            return
        
        self._set_text_caret(self._EditText)
        

class Button(Label):
    
    _Text = "Generic Button Text"
    _IdleAnimation = None
    _HoverAnimation = None
    _ClickAnimation = None
    
    _anchor_x = "center"
    _anchor_y = "center"
    
    _Callback = None
    _IsClicking = False
    
    def __init__(self, position, size, text, callback):
        Label.__init__(self, position, size, text)
        
        self._Callback = callback
        self._IdleAnimation = [data.load_texture("button_idle_00.png")]
        self._HoverAnimation = [data.load_texture("button_hover_00.png")]
        self._ClickAnimation = [data.load_texture("button_click_00.png")]
        self._color = (255, 255, 255, 255)
        self._update_textures()
    
    def _unregister_render(self):
        Label._unregister_render(self)
        self._IsClicking = False
        
    def _register_render(self):
        Label._register_render(self)
        
    def on_animation_end(self):
        if self._IsClicking:
            self._IsClicking = False
            self._update_textures()
            
    def _update_textures(self):
        if self._IsClicking:
            self.set_animation(self._ClickAnimation);
        elif self.isHovering:
            self.set_animation(self._HoverAnimation);
        else:
            self.set_animation(self._IdleAnimation);
    
    def _update_label(self):
        if not self._label:
            return
        
        center = self.get_position() + self.get_size() * 0.5
        self._label.x = center.x
        self._label.y = center.y + self.get_size().y / 15
        self._label.font_size = int(self.get_size().y * 0.7)
        
    def on_click(self):
        Element.on_click(self)
    
        self._IsClicking = True
            
        if self._Callback:
            self._Callback()
    
        self._update_textures()
        
        fileName = data.load_sound("click_01")
        sound.play_sound(fileName[1])
        
    def on_mouse_enter(self):
        Element.on_mouse_enter(self)
        self._update_textures()
        
    def on_mouse_leave(self):
        Element.on_mouse_leave(self)
        self._update_textures()
        
    def render(self, gameTime, deltaTime):
        Element.render(self, gameTime, deltaTime)
    