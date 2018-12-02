from __future__ import division, print_function, unicode_literals

import json
import os

from level import Level

class Profile(object):
    SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
    SAVE_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'save.dat'))

    def __init__(self):
        self.data = {}
        self.last_played = None # Session only

        # Try to load the profile if possible
        try:
            if os.path.exists(Profile.SAVE_PATH):
                with open(Profile.SAVE_PATH, 'r') as fin:
                    self.data = json.load(fin)
        except IOError:
            print('IOError: in Profile.__init__()')

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        return item in self.data

    # Works like dict.get()
    def get(self, key, default):
        return self.data.get(key, default)

    def update_result(self, level_num, skill_num, result):
        key = 'level_' + str(level_num) + '_' + str(skill_num)

        if key not in self.data:
            self.data[key] = result
        else:
            prev = self.data[key]

            if prev == Level.PERFECT_CLEAR:
                pass
            elif prev == Level.GRASS_CLEAR and result == Level.PERFECT_CLEAR:
                self.data[key] = result
            elif prev == Level.PASSED and result in (Level.GRASS_CLEAR,
                                                     Level.PERFECT_CLEAR):
                self.data[key] = result

        unlocked = self.data.get('unlocked', 1)
        if unlocked <= level_num:
            self.data['unlocked'] = level_num + 1

        self.save()

    def get_result(self, level_num, skill_num):
        key = 'level_' + str(level_num) + '_' + str(skill_num)

        if key not in self.data:
            return None
        else:
            return self.data[key]

    def save(self):
        """Save the user's profile."""
        try:
            with open(Profile.SAVE_PATH, 'w') as fout:
                json.dump(self.data, fout)
        except IOError:
            print('IOError: in Profile.save()')
