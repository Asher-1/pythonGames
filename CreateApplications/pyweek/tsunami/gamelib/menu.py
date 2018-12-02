#encoding: utf-8
from cocos.menu import Menu, LEFT, CENTER, MenuItem, ToggleMenuItem, shake, shake_back, MultipleMenuItem
from cocos.actions import CallFunc, MoveTo, Delay, CallFuncS
from cocos.scene import Scene
from cocos.layer import Layer, MultiplexLayer
from cocos.director import director
from cocos.sprite import Sprite
from cocos.text import Label, Label
from endrace import EndOfRaceScreen
from tabla import CapaTabla
from pyglet.window import key
from help import HelpLayer

from models import models, currentModel
from util import Vector
from dummymodel import DummyModel
from view import RaceScene
from game import Level
import controls
import options
import effects
import sound
import os.path
def MenuScene(theGame):
    fondo = Layer()
    bgsprite = Sprite(os.path.join('menu','background.png'), anchor=(0,0))
    fondo.add (bgsprite)
    credits = Layer()
    show_credit(0, credits)
    #fondo.add (effects.BubbleManager(640, 100), 5)
    m0 = MainMenu()
    m1 = PreferencesMenu()
    m2 = RaceChooserMenu(theGame)
    multiplex = MultiplexLayer (m0, m1, m2)
    m0.scale = 0.5
    m0.x = 145
    m0.y = -27
    m1.scale = 0.5
    m1.x = 145
    m1.y = -27
    caustics = effects.Caustics()
    s =  Scene(fondo, credits, multiplex, caustics)
    s.fondo = bgsprite
    s.credits = credits
    s.playing_music = False
    return s

def UpgradesScene():
    upgrades = UpgradesMenu()
    upgrades.scale = 0.95
    atts = dict(font_name='Yellowjacket', color=(255,255,255,255), font_size=20,
                anchor_x='center', anchor_y='center')
    fondo = Layer()
    bgsprite = Sprite(os.path.join('menu','background.png'), anchor=(0,0))
    fondo.add (bgsprite)
    bgsprite.opacity = 25
    y = 280
    x = 460
    nameLabel = Label('', position=(x,y), **atts)
    atts['font_size'] = 14
    atts['color'] = (200,200,200,255)
    y -= 30
    powLabel = Label('', position=(x,y), **atts)
    y -= 20
    rotSLabel = Label('', position=(x,y), **atts)
    y -= 20
    rotPLabel = Label('', position=(x,y), **atts)
    y -= 20
    rangeLabel = Label('', position=(x,y), **atts)
    y -= 20
    priceLabel = Label('', position=(x,y), **atts)
    fundsLabel = Label('', position=(400,120), **atts)
    atts['font_size'] = 20
    commentLabel = Label('', position=(320,30), **atts)
    
    upgrades.nameLabel = nameLabel
    upgrades.powLabel = powLabel
    upgrades.rotSLabel = rotSLabel
    upgrades.rotPLabel = rotPLabel
    upgrades.rangeLabel = rangeLabel
    upgrades.priceLabel = priceLabel
    upgrades.commentLabel = commentLabel
    upgrades.fundsLabel = fundsLabel

    upgrades.updateDescription()
    return Scene(fondo, upgrades, nameLabel, powLabel, rotSLabel, rotPLabel, rangeLabel, priceLabel, commentLabel, fundsLabel, effects.Caustics())

class UpgradesMenu (Menu):
    def __init__(self):

        super(UpgradesMenu, self).__init__("Upgrade your Submarine")

        FONT = 'Yellowjacket'
        COLOR = (200,200,200,255)
        self.font_title['font_name']=FONT
        self.font_title['color']=COLOR
        self.font_title['font_size'] = 35
        self.font_item['font_name']=FONT
        self.font_item['color']=COLOR
        self.font_item_selected['font_name']=FONT
        self.font_item_selected['color']=(230,230,230,255)
        self.font_item['font_size'] = 26
        self.font_item_selected['font_size'] = 32

        self.menu_valign = CENTER
        self.menu_halign = LEFT

        items = []

        for i, model in enumerate(models):
            items.append(MenuItem(model.name, self.select))

        items.append(MenuItem('Back', self.on_quit))
        self.create_menu(items, shake() | CallFunc(self.updateDescription), shake_back())

    def updateDescription(self):
        sound.menu_select()
        if self.selected_index < len(models):
            self.nameLabel.element.text = models[self.selected_index].name
            self.powLabel.element.text = 'Power: ' + str(models[self.selected_index].power)
            self.rotSLabel.element.text = 'Rotation Speed: ' + str(models[self.selected_index].rotspeed)
            self.rotPLabel.element.text = 'Rotation Power: ' + str(models[self.selected_index].rotpower)
            self.rangeLabel.element.text = 'Rope Range: ' + str(models[self.selected_index].RANGE)
            self.priceLabel.element.text = 'Price: $' + str(models[self.selected_index].price)
            if options.getopt('model') == models[self.selected_index].name:
                self.commentLabel.element.text = '(your current model)'
            elif self.selected_index < models.index(currentModel()):
                self.commentLabel.element.text = '(less than your current model)'
            elif float(options.getopt('score')) <= float(models[self.selected_index].price):
                self.commentLabel.element.text = '(insufficient funds)'
            else:
                self.commentLabel.element.text = '(upgrade now!)'
            self.fundsLabel.element.text = 'Funds: $' + str(options.getopt('score'))
        else:
            self.nameLabel.element.text = ''
            self.powLabel.element.text = ''
            self.rotSLabel.element.text = ''
            self.rotPLabel.element.text = ''
            self.rangeLabel.element.text = ''
            self.priceLabel.element.text = ''
            self.commentLabel.element.text = ''
            self.fundsLabel.element.text = ''

    def select(self):
        sound.menu_click()
        funds = float(options.getopt('score'))
        current = currentModel()
        if current.name == models[self.selected_index].name:
            self.commentLabel.element.text = 'You already have that model!'
        elif self.selected_index < models.index(current):
            self.commentLabel.element.text = 'You already have a better model!'
        elif funds < models[self.selected_index].price:
            self.commentLabel.element.text = "You don't have enough money!"
        else:
            funds -= models[self.selected_index].price
            options.setopt('score', funds)
            options.setopt('model', models[self.selected_index].name)
            self.updateDescription()
            self.commentLabel.element.text = "Upgrade complete!"

    def on_quit(self):
        sound.menu_click()
        director.pop()


def start_music(self):
    if not self.parent.parent.playing_music:
        sound.play_music (os.path.join('music','ap_surmx.xm'))
        self.parent.parent.playing_music = True

class RaceChooserMenu(Layer):
    normalScale = 0.4
    selectedScale = 0.7
    is_event_handler = True
    def __init__(self, theGame):
        super(RaceChooserMenu, self).__init__()
        self.game = theGame
        self.world = Sprite(os.path.join('data','world.png'), anchor=(0,0), scale=600/800.0, position=(20,10))
        self.add(self.world)
        title = Label('Select your challenge!', font_name='Yellowjacket',
                      color=(200,200,200,255), font_size=35, anchor_x='center',
                      anchor_y='baseline', position=(320, 420))
        self.add (title)
        self.back = Label('Back', font_name='Yellowjacket',
                      color=(200,200,200,255), font_size=30, anchor_x='center',
                      anchor_y='center', position=(60, 30))
        self.add(self.back)
        self.backSelected = False
        self.upgrade = Label('Upgrades', font_name='Yellowjacket',
                      color=(200,200,200,255), font_size=30, anchor_x='center',
                      anchor_y='center', position=(500, 30))
        self.add(self.upgrade)
        self.upgradeSelected = False
        self.levelLabel = Label('', font_name='Yellowjacket',
                      color=(200,200,200,255), font_size=18, anchor_x='center',
                      anchor_y='center', position=(320, 390))
        self.add(self.levelLabel)
        self.updateLevels()
        self.selected = None
        self.select_action= shake() | CallFunc (sound.menu_select)
        self.unselect_action= shake_back()

    def on_mouse_motion (self, x, y, dx, dy):
        x, y = director.get_virtual_coordinates (x, y)
        pos = Vector(x - self.x, y - self.y)
        for child in self.get_levels():
            if abs(pos - child.pos()) < 18:
                if self.selected is None:
                    child.scale = self.selectedScale
                    child.stop()
                    child.rotation = 0
                    child.do(self.select_action)
                    self.selected = child
                    self.updateLevelLabel()
                break
        else:
            self.select_none()
        if 10 < x < 90 and 10 < y < 50:
            if not self.backSelected:
                self.back.scale=1.3
                self.back.stop()
                self.back.rotation = 0
                self.back.do(self.select_action)
                self.backSelected = True
        else:
            if self.backSelected:
                self.back.scale=1
                self.back.stop()
                self.back.rotation = 0
                self.back.do(self.unselect_action)
                self.backSelected = False
        if 390 < x < 630 and 10 < y < 50:
            if not self.upgradeSelected:
                self.upgrade.scale=1.3
                self.upgrade.stop()
                self.upgrade.rotation = 0
                self.upgrade.do(self.select_action)
                self.upgradeSelected = True
        else:
            if self.upgradeSelected:
                self.upgrade.scale=1
                self.upgrade.stop()
                self.upgrade.rotation = 0
                self.upgrade.do(self.unselect_action)
                self.upgradeSelected = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.clicking = False

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.clicking = True

    def on_mouse_release(self, x, y, button, modifiers):
        if self.clicking:
            posx, posy = director.get_virtual_coordinates (x, y)
            print posx, posy
            if not self.selected is None:
                sound.menu_click()
                levelToPlay = self.selected
                self.select_none()
                self.on_play(levelToPlay)
            elif 10 < posx < 90 and 10 < posy < 50:
                sound.menu_click()
                self.back.scale=1
                self.back.stop()
                self.back.rotation = 0
                self.backSelected = False
                self.parent.switch_to (0)
                self.parent.parent.fondo.opacity = 255
                self.parent.parent.credits.visible = True
            elif 390 < posx < 630 and 10 < posy < 50:
                sound.menu_click()
                self.upgrade.scale=1
                self.upgrade.stop()
                self.upgrade.rotation = 0
                self.upgradeSelected = False
                director.push(UpgradesScene())

    def on_key_press (self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.select_none()
            self.parent.switch_to (0)
            self.parent.parent.fondo.opacity = 255
            self.parent.parent.credits.visible = True
        elif symbol == key.RETURN:
            sound.menu_click()
            if self.selected is None:
                levelToPlay = self.game.levelTree.unlocked['1']
            else:
                levelToPlay = self.selected
            self.select_none()
            self.on_play (levelToPlay)
        return True


    def select_none(self):
        if self.selected is None:
            return
        self.selected.scale = self.normalScale
        self.selected.stop()
        self.selected.rotation = 0
        self.selected.do(self.unselect_action)
        self.selected = None
        self.updateLevelLabel()

    def get_levels(self):
        return [l for l in self.get_children() if isinstance(l, Level)]

    def on_play(self, levelToPlay):
        sound.stop_music()
        self.parent.parent.playing_music = False
        self.game.setCurrentLevel(levelToPlay)
        model = DummyModel(self.game, levelToPlay.levelFilename)
        director.push (RaceScene(model))
        self.game.levelUpdater = self.updateLevels

    def updateLevelLabel(self):
        if self.selected:
            if self.selected.completed:
                completed = "   (Completed!)"
            else:
                completed = ""
            fields = (self.selected.name, self.selected.prizes[0], self.selected.difficulty, completed)
            self.levelLabel.element.text = "%s - Prize: $%d - %s%s" % fields
        else:
            self.levelLabel.element.text = ""

    def updateLevels(self):
        levels = self.get_levels()
        for level in self.game.levelTree.unlocked.values():
            if not level in levels:
                self.add (level, z=42)
                level.scale = self.normalScale

    def on_enter(self):
        super (RaceChooserMenu, self).on_enter()
        start_music(self)

class MainMenu (Menu):
    def __init__(self):

        super(MainMenu, self).__init__("")

        FONT = 'Yellowjacket'
        COLOR = (200,200,200,255)
        self.font_title['font_name']=FONT
        self.font_title['color']=COLOR
        self.font_title['font_size'] = 48
        self.font_item['font_name']=FONT
        self.font_item['color']=COLOR
        self.font_item_selected['font_name']=FONT
        self.font_item_selected['color']=(230,230,230,255)
        self.font_item['font_size'] = 26
        self.font_item_selected['font_size'] = 32

        self.menu_valign = CENTER
        self.menu_halign = CENTER

        items = []

        items.append(MenuItem('Play!', self.on_play))
        items.append(MenuItem('High scores', self.on_scores))
        items.append(MenuItem('Preferences', self.on_options))
        items.append(MenuItem('Help', self.on_help))
        items.append(MenuItem('Exit', self.on_quit))

        self.create_menu(items, shake() | CallFunc(sound.menu_select), shake_back())

    def on_play(self):
        self.parent.parent.fondo.opacity = 25
        self.parent.parent.credits.visible = False
        sound.menu_click()
        self.parent.switch_to (2)

    def on_scores(self):
        sound.menu_click()
        hiscore = CapaTabla()
        hiscore.onFinished = director.pop
        s = Scene(hiscore, effects.Caustics())
        director.push(s)

    def on_help (self):
        sound.menu_click()
        s = Scene (HelpLayer(), effects.Caustics())
        director.push (s)

    def on_options(self):
        sound.menu_click()
        self.parent.switch_to (1)

    def on_quit(self):
        sound.menu_click()
        director.pop()

    def on_enter(self):
        super (MainMenu, self).on_enter()
        start_music(self)


class PreferencesMenu(Menu):
    def __init__(self):

        super(PreferencesMenu, self).__init__("")

        FONT = 'Yellowjacket'
        COLOR = (200,200,200,255)
        self.font_title['font_name']=FONT
        self.font_title['color']=COLOR
        self.font_title['font_size'] = 48
        self.font_item['font_name']=FONT
        self.font_item['color']=COLOR
        self.font_item['font_size'] = 26
        self.font_item_selected['font_name']=FONT
        self.font_item_selected['color']=(230,230,230,255)
        self.font_item_selected['font_size'] = 28

        self.menu_valign = CENTER
        self.menu_halign = CENTER

        items = []

        self.toggle_thrust = MultipleMenuItem('Thrust keys: ', self.on_thrust,['Arrows', 'WASD'], options.getopt('arrow_map'))
        self.toggle_string = MultipleMenuItem('String keys: ', self.on_string,['Keypad', 'keys around S'], options.getopt('rope_map'))
        items.append(self.toggle_thrust)
        items.append(self.toggle_string)
        items.append(ToggleMenuItem('Fullscreen: ', self.on_pcompleta, 
                                    director.window.fullscreen))
        items.append(ToggleMenuItem('Sound FX: ', self.on_sonido, options.getopt('sound')))
        items.append(ToggleMenuItem('Music: ', self.on_music, options.getopt('music')))
        items.append(MenuItem('Back', self.on_quit))

        self.create_menu(items, shake() | CallFunc(sound.menu_select), shake_back())

    def on_thrust (self, value):
        sound.menu_click()
        kmap = [controls.arrow_map_1, controls.arrow_map_2]
        controls.Bindings.arrow_map = kmap[value]
        if value==1 and self.toggle_string.idx == 1:
            self.toggle_string.on_key_press (key.LEFT, 0)
        options.setopt ('arrow_map', value)

    def on_string (self, value):
        sound.menu_click()
        sound.menu_click()
        kmap = [controls.rope_map_2, controls.rope_map_1]
        controls.Bindings.rope_map = kmap[value]
        if value==1 and self.toggle_thrust.idx == 1:
            self.toggle_thrust.on_key_press (key.LEFT, 0)
        options.setopt ('rope_map', value)

    def on_pcompleta(self, value):
        sound.menu_click()
        director.window.set_fullscreen( bool(value) )
        options.setopt ('fullscreen', bool(value))

    def on_sonido (self, value):
        #sonido.activado = bool(valor)
        if bool(value):
            sound.enable_sound()
            sound.menu_click()
        else:
            sound.disable_sound()
        options.setopt ('sound', bool(value))

    def on_music (self, value):
        #sonido.activado = bool(valor)
        sound.menu_click()
        if bool(value):
            sound.enable_music()
            sound.play_music (os.path.join('music','ap_surmx.xm'))
        else:
            sound.disable_music ()
        options.setopt ('music', bool(value))

    def on_quit(self):
        sound.menu_click()
        self.parent.switch_to (0)

credits = """A game made for pyWeek7
© 2008 under the GNU GPLv2. See "COPYING" file for details
UI, AI, levels, logic & misc: Anthony A. Lenton
Game logic , physics & misc: Daniel F Moisset
Physics engine: Pablo Q. Moisset
Graphics & misc: Rayentray Tappa
Graphics: wileart
Additional resources: free, from the web. See README for details

The credits are over.

Go play, now

What, are you waiting for the cheatcodes?
I won't give you the cheatcodes.

I said no.

Are you still watching this instead of playing?
""".decode('utf-8').split('\n')

def show_credit (index, layer):
    l = Label (credits[index], font_name='Yellowjacket',
                      color=(200,200,200,255),
                      position=(840, 10), anchor_x='center')
    layer.add (l)
    next = (index+1) % len(credits)
    slide = MoveTo((320, 10),1)+Delay(1.5)+MoveTo ((-200, 10),1)+ \
            CallFunc (lambda: show_credit(next, layer))+MoveTo ((-640, 10),1)+CallFuncS(layer.remove)
    l.do (slide)

