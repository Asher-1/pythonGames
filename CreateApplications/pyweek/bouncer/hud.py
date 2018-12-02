from panda3d.core import Point3, TextNode
from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,)

class Hud():
    def __init__(self):
        wp = base.win.getProperties()
        aspX = 1.0
        aspY = 1.0
        wpXSize = wp.getXSize()
        wpYSize = wp.getYSize()
        aspect = wpXSize / float(wpYSize)

        paneWidth = 0.4444445

        self.frameMain = DirectFrame(
            image="hudBackground.png",
            image_scale=(paneWidth, 1, 1),
            image_pos=(paneWidth, 0, 0),
            frameSize=(
                0, base.a2dRight/2.0,
                base.a2dBottom, base.a2dTop),
            frameColor=(0, 0, 0, 0),
            pos=(base.a2dLeft, 0, 0))
        self.frameMain.setTransparency(True)

        self.frameRightPane = DirectFrame(
            image="hudBackgroundRight.png",
            image_scale=(paneWidth, 1, 1),
            image_pos=(-paneWidth, 0, 0),
            frameSize=(
                base.a2dLeft/2.0, 0,
                base.a2dBottom, base.a2dTop),
            frameColor=(0, 0, 0, 0),
            pos=(base.a2dRight, 0, 0))
        self.frameRightPane.setTransparency(True)
        self.hide()

        self.lblScore = DirectLabel(
            text="Scoreboard",
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            scale=0.1,
            pos=(paneWidth,0,0.8),
            frameColor=(0,0,0,0),)
        self.lblScore.setTransparency(True)
        self.lblScore.reparentTo(self.frameMain)

        self.lblReds = DirectLabel(
            text="Bad dudes: 0",
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            text_align=TextNode.ALeft,
            scale=0.08,
            pos=(0.1,0,0.5),
            frameColor=(0,0,0,0),)
        self.lblReds.setTransparency(True)
        self.lblReds.reparentTo(self.frameMain)

        self.lblBlues = DirectLabel(
            text="Good dudes: 0",
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            text_align=TextNode.ALeft,
            scale=0.08,
            pos=(0.1,0,0.3),
            frameColor=(0,0,0,0),)
        self.lblBlues.setTransparency(True)
        self.lblBlues.reparentTo(self.frameMain)
        self.hide()

        txt = ""
        if base.difficulty == 0:
            txt = "Get 25 good dudes.\nIf you have more red\ndudes than blue,\nyou loose."
        elif base.difficulty == 1:
            txt = "Get 50 good dudes.\nIf you have more red\ndudes than blue,\nyou loose."
        else:
            txt = "Get 100 good dudes.\nIf you have more red\ndudes than blue,\nyou loose."

        self.lblInfoWinCondition = DirectLabel(
            text=txt,
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            text_align=TextNode.ALeft,
            scale=0.08,
            pos=(0.1,0,0.0),
            frameColor=(0,0,0,0),)
        self.lblInfoWinCondition.setTransparency(True)
        self.lblInfoWinCondition.reparentTo(self.frameMain)
        self.hide()

        self.lblInfo = DirectLabel(
            text="Controlls",
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            scale=0.1,
            pos=(-paneWidth,0,0.8),
            frameColor=(0,0,0,0),)
        self.lblInfo.setTransparency(True)
        self.lblInfo.reparentTo(self.frameRightPane)

        self.lblRight = DirectLabel(
            text="~ Right Door ~\nRight Arrow\nRight Alt\nRight Ctrl\n/",
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            scale=0.05,
            pos=(-paneWidth,0,0.7),
            frameColor=(0,0,0,0),
            sortOrder = 0)
        self.lblRight.setTransparency(True)
        self.lblRight.reparentTo(self.frameRightPane)

        self.lblLeft = DirectLabel(
            text="~ Left Door ~\nLeft Arrow\nLeft Alt\nLeft Ctrl\nZ",
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            scale=0.05,
            pos=(-paneWidth,0,0.4),
            frameColor=(0,0,0,0),)
        self.lblLeft.setTransparency(True)
        self.lblLeft.reparentTo(self.frameRightPane)


    def show(self):
        self.frameMain.show()
        self.frameRightPane.show()

    def hide(self):
        self.frameMain.hide()
        self.frameRightPane.hide()

    def update(self, redDudes, blueDudes):
        self.lblReds["text"] = "Bad dudes: {}".format(redDudes)
        self.lblBlues["text"] = "Good dudes: {}".format(blueDudes)
