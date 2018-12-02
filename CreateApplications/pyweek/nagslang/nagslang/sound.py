"""Sound utilities."""

from pygame import mixer

from nagslang.options import options
from nagslang.resources import resources
from nagslang.constants import (
    FREQ, BITSIZE, CHANNELS, BUFFER, DEFAULT_SOUND_VOLUME,
    DEFAULT_MUSIC_VOLUME)


class DummySound(object):
    def init(self):
        pass

    def play_sound(self, name, volume=DEFAULT_SOUND_VOLUME):
        pass

    def play_music(self, name, volume=DEFAULT_MUSIC_VOLUME):
        pass

    def pause_music(self):
        pass

    def resume_music(self):
        pass

    def stop(self):
        pass


class PygameSound(object):
    def __init__(self):
        self._sounds = {}

    def init(self):
        mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
        silence = self.load_sound("silence.ogg")
        if silence.get_length() < 1:
            raise RuntimeError("Sound load error - silence.ogg too short")
        self.play_sound("silence.ogg")

    def load_sound(self, name):
        track_name = resources.get_resource_path("sounds", name)
        sound = self._sounds.get(track_name)
        if sound is None:
            sound = self._sounds[track_name] = mixer.Sound(track_name)
        return sound

    def play_sound(self, name, volume=DEFAULT_SOUND_VOLUME):
        sound = self.load_sound(name)
        if sound is not None:
            sound.set_volume(volume)
            sound.play()

    def play_music(self, name, volume=DEFAULT_MUSIC_VOLUME):
        if not options.music:
            return
        track_name = resources.get_resource_path("music", name)
        mixer.music.load(track_name)
        mixer.music.set_volume(volume)
        mixer.music.play(-1)  # loop sound

    def pause_music(self):
        mixer.music.pause()

    def unpause_music(self):
        mixer.music.unpause()

    def stop(self):
        mixer.fadeout(1000)
        mixer.music.stop()


class SoundProxy(object):
    def __init__(self):
        self._sound = DummySound()

    def init(self):
        """Attempt to initialize the sound system."""
        if options.sound:
            try:
                pyg_sound = PygameSound()
                pyg_sound.init()
                self._sound = pyg_sound
            except Exception, err:
                print "Failed to enable sound: %r" % (err,)

    def __getattr__(self, name):
        return getattr(self._sound, name)


sound = SoundProxy()
