# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# pyglet realted
from pyglet.window import key

# cocos2d related
from cocos.layer import Layer, ColorLayer
from cocos.director import director
from cocos.text import Label
from cocos.actions import *

# tetrico related
import soundex
import hiscore
from state import state


class GameOver( ColorLayer ):
    is_event_handler = True #: enable pyglet's events

    def __init__( self, win = False):
        super(GameOver,self).__init__( 32,32,32,64)

        w,h = director.get_window_size()

        self.win = win

        if win:
            soundex.play('oh_yeah.mp3')
            msg = 'LOVE ME DO'
        else:
            soundex.play('no.mp3')
            msg = 'GAME OVER'

        label = Label(msg,
                    font_name='Edit Undo Line BRK',
                    font_size=54,
                    anchor_y='center',
                    anchor_x='center' )
        label.position =  ( w/2.0, h/2.0 )

        self.add( label )

        angle = 5
        duration = 0.05
        accel = 2
        rot = Accelerate(Rotate( angle, duration//2 ), accel)
        rot2 = Accelerate(Rotate( -angle*2, duration), accel)
        effect = rot + (rot2 + Reverse(rot2)) * 4 + Reverse(rot)
        
        label.do( Repeat( Delay(5) + effect ) )

        if hiscore.hiscore.is_in( state.score ):
            self.hi_score = True

            label = Label('Enter your name:',
                        font_name='Edit Undo Line BRK',
                        font_size=36,
                        anchor_y='center',
                        anchor_x='center',
                        color=(32,32,32,255),
                        )
            label.position =  ( w/2.0, h/2.0 )
            label.position = (w//2, 130)
            self.add( label )

            self.name= Label('',
                        font_name='Edit Undo Line BRK',
                        font_size=36,
                        anchor_y='center',
                        anchor_x='center',
                        color=(32,32,32,255),
                        )
            self.name.position=(w//2,80)
            self.add(self.name)
        else:
            self.hi_score = False

            if not self.win:
                label = Label("Press 'R' to restart level",
                            font_name='Edit Undo Line BRK',
                            font_size=18,
                            anchor_y='center',
                            anchor_x='center' )
                label.position =  ( w/2.0, 20 )
                self.add( label )

    def on_key_press( self, k, m ):
        if not self.hi_score and (k == key.ENTER or k == key.ESCAPE):
            director.pop()
            return True

        if not self.hi_score and (k == key.R) and not self.win:
            self.parent.remove( self )
            self.parent.get('ctrl').restart_level()
            return True

        if self.hi_score:
            if k == key.BACKSPACE:
                self.name.element.text = self.name.element.text[0:-1]
                return True
            elif k == key.ENTER:
                hiscore.hiscore.add( state.score,self.name.element.text,state.level_idx )
                director.pop()
                return True
        return False

    def on_text( self, t ):
        if not self.hi_score:
            return False

        if t=='\r':
            return True

        self.name.element.text += t
