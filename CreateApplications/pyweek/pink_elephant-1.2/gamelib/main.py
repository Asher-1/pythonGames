import ctypes
import itertools
import math
import random
import pyglet
pyglet.options['debug_gl'] = False

from pyglet.gl import *
pyglet.resource.path = ['data']
pyglet.resource.reindex()

keys = pyglet.window.key
KEYS = {
  keys.LEFT: 'left',
  keys.RIGHT: 'right',
  keys.DOWN: 'down',
  keys.UP: 'up',
  keys.SPACE: 'jump',
  }


class Game(object):
  def __init__(self):
    self.window = pyglet.window.Window(width=800, height=600, caption='Flight of the Pink Elephant')
#    self.window.set_icon(pyglet.resource.image('icon16.png').get_image_data(), pyglet.resource.image('icon32.png').get_image_data(), pyglet.resource.image('icon128.png').get_image_data(), pyglet.resource.image('icon512.png').get_image_data())
    self.keys = set()
    @self.window.event
    def on_draw():
      self.window.clear()
      self.draw()
      self.window.invalid = False
    @self.window.event
    def on_key_press(symbol, modifiers):
      if symbol in KEYS:
        game.keys.add(KEYS[symbol])
    @self.window.event
    def on_key_release(symbol, modifiers):
      if symbol in KEYS:
        game.keys.discard(KEYS[symbol])
    @self.window.event
    def on_resize(width, height):
      glViewport(0, 0, width, height)
      glMatrixMode(GL_PROJECTION)
      glLoadIdentity()
#      gluPerspective(65, width / float(height), .1, 1000)
      glOrtho(0, width, 0, height, -1000, 1000)
      glMatrixMode(GL_MODELVIEW)
      return pyglet.event.EVENT_HANDLED

    pyglet.clock.schedule_interval(self.think, 1 / 40.0)

    self.music = pyglet.media.Player()
    try:
      self.music.queue(pyglet.resource.media('music.ogg'))
      self.music.eos_action = self.music.EOS_LOOP
    except:
      print 'Music is off. (AVbin is missing or does not support Ogg/Vorbis.)'
    else:
      self.music.play()

  def start(self):
    glClearColor(0.8, 0.8, 0.8, 1)
    glDisable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    self.elephant = Elephant(20)
    self.elephant.x = 100
    self.elephant.z = -300
    self.objects = [self.elephant]
    self.pink_elephant = pink_elephant = PinkElephant(18)
    pink_elephant.x = -100
    pink_elephant.z = 300
    self.objects.append(pink_elephant)
    for i in range(60):
      self.objects.append(Tree(random.gauss(0, 300), random.gauss(0, 300)))
    def hutposition():
      while True:
        px, pz = random.gauss(pink_elephant.x, 200), random.gauss(pink_elephant.z, 200)
        dx = pink_elephant.x - px
        dz = pink_elephant.z - pz
        d = math.sqrt(dx ** 2 + dz ** 2)
        if d > 100:
          dx = game.elephant.x - px
          dz = game.elephant.z - pz
          d = math.sqrt(dx ** 2 + dz ** 2)
          if d > HUT_VISIBILITY:
            return px, pz
    for i in range(10):
      self.objects.append(Hut(*hutposition()))
    for i in range(10):
      cannibal = Cannibal(pink_elephant.x + 50 * math.cos(math.pi * 2 * i / 10), pink_elephant.z - 50 * math.sin(math.pi * 2 * i / 10))
      cannibal.elephant = pink_elephant
      self.objects.append(cannibal)
      cannibal.rope = HomingRope(cannibal, pink_elephant)
      cannibal.rope.attached = pink_elephant, dist(pink_elephant, cannibal), 0, -2 * pink_elephant.radius, 0, 0
      self.objects.append(cannibal.rope)
    pyglet.app.run()

  def draw(self):
    glLoadIdentity()
    glTranslatef(350, 250, 0)
    glLightfv(GL_LIGHT0, GL_POSITION, (ctypes.c_float * 4)(0, 0, 1, 0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (ctypes.c_float * 3)(1, 1, 1))
    glRotatef(30, 1, 0, 0)
    glRotatef(180, 0, 0, 1)
    glRotatef(220, 0, 1, 0)
    for obj in self.objects:
      obj.draw()

  def think(self, dt):
    self.window.invalid = True
    for obj in self.objects:
      obj.think()


class Elephant(object):
  def __init__(self, radius=50, color=(0.5, 0.5, 0.5)):
    self.radius = float(radius)
    self.invmass = 50 / self.radius
    self.x = 0
    self.y = 0
    self.z = 0
    self.structure = [
        Block(0, 0, 0, 100, 90, 100, color=color), # Body.
        Block(20, -10, -20, 60, 60, 60, color=color), # Head.
        Block(-20, -10, -10, 40, 80, 10, color=color), # Right ear.
        Block(80, -10, -10, 40, 80, 10, color=color), # Left ear.
        Block(45, 30, -30, 10, 60, 10, color=color), # Trunk.
        Block(35, 20, -22, 10, 10, 10, color=(0.2, 0.2, 0.2)), # Right eye.
        Block(55, 20, -22, 10, 10, 10, color=(0.2, 0.2, 0.2)), # Left eye.
        Block(37.5, 46, -30, 5, 5, 20, color=(1, 1, 1)), # Right tusk.
        Block(57.5, 46, -30, 5, 5, 20, color=(1, 1, 1)), # Left tusk.
        Block(45, 0, 100, 10, 30, 10, color=color), # Tail.
        Block(0, 90, 0, 20, 10, 20, color=color), # Front right foot.
        Block(80, 90, 0, 20, 10, 20, color=color), # Front left foot.
        Block(0, 90, 80, 20, 10, 20, color=color), # Back right foot.
        Block(80, 90, 80, 20, 10, 20, color=color), # Back left foot.
        ]
    for block in self.structure:
      block.x *= self.radius / 50; block.y *= self.radius / 50; block.z *= self.radius / 50
      block.sx *= self.radius / 50; block.sy *= self.radius / 50; block.sz *= self.radius / 50
    self.vertexlist = vertexlist(self.structure[:-4])
    self.footvertexlists = [vertexlist([self.structure[i - 4]]) for i in range(4)]
    self.footpositions = [0, 0, 0, 0]
    self.center = self.radius, self.radius * 2, self.radius
    self.walk = 0
    self.dir = 0
    self.charge = 0
    self.max_charge = 200
    self.walksound = 999
    self.walksound_type = 0
  def draw(self):
    glPushMatrix()
    glTranslatef(self.x, self.y, self.z)
    glRotatef(self.dir, 0, 1, 0)
    glTranslatef(-self.center[0], -self.center[1], -self.center[2])
    self.vertexlist.draw(GL_QUADS)
    for y, foot in zip(self.footpositions, self.footvertexlists):
      glTranslatef(0, y - self.structure[-1].sy, 0)
      foot.draw(GL_QUADS)
      glTranslatef(0, self.structure[-1].sy - y, 0)
    glPopMatrix()
  def attachedropes(self):
    return [obj for obj in game.objects if getattr(obj, 'attached', None) and obj.attached[0] == self]
  def think(self):
    self.y += 0.5
    if self.y > 0:
      self.y = 0

    speed = math.sqrt(self.invmass)
    turn_mod = math.exp(-0.1 * len(self.attachedropes()))
    if 'left' in game.keys:
      self.dir -= speed * turn_mod
    if 'right' in game.keys:
      self.dir += speed * turn_mod
    if 'up' in game.keys:
      if not self.attachedropes() and self.charge < self.max_charge:
        self.charge += 1
      elif self.attachedropes() and self.charge > 0:
        self.charge -= 1
      speed *= 1 + 0.01 * self.charge
      self.x -= speed * math.sin(self.dir * math.pi / 180)
      self.z -= speed * math.cos(self.dir * math.pi / 180)
    else:
      self.charge = 0
    if 'down' in game.keys:
      self.x += speed * math.sin(self.dir * math.pi / 180)
      self.z += speed * math.cos(self.dir * math.pi / 180)
    if game.keys & set('left right up down'.split()):
      if self.walksound > 20 - self.charge / 20:
        play('elephant-step-%d' % self.walksound_type)
        self.walksound_type = 1 - self.walksound_type
        self.walksound = 0
      self.walksound += 1
      self.walk += 1
      for i, j in zip([0, 2, 1, 3], range(4)):
        self.footpositions[j] = min(10, 2 + 1.3 * abs((1.2 * self.walk + i * 20. / 4) % 20 - 10)) * self.radius / 50
    else:
      for j in range(4):
        self.footpositions[j] = self.structure[-1].sy
  def covers(self, x, z):
    dx = x - self.x
    dz = z - self.z
    a = self.dir * math.pi / 180
    return -self.radius < math.cos(a) * dx - math.sin(a) * dz < self.radius and \
           -self.radius < math.sin(a) * dx + math.cos(a) * dz < self.radius

class PinkElephant(Elephant):
  def __init__(self, radius, color=(0.8, 0.5, 0.5)):
    super(PinkElephant, self).__init__(radius, color)
    self.victory = False
  def think(self):
    self.y += 0.5
    if self.y > 0:
      self.y = 0
    
    dx = game.elephant.x - self.x
    dz = game.elephant.z - self.z
    d = math.sqrt(dx ** 2 + dz ** 2)
    if not self.attachedropes() and not self.victory:
      self.victory = True
      play('victory')
    if not self.attachedropes() and d > 100:
      if self.walksound > 20 - self.charge / 20:
        play('pink-elephant-step-%d' % self.walksound_type)
        self.walksound_type = 1 - self.walksound_type
        self.walksound = 0
      self.walksound += 1
      speed = math.sqrt(self.invmass)
      wdir = math.atan2(dx, dz) * 180 / math.pi
      ddir = (wdir - self.dir) % 360 - 180
      if ddir > speed:
        self.dir += speed
      elif ddir < -speed:
        self.dir -= speed
      if -10 < ddir < 10:
        self.x -= speed * math.sin(self.dir * math.pi / 180)
        self.z -= speed * math.cos(self.dir * math.pi / 180)
      self.walk += 1
      for i, j in zip([0, 2, 1, 3], range(4)):
        self.footpositions[j] = min(10, 2 + 1.3 * abs((1.2 * self.walk + i * 20. / 4) % 20 - 10)) * self.radius / 50
    else:
      for j in range(4):
        self.footpositions[j] = self.structure[-1].sy
      

MAX_ROPE_LENGTH = 200
class Cannibal(object):
  def __init__(self, x, z):
    self.invmass = 5
    self.x = x
    self.y = -20
    self.z = z
    self.structure = [
        Block(-3, -10, -3, 6, 10, 6, color=(0.4, 0.2, 0.2)), # Body.
        ]
    self.vertexlist = vertexlist(self.structure)
    self.ox, self.oy, self.oz = self.x, self.y, self.z
    self.rope = None
    self.elephant = game.elephant
  def draw(self):
    glPushMatrix()
    glTranslatef(self.x, self.y, self.z)
    self.vertexlist.draw(GL_QUADS)
    glPopMatrix()
  def think(self):
    self.x += 0.95 * (self.x - self.ox); self.ox = self.x
    self.y += 0.9999 * (self.y - self.oy); self.oy = self.y
    self.z += 0.95 * (self.z - self.oz); self.oz = self.z
    self.y += 1
    if self.y > 0:
      self.y = 0
    
    dx = self.elephant.x - self.x
    dz = self.elephant.z - self.z
    d = math.sqrt(dx ** 2 + dz ** 2)
    rope_range = min(MAX_ROPE_LENGTH, self.elephant.radius * 3)
    wx = wz = 0
    if self.rope and self.rope.attached or 0 < d < rope_range * 0.9 and not self.rope:
      wx = -dx / d
      wz = -dz / d
    elif d < rope_range:
      if not self.rope:
#        self.rope = Rope(self, dx * (0.9 + 0.2 * random.random()), dz * (0.9 + 0.2 * random.random()))
        play('rope')
        self.rope = HomingRope(self, self.elephant)
        game.objects.append(self.rope)
    elif d > 0 and (not self.rope or self.rope.attached):
      wx = dx / d
      wz = dz / d
    # aversion
    for obj in game.objects:
      if obj.invmass > self.invmass: continue
      dx = obj.x - self.x
      dz = obj.z - self.z
      d2 = dx ** 2 + dz ** 2
      if d2 > 0:
        wx -= dx / d2
        wz -= dz / d2
    if self.rope:
      speed = 0.3
    else:
      speed = 0.5
    w = math.sqrt(wx ** 2 + wz ** 2)
    if w < 1: w = 1
    self.x += speed * wx / w
    self.z += speed * wz / w
    if game.elephant.covers(self.x, self.z) or game.pink_elephant.covers(self.x, self.z):
      play('cannibal-trampled')
      self.remove()
  def remove(self):
    if self.rope:
      self.rope.remove()
    game.objects.remove(self)

class Rope(object):
  def __init__(self, owner, tx, tz):
    self.invmass = 1000
    self.owner = owner
    self.attached = None
    d = math.sqrt(tx ** 2 + tz ** 2)
    self.x, self.y, self.z = self.owner.x, self.owner.y, self.owner.z
    self.vx = 2 * tx / d
    self.vz = 2 * tz / d
    self.vy = -10
    self.vx *= d / 200
    self.vy *= d / 200
    self.vz *= d / 200
  def draw(self):
    drawline(self.owner.x, self.owner.y, self.owner.z, self.x, self.y, self.z)
  def think(self):
    if not self.attached:
      self.x += self.vx
      self.y += self.vy
      self.z += self.vz
      self.vy += 0.2
      if self.y > 0:
        self.remove()
      self.attached = self.hit(game.elephant)
    else:
      elephant, length, rx, ry, rz, dir = self.attached
      # position correctly
      dir -= elephant.dir * math.pi / 180
      self.x = elephant.x + rx * math.cos(dir) - rz * math.sin(dir)
      self.y = elephant.y + ry
      self.z = elephant.z + rx * math.sin(dir) + rz * math.cos(dir)
      # physics
      dx = self.x - self.owner.x
      dy = self.y - self.owner.y
      dz = self.z - self.owner.z
      d = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
      if d > length:
        total_invmass = float(elephant.invmass + self.owner.invmass)
        elephant.x -= (elephant.invmass / total_invmass) * (dx / d) * (d - length)
        elephant.y -= (elephant.invmass / total_invmass) * (dy / d) * (d - length)
        elephant.z -= (elephant.invmass / total_invmass) * (dz / d) * (d - length)
        self.owner.x += (self.owner.invmass / total_invmass) * (dx / d) * (d - length)
        self.owner.y += (self.owner.invmass / total_invmass) * (dy / d) * (d - length)
        self.owner.z += (self.owner.invmass / total_invmass) * (dz / d) * (d - length)
  def hit(self, elephant):
    # High-tech collision detection at work.
    dx = self.x - elephant.x
    dy = self.y - elephant.y + elephant.radius
    dz = self.z - elephant.z
    d = math.sqrt(dx ** 2 + dz ** 2)
    if d < elephant.radius and abs(dy) < elephant.radius:
      return elephant, dist(self, self.owner), dx, dy - elephant.radius, dz, elephant.dir * math.pi / 180
  def remove(self):
    self.owner.rope = None
    game.objects.remove(self)

class HomingRope(object):
  def __init__(self, owner, elephant):
    self.invmass = 1000
    self.owner = owner
    self.attached = None
    self.elephant = elephant
    self.x, self.y, self.z = self.owner.x, self.owner.y, self.owner.z
    self.speed = 5
    self.height = 100
  def draw(self):
    drawline(self.owner.x, self.owner.y, self.owner.z, self.x, self.y, self.z)
  def think(self):
    if not self.attached:
      dex = self.elephant.x - self.x
      dez = self.elephant.z - self.z
      de = math.sqrt(dex ** 2 + dez ** 2)
      self.x += self.speed * dex / de
      self.z += self.speed * dez / de
      dox = self.owner.x - self.x
      doz = self.owner.z - self.z
      do = math.sqrt(dox ** 2 + doz ** 2)
      if do > MAX_ROPE_LENGTH:
        self.remove()
      x0 = (do + de) / 2
      x = (do - x0) / x0
      self.y = -self.height * (1 - x ** 2)
      self.attached = self.hit(self.elephant)
    else:
      elephant, length, rx, ry, rz, dir = self.attached
      # position correctly
      dir -= elephant.dir * math.pi / 180
      self.x = elephant.x + rx * math.cos(dir) - rz * math.sin(dir)
      self.y = elephant.y + ry
      self.z = elephant.z + rx * math.sin(dir) + rz * math.cos(dir)
      # physics
      dx = self.x - self.owner.x
      dy = self.y - self.owner.y
      dz = self.z - self.owner.z
      d = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
      if d > length:
        total_invmass = float(elephant.invmass + self.owner.invmass)
        elephant.x -= (elephant.invmass / total_invmass) * (dx / d) * (d - length)
        elephant.y -= (elephant.invmass / total_invmass) * (dy / d) * (d - length)
        elephant.z -= (elephant.invmass / total_invmass) * (dz / d) * (d - length)
        self.owner.x += (self.owner.invmass / total_invmass) * (dx / d) * (d - length)
        self.owner.y += (self.owner.invmass / total_invmass) * (dy / d) * (d - length)
        self.owner.z += (self.owner.invmass / total_invmass) * (dz / d) * (d - length)
  def hit(self, elephant):
    # High-tech collision detection at work.
    dx = self.x - elephant.x
    dy = self.y - elephant.y + elephant.radius
    dz = self.z - elephant.z
    d = math.sqrt(dx ** 2 + dz ** 2)
    if d < elephant.radius and abs(dy) < elephant.radius:
      play('hooked')
      return elephant, dist(self, self.owner), dx, dy - elephant.radius, dz, elephant.dir * math.pi / 180
  def remove(self):
    self.owner.rope = None
    game.objects.remove(self)

class Tree(object):
  def __init__(self, x, z):
    self.invmass = 10
    self.x = x
    self.y = 0
    self.z = z
    self.size = 6 + random.random()
    trunkcolor = (0.4 + 0.3 * random.random(),
                  0.3 + 0.3 * random.random(),
                  0.1 + 0.3 * random.random())
    leafcolor = (0.3 + 0.3 * random.random(),
                 0.4 + 0.3 * random.random(),
                 0.2 + 0.3 * random.random())
    self.height = 4
    self.leaves = 4
    self.structure = [Block(-self.size / 2, -self.size * (i + 1), -self.size / 3, self.size, self.size, self.size, color=trunkcolor, rotation=math.pi * 2 * random.random()) for i in range(self.height)] + \
                     [Block(0, -self.size * self.height - 1, 0, self.size * 1.5, 1, self.size * 1.5, color=leafcolor, rotation=math.pi * 2 * random.random()) for i in range(self.leaves)]
    self.vertexlist = vertexlist(self.structure)
    self.scale = 0.9 + 0.2 * random.random()
    self.dir = 0
    self.lean = 0
    self.broken = False
  def draw(self):
    glPushMatrix()
    glTranslatef(self.x, self.y, self.z)
    glScalef(self.scale, self.scale, self.scale)
    glRotatef(self.dir, 0, 1, 0)
    glRotatef(self.lean, 1, 0, 0)
    glRotatef(-self.dir, 0, 1, 0)
    self.vertexlist.draw(GL_QUADS)
    glPopMatrix()
  def think(self):
    dx = game.elephant.x - self.x
    dz = game.elephant.z - self.z
    d = math.sqrt(dx ** 2 + dz ** 2)
    radius = game.elephant.radius * 1.2 + 2 * self.size
    if 0 < d < radius:
      if self.broken:
        self.lean = max(self.lean, 90 * (radius - d) / radius)
      else:
        if not self.lean:
          play('tree-bend')
        self.lean = 90 * (radius - d) / radius
        self.dir = math.atan2(dx, dz) * 180 / math.pi
    elif not self.broken:
      self.lean = 0
    if not self.broken and self.lean > 45:
      play('tree-break')
      self.broken = True
    if self.broken:
      self.lean *= 1.1
      if self.lean > 130:
        game.objects.remove(self)
        game.objects.append(Leaf(self.x, self.z))

class Leaf(object):
  def __init__(self, x, z):
    self.invmass = 100
    self.x = x
    self.y = 0
    self.z = z
    self.size = 6 + random.random()
    self.structure = [
        Block(0, -1, 0, self.size * 1.5, 1, self.size * 1.5),
        ]
    self.rotations = [360 * random.random() for block in self.structure]
  def draw(self):
    glPushMatrix()
    glTranslatef(self.x, self.y, self.z)
    for r, block in zip(self.rotations, self.structure):
      glRotatef(r, 0, 1, 0)
      block.draw()
    glPopMatrix()
  def think(self):
    pass

HUT_VISIBILITY = 300
MAX_CANNIBALS = 20
class Hut(object):
  def __init__(self, x, z):
    self.invmass = 1
    self.x = x
    self.y = 0
    self.z = z
    self.size = size = 25
    rotation = math.pi * 2 * random.random()
    self.structure = [
        Block(-size / 2, -size, -size / 2, size, size, size, color=(0.4, 0.2, 0.2), rotation=rotation),
        Block(-size / 1.5, -size - 2, -size / 1.5, size * 1.5, 2, size * 1.5, color=(0.4, 0.2, 0.2), rotation=rotation),
        Block(-size / 1.5, -size, -size / 1.5, 2, size, 2, color=(0.4, 0.2, 0.2), rotation=rotation),
        ]
    self.vertexlist = vertexlist(self.structure)
    self.brokenvertexlist = vertexlist([
        Block(-size / 2, -size / 5, -size / 2, size, size / 5, size, color=(0.4, 0.2, 0.2), rotation=rotation)
        ])
    self.broken = False
    self.delay = 200
    self.counter = self.delay
  def draw(self):
    glPushMatrix()
    glTranslatef(self.x, self.y, self.z)
    if self.broken:
      self.brokenvertexlist.draw(GL_QUADS)
    else:
      self.vertexlist.draw(GL_QUADS)
    glPopMatrix()
  def think(self):
    if not self.broken and (game.elephant.covers(self.x, self.z) or game.pink_elephant.covers(self.x, self.z)):
      play('hut-collapse')
      self.broken = True
    if self.broken:
      return
    if len([1 for obj in game.objects if isinstance(obj, Cannibal)]) < MAX_CANNIBALS:
      self.counter += 1
    dx = game.elephant.x - self.x
    dz = game.elephant.z - self.z
    d = math.sqrt(dx ** 2 + dz ** 2)
    if self.counter >= self.delay and d < HUT_VISIBILITY:  # hearing distance
      play('cannibal-attack')
      game.objects.append(Cannibal(self.x, self.z))
      self.counter = 0

class Block(object):
  def __init__(self, x, y, z, sx, sy, sz, color=(0.5, 0.5, 0.5), rotation=0):
    self.x, self.y, self.z = x, y, z
    self.sx, self.sy, self.sz = sx, sy, sz
    self.color = color
    self.rotation = rotation
  def draw(self):
    glColor3f(*self.color)
    glBegin(GL_QUADS)
    for normal, vertex in zip(self.getnormals(), self.getvertices()):
      glNormal3f(*normal  )
      glVertex3d(*vertex)
    glEnd()
  def getvertices(self):
    x, y, z = self.x, self.y, self.z
    sx, sy, sz = self.sx, self.sy, self.sz
    for vx, vy, vz in itertools.chain(quad(x, y, z, sx, sy, 0),
                                      quad(x, y, z, sx, 0, sz),
                                      quad(x, y, z, 0, sy, sz),
                                      quad(x + sx, y + sy, z + sz, -sx, -sy, 0),
                                      quad(x + sx, y + sy, z + sz, -sx, 0, -sz),
                                      quad(x + sx, y + sy, z + sz, 0, -sy, -sz)):
      yield (math.cos(self.rotation) * vx - math.sin(self.rotation) * vz,
             vy,
             math.sin(self.rotation) * vx + math.cos(self.rotation) * vz)
  def getnormals(self):
    for x, y, z in [(0, 0, -1)] * 4 + [(0, -1, 0)] * 4 + [(-1, 0, 0)] * 4 + \
                   [(0, 0, 1)] * 4 + [(0, 1, 0)] * 4 + [(1, 0, 0)] * 4:
      yield (math.cos(self.rotation) * x - math.sin(self.rotation) * z,
             y,
             math.sin(self.rotation) * x + math.cos(self.rotation) * z)


VARIED_SOUNDS = {
  'cannibal-attack': 10,
  'cannibal-trampled': 5,
  'hooked': 6,
  'rope': 6,
  'tree-bend': 7,
  'tree-break': 4,
  }

def play(sound):
  if sound in VARIED_SOUNDS:
    pyglet.resource.media('%s-%d.ogg' % (sound, random.randrange(VARIED_SOUNDS[sound]))).play()
  else:
    pyglet.resource.media('%s.ogg' % sound).play()

def quad(x, y, z, sx, sy, sz, normal=1):
  if sx == 0:
    yield (x, y, z)
    yield (x, y + sy, z)
    yield (x, y + sy, z + sz)
    yield (x, y, z + sz)
  elif sy == 0:
    yield (x, y, z)
    yield (x + sx, y, z)
    yield (x + sx, y, z + sz)
    yield (x, y, z + sz)
  elif sz == 0:
    yield (x, y, z)
    yield (x + sx, y, z)
    yield (x + sx, y + sy, z)
    yield (x, y + sy, z)

def drawline(x0, y0, z0, x1, y1, z1):
  glBegin(GL_LINES)
  glColor3f(0, 0, 0)
  glVertex3d(x0, y0, z0)
  glVertex3d(x1, y1, z1)
  glEnd()

def vertexlist(blocks):
  return pyglet.graphics.vertex_list(len(blocks) * 6 * 4,
      ('v3f', tuple(itertools.chain(*[itertools.chain(*block.getvertices()) for block in blocks]))),
      ('n3f', tuple(itertools.chain(*[itertools.chain(*block.getnormals()) for block in blocks]))),
      ('c3f', tuple(itertools.chain(*[itertools.chain(*[block.color] * 6 * 4) for block in blocks]))),
  )

def dist(a, b):
  return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)

def main():
  global game
  game = Game()
  game.start()
