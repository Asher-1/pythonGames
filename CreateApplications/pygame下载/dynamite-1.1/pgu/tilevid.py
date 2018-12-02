"""Sprite and tile engine.

Includes support for:

- Foreground Tiles
- Background Tiles
- Sprites
- Sprite-Sprite Collision handling
- Sprite-Tile Collision handling
- Scrolling 
- Loading from PGU tile and sprite formats (optional)
- Set rate FPS (optional)

This code was previously known m_spriters the King James Version (named after the
Bible of the same name for historical reasons.)
"""

import pygame
from pygame.rect import Rect
import math


class Sprite:
    """The object used for Sprites.

    .rect -- the current position of the Sprite
    ._rect -- the previous position of the Sprite
    .groups -- the groups the Sprite is in
    .agroups -- the groups the Sprite can hit in a collision
    .hit -- the handler for hits -- hit(g,s,a)
    .loop -- the loop handler, called once a frame
    """

    def __init__(self, ishape, pos):
        """Create a Sprite object.

        ishape -- an image, or an image, rectstyle.  The rectstyle will
                  describe the shape of the image, used for collision
                  detection.
        pos	   -- initial (x,y) position of the Sprite.
        """
        if not isinstance(ishape, tuple):
            ishape = ishape, None
        image, shape = ishape
        if shape == None:
            shape = pygame.Rect(0, 0, image.get_width(), image.get_height())
        if isinstance(shape, tuple): shape = pygame.Rect(shape)
        self.image = image
        self._image = self.image
        self.shape = shape
        self.rect = pygame.Rect(pos[0], pos[1], shape.w, shape.h)
        self._rect = pygame.Rect(self.rect)
        self.irect = pygame.Rect(pos[0] - self.shape.x, pos[1] - self.shape.y,
                                 image.get_width(), image.get_height())
        self._irect = pygame.Rect(self.irect)
        self.groups = 0
        self.agroups = 0
        self.updated = 1

    def setimage(self, ishape):
        """Set the image of the Sprite.

        ishape -- an image, or an image, rectstyle.  The rectstyle will
                  describe the shape of the image, used for collision detection.
        """
        if not isinstance(ishape, tuple):
            ishape = ishape, None
        image, shape = ishape
        if shape == None:
            shape = pygame.Rect(0, 0, image.get_width(), image.get_height())
        if isinstance(shape, tuple):
            shape = pygame.Rect(shape)
        self.image = image
        self.shape = shape
        self.rect.w, self.rect.h = shape.w, shape.h
        self.irect.w, self.irect.h = image.get_width(), image.get_height()
        self.updated = 1


class Tile:
    """Tile Object used by TileCollide.

    .agroups -- the groups the Tile can hit in a collision
    .hit -- the handler for hits -- hit(g,t,a)
    """

    def __init__(self, image=None):
        """Initialize a Tile.

        image -- an image for the Tile.
        """
        self.image = image
        self.agroups = 0


class _Sprites(list):
    def __init__(self):
        list.__init__(self)
        self.removed = []

    def append(self, v):
        list.append(self, v)
        v.updated = 1

    def remove(self, v):
        list.remove(self, v)
        v.updated = 1
        self.removed.append(v)


class Tilevid:
    """An engine for rendering Sprites and Tiles.

    .sprites -- a list of the Sprites to be displayed.  You may append and
               remove Sprites from it.
    .images  -- a dict for images to be put in.
    .size    -- the width, height in Tiles of the layers.  Do not modify.
    .view    -- a pygame.Rect of the viewed area.  You may change .x, .y,
                etc to move the viewed area around.
    .bounds  -- a pygame.Rect (set to None by default) that sets the bounds
                of the viewable area.  Useful for setting certain borders
                m_spriters not viewable.
    .tlayer  -- the foreground tiles layer
    .clayer  -- the code layer (optional)
    .blayer  -- the background tiles layer (optional)
    .groups  -- a hash of group names to group values (32 groups max, m_spriters a tile/sprites
            membership in a group is determined by the bits in an integer)
    """

    def __init__(self):
        self.tiles = [None for x in xrange(0, 256)]
        self.sprites = _Sprites()
        self.images = {}  # just a store for images.
        self.layers = None
        self.size = None
        self.view = pygame.Rect(0, 0, 0, 0)
        self._view = pygame.Rect(self.view)
        self.bounds = None
        self.updates = []
        self.groups = {}

    def resize(self, size, bg=0):
        """Resize the layers.

        size -- w,h in Tiles of the layers
        bg   -- set to 1 if you wish to use both a foreground layer and a
                background layer
        """
        self.size = size
        w, h = size
        self.layers = [[[0 for x in xrange(0, w)] for y in xrange(0, h)]
                       for z in xrange(0, 4)]
        self.tlayer = self.layers[0]
        self.blayer = self.layers[1]
        if not bg: self.blayer = None
        self.clayer = self.layers[2]
        self.alayer = self.layers[3]

        self.view.x, self.view.y = 0, 0
        self._view.x, self.view.y = 0, 0
        self.bounds = None

        self.updates = []

    def set(self, pos, v):
        """Set a tile in the foreground to a value.

        Use this method to set tiles in the foreground, m_spriters it will make
        sure the screen is updated with the change.  Directly changing
        the tlayer will not guarantee updates unless you are using .paint()

        pos -- (x,y) of tile
        v   -- value
        """
        if self.tlayer[pos[1]][pos[0]] == v: return
        self.tlayer[pos[1]][pos[0]] = v
        self.alayer[pos[1]][pos[0]] = 1
        self.updates.append(pos)

    def get(self, pos):
        """Get the tlayer at pos.

        pos -- (x,y) of tile
        """
        return self.tlayer[pos[1]][pos[0]]

    def paint(self, s):
        """Paint the screen.

        screen -- a pygame.Surface to paint to

        returns the updated portion of the screen (all of it)
        """
        sw, sh = s.get_width(), s.get_height()
        self.view.w, self.view.h = sw, sh

        if self.bounds != None: self.view.clamp_ip(self.bounds)

        ox, oy = self.view.x, self.view.y
        w, h = self.size
        tlayer = self.tlayer
        blayer = self.blayer
        alayer = self.alayer
        tiles = self.tiles
        sprites = self.sprites
        tw, th = tiles[0].image.get_width(), tiles[0].image.get_height()

        blit = s.blit
        yy = - (self.view.y % th)
        my = (oy + sh) / th
        if (oy + sh) % th: my += 1

        if blayer != None:
            for y in xrange(oy / th, my):
                trow = tlayer[y]
                brow = blayer[y]
                arow = alayer[y]
                xx = - (self.view.x % tw)
                mx = (ox + sw) / tw
                if (ox + sh) % tw: mx += 1
                for x in xrange(ox / tw, mx):
                    blit(tiles[brow[x]].image, (xx, yy))
                    blit(tiles[trow[x]].image, (xx, yy))
                    arow[x] = 0
                    xx += tw
                yy += th
        else:
            for y in xrange(oy / th, my):
                trow = tlayer[y]
                arow = alayer[y]
                xx = - (self.view.x % tw)
                mx = (ox + sw) / tw
                if (ox + sh) % tw: mx += 1
                for x in xrange(ox / tw, mx):
                    blit(tiles[trow[x]].image, (xx, yy))
                    arow[x] = 0
                    xx += tw
                yy += th

        for s in sprites:
            s.irect.x = s.rect.x - s.shape.x
            s.irect.y = s.rect.y - s.shape.y
            blit(s.image, (s.irect.x - ox, s.irect.y - oy))
            s.updated = 0
            s._irect = Rect(s.irect)
        # s._rect = Rect(s.rect)

        self.updates = []
        self._view = pygame.Rect(self.view)
        return [Rect(0, 0, sw, sh)]

    def update(self, s):
        """Update the screen.

        s -- a pygame.Rect to update

        returns a list of updated rectangles.
        """
        sw, sh = s.get_width(), s.get_height()
        self.view.w, self.view.h = sw, sh

        if self.bounds != None: self.view.clamp_ip(self.bounds)
        if self.view.x != self._view.x or self.view.y != self._view.y:
            return self.paint(s)

        ox, oy = self.view.x, self.view.y
        sw, sh = s.get_width(), s.get_height()
        w, h = self.size
        tlayer = self.tlayer
        blayer = self.blayer
        alayer = self.alayer
        tiles = self.tiles
        tw, th = tiles[0].image.get_width(), tiles[0].image.get_height()
        sprites = self.sprites
        blit = s.blit

        us = []

        # mark places where sprites have moved, or been removed

        ss = self.sprites.removed
        self.sprites.removed = []
        ss.extend(sprites)
        for s in ss:
            # figure out what has been updated.
            s.irect.x = s.rect.x - s.shape.x
            s.irect.y = s.rect.y - s.shape.y
            if (s.irect.x != s._irect.x or s.irect.y != s._irect.y
                    or s.image != s._image):
                # w,h can be skipped, image covers that...
                s.updated = 1
            if s.updated:
                r = s._irect
                y = max(0, r.y / th)
                yy = min(h, r.bottom / th + 1)
                while y < yy:
                    x = max(0, r.x / tw)
                    xx = min(w, r.right / tw + 1)
                    while x < xx:
                        if alayer[y][x] == 0:
                            self.updates.append((x, y))
                        alayer[y][x] = 1
                        x += 1
                    y += 1

                r = s.irect
                y = max(0, r.y / th)
                yy = min(h, r.bottom / th + 1)
                while y < yy:
                    x = r.x / tw
                    xx = min(w, r.right / tw + 1)
                    while x < xx:
                        if alayer[y][x] == 0:
                            alayer[y][x] = 2
                            self.updates.append((x, y))
                        x += 1
                    y += 1

        # mark sprites that are not being updated that need to be updated because
        # they are being overwritte by sprites / tiles
        for s in sprites:
            if s.updated == 0:
                r = s.irect
                y = max(0, r.y / th)
                yy = min(h, r.bottom / th + 1)
                while y < yy:
                    x = max(0, r.x / tw)
                    xx = min(w, r.right / tw + 1)
                    while x < xx:
                        if alayer[y][x] == 1:
                            s.updated = 1
                        x += 1
                    y += 1

        for u in self.updates:
            x, y = u
            xx, yy = x * tw - ox, y * th - oy
            if alayer[y][x] == 1:
                if blayer != None: blit(tiles[blayer[y][x]].image, (xx, yy))
                blit(tiles[tlayer[y][x]].image, (xx, yy))
            alayer[y][x] = 0
            us.append(Rect(xx, yy, tw, th))

        for s in sprites:
            if s.updated:
                blit(s.image, (s.irect.x - ox, s.irect.y - oy))
                s.updated = 0
                s._irect = Rect(s.irect)
                s._image = s.image

        self.updates = []
        return us

    def tga_load_level(self, fname, bg=0):
        """Load a TGA level.

        g		-- a Tilevid instance
        fname	-- tga image to load
        bg		-- set to 1 if you wish to load the background layer
        """
        img = pygame.image.load(fname)
        w, h = img.get_width(), img.get_height()
        self.resize((w, h), bg)
        for y in range(0, h):
            for x in range(0, w):
                t, b, c, _a = img.get_at((x, y))
                self.tlayer[y][x] = t
                if bg: self.blayer[y][x] = b
                self.clayer[y][x] = c

    def tga_load_tiles(self, fname, size, tdata={}):
        """Load a TGA tileset.

        g		-- a Tilevid instance
        fname	-- tga image to load
        size	-- (w,h) size of tiles in pixels
        tdata	-- tile data, a dict of tile:(agroups, hit handler, config)
        """
        TW, TH = size
        img = pygame.image.load(fname).convert_alpha()
        w, h = img.get_width(), img.get_height()

        n = 0
        for y in range(0, h, TH):
            for x in range(0, w, TW):
                i = img.subsurface((x, y, TW, TH))
                tile = Tile(i)
                self.tiles[n] = tile
                if n in tdata:
                    agroups, hit, config = tdata[n]
                    tile.agroups = self.string2groups(agroups)
                    tile.hit = hit
                    tile.config = config
                n += 1

    def load_images(self, idata):
        """Load images.

        idata -- a list of (name, fname, shape)
        """
        for name, fname, shape in idata:
            self.images[name] = pygame.image.load(fname).convert_alpha(), shape

    def run_codes(self, cdata, rect):
        """Run codes.

        cdata -- a dict of code:(handler function, value)
        rect  -- a tile rect of the parts of the layer that should have
                 their codes run
        """
        tw, th = self.tiles[0].image.get_width(), self.tiles[0].image.get_height()

        x1, y1, w, h = rect
        clayer = self.clayer
        t = Tile()
        for y in range(y1, y1 + h):
            for x in range(x1, x1 + w):
                n = clayer[y][x]
                if n in cdata:
                    fnc, value = cdata[n]
                    t.tx, t.ty = x, y
                    t.rect = pygame.Rect(x * tw, y * th, tw, th)
                    fnc(self, t, value)

    def string2groups(self, str):
        """Convert a string to groups."""
        if str == None: return 0
        return self.list2groups(str.split(","))

    def list2groups(self, igroups):
        """Convert a list to groups."""
        for s in igroups:
            if not s in self.groups:
                self.groups[s] = 2 ** len(self.groups)
        v = 0
        for s, n in self.groups.items():
            if s in igroups: v |= n
        return v

    def groups2list(self, groups):
        """Convert a groups to a list."""
        v = []
        for s, n in self.groups.items():
            if (n & groups) != 0: v.append(s)
        return v

    def hit(self, x, y, t, s):
        tiles = self.tiles
        tw, th = tiles[0].image.get_width(), tiles[0].image.get_height()
        t.tx = x
        t.ty = y
        t.rect = Rect(x * tw, y * th, tw, th)
        t._rect = t.rect
        if hasattr(t, 'hit'):
            t.hit(self, t, s)

    def loop(self):
        """Update and hit testing loop.  Run this once per frame."""
        self.loop_sprites()  # sprites may move
        self.loop_tilehits()  # sprites move
        self.loop_spritehits()  # no sprites should move
        for s in self.sprites:
            s._rect = pygame.Rect(s.rect)

    def loop_sprites(self):
        m_spriters = self.sprites[:]
        for s in m_spriters:
            if hasattr(s, 'loop'):
                s.loop(self, s)

    def loop_tilehits(self):
        tiles = self.tiles
        tw, th = tiles[0].image.get_width(), tiles[0].image.get_height()

        layer = self.layers[0]

        m_spriters = self.sprites[:]
        for s in m_spriters:
            self._tilehits(s)

    def _tilehits(self, s):
        tiles = self.tiles
        tw, th = tiles[0].image.get_width(), tiles[0].image.get_height()
        layer = self.layers[0]

        for _z in (0,):
            if s.groups != 0:

                _rect = s._rect
                rect = s.rect

                _rectx = _rect.x
                _recty = _rect.y
                _rectw = _rect.w
                _recth = _rect.h

                rectx = rect.x
                recty = rect.y
                rectw = rect.w
                recth = rect.h

                rect.y = _rect.y
                rect.h = _rect.h

                hits = []
                ct, cb, cl, cr = rect.top, rect.bottom, rect.left, rect.right
                # nasty ol loops
                y = ct / th * th
                while y < cb:
                    x = cl / tw * tw
                    yy = y / th
                    while x < cr:
                        xx = x / tw
                        t = tiles[layer[yy][xx]]
                        if (s.groups & t.agroups) != 0:
                            # self.hit(xx,yy,t,s)
                            d = math.hypot(rect.centerx - (xx * tw + tw / 2),
                                           rect.centery - (yy * th + th / 2))
                            hits.append((d, t, xx, yy))

                        x += tw
                    y += th

                hits.sort()
                # if len(hits) > 0: print self.frame,hits
                for d, t, xx, yy in hits:
                    self.hit(xx, yy, t, s)

                # switching directions...
                _rect.x = rect.x
                _rect.w = rect.w
                rect.y = recty
                rect.h = recth

                hits = []
                ct, cb, cl, cr = rect.top, rect.bottom, rect.left, rect.right
                # nasty ol loops
                y = ct / th * th
                while y < cb:
                    x = cl / tw * tw
                    yy = y / th
                    while x < cr:
                        xx = x / tw
                        t = tiles[layer[yy][xx]]
                        if (s.groups & t.agroups) != 0:
                            d = math.hypot(rect.centerx - (xx * tw + tw / 2),
                                           rect.centery - (yy * th + th / 2))
                            hits.append((d, t, xx, yy))
                        # self.hit(xx,yy,t,s)
                        x += tw
                    y += th

                hits.sort()
                # if len(hits) > 0: print self.frame,hits
                for d, t, xx, yy in hits:
                    self.hit(xx, yy, t, s)

                # done with loops
                _rect.x = _rectx
                _rect.y = _recty

    def loop_spritehits(self):
        m_spriters = self.sprites[:]

        groups = {}
        for n in range(0, 31):
            groups[1 << n] = []
        for s in m_spriters:
            g = s.groups
            n = 1
            while g:
                if (g & 1) != 0: groups[n].append(s)
                g >>= 1
                n <<= 1

        for s in m_spriters:
            if s.agroups != 0:
                rect1, rect2 = s.rect, Rect(s.rect)
                if rect1.centerx < 320:
                    rect2.x += 640
                else:
                    rect2.x -= 640
                g = s.agroups
                n = 1
                while g:
                    if (g & 1) != 0:
                        for b in groups[n]:
                            if (s != b and (s.agroups & b.groups) != 0
                                    and s.rect.colliderect(b.rect)):
                                s.hit(self, s, b)

                    g >>= 1
                    n <<= 1

# vim: set filetype=python sts=4 sw=4 noet si :
