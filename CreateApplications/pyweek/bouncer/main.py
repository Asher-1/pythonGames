#!/usr/bin/python

# Python imports
import random
import sys
import os

# Panda Engine imports
from panda3d.core import (
    loadPrcFileData,
    loadPrcFile,
    AntialiasAttrib,
    TextNode,
    CardMaker,
    NodePath,
    TransparencyAttrib,
    TextureStage,
    LVecBase4f,
    ConfigPageManager,
    ConfigVariableBool,
    ConfigVariableInt,
    ConfigVariableDouble,
    OFileStream,)
from direct.interval.IntervalGlobal import Sequence
from direct.interval.FunctionInterval import (
    Wait,
    Func)
from direct.interval.LerpInterval import LerpColorScaleInterval
loadPrcFileData("",
"""
    window-title Grimfang - PyWeek22 - bouncer
    cursor-hidden 0
    model-path $MAIN_DIR/assets/
"""
)
prcFile = "mainConfig.prc"
if os.path.exists(prcFile):
    mainConfig = loadPrcFile(prcFile)
from direct.showbase.ShowBase import ShowBase
from direct.fsm.FSM import FSM
from direct.gui.DirectGui import DGG
from pandac.PandaModules import WindowProperties

# Game imports
from gamebase import GameBase
from game import Game
from mainmenu import MainMenu
from optionsmenu import OptionsMenu
from direct.gui.DirectGui import DirectLabel


def hide_cursor():
    """set the Cursor invisible"""
    props = WindowProperties()
    props.setCursorHidden(True)
    # somehow the window gets undecorated after hiding the cursor
    # so we reset it here to the value we need
    # props.setUndecorated(settings.fullscreen)
    base.win.requestProperties(props)


def show_cursor():
    """set the Cursor visible again"""
    props = WindowProperties()
    props.setCursorHidden(False)
    # set the filename to the mouse cursor
    cursors = ["cursorRed", "cursorBlue", "cursorViolet", "cursorGreen"]
    cursor = random.choice(cursors)
    x11 = "cursors/{}.x11".format(cursor)
    win = "cursors/{}.ico".format(cursor)
    if sys.platform.startswith("linux"):
        props.setCursorFilename(x11)
    else:
        props.setCursorFilename(win)
    base.win.requestProperties(props)
#----------------------------------------------------------------------#

class Main(ShowBase, FSM):

    def __init__(self):
        ShowBase.__init__(self)
        FSM.__init__(self, "mainStateMachine")

        # some basic enhancements
        # window background color
        self.setBackgroundColor(0, 0, 0)
        # set antialias for the complete sceen to automatic
        self.render.setAntialias(AntialiasAttrib.MAuto)
        # shader generator
        render.setShaderAuto()
        # Enhance font readability
        DGG.getDefaultFont().setPixelsPerUnit(100)
        # hide the mouse cursor
        hide_cursor()

        #
        # CONFIGURATION LOADING
        #
        # load given variables or set defaults
        # check if audio should be muted
        mute = ConfigVariableBool("audio-mute", False).getValue()
        if mute:
            self.disableAllAudio()
        else:
            self.enableAllAudio()

        base.sfxManagerList[0].setVolume(ConfigVariableDouble("audio-volume-sfx", 1.0).getValue())
        base.difficulty = ConfigVariableInt("difficulty", 0).getValue()

        def setFullscreen():
            """Helper function to set the window fullscreen
            with width and height set to the screens size"""
            # get the displays width and height
            w = self.pipe.getDisplayWidth()
            h = self.pipe.getDisplayHeight()
            # set window properties
            # clear all properties not previously set
            base.win.clearRejectedProperties()
            # setup new window properties
            props = WindowProperties()
            # Fullscreen
            props.setFullscreen(True)
            # set the window size to the screen resolution
            props.setSize(w, h)
            # request the new properties
            base.win.requestProperties(props)

        # check if the config file hasn't been created
        if not os.path.exists(prcFile):
            setFullscreen()
        elif base.appRunner:
            # When the application is started as appRunner instance, it
            # doesn't respect our loadPrcFiles configurations specific
            # to the window as the window is already created, hence we
            # need to manually set them here.
            for dec in range(mainConfig.getNumDeclarations()):
                # check if we have the fullscreen variable
                if mainConfig.getVariableName(dec) == "fullscreen":
                    setFullscreen()
        # automatically safe configuration at application exit
        base.exitFunc = self.__writeConfig

        # due to the delayed window resizing and switch to fullscreen
        # we wait some time until everything is set so we can savely
        # proceed with other setups like the menus
        if base.appRunner:
            # this behaviour only happens if run from p3d files and
            # hence the appRunner is enabled
            taskMgr.doMethodLater(0.5, self.postInit,
                "post initialization", extraArgs=[])
        else:
            self.postInit()

    def postInit(self):
        # Some game related variables
        self.currentLevel = 1
        self.youWon = False

        # Set esc to force exit $ remove
        self.accept('escape', self.exitApp)

        # Menu Events
        self.accept("menu_StartGame", self.startGame)
        self.accept("menu_Options", self.request, ["Options"])
        self.accept("menu_QuitGame", self.exitApp)
        self.accept("menu_Back", self.request, ["Menu"])
        self.accept("n", self.playNextTrack)

        ## Load Menu
        self.mainMenu = MainMenu()
        self.optionsMenu = OptionsMenu()

        ## Load music list
        self.musicList = [
            ["Housewell - Housewell - Sea  Sun  Fun", loader.loadMusic("music/Housewell_-_Housewell_-_Sea__Sun__Fun.ogg")],
            ["KontrastE - LISTEN TO NIGHT", loader.loadMusic("music/KontrastE_-_LISTEN_TO_NIGHT.ogg")],
            ["LukHash - THE OTHER SIDE", loader.loadMusic("music/LukHash_-_THE_OTHER_SIDE.ogg")],
            ["Axl & Arth - Breathe", loader.loadMusic("music/Axl__amp__Arth_-_Breathe.ogg")],
            ["Lyonn - The Symphony", loader.loadMusic("music/Lyonn_-_The_Symphony.ogg")],]
        self.lblNowPlaying = DirectLabel(
            text="No track running!",
            text_align=TextNode.ARight,
            text_fg=(240/255.0,255/255.0,240/255.0,0.75),
            pos=(base.a2dRight-0.05, 0, base.a2dBottom+0.1),
            scale=0.04,
            frameColor=(0,0,0,0.5),
            sortOrder = 10)
        self.lblNowPlaying.hide()

        # The games Intro
        def create16To9LogoCard(logoPath, tsName):
            cm = CardMaker("fade")
            scale = abs(base.a2dLeft) / 1.7776
            cm.setFrame(-1, 1, -1*scale, 1*scale)
            logo = NodePath(cm.generate())
            logo.setTransparency(TransparencyAttrib.MAlpha)
            logoTex = loader.loadTexture(logoPath)
            logoTs = TextureStage(tsName)
            logoTs.setMode(TextureStage.MReplace)
            logo.setTexture(logoTs, logoTex)
            logo.setBin("fixed", 5000)
            logo.reparentTo(render2d)
            logo.hide()
            return logo
        self.gfLogo = create16To9LogoCard("intro/GrimFangLogo.png", "gfLogoTS")
        self.pandaLogo = create16To9LogoCard("intro/Panda3DLogo.png", "pandaLogoTS")
        self.gameLogo = create16To9LogoCard("intro/GameLogo.png", "gameLogoTS")
        def createFadeIn(logo):
            return LerpColorScaleInterval(
                logo,
                2,
                LVecBase4f(0.0, 0.0, 0.0, 1.0),
                LVecBase4f(0.0, 0.0, 0.0, 0.0))
        def createFadeOut(logo):
            return LerpColorScaleInterval(
                logo,
                2,
                LVecBase4f(0.0, 0.0, 0.0, 0.0),
                LVecBase4f(0.0, 0.0, 0.0, 1.0))
        gfFadeInInterval = createFadeIn(self.gfLogo)
        gfFadeOutInterval = createFadeOut(self.gfLogo)
        p3dFadeInInterval = createFadeIn(self.pandaLogo)
        p3dFadeOutInterval = createFadeOut(self.pandaLogo)
        gameFadeInInterval = createFadeIn(self.gameLogo)
        gameFadeOutInterval = createFadeOut(self.gameLogo)
        self.introFadeInOutSequence = Sequence(
            Func(self.gfLogo.show),
            gfFadeInInterval,
            Wait(1.0),
            gfFadeOutInterval,
            Wait(0.5),
            Func(self.gfLogo.hide),
            Func(self.pandaLogo.show),
            p3dFadeInInterval,
            Wait(1.0),
            p3dFadeOutInterval,
            Wait(0.5),
            Func(self.pandaLogo.hide),
            Func(self.gameLogo.show),
            gameFadeInInterval,
            Wait(1.0),
            gameFadeOutInterval,
            Wait(0.5),
            Func(self.gameLogo.hide),
            Func(self.messenger.send, "intro_done"),
            Func(self.startMusic),
            name="fadeInOut")
        # game intro end

        # story intro
        self.storyImage1 = create16To9LogoCard("intro1.png", "storyIntro1TS")
        story1FadeInInterval = createFadeIn(self.storyImage1)
        story1FadeOutInterval = createFadeOut(self.storyImage1)
        self.storySequence = Sequence(
            Func(self.storyImage1.show),
            story1FadeInInterval,
            Wait(8.0),
            story1FadeOutInterval,
            Func(self.request, "Game"),
            name="story")

        # Outros
        self.outroImage1 = create16To9LogoCard("outro1.png", "storyOutro1TS")
        outro1FadeInInterval = createFadeIn(self.outroImage1)
        outro1FadeOutInterval = createFadeOut(self.outroImage1)
        self.outroWonSequence = Sequence(
            Func(self.outroImage1.show),
            outro1FadeInInterval,
            Wait(8.0),
            outro1FadeOutInterval,
            Func(self.request, "Game"),
            name="OutroWon")

        self.outroImage2 = create16To9LogoCard("outro2.png", "storyOutro2TS")
        outro2FadeInInterval = createFadeIn(self.outroImage2)
        outro2FadeOutInterval = createFadeOut(self.outroImage2)
        self.outroLostSequence = Sequence(
            Func(self.outroImage2.show),
            outro2FadeInInterval,
            Wait(8.0),
            outro2FadeOutInterval,
            Func(self.request, "Menu"),
            name="OutroLost")

        self.outroImage3 = create16To9LogoCard("outro3.png", "storyOutro3TS")
        outro3FadeInInterval = createFadeIn(self.outroImage3)
        outro3FadeOutInterval = createFadeOut(self.outroImage3)
        self.outroWonGameSequence = Sequence(
            Func(self.outroImage3.show),
            outro3FadeInInterval,
            Wait(8.0),
            outro3FadeOutInterval,
            Func(self.request, "Menu"),
            name="OutroWonGame")

        #
        # Start with the menu after the intro has been played
        #
        self.introFadeInOutSequence.start()
        self.accept("intro_done", self.request, ["Menu"])


    def exitApp(self):
        if self.state == "Off":
            self.introFadeInOutSequence.finish()
        elif self.state == "Menu":
            self.userExit()
        elif self.state == "Intro":
            self.storySequence.finish()
        elif self.state == "Outro":
            if self.youWon:
                if self.currentLevel == 2:
                    self.outroWonSequence.finish()
                else:
                    self.outroWonGameSequence.finish()
            else:
                self.outroLostSequence.finish()
        else:
            self.request("Menu")

    def startMusic(self):
        self.lblNowPlaying.show()
        self.lastPlayed = None
        self.currentTrack = [None]
        self.playNextTrack()
        base.taskMgr.add(self.musicTask, "music playlist")

    def playNextTrack(self):
        if self.currentTrack[0] is not None:
            self.currentTrack[1].stop()
        while self.lastPlayed == self.currentTrack[0]:
            self.currentTrack = random.choice(self.musicList)
        self.lastPlayed = self.currentTrack[0]
        self.lblNowPlaying["text"] = "Press 'N' for Next ~\nNOW PLAYING: {}".format(self.currentTrack[0])
        self.lblNowPlaying.resetFrameSize()
        self.currentTrack[1].play()

    def musicTask(self, task):
        if not base.AppHasAudioFocus: return task.cont
        track = self.currentTrack[1]
        if track.status() != track.PLAYING:
            self.playNextTrack()
        return task.cont

    def startGame(self):
        self.acceptWinLoose()
        self.currentLevel = 1
        self.request("Intro")

    def enterMenu(self):
        show_cursor()
        self.mainMenu.show()

    def exitMenu(self):
        self.mainMenu.hide()

    def enterOptions(self):
        self.optionsMenu.show()

    def exitOptions(self):
        self.optionsMenu.hide()

    def enterIntro(self):
        self.storySequence.start()

    def enterGame(self):
        self.youWon = False
        hide_cursor()
        ## Load/Start GameBase
        self.gamebase = GameBase()
        ## Load/Start Game
        self.game = Game()
        self.gamebase.start()
        self.game.setPhysicsWorld(self.gamebase.physics_world)
        if base.difficulty == 0:
            self.game.start(self.currentLevel, 25)
        elif base.difficulty == 1:
            self.game.start(self.currentLevel, 50)
        else:
            self.game.start(self.currentLevel, 100)
        self.acceptWinLoose()

        # Debug #
        #self.gamebase.enablePhysicsDebug()
        #print (render.ls())

    def exitGame(self):
        self.ignoreWinLoose()
        self.game.stop()
        self.gamebase.stop()
        del self.game
        del self.gamebase
        self.game = None
        self.gamebase = None

    def enterOutro(self):
        if self.youWon:
            if self.currentLevel == 1:
                self.outroWonSequence.start()
            else:
                self.outroWonGameSequence.start()
        else:
            self.outroLostSequence.start()

    def wonGame(self):
        self.ignoreWinLoose()
        self.youWon = True
        self.request("Outro")
        self.currentLevel += 1

    def lostGame(self):
        self.ignoreWinLoose()
        self.youWon = False
        self.request("Outro")

    def acceptWinLoose(self):
        self.accept("wonGame", self.wonGame)
        self.accept("lostGame", self.lostGame)

    def ignoreWinLoose(self):
        self.ignore("wonGame")
        self.ignore("lostGame")

    def __writeConfig(self):
        """Save current config in the prc file or if no prc file exists
        create one. The prc file is set in the prcFile variable"""
        page = None

        volume = str(round(base.musicManager.getVolume(), 2))
        volumeSfx = str(round(base.sfxManagerList[0].getVolume(), 2))
        mute = "#f" if base.AppHasAudioFocus else "#t"
        difficuty = str(base.difficulty)
        customConfigVariables = [
            "", "audio-mute", "audio-volume", "audio-volume-sfx", "difficulty"]
        if os.path.exists(prcFile):
            # open the config file and change values according to current
            # application settings
            page = loadPrcFile(prcFile)
            removeDecls = []
            for dec in range(page.getNumDeclarations()):
                # Check if our variables are given.
                # NOTE: This check has to be done to not loose our base or other
                #       manual config changes by the user
                if page.getVariableName(dec) in customConfigVariables:
                    decl = page.modifyDeclaration(dec)
                    removeDecls.append(decl)
            for dec in removeDecls:
                page.deleteDeclaration(dec)
            # NOTE: audio-mute are custom variables and
            #       have to be loaded by hand at startup
            # audio
            page.makeDeclaration("audio-volume", volume)
            page.makeDeclaration("audio-volume-sfx", volumeSfx)
            page.makeDeclaration("audio-mute", mute)
            page.makeDeclaration("difficulty", difficuty)
        else:
            # Create a config file and set default values
            cpMgr = ConfigPageManager.getGlobalPtr()
            page = cpMgr.makeExplicitPage("App Pandaconfig")
            # set OpenGL to be the default
            page.makeDeclaration("load-display", "pandagl")
            # get the displays width and height
            w = self.pipe.getDisplayWidth()
            h = self.pipe.getDisplayHeight()
            # set the window size in the config file
            page.makeDeclaration("win-size", "%d %d"%(w, h))
            # set the default to fullscreen in the config file
            page.makeDeclaration("fullscreen", "1")
            # audio
            page.makeDeclaration("audio-volume", volume)
            page.makeDeclaration("audio-volume-sfx", volumeSfx)
            page.makeDeclaration("audio-mute", "#f")
            page.makeDeclaration("sync-video", "1")
            page.makeDeclaration("textures-auto-power-2", "1")
            page.makeDeclaration("framebuffer-multisample", "1")
            page.makeDeclaration("multisamples", "2")
            page.makeDeclaration("texture-anisotropic-degree", "0")
            page.makeDeclaration("difficulty", 0)
        # create a stream to the specified config file
        configfile = OFileStream(prcFile)
        # and now write it out
        page.write(configfile)
        # close the stream
        configfile.close()

main = Main()
main.run()
