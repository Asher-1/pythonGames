import random
import pyglet

from gamelib import app
from gamelib.constants import *


class FadingPlayer(pyglet.media.Player):

    def __init__(self, volume=1.0):
        super(FadingPlayer, self).__init__()
        self.volume = volume
        self.fading = False
        self._fstart = 0.0
        self._fend = 0.0
        self._ftime = 1.0
        self._fremaining = 0.0
        self._fgrace = 0.0
        self._fcallback = None

    def start_fade(self, target, time, callback=None):
        self.fading = True
        self._fstart = min(1.0, max(0.0, self.volume))
        self._fend = min(1.0, max(0.0, target))
        self._ftime = time
        self._fremaining = time
        self._fgrace = 0.5
        self._fcallback = callback

    def stop_fade(self):
        callback = self._fcallback
        self.volume = self._fend
        self.fading = False
        self._fstart = self._fend
        self._ftime = 1.0
        self._fremaining = 0.0
        self._fgrace = 0.0
        self._fcallback = None
        if callback is not None:
            callback()

    def update(self, dt):
        if self.fading:
            if self._fremaining > 0.0:
                dt, self._fremaining = map(abs,
                        sorted([0.0, self._fremaining - dt]))
                progress = self._fremaining / self._ftime
                progress = 3 * progress ** 2 - 2 * progress ** 3
                self.volume = progress * self._fstart + \
                        (1 - progress) * self._fend
            if self._fremaining == 0.0 and self._fgrace > 0.0:
                self._fgrace = max(0.0, self._fgrace - abs(dt))
            if self._fremaining == 0.0 and self._fgrace == 0.0:
                self.stop_fade()


class MusicManager(pyglet.event.EventDispatcher):

    def __init__(self):
        self.player = FadingPlayer()
        self.tracks = []
        self.current = None
        self.random = False
        self.looping = False
        self.orders = []
        pyglet.clock.schedule(self.update)

    ## Useful API
    #############

    def play_track(self, track, fadeout=None, fadein=None, looping=False):
        self.tracks = [track]
        self.looping = looping
        self.random = False
        if track != self.current:
            self.next_track(fadeout=fadeout, fadein=fadein)

    def play_tracklist(self, tracks, fadeout=None, fadein=None, looping=False,
            random=False):
        self.tracks = list(tracks)
        self.looping = looping
        self.random = random
        self.next_track(fadeout=fadeout, fadein=fadein)

    def stop(self, fadeout=None):
        self.tracks = []
        self.random = False
        self.looping = False
        self.next_track(fadeout=fadeout)

    def next_track(self, fadeout=None, fadein=None):
        if not pyglet.media.have_avbin:
            return
        if not app.config.get('music'):
            return
        if self.tracks:
            if self.random:
                idx = random.randrange(-(len(self.tracks) // -2))
                track = self.tracks.pop(idx)
            else:
                track = self.tracks.pop(0)
            source = pyglet.resource.media(track, streaming=True)
            self.orders.append([self.do_fadeout, fadeout])
            self.orders.append([self.do_switch_source, track, source])
            self.orders.append([self.do_fadein, fadein])
            if self.looping:
                self.tracks.append(track)
        else:
            self.orders.append([self.do_fadeout, fadeout])
            self.orders.append([self.do_switch_source, None, None])

    ## Order functions
    ##################

    def do_fadeout(self, time):
        if time is None or not self.player.playing:
            self.player.volume = 0.0
        if self.player.volume > 0.0:
            self.player.start_fade(0.0, time)

    def do_fadein(self, time):
        if time is None or not self.player.playing:
            self.player.volume = 1.0
        if self.player.volume < 1.0:
            self.player.start_fade(1.0, time)

    def do_switch_source(self, track, source):
        self.current = track
        self.player.pause()
        volume = self.player.volume
        self.player = FadingPlayer(volume)
        if source is not None:
            self.dispatch_event("on_music_change", track)
            self.player.queue(source)
            self.player.play()
        else:
            self.dispatch_event("on_music_stop")

    ## Scheduled update
    ###################

    _lastdata = None
    def _report(self):
        data = "\n".join(["%s = %r"] * 9) % (
                'source', self.player.source,
                'fading', self.player.fading,
                'playing', self.player.playing,
                'volume', self.player.volume,
                'tracks', self.tracks,
                'current', self.current,
                'random', self.random,
                'looping', self.looping,
                'orders', self.orders,
                )
        if data != self._lastdata:
            self._lastdata = data
            print "\n" + data

    def update(self, dt):
        while not self.player.fading:
            if self.orders:
                order = self.orders.pop(0)
                order[0](*order[1:])
            else:
                break
        if not self.player.source:
            if self.current:
                self.next_track()
        self.player.update(dt)

MusicManager.register_event_type("on_music_change")
MusicManager.register_event_type("on_music_stop")

class MusicScene(object):

    tracks = [
        'music/ABreezeFromAlabama.mp3',
        'music/EliteSyncopations.mp3',
        'music/MapleLeafRag.mp3',
        'music/SomethingDoing.mp3',
        'music/TheCrushCollisionMarch.mp3',
        'music/TheEasyWinners.mp3',
        'music/WeepingWillow.mp3',
        ]

    def __init__(self):
        from gamelib import interface
        self.text = app.interface.add(interface.Text,
                valign = 'top',
                align = 'left',
                halign = 'left',
                font_size = 0.03,
                )
        self.messages = []
        app.music.push_handlers(self)

    def tick(self):
        pass

    def message(self, text):
        self.messages.append(text)
        self.messages = self.messages[-10:]
        self.text.text = u'\n'.join(self.messages)

    def on_music_change(self, track):
        self.message('Event: on_music_change(track=%r)' % track)

    def on_music_stop(self):
        self.message('Event: on_music_stop()')

    def on_key_press(self, sym, mods):
        from pyglet.window import key
        if sym == key.R:
            self.message(u'Playing tracklist with random and looping.')
            app.music.play_tracklist(self.tracks, looping=True, random=True)
        if sym == key.F:
            self.message(u'Skipping to the end of the current track.')
            app.music.player.seek(app.music.player.source.duration - 1)
            app.music.player.play()
        if sym == key.S:
            self.message(u'Playing single track without looping.')
            app.music.play_track(random.choice(self.tracks))
