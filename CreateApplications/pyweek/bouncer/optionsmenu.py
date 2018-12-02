from panda3d.core import TextNode
from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
    DirectRadioButton,
    DirectButton,
    DirectSlider,
    DGG,)
from direct.gui.DirectCheckBox import DirectCheckBox

class OptionsMenu():
    def __init__(self):
        self.frameMain = DirectFrame(
            image="optionsmenu.png",
            image_scale=(1.7778, 1, 1),
            frameSize=(
                base.a2dLeft, base.a2dRight,
                base.a2dBottom, base.a2dTop),
            frameColor=(0, 0, 0, 0))
        self.frameMain.setTransparency(True)

        volume = base.musicManager.getVolume()
        self.sliderMusicVolume = DirectSlider(
            scale=0.5,
            pos=(0, 0, -0.1),
            range=(0, 1),
            scrollSize=0.01,
            text="Music Volume: %d%%" % volume*100,
            text_scale=0.15,
            text_align=TextNode.ACenter,
            text_pos=(.0, 0.15),
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            thumb_frameColor=(0.8, 0, 1, 0.75),
            thumb_relief=DGG.FLAT,
            frameColor=(0.25, 0.25, 0.55, 1),
            value=volume,
            command=self.sliderMusicVolume_ValueChanged)
        self.sliderMusicVolume.reparentTo(self.frameMain)

        volume = base.sfxManagerList[0].getVolume()
        self.sliderSFXVolume = DirectSlider(
            scale=0.5,
            pos=(0, 0, -0.3),
            range=(0, 1),
            scrollSize=0.01,
            text="SFX Volume: %d%%" % volume*100,
            text_scale=0.15,
            text_align=TextNode.ACenter,
            text_pos=(.0, 0.15),
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            thumb_frameColor=(0.8, 0, 1, 0.75),
            thumb_relief=DGG.FLAT,
            frameColor=(0.25, 0.25, 0.55, 1),
            value=volume,
            command=self.sliderSFXVolume_ValueChanged)
        self.sliderSFXVolume.reparentTo(self.frameMain)

        isChecked = not base.AppHasAudioFocus
        img = None
        imgON = "AudioSwitch_on.png"
        imgOFF = "AudioSwitch_off.png"
        if base.AppHasAudioFocus:
            img = imgON
        else:
            img = imgOFF
        self.cbVolumeMute = DirectCheckBox(
            scale=0.5,
            text="Mute Audio",
            text_scale=0.15,
            text_align=TextNode.ACenter,
            text_pos=(0.0, 0.15),
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            pos=(0, 0, -0.5),
            command=self.cbVolumeMute_CheckedChanged,
            rolloverSound=None,
            clickSound=None,
            relief=None,
            pressEffect=False,
            isChecked=isChecked,
            image=img,
            image_scale=0.1,
            checkedImage=imgOFF,
            uncheckedImage=imgON)
        self.cbVolumeMute.setTransparency(True)
        self.cbVolumeMute.setImage()
        self.cbVolumeMute.reparentTo(self.frameMain)

        radio = base.loader.loadModel("radioBtn")
        radioGeom = (radio.find("**/RadioButtonReady"),
                     radio.find("**/RadioButtonChecked"))

        self.lblDifficulty = DirectLabel(
            text="Difficulty",
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            text_scale=0.6,
            scale=0.15,
            frameColor=(0, 0, 0, 0),
            pos=(-0.5, 0, -0.6))
        self.lblDifficulty.reparentTo(self.frameMain)
        self.difficulty = [base.difficulty]
        def createDifficultyDRB(self, text, value, initialValue, xPos):
            drb = DirectRadioButton(
                text=text,
                text_fg=(240/255.0,255/255.0,240/255.0,1),
                variable=self.difficulty,
                value=value,
                indicatorValue=initialValue,
                boxGeom=radioGeom,
                boxGeomScale = 0.5,
                #indicator_pad = (0.1, 0.1),
                scale=0.05,
                frameColor=(0.5,0.5,0.5,1),
                pressEffect=False,
                relief=1,
                pad=(0.5, 0, 0.5, 0.5),
                pos=(xPos, 0, -0.6),
                command=self.rbDifficulty_ValueChanged)
            drb.indicator.setX(drb.indicator.getX() + 0.1)
            drb.indicator.setZ(drb.indicator.getZ() + 0.1)
            drb.reparentTo(self.frameMain)
            return drb
        self.difficultyButtons = [
            createDifficultyDRB(
                self, "Easy", [0],
                1 if base.difficulty == 0 else 0,
                0.5-0.3),
            createDifficultyDRB(
                self, "Medium", [1],
                1 if base.difficulty == 1 else 0,
                0.5),
            createDifficultyDRB(
                self, "Hard", [2],
                1 if base.difficulty == 2 else 0,
                0.5+0.3)
        ]
        for button in self.difficultyButtons:
            button.setOthers(self.difficultyButtons)

        self.btnBack = DirectButton(
            text="Back",
            scale=0.15,
            text_pos=(-0.3, -0.2),
            text_scale=0.6,
            text_fg=(240/255.0,255/255.0,240/255.0,1),
            frameColor=(0, 0, 0, 0),
            image=("btnExit.png", "btnExit_hover.png", "btnExit_hover.png", "btnExit_hover.png"),
            image_scale=(1, 1, 0.5),
            pos=(0, 0, -0.8),
            command=base.messenger.send,
            extraArgs=["menu_Back"])
        self.btnBack.setTransparency(True)
        self.btnBack.reparentTo(self.frameMain)

        self.hide()

    def show(self):
        self.frameMain.show()

    def hide(self):
        self.frameMain.hide()

    def cbVolumeMute_CheckedChanged(self, checked):
        if checked:
            base.disableAllAudio()
        else:
            base.enableAllAudio()

    def sliderMusicVolume_ValueChanged(self):
        volume = round(self.sliderMusicVolume["value"], 2)
        self.sliderMusicVolume["text"] = "Music Volume: %d%%" % int(volume * 100)
        base.musicManager.setVolume(volume)

    def sliderSFXVolume_ValueChanged(self):
        volume = round(self.sliderSFXVolume["value"], 2)
        self.sliderSFXVolume["text"] = "SFX Volume: %d%%" % int(volume * 100)
        base.sfxManagerList[0].setVolume(volume)

    def rbDifficulty_ValueChanged(self):
        base.difficulty = self.difficulty[0]
