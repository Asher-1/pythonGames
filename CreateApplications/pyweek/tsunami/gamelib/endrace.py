from cocos.menu import Menu, CENTER, MenuItem, ToggleMenuItem, shake, shake_back
from cocos.layer import Layer
from cocos.scene import Scene
from cocos.director import director
from cocos.text import Label
from pyglet.window import key
import random

def EndOfRaceScreen(level, time, position, score):
    """ A Screen to show at the end of a race. Shows time, score, position and such"""
    return Scene (VictoryLayer(level, time, position, score))

nothing = ["Nothing", "Zero", "Nada", "Null", "None (as in no prize at all)", "Nulla", "Nichts", "Nihil", "Another chance", "A rubber duck", "Void", "Keep trying"]

class VictoryLayer(Layer):
    is_event_handler = True
    def __init__(self, level, time, position, score):
        super(VictoryLayer, self).__init__()
        if position == 1:
            title = Label('You won!', font_name='Yellowjacket',
                      color=(255,255,255,255), font_size=40, anchor_x='center',
                      anchor_y='baseline', position=(320, 420))
        else:
            title = Label('Race Finished', font_name='Yellowjacket',
                      color=(255,255,255,255), font_size=40, anchor_x='center',
                      anchor_y='baseline', position=(320, 420))
        self.add (title)

        timeLabel = Label('Elapsed time:   ' + time, font_name='Yellowjacket',
                      color=(200,200,200,255), font_size=22, anchor_x='center',
                      anchor_y='baseline', position=(320, 320))
        self.add (timeLabel)
        suffix = {1: 'st!', 2: 'nd', 3: 'rd'}
        posLabel = Label('Final Position:   %d%s' % (position, suffix.get(position,'th')), font_name='Yellowjacket',
                      color=(200,200,200,255), font_size=22, anchor_x='center',
                      anchor_y='baseline', position=(320, 285))
        self.add (posLabel)

        if len(level.prizes) < position:
            prize = random.choice (nothing)
        else:
            prize = "$%d" % level.prizes[position-1]
        prizeLabel = Label('Your prize:   %s' % prize, font_name='Yellowjacket',
                      color=(200,200,200,255), font_size=22, anchor_x='center',
                      anchor_y='baseline', position=(320, 250))
        self.add (prizeLabel)

        currentFunds = Label('Current funds:   $%s' % score, font_name='Yellowjacket',
                      color=(200,200,200,255), font_size=22, anchor_x='center',
                      anchor_y='baseline', position=(320, 215))
        self.add (currentFunds)

        #idea = Label('Aca de fondo puede haber un tipo descorchando champagne en la cubierta de un sucmarino', font_name='Yellowjacket',
        #              color=(200,200,200,255), font_size=12, anchor_x='center',
        #              anchor_y='baseline', position=(320, 60))
        #self.add (idea)
        self.back = Label('Continue', font_name='Yellowjacket',
                      color=(200,200,200,255), font_size=30, anchor_x='center',
                      anchor_y='center', position=(530, 30))
        self.add(self.back)
        self.backSelected = False

    def on_mouse_motion (self, x, y, dx, dy):
        x, y = director.get_virtual_coordinates (x, y)
        if 450 < x < 610 and 10 < y < 50:
            if not self.backSelected:
                self.back.scale=1.3
                self.back.stop()
                self.back.rotation = 0
                self.back.do(shake())
                self.backSelected = True
        else:
            if self.backSelected:
                self.back.scale=1
                self.back.stop()
                self.back.rotation = 0
                self.back.do(shake())
                self.backSelected = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.clicking = False

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.clicking = True

    def on_mouse_release(self, x, y, button, modifiers):
        if self.clicking:
            posx, posy = director.get_virtual_coordinates (x, y)
            if self.backSelected:
                self.on_quit()

    def on_quit(self):
        director.pop()
        director.pop()

    def on_key_press (self, symbol, modifiers):
        if symbol == key.ESCAPE or symbol == key.RETURN:
            self.on_quit()


