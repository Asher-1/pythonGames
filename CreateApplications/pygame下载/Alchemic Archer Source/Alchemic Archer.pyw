# Setup Python ----------------------------------------------- #
import pygame, sys, random, time, webbrowser, os, math
from datetime import datetime
import ThiSisa_Reader as map_loader
import Text

"""
K_F11   Fullscreen
"""

# Version ---------------------------------------------------- #
Version = '1.0'
# Setup pygame/window ---------------------------------------- #
mainClock = pygame.time.Clock()
from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.display.set_caption('Alchemic Archer')
Icon = pygame.image.load('Data/Images/Misc/icon.png')
Icon.set_colorkey((189, 234, 249))
WINDOWWIDTH = 720
WINDOWHEIGHT = 480
global fullscreen
fullscreen = False
global screen
screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
DisplaySurf = pygame.Surface((240, 160))
pygame.mouse.set_visible(False)
Icon = pygame.image.load('Data/Images/Misc/icon.png')
Icon.set_colorkey((189, 234, 249))
pygame.display.set_icon(Icon)
# Font ------------------------------------------------------- #
basicFont = pygame.font.SysFont(None, 20)
Font_0 = {'A': [6], 'B': [6], 'C': [6], 'D': [6], 'E': [6], 'F': [6], 'G': [6], 'H': [6], 'I': [6], 'J': [6], 'K': [6],
          'L': [6], 'M': [6], 'N': [6], 'O': [6], 'P': [6], 'Q': [6], 'R': [6], 'S': [6], 'T': [6], 'U': [6], 'V': [6],
          'W': [6], 'X': [6], 'Y': [6], 'Z': [6], '.': [3], '-': [6], ',': [3], ':': [3], '+': [6], '\'': [3],
          'a': [6], 'b': [6], 'c': [6], 'd': [6], 'e': [6], 'f': [5], 'g': [6], 'h': [6], 'i': [2], 'j': [5], 'k': [5],
          'l': [3], 'm': [6], 'n': [5], 'o': [6], 'p': [6], 'q': [6], 'r': [5], 's': [5], 't': [5], 'u': [5], 'v': [6],
          'w': [6], 'x': [6], 'y': [6], 'z': [6], '!': [2], '?': [6],
          '0': [6], '1': [3], '2': [6], '3': [6], '4': [6], '5': [6], '6': [6], '7': [6], '8': [6], '9': [6]}

Font_1 = {'A': [6], 'B': [6], 'C': [6], 'D': [6], 'E': [6], 'F': [6], 'G': [6], 'H': [6], 'I': [6], 'J': [6], 'K': [6],
          'L': [6], 'M': [6], 'N': [6], 'O': [6], 'P': [6], 'Q': [6], 'R': [6], 'S': [6], 'T': [6], 'U': [6], 'V': [6],
          'W': [6], 'X': [6], 'Y': [6], 'Z': [6], '.': [3], '-': [6], ',': [3], ':': [3], '+': [6], '\'': [3],
          'a': [6], 'b': [6], 'c': [6], 'd': [6], 'e': [6], 'f': [5], 'g': [6], 'h': [6], 'i': [2], 'j': [5], 'k': [5],
          'l': [3], 'm': [6], 'n': [5], 'o': [6], 'p': [6], 'q': [6], 'r': [5], 's': [5], 't': [5], 'u': [5], 'v': [6],
          'w': [6], 'x': [6], 'y': [6], 'z': [6], '!': [2], '?': [6],
          '0': [6], '1': [3], '2': [6], '3': [6], '4': [6], '5': [6], '6': [6], '7': [6], '8': [6], '9': [6]}

Font_0 = Text.GenerateFont('Data/Images/Font/Font.png', Font_0, 11)
Font_1 = Text.GenerateFont('Data/Images/Font/Font_2.png', Font_1, 11)
# Images ----------------------------------------------------- #
selector = pygame.image.load('Data/Images/Misc/selector.png').convert()
selector.set_colorkey((255, 255, 255))
ArrowImg = pygame.image.load('Data/Images/Misc/arrow.png').convert()
ArrowImg.set_colorkey((255, 255, 255))
item_bar = pygame.image.load('Data/Images/Misc/item_bar.png').convert()
item_bar.set_colorkey((255, 255, 255))
heart = pygame.image.load('Data/Images/Misc/heart.png').convert()
heart.set_colorkey((255, 255, 255))
twitter = pygame.image.load('Data/Images/Misc/twitter.png').convert()
twitter.set_colorkey((255, 255, 255))
x_buttons = [pygame.image.load('Data/Images/Misc/button_x.png').convert(),
             pygame.image.load('Data/Images/Misc/button_x_2.png').convert()]
z_buttons = [pygame.image.load('Data/Images/Misc/button_z.png').convert(),
             pygame.image.load('Data/Images/Misc/button_z_2.png').convert()]
x_buttons[0].set_colorkey((255, 255, 255))
x_buttons[1].set_colorkey((255, 255, 255))
z_buttons[0].set_colorkey((255, 255, 255))
z_buttons[1].set_colorkey((255, 255, 255))
x_use = False
z_use = False
c_use = False
button_timer = 0
button_frame = 0
Item_Images = {}
Item_List = ['snail', 'butterfly', 'guts', 'mushroom', 'flower']
for Item in Item_List:
    img = pygame.image.load('Data/Images/Items/' + str(Item) + '.png').convert()
    img.set_colorkey((255, 255, 255))
    Item_Images[Item] = img.copy()
global PotionImg
PotionImg = pygame.image.load('Data/Images/Misc/potion.png').convert()
global Potions
Potions = {
    'weakness': [(74, 101, 140), 6],
    'slowness': [(87, 75, 53), 8],
    'paralysis': [(179, 212, 122), 4],
    'knockback': [(240, 0, 120), 8]
}


def PotionImage(ID, amount):
    global PotionImg
    global Potions
    amount = round(amount / Potions[ID][1] * 4, 0)
    if amount == 0:
        amount = 1
    img = PotionImg.copy()
    back_surf = pygame.Surface((8, 8))
    back_surf.fill((255, 255, 255))
    liquid = pygame.Surface((8, amount))
    liquid.fill(Potions[ID][0])
    back_surf.blit(liquid, (0, 4 - amount + 3))
    img.set_colorkey((0, 0, 0))
    back_surf.blit(img, (0, 0))
    back_surf.set_colorkey((255, 255, 255))
    return back_surf


# Audio ------------------------------------------------------ #
Sounds = [
    ['Ambience_0', 1],
    ['Ambience_1', 1],
    ['Pew_0', 0.5],
    ['Pop_0', 1],
    ['Squish_0', 1],
    ['Step_0', 1],
    ['Step_1', 1],
    ['Take_0', 1],
    ['Hit_0', 1]
]
SFX = {}
for sound in Sounds:
    sound2 = pygame.mixer.Sound('Data/SFX/' + sound[0] + '.wav')
    sound2.set_volume(sound[1])
    SFX[sound[0]] = sound2
# Colors ----------------------------------------------------- #
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY3 = (105, 105, 105)
GRAY = (195, 195, 195)
GRAY2 = (127, 127, 127)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
PURPLE = (115, 0, 242)
# Variables -------------------------------------------------- #
global DisplayR
global Image_Database
global CHUNK_SIZE
CHUNK_SIZE = 50
global ScrollX
global ScrollY
global Held_Item
Held_Item = ''
JUMP_MAX = 2
ScrollX = 0
ScrollY = 0
Moving_Right = False
Moving_Left = False
last_dir = 'r'
CDown = False
invincible = 0
fade = 3
Collisions = []
SolidTiles = ['Dirt_0', 'Dirt_1', 'Dirt_2', 'Dirt_3', 'Dirt_4', 'Dirt_5']
DisplayR = pygame.Rect(ScrollX, ScrollY, 240, 240)
Arrows = []
Particles = []
player_collisions = [False, False, False, False]
NPCparticles = {
    'blob': (211, 58, 116),
    'spike_blob': (211, 58, 116),
    'flying_blob': (211, 58, 116)
}
Jumps = JUMP_MAX
item_checkR = pygame.Rect(0, 0, 2, 2)
TextQueue = []
Held_Potions = {}
Selected_Potion = 0
FX = []
Wind = {
    5: [],
    4: [],
    3: [],
    2: []
}
wind_strength = 1


def gen_trees():
    random.randint(1, 4)
    Trees = {5: [], 4: [], 3: [], 2: []}
    for l in range(3):
        num = 0
        random.randint(1, 4)
        for i in range(30):
            random.randint(1, 4)
            Trees[l + 2].append([num, random.randint(4, 6) * 12 / (l + 2)])
            num += random.randint(36, 48)
    return Trees


Trees = gen_trees()
TreeLayers = {
    4: (179, 212, 122),
    3: (106, 183, 115),
    2: (51, 120, 115)
}
# Rects ------------------------------------------------------ #
# FPS -------------------------------------------------------- #
FPS = 80
TrueFPSCount = 0
TrueFPS = 0
fpsOn = False
PrevNow = 0


# Physics Stuff ---------------------------------------------- #
def CollisionTest(Object1, ObjectList):
    CollisionList = []
    for Object in ObjectList:
        ObjectRect = pygame.Rect(Object[0], Object[1], Object[2], Object[3])
        if ObjectRect.colliderect(Object1):
            CollisionList.append(ObjectRect)
    return CollisionList


class PhysicsObject(object):
    def __init__(self, x, y, w, h):
        self.width = w
        self.height = h
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def Move(self, Movement, platforms):
        collisions = [False, False, False, False]
        self.rect.x += Movement[0]
        block_hit_list = CollisionTest(self.rect, platforms)
        for block in block_hit_list:
            if Movement[0] > 0:
                collisions[2] = True
                self.rect.right = block.left
            elif Movement[0] < 0:
                collisions[3] = True
                self.rect.left = block.right
        self.rect.y += Movement[1]
        block_hit_list = CollisionTest(self.rect, platforms)
        for block in block_hit_list:
            if Movement[1] > 0:
                collisions[0] = True
                self.rect.bottom = block.top
            elif Movement[1] < 0:
                collisions[1] = True
                self.rect.top = block.bottom
            self.change_y = 0
        return collisions

    def Draw(self):
        pygame.draw.rect(screen, (0, 0, 255), self.rect)

    def CollisionItem(self):
        CollisionInfo = [self.rect.x, self.rect.y, self.width, self.height]
        return CollisionInfo


# Functions/Classes ------------------------------------------ #
def run_title():
    global fullscreen
    global screen
    running = True
    selection = 0
    options = ['play', 'help', 'exit']
    show_help = False
    help_text = 'Controls:\nZ - Take\nX - Jump\nC - Shoot\nRight and Left Arrow Keys - Move\nUp and Down Arrow Keys - Cycle Through Potions\nF11 - Fullscreen\n\nInstructions:\nTry to get through the world alive! Kill blobs for health. Blobs can also kill you! Collect items to combine with gooey blob guts to make potions. Potions are used to tip your arrows, which add effects to your arrows. It\'s your job to figure out what they do!\n\nSample Combination:\nSnail and Gooey Guts: Slowing Potion\n\nUser Interface:\nHealth is shown on the top left, your current item is shown on the bottom right, and your potions are shown on the bottom left.\nRemember: Cycle through potions with the up and down arrow keys.\n\nPress X '
    while running == True:
        screen.fill(BLACK)
        DisplaySurf.fill(BLACK)
        DisplaySurf.blit(twitter, (2, DisplaySurf.get_height() - 12))
        num = 0
        for option in options:
            if num == selection:
                Text.ShowText(option + ' ', 5, 2 + num * 12, 1, 1000, Font_1, DisplaySurf)
                Bar = pygame.Surface((1, 7))
                Bar.fill((45, 58, 104))
                DisplaySurf.blit(Bar, (2, 2 + num * 12))
            else:
                Text.ShowText(option + ' ', 2, 2 + num * 12, 1, 1000, Font_1, DisplaySurf)
            num += 1
        Text.ShowText('DaFluffyPotato ', 16, DisplaySurf.get_height() - 10, 1, 1000, Font_0, DisplaySurf)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_F11:
                    if fullscreen == False:
                        fullscreen = True
                        screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.FULLSCREEN)
                    else:
                        fullscreen = False
                        screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if show_help == False:
                    if event.key == K_UP:
                        selection -= 1
                        if selection < 0:
                            selection = 0
                    if event.key == K_DOWN:
                        selection += 1
                        if selection >= len(options):
                            selection = len(options) - 1
                if (event.key == K_RETURN) or (event.key == ord('x')):
                    if show_help == False:
                        if options[selection] == 'play':
                            running = False
                        elif options[selection] == 'help':
                            show_help = True
                        elif options[selection] == 'exit':
                            pygame.quit()
                            sys.exit()
                    else:
                        show_help = False
        screen.blit(pygame.transform.scale(DisplaySurf, (720, 480)), (0, 0))
        if show_help == True:
            screen.fill(BLACK)
            Text.ShowText(help_text, 2, 2, 1, 720, Font_1, screen)
        pygame.display.update()
        mainClock.tick(40)


def Combine(Held_Item, New_Item):
    Result = ''
    Chart = {
        'snail': 'slowness',
        'butterfly': 'weakness',
        'mushroom': 'paralysis',
        'flower': 'knockback'
    }
    if Held_Item == 'guts':
        if New_Item in Chart:
            Result = Chart[New_Item]
    elif New_Item == 'guts':
        if Held_Item in Chart:
            Result = Chart[Held_Item]
    return Result


def AddParticles(Particles, x, y, colors, speed_range, duration_range, amount, handle='normal', handle_args=1):
    for i in range(amount):
        speed = random.randint(speed_range[0] * 100, speed_range[1] * 100)
        speed /= 100
        duration = random.randint(duration_range[0], duration_range[1])
        color = random.choice(colors)
        x_speed = random.randint(1, 100)
        x_speed /= 100
        x_speed *= speed
        y_speed = speed - x_speed
        if random.randint(1, 2) == 1:
            x_speed *= -1
        if random.randint(1, 2) == 1:
            y_speed *= -1
        Particles.append([x, y, x_speed, y_speed, color, speed, 0, duration, handle, handle_args])


def load_entities(Map, entity_IDs):
    global entity_sizes
    entity_list = []
    num = 0
    RemoveList = []
    for Chunk in Map:
        num = 0
        for Tile in Map[Chunk]:
            if Tile[0] in entity_IDs:
                entity_type = entity_IDs[Tile[0]]
                entity_list.append([Tile[0], entity_type, Tile[2], Tile[3]])
                RemoveList.append([num, Chunk])
                num -= 1
            num += 1
    for Item in RemoveList:
        Map[Item[1]].remove(Map[Item[1]][Item[0]])
    NPCs = []
    Items = []
    spawn = [0, 0]
    end = []
    for entity in entity_list:
        if entity[1] == 'start':
            spawn = [entity[2], entity[3]]
        if entity[1] == 'end':
            end.append([entity[2], entity[3]])
        elif entity[1] == 'npc':
            NPCs.append(Entity(entity[0], entity[2], entity[3], entity_sizes[entity[0]][0], entity_sizes[entity[0]][1]))
        elif entity[1] == 'item':
            Items.append([entity[0], entity[2], entity[3]])
    return Map, NPCs, Items, spawn, end


def load_animation(directory, amount, flip=False):
    images = []
    for i in range(amount):
        img = pygame.image.load(directory + '/' + str(i) + '.png').convert()
        img.set_colorkey((255, 255, 255))
        if flip == True:
            img = pygame.transform.flip(img, True, False)
        images.append(img)
    return images


def load_map(name):
    global CHUNK_SIZE
    l, m = map_loader.load('Data/Maps/' + name)
    m = map_loader.format_tiles(m, CHUNK_SIZE)
    return l, m


def load_tiles(base_name, total):
    images = {}
    for i in range(total):
        name = base_name + '_' + str(i)
        img = pygame.image.load('Data/Images/Tiles/' + name + '.png').convert()
        img.set_colorkey((255, 255, 255))
        images[name] = img.copy()
    return images


class DisplayObjects():
    def __init__(self):
        self.queue = {}

    def add(self, item, layer):
        if layer not in self.queue:
            self.queue[layer] = []
        self.queue[layer].append(item)

    def display(self, surf):
        for layer in self.queue:
            for item in self.queue[layer]:
                surf.blit(item[0], (item[1], item[2]))
        self.queue = {}


class Entity():
    global Image_Database
    global Animation_Data
    global Animations
    global entity_stats
    global DisplayR

    def __init__(self, entity_type, x, y, size_x, size_y, gravity_speed=0.2, gravity_max=4):
        self.type = entity_type
        self.x = x
        self.y = y
        self.x_size = size_x
        self.y_size = size_y
        self.grounded = False
        self.gravity = 0
        self.gravity_speed = 0.2
        self.gravity_max = 4
        self.x_momentum = 0
        self.collisions = [False, False, False, False]
        self.obj = PhysicsObject(self.x, self.y, self.x_size, self.y_size)
        self.health = entity_stats[self.type][0]
        if self.type == 'player':
            self.animation = 4
        else:
            self.animation = 0
        self.animation_frame = 0
        self.animation_timer = 0
        self.last_movement = [0, 0]
        self.status = None
        # player: 2: running right 3: running left 4: drawing back bow

    def move(self, Movement, platforms):
        Movement[1] += self.gravity
        Movement[0] += self.x_momentum
        self.last_movement = Movement
        self.gravity += self.gravity_speed
        if self.gravity > self.gravity_max:
            self.gravity = self.gravity_max
        collisions = self.obj.Move(Movement, platforms)
        self.grounded = collisions[0]
        self.collisions = collisions
        if (self.grounded == True) or (self.collisions[1] == True):
            self.gravity = 0
        self.x = self.obj.rect.x
        self.y = self.obj.rect.y
        return collisions

    def display(self):
        animation_state = [self.animation, self.animation_frame, self.animation_timer]
        x_change = 0
        y_change = 0
        if self.type == 'player':
            # \/ player specific animation logic \/
            if self.last_movement[0] > 0:
                self.animation = 2
            elif self.last_movement[0] < 0:
                self.animation = 3
            elif self.last_movement[0] == 0:
                if self.animation == 2:
                    self.animation = 4
                if self.animation == 3:
                    self.animation = 5
            x_change = -1
            y_change = -1
            # /\ player specific animation logic /\
        elif self.type == 'blob':
            left_m = [0, 1, 3]
            right_m = [0, 2, 4]
            if self.last_movement[0] > 0:
                if self.animation in left_m:
                    self.animation = 2
            elif self.last_movement[0] < 0:
                if self.animation in right_m:
                    self.animation = 1
            elif self.last_movement[0] == 0:
                self.animation = 0
            if animation_state == [2, 3, 2]:
                self.animation = 4
                self.animation_timer = 0
                self.animation_frame = 0
            if animation_state == [1, 3, 2]:
                self.animation = 3
                self.animation_timer = 0
                self.animation_frame = 0
        elif self.type == 'spike_blob':
            if self.grounded == False:
                if self.animation == 0:
                    if self.gravity < 0:
                        self.animation_timer = 0
                        self.animation = 3
            elif self.grounded == True:
                if self.animation == 3:
                    self.animation = 0
            if animation_state == [3, 3, 2]:
                self.animation_timer = 0
        self.animation_timer += 1
        if self.animation_timer >= AnimationData[self.type][self.animation][1]:
            self.animation_timer = 0
            self.animation_frame += 1
        if self.animation_frame >= AnimationData[self.type][self.animation][0]:
            self.animation_frame = 0
            if self.type == 'player':
                if self.last_movement[0] != 0:
                    if self.grounded == True:
                        random.choice([SFX['Step_0'], SFX['Step_1']]).play()
        img = Animations[AnimationData[self.type][self.animation][2]][self.animation_frame]
        DisplaySurf.blit(img, (self.x + x_change + ScrollX, self.y + y_change + ScrollY))

    def AI(self, target, platforms, speed):
        if (self.type == 'blob') or (self.type == 'spike_blob'):
            chasing = False
            if self.type == 'spike_blob':
                if abs(self.x - target.x) < 120:
                    if abs(self.y - target.y) < 36:
                        if random.randint(1, 15) == 1:
                            if self.grounded == True:
                                self.gravity = -3
                                self.animation = 3
                        chasing = True
            if self.type == 'blob':
                if abs(self.x - target.x) < 100:
                    if abs(self.y - target.y) < 18:
                        chasing = True
            if chasing == True:
                if target.x < self.x:
                    if self.x_momentum > 0:
                        self.x_momentum = 0
                    self.x_momentum -= 0.1
                    if self.x_momentum < -2 * speed:
                        self.x_momentum = -2 * speed
                elif target.x > self.x:
                    if self.x_momentum < 0:
                        self.x_momentum = 0
                    self.x_momentum += 0.1
                    if self.x_momentum > 2 * speed:
                        self.x_momentum = 2 * speed
            if chasing == False:
                self.last_movement[0] = 0
                if self.type == 'blob':
                    self.x_momentum = 0
                    self.animation = 0
                    self.animation_timer = 0
                    self.animation_frame = 0
            collisions = self.move([0, 0], platforms)
            if (collisions[2] == True) or (collisions[3] == True):
                self.last_movement[0] = 0
                if self.type == 'blob':
                    self.x_momentum = 0
                    self.animation = 0
                    self.animation_timer = -10
                    self.animation_frame = 0
        elif self.type == 'flying_blob':
            if target.x < self.x:
                self.x_momentum -= 0.1
                if self.x_momentum < -1 * speed:
                    self.x_momentum = -1 * speed
            if target.x > self.x:
                self.x_momentum += 0.1
                if self.x_momentum > 1 * speed:
                    self.x_momentum = 1 * speed
            if abs(target.x - self.x) < 50:
                self.gravity = 2
            else:
                self.gravity = -2
            if self.obj.rect.colliderect(DisplayR):
                collisions = self.move([0, 0], platforms)


class AnimatedObject():
    global Image_Database
    global Animation_Data
    global Animations

    # destroy: deletes itself on completion, pause: stops on last frame, loop: loops
    def __init__(self, obj_type, x, y, handle='destroy'):
        self.type = obj_type
        self.x = x
        self.y = y
        self.animation = 0
        self.animation_frame = 0
        self.animation_timer = 0
        self.handle = handle

    def display(self):
        done = False
        self.animation_timer += 1
        if self.animation_timer >= AnimationData[self.type][self.animation][1]:
            self.animation_timer = 0
            self.animation_frame += 1
        if self.animation_frame >= AnimationData[self.type][self.animation][0]:
            if self.handle == 'destroy':
                done = True
                self.animation_frame = AnimationData[self.type][self.animation][0] - 1
            elif self.handle == 'pause':
                self.animation_frame = AnimationData[self.type][self.animation][0] - 1
            elif self.handle == 'loop':
                self.animation_frame = 0
        img = Animations[AnimationData[self.type][self.animation][2]][self.animation_frame]
        DisplaySurf.blit(img, (self.x + ScrollX, self.y + ScrollY))
        return done

    def change(self, item, value):
        if item == 'animation':
            self.animation = value
        if item == 'location':
            self.x = value[0]
            self.y = value[1]
        if item == 'frame':
            self.animation_frame = value


def Get_Potion(Held_Potions, selection):
    num = 0
    ID = None
    for Potion in Held_Potions:
        if num == selection:
            ID = Potion
        num += 1
    return ID


# Initiate Functions/Classes --------------------------------- #
run_title()
Tile_Database = {}
Tile_Database.update(load_tiles('Dirt', 10))
Tile_Database.update(load_tiles('Bush', 1))
DisplayedObjects = DisplayObjects()
Level = 1
Layers, Map = load_map('Level_1')
entity_IDs = {
    'end': 'end',
    'start': 'start',
    'blob': 'npc',
    'spike_blob': 'npc',
    'flying_blob': 'npc',
    'snail': 'item',
    'butterfly': 'item',
    'mushroom': 'item',
    'flower': 'item'
}
global entity_stats
entity_stats = {
    'blob': [2],
    'spike_blob': [6],
    'flying_blob': [4],
    'player': [5]
}
global entity_sizes
entity_sizes = {
    'blob': [12, 12],
    'spike_blob': [12, 12],
    'flying_blob': [12, 12]
}
global AnimationData
# ID: {animation_state:[total_frames,rate,animation_ID]}
AnimationData = {
    'player': {5: [1, 1, 'player_walking2'], 4: [1, 1, 'player_walking'], 2: [3, 3, 'player_walking'],
               3: [3, 3, 'player_walking2']},
    'bow': {0: [3, 4, 'bow'], 1: [3, 4, 'bow2']},
    'blob': {0: [1, 1, 'blob_start'], 1: [4, 3, 'blob_start'], 2: [4, 3, 'blob_start2'], 3: [3, 3, 'blob_moving'],
             4: [3, 3, 'blob_moving2']},
    'snail': {0: [23, 30, 'snail']},
    'mushroom': {0: [1, 1, 'mushroom']},
    'flower': {0: [1, 1, 'flower']},
    'butterfly': {0: [12, 1, 'butterfly']},
    'spike_blob': {0: [1, 1, 'spike_blob'], 1: [1, 1, 'spike_blob'], 2: [1, 1, 'spike_blob'], 3: [4, 3, 'spike_blob']},
    'flying_blob': {0: [5, 4, 'flying_blob']},
    'jump': {0: [12, 2, 'jump']},
    'turn': {0: [14, 1, 'turn']},
    'turn2': {0: [14, 1, 'turn2']}
}
global Animations
Animations = {}
Animations['player_walking'] = load_animation('Data/Images/Entities/Player/Walking', 3)
Animations['player_walking2'] = load_animation('Data/Images/Entities/Player/Walking', 3, True)
Animations['bow'] = load_animation('Data/Images/Entities/Player/Bow', 4)
Animations['bow2'] = load_animation('Data/Images/Entities/Player/Bow', 4, True)
Animations['blob_start'] = load_animation('Data/Images/Entities/Blob/Start', 4)
Animations['blob_start2'] = load_animation('Data/Images/Entities/Blob/Start', 4, True)
Animations['blob_moving'] = load_animation('Data/Images/Entities/Blob/Moving', 3)
Animations['blob_moving2'] = load_animation('Data/Images/Entities/Blob/Moving', 3, True)
Animations['snail'] = load_animation('Data/Images/Entities/Snail', 23)
Animations['butterfly'] = load_animation('Data/Images/Entities/Butterfly', 12)
Animations['spike_blob'] = load_animation('Data/Images/Entities/SpikeBlob', 4)
Animations['flying_blob'] = load_animation('Data/Images/Entities/FlyingBlob', 5)
Animations['mushroom'] = load_animation('Data/Images/Entities/Mushroom', 1)
Animations['flower'] = load_animation('Data/Images/Entities/Flower', 1)
Animations['jump'] = load_animation('Data/Images/Entities/Jump', 12)
Animations['turn'] = load_animation('Data/Images/Entities/Turn', 14)
Animations['turn2'] = load_animation('Data/Images/Entities/Turn', 14, True)
CurrentAnimations = []
Map, NPCs, Items, spawn, end = load_entities(Map, entity_IDs)
Player = Entity('player', spawn[0], spawn[1], 4, 7)
ScrollX = -(-DisplaySurf.get_width() / 2 + spawn[0])
ScrollY = -(-DisplaySurf.get_height() / 2 + spawn[1])
pygame.mixer.music.load('Data/Music/Main2.wav')
pygame.mixer.music.set_volume(0.075)
pygame.mixer.music.play(-1)
SFX['Ambience_1'].play(9999)
# Loop ------------------------------------------------------- #
while True:
    # Background --------------------------------------------- #
    screen.fill(BLACK)
    DisplaySurf.fill((149, 221, 244))
    ScrollX -= (Player.x + ScrollX - DisplaySurf.get_width() / 2) / 10
    ScrollY -= (Player.y + ScrollY - DisplaySurf.get_height() / 2) / 10
    ScrollX = round(ScrollX, 2)
    ScrollY = round(ScrollY, 2)
    # Handle Things ------------------------------------------ #
    DisplayR = pygame.Rect(-ScrollX, -ScrollY, 240, 240)
    VisibleDisplayR = pygame.Rect(0, 0, 240, 160)
    # buttons
    button_timer += 1
    if button_timer == 20:
        button_timer = 0
        button_frame += 1
        if button_frame > 1:
            button_frame = 0
    # trees
    TreeGroups = [5, 4, 3, 2]
    if random.randint(1, 80) == 1:
        wind_strength += random.randint(1, 3) - 2
    if wind_strength > 6:
        wind_strength = 6
    if wind_strength < 0:
        wind_strength = 0
    if random.randint(1, (7 - wind_strength) * 2) == 1:
        # layer: x, y, speed, size
        Wind[2].append(
            [240, random.randint(0, 160), random.randint(4 + int(wind_strength / 2), 6 + int(wind_strength / 2)),
             random.randint(4, 16)])
    if random.randint(1, (7 - wind_strength) * 2) == 1:
        Wind[random.randint(2, 5)].append(
            [240, random.randint(0, 160), random.randint(4 + int(wind_strength / 2), 6 + int(wind_strength / 2)),
             random.randint(4, 16)])
    for Layer in Wind:
        for Gust in Wind[Layer]:
            Gust[0] -= Gust[2]
            if Gust[0] < -20:
                try:
                    Wind[Layer].remove(Gust)
                except:
                    pass
    for TreeGroup in TreeGroups:
        for Tree in Trees[TreeGroup]:
            TreeR = pygame.Rect(Tree[0] + ScrollX / TreeGroup, 0, Tree[1], 160)
            if TreeR.colliderect(VisibleDisplayR):
                pass
            TreeSurf = pygame.Surface((Tree[1], 160))
            TreeSurf.fill(TreeLayers[TreeGroup])
            DisplaySurf.blit(TreeSurf, (Tree[0] + ScrollX / TreeGroup, 0))
        for Gust in Wind[TreeGroup]:
            GustSurf = pygame.Surface((Gust[3], 1))
            GustSurf.fill((161, 168, 204))
            DisplaySurf.blit(GustSurf, (Gust[0], Gust[1]))
    # tiles
    NeededChunks = {}
    for y in range(int(DisplaySurf.get_height() / CHUNK_SIZE) + 3):
        for x in range(int(DisplaySurf.get_width() / CHUNK_SIZE) + 3):
            xc = x - 1
            yc = y - 1
            xc += int(-ScrollX / CHUNK_SIZE)
            yc += int(-ScrollY / CHUNK_SIZE)
            Chunk = str(xc) + ',' + str(yc)
            if Chunk in Map:
                NeededChunks[Chunk] = Map[Chunk]
    Collisions = []
    for Chunk in NeededChunks:
        for Tile in NeededChunks[Chunk]:
            cy = 0
            if Tile[0] == 'Bush_0':
                cy = 1
            DisplayedObjects.add([Tile_Database[Tile[0]], Tile[2] + ScrollX, Tile[3] + ScrollY + cy], int(Tile[1]))
            if Tile[0] in SolidTiles:
                Collisions.append([Tile[2], Tile[3] + 1, 12, 11])
    # items
    closest = [None, 9999, 0]
    num = 0
    for item in Items:
        itemR = pygame.Rect(item[1], item[2], 12, 12)
        if item_checkR.colliderect(itemR):
            if abs(Player.x - item[1]) < closest[1]:
                closest = [item, abs(Player.x - item[1]), num]
        if item[0] in AnimationData:
            if len(item) == 3:
                item.append(0)
                item.append(0)
            item[3] += 1
            if item[3] >= AnimationData[item[0]][0][1]:
                item[3] = 0
                item[4] += 1
            if item[4] >= AnimationData[item[0]][0][0]:
                item[4] = 0
            DisplaySurf.blit(Animations[AnimationData[item[0]][0][2]][item[4]],
                             (item[1] + ScrollX, item[2] + ScrollY + 1))
        else:
            DisplaySurf.blit(Item_Images[item[0]], (item[1] + ScrollX, item[2] + ScrollY + 1))
        if item[0] == 'butterfly':
            if len(item) == 5:
                item.append(item[1])
                item.append(item[2])
            if item[4] == 4:
                if item[3] == 0:
                    item[1] += random.randint(1, 3) - 2
                    item[2] += random.randint(1, 3) - 2
            if item[1] > item[5] + 12:
                item[1] = item[5] + 12
            elif item[1] < item[5] - 12:
                item[1] = item[5] - 12
            if item[2] > item[6] + 12:
                item[2] = item[6] + 12
            elif item[2] < item[6] - 12:
                item[2] = item[6] - 12
        if item[0] == 'guts':
            guts_obj = PhysicsObject(item[1], item[2], 12, 9)
            guts_obj.Move([0, 4], Collisions)
            item[1] = guts_obj.rect.x
            item[2] = guts_obj.rect.y
        num += 1
    if closest[0] != None:
        item = closest[0]
        DisplayedObjects.add([Item_Images[item[0]], item[1] + ScrollX + 9, item[2] + ScrollY - 3], 0)
        DisplayedObjects.add([item_bar, item[1] + 6 + ScrollX, item[2] + ScrollY + 6], 0)
        if z_use == False:
            DisplayedObjects.add([z_buttons[button_frame], Player.x - 2 + ScrollX, Player.y - 11 + ScrollY], 0)
        if Craft == True:
            if Held_Item == '':
                Held_Item = item[0]
                Items.remove(Items[closest[2]])
                SFX['Take_0'].play()
            else:
                result = Combine(Held_Item, item[0])
                if result != '':
                    if len(Held_Potions) < 4:
                        Items.remove(Items[closest[2]])
                        Held_Item = ''
                        Held_Potions[result] = Potions[result][1]
                        SFX['Pop_0'].play()
                    elif result in Held_Potions:
                        Items.remove(Items[closest[2]])
                        Held_Item = ''
                        Held_Potions[result] = Potions[result][1]
                        SFX['Pop_0'].play()
    # enemies
    for NPC in NPCs:
        if NPC.health <= 0:
            Player.health += 1
            Items.append(['guts', NPC.x, NPC.y])
            NPCs.remove(NPC)
        speed = 1
        if NPC.status == 'slowness':
            speed = 0.5
        elif NPC.status == 'weakness':
            NPC.health -= 1
            NPC.status = None
        elif NPC.status == 'paralysis':
            speed = 0
        elif NPC.status == 'knockback':
            NPC.x_momentum *= 3
            NPC.x_momentum = -NPC.x_momentum
            NPC.status = None
            Player.health += 1
            if Player.health > entity_stats['player'][0]:
                Player.health = entity_stats['player'][0]
        if NPC.obj.rect.colliderect(DisplayR):
            NPC.AI(Player, Collisions, speed)
        if NPC.obj.rect.colliderect(Player.obj.rect):
            if invincible == 0:
                invincible = 40
                Player.health -= 1
                SFX['Hit_0'].play()
                if Player.health < 0:
                    Player.health = 0
        NPC.display()
    # player
    PlayerMovement = [0, 1]
    if Moving_Right == True:
        if last_dir == 'l':
            FX.append(['turn2', Player.x, Player.y - 4, 0, 0])
        PlayerMovement[0] += 2
        last_dir = 'r'
    if Moving_Left == True:
        if last_dir == 'r':
            FX.append(['turn', Player.x - 8, Player.y - 4, 0, 0])
        PlayerMovement[0] -= 2
        last_dir = 'l'
    player_collisions = Player.move(PlayerMovement, Collisions)
    if player_collisions[0] == True:
        Jumps = JUMP_MAX
    if invincible == 0:
        Player.display()
    elif random.randint(1, 2) == 1:
        Player.display()
    item_checkR = pygame.Rect(Player.x - 12, Player.y, 27, 8)
    for end_tile in end:
        end_tileR = pygame.Rect(end_tile[0], end_tile[1], 12, 12)
        if Player.obj.rect.colliderect(end_tileR):
            Level += 1
            Trees = gen_trees()
            Layers, Map = load_map('Level_' + str(Level))
            Map, NPCs, Items, spawn, end = load_entities(Map, entity_IDs)
            health = Player.health
            Player = Entity('player', spawn[0], spawn[1], 4, 7)
            Player.health = health
            ScrollX = -(-DisplaySurf.get_width() / 2 + spawn[0])
            ScrollY = -(-DisplaySurf.get_height() / 2 + spawn[1])
            Arrows = []
            fade = 2
    if invincible > 0:
        invincible -= 1
    if Player.health <= 0:
        Layers, Map = load_map('Level_' + str(Level))
        Map, NPCs, Items, spawn, end = load_entities(Map, entity_IDs)
        Player = Entity('player', spawn[0], spawn[1], 4, 7)
        Player.health -= 2
        ScrollX = -(-DisplaySurf.get_width() / 2 + spawn[0])
        ScrollY = -(-DisplaySurf.get_height() / 2 + spawn[1])
        Arrows = []
        Held_Potions = {}
        Held_Item = ''
        invincible = 70
        fade = 3
    elif Player.health > 5:
        Player.health = 5
    # FX
    for animation in FX:
        DisplaySurf.blit(Animations[animation[0]][animation[4]], (animation[1] + ScrollX, animation[2] + ScrollY))
        animation[3] += 1
        if animation[3] >= AnimationData[animation[0]][0][1]:
            animation[3] = 0
            animation[4] += 1
        if animation[4] >= AnimationData[animation[0]][0][0]:
            try:
                FX.remove(animation)
            except:
                pass
    # arrows
    for Arrow in Arrows:
        img = ArrowImg.copy()
        arrow_movement = [0, 0]
        if Arrow[2] == 'l':
            img = pygame.transform.flip(img, True, False)
            arrow_movement[0] -= 6
            arrow_obj = PhysicsObject(Arrow[0] + 2, Arrow[1], 6, 3)
        elif Arrow[2] == 'r':
            arrow_movement[0] += 6
            arrow_obj = PhysicsObject(Arrow[0], Arrow[1], 6, 3)
        collisions = arrow_obj.Move(arrow_movement, Collisions)
        Arrow[0] = arrow_obj.rect.x
        if Arrow[2] == 'l':
            Arrow[0] -= 2
        Arrow[1] = arrow_obj.rect.y
        if (collisions[2] == False) and (collisions[3] == False):
            for NPC in NPCs:
                if NPC.obj.rect.colliderect(arrow_obj.rect):
                    NPC.health -= 1
                    NPC.status = Arrow[3]
                    SFX['Squish_0'].play()
                    if Player.health > entity_stats['player'][0]:
                        Player.health = entity_stats['player'][0]
                    try:
                        Arrows.remove(Arrow)
                    except:
                        pass
                    AddParticles(Particles, NPC.x + entity_sizes[NPC.type][0] / 2,
                                 NPC.y + entity_sizes[NPC.type][1] / 2, [NPCparticles[NPC.type]], (0.5, 1), (7, 9), 75,
                                 'fall', 0.15)
        DisplaySurf.blit(img, (Arrow[0] + ScrollX, Arrow[1] + ScrollY))
        if Arrow[3] != None:
            if random.randint(1, 2) == 1:
                if Arrow[2] == 'r':
                    if collisions[2] == False:
                        Particles.append(
                            [Arrow[0] + 7, Arrow[1] + 1, 0.5, -0.5, Potions[Arrow[3]][0], 1, 0, 20, 'normal', 1])
                if Arrow[2] == 'l':
                    if collisions[3] == False:
                        Particles.append(
                            [Arrow[0], Arrow[1] + 1, -0.5, -0.5, Potions[Arrow[3]][0], 1, 0, 20, 'normal', 1])
        try:
            if abs(Arrow[0] - (-ScrollY + DisplaySurf.get_width() / 2)) > 1000:
                Arrows.remove(Arrow)
        except:
            pass
    # particles
    for Particle in Particles:
        Particle[0] += Particle[2]
        Particle[1] += Particle[3]
        if Particle[8] == 'fall':
            Particle[3] += abs(Particle[3] / 10) + Particle[9]
            Particle[1] -= Particle[3] / 10
        ParticleSurf = pygame.Surface((1, 1))
        ParticleSurf.fill(Particle[4])
        Particle[6] += 1
        if Particle[6] >= Particle[7]:
            Particles.remove(Particle)
        DisplaySurf.blit(ParticleSurf, (Particle[0] + ScrollX, Particle[1] + ScrollY))
    # handle animations
    for Animation in CurrentAnimations:
        if Animation.type == 'bow':
            y_change = 0
            if (Player.animation == 2) or (Player.animation == 3):
                if Player.animation_frame == 1:
                    y_change = -1
            if Animation.animation == 0:
                Animation.change('location', (Player.x, Player.y - 2 + y_change))
                if CDown == False:
                    CurrentAnimations.remove(Animation)
                    if Animation.animation_frame == 2:
                        ID = Get_Potion(Held_Potions, Selected_Potion)
                        if ID != None:
                            Held_Potions[ID] -= 1
                            if Held_Potions[ID] <= 0:
                                del Held_Potions[ID]
                        Arrows.append([Player.x, Player.y + 2, 'r', ID])
                        SFX['Pew_0'].play()
                        c_use = True
                elif last_dir == 'l':
                    Animation.change('animation', 1)
            if Animation.animation == 1:
                Animation.change('location', (Player.x - 6, Player.y - 2 + y_change))
                if CDown == False:
                    CurrentAnimations.remove(Animation)
                    if Animation.animation_frame == 2:
                        ID = Get_Potion(Held_Potions, Selected_Potion)
                        if ID != None:
                            Held_Potions[ID] -= 1
                            if Held_Potions[ID] <= 0:
                                del Held_Potions[ID]
                        Arrows.append([Player.x - 6, Player.y + 2, 'l', ID])
                        SFX['Pew_0'].play()
                        c_use = True
                elif last_dir == 'r':
                    Animation.change('animation', 0)
        done = Animation.display()
        if done == True:
            CurrentAnimations.remove(Animation)
    # update display
    DisplayedObjects.display(DisplaySurf)
    # HUD
    if (x_use == False) or (c_use == False):
        DisplaySurf.blit(x_buttons[button_frame], (Player.x - 17 + ScrollX, Player.y - 11 + ScrollY))
    for i in range(Player.health):
        DisplaySurf.blit(heart, (2 + i * 8, 2))
    if Held_Item != '':
        DisplaySurf.blit(Item_Images[Held_Item], (DisplaySurf.get_width() - 10, DisplaySurf.get_height() - 11))
        held_item_bar = pygame.Surface((8, 1))
        held_item_bar.fill((225, 228, 237))
        DisplaySurf.blit(held_item_bar, (DisplaySurf.get_width() - 10, DisplaySurf.get_height() - 2))
    num = 0
    if Selected_Potion > len(Held_Potions) - 1:
        Selected_Potion = len(Held_Potions) - 1
    if Selected_Potion < 0:
        Selected_Potion = 0
    for Potion in Held_Potions:
        DisplaySurf.blit(PotionImage(Potion, Held_Potions[Potion]), (2 + num * 10, DisplaySurf.get_height() - 12))
        if num == Selected_Potion:
            DisplaySurf.blit(selector, (2 + num * 10, DisplaySurf.get_height() - 12))
        num += 1
    xs = num * 10 - 2
    if xs < 0:
        xs = 0
    potion_bar = pygame.Surface((xs, 1))
    potion_bar.fill((225, 228, 237))
    DisplaySurf.blit(potion_bar, (2, DisplaySurf.get_height() - 2))
    # FPS ---------------------------------------------------- #
    NewSec = False
    TrueFPSCount += 1
    now = datetime.now()
    now = now.second
    if PrevNow != now:
        PrevNow = now
        NewSec = True
        TrueFPS = TrueFPSCount
        TrueFPSCount = 0
        TrueFPS = str(TrueFPS)
    # Buttons ------------------------------------------------ #
    Craft = False
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == ord('q'):
                if fpsOn == True:
                    fpsOn = False
                elif fpsOn == False:
                    fpsOn = True
            if event.key == ord('z'):
                Craft = True
            if event.key == ord('x'):
                if Jumps > 0:
                    Jumps -= 1
                    Player.gravity = -4
                    x_use = True
                    FX.append(['jump', Player.x - 4, Player.y - 4, 0, 0])
            if event.key == K_RIGHT:
                Moving_Right = True
            if event.key == K_LEFT:
                Moving_Left = True
            if event.key == K_UP:
                if Selected_Potion > 0:
                    Selected_Potion -= 1
            if event.key == K_DOWN:
                Selected_Potion += 1
            if event.key == ord('c'):
                CDown = True
                CurrentAnimations.append(AnimatedObject('bow', Player.x, Player.y - 2, 'pause'))
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                Moving_Right = False
            if event.key == K_LEFT:
                Moving_Left = False
            if event.key == ord('c'):
                CDown = False
            if event.key == K_F11:
                if fullscreen == False:
                    fullscreen = True
                    screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.FULLSCREEN)
                else:
                    fullscreen = False
                    screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
    # Update ------------------------------------------------- #
    if Level == 6:
        DisplaySurf.blit(twitter, (2, 14))
        Text.ShowText('DaFluffyPotato ', 16, 16, 1, 1000, Font_0, DisplaySurf)
    screen.blit(pygame.transform.scale(DisplaySurf, (720, 480)), (0, 0))
    if fade == 2:
        timer = 40
        while timer > 0:
            screenshot = pygame.transform.scale(DisplaySurf, (720, 480))
            timer -= 1
            black = pygame.Surface((720, 480))
            black.set_alpha(255 - 255 / 40 * timer)
            screenshot.blit(black, (0, 0))
            screen.blit(screenshot, (0, 0))
            pygame.display.update()
            mainClock.tick(40)
    elif fade == 1:
        timer = 40
        while timer > 0:
            screenshot = pygame.transform.scale(DisplaySurf, (720, 480))
            timer -= 1
            black = pygame.Surface((720, 480))
            black.set_alpha(255 / 40 * timer)
            screenshot.blit(black, (0, 0))
            screen.blit(screenshot, (0, 0))
            pygame.display.update()
            mainClock.tick(40)
    elif fade == 3:
        fade = 2
        screen.fill((0, 0, 0))
    if fade > 0:
        fade -= 1
    for Chars in TextQueue:
        Text.ShowText(Chars[0], int(Chars[1]) * 3, int(Chars[2]) * 3, 1, 1000, Font_0, screen)
    TextQueue = []
    if fpsOn == True:
        Text.ShowText('FPS:' + (TrueFPS) + ' ', 12, 12, 1, 1000, Font_0, screen)
    pygame.display.update()
    mainClock.tick(40)
