"""gamelib.config -- stored configuration data

"""

import os
import pickle
import pyglet

from gamelib.constants import *

__all__ = ['Config']


## Config #####################################################################

class Config(object):
    """Attribute access object for config values stored in a settings file.

    ::Methods::

        `Config.save_option(name, value)`
            Change the given config value and save it to the settings file.

    """

    # Defined here to prevent __setattr__ complaining.
    _values = dict(CONFIG_DEFAULTS)

    def __init__(self):
        self._saved = dict(CONFIG_DEFAULTS)
        if os.path.exists(self._save_path()):
            settings_file = open(self._save_path(), 'rb')
            self._saved.update(pickle.load(settings_file))
        self._values = dict(self._saved)

    def _save_path(self):
        path = pyglet.resource.get_settings_path(CONFIG_NAME)
        if not os.path.exists(path): os.makedirs(path)
        return os.path.join(path, 'settings.pkl')

    def __getattr__(self, name):
        if name in self._values:
            return self._values[name]
        return getattr(super(Config, self), name)

    def __setattr__(self, name, value):
        if name in self._values:
            self._values[name] = value
            return
        return super(Config, self).__setattr__(name, value)

    def save_option(self, name, value):
        if name in self._values:
            self._values[name] = value
            self._saved[name] = value
            settings_file = open(self._save_path(), 'wb')
            pickle.dump(self._saved, settings_file)
