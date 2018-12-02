import pyglet

import cocos
from cocos.scenes.transitions import FadeTRTransition

import gamelib.data as d
from gamelib.loading import Loading


class StartLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, game_scene_class):
        super(StartLayer, self).__init__()
        self.game_scene_class = game_scene_class
        self.add(cocos.sprite.Sprite(d.img('start'), anchor=(0, 0)), z=0)
        self.loading = Loading()
        self.add(self.loading)

    def on_key_press (self, key, modifiers):
        if key != pyglet.window.key.ESCAPE:
            self.loading.turon()
            pyglet.clock.schedule_once(self.play_game, 0.2)

    def play_game(self, dt):
        cocos.director.director.replace(
            FadeTRTransition(self.game_scene_class()))
