import os, sys, random, cProfile, math, random
import pygame
from pygame.locals import *

from model import grid, path, part, gamestate, task, device

cellsize = 16
mapw = 50
maph = 25

pxfromcx = lambda cx: cx * cellsize
pyfromcy = lambda cy: (maph - cy - 1) * cellsize
pfromc = lambda (cx,cy): (pxfromcx(cx), pyfromcy(cy))
mpfromc = lambda (cx, cy): (pxfromcx(cx) + 8, pyfromcy(cy) + 8)

cxfrompx = lambda px: px / cellsize
cyfrompy = lambda py: maph - (py / cellsize) - 1
cfromp = lambda (px,py): (cxfrompx(px), cyfrompy(py))

c_belt                  = (255, 255,   0)
c_cog_static            = (150,   0,  50)
c_cog_clockwise         = (150, 100,   0)
c_cog_counterclockwise  = (150,   0, 100)
c_cursor                = (255, 255, 255)
c_cursorline            = (  0, 100,   0)
c_device                = (100,  50,   0)
c_elf_body              = (255, 255,   0)
c_elf_head              = (255, 200, 200)
c_ladder                = ( 50, 200,  50)
c_path_broken_start     = (255,   0,   0)
c_path_broken_end       = (255, 255,   0)
c_path_connected_start  = (  0, 255,   0)
c_path_connected_end    = (  0, 255, 255)
c_path                  = (  0,   0, 255)
c_platform              = (200,  50,  50)
c_spring                = ( 20,  40, 100)
c_task                  = (100, 100, 100)
c_wheel                 = (  0, 150, 150)

c_zones = [(50,0,0), (0,0,50), (0,50,0), (50,50,0), (0,50,50), (50,0,50),
           (25,75,0),(0,25,75),(75,0,25),(75,25,0), (0,75,25), (25,0,75)]

pygame.init()
screen = pygame.display.set_mode((mapw*cellsize, maph*cellsize), HWSURFACE)
pygame.display.set_caption('Grid test')

clock = pygame.time.Clock()

gs = gamestate.Gamestate(mapw, maph)

#gs.pgrid.lock()
#for n in xrange(30):
#    length = random.randint(3,20)
#    y = random.randint(0,maph-1)
#    x = random.randint(0,mapw-length)
#    gs.pgrid.add_platform((x,y),length)
#for n in xrange(30):
#    length = random.randint(3,13)
#    x = random.randint(0,mapw-1)
#    y = random.randint(0,maph-length)
#    gs.pgrid.add_ladder((x,y),length)
#gs.pgrid.unlock()

gs.add_spring((5, 1))

gs.pgrid.lock()
gs.pgrid.add_platform((5,0),8)
gs.pgrid.add_ladder((7,0),1)

gs.add_elf((8,1))
gs.add_elf((9,1))

gs.add_device(device.GumballMachine((20, 3)))
gs.add_device(device.GumballMachine((25, 3)))
gs.pgrid.add_platform((16,2),10)
gs.pgrid.add_ladder((22,0),3)

gs.add_device(device.RubberFactory((29, 0)))
gs.add_device(device.MetalFactory((33, 1)))
gs.pgrid.add_platform((32, 0), 6)
gs.pgrid.add_ladder((33,0), 1)
gs.pgrid.unlock()

def randompts(grid):
    startpos, endpos = (-8,-8), (-8,-8)
    while gs.pgrid[startpos[0],startpos[1]-1][0] == False:
        startpos = (random.randint(0,mapw-1), random.randint(0,maph-1))
    while gs.pgrid[endpos[0],endpos[1]-1][0] == False or startpos == endpos:
        endpos = (random.randint(0,mapw-1), random.randint(0,maph-1))
    return startpos, endpos

def draw_spring(screen, spring):
    corner = (spring.pos[0]-1, spring.pos[1]+1)
    pygame.draw.rect(screen, c_spring, Rect(pfromc(corner), (3*cellsize, 3*cellsize)), 0)
    draw_cog(screen, spring.pos, 1.5, spring.angle, None)

def draw_device(screen, device):
    cx, cy = device.pos
    for xo, yo in device.region:
        px = pxfromcx(cx + xo)
        py = pyfromcy(cy + yo)
        pygame.draw.rect(screen, c_device, Rect(px, py, cellsize, cellsize))
    draw_cog(screen, device.pos, 1.5, device.angle, None)        

def draw_platform(screen, pos, colour):
    cx, cy = pos
    px = cx * 16
    py = (maph - cy - 1) * 16
    pygame.draw.rect(screen, colour, Rect(px, py, 16, 4))
    
def draw_ladder(screen, pos, colour):
    cx, cy = pos
    px = cx * 16
    py = (maph - cy - 1) * 16
    pygame.draw.line(screen, colour, (px+6,py), (px+6,py+15))
    pygame.draw.line(screen, colour, (px+9,py), (px+9,py+15))
    pygame.draw.line(screen, colour, (px+6,py+2), (px+9,py+2))
    pygame.draw.line(screen, colour, (px+6,py+6), (px+9,py+6))
    pygame.draw.line(screen, colour, (px+6,py+10), (px+9,py+10))
    pygame.draw.line(screen, colour, (px+6,py+14), (px+9,py+14))

def draw_belt(screen, pixpos1, pixpos2):
    px1, py1 = pixpos1
    px2, py2 = pixpos2
    px1, px2, py1, py2 = px1 + 8, px2 + 8, py1 + 8, py2 + 8
    pygame.draw.line(screen, c_belt, (px1,py1), (px2,py2), 2)

def draw_cog(screen, pos, diam, angle, direction):
    px, py = pfromc(pos)
    px += 8
    py += 8
    prad = diam * 8
    px2 = px + prad * math.cos(angle*math.pi/180)
    py2 = py + prad * math.sin(angle*math.pi/180)
    colour = c_wheel
    if direction is not None:
        colour = c_cog_static
        if direction > 0:
            colour = c_cog_clockwise
        if direction < 0:
            colour = c_cog_counterclockwise
    pygame.draw.circle(screen, colour, (px, py), prad, 3)
    pygame.draw.line(screen, colour, (px,py), (px2,py2), 2)

def get_elf_pixelpos(e):
    px, py = pfromc(e.path[0])
    if e.is_falling:
        py += cellsize * e.offset
    else:
        try:
            pxnext, pynext = pfromc(e.path[1])
            px += (pxnext - px) * e.offset
            py += (pynext - py) * e.offset
        except:
            pass
    return px, py

def draw_elf(screen, e):
    px, py = get_elf_pixelpos(e)
    if e.is_falling:
        pygame.draw.circle(screen, c_elf_body, (px+8, py+8), 4)
        pygame.draw.circle(screen, c_elf_head, (px+8, py+14), 2)
    else:
        pygame.draw.circle(screen, c_elf_body, (px+8, py+12), 4)
        pygame.draw.circle(screen, c_elf_head, (px+8, py+6), 2)

def render(screen, gs):
    screen.fill((0,0,0))
    if showzones:
        renderzones(screen, gs.pgrid)
    draw_spring(screen, gs.spring)
    for d in gs.devices:
        draw_device(screen, d)
    for c in gs.cogs:
        draw_cog(screen, c.pos, c.diam, c.angle, c.g_ratio)
    for b in gs.belts:
        draw_belt(screen, pfromc(b.part1.pos), pfromc(b.part2.pos))
    # do this here to get the layers right
    for e1, e2 in [(t.elf1, t.elf2) for t in gs.tasks if isinstance(t, task.ConnectTask) and t.phase == 2]:
        draw_belt(screen, get_elf_pixelpos(e1), get_elf_pixelpos(e2))
    for pos, cell in gs.pgrid:
        plt, ldr = cell
        if plt: draw_platform(screen, pos, c_platform)
        if ldr: draw_ladder(screen, pos, c_ladder)
    for e in gs.elves:
        draw_elf(screen, e)
    for t in gs.tasks:
        rendertask(screen, t)

def renderzones(screen, grid):
    for x in xrange(grid.w):
        for y in xrange(grid.h):
            pos = x, y
            colour = grid.colours[pos]
            if colour is not None:
                pygame.draw.rect(screen, c_zones[colour % len(c_zones)], Rect(pfromc(pos), (16,16)))

def renderpath(screen, pstart, pend, path):
    pxs, pys = pstart[0]*16, (maph-pstart[1]-1)*16
    pxe, pye = pend[0]*16, (maph-pend[1]-1)*16
    if path is None:
        pygame.draw.rect(screen, c_path_broken_start, Rect(pxs+2, pys+2, 12, 12), 1)
        pygame.draw.rect(screen, c_path_broken_end, Rect(pxe+2, pye+2, 12, 12), 1)
    else:
        pygame.draw.rect(screen, c_path_connected_start, Rect(pxs+2, pys+2, 12, 12), 1)
        pygame.draw.rect(screen, c_path_connected_end, Rect(pxe+2, pye+2, 12, 12), 1)
        pixelpath = map(lambda (x, y): (x*16+7, (maph-y-1)*16+7), path)
        pygame.draw.lines(screen, c_path, False, pixelpath, 2)

def rendercursor(screen, cursor):
    pygame.draw.rect(screen, c_cursor, Rect(pfromc(cursor), (16,16)), 1)
    if currentbelt is not None:
        pygame.draw.line(screen, c_cursorline, mpfromc(cursor), mpfromc(currentbelt.pos))
    if currentconnect is not None:
        pygame.draw.line(screen, c_cursorline, mpfromc(cursor), mpfromc(currentconnect.pos))

def rendertask(screen, t):
    if isinstance(t, task.GoTask):
        px, py = pfromc(t.pos)
        pygame.draw.lines(screen, c_task, True, [(px+2,py+2),(px+12,py+2),(px+7,py+12)])
    if isinstance(t, task.CreateCogTask):
        px, py = pfromc(t.pos)
        prad = t.diam * 8 - 3
        pygame.draw.circle(screen, c_task, (px+8,py+8), prad, 1)
    if isinstance(t, task.ConnectTask):
        px1, py1 = mpfromc(t.part1.pos)
        px2, py2 = mpfromc(t.part2.pos)
        pygame.draw.line(screen, c_task, (px1,py1), (px2,py2))
    if isinstance(t, task.BuildPlatformTask):
        draw_platform(screen, t.pos, c_task)
    if isinstance(t, task.BuildLadderTask):
        draw_ladder(screen, t.pos, c_task)

cursor = (0, 0)

def update_cursor():
    return cfromp(pygame.mouse.get_pos())

def do_belt_click(gs, pos, currentbelt):
    clicked_cog = gs.mgrid[pos]
    if clicked_cog is not None:
        if currentbelt == None:
            return clicked_cog
        else:
            if clicked_cog != currentbelt:
                create_belt(gs, clicked_cog, currentbelt)
            return None

def do_connect_click(gs, pos, currentconnect):
    clicked_part = gs.mgrid[pos]
    if clicked_part is not None:
        if currentconnect == None:
            return clicked_part
        else:
            if clicked_part != currentconnect:
                gs.add_task(task.ConnectTask(gs, clicked_part, currentconnect))
            return None

def create_belt(gs, part1, part2):
    gs.add_belt(part1, part2)
    gs.recalculate_ratios()

def create_small_cog(gs, pos):
    try:
        gs.add_cog(pos, 1)
    except:
        return
    gs.recalculate_ratios()

def create_cog(gs, pos, size):
    try:
        gs.add_cog(pos, size)
    except:
        return
    gs.recalculate_ratios()

def map_add_platform(gs, pos):
    gs.pgrid[pos] = (True, gs.pgrid[pos][1])
    gs.recalculate_paths()
def map_add_ladder(gs, pos):
    gs.pgrid[pos] = (gs.pgrid[pos][0], True)
    gs.recalculate_paths()
def map_erase(gs,pos):
    del gs.pgrid[pos]
    gs.recalculate_paths()

def report_cell(gs, cursor):
    p_item = gs.pgrid[cursor]
    m_item = gs.mgrid[cursor]
    print "Cell: (%i, %i)" % cursor
    print "  platform = %s" % str(p_item[0])
    print "  ladder = %s" % str(p_item[1])
    if m_item is not None:
        print "  part = %r" % m_item
        if isinstance(m_item, part.Part):
            print "  angle = %f" % m_item.angle
            print "  g_ratio = %f" % m_item.g_ratio
            print "  get_angular_speed() = %f" % m_item.get_angular_speed(gs)
        if isinstance(m_item, part.Spring) or isinstance(m_item, device.Device):
            print "  energy = %f" % m_item.energy
            print "  global load factor = %f" % gs.load_factor

def dump_elf_info(gs):
    print "elf tasklist: --"
    for e in gs.elves:
        print e.task

quit = False
timer = 0

pstart, pend = randompts(gs.pgrid)
currentpath = None
currentbelt = None
currentconnect = None

showzones = False
showtests = False

gs.recalculate_ratios()

update_cursor()

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
            elif evt.key == K_KP1:
                gs.add_task(task.CreateCogTask(gs, cursor, 1))
            elif evt.key == K_KP2:
                gs.add_task(task.CreateCogTask(gs, cursor, 3))
            elif evt.key == K_KP3:
                gs.add_task(task.CreateCogTask(gs, cursor, 5))
            elif evt.key == K_KP4:
                gs.add_task(task.CreateCogTask(gs, cursor, 7))
            elif evt.key == K_b:
                currentbelt = do_belt_click(gs, cursor, currentbelt)
            elif evt.key == K_c:
                currentconnect = do_connect_click(gs, cursor, currentconnect)
            elif evt.key == K_d:
                map_erase(gs, cursor)
            elif evt.key == K_e:
                gs.add_elf(cursor)
            elif evt.key == K_k:
                gs.add_task(task.BuildLadderTask(gs, cursor))
            elif evt.key == K_l:
                map_add_ladder(gs, cursor)
            elif evt.key == K_o:
                gs.add_task(task.BuildPlatformTask(gs, cursor))
            elif evt.key == K_p:
                map_add_platform(gs, cursor)
            elif evt.key == K_q:
                showtests = not showtests
            elif evt.key == K_r:
                report_cell(gs, cursor)
            elif evt.key == K_t:
                gs.add_task(task.GoTask(gs, cursor))
            elif evt.key == K_w:
                if gs.mgrid[cursor] == gs.spring:
                    gs.add_task(task.EnterSpringTask(gs))
                else:
                    gs.release_winding_elf()
            elif evt.key == K_x:
                dump_elf_info(gs)
            elif evt.key == K_z:
                showzones = not showzones

    gs.tick()

    render(screen, gs)
    if showtests:
        renderpath(screen, pstart, pend, currentpath)
    rendercursor(screen, cursor)
    pygame.display.flip()
    clock.tick(50)

    timer += 1
    if (timer % 100 == 98):
        pstart, pend = randompts(gs.pgrid)
        currentpath = None
    if (timer % 100 == 99):
        currentpath = path.find_best_path(gs.pgrid, pstart, pend)

pygame.quit()
