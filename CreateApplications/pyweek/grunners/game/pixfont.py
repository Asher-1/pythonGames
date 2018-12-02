import pyglet
from pyglet import gl, sprite

__all__ = [ "register_font", "free_font", "get_font", ]
__version__ = 0.1

_fonts = {}
default_map = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?()@:/'., "

class PixFont(object):

    def __init__(self, name, image, width, height, font_map):
        self.name = name
        self.grid = pyglet.image.ImageGrid(image, 1, image.width//width)
        self.width = width+1
        self.height = height+1
        self.font_map = font_map

    @property
    def texture(self):
        return self.grid.texture

    def render(self, batch, x, y, text, align="left", group=None):

        if batch is None:
            batch = pyglet.graphics.Batch()

        px_len = len(text)*self.width
        if align == "center":
            x -= px_len // 2
            y -= self.height // 2
        elif align == "right":
            x -= px_len

        sprites = []
        for i, c in enumerate(text):
            s = sprite.Sprite(self.grid[self.font_map.find(c)],
                              x=x+i*self.width,
                              y=y,
                              usage="static",
                              batch=batch,
                              group=group,
                              )
            sprites.append(s)
        return SpriteText(x, y, px_len, self.height, batch, sprites)

class SpriteText(object):

    def __init__(self, x, y, width, height, batch, sprites):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sprites = sprites
        self.batch = batch

    def draw(self):
        self.batch.draw()

    def delete(self):
        for sprite in self.sprites:
            sprite.delete()
        self.sprites = []

def get_font(name):
    """
    Get a PixFont object registered with `register_font`.

    May raise `KeyError` if the font doesn't exist.
    """
    if name not in _fonts:
        raise KeyError("%r font not registered" % name)
    return _fonts[name]

def register_font(name, filename, width, height, font_map=None):
    """
    Register a PixFont.

    :Parameters:

        `name` : string
            Name of the font. It will be used to access it using `pixfont.get_font` and
            `pixfont.free_font`.
        `filename`: string
            File name of the image containing the pixel font.
        `width` : int
            Width of a character.
        `height`: int
            Height of a character.
        `font_map` : string (optional)
            String containing all the characters in the pixel font. By default the map is:

            `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?()@:/'., `

    After a font is registered by `register_font`, it can be used by obtaining a PixFont
    object with `pixfont.get_font`.

    """
    _map = font_map or default_map
    _fonts[name] = PixFont(name=name, image=pyglet.resource.image(filename), width=width, height=height, font_map=_map)
    gl.glTexParameteri(_fonts[name].texture.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(_fonts[name].texture.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(_fonts[name].texture.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(_fonts[name].texture.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

def free_font(name):
    """
    Free an registered font.

    May raise `KeyError` if the font doesn't exist.
    """
    if name not in _fonts:
        raise KeyError("%r font not registered" % name)
    del _fonts[name]

