import cocos

import gamelib.data as d


PADDING = 5


class Loading(cocos.sprite.Sprite):
    def __init__(self):
        super(Loading, self).__init__(d.img('loading'))
        w, h = cocos.director.director.get_window_size()
        self.position = (w / 2.0, self.image.height / 2.0 + PADDING)
        self.turoff()

    def turon(self):
        self.opacity = 255

    def turoff(self):
        self.opacity = 0
