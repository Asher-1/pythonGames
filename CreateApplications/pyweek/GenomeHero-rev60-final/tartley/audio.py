import pyglet
import json


MAX_SOUNDS = 16

################################################################################
############################################################## SoundManager ####
################################################################################

class SoundManager (object):

    def __init__(self, list_file=None):
        self._sounds = {}
        self._music = {}
        if list_file:
            self.load_from_list(list_file)

        self.music_players = {}
        self.current_music_key = None
        self.current_music_player = None
        self.next_music = None

        self.fading = False
        self.fading_in = False
        

    def load_sound(self, key, filename):
        print "Loading %s as %s" % (key, filename)
        s = pyglet.media.load(filename, streaming=False)
        self._sounds[key] = s

    def load_music(self, key, filename):
        print "Loading %s as %s" % (key, filename)
        s = pyglet.media.load(filename, streaming=True)
        self._music[key] = s
        
    def play_sound(self, key):
        if self._sounds.has_key(key):
            self._sounds[key].play()

    def play_music(self, key):
        print "Playing music:", key
        if self.current_music_key == key:
            print "That is already playing!", key
            return
        elif self.music_players.has_key(key):
            p = self.music_players[key]
            self.fading_in = True
            p.play()
            self.current_music_player = p
            self.current_music_key = key
        elif self._music.has_key(key):
            p = self._music[key].play()
            self.current_music_player = p
            self.current_music_key = key
            self.music_players[key] = p
        else:
            print key, "Song Not found."
            
    def pause_music(self):
        if self.current_music_player:
            self.current_music_player.pause()
            
    def resume_music(self):
         if self.current_music_player:
            self.current_music_player.play()
            
    def load_from_list(self, list_file):
        print "Loading sounds and music from: %s" % list_file
        f = open(list_file)
        buf = f.read()
        f.close()
        data = json.loads(buf)
        for s in data["sounds"]:
            self.load_sound(s, data["sounds"][s])
        for m in data["music"]:
            self.load_music(m, data["music"][m])

    def fade(self, dt, speed=0.4):
        
        if not self.current_music_player:
            return
        if self.current_music_player.volume > 0:
            self.current_music_player.volume -= speed*dt
        else:
            self.current_music_player.pause()
            self.fading = False
            if self.next_music:
                self.play_music(self.next_music)
                self.current_music_key = self.next_music
                self.next_music = None


    def fade_in(self, dt, speed=0.4):
        if not self.current_music_player:
            return
        if self.current_music_player.volume < 1:
            self.current_music_player.volume += speed*dt
        else:
            self.fading_in = False


    def fade_to(self, key, speed=0.8):
        if not self.current_music_player:
            self.play_music(key)
            return
        if self.current_music_key == key:
            print "That is playing, fading to that would be dumb"
        self.fading = True
        self.next_music = key
        print "Setting fade from %s to %s" % (self.current_music_key, key)

    def set_volume(self, v):
        if self.current_music_player:
            self.current_music_player.volume = v

    def update(self, dt):
        if self.fading:
            self.fade(dt)
        if self.fading_in:
            self.fade_in(dt)
        
_sm = SoundManager('data/sound_list.lmp')

def update(dt):
    _sm.update(dt)

def play_sound(sound):
    _sm.play_sound(sound)

def play_music(track):
    _sm.play_music(track)

def play_music_fade(track, speed=0.5):
    _sm.fade_to(track, speed)

def attenuate_music():
    _sm.set_volume(0.4)

def unattenuate_music():
    _sm.set_volume(1.0)
    
def playing():
    if _sm.current_music_player:
        return True
    else:
        return False
        
def pause_music():
    _sm.pause_music()
    
def resume_music():
    _sm.resume_music()
