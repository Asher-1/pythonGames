import glob
import itertools
import math
import os
import random
import pyglet
pyglet.options['debug_gl'] = False

from pyglet.gl import *
pyglet.resource.path = ['data']
pyglet.resource.reindex()

keys = pyglet.window.key
KEYS = {
  'right': {
    'attack': keys.SLASH,
    'left': keys.LEFT,
    'right': keys.RIGHT,
    'down': keys.DOWN,
    'jump': keys.UP,
    'rope': keys.PERIOD,
    },
  'left': {
    'attack': keys.Q,
    'left': keys.A,
    'right': keys.D,
    'down': keys.S,
    'jump': keys.W,
    'rope': keys._1,
    },
  }


imagecache = {}
def sprite(imagename, flip_x=False, **kwargs):
  if (imagename, flip_x) not in imagecache:
    imagecache[imagename, flip_x] = pyglet.resource.image(imagename, flip_x=flip_x)
  sprite = pyglet.sprite.Sprite(imagecache[imagename, flip_x], **kwargs)
  if flip_x:
    sprite.x = sprite.width
  return sprite

def globx(path):
  return [x.replace(os.sep, '/') for x in glob.glob(path.replace('/', os.sep))]

class Game(object):
  def __init__(self):
    # Pyglet setup
    self.window = pyglet.window.Window(width=800, height=800, caption='Ninja Tower')
    self.window.set_icon(pyglet.resource.image('icon16.png').get_image_data(), pyglet.resource.image('icon32.png').get_image_data(), pyglet.resource.image('icon128.png').get_image_data(), pyglet.resource.image('icon512.png').get_image_data())
    @self.window.event
    def on_draw():
      self.window.clear()
      self.draw()
      self.window.invalid = False
    @self.window.event
    def on_key_press(symbol, modifiers):
      if self.instructions:
        self.nextinstruction()
        return
      for ninja in self.ninjas:
        ninja.on_key_press(symbol, modifiers)
      if symbol == keys.ESCAPE and not self.instructions:
        self.playmusic()
        self.startinstructions()
        return True
    @self.window.event
    def on_key_release(symbol, modifiers):
      if self.instructions:
        return
      for ninja in self.ninjas:
        ninja.on_key_release(symbol, modifiers)
    pyglet.clock.schedule_interval(self.think, 1 / 60.0)

    self.playmusic()
    self.startinstructions()
    
  def playmusic(self, song=None):
    if song is None:
      if hasattr(self, 'music'):
        return
      song = random.choice(['piano', 'whistle', 'xylophone'])
    if getattr(self, 'musicname', None) != song:
      self.stopmusic()
    self.musicname = song
    self.music = pyglet.media.Player()
    try:
      self.music.queue(pyglet.resource.media(song + '.ogg'))
      self.music.eos_action = self.music.EOS_LOOP
    except:
      print 'Music is off. (AVbin is missing or does not support Ogg/Vorbis.)'
    else:
      self.music.play()
  def stopmusic(self):
    if hasattr(self, 'music'):
      self.music.pause()
      del self.music
    
  def startinstructions(self):
    self.instructions = [sprite(x.split('/')[-1]) for x in sorted(globx('data/instructions*.png'))]

  def nextinstruction(self):
    self.instructions.pop(0)
    if not self.instructions:
      self.stopmusic()
      self.startgame()

  def startgame(self):
    self.ninjas = [Ninja(self, 100, 30, 'left', KeyController(KEYS['left'])),
                   Ninja(self, 700, 30, 'right', KeyController(KEYS['right']))]
    self.orb = Orb(self, 400, 790)
    self.objects = [self.orb]
    self.building = Building(self)
    self.ground = sprite('ground.png')
    self.effects = []

  def start(self):
    glClearColor(1.0, 1.0, 1.0, 1.0)
    pyglet.app.run()
    
  def draw(self):
    if self.instructions:
      self.instructions[0].draw()
      return
    self.building.draw()
    self.ground.draw()
    for ninja in self.ninjas:
      ninja.draw()
    for obj in self.objects:
      obj.draw()
    for time, effect in self.effects:
      effect.draw()

  def think(self, dt):
    self.window.invalid = True
    if self.instructions:
      return
    self.building.think()
    for ninja in self.ninjas:
      ninja.think()
    for obj in self.objects:
      obj.think()
    for effect in self.effects[:]:
      effect[0] -= 1
      if effect[0] == 0:
        self.effects.remove(effect)
    
  @property
  def things(self):
    return itertools.chain(self.ninjas, self.objects)


class KeyController(object):
  def __init__(self, keymap):
    self.keymap = dict((v, k) for (k, v) in keymap.items())
    self.keysdown = set()
  def think(self):
    if 'attack' in self.keysdown:
      self.ninja.attack()
      self.keysdown.discard('attack')
    if 'jump' in self.keysdown and self.ninja.canjump:
      self.ninja.jump()
      self.keysdown.discard('jump')
    if 'rope' in self.keysdown:
      self.ninja.rope()
      self.keysdown.discard('rope')
    if 'left' in self.keysdown and 'right' not in self.keysdown:
      self.ninja.runleft()
    elif 'right' in self.keysdown and 'left' not in self.keysdown:
      self.ninja.runright()
    if 'down' in self.keysdown:
      self.ninja.descend()
  def on_key_press(self, symbol, modifiers):
    action = self.keymap.get(symbol)
    if action is not None:
      self.keysdown.add(action)
  def on_key_release(self, symbol, modifiers):
    action = self.keymap.get(symbol)
    if action is not None:
      self.keysdown.discard(action)


class Poof(object):
  SPRITES = [sprite('poof-%d.png' % i) for i in range(1, 8)]
  SPEED = 3
  LIFE = len(SPRITES) * SPEED
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.animation = 0
  def draw(self):
    glPushMatrix()
    glTranslatef(int(self.x - 8), int(self.y - 15), 0)
    self.SPRITES[(self.animation / self.SPEED) % len(self.SPRITES)].draw()
    glPopMatrix()
    self.animation += 1
    

class Ninja(object):
  def __init__(self, game, x, y, side, controller):
    self.game = game
    self.setpos(x, y)
    self.controller = controller
    self.controller.ninja = self
    self.width = 15
    self.height = 15
    self.canjump = False
    self.onground = False
    self.wallslide = False
    self.onrope = None
    self.rope_hate = 0
    self.orb = None
    self.orb_points = 0
    if side == 'left':
      self.win = sprite('win-left.png')
      self.win.color = 0, 0, 0
      def winthink():
        score = self.orb_points / 2000.0
        self.win.scale = min(1, score)
        self.win.x = min(0, 10 - self.win.width)
        self.win.y = 30
        if score >= 1:
          self.win.spd = 1
          self.win.rotation = -90
          self.win.think = tumble
          self.win.color = 255, 255, 255
          pyglet.resource.media('gameover.ogg').play()
          self.game.playmusic('whistle')
      def tumble():
        self.win.rotation += 0.2 * self.win.spd
        if self.win.rotation > 0:
          self.win.rotation = 0
          self.win.spd *= -0.3
        self.win.x = 30 + 20 * self.win.rotation / 90.0
        self.win.spd += math.sin((self.win.rotation + 90) * math.pi / 180)
      self.win.think = winthink
      self.win.scale = 0
    else:
      self.win = sprite('win-right.png')
      self.win.color = 0, 0, 0
      def winthink():
        score = self.orb_points / 2000.0
        self.win.scale = min(1, score)
        self.win.x = max(790, 800 - self.win.width)
        self.win.y = 30
        if score >= 1:
          self.win.spd = -1
          self.win.think = tumble
          self.win.color = 255, 255, 255
          pyglet.resource.media('gameover.ogg').play()
          self.game.playmusic('xylophone')
      def tumble():
        self.win.rotation += 0.2 * self.win.spd
        if self.win.rotation < -90:
          self.win.rotation = -90
          self.win.spd *= -0.3
        self.win.x = 790 + 20 * self.win.rotation / 90.0
        self.win.spd += math.sin(self.win.rotation * math.pi / 180)
      self.win.think = winthink
      self.win.scale = 0
    self.side = side  # For sound effects.
    self.levitate = 0
    self.jumps = 0
    self.stand = False
    self.dir = 'left'
    self.animation = 0
    self.running = {
      'left':  [sprite('ninja-run-%d.png' % i) for i in range(1, 7)],
      'right': [sprite('ninja-run-%d.png' % i, flip_x=True) for i in range(1, 7)],
      }
    self.standing = {
      'left':  [sprite('ninja-stand-%d.png' % i) for i in range(1, 7)],
      'right': [sprite('ninja-stand-%d.png' % i, flip_x=True) for i in range(1, 7)],
      }
    self.slashing = {
      'left':  [sprite('ninja-slash-%d.png' % i) for i in [1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5]],
      'right': [sprite('ninja-slash-%d.png' % i, flip_x=True) for i in [1, 1, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5]],
      }
    self.climbing = sprite('ninja-climb.png')
  def setpos(self, x, y):
    self.x = self.ox = x
    self.y = self.oy = y
  def think(self):
    self.physics()
    self.stand = True
    self.controller.think()
    self.animation += 1
    if self.rope_hate:
      self.rope_hate -= 1
    if self.orb:
      self.orb_points += 1
    if not self.levitate:
      self.y -= 0.6
    self.collision()
    self.win.think()
  def collision(self):
    self.onground = False
    self.wallslide = False
    belowceiling = False

    # Grab ropes.
    x = self.x + self.width / 2
    y = self.y + self.height / 2
    if not self.onrope and not self.rope_hate:
      for rope in self.game.building.ropes:
        if rope.block and rope.loose_y < rope.fixed_y and rope.grab(x, y, radius=10):
          self.onrope = rope
          rope.attachments.append(self)
          self.rope_pos = math.sqrt((x - rope.fixed_x) ** 2 + (y - rope.fixed_y) ** 2)
          self.sound('rope-grab')
          break
    if self.onrope:
      rope = self.onrope
      d = math.sqrt((x - rope.fixed_x) ** 2 + (y - rope.fixed_y) ** 2)
      if d > self.rope_pos or self.y < rope.fixed_y:
        x = rope.fixed_x + (x - rope.fixed_x) * self.rope_pos / d
        y = rope.fixed_y + (y - rope.fixed_y) * self.rope_pos / d
      else:
        self.rope_pos = d
      rope.loose_x = rope.fixed_x + (x - rope.fixed_x) * rope.length / self.rope_pos
      rope.loose_y = rope.fixed_y + (y - rope.fixed_y) * rope.length / self.rope_pos
      self.x = x - self.width / 2
      self.y = y - self.height / 2
      if not rope.block or self.onground:
        self.detach()
        
    vy = self.y - self.oy
    if self.x < 10:
      self.x = 10
    elif self.x > 790 - self.width:
      self.x = 790 - self.width
    if self.y < 30:
      self.y = 30
      self.onground = True
      if vy < -10:
        self.poof()
        self.sound('land')
    elif self.y > 800 - self.height:
      self.y = 800 - self.height
      belowceiling = False
    dx, dy = getoffset(self, bounce=1.1)
    if dx:
      self.wallslide = True
    if dy > 0:
      self.onground = True
      if vy < -10:
        self.poof()
        self.sound('land')
    elif dy < 0:
      belowceiling = False
    
    # Get the orb.
    if self.game.orb in self.game.objects and not self.game.orb.timer:
      dist2 = (self.x - self.game.orb.x) ** 2 + (self.y - self.game.orb.y) ** 2
      if dist2 < 100:
        self.orb = self.game.orb.sprites
        self.game.objects.remove(self.game.orb)
        self.sound('orb-grab')
        
    if self.onground or self.onrope:
      self.jumps = 2
    self.canjump = self.jumps and not belowceiling
  def physics(self):
    if self.levitate:
      self.levitate -= 1
      return
    vx = self.x - self.ox
    vy = self.y - self.oy
    if self.onrope:
      vx *= 0.99
      vy *= 0.99
    else:
      vx *= 0.85
      if self.wallslide and vy < 0:
        vy *= 0.85
      else:
        vy *= 0.999
    self.x, self.ox = self.x + vx, self.x
    self.y, self.oy = self.y + vy, self.y
  def runleft(self):
    if self.levitate:
      return
    self.stand = False
    self.x -= 1
    self.dir = 'left'
  def runright(self):
    if self.levitate:
      return
    self.stand = False
    self.x += 1
    self.dir = 'right'
  def jump(self):
    if self.levitate:
      return
    self.detach()
    if self.canjump:
      self.poof()
      self.y += 8
      self.jumps -= 1
      if self.jumps == 1:
        self.sound('jump-1')
      else:
        self.sound('jump-2')
  def sound(self, name):
    pyglet.resource.media('ninja-' + self.side + '-' + name + '.ogg').play()
  def rope(self):
    if self.levitate:
      return
    rope = self.game.building.add_rope(self.x + self.width / 2, self.y)
    if rope.block:
      self.sound('rope-hit')
    else:
      self.sound('rope-miss')
  def poof(self):
    self.game.effects.append([Poof.LIFE, Poof(self.x, self.y)])
  def detach(self):
    if self.onrope:
      self.onrope.attachments.remove(self)
      self.onrope = None
      self.rope_hate = 10
  def descend(self):
    if self.onrope:
      self.rope_pos = min(self.onrope.length, self.rope_pos + 5)
  def attack(self):
    if self.levitate:
      return
    self.detach()
    hit = False
    building = self.game.building
    for block in building.blocks_touching(self.x - 7, self.y - 7, self.width + 15, self.height + 15):
      building.destroy_block(block)
      hit = True
    if hit:
      self.sound('hit-block')
    else:
      self.sound('miss')
      
    for opponent in self.game.ninjas:
      if opponent is self:
        continue
      if ((opponent.x - self.x) ** 2 + (opponent.y - self.y) ** 2) < 600:
        opponent.hit(by=self)

    self.levitate = 16
    self.animation = 0
  def hit(self, by, strength=10):
    self.sound('gets-hit')
    dx = self.x - by.x
    dy = self.y - by.y
    r = math.sqrt(dx ** 2 + dy ** 2)
    if r == 0:
      return
    dx /= r
    dy /= r
    dy += 0.5  # Throw into the air.
    self.x += strength * dx
    self.y += strength * dy
    
    self.onrope = None

    # Drop the orb.
    if self.orb:
      self.orb = None
      self.game.orb.timer = 10
      self.game.orb.x = self.x
      self.game.orb.ox = self.ox
      self.game.orb.y = self.oy
      self.game.orb.oy = self.oy - 10
      self.game.objects.append(self.game.orb)
  def draw(self):
    glPushMatrix()
    if self.levitate:
      loop = self.slashing[self.dir]
      sprite = loop[(self.animation) % len(loop)]
    elif self.onrope:
      sprite = self.climbing
    elif self.stand and self.onground:
      loop = self.standing[self.dir]
      sprite = loop[(self.animation / 5) % len(loop)]
    elif self.stand:  # Flying through the air.
      loop = self.running[self.dir]
      sprite = loop[0]
    else:
      loop = self.running[self.dir]
      sprite = loop[(self.animation / 2) % len(loop)]
    glTranslatef(int(self.x - (sprite.width - self.width) / 2),
                 int(self.y - (sprite.height - self.height) / 2), 0)
    sprite.draw()
    if self.orb:
      self.orb[(self.animation / 6) % len(self.orb)].draw()
    glPopMatrix()
    self.win.draw()
  def on_key_press(self, symbol, modifiers):
    self.controller.on_key_press(symbol, modifiers)
  def on_key_release(self, symbol, modifiers):
    self.controller.on_key_release(symbol, modifiers)

def getoffset(thing, bounce=1):
  mx = my = 0
  absbigger = lambda x, y: abs(x) > abs(y) and x or y
  abssmaller = lambda x, y: x + y - absbigger(x, y)
  for block in thing.game.building.blocks_touching(thing.ox, thing.y, thing.width, thing.height):
    my = absbigger(my, abssmaller(block.y - thing.height - thing.y, block.y + block.height - thing.y))
  thing.y += bounce * my
  for block in thing.game.building.blocks_touching(thing.x, thing.y, thing.width, thing.height):
    mx = absbigger(mx, abssmaller(block.x - thing.width - thing.x, block.x + block.width - thing.x))
  thing.x += bounce * mx
  return mx, my

class Orb(object):
  def __init__(self, game, x, y):
    self.game = game
    self.setpos(x, y)
    self.sprites = [sprite('orb-%d.png' % i) for i in range(12)]
    self.animation = 0
    self.width = 20
    self.height = 20
    self.timer = 0
    self.onground = False
  def setpos(self, x, y):
    self.x = self.ox = x
    self.y = self.oy = y
  def think(self):
    self.physics()
    self.animation += 1
    if self.timer:
      self.timer -= 1
    self.y -= 0.5
    self.collision()
  def collision(self):
    self.onground = False
    v = (self.y - self.oy) ** 2 + (self.y - self.oy) ** 2
    BOUNCE = 1.5
    bounced = False
    if self.x < 10:
      self.x -= BOUNCE * (self.x - 10)
      bounced = True
    elif self.x > 790 - self.width:
      self.x -= BOUNCE * (self.x - (790 - self.width))
      bounced = True
    if self.y < 30:
      self.y -= BOUNCE * (self.y - 30)
      self.onground = True
      bounced = True
    elif self.y > 800 - self.height:
      self.y -= BOUNCE * (self.y - (800 - self.height))
      bounced = True
    dx, dy = getoffset(self, BOUNCE)
    if dy > 0:
      self.onground = True
    if dx != 0 or dy != 0:
      bounced = True
    if bounced and v > 10:
      pyglet.resource.media('orb-bounce-%d.ogg' % random.randint(0, 5)).play()
  def physics(self):
    vx = self.x - self.ox
    vy = self.y - self.oy
    if self.onground:
      vx *= 0.85
    else:
      vx *= 0.99
    vy *= 0.99
    self.x, self.ox = self.x + vx, self.x
    self.y, self.oy = self.y + vy, self.y
  def draw(self):
    glPushMatrix()
    glTranslatef(int(self.x), int(self.y - 10), 0)
    self.sprites[(self.animation / 6) % len(self.sprites)].draw()
    glPopMatrix()


def bucket_for(x, y):
  return int(x / 30), int((y - 20) / 40)
  
def unbucket(x, y):
  return x * 30, y * 40 + 20

def buckets_near(x, y, distance=1):
  return coords_near(*bucket_for(x, y), distance=distance)

def coords_near(x, y, distance=1):
  for nx in range(x - distance, x + distance + 1):
    for ny in range(y - distance, y + distance + 1):
      yield nx, ny

def coords_next_to(x, y):
  return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

def touching(x1, y1, w1, h1, x2, y2, w2, h2):
  return (x1 - w2 < x2 < x1 + w1 and
          y1 - h2 < y2 < y1 + h1)

def touching_obj(o1, o2):
  return (o1.x - o2.width <= o2.x <= o1.x + o1.width and
          o1.y - o2.height <= o2.y <= o1.y + o1.height)


class Rope(object):
  def __init__(self, building, loose_x, loose_y, fixed_x, fixed_y, block):
    self.building = building
    self.loose_x = loose_x
    self.loose_y = loose_y
    self.fixed_x = fixed_x
    self.fixed_y = fixed_y
    self.length = math.sqrt((loose_x - fixed_x) ** 2 + (loose_y - fixed_y) ** 2)
    self.block = block
    if block:
      if not hasattr(block, 'ropes'): block.ropes = []
      block.ropes.append(self)
    self.oloose_x = loose_x
    self.oloose_y = loose_y
    self.attachments = []
  def draw(self):
    glBegin(GL_LINES)
    glColor3f(0, 0, 0)
    glVertex2d(self.fixed_x, self.fixed_y)
    glVertex2d(self.loose_x, self.loose_y)
    glColor3f(255, 255, 255)
    glEnd()
  def think(self):
    self.loose_y -= 0.1  # The weight of the rope.
    self.loose_x += self.building.wind
    sway_x = 0.99 * (self.loose_x - self.oloose_x)
    sway_y = 0.99 * (self.loose_y - self.oloose_y)
    self.loose_x, self.oloose_x = self.loose_x + sway_x, self.loose_x
    self.loose_y, self.oloose_y = self.loose_y + sway_y, self.loose_y
    length = math.sqrt((self.loose_x - self.fixed_x) ** 2 + (self.loose_y - self.fixed_y) ** 2)
    self.loose_x = self.fixed_x + (self.loose_x - self.fixed_x) * self.length / length
    self.loose_y = self.fixed_y + (self.loose_y - self.fixed_y) * self.length / length
    if self.block is None:
      self.fixed_y -= 5
      self.loose_y -= 5
      if self.fixed_y < 0 and self.loose_y < 0:
        self.building.ropes.remove(self)
      return
  def grab(self, x, y, radius):
    # Mostly copied from euclid._intersect_line2_circle.
    def dot(x1, y1, x2, y2):
      return x1 * x2 + y1 * y2
    rx = self.loose_x - self.fixed_x
    ry = self.loose_y - self.fixed_y
    a = rx ** 2 + ry ** 2
    b = 2 * (rx * (self.fixed_x - x) + ry * (self.fixed_y - y))
    c = (x ** 2 + y ** 2 +
         self.fixed_x ** 2 + self.fixed_y ** 2 -
         2 * dot(x, y, self.fixed_x, self.fixed_y) -
         radius ** 2)
    det = b ** 2 - 4 * a * c
    if det < 0:
      return False
    sq = math.sqrt(det)
    u1 = (-b + sq) / (2 * a)
    u2 = (-b - sq) / (2 * a)
    return 0 < (u1 + u2) / 2 < 1


class Building(object):
  def __init__(self, game):
    self.game = game
    self.traps = []
    self.ropes = []
    self.wind = 0
    self.batch = pyglet.graphics.Batch()
    self.blocks = {}
    self.growing = []
    self.shrinking = set()
    self.mass = 0
    for bx in range(7, 20):
      for by in range(0, 10):
        x, y = unbucket(bx, by)
        self.add_block(x, y)
    self.normalmass = self.mass
  def add_block(self, x, y):
    if not self.connected(bucket_for(x, y)):
      return
    block = sprite('block.png', batch=self.batch, x=x, y=y)
    for thing in self.game.things:
      if touching(block.x, block.y, block.width, block.height,
                  thing.x, thing.y, thing.width, thing.height):
        return
    bucket = self.blocks.setdefault(bucket_for(x, y), [])
    bucket.append(block)
    self.mass += 1
    block.x += block.width / 2
    block.y += block.height / 2
    block.scale = 0
    self.growing.append(block)
  def destroy_block(self, block):
    if self.needed(block):
      return
    bucket = bucket_for(block.x, block.y)
    if bucket not in self.blocks:
      return
    self.blocks[bucket].remove(block)
    if len(self.blocks[bucket]) == 0:
      del self.blocks[bucket]
    if block in self.growing:
      self.growing.remove(block)
    for rope in getattr(block, 'ropes', []):
      rope.block = None
    self.shrinking.add(block)
    self.mass -= 1
  def needed(self, block):
    question = bucket_for(block.x, block.y)
    connected = set()
    for root in coords_next_to(*question):
      if root in self.blocks:
        if not self.connected(root, connected, ignore=question):
          return True
    return False
  def connected(self, root, connected=None, ignore=None):
    import heapq
    if connected is None:
      connected = set()
    visited = set()
    x, y = root
    heap = [(y, 0, root)]
    while heap:
      pcost, scost, bucket = heapq.heappop(heap)
      x, y = bucket
      if bucket in connected or y == 0:
        connected.update(visited)
        return True
      for neighbor in coords_next_to(x, y):
        if neighbor in self.blocks and neighbor != ignore and neighbor not in visited and neighbor not in self.shrinking:
          visited.add(neighbor)
          heapq.heappush(heap, (scost + 1 + neighbor[1], scost + 1, neighbor))
    return False
  def blocks_near(self, x, y, distance=1):
    for bucket in buckets_near(x, y, distance):
      for block in self.blocks.get(bucket, []):
        yield block
  def blocks_touching(self, x, y, w, h):
    for block in self.blocks_near(x + w / 2, y + h / 2):
      if touching(block.x, block.y, block.width, block.height, x, y, w, h):
        yield block
  def blocks_touching_obj(self, obj):
    return self.blocks_touching(obj.x, obj.y, obj.width, obj.height)
  def add_rope(self, x, y):
    topblock = None
    for i in range(5):
      for block in self.blocks_touching(x, y + 40 * i, 1, 1):
        topblock = block
    if topblock is None:
      rope = Rope(self, x, y, x, y + 40 * i, block=None)
    else:
      rope = Rope(self, x, y, x, topblock.y + 20, block=topblock)
    self.ropes.append(rope)
    return rope
  def regenerate(self):
    x = random.randint(50, 749)
    y = random.randint(20, 749)
    for thing in self.game.things:
      if (x - thing.x) ** 2 + (y - thing.y) ** 2 < 150 ** 2 and random.random() < 0.9:
        return
    x, y = bucket_for(x, y)
    living = len([bucket for bucket in coords_near(x, y) if bucket in self.blocks])
    if (x, y) in self.blocks:
      if living <= 3:
        for block in self.blocks[x, y]:
          self.destroy_block(block)
      elif living >= 6 and y > 0 and (x, y - 1) not in self.blocks:
        self.add_block(*unbucket(x, y - 1))
    elif self.mass < self.normalmass:
      if living and random.random() * 3 < (living - 1) + y * 0.05:
        self.add_block(*unbucket(x, y))
  def think(self):
    self.regenerate()
    for trap in self.traps:
      trap.think()
    for block in self.growing[:]:
      block.scale += 0.05
      block.x -= 0.05 * block.width / 2 / block.scale
      block.y -= 0.05 * block.height / 2 / block.scale
      if block.scale >= 1:
        block.scale = 1
        block.x, block.y = unbucket(*bucket_for(block.x, block.y))
        self.growing.remove(block)
    for block in list(self.shrinking):
      block.scale -= 0.05
      if block.scale <= 0:
        self.shrinking.remove(block)
        block.delete()  # "pyglet" delete.
      else:
        block.x += 0.05 * block.width / 2 / block.scale
        block.y += 0.05 * block.height / 2 / block.scale
    self.wind = 0.1 * (random.random() - 0.5)
    for rope in self.ropes[:]:
      rope.think()
  def draw(self):
    self.batch.draw()
    for trap in self.traps:
      trap.draw()
    for rope in self.ropes:
      rope.draw()


def main():
  game = Game()
  game.start()
