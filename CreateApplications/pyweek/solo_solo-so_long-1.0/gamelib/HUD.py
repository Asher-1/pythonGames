from cocos.layer import *
from cocos.text import *
from cocos.actions import *

import pyglet
from pyglet.gl import *

from state import state

class BackgroundLayer( Layer ):
    def __init__(self):
        super( BackgroundLayer, self ).__init__()
        self.img = pyglet.resource.image('background.png')

    def draw( self ):
        glPushMatrix()
        self.transform()
        self.img.blit(0,0)
        glPopMatrix()


class ScoreLayer( Layer ): 
    def __init__(self):
        w,h = director.get_window_size()
        super( ScoreLayer, self).__init__()

        # transparent layer
        self.add( ColorLayer(32,32,32,32, width=w, height=48),z=-1 )

        self.position = (0,h-48)

        self.score=  Label('Score:', font_size=36,
                font_name='Edit Undo Line BRK',
                color=(255,255,255,255),
                anchor_x='left',
                anchor_y='bottom')
        self.score.position=(0,0)
        self.add( self.score)

        self.time= Label('time:', font_size=36,
                font_name='Edit Undo Line BRK',
                color=(255,255,255,255),
                anchor_x='left',
                anchor_y='bottom')
        self.time.position=(245,0)
        self.add( self.time)

        self.lvl=  Label('Lvl:', font_size=36,
                font_name='Edit Undo Line BRK',
                color=(255,255,255,255),
                anchor_x='left',
                anchor_y='bottom')

        self.lvl.position=(480,0)
        self.add( self.lvl)

    def draw(self):
        super( ScoreLayer, self).draw()
        self.score.element.text = 'Score:%d' % state.score 
        self.time.element.text = 'time:%d' % state.time

        lvl = state.level_idx or 0
        self.lvl.element.text = 'Lvl:%d' % lvl
        

class MessageLayer( Layer ):
    def show_message( self, msg, callback=None ):

        w,h = director.get_window_size()

        self.msg = Label( msg,
            font_size=42,
            font_name='Edit Undo Line BRK',
            color=(64,64,64,255),
            anchor_y='center',
            anchor_x='center' )
        self.msg.position=(w/2.0, h)

        self.msg2 = Label( msg,
            font_size=42,
            font_name='Edit Undo Line BRK',
            color=(255,255,255,255),
            anchor_y='center',
            anchor_x='center' )
        self.msg2.position=(w/2.0+2, h+2)

        self.add( self.msg, z=1 )
        self.add( self.msg2, z=0 )

        actions = Accelerate(MoveBy( (0,-h/2.0), duration=0.5)) + \
                    Delay(1) +  \
                    Accelerate(MoveBy( (0,-h/2.0), duration=0.5)) + \
                    Hide()

        if callback:
            actions += CallFunc( callback )

        self.msg.do( actions )
        self.msg2.do( actions )

class HUD( Layer ):
    def __init__( self ):
        super( HUD, self).__init__()
        self.add( ScoreLayer() )
        self.add( MessageLayer(), name='msg' )

    def show_message( self, msg, callback = None ):
        self.get('msg').show_message( msg, callback )
