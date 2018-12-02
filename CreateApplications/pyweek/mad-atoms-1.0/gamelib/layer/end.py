# Six hours to pyweek ends -- Lets write at least one spagetti file...
import time
import urllib2
import urllib
import json

import pyglet

import cocos
from cocos.scenes.transitions import FadeTRTransition

import gamelib.data as d
from gamelib.loading import Loading


COLOR = (0, 81, 109, 255)
TOP10_URL = 'http://pyweek14.petraszd.com/top-10/'
POST_URL = 'http://pyweek14.petraszd.com/submit/'
TOP10_FONT_SIZE = 18

SCORE_SIZE = 30

MSG = 'Type Your name and press ENTER to submit (ESC to play again)'
MSG_SUBMITTING = 'Submitting...'
MSG_AFTER = 'Press ANY key to play again'
MSG_SIZE = 14

NAME_SIZE = 30
NAME_DEFAULT = '<Your Name>'

MAX_SIZE = 15

ERROR_MSG = 'Network error...'


class EndLayer(cocos.layer.Layer):
    """ Ugliest class within project

    Hey, but at least it has docstring so it is like scrum and agile...
    """
    is_event_handler = True

    def __init__(self, game_scene_class, score):
        super(EndLayer, self).__init__()
        self.score = score
        self.current_name = ''
        self.submited = False
        self.allow_restart = False
        self.game_scene_class = game_scene_class
        self.add(cocos.sprite.Sprite(d.img('end'), anchor=(0, 0)), z=0)
        self.loading = Loading()
        self.add(self.loading)

        self.score_label = cocos.text.Label(self.get_score_text(),
                                            font_size=SCORE_SIZE,
                                            color=COLOR,
                                            anchor_y='top',
                                            anchor_x='left')
        self.score_label.position = (120, 500)
        self.add(self.score_label, z=1)

        self.name_label = cocos.text.Label(NAME_DEFAULT,
                                           font_size=NAME_SIZE,
                                           color=COLOR,
                                           anchor_y='top',
                                           anchor_x='left')
        self.name_label.position = (120, 450)
        self.add(self.name_label, z=1)

        self.msg_label = cocos.text.Label(MSG, font_size=MSG_SIZE,
                                          color=COLOR,
                                          anchor_y='top',
                                          anchor_x='left')
        self.msg_label.position = (120, 400)
        self.add(self.msg_label, z=1)

        self.top10_nr = self.get_top10_label(60, 'right')
        self.top10_nr.position = (120, 370)
        self.add(self.top10_nr, z=1)

        self.top10_names = self.get_top10_label(300, 'center')
        self.top10_names.position = (180, 370)
        self.add(self.top10_names, z=1)

        self.top10_scores = self.get_top10_label(100, 'right')
        self.top10_scores.position = (480, 370)
        self.add(self.top10_scores, z=1)

        self.loading.turon()
        pyglet.clock.schedule_once(self.try_to_display_scores, 0.1)

    def get_score_text(self):
        return 'Score: {0}'.format(self.score)

    def get_top10_label(self, width, halign):
        return cocos.text.Label('', font_size=TOP10_FONT_SIZE,
                                color=COLOR,
                                anchor_y='top',
                                anchor_x='left',
                                halign=halign,
                                width=width,
                                multiline=True)

    def try_to_display_scores(self, dt):
        self.update_top10_labels(self.get_online_data())
        self.loading.turoff()

    def update_top10_labels(self, data):
        if not data:
            return

        nrs = []
        names = []
        scores = []
        for i, item in enumerate(self.get_online_data()):
            nrs.append('{0}.'.format(i + 1))
            names.append(item['fields']['playername'][:MAX_SIZE])
            scores.append(str(item['fields']['score']))
        self.top10_nr.element.text = '\n'.join(nrs)
        self.top10_names.element.text = '\n'.join(names)
        self.top10_scores.element.text = '\n'.join(scores)

    def get_online_data(self):
        try:
            handle = urllib2.urlopen(TOP10_URL + '?' + str(int(time.time())))
            data = json.load(handle)
            handle.close()
            return data
        except: # Sh*t happens pattern
            self.set_error()
            return []

    def on_key_press (self, key, modifiers):
        if self.allow_restart:
            self.restart_game_delayed()
            return True

        if key == pyglet.window.key.BACKSPACE:
            if self.current_name:
                self.current_name = self.current_name[:-1]
        elif key == pyglet.window.key.SPACE:
            self.current_name += ' '
        elif key >= pyglet.window.key.A and key <= pyglet.window.key.Z:
            self.current_name += pyglet.window.key.symbol_string(key)
        elif key in [pyglet.window.key.RETURN, pyglet.window.key.ENTER]:
            if self.current_name:
                self.submited = True
                self.loading.turon()
                self.msg_label.element.text = MSG_SUBMITTING
                pyglet.clock.schedule_once(self.try_to_submit, 0.1)
        elif key == pyglet.window.key.ESCAPE:
            self.restart_game_delayed()
            return True
        self.current_name = self.current_name[:MAX_SIZE]
        self.update_name_label()

    def restart_game_delayed(self):
        self.submited = True
        self.allow_restart = True
        self.loading.turon()
        pyglet.clock.schedule_once(self.restart_game, 0.1)

    def restart_game(self, dt):
        cocos.director.director.replace(
            FadeTRTransition(self.game_scene_class()))

    def update_name_label(self):
        if self.current_name:
            self.name_label.element.text = self.current_name
        else:
            self.name_label.element.text = NAME_DEFAULT

    def try_to_submit(self, dt):
        self.update_top10_labels(self.post_data())
        self.msg_label.element.text = MSG_AFTER
        self.loading.turoff()
        self.allow_restart = True

    def set_error(self):
        self.top10_names.element.text = ERROR_MSG # Best place to store error msg...

    def post_data(self):
        try:
            data = urllib.urlencode({'playername': self.current_name,
                                     'score': self.score})
            req = urllib2.Request(POST_URL + '?' + str(int(time.time())), data)
            handle = urllib2.urlopen(req)
            result = json.load(handle)
            handle.close()
            return result
        except: # Sh*t happens patter is the best pattern
            self.set_error()
            return []
