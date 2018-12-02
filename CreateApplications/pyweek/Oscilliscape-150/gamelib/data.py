"""Data loaders.

Add functions here to load specific types of resources.

"""

from __future__ import division

import os

import config
import pyglet
pyglet.options['audio'] = config.audio

from pyglet import font
from pyglet import media

from common import *
from constants import *

images = {}

def filepath(filename):
    """ determine the pathe to a file in the data directory
    """
    return os.path.join(DATA_DIR, filename)

def load_file(path, mode="rb"):
    """Open a file.

    :Parameters:
        `path` : str
            The relative path from the data directory to the file.
        `mode` : str
            The mode to use when opening the file (default: "rb").

    """
    file_path = os.path.join(DATA_DIR, path)
    return open(file_path, mode)

def load_image(path):
    """
    Load an image from the graphics directory
    """
    if path not in images:
        image_path = os.path.join(DATA_DIR, "graphics", path)
        images[path] = pyglet.image.load(image_path)
    return images[path]

def load_song(path):
    """Load a music stream from the music directory.

    :Parameters:
        `path` : str
            The relative path from the music directory to the file.

    """
    song_path = os.path.join(DATA_DIR, "music", path)
    return media.load(song_path)


def load_sound(path):
    """Load a static sound source from the sounds directory.

    :Parameters:
        `path` : str
            The relative path from the sounds directory to the file.

    """
    sound_path = os.path.join(DATA_DIR, "sounds", path)
    return media.load(sound_path, streaming=False)
