import data
import os.path

class Options():
    attrs = ['arrow_map', 'rope_map', 'fullscreen', 'sound', 'music', 'unlocked', 'completed', 'score', 'model']
    arrow_map = 0
    rope_map = 1
    fullscreen = False
    sound = True
    music = True
    completed = ''
    unlocked = ''
    score = 0.0
    model = 'Dolphin'


def save():
    f = data.load ('config', 'w')
    for attr in Options.attrs:
        f.write("%s=%s\n" % (attr, getattr (Options, attr)))
    f.close()

def getopt (key):
    assert key in Options.attrs
    return getattr (Options, key)

def setopt (key, value):
    assert key in Options.attrs
    setattr (Options, key, value)
    save()

def load():
    try:
        f = data.load ('config', 'r')
    except IOError:
        save()
        return
    for l in f:
        kw, value = l.strip().split('=')
        assert kw in Options.attrs
        if value.isdigit(): value = int(value)
        elif value in (str(True), str(False)): value = (value == str(True))
        setattr (Options, kw, value)
    save()

load()
