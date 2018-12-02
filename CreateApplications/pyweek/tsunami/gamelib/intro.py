from cocos.scene import Scene
from cocos.layer import Layer
from cocos.sprite import Sprite
from cocos.director import director
from cocos.actions import *

from menu import MenuScene
from game import Game
import data
import sound
import os.path
T = 4.0
FT = 0.75

class SkipLayer(Layer):

    is_event_handler = True
    
    def on_mouse_release(self, x, y, button, modifiers):
        self.parent.end()

    def on_key_press(self, key, modifiers):
        return True

    def on_key_release(self, key, modifiers):
        self.parent.end()
        return True

class IntroScene (Scene):

    def __init__ (self, next):
        super (IntroScene, self).__init__ ()
        self.add (SkipLayer())
        self.next = next
    
    def on_enter(self):
        super (IntroScene, self).on_enter ()
        l = Layer()
        i1 = Sprite (os.path.join('intro','1.png'), anchor=(0,0))
        i2 = Sprite (os.path.join('intro','2.png'), anchor=(0,0))
        l.add (i1)
        l.add (i2)
        self.add (l)
        i1.visible=False
        i2.visible=False
        i1.do(Show()+FadeIn(FT)+Delay(T)+FadeOut(FT)+Hide())
        i2.do(Delay(FT+T+FT/2)+Show()+FadeIn(FT)+Delay(T)+FadeOut(FT)+CallFunc(self.end))

        sound.play_music (os.path.join('music','ap_surmx.xm'))
        self.next.playing_music = True

    def end(self):
        director.replace(self.next)


