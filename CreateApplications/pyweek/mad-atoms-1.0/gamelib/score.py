import cocos


FONT_SIZE = 18
PADDING = 12, 6


class Score(cocos.cocosnode.CocosNode):
    def __init__(self, checkpoit_callback):
        super(Score, self).__init__()
        self.checkpoit_callback = checkpoit_callback
        self.label = cocos.text.Label("", font_size=FONT_SIZE,
                                      anchor_x='right',
                                      anchor_y='top')
        self.add(self.label)
        self.score = 0

        w, h = cocos.director.director.get_window_size()
        self.position = (w - PADDING[0], h - PADDING[1])

    def on_enemy_kill(self):
        self.score += 1
        if self.score > 0 and self.score % 10 == 0:
            self.checkpoit_callback()

    def set_score(self, value):
        self._score = value
        self.label.element.text = "Score: {0:>6}".format(self._score)

    def get_score(self):
        return self._score

    score = property(get_score, set_score)
