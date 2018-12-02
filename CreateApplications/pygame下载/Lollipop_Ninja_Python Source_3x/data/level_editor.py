#!/usr/bin/python3.4
# Setup Python ----------------------------------------------- #
import pygame, sys, random, time, os
# Setup pygame/window ---------------------------------------- #
mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.mixer.quit()
pygame.display.set_caption('level editor')
WINDOWWIDTH = 300*2
WINDOWHEIGHT = 200*2
screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT),0,32)
Display = pygame.Surface((300,200))
# Font ------------------------------------------------------- #
basicFont = pygame.font.SysFont(None, 20)
# Images ----------------------------------------------------- #
tile_list = os.listdir('images/tiles')
tile_database = {}
for tile in tile_list:
    if tile != 'Thumbs.db':
        img = pygame.image.load('Images/Tiles/' + tile).convert()
        img.set_colorkey((255,255,255))
        tile_database[tile] = img.copy()
tile_map = {}
# Audio ------------------------------------------------------ #
# Colors ----------------------------------------------------- #
SKY = (174,228,240)
# Variables -------------------------------------------------- #
Clicking = False
Removing = False
current_tile = None
Click = False
scroll_x = 0
scroll_y = 0
up = False
down = False
right = False
left = False
export = False
tile_scroll = 0
# Functions -------------------------------------------------- #
def Text2List(Text,Divider,intmode=False):
    List = []
    Current = ''
    for char in Text:
        if char != Divider:
            Current += char
        else:
            if intmode == True:
                try:
                    List.append(int(Current))
                except:
                    List.append(Current)
            else:
                List.append(Current)
            Current = ''
    return List

def load_map():
    file = open('in.txt','r')
    map_data = file.read()
    file.close()
    tiles = Text2List(map_data,'=')
    n = 0
    for tile in tiles:
        tiles[n] = Text2List(tile,';',True)
        n += 1
    for tile in tiles:
        tile[0] = Text2List(tile[0],'+')
    tile_map = {}
    for tile in tiles:
        tile_map[str(tile[1]) + ';' + str(tile[2])] = tile
    return tile_map
# Loop ------------------------------------------------------- #
while True:
    # Background --------------------------------------------- #
    Display.fill(SKY)
    if right == True:
        scroll_x += 4
    if left == True:
        scroll_x -= 4
    if up == True:
        scroll_y -= 4
    if down == True:
        scroll_y += 4
    # Tiles -------------------------------------------------- #
    for tile in tile_map:
        for img in tile_map[tile][0]:
            if img[:5] != 'grass':
                Display.blit(tile_database[img],(tile_map[tile][1]*32-scroll_x,tile_map[tile][2]*32-scroll_y))
            else:
                Display.blit(tile_database[img],(tile_map[tile][1]*32-scroll_x,tile_map[tile][2]*32-5-scroll_y))
    # GUI ---------------------------------------------------- #
    x = 0
    y = 0
    for img in tile_list:
        if img != 'Thumbs.db':
            Display.blit(pygame.transform.scale(tile_database[img],(16,16)),(x*17,y*17-tile_scroll*17))
            TileR = pygame.Rect(x*17,y*17-tile_scroll*17,16,16)
            if Click == True:
                if MouseR.colliderect(TileR):
                    current_tile = img
                    Clicking = False
            x += 1
            if x > 2:
                x = 0
                y += 1
    # Mouse -------------------------------------------------- #
    MX,MY = pygame.mouse.get_pos()
    MX = int(MX/2)
    MY = int(MY/2)
    MouseR = pygame.Rect(MX,MY,2,2)
    MX = int(round((scroll_x+MX-10)/32,0))
    MY = int(round((scroll_y+MY-10)/32,0))
    if current_tile != None:
        if current_tile[:5] != 'grass':
            Display.blit(tile_database[current_tile],(MX*32-scroll_x,MY*32-scroll_y))
        else:
            Display.blit(tile_database[current_tile],(MX*32-scroll_x,MY*32-5-scroll_y))
        if Clicking == True:
            loc = str(MX) + ';' + str(MY)
            if loc not in tile_map:
                tile_map[loc] = [[current_tile],MX,MY]
            elif current_tile not in tile_map[loc][0]:
                tile_map[loc][0].append(current_tile)
        if Removing == True:
            loc = str(MX) + ';' + str(MY)
            if loc in tile_map:
                del tile_map[loc]
    # Buttons ------------------------------------------------ #
    Click = False
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == ord('a'):
                left = True
            if event.key == ord('d'):
                right = True
            if event.key == ord('w'):
                up = True
            if event.key == ord('s'):
                down = True
            if event.key == ord('e'):
                export = True
            if event.key == ord('i'):
                tile_map = load_map()
        if event.type == KEYUP:
            if event.key == ord('a'):
                left = False
            if event.key == ord('d'):
                right = False
            if event.key == ord('w'):
                up = False
            if event.key == ord('s'):
                down = False
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                Clicking = True
                Click = True
            if event.button == 3:
                Removing = True
            if event.button == 4:
                tile_scroll -= 1
            if event.button == 5:
                tile_scroll += 1
        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                Clicking = False
            if event.button == 3:
                Removing = False
    # Export ------------------------------------------------- #
    if export == True:
        export = False
        export_str = ''
        for tile in tile_map:
            for img in tile_map[tile][0]:
                export_str += img + '+'
            export_str += ';' + str(tile_map[tile][1]) + ';' + str(tile_map[tile][2]) + ';='
        file = open('export.txt','w')
        file.write(export_str)
        file.close()
    # Update ------------------------------------------------- #
    screen.blit(pygame.transform.scale(Display,(300*2,200*2)),(0,0))
    pygame.display.update()
    mainClock.tick(40)
    
