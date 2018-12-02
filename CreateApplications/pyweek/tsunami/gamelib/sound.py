# Use pygame mixer if possible... AVbin is harder to install and pyglet sound
# seems to be buggy on non-mac platrforms
try:
    import pygame.mixer
except:
    class pygame():
        class mixer():
            class music():
                @staticmethod
                def load(*k, **kw): pass

                @staticmethod
                def play(*k, **kw): pass

                @staticmethod
                def stop(*k, **kw): pass

                @staticmethod
                def get_busy(*k, **kw): pass

            class Sound():
                def __init__(*k, **kw): pass

import options, data, os.path


class Settings():
    music = options.getopt('music')
    sound = options.getopt('sound')


def disable_music():
    stop_music()
    Settings.music = False


def enable_music():
    Settings.music = True


def disable_sound():
    Settings.sound = False


def enable_sound():
    Settings.sound = True


def play_music(song):
    if Settings.music:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(data.filepath(song))
        pygame.mixer.music.play(-1)


def stop_music():
    pygame.mixer.music.stop()


sound_available = True
try:
    select_sound = pygame.mixer.Sound(data.filepath(os.path.join("menu", "select.wav")))
    click_sound = pygame.mixer.Sound(data.filepath(os.path.join("menu", "click.wav")))
except:
    sound_available = False


def menu_click():
    if sound_available and Settings.sound:
        click_sound.play()


def menu_select():
    if sound_available and Settings.sound:
        select_sound.play()
