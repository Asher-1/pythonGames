#!/usr/bin/python

# Panda Engine imports
from panda3d.core import CardMaker, NodePath

#----------------------------------------------------------------------#

def createSprite(_filename, _x, _z, _transparent=1):   
    tex = loader.loadTexture(_filename)   
    cm = CardMaker('spritesMaker')
    sprite = NodePath(cm.generate())   
    sprite.setTexture(tex)
   
    #Scale and position
    sx = float(tex.getXSize()) / base.win.getXSize()
    sz = float(tex.getYSize()) / base.win.getYSize()
    sprite.setScale(sx, 1.0, sz)
    #sprite.setPos(_x/2, 0.0, _z/2)
    sprite.setTransparency(_transparent)
    return sprite, (sx, sz)

def getMousePos():
    if base.mouseWatcherNode.hasMouse():
        x=base.mouseWatcherNode.getMouseX()
        y=base.mouseWatcherNode.getMouseY()
        print(x, y)
        return (x, y)