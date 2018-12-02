import os

import pyglet


__all__ = ['img']


data_path = 'data'
images_path = os.path.join(data_path, 'images')
soundfx_path = os.path.join(data_path, 'soundfx')
music_path = os.path.join(data_path, 'music')


def img(name):
    return pyglet.image.load(os.path.join(images_path, '{0}.png'.format(name)))


def soundfx(name):
    path = os.path.join(soundfx_path, '{0}.wav'.format(name))
    return pyglet.media.load(path, streaming=False)


def music(name):
    path = os.path.join(music_path, '{0}.ogg'.format(name))
    return pyglet.media.load(path)


def play_music():
    try:
        player = pyglet.media.Player()
        player.eos_action = pyglet.media.Player.EOS_LOOP
        player.queue(music('nebula'))
        player.play()
    except pyglet.media.riff.WAVEFormatException:
        pass # Can't play music, but game still is playable


class SoundFxHolder(object):
    def __init__(self, soundfx_names):
        self.soundfxs = {}
        for name in soundfx_names:
            try:
                self.soundfxs[name] = soundfx(name)
            except pyglet.media.riff.WAVEFormatException:
                pass

    def play(self, name, volume=1.0):
        if name in self.soundfxs:
            self.soundfxs[name].play().volume = volume
