import cocos

import gamelib.data as d


class StaticImageLayer(cocos.layer.Layer):
    def __init__(self):
        super(StaticImageLayer, self).__init__()
        s = cocos.sprite.Sprite(d.img(self.get_img_name()), anchor=(0, 0))
        self.add(s)


class BackgroundLayer(StaticImageLayer):
    def get_img_name(self):
        return 'background'


class SideSignsLayer(StaticImageLayer):
    def get_img_name(self):
        return 'side-signs'


class CornersLayer(StaticImageLayer):
    def get_img_name(self):
        return 'corners'
