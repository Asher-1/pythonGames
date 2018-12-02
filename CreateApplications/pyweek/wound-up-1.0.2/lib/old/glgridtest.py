import os, sys, random, cProfile, math, random
import pygame
import gl, interface
import cProfile
from pygame.locals import *

from model import grid, path, part, gamestate

cellsize = 16
mapw = 50
maph = 25

pygame.init()

pygame.display.set_mode((640, 480), OPENGL | DOUBLEBUF)
pygame.display.set_caption('Grid test')
gl.init(640, 480)

clock = pygame.time.Clock()

gs = gamestate.Gamestate(mapw, maph)

for n in xrange(30):
    len = random.randint(3,20)
    y = random.randint(0,maph-1)
    x = random.randint(0,mapw-len)
    gs.pgrid.add_platform((x,y),len)
for n in xrange(30):
    len = random.randint(3,13)
    x = random.randint(0,mapw-1)
    y = random.randint(0,maph-len)
    gs.pgrid.add_ladder((x,y),len)

gs.add_cog((12,12), 3)

gs.add_spring((2,2))
somecog = gs.cogs.__iter__().next()

gs.add_belt(gs.spring, somecog)
gs.set_speeds(5)
cb = interface.CogBag()
pb = interface.PlatBag()
lb = interface.LadderBag()
eb = interface.ElfBag()
bb = interface.BeltBag()
spr = interface.Spring(gs)

cam = gl.Camera((15, 15), 20)
cam.setCurrent()
lights = []
lights.append(gl.Light((10, 10, 5)))
lights.append(gl.Light((12, 18, 5)))
def randompts(grid):
    startpos, endpos = (-8,-8), (-8,-8)
    while gs.pgrid[startpos[0],startpos[1]-1][0] == False:
        startpos = (random.randint(0,mapw-1), random.randint(0,maph-1))
    while gs.pgrid[endpos[0],endpos[1]-1][0] == False or startpos == endpos:
        endpos = (random.randint(0,mapw-1), random.randint(0,maph-1))
    return startpos, endpos
cursor = (0, 0)
curobj = gl.Object()
curobj.axis = (0,1,0)
def update_cursor():
    pos = cam.getIntPos(pygame.mouse.get_pos())
    curobj.setPosition(pos)
    return pos

def create_small_cog(gs, pos):
    try:
        gs.add_cog(pos, 1)
        gs.set_speeds(1)
    except:
        pass

def create_cog(gs, pos, size):
    try:
        gs.add_cog(pos, size)
        gs.set_speeds(1)
    except:
        pass

def create_elf(gs, pos):
    gs.add_elf(pos)

def send_random_elf_to_point(gs, pos):
    luckyelf = random.choice(list(gs.elves))
    if not luckyelf.is_falling:
        luckyelf.send_to(gs, pos)

def map_add_platform(gs, pos):
    gs.pgrid[pos] = (True, gs.pgrid[pos][1])
    gs.recalculate_paths()
def map_add_ladder(gs, pos):
    gs.pgrid[pos] = (gs.pgrid[pos][0], True)
    gs.recalculate_paths()
def map_erase(gs,pos):
    del gs.pgrid[pos]
    gs.recalculate_paths()

quit = False
timer = 0

pstart, pend = randompts(gs.pgrid)
currentpath = None

gs.set_speeds(1)
print gs.pgrid.platform_dict()

update_cursor()
#cProfile.run('''
while not quit:
    e = pygame.event.get()
    for evt in e:
        if evt.type == QUIT:
            quit = True
        if evt.type == MOUSEMOTION:
            cursor = update_cursor()
        if evt.type == MOUSEBUTTONDOWN:
            create_small_cog(gs, cursor)
        if evt.type == KEYDOWN:
            if evt.key == K_ESCAPE:
                quit = True
            elif evt.key == K_1:
                create_cog(gs, cursor, 1)
            elif evt.key == K_2:
                create_cog(gs, cursor, 3)
            elif evt.key == K_3:
                create_cog(gs, cursor, 5)
            elif evt.key == K_4:
                create_cog(gs, cursor, 7)
            elif evt.key == K_d:
                map_erase(gs, cursor)
            elif evt.key == K_e:
                create_elf(gs, cursor)
            elif evt.key == K_g:
                send_random_elf_to_point(gs, cursor)
            elif evt.key == K_l:
                map_add_ladder(gs, cursor)
            elif evt.key == K_p:
                map_add_platform(gs, cursor)
            elif evt.key == K_UP:
                cam.move((0, .5))    
            elif evt.key == K_DOWN:
                cam.move((0, -.5))    
            elif evt.key == K_LEFT:
                cam.move((-.5, 0))    
            elif evt.key == K_RIGHT:
                cam.move((.5, 0))
            elif evt.key == K_EQUALS:
                cam.zoom(-1)
            elif evt.key == K_MINUS:
                cam.zoom(1)
            elif evt.key == K_f:
                gl.GLState.toggleLighting()

    gs.tick()
    cb.update(gs.cogs)
    pb.update(gs.pgrid.platform_dict())
    lb.update([x for x, y in gs.pgrid if y[1]])
    eb.update(gs.elves)
    bb.update(gs.belts)
    gl.clear()
    eb.render()
    cb.render()
    pb.render()
    lb.render()
    bb.render()
    spr.render()
    curobj.render()
    curobj.rotate(1)

    pygame.display.flip()

    clock.tick(50)

    timer += 1
    if (timer % 100 == 98):
        pstart, pend = randompts(gs.pgrid)
        currentpath = None
    if (timer % 100 == 99):
        currentpath = path.find_best_path(gs.pgrid, pstart, pend)

#''')
print "FPS:", clock.get_fps()
pygame.quit()
