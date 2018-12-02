import math
import pyglet
import cocos.rect, cocos.sprite, cocos.scene, cocos.text
from cocos.actions import *
import effects
import controls
from util import to_tuple
from scroll import ScrollManager, ParallaxScroller, position_setter
import os.path
import sound

musics = ['levela.xm', 'levelb.xm', 'levelc.mod']

def RaceScene(model):
    scroller = ScrollManager (cocos.rect.Rect(200, 200, 240, 80))
    bgscroller = ParallaxScroller (scroller, 4.0)

    bg = RaceBG(bgscroller, model.game.currentLevel.levelId)
    water = effects.Caustics(scroller=bgscroller)
    race = RaceView (model, scroller)
    hud = RaceHUD (race, model, scroller)
    start = Starter (race)
    control = controls.ControlLayer(model.hero)
    race.control = control
    # Music!
    n = int(model.game.currentLevel.levelId)

    class MusicScene(cocos.scene.Scene):
 
        def on_enter (self):
            super(MusicScene, self).on_enter()
            # sound.play_music(os.path.join("music", musics[n % len(musics)]))
 
        def on_exit (self):
            super (MusicScene, self).on_enter()
            sound.stop_music()
    
    return MusicScene (bg, water, race, hud, start, control)
    
class RaceView(cocos.layer.Layer):
    def __init__ (self, model, scroller):
        super(RaceView, self ).__init__()
        self.model = model
        self.scroller = scroller
        scroller.add_action (position_setter (self))
        self.shipId = 0
        for item in self.model.world.items:
                self.add (item)
        for chkpt in self.model.world.checkpoints:
                self.add (chkpt)

    def start (self):
        self.model.world.setStartTime()
        self.schedule (self.update)
        tune = ['a', 'b'][int(self.model.game.currentLevel.levelId) % 2]
        # sound.play_music (os.path.join('music','level%s.xm' % tune))

    def on_exit(self):
        super(RaceView, self).on_exit()
        self.unschedule (self.update)        

    def leaveHeroWithin (self, rect):
        x = -self.position[0]
        if self.model.hero.position[0] < x + rect.left:
            x = self.model.hero.position[0] - rect.left
        elif self.model.hero.position[0] > x + rect.right:
            x = self.model.hero.position[0] - rect.right
        y = -self.position[1]
        if self.model.hero.position[1] < y + rect.bottom:
            y = self.model.hero.position[1] - rect.bottom
        elif self.model.hero.position[1] > y + rect.top:
            y = self.model.hero.position[1] - rect.top
        self.position = (-x,-y)

    def update(self, delta):
        # For testing
        self.model.update(delta)
        children = self.get_children()
        for fish in self.model.fish:
            if not fish in children:
                self.add(fish)
        for ship in self.model.ships:
            if not ship in children:
                self.add(ship)
        for rope in self.model.ropes:
            if not rope in children:
                self.add(rope)
        if not self.model.hero in children:
            self.add(self.model.hero)
            self.bubbles = effects.BubbleManager(5, 15, self.model.hero)
            self.model.hero.bubbles = self.bubbles
            self.add (self.bubbles)
        self.scroller.focus_on (self.model.hero)

    
class Starter (cocos.layer.Layer):
    def __init__ (self, race):        
        super (Starter, self).__init__()
        name = ['go', '1', '2', '3']
        x, y = cocos.director.director.get_window_size()
        disappear = FadeOut (1.2) | ScaleBy (3, 1.2)
        for i in xrange (4):
            node = cocos.cocosnode.CocosNode()
            bgr = cocos.sprite.Sprite('star.png', position=(x/2,y/2), scale=0.5)
            number = cocos.sprite.Sprite('%s.png' % name[i], position=(x/2,y/2))
            node.add (bgr); node.add (number)
            bgr.visible = False
            number.visible = False
            self.add (node)
            action = Delay(3.01-i)+Show()
            if i==0:
                action += CallFunc (lambda: race.start())
            action += disappear
            number.do (action)
            if i==0:
                action += CallFunc (lambda: self.parent.remove (self))
            bgr.do (action)
        
class RaceHUD (cocos.layer.Layer):

    def __init__ (self, race, model, scroller):
        super (RaceHUD, self).__init__()
        self.model = model
        self.race = race
        self.add(cocos.sprite.Sprite('hud.png', anchor=(0,0)))
        atts = {"font_name":'LMTypeWriter10', "font_size":12, "color":(0,0,0,255)}
        self.lapstr = 'Lap: 1'
        self.laplabel = cocos.text.Label (self.lapstr, **atts)
        self.add (self.laplabel, z=3)
        self.laplabel.position= 15, 10
        self.timerlabellabel = cocos.text.Label ('Time:', **atts)
        self.add (self.timerlabellabel, z=3)
        self.timerlabellabel.position = 15, 53
        self.timerlabel = cocos.text.Label ('00:00:00', **atts)
        self.add (self.timerlabel, z=3)
        self.timerlabel.position = 12, 35
        self.helper = cocos.sprite.Sprite ('arrow.png')
        self.helper.position = 109, 36
        self.helper.scale = 0.5
        self.add (self.helper,z=3)

    def on_enter(self):
        super(RaceHUD, self).on_enter()
        self.schedule (self.step)

    def on_exit(self):
        super(RaceHUD, self).on_exit()
        self.unschedule (self.step)
        
    def step (self, dt):
        x1, y1 = self.model.hero.position
        next = self.model.world.checkpoints [self.model.hero.next]
        x2, y2 = to_tuple ((next.left + next.right)/2)
        angle = math.atan2 (y2-y1, x2-x1)
        self.helper.rotation = - math.degrees (angle)
        newtimerstr = self.model.world.getElapsedTime()
        self.timerlabel.element.text = newtimerstr
        newlapstr = 'Laps: %d' % max(self.model.hero.laps, 0)
        if newlapstr != self.lapstr:
            self.lapstr = newlapstr
            self.laplabel.element.text = self.lapstr

class RaceBG (cocos.layer.Layer):

    def __init__ (self, scroller, levelId):
        super (RaceBG, self).__init__()
        try:
            self.add (cocos.sprite.Sprite (os.path.join ('backgrounds', '%s.jpg' % levelId), position=(320,240)))
        except:
            self.add (cocos.sprite.Sprite ('bg1.jpg', position=(320,240)))
        scroller.add_action (position_setter (self))


