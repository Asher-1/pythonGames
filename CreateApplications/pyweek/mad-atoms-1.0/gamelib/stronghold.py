import cocos
from cocos.actions import FadeIn, FadeOut, Repeat

import gamelib.data as d


class Stronghold(cocos.cocosnode.CocosNode):
    def __init__(self):
        super(Stronghold, self).__init__()
        self.normal = cocos.sprite.Sprite(d.img('base'), anchor=(0, 0))
        self.damaged = cocos.sprite.Sprite(d.img('base-damaged'),
                                           opacity=0, anchor=(0, 0))
        self.add(self.normal, z=1)
        self.add(self.damaged, z=0)

    def to_damaged(self):
        self.normal.do(Repeat(FadeOut(0.2) + FadeIn(0.2)))
        self.damaged.do(Repeat(FadeIn(0.2) + FadeOut(0.2)))
