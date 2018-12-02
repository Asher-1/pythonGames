import cocos

from gamelib.layer.static import BackgroundLayer, SideSignsLayer, CornersLayer
from gamelib.layer.start import StartLayer
from gamelib.layer.end import EndLayer
from gamelib.layer.game import GameLayer


class GameScene(cocos.scene.Scene):
    def __init__(self, *args, **kwargs):
        super(GameScene, self).__init__(*args, **kwargs)
        self.add(BackgroundLayer(), z=0)
        self.add(GameLayer(EndScene), z=1)
        self.add(SideSignsLayer(), z=2)
        self.add(CornersLayer(), z=3)


class StartScene(cocos.scene.Scene):
    def __init__(self, *args, **kwargs):
        super(StartScene, self).__init__(*args, **kwargs)
        self.add(BackgroundLayer(), z=0)
        self.add(StartLayer(GameScene), z=1)
        self.add(CornersLayer(), z=2)


class EndScene(cocos.scene.Scene):
    def __init__(self, score, *args, **kwargs):
        super(EndScene, self).__init__(*args, **kwargs)
        self.add(BackgroundLayer(), z=0)
        self.add(EndLayer(GameScene, score), z=1)
        self.add(CornersLayer(), z=2)
