# Make this work on Python 2.5
from __future__ import with_statement

import collections
import cPickle as pickle
import glob
import math
import os
import pyglet
import random
import string
import sys
import time
import traceback
pyglet.options['debug_gl'] = False
from pyglet.gl import *
pyglet.resource.path = ['data']
pyglet.resource.reindex()


# Settings. Feel free to modify!
RECOMBINATION_RATE = 0.001
MUTATOR_STRENGTH = 0.001
TITLE_HOLD = 60
TITLE_FADE = 30
STARTING_MONEY = 2
SOUND_EFFECTS = True
MUSIC = True
SONGS = ['blues-blues-bunny-blues.mp3', 'blues-blues-bunny-blues_2.mp3', 'song-song-bunny-sing.mp3']
MULTISAMPLING = False  # Didn't make much difference.
# Since body parts can be small or large, mipmapping is useful.
MIPMAP = True
# But the default causes the textures to be too blurry. This bias fixes that.
glTexEnvf(GL_TEXTURE_FILTER_CONTROL, GL_TEXTURE_LOD_BIAS, -1)

# Genetics. Tinkering will have consequences!
BASES = 4
ALPHABET = string.uppercase[:BASES]

def RandomSequence(min_length, max_length=-1, random=random):
  if max_length == -1:
    l = min_length
  else:
    l = random.randrange(min_length, max_length + 1)
  return ''.join(random.choice(ALPHABET) for i in range(l))

random.seed(0)
SEQUENCE_RANDOM = random.Random(0)
def Sequence(min_length, max_length=-1):
  return RandomSequence(min_length, max_length, random=SEQUENCE_RANDOM)

class Gene(object):
  def __init__(self, string, meaning):
    self.string = string
    self.meaning = meaning

GENES = set([Gene(Sequence(4), 'furry'),
             Gene(Sequence(6), 'scaled'),
             Gene(Sequence(6), 'leaf'),
             Gene(Sequence(5), 'green'),
             Gene(Sequence(5), 'red'),
             Gene(Sequence(5), 'blue'),
             Gene(Sequence(5), 'bright'),
             Gene(Sequence(5), 'dark'),
             Gene(Sequence(15), 'eye'),
             Gene(Sequence(10), 'tooth'),
             Gene(Sequence(20), 'wing'),
             ])
# These are not applicable to entire appendages.
LEAF_GENES = set('eye tooth wing'.split())

BALL_START = set(Sequence(10) for i in range(1))
BALL_END = set(Sequence(10) for i in range(1))
BALL_INFLATE = set(Sequence(6) for i in range(1))
BALL_CONTRACT = set(Sequence(5) for i in range(1))
BALL_WIDEN = set(Sequence(5) for i in range(1))
BALL_SHRINK = set(Sequence(7) for i in range(1))
BALL_ROTATE_CW = set(Sequence(6) for i in range(1))
BALL_ROTATE_CCW = set(Sequence(7) for i in range(1))

# print 'Gene coverage:'
# ALL_GENES = set(g.string for g in GENES) | BALL_START | BALL_END | BALL_INFLATE | BALL_SHRINK | BALL_ROTATE_CW | BALL_ROTATE_CCW | BALL_CONTRACT | BALL_WIDEN
# maxl = max(len(g) for g in ALL_GENES)
# for i in range(1, maxl+1):
#   print i, float(len([g for g in ALL_GENES if len(g) == i])) / BASES ** i


# The rest is just code.

IMAGECACHE = {}
def Sprite(imagename, rescale=False, center=True, mipmap=MIPMAP):
  if imagename not in IMAGECACHE:
    image = pyglet.resource.image(imagename)
    if mipmap:
      image = image.get_image_data()
      image.get_regular_texture = image.get_texture
      image.get_texture = image.get_mipmapped_texture
    IMAGECACHE[imagename] = image
  sprite = pyglet.sprite.Sprite(IMAGECACHE[imagename])
  # Clamp down the texture coordinates so to prevent hackers driving away in them.
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
  if rescale:
    sprite.scale = 2.0 / sprite.width
  if center:
    sprite.x = -sprite.width / 2
    sprite.y = -sprite.height / 2
  else:
    sprite.y = -sprite.height
  sprite.recreate_with = Sprite, imagename, rescale, center, mipmap
  return sprite

def Sound(name):
  if SOUND_EFFECTS:
	  return pyglet.resource.media(name).play()

class HasSprites(object):
  def __setstate__(self, state):
    self.__dict__.update(state['other'])
    for k, v in state['sprites'].items():
      if v is None:
        continue
      elif isinstance(v[0], basestring):
        self.__dict__[k] = getattr(self, v[0])(*v[1:])
      else:
        self.__dict__[k] = v[0](*v[1:])
  def __getstate__(self):
    state = dict(sprites={}, other={})
    for k, v in self.__dict__.items():
      if hasattr(v, 'recreate_with'):
        state['sprites'][k] = v.recreate_with
      else:
        state['other'][k] = v
    return state

class DropSprites(object):
  def __getstate__(self):
    state = {}
    for k, v in self.__dict__.items():
      if not hasattr(v, 'recreate_with'):
        state[k] = v
    return state


class Ball(DropSprites):
  def __init__(self):
    self.size = 0
    self.contraction = 0
    self.rot = 0
    self.parent = None
    self.genes = collections.defaultdict(int)
    self.children = collections.defaultdict(list)
  def AddBall(self):
    ball = Ball()
    ball.parent = self
    ball.genes.update(self.genes)
    for gene in LEAF_GENES:
      ball.genes[gene] = 0
    self.children[self.size, self.rot].append(ball)
    return ball
  def __repr__(self):
    r = '%r\n' % dict(size=self.size, rot=self.rot, contr=self.contraction, genes=self.genes)
    for k, v in self.children.items():
      r += '%r:\n' % (k,)
      c = repr(v)
      for l in c.split('\n'):
        r += '  %s\n' % l
    return r
  def Weight(self):
    return self.size + sum(c.Weight() for c in self.children.values())
  def Complexity(self):
    if not self.children:
      return 1
    return max(c.Complexity() for c in self.children.values()) + 1
  def Draw(self, inherited_genes, animation):
    genes = collections.defaultdict(int)
    genes.update(self.genes)
    for k, v in inherited_genes.items():
      if k not in LEAF_GENES:
        genes[k] += v
    if not hasattr(self, 'sprite'):
      if genes['eye']:
        self.sprite = Sprite('eye_bottom.png', rescale=True)
        self.sprite2 = Sprite('eye_top.png', rescale=True)
        material = 'eye'
      elif genes['wing']:
        self.sprite = Sprite('wing.png', rescale=True)
        material = 'wing'
      elif genes['tooth']:
        self.sprite = Sprite('tooth.png', rescale=True)
        material = 'tooth'
      elif genes['furry'] > genes['leaf'] and genes['furry'] > genes['scaled']:
        self.sprite = Sprite('furball.png', rescale=True)
        material = 'furry'
      elif genes['leaf'] > genes['scaled']:
        self.sprite = Sprite('leafball.png', rescale=True)
        material = 'leaf'
      else:
        self.sprite = Sprite('scaleball.png', rescale=True)
        material = 'scaled'
      # Color expression.
      r = genes['red']
      g = genes['green']
      b = genes['blue']
      brightness = genes['bright'] - genes['dark']
      if material == 'furry':
        if r and g:  # Brown is dominant.
          b = 0
          g = min(r, g)
      elif material == 'leaf':
        if g:  # Green is dominant.
          r /= 2
          b /= 3
      Formula = lambda x: (255 - 95 / (1 + x)) if x > 0 else (64 + 60 / (1 - x))
      r = Formula(r + brightness)
      g = Formula(g + brightness)
      b = Formula(b + brightness)
      self.sprite.color = r, g, b
    tr = math.sin(0.02 * animation) * 2
    glPushMatrix()
    if self.parent is None:
      glRotatef(self.rot * 5 + tr, 0, 0, 1)
    glScalef(self.size, max(self.size * 0.2, self.size - self.contraction), 1)
    self.sprite.draw()
    if hasattr(self, 'sprite2'):
      # A little known fact is that unrealistically rotating the highlight
      # makes the image more life-like!
      glRotatef(-15 * tr, 0, 0, 1)
      self.sprite2.draw()
      glRotatef(15 * tr, 0, 0, 1)
    glPopMatrix()
    for (d, r), cs in self.children.items():
      for c in cs:
        glPushMatrix()
        if self.parent is None:
          glRotatef(self.rot * 5 + tr, 0, 0, 1)
        glRotatef(5 * (r - self.rot), 0, 0, 1)
        glTranslatef(d, 0, 0)
        glRotatef(c.rot * 5 + tr, 0, 0, 1)
        glTranslatef(c.size, 0, 0)
        c.Draw(inherited_genes, animation)
        glPopMatrix()

def StartsWith(dna, pattern):
  return any(half.startswith(pattern) for half in dna)

def Positions(dna, pattern):
  p = set()
  i = 0
  while True:
    i = dna.find(pattern, i)
    if i == -1:
      return p
    p.add(i)
    i += 1

def DiploidPositions(dna, pattern):
  a, b = dna
  return Positions(a, pattern) | Positions(b, pattern)

def DiploidGenesetPositions(dna, geneset):
  p = set()
  for half in dna:
    for gene in geneset:
      p.update(Positions(half, gene))
  return p

def LoadDNA(filename):
  lib = {}
  try:
    with file(filename) as f:
      exec f in lib
    return lib['GetDNA']()
  except Exception:
    traceback.print_exc()


class Creature(object):
  def __init__(self, dna):
    self.animation = 0
    self.SetDNA(dna)

  def SetDNA(self, dna):
    self.dna = dna
    a, b = dna
    ball = Ball()
    self.root = ball
    starts = DiploidGenesetPositions(dna, BALL_START)
    ends = DiploidGenesetPositions(dna, BALL_END)
    rotate_cws = DiploidGenesetPositions(dna, BALL_ROTATE_CW)
    rotate_ccws = DiploidGenesetPositions(dna, BALL_ROTATE_CCW)
    inflates = DiploidGenesetPositions(dna, BALL_INFLATE)
    shrinks = DiploidGenesetPositions(dna, BALL_SHRINK)
    contracts = DiploidGenesetPositions(dna, BALL_CONTRACT)
    widens = DiploidGenesetPositions(dna, BALL_WIDEN)
    self.genes = collections.defaultdict(int)
    genes = dict((gene.meaning, DiploidPositions(dna, gene.string)) for gene in GENES)
    merged = starts | ends | rotate_cws | rotate_ccws | inflates | shrinks | contracts | widens
    for positions in genes.values():
      merged.update(positions)
    for i in sorted(merged):
      if ball:
        for meaning, positions in genes.items():
          if i in positions:
            ball.genes[meaning] += 1
        if i in starts:
          ball = ball.AddBall()
        elif i in ends:
          ball = ball.parent  # May be None.
        elif i in rotate_cws:
          ball.rot -= 1
        elif i in rotate_ccws:
          ball.rot += 1
        elif i in inflates:
          ball.size += 1
        elif i in shrinks:
          ball.size -= 1
        elif i in contracts:
          ball.contraction += 1
        elif i in widens:
          ball.contraction -= 1
      else:
        for meaning, positions in genes.items():
          if i in positions:
            self.genes[meaning] += 1

  def Draw(self, selected=False):
    if selected:
      self.animation += 5
    else:
      self.animation += 1
    self.root.Draw(self.genes, self.animation)

  def GetHalf(self):
    a = list(self.dna[0])
    b = list(self.dna[1])
    for i in range(min(len(a), len(b))):
      if random.random() < RECOMBINATION_RATE:
        a[i:], b[i:] = b[i:], a[i:]
    return random.choice([''.join(a), ''.join(b)])
    
    
CARD_WIDTH = 216
CARD_HEIGHT = 240
class Card(HasSprites):
  def __init__(self, creature, caption='Unnamed'):
    self.creature = creature
    self.sprite = Sprite('card.png', center=False)
    self.caption = caption
    self.label = self.MakeLabel()
    self.x, self.y = None, None
    self.selected = False
    self.held = False
    self.moved = False

  def MakeLabel(self):
    label = pyglet.text.HTMLLabel(self.caption, anchor_x='center')
    label.last_text = ''
    label.recreate_with = 'MakeLabel',
    return label
  
  def Width(self):
    return CARD_WIDTH

  def SetText(self, text):
    if text != self.label.last_text:
      self.label.text = '<font face="Helvetica, Arial" size="+1">' + text
      self.label.last_text = text

  def Contains(self, x, y):
    return self.x < x < self.x + self.Width() and self.y - 240 < y < self.y

  def KeyPress(self, text):
    self.caption += text

  def Backspace(self):
    self.caption = self.caption[:-1]

  def Draw(self):
    glPushMatrix()
    glTranslatef(self.x, self.y, 0)
    self.DrawFixed()
    glPopMatrix()
    
  def DrawFixed(self):
    glTranslatef(CARD_WIDTH / 2 - self.sprite.width / 2, 0, 0)
    self.sprite.draw()
    if self.selected and not self.held:
      if int(time.time() * 2) % 2:
        self.SetText(self.caption)
      else:
        self.SetText('<font color="white">_</font>' + self.caption + '_')
    else:
      self.SetText(self.caption)
    glTranslatef(self.sprite.width / 2, -28, 0)
    self.label.draw()
    glTranslatef(0, -145, 0)
    self.creature.Draw(self.selected)

  def Think(self):
    if not self.held:
      self.x = (self.x * 5 + self.place.x) / 6
      self.y = (self.y * 5 + self.place.y) / 6


class Place(HasSprites):
  def __init__(self):
    self.sprite = Sprite('place.png', center=False)
    self.card = None
    self.listeners = []
  def Width(self):
    return CARD_WIDTH
  def Height(self):
    return CARD_HEIGHT
  def Contains(self, x, y):
    return self.x < x < self.x + self.Width() and self.y - 240 < y < self.y
  def DrawFixed(self):
    glTranslatef(CARD_WIDTH / 2 - self.sprite.width / 2, 0, 0)
    self.sprite.draw()
  def Drop(self, card):
    if self.card:
      # Swap.
      if not hasattr(card.place, 'Drop'):
        return # Cannot swap.
      self.card.place = card.place
      card.place.card = self.card
    elif card.place:
      card.place.card = None
    card.place = self
    self.card = card
    if card.x is None:
      card.x = self.x
      card.y = self.y
    for listener in self.listeners:
      listener.Drop(self)
    game.Save()
    Sound('drop.wav')


class Button(HasSprites):
  def __init__(self, caption):
    self.sprite = Sprite('button.png', center=False)
    self.label = self.MakeLabel(caption)
    self.card = None
  def MakeLabel(self, caption):
    label = pyglet.text.Label(caption, font_size=25, color=(0, 0, 0, 255), anchor_x='center',
                              x=self.sprite.width / 2, y=-130)
    label.recreate_with = 'MakeLabel', caption
    return label
  def Width(self):
    return CARD_WIDTH
  def Height(self):
    return CARD_HEIGHT
  def Contains(self, x, y):
    return self.x < x < self.x + self.Width() and self.y - 240 < y < self.y
  def DrawFixed(self):
    glTranslatef(CARD_WIDTH / 2 - self.sprite.width / 2, 0, 0)
    self.sprite.draw()
    self.label.draw()
  def Spawn(self, card):
    if self.card:
      return  # Occupied.
    card.place = self
    self.card = card
    card.x = self.x
    card.y = self.y


class Label(HasSprites):
  def __init__(self, caption):
    self.label = self.MakeLabel(caption)
  def MakeLabel(self, caption):
    label = pyglet.text.Label(caption, y=-130, font_size=25, color=(0, 0, 0, 255))
    label.recreate_with = 'MakeLabel', caption
    return label
  def Width(self):
    return self.label.content_width
  def DrawFixed(self):
    self.label.draw()
  def Contains(self, x, y):
    return False

class VerticalLabel(Label):
  def MakeLabel(self, caption):
    label = pyglet.text.Label(caption, x=10, width=200, multiline=True, font_size=15, color=(0, 0, 0, 255))
    label.recreate_with = 'MakeLabel', caption
    return label
  def Height(self):
    return self.label.content_height - 15
    

class Container(HasSprites):
  def __init__(self, caption, *contents):
    self.label = self.MakeLabel(caption)
    self.sprite1 = Sprite('pen1.png', center=False)
    self.sprite2 = Sprite('pen2.png', center=False)
    self.sprite3 = Sprite('pen3.png', center=False)
    self.x, self.y = 0, 0
    self.contents = list(contents)
    self.held = False

  def MakeLabel(self, caption):
    label = pyglet.text.Label(caption, font_size=15, color=(0, 0, 0, 255), x=20, y=-28)
    label.recreate_with = 'MakeLabel', caption
    return label
    
  def Width(self):
    return sum(c.Width() for c in self.contents) + 20

  def Contains(self, x, y):
    return self.x < x < self.x + self.Width() and self.y - 300 < y < self.y

  def Clicked(self, x, y):
    for c in self.contents:
      if c.Contains(x, y):
        if isinstance(c, Button):
          self.ButtonPress(c)
          game.Save()
        return

  def ButtonPress(self, button):
    pass
    
  def Think(self):
    # Yeah, um, we update the position of everything all the time.
    # It's the only way to be sure!
    cx = self.x + 10
    cy = self.y - 40
    for c in self.contents:
      c.x = cx
      c.y = cy
      cx += c.Width()
    
  def Draw(self):
    glPushMatrix()
    glTranslatef(self.x, self.y, 0)
    self.DrawFixed()
    glPopMatrix()
    
  def DrawFixed(self):
    width = self.Width()
    glPushMatrix()
    glTranslatef(width - 256, 0, 0)
    self.sprite3.draw()
    glTranslatef(256 - width, 0, 0)
    self.sprite1.draw()
    self.label.draw()
    glTranslatef(256, 0, 0)
    for i in range((width - 1) / 128 - 3):
      self.sprite2.draw()
      glTranslatef(128, 0, 0)
    glPopMatrix()
    glTranslatef(10, -40, 0)
    for c in self.contents:
      glPushMatrix()
      c.DrawFixed()
      glPopMatrix()
      glTranslatef(c.Width(), 0, 0)


class VerticalContainer(Container):
  def __init__(self, caption, *contents):
    self.label = self.MakeLabel(caption)
    self.sprite1 = Sprite('vpen1.png', center=False)
    self.sprite2 = Sprite('vpen2.png', center=False)
    self.sprite3 = Sprite('vpen3.png', center=False)
    self.x, self.y = 0, 0
    self.contents = list(contents)
    self.held = False
    self.gap = 17

  def MakeLabel(self, caption):
    label = pyglet.text.Label(caption, font_size=15, color=(0, 0, 0, 255), x=self.Width() / 2, y=-28, anchor_x='center')
    label.recreate_with = 'MakeLabel', caption
    return label
    
  def Width(self):
    return 240

  def Height(self):
    return sum(c.Height() + self.gap for c in self.contents) + 50

  def Contains(self, x, y):
    return self.x < x < self.x + self.Width() and self.y - self.Height() < y < self.y
    
  def Think(self):
    # Yeah, um, we update the position of everything all the time.
    # It's the only way to be sure!
    cx = self.x + 10
    cy = self.y - 50
    for c in self.contents:
      c.x = cx
      c.y = cy
      cy -= c.Height() + self.gap
    
  def DrawFixed(self):
    height = self.Height()
    glPushMatrix()
    glTranslatef(0, 140 - height, 0)
    self.sprite3.draw()
    glTranslatef(0, height - 140, 0)
    self.sprite1.draw()
    self.label.draw()
    glTranslatef(0, -64, 0)
    for i in range((height - 140) / 64):
      self.sprite2.draw()
      glTranslatef(0, -64, 0)
    glPopMatrix()
    glTranslatef(10, -50, 0)
    for c in self.contents:
      glPushMatrix()
      c.DrawFixed()
      glPopMatrix()
      glTranslatef(0, -c.Height() - self.gap, 0)


class SmallButton(Button):
  def __init__(self, caption):
    self.sprite = Sprite('small_button.png', center=False)
    self.label = self.MakeLabel(caption)
  def MakeLabel(self, caption):
    label = pyglet.text.Label(caption, font_size=15, color=(0, 0, 0, 255), anchor_x='center',
                              x=self.sprite.width / 2, y=-38)
    label.recreate_with = 'MakeLabel', caption
    return label
  def Height(self):
    return 64
  def Contains(self, x, y):
    return self.x < x < self.x + self.Width() and self.y - self.Height() < y < self.y
  def Spawn(self):
    return


class Pen(Container):
  NAME = 'Pen'
  def __init__(self, size):
    Container.__init__(self, self.NAME, *[Place() for i in range(size)])

class SmallPen(Pen):
  '''Holds 3.'''
  NAME = 'Small Pen'
  PRICE = 10
  def __init__(self):
    Pen.__init__(self, 3)

class LargePen(Pen):
  '''Holds 6.'''
  NAME = 'Large Pen'
  PRICE = 50
  def __init__(self):
    Pen.__init__(self, 6)


class Breeder(Container):
  """Let's you cross-breed any two animals."""
  NAME = 'Breeder'
  PRICE = 10
  def __init__(self):
    self.mother = Place()
    self.father = Place()
    self.button = Button('Breed')
    Container.__init__(self, self.NAME, self.mother, Label('+'), self.father, Label('='), self.button)
  def ButtonPress(self, button):
    if self.mother.card and self.father.card:
      Sound('breed.wav')
      creature = Creature((self.mother.card.creature.GetHalf(), self.father.card.creature.GetHalf()))
      card = Card(creature)
      game.cards.append(card)
      self.button.Spawn(card)
    else:
      Sound('rejected.wav')


class Tips(HasSprites):
  def __init__(self):
    self.tips = [
'Welcome to Lab Lab Bunny Lab! First some tips on navigating the user interface:\n\n'
'Use the mouse. Click and drag the background to pan the view. Scroll to zoom in or out.\n\n'
'You can also restart with "-f" to go to fullscreen. Your game is saved on exit so remember to exit often.'
, # 1
'We are in your rudimentary laboratory now. It is not much but you can get better equipment with a little effort.\n\n'
'For now buy two rabbits from the market and place them in the pen.\n\n'
'If you click a rabbit you can name it. If you drag it you can move it.'
, # 2
'Breed them using the breeder and sell the bunnies.\n\n'
'Yeah, so this "lab" is more like a farm. But wait until we can afford high-tech research tools!'
, # 3
'Okay, let\'s say you inherited some money. Go ahead and buy some fancy tools from the equipment store!\n\n'
, # 4
'Tips for using the Digitalizer:\n\n'
'1. You can map the genome of a creature by deleting parts of its genome and seeing what disappears.\n\n'
'2. To make your life easier return the same DNA for both chromosomes.\n\n'
'3. Look at data/*.py to see how the pre-made creatures are built. You can put the same code in DNA.py.'
, # 5
'The goal of the game is...\n\n'
'Not implemented yet. But try creating a rabbit with wings and I\'ll give you $1,000,000!\n\n'
'(Press next when you honestly have the ordered specimen!)'
, # 6
'Okay, I trust you!\n\n'
'Now make me something that looks like a giraffe! A long, flexible neck is  paramount'
' and will fetch you another $1,000,000!\n\n'
'(Press next when you honestly have the ordered specimen!)'
, # 7
'That\'s a nice giraffe if I\'ve ever seen one!\n\n'
'Create something with a lot of teeth! I need it to fight sharks!'
' My life is in danger so I offer you $1,000,000!\n\n'
'(Press next when you honestly have the ordered specimen!)'
, # 8
'Oh, no! The sharks got Beata before your monster got here!\n\n'
'I offer you my last dollar. Please create a bouquet a flowers that'
' I can remember her by.\n\n'
'(Press next when you honestly have the ordered specimen!)'
, # 9
'Congratulations!\n\n'
'Thanks for playing! Sorry the lack of clear goals. I got distracted by the bunnies.'
    ]
    self.tip_index = 0
    self.width = 800
    self.label = self.MakeLabel()
  def MakeLabel(self):
    label = pyglet.text.Label(self.tips[self.tip_index], font_size=18, width=self.width, color=(0, 0, 0, 255), x=25, y=-30, multiline=True)
    label.recreate_with = 'MakeLabel',
    return label
  def Contains(self, x, y):
    return False
  def Width(self):
    return self.width + 50
  def DrawFixed(self):
    self.label.draw()
  def Next(self):
    self.tip_index += 1
    if self.tip_index == 3:
      Sound('buy-big.wav')
      if game.money < 300:
        game.GiveMoney(300 - game.money)
    elif self.tip_index in (6, 7, 8):
      Sound('buy-big.wav')
      game.GiveMoney(1000000)
    elif self.tip_index == 9:
      Sound('buy-big.wav')
      game.GiveMoney(1)
    elif self.tip_index >= len(self.tips):
      self.tip_index -= 1
      Sound('rejected.wav')
    else:
      Sound('button.wav')
    self.label.text = self.tips[self.tip_index]


class Help(Container):
  NAME = 'Tips'
  def __init__(self):
    self.tips = Tips()
    Container.__init__(self, self.NAME, self.tips, Button('Next'))
  def ButtonPress(self, button):
    self.tips.Next()


class Market(Container):
  NAME = 'Market'
  def __init__(self):
    self.buy = Button('Buy')
    self.place = Place()
    self.sell = Button('Sell')
    self.price = 1
    self.species = 'data/bunny.py'
    Container.__init__(self, self.NAME, self.buy, self.place, self.sell)
  def ButtonPress(self, button):
    if button is self.buy:
      if not self.buy.card and game.money >= self.price:
        game.TakeMoney(self.price)
        card = Card(Creature(LoadDNA(self.species)))
        game.cards.append(card)
        self.buy.Spawn(card)
        Sound('buy-small.wav')
      else:
        Sound('rejected.wav')
    elif button is self.sell:
      if self.place.card:
        game.GiveMoney(self.price)
        game.cards.remove(self.place.card)
        self.place.card = None
        Sound('sell.wav')
      else:
        Sound('rejected.wav')


class ExoticAnimal(VerticalContainer):
  '''Gives you access to a randomly chosen fabulous species.'''
  NAME = 'Exotic Animal'
  PRICE = 20
  ANIMALS = 'chicken tree monkey'.split()
  def __init__(self):
    self.buy = Button('Buy')
    animal = random.choice(self.ANIMALS)
    # Let's not let honesty get in the way of a good story.
    already_have = 0
    for c in game.containers:
      if isinstance(c, ExoticAnimal):
        already_have += 1
    animal = self.ANIMALS[already_have % len(self.ANIMALS)]
    self.species = 'data/%s.py' % animal
    self.price = self.PRICE / 2
    VerticalContainer.__init__(self, animal.capitalize(), self.buy)
    self.freebie_spawned = False  # Have to spawn it once placed in-game.
  def Think(self):
    VerticalContainer.Think(self)
    if not self.freebie_spawned:
      game.GiveMoney(self.price)
      self.ButtonPress(self.buy)
      self.freebie_spawned = True
  def ButtonPress(self, button):
    if not self.buy.card and game.money >= self.price:
      Sound('buy-big.wav')
      game.TakeMoney(self.price)
      card = Card(Creature(LoadDNA(self.species)))
      game.cards.append(card)
      self.buy.Spawn(card)
    else:
      Sound('rejected.wav')


class Mutator(Container):
  '''Specimen goes into high-energy radiation cabin. Something else comes out.'''
  NAME = 'Mutator'
  PRICE = 25
  def __init__(self):
    self.place = Place()
    Container.__init__(self, self.NAME, self.place, Button('Mutate'))
  def ButtonPress(self, button):
    if self.place.card:
      a, b = self.place.card.creature.dna
      a, b = list(a), list(b)
      for i in range(len(a)):
        if random.random() < MUTATOR_STRENGTH:
          a[i] = random.choice(ALPHABET)
      for i in range(len(b)):
        if random.random() < MUTATOR_STRENGTH:
          b[i] = random.choice(ALPHABET)
      self.place.card.creature.SetDNA((''.join(a), ''.join(b)))
      Sound('mutate.wav')
    else:
      Sound('rejected.wav')


class Cloner(Container):
  '''Create an identical copy of a specimen. Think of it as backup.'''
  NAME = 'Cloning Vat'
  PRICE = 50
  def __init__(self):
    self.input = Place()
    self.output = Button('Clone')
    Container.__init__(self, self.NAME, self.input, self.output)
  def ButtonPress(self, button):
    if self.input.card:
      card = Card(Creature(self.input.card.creature.dna))
      game.cards.append(card)
      self.output.Spawn(card)
      Sound('clone.wav')
    else:
      Sound('rejected.wav')


class Digitalizer(VerticalContainer):
  '''Edit a creature's genome in a text editor and see the changes any time you save the file!'''
  PRICE = 100
  NAME = 'Digitalizer'
  def __init__(self):
    self.place = Place()
    self.place.listeners.append(self)
    self.last_load = 0
    VerticalContainer.__init__(self, self.NAME, self.place)
    
  def Drop(self, place):
    print 'Analyzing creature...'
    print place.card.creature.root
    dna = place.card.creature.dna
    with file('DNA.py', 'w') as f:
      f.write('''
# This file holds the DNA of the specimen in the Digitalizer.
#
# With the latest Digitalizer model genetic manipulation is at
# your fingertips! Just edit this file and as soon as you save it
# the creature in the Digitalizer's cabin will express its new
# genetic code! No need to restart the game!
#
# Digitalizer reports errors on the operator console. See the
# Troubleshooting section of the User's Manual or call our support
# line in case of persistent errors.
#
# Digitalizer Inc. reminds you of your legal and moral obligation
# for the respectful treatment of laboratory animals. Laughing
# at funny mutants is forbidden under the Animal Welfare Act.

def GetDNA():
  # This animal has 1 pair of homologous chromosomes.
  chromosome_a = '%s'
  chromosome_b = '%s'
  return chromosome_a, chromosome_b
      '''.strip() % dna + '\n')
    print 'Live DNA sample is in', os.path.abspath('dna.py')
  def Think(self):
    VerticalContainer.Think(self)
    if self.place.card:
      if self.last_load < os.stat('DNA.py').st_mtime:
        dna = LoadDNA('DNA.py')
        if dna:
          self.place.card.creature.SetDNA(dna)
        self.last_load = time.time()


class EquipmentStore(VerticalContainer):
  NAME = 'Equipment Store'
  def __init__(self):
    contents = []
    for cls in SmallPen, Breeder, ExoticAnimal, Mutator, Cloner, LargePen, Digitalizer:
      button = SmallButton(cls.NAME)
      button.cls = cls
      contents.append(button)
      label = VerticalLabel(cls.__doc__ + ' Cost: ' + Dollar(cls.PRICE))
      contents.append(label)
    VerticalContainer.__init__(self, 'Equipment Store', *contents)
  def ButtonPress(self, button):
    if game.money > button.cls.PRICE:
      Sound('buy-big.wav')
      game.TakeMoney(button.cls.PRICE)
      c = button.cls()
      c.x = button.x
      c.y = button.y
      game.containers.append(c)


class Game(object):
  def __init__(self):
    if MULTISAMPLING:
      config = pyglet.gl.Config(double_buffer=True, sample_buffers=1, samples=8)
    else:
      config = None
    if '-f' in sys.argv:
      self.window = pyglet.window.Window(config=config, fullscreen=True, caption='Lab Lab Bunny Lab')
    else:
      self.window = pyglet.window.Window(config=config, width=1000, height=700, caption='Lab Lab Bunny Lab')
    self.window.set_icon(pyglet.resource.image('icon16.png').get_image_data(), pyglet.resource.image('icon32.png').get_image_data(), pyglet.resource.image('icon128.png').get_image_data(), pyglet.resource.image('icon512.png').get_image_data())
    @self.window.event
    def on_draw():
      self.window.clear()
      self.Draw()
      self.window.invalid = False
    @self.window.event
    def on_text(text):
      for card in self.cards:
        if card.selected:
          card.KeyPress(text)
          return
    @self.window.event
    def on_text_motion(motion):
      if motion == pyglet.window.key.MOTION_BACKSPACE:
        for card in self.cards:
          if card.selected:
            card.Backspace()
            return
    @self.window.event
    def on_key_press(symbol, modifiers):
      for card in self.cards:
        if card.selected:
          if symbol == pyglet.window.key.ESCAPE:
            card.selected = False
          return True
      if symbol == pyglet.window.key.ESCAPE:
        self.Save()
    @self.window.event
    def on_mouse_press(x, y, button, modifiers):
      gx = (x - self.window.width / 2) / self.zoom - self.offset_x
      gy = (y - self.window.height / 2) / self.zoom - self.offset_y
      for card in self.cards:
        card.selected = False
      for card in self.cards:
        if card.Contains(gx, gy):
          card.selected = True
          card.held = True
          card.moved = False
          return
      for c in self.containers:
        c.held = False
      for c in reversed(self.containers):
        if c.Contains(gx, gy):
          c.held = True
          c.Clicked(gx, gy)
          return
    @self.window.event
    def on_mouse_release(x, y, button, modifiers):
      gx = (x - self.window.width / 2) / self.zoom - self.offset_x
      gy = (y - self.window.height / 2) / self.zoom - self.offset_y
      for c in self.containers:
        c.held = False
      for card in self.cards:
        card.held = False
        if card.moved:
          card.selected = False
          card.moved = False
          # Is the mouse inside any "Place"?
          for c in reversed(self.containers):
            for x in c.contents:
              if hasattr(x, 'Drop') and x.Contains(gx, gy):
                x.Drop(card)
                return
    @self.window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
      for c in self.containers:
        if c.held:
          c.x += dx / self.zoom
          c.y += dy / self.zoom
          return
      for card in self.cards:
        if card.held:
          card.x += dx / self.zoom
          card.y += dy / self.zoom
          card.moved = True
          return
      self.offset_x += dx / self.zoom
      self.offset_y += dy / self.zoom
    @self.window.event
    def on_key_release(symbol, modifiers):
      pass
    @self.window.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
      self.zoom_count += scroll_y
    pyglet.clock.schedule_interval(self.Think, 1 / 60.0)
    
    if os.path.exists('save_game'):
      with file('save_game') as f:
        data = pickle.load(f)
      self.__dict__.update(data)
    else:
      self.offset_x, self.offset_y = 0, 150
      self.zoom_count = -16
      self.zoom = 2 ** (0.05 * self.zoom_count)
      
      self.cards = []
      self.containers = [Help(), Breeder(), SmallPen(), Market(), EquipmentStore()]
      WW = self.window.width / self.zoom
      WH = self.window.height / self.zoom
      self.containers[0].x = -WW / 2 + 50
      self.containers[0].y = -WH / 2 + 330
      self.containers[1].x = -WW / 2 + 50
      self.containers[1].y = -WH / 2 + 660
      self.containers[2].x = -WW / 2 + 750
      self.containers[2].y = -WH / 2 + 990
      self.containers[3].x = -WW / 2 + 50
      self.containers[3].y = -WH / 2 + 990
      self.containers[4].x = -WW / 2 + 1450
      self.containers[4].y = -WH / 2 + 990
      
      self.money = STARTING_MONEY
    self.title = Sprite('title.png', mipmap=False)
    self.title_time = -TITLE_HOLD
    self.money_background = Sprite('label.png', mipmap=False, center=False)
    self.money_background.y = self.window.height - self.money_background.height
    self.money_label = pyglet.text.Label(Dollar(self.money), x=120, y=self.window.height - 20, color=(0, 0, 0, 255), anchor_x='right')
    if MUSIC:
      self.music = pyglet.media.Player()
      self.song_index = random.randrange(len(SONGS))
  
  def Start(self):
    glClearColor(0.9, 0.9, 0.9, 0)
    pyglet.app.run()

  def Draw(self):
    glLoadIdentity()
    glTranslatef(self.window.width / 2, self.window.height / 2, 0)
    if self.title_time > 0:
      glScalef(self.zoom, self.zoom, 1)
      glTranslatef(self.offset_x, self.offset_y, 0)
      # Sort by "distance".
      stuff = self.containers + self.cards
      stuff.sort(key=lambda c: -c.place.y if isinstance(c, Card) else -c.y)
      # Held card on top.
      stuff.sort(key=lambda c: isinstance(c, Card) and c.held)
      for c in stuff:
        c.Draw()
    glLoadIdentity()
    self.money_background.draw()
    self.money_label.draw()
    if self.title_time < TITLE_FADE:
      alpha = 1 - float(max(0, self.title_time)) / TITLE_FADE
      glColor4f(0.9, 0.9, 0.9, alpha)
      glEnable(GL_BLEND)
      glLoadIdentity()
      glBegin(GL_QUADS)
      glVertex3f(0, 0, 0)
      glVertex3f(self.window.width, 0, 0)
      glVertex3f(self.window.width, self.window.height, 0)
      glVertex3f(0, self.window.height, 0)
      glEnd()
      glTranslatef(self.window.width / 2, self.window.height / 2, 0)
      self.title.opacity = 255 * alpha
      self.title.draw()
    self.title_time += 1

  def Think(self, dt):
    zoom_target = 2 ** (0.05 * self.zoom_count)
    self.zoom = (self.zoom + zoom_target) / 2
    for c in self.containers:
      c.Think()
    for card in self.cards:
      card.Think()
    self.window.invalid = True
    if hasattr(self, 'music') and not self.music.playing:
      try:
        self.music.queue(pyglet.resource.media(SONGS[self.song_index % len(SONGS)]))
        self.song_index += 1
        self.music.play()
      except:
        print 'AVbin is missing. No music for you!'
        del self.music
    
  def Save(self):
    data = {}
    for k in 'cards containers offset_x offset_y zoom zoom_count money'.split():
      data[k] = getattr(self, k)
    with file('save_game', 'w') as f:
      pickle.dump(data, f)
#    print 'Game saved.'

  def GiveMoney(self, money):
    self.money += money
    self.money_label.text = Dollar(self.money)
    
  def TakeMoney(self, money):
    self.money -= money
    self.money_label.text = Dollar(self.money)
      
  def StopMusic(self):
    if hasattr(self, 'music'):
      self.music.pause()
      del self.music
    
def Dollar(money):
  m = '%03d' % (money % 1000)
  money /= 1000
  while money:
    m = '%03d,%s' % (money % 1000, m)
    money /= 1000
  m = m.lstrip('0')
  if not m:
    m = '0'
  return '$' + m

if __name__ == '__main__':
  game = Game()
  game.Start()
