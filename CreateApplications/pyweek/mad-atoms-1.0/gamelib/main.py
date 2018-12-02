import cocos

from gamelib.scenes import StartScene
import gamelib.data


def main():
    gamelib.data.play_music()
    cocos.director.director.init(width=800, height=600)
    cocos.director.director.run(StartScene())
