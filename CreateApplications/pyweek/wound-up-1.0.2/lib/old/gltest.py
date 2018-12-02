import gl
import pygame
from pygame.locals import *
pygame.init()
pygame.display.set_mode((640, 480), OPENGL | DOUBLEBUF)

gl.init(640, 480)

o = gl.Object()
l = gl.Light((1, 1, 1), point=False)
l2 = gl.Light((-5, 5, 5))
l2.setColour((0, 0, 1))
b = False
cam = gl.Camera()
cam.setCurrent()

o2 = None

while 1:
    event = pygame.event.poll()
    if event.type == KEYDOWN:
        if event.key == K_DOWN:
            cam.move((0, -.1))
        if event.key == K_UP:
            cam.move((0, .1))
        if event.key == K_SPACE and not b:
            o = gl.ModelObject("bucket.obj")
            o.axis = (0, 1, 0)
            o2 = gl.Object()
            o2.position = (0, 2, 0) 
            b = True
    if event.type == QUIT:
        break

    gl.clear()
    o.render()
    if o2:
        o2.render()

    o.rotate(.1)
    pygame.display.flip()
