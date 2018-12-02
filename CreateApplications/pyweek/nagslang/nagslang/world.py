# The world object
#
# This is a global object for tracking state across scenes and all that

import os
import sys

import pymunk

from nagslang.level import Level
from nagslang.protagonist import Protagonist
from nagslang.yamlish import dump, load


class World(object):

    def __init__(self):
        self.__dict__['protagonist'] = Protagonist(
            pymunk.Space(), self, Level.game_starting_point()[1])
        self.reset(load=True)

    def reset(self, load=False):
        self.__dict__['_data'] = {
            'attacks': 0,
            'deaths': 0,
            'transformations': 0,
            'kills': 0,
            'rooms': 0,
            'level': (None, (None, None)),
            'level_state': {},
            'inventory': set(),
        }
        if load:
            self.load()
        else:
            self.save()

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError()

    def __setattr__(self, name, value):
        if name not in self._data:
            raise AttributeError("Worlds don't have a %s property" % name)
        self._data[name] = value

    def _save_location(self):
        app = 'nagslang'
        if sys.platform.startswith('win'):
            if 'APPDATA' in os.environ:
                return os.path.join(os.environ['APPDATA'], app)
            return os.path.join(os.path.expanduser('~'), '.' + app)
        elif 'XDG_DATA_HOME' in os.environ:
            return os.path.join(os.environ['XDG_DATA_HOME'], app)
        return os.path.join(os.path.expanduser('~'), '.local', 'share', app)

    def save(self):
        data = self._data.copy()
        data['inventory'] = sorted(data['inventory'])
        fn = self._save_location()
        if not os.path.isdir(os.path.dirname(fn)):
            os.makedirs(os.path.dirname(fn))
        with open(fn, 'w') as f:
            dump(data, f)

    def load(self):
        fn = self._save_location()
        if not os.path.exists(fn):
            return False
        with open(fn) as f:
            data = load(f)
        data['inventory'] = set(data['inventory'])
        data['level'] = (data['level'][0], tuple(data['level'][1]))
        self.__dict__['_data'].update(data)
        return True

    def get_formatted_stats(self):
        return (('Times transformed: %(transformations)d\n'
                 'Shots fired/claws drawn: %(attacks)d\n'
                 'Enemies killed: %(kills)d\n'
                 'Rooms entered: %(rooms)d\n'
                 ) % self._data)
