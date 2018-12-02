"""Some utils"""

import pyglet
from pyglet import gl

def texture_parameters(texture, clamp=True):
    gl.glTexParameteri(texture.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(texture.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    if clamp:
        gl.glTexParameteri(texture.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(texture.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    else:
        gl.glTexParameteri(texture.target, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(texture.target, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

def get_texture(filename):
    image = pyglet.resource.image(filename)
    texture = image.get_texture()
    texture_parameters(texture)

    return texture

def get_texture_sequence(filename, tilewidth=32, tileheight=32, margin=1, spacing=1):
    image = pyglet.resource.image(filename)
    region = image.get_region(margin, margin, image.width-margin*2, image.height-margin*2)
    grid = pyglet.image.ImageGrid(region,
                                  region.height/tileheight,
                                  region.width/tilewidth,
                                  row_padding=spacing,
                                  column_padding=spacing,
                                  )

    texture = grid.get_texture_sequence()
    texture_parameters(texture)

    return texture

