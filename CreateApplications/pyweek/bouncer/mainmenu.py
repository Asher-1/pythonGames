from panda3d.core import Point3
from direct.gui.DirectGui import (
    DirectFrame,
    DirectButton,
    OnscreenImage,)
from direct.interval.IntervalGlobal import Sequence, Parallel

class MainMenu():
    def __init__(self):
        self.frameMain = DirectFrame(
            image="mainmenu.png",
            image_scale=(1.7778, 1, 1),
            frameSize=(
                base.a2dLeft, base.a2dRight,
                base.a2dBottom, base.a2dTop),
            frameColor=(0, 0, 0, 0))
        self.frameMain.setTransparency(True)

        self.btnStart = DirectButton(
            text="Enter",
            scale=0.15,
            text_pos=(0, 1.1),
            text_scale=0.5,
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            frameColor=(0, 0, 0, 0),
            image=("btnEnter.png", "btnEnter_hover.png", "btnEnter_hover.png", "btnEnter_hover.png"),
            pos=(0, 0, -0.3),
            command=base.messenger.send,
            extraArgs=["menu_StartGame"])
        self.btnStart.setTransparency(True)
        self.btnStart.reparentTo(self.frameMain)

        self.btnOptions = DirectButton(
            text="Options",
            scale=0.1,
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            frameColor=(0, 0, 0, 0),
            image=("settings.png"),
            image_scale=1.2,
            text_pos=(0, -0.2),
            pos=(base.a2dRight-0.3, 0, base.a2dBottom+0.25),
            command=base.messenger.send,
            extraArgs=["menu_Options"])
        self.btnOptions.setTransparency(True)
        self.btnOptions.reparentTo(self.frameMain)

        self.btnQuit = DirectButton(
            text="Exit",
            scale=0.15,
            text_pos=(-0.3, -0.25),
            text_scale=0.75,
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            frameColor=(0, 0, 0, 0),
            image=("btnExit.png", "btnExit_hover.png", "btnExit_hover.png", "btnExit_hover.png"),
            image_scale=(1, 1, 0.5),
            pos=(base.a2dLeft+0.3, 0, base.a2dBottom+0.25),
            command=base.messenger.send,
            extraArgs=["menu_QuitGame"])
        self.btnQuit.setTransparency(True)
        self.btnQuit.reparentTo(self.frameMain)


        self.imgBouncer = OnscreenImage(
            image="bouncer.png",
            scale=(0.75*0.25, 1*0.25, 1*0.25),
            pos=(-0.25, 0, -0.3))
        self.imgBouncer.setTransparency(True)
        self.imgBouncer.reparentTo(self.frameMain)


        self.imgBadDude1 = OnscreenImage(
            image="badDude1.png",
            scale=(0.25, 0.25, 0.25),
            pos=(-0.75, 0, -0.4))
        self.imgBadDude1.setTransparency(True)
        self.imgBadDude1.reparentTo(self.frameMain)

        img = self.imgBadDude1
        up = img.posInterval(3.0, Point3(img.getX(), img.getY(), img.getZ()+0.01), bakeInStart=0)
        left = img.posInterval(3.0, Point3(img.getX()-0.01, img.getY(), img.getZ()), bakeInStart=0)
        right = img.posInterval(3.0, Point3(img.getX()+0.01, img.getY(), img.getZ()), bakeInStart=0)
        down = img.posInterval(3.0, Point3(img.getX(), img.getY(), img.getZ()-0.01), bakeInStart=0)
        rotForward = img.hprInterval(3.0, Point3(0, 0, 2.5), bakeInStart=0)
        rotBackward = img.hprInterval(3.0, Point3(0, 0, -2.5), bakeInStart=0)
        rotCenter = img.hprInterval(3.0, Point3(0, 0, 0), bakeInStart=0)
        self.ivalBadDude1 = Sequence(
            Parallel(rotCenter, up),
            Parallel(rotBackward, left),
            down,
            Parallel(rotCenter, up),
            Parallel(rotForward, right),
            down)


        self.imgGoodGal1 = OnscreenImage(
            image="goodGal1.png",
            scale=(0.6*0.25, 0.25, 0.25),
            pos=(-0.95, 0, -0.43))
        self.imgGoodGal1.setTransparency(True)
        self.imgGoodGal1.reparentTo(self.frameMain)

        img = self.imgGoodGal1
        up = img.posInterval(3.0, Point3(img.getX(), img.getY(), img.getZ()+0.01), bakeInStart=0)
        left = img.posInterval(3.0, Point3(img.getX()-0.01, img.getY(), img.getZ()), bakeInStart=0)
        right = img.posInterval(3.0, Point3(img.getX()+0.01, img.getY(), img.getZ()), bakeInStart=0)
        down = img.posInterval(3.0, Point3(img.getX(), img.getY(), img.getZ()-0.01), bakeInStart=0)
        rotForward = img.hprInterval(3.0, Point3(0, 0, 2.5), bakeInStart=0)
        rotBackward = img.hprInterval(3.0, Point3(0, 0, -2.5), bakeInStart=0)
        rotCenter = img.hprInterval(3.0, Point3(0, 0, 0), bakeInStart=0)
        self.ivalGoodGal1 = Sequence(
            left,
            right,
            left,
            down, up)


        self.imgGoodDude1 = OnscreenImage(
            image="goodDude1.png",
            scale=(0.25, 0.25, 0.25),
            pos=(0.95, 0, 0))
        self.imgGoodDude1.setTransparency(True)
        self.imgGoodDude1.reparentTo(self.frameMain)

        img = self.imgGoodDude1
        up = img.posInterval(3.0, Point3(img.getX(), img.getY(), img.getZ()+0.02), bakeInStart=0)
        left = img.posInterval(3.0, Point3(img.getX()-0.02, img.getY(), img.getZ()), bakeInStart=0)
        right = img.posInterval(3.0, Point3(img.getX()+0.02, img.getY(), img.getZ()), bakeInStart=0)
        down = img.posInterval(3.0, Point3(img.getX(), img.getY(), img.getZ()-0.02), bakeInStart=0)
        rotForward = img.hprInterval(3.0, Point3(0, 0, 4), bakeInStart=0)
        rotBackward = img.hprInterval(3.0, Point3(0, 0, -4), bakeInStart=0)
        rotCenter = img.hprInterval(3.0, Point3(0, 0, 0), bakeInStart=0)
        self.ivalGoodDude1 = Sequence(
            Parallel(up, rotCenter),
            Parallel(right, rotForward),
            Parallel(down, rotCenter),
            Parallel(left,rotBackward))

        self.hide()

    def show(self):
        self.frameMain.show()
        self.ivalBadDude1.loop()
        self.ivalGoodGal1.loop()
        self.ivalGoodDude1.loop()

    def hide(self):
        self.frameMain.hide()
        self.ivalBadDude1.finish()
        self.ivalGoodGal1.finish()
        self.ivalGoodDude1.finish()
