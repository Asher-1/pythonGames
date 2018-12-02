# -*- coding: UTF-8 -*-
'''
Alien Conquer
Copyright (C) 2008 Taiua Pires

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License,
or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
or write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

Taiua Pires
Lavras,375/ap201 - Porto Alegre
CEP 90460-040
taiuapires@gmail.com
'''
# the pt_br_english is merely for reference of wich language the user preferes
import pt_br_english

lang = pt_br_english.pt_br

# the extra modules made by me for Alien Conquer
import ia, load, customgame_auxiliar_function, auxiliar_colision, save

if lang:
    print 'carregando pygame'
else:
    print 'loading pygame'

# the extra modules for various suports
import pygame, sys, random
from pygame.locals import *

if lang:
    print 'pygame carregado'
else:
    print 'pygame loaded'
if lang:
    print 'iniciando pygame'
else:
    print 'starting pygame'

# initializes pygame, make the cursor invisible, name the window and set an icon for the window
pygame.init()
pygame.mouse.set_visible(False)
pygame.display.set_caption('Alien Conquer')
pygame.display.set_icon(pygame.image.load(load.icon))

if lang:
    print 'pygame iniciado'
else:
    print 'pygame started'
if lang:
    print 'carregando classe "jogo"'
else:
    print 'loading class "game"'


# the main class of the game
# since most of the variables and functions names are in brazilian portuguese i'll put a comment on the side of their declaration
class game:
    altura = 768  # height
    largura = 1024  # width
    clock = pygame.time.Clock()  # so i can set the framerate
    alien = False  # play or not the dying alien sound
    laser = False  # play or not the laser sound
    die = False  # play or not the ship blowing up sound
    p = [True, True, True, True]  # list of which players are dead or alive
    velogame = 3  # game speed
    contgame = 0  # auxiliar counter of game speed
    nshot = 4  # i have absolutely no idea
    shotpx = [
        [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
         -40, -40, -40, -40, -40, -40, -40, -40, -40, -40],
        [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
         -40, -40, -40, -40, -40, -40, -40, -40, -40, -40],
        [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
         -40, -40, -40, -40, -40, -40, -40, -40, -40, -40],
        [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
         -40, -40, -40, -40, -40, -40, -40, -40, -40,
         -40]]  # coordenate x of the shoots of all players each player have 32 shots
    shotpy = [
        [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
         -40, -40, -40, -40, -40, -40, -40, -40, -40, -40],
        [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
         -40, -40, -40, -40, -40, -40, -40, -40, -40, -40],
        [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
         -40, -40, -40, -40, -40, -40, -40, -40, -40, -40],
        [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
         -40, -40, -40, -40, -40, -40, -40, -40, -40, -40]]  # coordenate x of the shoots of all players
    shotp = [0, 0, 0, 0]  # counter of which of the 32 shots should be next
    monsters = [
        [0, 32, 64, 96, 128, 160, 192, 256, 224, 288, 320, 352, 384, 416, 448, 480, 512, 544, 576, 608, 640, 672, 704,
         736, 768, 800, 832, 864, 896, 928, 960, 992],
        [18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18,
         18, 18, 18, 18]]  # although i call them monsters in the code they're the aliens coordenates x and y
    died1 = 0
    died2 = 0
    died3 = 0
    died4 = 0
    ship = [128, 600], [384, 600], [640, 600], [896, 600]  # positions (x and y) of the ships
    back1y = 0  # position for rendering the space background (since the background image "starfiel.gif is 512x512 an the runs at 1024x768 i need to render it several times in different positions")
    back2y = -512
    back3y = 512
    contshot = [0, 0, 0, 0]  # counter for time waiting between shoots
    contdead = [0, 0, 0, 0]  # counter for time waiting before respawn
    spritechange = [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3,
                    3]  # list aliens colors
    contboom = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]  # counter for aliens respawn
    x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0]  # were too lazy to put a decent name in it but this is the listof which aliens are dead (value 1) or alive (value 0)
    contboost = 0  # counter of which image should be rendered below the ships for the engine fire animation
    score = [0, 0, 0, 0]  # the score of each player
    end = 5  # the end condition reached (0=tie, 1=P1wins, 2=P2wins, 3=P3wins, 4=P4wins, 5=keep runing)
    horc = [0, 0, 0,
            0]  # which players are controled by humans or the artificial inteligence system (human or computer)
    trg = [ia.aim_foo(spritechange, x, monsters, ship[0][0], ship[0][1], 0),
           ia.aim_foo(spritechange, x, monsters, ship[1][0], ship[1][1], 1),
           ia.aim_foo(spritechange, x, monsters, ship[2][0], ship[2][1], 2),
           ia.aim_foo(spritechange, x, monsters, ship[3][0], ship[3][1],
                      3)]  # make the AI system choose initial targets for players (if one of them is not in game or controled by the a human this value is ignored)
    restart = False  # activates the "restartgame(self)" function
    notgonnadie = 0  # which player can respawn
    full = False  # False for default two player match/True for 4 player system (it is used to avoid wasting CPU on the 4 players system when only 2 are playing)
    finalscore = 0  # final score to show in the end

    # the wallless system, basicly the ships, esplosions sprites,etc are rendered 3 times, one in the screen one to left of the screen and one to the right
    # but when the middle one go out all three are pulled to the oposite direction, the function below bases itself in the middle one
    def wallless(self):
        for i in range(4):
            if self.ship[i][0] >= 1025:  # if it goes to the right
                self.ship[i][0] = 0  # move to the left
            elif self.ship[i][0] <= -1:  # if it goes to the left
                self.ship[i][0] = 1024  # move to the right

    # this function sets all variables to their original state when it goes back to the main menu after a match, there are variables from all classes here
    def restartgame(self):
        self.alien = False
        self.laser = False
        self.die = False
        self.p[0] = True
        self.p[1] = True
        self.p[2] = True
        self.p[3] = True
        self.velogame = 3
        self.contgame = 0
        self.nshot = 4
        self.shotpx[0] = [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
                          -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40]
        self.shotpy[0] = [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
                          -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40]
        self.shotp[0] = 0
        self.shotpx[1] = [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
                          -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40]
        self.shotpy[1] = [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
                          -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40]
        self.shotp[1] = 0
        self.shotpx[2] = [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
                          -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40]
        self.shotpy[2] = [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
                          -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40]
        self.shotp[2] = 0
        self.shotpx[3] = [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
                          -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40]
        self.shotpy[3] = [-40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40,
                          -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40, -40]
        self.shotp[3] = 0
        self.monsters = [
            [0, 32, 64, 96, 128, 160, 192, 256, 224, 288, 320, 352, 384, 416, 448, 480, 512, 544, 576, 608, 640, 672,
             704, 736, 768, 800, 832, 864, 896, 928, 960, 992],
            [18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18,
             18, 18, 18, 18, 18]]
        self.died1 = 0
        self.died2 = 0
        self.died3 = 0
        self.died4 = 0
        self.ship = [128, 600], [384, 600], [640, 600], [896, 600]
        self.back1y = 0
        self.back2y = -512
        self.back3y = 512
        self.contshot[0] = 0
        self.contshot[1] = 0
        self.contshot[2] = 0
        self.contshot[3] = 0
        self.contdead = [0, 0, 0, 0]
        self.spritechange = [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3,
                             3, 3]
        self.contboom = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                         100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
        self.x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.contboost = 0
        self.horc = [0, 0, 0, 0]
        self.score = [0, 0, 0, 0]
        self.end = 5
        self.notgonnadie = 0
        self.finalscore = 0
        r.dir[0] = 'c'
        r.dir[1] = 'c'
        r.dir[2] = 'c'
        r.dir[3] = 'c'
        r.font = pygame.font.Font('font.ttf', 24)
        r.txt = r.font.render(str(self.score), True, (0, 0, 0))
        r.createsurfaces = 0
        m.option = 0
        m.selected = 0
        self.restart = False  # so it won't restart again
        pygame.mixer.music.set_volume(1.0)

    # the name explains it
    def mainloop(self):
        a.music()  # start a music
        while m.selected == 0:  # while no option on the main menu has been selected
            pygame.time.wait(75)  # so the cursor won't move too fast
            m.mainscreen()
            if m.selected == 1:
                self.full = False
                # the other 2 must be killed
                self.p[2] = False
                self.p[3] = False
                # the 2 on game ships realligned
                self.ship[0][0] = 256
                self.ship[0][1] = 600
                self.ship[1][0] = 768
                self.ship[1][1] = 600
                # the aliens colors changed
                self.spritechange = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                     1, 1, 1, 1]
            elif m.selected == 2:
                # run as it is supposed to be
                self.full = True
            elif m.selected == 3:
                # opens the custom game screen
                m.customgame()
            elif m.selected == 4:
                # opens the inputs configuration screen
                m.custominput()
            elif m.selected == 5:
                # opens the instructions screen
                m.controlsscreen()
            elif m.selected == 6:
                # opens the credits screen
                r.creditsscreen()
            elif m.selected == 7:
                # shut Alien Conquer down
                sys.exit()
        # initializes items
        i.fullitem()
        # start to play the game music
        a.music()
        # the game main loop
        while self.restart == False:
            self.updatetime()
            self.invincible()
            c.fullinput()
            self.wallless()
            self.collision()
            self.areyoudead()
            r.fullrender()
            self.bonus()
            self.willend()
            a.soundfx()
            i.bullettimeoff()
            i.beam()
            i.bullettime()
            self.clock.tick(30)  # maintain an 30 frames per second framerate
            pygame.display.flip()  # update monitor
        # when the game is over restart variables and return to the main menu
        else:
            self.restartgame()
            self.mainloop()

    # make an player with the highest score able to respawn, not much to explain here
    def invincible(self):
        if self.score[0] > self.score[1] and self.score[0] > self.score[2] and self.score[0] > self.score[3]:
            self.notgonnadie = 1
        if self.score[1] > self.score[0] and self.score[1] > self.score[2] and self.score[1] > self.score[3]:
            self.notgonnadie = 2
        if self.full == True:
            if self.score[2] > self.score[0] and self.score[2] > self.score[1] and self.score[2] > self.score[3]:
                self.notgonnadie = 3
            if self.score[3] > self.score[0] and self.score[3] > self.score[1] and self.score[3] > self.score[2]:
                self.notgonnadie = 4

    # update counters and timers
    def updatetime(self):
        # changes the engine fire animation image of the ships
        self.contboost += 1
        if self.contboost >= 2:  # since there are only 2 images for that animation i only need the values 1 and 0
            self.contboost = 0
        # increase the time counter for shots, when it reaches the formula [30-game speed] allows the player to shoot
        self.contshot[0] += 1
        self.contshot[1] += 1
        # here is the first use of "full", as said before it prevents waste of cpu by NOT considerating players 3 and 4
        if self.full == True:
            self.contshot[2] += 1
            self.contshot[3] += 1
        # bt stands for "bullet time" since that item in the game affects all timers i need to check
        # if someone has it, who has it and who hasn't it
        for q in range(4):
            # check if it is activated
            if i.bt:
                # for the player that has the item limit the couter normally
                if i.gotitem[q] == 2:
                    if self.contshot[q] >= 30 - self.velogame:
                        self.contshot[q] = 30 - self.velogame
                # for the others give a larger counter
                else:
                    if self.contshot[q] >= 30:
                        self.contshot[q] = 30
            # if it is deactivated proceed normally
            else:
                if self.contshot[q] >= 30 - self.velogame:
                    self.contshot[q] = 30 - self.velogame
        # increase the counter for alien respawn
        for z in range(32):
            self.contboom[z] += 1
            # limit the counter at value 100
            if self.contboom[z] > 100: self.contboom[z] = 100
        # loop counter increase for increasing game speed
        self.contgame += 1
        # when loop counter reaches 250 increase game speed
        if self.contgame >= 250:
            self.velogame += 1
            self.contgame = 0

    # name self explanatory
    def collision(self):

        pygame.event.pump()
        keyinput = pygame.key.get_pressed()
        self.ship, self.trg = auxiliar_colision.ship2ship_colision(self.ship, self.p, self.velogame,
                                                                   auxiliar_colision.all_players_inputs_list(c.udrls,
                                                                                                             keyinput,
                                                                                                             c.shot,
                                                                                                             m.mode,
                                                                                                             c.joyvert,
                                                                                                             c.joyhor,
                                                                                                             c.AI_x,
                                                                                                             c.AI_y,
                                                                                                             c.njoy),
                                                                   self.trg, self.x)

        # colision between shots and aliens
        for s in range(32):  # 32 shots
            for j in range(32):  # 32 aliens
                if ((self.shotpx[0][s] >= self.monsters[0][j] - 15 and self.shotpx[0][s] <= self.monsters[0][
                    j] + 25) and (
                        self.shotpy[0][s] >= self.monsters[1][j] - 20 and self.shotpy[0][s] <= self.monsters[1][
                    j] + 20) and (self.x[j] == 0)):
                    if self.spritechange[j] == 0:  # check the color
                        self.score[0] += 10  # if it is the same add 10 to score
                    else:
                        self.score[0] += 20  # else add 20
                    self.shotpy[0][s] = -40  # move the shot to out of the screen
                    self.alien = True  # so that the "audio" class run the dying alien sound
                    self.contboom[j] = 0  # start the alien respawn counter
                    self.x[j] = 1  # set the alien to "dead" in the dead aliens list
                    if i.itemlist[j] != 0:  # if the alien killed had an item, drop it
                        i.dropitem(j)
                    self.spritechange[j] = 0  # set the alien color to the same color as the ship who killed it
                # from here i just repeat the system above
                if ((self.shotpx[1][s] >= self.monsters[0][j] - 15 and self.shotpx[1][s] <= self.monsters[0][
                    j] + 25) and (
                        self.shotpy[1][s] >= self.monsters[1][j] - 20 and self.shotpy[1][s] <= self.monsters[1][
                    j] + 20) and (self.x[j] == 0)):
                    if self.spritechange[j] == 1:
                        self.score[1] += 10
                    else:
                        self.score[1] += 20
                    self.shotpy[1][s] = -40
                    self.alien = True
                    self.contboom[j] = 0
                    self.x[j] = 1
                    if i.itemlist[j] != 0:
                        i.dropitem(j)
                    self.spritechange[j] = 1
                if self.full == True:  # to avoid cpu waste
                    if ((self.shotpx[2][s] >= self.monsters[0][j] - 15 and self.shotpx[2][s] <= self.monsters[0][
                        j] + 25) and (
                            self.shotpy[2][s] >= self.monsters[1][j] - 20 and self.shotpy[2][s] <= self.monsters[1][
                        j] + 20) and (self.x[j] == 0)):
                        if self.spritechange[j] == 2:
                            self.score[2] += 10
                        else:
                            self.score[2] += 20
                        self.shotpy[2][s] = -40
                        self.alien = True
                        self.contboom[j] = 0
                        self.x[j] = 1
                        if i.itemlist[j] != 0:
                            i.dropitem(j)
                        self.spritechange[j] = 2
                    if ((self.shotpx[3][s] >= self.monsters[0][j] - 15 and self.shotpx[3][s] <= self.monsters[0][
                        j] + 25) and (
                            self.shotpy[3][s] >= self.monsters[1][j] - 20 and self.shotpy[3][s] <= self.monsters[1][
                        j] + 20) and (self.x[j] == 0)):
                        if self.spritechange[j] == 3:
                            self.score[3] += 10
                        else:
                            self.score[3] += 20
                        self.shotpy[3][s] = -40
                        self.alien = True
                        self.contboom[j] = 0
                        self.x[j] = 1
                        if i.itemlist[j] != 0:
                            i.dropitem(j)
                        self.spritechange[j] = 3

        # colision between aliens and players respawn
        for u in range(32):  # 32 aliens
            for o in range(4):  # 4 players
                if (self.monsters[0][u] > 485 and self.monsters[0][u] + 34 < 563) and (
                        self.monsters[1][u] > 578 and self.monsters[1][u] + 26 < 696) and self.contdead[o] in range(130,
                                                                                                                    135):
                    if self.spritechange[u] == 1:
                        self.score[o] += 10
                    else:
                        self.score[o] += 20
                    self.alien = True
                    self.contboom[u] = 0
                    self.x[u] = 1
                    if i.itemlist[u] != 0:
                        i.dropitem(u)
                    self.spritechange[u] = 1
                elif (self.monsters[0][u] > 476 and self.monsters[0][u] + 34 < 541) and (
                        self.monsters[1][u] > 564 and self.monsters[1][u] + 26 < 662) and self.contdead[o] in range(135,
                                                                                                                    140):
                    if self.spritechange[u] == 1:
                        self.score[o] += 10
                    else:
                        self.score[o] += 20
                    self.alien = True
                    self.contboom[u] = 0
                    self.x[u] = 1
                    if i.itemlist[u] != 0:
                        i.dropitem(u)
                    self.spritechange[u] = 1
                elif (self.monsters[0][u] > 468 and self.monsters[0][u] + 34 < 518) and (
                        self.monsters[1][u] > 552 and self.monsters[1][u] + 26 < 627) and self.contdead[o] in range(140,
                                                                                                                    145):
                    if self.spritechange[u] == 1:
                        self.score[o] += 10
                    else:
                        self.score[o] += 20
                    self.alien = True
                    self.contboom[u] = 0
                    self.x[u] = 1
                    if i.itemlist[u] != 0:
                        i.dropitem(u)
                    self.spritechange[u] = 1
                elif (self.monsters[0][u] > 462 and self.monsters[0][u] + 34 < 492) and (
                        self.monsters[1][u] > 542 and self.monsters[1][u] + 26 < 587) and self.contdead[o] in range(145,
                                                                                                                    150):
                    if self.spritechange[u] == 1:
                        self.score[o] += 10
                    else:
                        self.score[o] += 20
                    self.alien = True
                    self.contboom[u] = 0
                    self.x[u] = 1
                    if i.itemlist[u] != 0:
                        i.dropitem(u)
                    self.spritechange[u] = 1

        # colision between aliens and ships
        for k in range(32):  # 32 aliens
            # check player by player (i will optimaze it in the future)
            if self.x[k] == 0:
                if (self.ship[0][0] >= self.monsters[0][k] - 15 and self.ship[0][0] <= self.monsters[0][k] + 50) and (
                        self.ship[0][1] >= self.monsters[1][k] - 15 and self.ship[0][1] <= self.monsters[1][k] + 48) and \
                        self.contboom[k] >= 0:
                    if self.died1 == 0: self.died1 = 1
                    self.p[0] = False  # turn stat to dead ("False")
                if (self.ship[1][0] >= self.monsters[0][k] - 15 and self.ship[1][0] <= self.monsters[0][k] + 50) and (
                        self.ship[1][1] >= self.monsters[1][k] - 15 and self.ship[1][1] <= self.monsters[1][k] + 48) and \
                        self.contboom[k] >= 0:
                    if self.died2 == 0: self.died2 = 1
                    self.p[1] = False
                if self.full == True:
                    if (self.ship[2][0] >= self.monsters[0][k] - 15 and self.ship[2][0] <= self.monsters[0][
                        k] + 50) and (
                            self.ship[2][1] >= self.monsters[1][k] - 15 and self.ship[2][1] <= self.monsters[1][
                        k] + 48) and self.contboom[k] >= 0:
                        if self.died3 == 0: self.died3 = 1
                        self.p[2] = False
                    if (self.ship[3][0] >= self.monsters[0][k] - 15 and self.ship[3][0] <= self.monsters[0][
                        k] + 50) and (
                            self.ship[3][1] >= self.monsters[1][k] - 15 and self.ship[3][1] <= self.monsters[1][
                        k] + 48) and self.contboom[k] >= 0:
                        if self.died4 == 0: self.died4 = 1
                        self.p[3] = False

        # colision between players and items
        if self.p[0]:  # check if the player is alive
            if (self.ship[0][0] >= i.itemx - 15 and self.ship[0][0] <= i.itemx + 50) and (
                    self.ship[0][1] >= i.itemy - 15 and self.ship[0][1] <= i.itemy + 48):
                i.gotitem[0] = i.selected  # set, in the item list, who has the item(gotitem[]) and which item(selected)
                a.item(0)  # run item specific sound effect
                i.itemx = -50  # move the item to out of the the screen so no one else get it too
        if self.p[1]:
            if (self.ship[1][0] >= i.itemx - 15 and self.ship[1][0] <= i.itemx + 50) and (
                    self.ship[1][1] >= i.itemy - 15 and self.ship[1][1] <= i.itemy + 48):
                i.gotitem[1] = i.selected
                a.item(1)
                i.itemx = -50
        if self.p[2]:
            if (self.ship[2][0] >= i.itemx - 15 and self.ship[2][0] <= i.itemx + 50) and (
                    self.ship[2][1] >= i.itemy - 15 and self.ship[2][1] <= i.itemy + 48):
                i.gotitem[2] = i.selected
                a.item(2)
                i.itemx = -50
        if self.p[3]:
            if (self.ship[3][0] >= i.itemx - 15 and self.ship[3][0] <= i.itemx + 50) and (
                    self.ship[3][1] >= i.itemy - 15 and self.ship[3][1] <= i.itemy + 48):
                i.gotitem[3] = i.selected
                a.item(3)
                i.itemx = -50

    # when a player dies its "died#" changes from 0 to 1, when it becomes 1 a sound is played and "died#" becomes 2 meaning that the sound has been played and the player is dead
    def areyoudead(self):
        if self.died1 == 1:
            self.die = True
            self.died1 = 2
        if self.died2 == 1:
            self.die = True
            self.died2 = 2
        if self.full == True:
            if self.died3 == 1:
                self.die = True
                self.died3 = 2
            if self.died4 == 1:
                self.die = True
                self.died4 = 2

    # bonus points conditions, basicly if a player has all aliens in the same color as its own it gets 5 bonus points per loop (30 loops per socond)
    def bonus(self):
        if self.spritechange == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                 0, 0, 0]:
            self.score[0] += 5
        if self.spritechange == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                 1, 1, 1]:
            self.score[1] += 5
        if self.full == True:
            if self.spritechange == [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                                     2, 2, 2, 2]:
                self.score[2] += 5
            if self.spritechange == [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
                                     3, 3, 3, 3]:
                self.score[3] += 5

    # end game conditions
    def willend(self):
        if (self.contdead[0] >= 150 and self.p[
            0] == False) and self.end == 5 and self.notgonnadie == 1:  # if the player died but its covered by the respawn conditions
            self.p[0] = True  # change stat to alive (True)
            self.died1 = 0  # sets the audio dying condition to 0 (alive)
            self.ship[0][0] = 500  # coordinate x for respawn
            self.ship[0][1] = 600  # coordinate y for respawn
            self.contdead[0] = 0  # sets the respawn counter to 0
        if self.p[2] == False and self.p[1] == False and self.p[
            3] == False and self.end == 5 and self.notgonnadie == 1:  # if all the other players are dead and NOT covered by the respawn condition
            self.end = 1  # means that player1 wins
            self.finalscore = self.score[0]  # set the final score for showing in screen
            if r.createsurfaces == 0: r.createendgamesurfaces()

        if (self.contdead[1] >= 150 and self.p[1] == False) and self.end == 5 and self.notgonnadie == 2:
            self.p[1] = True
            self.died2 = 0
            self.ship[1][0] = 500
            self.ship[1][1] = 600
            self.contdead[1] = 0
        if self.p[0] == False and self.p[2] == False and self.p[3] == False and self.end == 5 and self.notgonnadie == 2:
            self.end = 2
            self.finalscore = self.score[1]
            if r.createsurfaces == 0: r.createendgamesurfaces()

        if self.full == True:
            if (self.contdead[2] >= 150 and self.p[2] == False) and self.end == 5 and self.notgonnadie == 3:
                self.p[2] = True
                self.died3 = 0
                self.ship[2][0] = 500
                self.ship[2][1] = 600
                self.contdead[2] = 0
            if self.p[0] == False and self.p[1] == False and self.p[
                3] == False and self.end == 5 and self.notgonnadie == 3:
                self.end = 3
                self.finalscore = self.score[2]
                if r.createsurfaces == 0: r.createendgamesurfaces()

            if (self.contdead[3] >= 150 and self.p[3] == False) and self.end == 5 and self.notgonnadie == 4:
                self.p[3] = True
                self.died4 = 0
                self.ship[3][0] = 500
                self.ship[3][1] = 600
                self.contdead[3] = 0
            if self.p[0] == False and self.p[1] == False and self.p[
                2] == False and self.end == 5 and self.notgonnadie == 4:
                self.end = 4
                self.finalscore = self.score[3]
                if r.createsurfaces == 0: r.createendgamesurfaces()

        # if all players are dead and no one is covered by the respawn conditions (tie)
        if self.p[0] == False and self.p[1] == False and self.p[2] == False and self.p[3] == False and self.end == 5:
            if self.contdead[0] < 150 and self.contdead[1] < 150 and self.contdead[2] < 150 and self.contdead[3] < 150:
                self.end = 0  # means "no winner", "tie"
                if r.createsurfaces == 0: r.createendgamesurfaces()


# declare the global access to the "game" class through pointer "g"
g = game()
if lang:
    print 'classe "jogo" carregada'
else:
    print 'class "game" loaded'
if lang:
    print 'carregando classe "audio"'
else:
    print 'loading class "audio"'


# class that is responsible for playing music and sound effects
class audio:
    # load audio files through "load" module
    def __init__(self):
        self.lasercanon = pygame.mixer.Sound(load.lc)
        self.laser = pygame.mixer.Sound(load.lsr)
        self.alien = pygame.mixer.Sound(load.aln)
        self.die = pygame.mixer.Sound(load.d)
        self.bton = pygame.mixer.Sound(load.bon)
        self.btoff = pygame.mixer.Sound(load.boff)

    # audio efects for item caughting
    def item(self, c):
        if i.gotitem[c] == 1:  # if the player that caught an item caught the "laser canon" item
            self.lasercanon.play()  # play "laser canon" sound effect
        elif i.gotitem[c] == 2:  # if the player that caught an item caught the "bullet time" item
            self.bton.play()  # play activation of "bullet time" sound effect
            pygame.mixer.music.set_volume(0.25)  # set the music volume to 25% of its maximium volume

    # general sound effects
    # *see alien,laser and die variable description of class "game"*
    def soundfx(self):
        if g.alien == True:
            self.alien.play()
            g.alien = False
        if g.laser == True:
            self.laser.play()
            g.laser = False
        if g.die == True:
            self.die.play()
            g.die = False

    # music player (this function is only called when an music must be restarted or changed)
    # pygame can only play one "music" at time
    def music(self):
        pygame.mixer.music.stop()  # stops the current music
        if m.selected == 0:  # if it still is in menu
            pygame.mixer.music.load(load.menumusic)  # play menu music
        else:  # the other possibility is that it is in game
            pygame.mixer.music.load(load.gamemusic)  # play game music
        pygame.mixer.music.play(-1, 0.0)  # "-1" to play it again when it is over
        pygame.mixer.music.set_volume(1.0)  # set music volume at maximium


# declare the global access to the "audio" class through pointer "a"
a = audio()
a.__init__()
if lang:
    print 'classe "audio" carregada'
else:
    print 'class "audio" loaded'
if lang:
    print 'carregando classe "render"'
else:
    print 'loading class "render"'


# class responsible for rendering screen
class render:
    winnersurface = pygame.Surface((635, 74))  # surface that declares the winner
    finalscoresurface = pygame.Surface((438, 38))  # surface that shows the winner's final score
    # verdana = pygame.font.match_font('Verdana')
    font = pygame.font.Font('font.ttf', 24)  # load TrueType font and set a size for it
    txt = font.render('', True, (0, 0, 0))  # set a color for the font
    customscreen1 = pygame.image.load(
        load.custom1)  # custom game screen 1 and 2 (one of them has the colored rectangles and the other don't)
    customscreen2 = pygame.image.load(
        load.custom2)  # in game at the custom game screen they alternate quickly for visual effect
    customicon = pygame.image.load(load.customicon)  # the icon for the main menu cursor when over "Custom Game" option
    beam = [pygame.image.load(load.bm1), pygame.image.load(load.bm2), pygame.image.load(load.bm3),
            pygame.image.load(load.bm4)]  # load all the "laser canon sprites" in a list of surfaces
    # ship sprites
    sprite1 = pygame.image.load(load.sc1)  # sprite1 stand for sprite of ship of player one
    sprite2 = pygame.image.load(load.sc2)
    sprite3 = pygame.image.load(load.sc3)
    sprite4 = pygame.image.load(load.sc4)
    sprite1e = pygame.image.load(
        load.se1)  # sprite1e stand for sprite of ship of player one turned to the left ("esquerda" in potuguese means "left")
    sprite2e = pygame.image.load(load.se2)
    sprite3e = pygame.image.load(load.se3)
    sprite4e = pygame.image.load(load.se4)
    sprite1d = pygame.image.load(
        load.sd1)  # sprite1e stand for sprite of ship of player one turned to the right ("direita" in potuguese means "right")
    sprite2d = pygame.image.load(load.sd2)
    sprite3d = pygame.image.load(load.sd3)
    sprite4d = pygame.image.load(load.sd4)
    # the "tevira#" sprite are for an effect of a joke put in the instructions screen
    tevira1 = pygame.image.load(load.tv1)
    tevira2 = pygame.image.load(load.tv2)
    tevira3 = pygame.image.load(load.tv3)
    tevira4 = pygame.image.load(load.tv4)
    # item sprites
    item1a = pygame.image.load(load.i1a)  # item 1 sprite 1
    item1b = pygame.image.load(load.i1b)  # item 1 sprite 2
    item2a = pygame.image.load(load.i2a)  # item 2 sprite 1
    item2b = pygame.image.load(load.i2b)  # item 2 sprite 2
    boom = pygame.image.load(load.booom)  # explosion sprite
    # aliens sprites
    monster1 = pygame.image.load(load.m1)  # alien 1
    monster2 = pygame.image.load(load.m2)  # alien 2
    monster3 = pygame.image.load(load.m3)  # alien 3
    monster4 = pygame.image.load(load.m4)  # alien 4
    background1 = pygame.image.load(load.bk)  # space background
    # laser sprites
    shot1 = pygame.image.load(load.l1)  # laser 1
    shot2 = pygame.image.load(load.l2)  # laser 2
    shot3 = pygame.image.load(load.l3)  # laser 3
    shot4 = pygame.image.load(load.l4)  # laser 4
    # ships' engine fire animation sprites
    boost1 = pygame.image.load(load.bst1)
    boost2 = pygame.image.load(load.bst2)
    if lang:
        mainmenu = pygame.image.load(load.mainm)  # if the languge choosen is portuguese, load portuguese menu
    else:
        mainmenu = pygame.image.load(load.mainmeng)  # if the languge choosen is english, load english menu
    cursor1 = pygame.image.load(load.csr1)  # main menu cursor for 2 player game
    cursor2 = pygame.image.load(load.csr2)  # main menu cursor for 4 player game
    info = pygame.image.load(load.ci)  # main menu cursor for "Instructions" screen
    if lang:
        infoscreen = pygame.image.load(
            load.ciscreen)  # if the languge choosen is portuguese, load portuguese instructions screen image
    else:
        infoscreen = pygame.image.load(
            load.ciscreeneng)  # if the languge choosen is english, load english instruction screen image
    quit = pygame.image.load(load.qt)  # main menu cursor for "Quit" option
    config = pygame.image.load(load.setupinput)  # image for "Configurations" screen
    configicon = pygame.image.load(load.config)  # main menu cursor for "Configurations" screen
    if lang:
        credit = pygame.image.load(load.credit)  # if the languge choosen is portuguese, load portuguese credits screen
    else:
        credit = pygame.image.load(load.crediteng)  # if the languge choosen is english, load english credits screen
    crediticon = pygame.image.load(load.credicon)  # main menu cursor for credits screen
    # respawn sprites
    respawn1 = [pygame.image.load(load.respawn1[0]), pygame.image.load(load.respawn1[1]),
                pygame.image.load(load.respawn1[2]), pygame.image.load(load.respawn1[3])]
    respawn2 = [pygame.image.load(load.respawn2[0]), pygame.image.load(load.respawn2[1]),
                pygame.image.load(load.respawn2[2]), pygame.image.load(load.respawn2[3])]
    respawn3 = [pygame.image.load(load.respawn3[0]), pygame.image.load(load.respawn3[1]),
                pygame.image.load(load.respawn3[2]), pygame.image.load(load.respawn3[3])]
    respawn4 = [pygame.image.load(load.respawn4[0]), pygame.image.load(load.respawn4[1]),
                pygame.image.load(load.respawn4[2]), pygame.image.load(load.respawn4[3])]
    finalsurface1 = pygame.Surface((635, 74))
    finalsurface2 = pygame.Surface((438, 38))
    fullrespawn = [respawn1, respawn2, respawn3, respawn4]  # an "all-in-one" respawn sprites
    dir = ['c', 'c', 'c',
           'c']  # stands for direction (all ships have 3 sprites('c' for center,'e' for left,'d' for right)) for all players (P1,P2,P3,P4)
    createsurfaces = 0  # 0 for don't create them yet, 1 for create them, 2 for already created them

    # screen initialization
    def __init__(self):
        aux = pygame.display.list_modes()  # get supported fullscreen resolutions
        maxres = max(aux)  # get maximium value
        if maxres > (1024, 768):
            # if the maximium fullscreen resolution is greater than 1024x768 run Alien Conquer in a window
            self.screen = pygame.display.set_mode((1024, 768))
        else:
            # else run it in fullscreen mode
            self.screen = pygame.display.set_mode((1024, 768), FULLSCREEN)

    # the all-in-one render function
    def fullrender(self):
        self.space()
        self.boost()
        self.ship()
        self.laser()
        self.alien()
        self.respawn()
        self.txtrender()

    # render respawn animation when required
    def respawn(self):
        if g.end == 5:
            for p in range(4):
                # only render it in the end of the counter (130->150) in the center of the screen where the respawning player will appear
                if g.contdead[p] in range(130, 135):
                    self.screen.blit(self.fullrespawn[p][3], (485, 578))
                elif g.contdead[p] in range(135, 140):
                    self.screen.blit(self.fullrespawn[p][2], (476, 564))
                elif g.contdead[p] in range(140, 145):
                    self.screen.blit(self.fullrespawn[p][1], (468, 552))
                elif g.contdead[p] in range(145, 150):
                    self.screen.blit(self.fullrespawn[p][0], (462, 542))

    # render space background
    # the background image is only 512x512 and the game runs at 1024x768 so that image must be drawn multiple time in different locations, in total there are 3 vertical coordenates
    def space(self):
        if i.bt:  # move background slower when "bullet time" is activated
            g.back1y += 1
            g.back2y += 1
            g.back3y += 1
        else:
            g.back1y += g.velogame  # since the gamespeed affects here the background will move faster according to the game speed
            g.back2y += g.velogame
            g.back3y += g.velogame
        # after an image goes below the screen, it must be pushed above it
        if g.back1y >= 1024:
            g.back1y -= 1536
        if g.back2y >= 1024:
            g.back2y -= 1536
        if g.back3y >= 1024:
            g.back3y -= 1536
        # rendering commands
        self.screen.blit(self.background1, (0, g.back1y))
        self.screen.blit(self.background1, (0, g.back2y))
        self.screen.blit(self.background1, (0, g.back3y))
        self.screen.blit(self.background1, (512, g.back1y))
        self.screen.blit(self.background1, (512, g.back2y))
        self.screen.blit(self.background1, (512, g.back3y))

    # render the surfacer made with font (such as score)
    def txtrender(self):
        if g.end == 5:  # condition that means that the game is still running
            self.txt = self.font.render(str(g.score[0]), True, (255, 0, 0))
            self.screen.blit(self.txt, (10,
                                        740))  # the score of the first player will always appear in the same place but the others depend on the game mode selected in the main menu
            if g.full == True:
                self.txt = self.font.render(str(g.score[1]), True, (0, 0, 255))
                self.screen.blit(self.txt, (270, 740))
                self.txt = self.font.render(str(g.score[2]), True, (255, 255, 0))
                pos = len(str(g.score[1]))
                self.screen.blit(self.txt, (600 - (pos * 20), 740))
                self.txt = self.font.render(str(g.score[3]), True, (0, 255, 0))
                pos = len(str(g.score[3]))
                self.screen.blit(self.txt, (1022 - (pos * 20), 740))
            else:
                self.txt = self.font.render(str(g.score[1]), True, (0, 0, 255))
                pos = len(str(g.score[1]))
                self.screen.blit(self.txt, (1022 - (pos * 20), 740))
        else:
            self.drawfinalsurfaces()

    def drawfinalsurfaces(self):
        self.screen.blit(self.winnersurface, (250, 300))
        if g.end != 0:
            self.screen.blit(self.finalscoresurface, (270, 400))

    # render the final score below the winner message in the end of a match
    def finalscore(self):
        fontfinalscore = pygame.font.Font('font.ttf', 30)
        if lang:
            yourfinalscore = fontfinalscore.render('sua pontuacao final foi:' + str(g.finalscore), True,
                                                   customgame_auxiliar_function.aux_func(
                                                       g.end - 1))  # the message depends on the language selected
        else:
            yourfinalscore = fontfinalscore.render('  your final score were:' + str(g.finalscore), True,
                                                   customgame_auxiliar_function.aux_func(g.end - 1))
        self.screen.blit(yourfinalscore, (270, 400))

    # ships' engine fire animation, in the class "game" there was a counter "contboost" to decide which of the 2 images should be drawn below the ships
    def boost(self):
        if g.contboost == 1:
            if g.p[0]:
                self.screen.blit(self.boost1, (g.ship[0][0] - 7, g.ship[0][1] + 20))
            if g.p[1]:
                self.screen.blit(self.boost1, (g.ship[1][0] - 7, g.ship[1][1] + 20))
            if g.full == True:
                if g.p[2]:
                    self.screen.blit(self.boost1, (g.ship[2][0] - 7, g.ship[2][1] + 20))
                if g.p[3]:
                    self.screen.blit(self.boost1, (g.ship[3][0] - 7, g.ship[3][1] + 20))
        if g.contboost == 0:
            if g.p[0]:
                self.screen.blit(self.boost2, (g.ship[0][0] - 7, g.ship[0][1] + 20))
            if g.p[1]:
                self.screen.blit(self.boost2, (g.ship[1][0] - 7, g.ship[1][1] + 20))
            if g.full == True:
                if g.p[2]:
                    self.screen.blit(self.boost2, (g.ship[2][0] - 7, g.ship[2][1] + 20))
                if g.p[3]:
                    self.screen.blit(self.boost2, (g.ship[3][0] - 7, g.ship[3][1] + 20))

    # draw the ship sprites and which image (left, center or right)
    def ship(self):
        if g.p[0]:  # check if the player is alive
            if self.dir[0] == 'c':
                self.screen.blit(self.sprite1, (g.ship[0][0] - 23, g.ship[0][1] - 25))
                self.screen.blit(self.sprite1, (g.ship[0][0] - 1047, g.ship[0][1] - 25))
                self.screen.blit(self.sprite1, (g.ship[0][0] + 1001, g.ship[0][1] - 25))
            if self.dir[0] == 'e':
                self.screen.blit(self.sprite1e, (g.ship[0][0] - 23, g.ship[0][1] - 22))
                self.screen.blit(self.sprite1e, (g.ship[0][0] - 1047, g.ship[0][1] - 22))
                self.screen.blit(self.sprite1e, (g.ship[0][0] + 1001, g.ship[0][1] - 22))
            if self.dir[0] == 'd':
                self.screen.blit(self.sprite1d, (g.ship[0][0] - 23, g.ship[0][1] - 22))
                self.screen.blit(self.sprite1d, (g.ship[0][0] - 1047, g.ship[0][1] - 22))
                self.screen.blit(self.sprite1d, (g.ship[0][0] + 1001, g.ship[0][1] - 22))
            self.dir[0] = 'c'
        else:  # if the player is dead draw the explosion sprite
            g.ship[0][1] += 1
            self.screen.blit(self.boom, (g.ship[0][0] - 23, g.ship[0][1] - 25))
            self.screen.blit(self.boom, (g.ship[0][0] - 1047, g.ship[0][1] - 25))
            self.screen.blit(self.boom, (g.ship[0][0] + 1001, g.ship[0][1] - 25))
            if g.notgonnadie == 1:
                g.contdead[0] += 1
        if g.p[1]:
            if self.dir[1] == 'c':
                self.screen.blit(self.sprite2, (g.ship[1][0] - 23, g.ship[1][1] - 25))
                self.screen.blit(self.sprite2, (g.ship[1][0] - 1047, g.ship[1][1] - 25))
                self.screen.blit(self.sprite2, (g.ship[1][0] + 1001, g.ship[1][1] - 25))
            if self.dir[1] == 'e':
                self.screen.blit(self.sprite2e, (g.ship[1][0] - 23, g.ship[1][1] - 22))
                self.screen.blit(self.sprite2e, (g.ship[1][0] - 1047, g.ship[1][1] - 22))
                self.screen.blit(self.sprite2e, (g.ship[1][0] + 1001, g.ship[1][1] - 22))
            if self.dir[1] == 'd':
                self.screen.blit(self.sprite2d, (g.ship[1][0] - 23, g.ship[1][1] - 22))
                self.screen.blit(self.sprite2d, (g.ship[1][0] - 1047, g.ship[1][1] - 22))
                self.screen.blit(self.sprite2d, (g.ship[1][0] + 1001, g.ship[1][1] - 22))
            self.dir[1] = 'c'
        else:
            g.ship[1][1] += 1
            self.screen.blit(self.boom, (g.ship[1][0] - 23, g.ship[1][1] - 25))
            self.screen.blit(self.boom, (g.ship[1][0] - 1047, g.ship[1][1] - 25))
            self.screen.blit(self.boom, (g.ship[1][0] + 1001, g.ship[1][1] - 25))
            if g.notgonnadie == 2:
                g.contdead[1] += 1
        if g.full == True:
            if g.p[2]:
                if self.dir[2] == 'c':
                    self.screen.blit(self.sprite3, (g.ship[2][0] - 23, g.ship[2][1] - 25))
                    self.screen.blit(self.sprite3, (g.ship[2][0] - 1047, g.ship[2][1] - 25))
                    self.screen.blit(self.sprite3, (g.ship[2][0] + 1001, g.ship[2][1] - 25))
                if self.dir[2] == 'e':
                    self.screen.blit(self.sprite3e, (g.ship[2][0] - 23, g.ship[2][1] - 22))
                    self.screen.blit(self.sprite3e, (g.ship[2][0] - 1047, g.ship[2][1] - 22))
                    self.screen.blit(self.sprite3e, (g.ship[2][0] + 1001, g.ship[2][1] - 22))
                if self.dir[2] == 'd':
                    self.screen.blit(self.sprite3d, (g.ship[2][0] - 23, g.ship[2][1] - 22))
                    self.screen.blit(self.sprite3d, (g.ship[2][0] - 1047, g.ship[2][1] - 22))
                    self.screen.blit(self.sprite3d, (g.ship[2][0] + 1001, g.ship[2][1] - 22))
                self.dir[2] = 'c'
            else:
                g.ship[2][1] += 1
                self.screen.blit(self.boom, (g.ship[2][0] - 23, g.ship[2][1] - 25))
                self.screen.blit(self.boom, (g.ship[2][0] - 1047, g.ship[2][1] - 25))
                self.screen.blit(self.boom, (g.ship[2][0] + 1001, g.ship[2][1] - 25))
                if g.notgonnadie == 3:
                    g.contdead[2] += 1
            if g.p[3]:
                if self.dir[3] == 'c':
                    self.screen.blit(self.sprite4, (g.ship[3][0] - 23, g.ship[3][1] - 25))
                    self.screen.blit(self.sprite4, (g.ship[3][0] - 1047, g.ship[3][1] - 25))
                    self.screen.blit(self.sprite4, (g.ship[3][0] + 1001, g.ship[3][1] - 25))
                if self.dir[3] == 'e':
                    self.screen.blit(self.sprite4e, (g.ship[3][0] - 23, g.ship[3][1] - 22))
                    self.screen.blit(self.sprite4e, (g.ship[3][0] - 1047, g.ship[3][1] - 22))
                    self.screen.blit(self.sprite4e, (g.ship[3][0] + 1001, g.ship[3][1] - 22))
                if self.dir[3] == 'd':
                    self.screen.blit(self.sprite4d, (g.ship[3][0] - 23, g.ship[3][1] - 22))
                    self.screen.blit(self.sprite4d, (g.ship[3][0] - 1047, g.ship[3][1] - 22))
                    self.screen.blit(self.sprite4d, (g.ship[3][0] + 1001, g.ship[3][1] - 22))
                self.dir[3] = 'c'
            else:
                g.ship[3][1] += 1
                self.screen.blit(self.boom, (g.ship[3][0] - 23, g.ship[3][1] - 25))
                self.screen.blit(self.boom, (g.ship[3][0] - 1047, g.ship[3][1] - 25))
                self.screen.blit(self.boom, (g.ship[3][0] + 1001, g.ship[3][1] - 25))
                if g.notgonnadie == 4:
                    g.contdead[3] += 1

    # render shots sprites, but first move them in the game
    def laser(self):
        for l in range(32):  # the game supports 32 laser coordenates
            for p in range(4):  # 4 players
                if i.bt:  # since the shots must move slower when the game is in bulet time
                    if i.gotitem[p] == 2:  # if the player has the bullet time item
                        g.shotpy[p][l] -= g.velogame + 4
                    else:  # for the others
                        g.shotpy[p][l] -= 4
                else:  # when bullet time is off
                    g.shotpy[p][l] -= g.velogame + 4
            self.screen.blit(self.shot1, (g.shotpx[0][l], g.shotpy[0][l]))
            self.screen.blit(self.shot2, (g.shotpx[1][l], g.shotpy[1][l]))
            self.screen.blit(self.shot3, (g.shotpx[2][l], g.shotpy[2][l]))
            self.screen.blit(self.shot4, (g.shotpx[3][l], g.shotpy[3][l]))

    # draw the aliens in screen if they're alive in their respective color or if they're dead draw explosion sprite and item
    def alien(self):
        for t in range(32):  # 32 aliens
            if g.x[t] == 0:  # if it is alive
                if g.spritechange[t] == 0:  # check if it is "red" colored draw its respective sprite
                    self.screen.blit(self.monster1, (g.monsters[0][t], g.monsters[1][t]))
                elif g.spritechange[t] == 1:
                    self.screen.blit(self.monster2, (g.monsters[0][t], g.monsters[1][t]))
                elif g.spritechange[t] == 2:
                    self.screen.blit(self.monster3, (g.monsters[0][t], g.monsters[1][t]))
                elif g.spritechange[t] == 3:
                    self.screen.blit(self.monster4, (g.monsters[0][t], g.monsters[1][t]))
            elif g.x[t] == 1 and i.itemlist[t] == 0:  # if it is dead and don't have any item on it draw explsion sprite
                self.screen.blit(self.boom, (g.monsters[0][t], g.monsters[1][t]))
                # move it depending of bullet time
                if i.bt:
                    g.monsters[1][t] += 1
                else:
                    g.monsters[1][t] = g.monsters[1][t] + g.velogame
            # if the alien has an item, render it
            if i.itemlist[t] != 0 and g.x[t] != 0:
                i.itemshow[t] = 1
                i.itemfall(t)
            # move aliens if they're alive
            if g.contboom[t] >= 100 and g.x[t] == 0:
                if i.bt:
                    g.monsters[1][t] += 1
                else:
                    g.monsters[1][t] = g.monsters[1][t] + g.velogame
            elif g.monsters[1][t] >= 770 or (g.contboom[t] >= 100 and g.x[t] == 1):
                g.x[t] = 0
                g.monsters[1][t] = -26
            if g.monsters[1][t] > 769:
                g.x[t] = 0
                g.monsters[1][t] = -26

    # input configurations screen, this function is only for drawing
    def configscreen(self, player, cursor):  # it needs the current player and where is the cursor
        cursorimg = pygame.Surface((200, 50))  # creates a surface for the cursor
        cursorimg.fill(customgame_auxiliar_function.aux_func(player))  # color it according the current player
        inputs = [str(pygame.key.name(c.udrls[player][0])), str(pygame.key.name(c.udrls[player][1])),
                  str(pygame.key.name(c.udrls[player][2])), str(pygame.key.name(c.udrls[player][3])),
                  str(pygame.key.name(c.udrls[player][4]))]  # get the name of current controls in string format
        if lang:  # if the selected language was brazilian portuguese the input names must be translated since pygame return the key names in english
            for entrada in range(5):  # 5 strings
                inputs[entrada] = customgame_auxiliar_function.aux_name(inputs[entrada])
        self.screen.blit(self.config, (0, 0))  # draw the configurations screen image
        self.screen.blit(cursorimg, ((cursor * 200) + 10, 600))  # draw cursor
        # now i create the surfaces to of text in TrueType font
        # first for displaying which player
        fontinput = pygame.font.Font('font.ttf', 80)
        if lang:
            editing = fontinput.render('Jogador ' + str(player + 1), True,
                                       (customgame_auxiliar_function.aux_func(player)))
        else:
            editing = fontinput.render('Player ' + str(player + 1), True,
                                       (customgame_auxiliar_function.aux_func(player)))
        self.screen.blit(editing, (310, 78))
        # second for displaying instructions
        howtofont = pygame.font.Font('font.ttf', 20)
        if lang:
            howto1 = howtofont.render('Pressione "ENTER" para mudar um comando', True, (0, 0, 0))
        else:
            howto1 = howtofont.render('Press "RETURN" to change a comand input', True, (0, 0, 0))
        if lang:
            howto2 = howtofont.render('Pressione "ESC" salvar novos camandos e retornar ao menu', True, (0, 0, 0))
        else:
            howto2 = howtofont.render('Press "ESC" to save the new comand inputs and return to the menu', True,
                                      (0, 0, 0))
        self.screen.blit(howto1, (10, 730))
        self.screen.blit(howto2, (10, 746))
        # now to finnaly draw the current inputs
        for o in range(5):
            inputfont = pygame.font.Font('font.ttf', 30)
            edit = inputfont.render(inputs[o], True, (customgame_auxiliar_function.aux_func(player)))
            self.screen.blit(edit, ((200 * o) + 10, 550))
        pygame.display.flip()

    # draw the credits screen, this function unlike the above one, is independant, has its own loop
    def creditsscreen(self):
        pygame.mixer.music.set_volume(0.5)  # reduce the music volume t0 50% for effect
        showcredits = True  # variable to know when to break the loop below
        creditsy = 200  # set an initial position to put the credits image
        self.screen.fill((255, 255, 255))  # fill the screen with color white(RGB 255,255,255)
        while showcredits == True:
            pygame.event.pump()
            keyinput = pygame.key.get_pressed()  # get pressed keys
            creditsy -= 2  # move credits image
            if keyinput[K_ESCAPE]:
                showcredits = False  # so it will break the loop
                pygame.mixer.music.set_volume(1.0)  # set music volume back to 100%
                m.selected = 0  # see class "menu"
            if keyinput[K_UP]:
                creditsy -= 4  # move credits image up
            if keyinput[K_DOWN]:
                creditsy += 4  # move it down
            if creditsy < -4542:  # limit to stop moving credits image
                creditsy = -4542
            self.screen.blit(self.credit, (0, creditsy))  # draw credits image
            pygame.display.flip()  # update screen
            g.clock.tick(15)  # set framerate to 15fps

    def createendgamesurfaces(self):
        if g.end == 0:  # tie
            self.font = pygame.font.Font('font.ttf', 60)
            if lang:
                self.winnersurface = self.font.render('SEM VENCEDOR', True, (255, 255, 255))
            else:
                self.winnersurface = self.font.render('NO WINNER', True, (255, 255, 255))
        else:
            self.font = pygame.font.Font('font.ttf', 60)
            if lang:
                self.winnersurface = self.font.render('JOGADOR ' + str(g.end) + ' VENCE!', True,
                                                      customgame_auxiliar_function.aux_func(g.end - 1))
            else:
                self.winnersurface = self.font.render('PLAYER ' + str(g.end) + ' WINS!', True,
                                                      customgame_auxiliar_function.aux_func(g.end - 1))
            fontfinalscore = pygame.font.Font('font.ttf', 30)
            if lang:
                self.finalscoresurface = fontfinalscore.render('sua pontuacao final foi:' + str(g.finalscore), True,
                                                               customgame_auxiliar_function.aux_func(
                                                                   g.end - 1))  # the message depends on the language selected
            else:
                self.finalscoresurface = fontfinalscore.render('  your final score were:' + str(g.finalscore), True,
                                                               customgame_auxiliar_function.aux_func(g.end - 1))
            self.createsurfaces = 2


if lang:
    print 'classe "render" carregada'
else:
    print 'class "render" loaded'
if lang:
    print 'carregando classe "menu"'
else:
    print 'loading class "menu"'


# class responsable for most of menus
class mainmenu:
    tevira = 0
    option = 0  # determine which is the current option on the main menu, cursor location
    selected = 0  # which option has been selected (0 means that no option on the main menu has been selected)
    inf = False  # show or not the instruction screen
    mode = load.lastgamemode  # [0,0,0,0]#game mode for custom matches (0 for human and 1 for CPU)

    # gets and returns the next key pressed (ignores any key that were being hold before reaching this function)
    def input(self):
        pygame.event.clear()
        while 1 == 1:
            p = pygame.event.get(KEYDOWN)
            if p != []:
                x = p[0]
                if x.key != K_RETURN and x.key != K_ESCAPE:  # so it won't set as custom input keys ESCAPE or RETURN
                    return x.key

    # custom inputs screen
    def custominput(self):
        player = 0  # for initial value
        cursor = 0  # for initial value
        out = False  # to know when to break the loop
        while out == False:
            g.clock.tick(15)  # set framerate at 15fps
            r.configscreen(player, cursor)  # update screen
            pygame.event.pump()
            keyinput = pygame.key.get_pressed()  # get current keyboard state
            if keyinput[K_ESCAPE]:
                c.udrls = c.default_input  # set the new input options
                self.selected = 0  # so it will return to the main menu
                out = True  # so it will break the loop
            if keyinput[K_UP]:
                player += 1
                if player > 3:  # so it won't select an invalid player value
                    player = 0
            if keyinput[K_DOWN]:
                player -= 1
                if player < 0:  # so it won't select an invalid player value
                    player = 3
            if keyinput[K_LEFT]:
                cursor -= 1
                if cursor < 0:  # so it won't select an invalid cursor value
                    cursor = 4
            if keyinput[K_RIGHT]:
                cursor += 1
                if cursor > 4:  # so it won't select an invalid cursor value
                    cursor = 0
            if keyinput[K_RETURN]:  # get the new input
                c.udrls[player][cursor] = self.input()
                pygame.event.clear()
                pygame.time.wait(100)
        save.saveconfigurations(c.udrls, self.mode)

    # draw main menu image screen and cursor
    def mainscreen(self):
        r.screen.blit(r.mainmenu, (0, 0))
        self.cursor()
        g.clock.tick(20)
        pygame.display.flip()

    # custom game menu
    def customgame(self):
        aux = False  # auxiliar to brak te loop below
        show = 1  # to choose which background image to draw, to swich between them quickly for an visual effect
        while aux == False:
            if show == 1:
                r.screen.blit(r.customscreen1, (0, 0))
                show = 2  # to draw the other
            elif show == 2:
                r.screen.blit(r.customscreen2, (0, 0))
                show = 1  # to draw the other
            for e in pygame.event.get():  # this is for displaying cursors only when the RETURN key is released, to don't start the game too quickly
                if e.type == KEYUP:
                    if e.key == K_RETURN:
                        aux = True
            pygame.display.flip()
            g.clock.tick(20)
        # creates cursors
        verdana = pygame.font.match_font('Verdana')
        customfont = pygame.font.Font('font.ttf', 50)
        if lang:
            humano = 'HUMANO'
        else:
            humano = 'HUMAN'
        cpu = 'CPU'
        out = False  # other auxiliar to brak the loop
        selector = 0
        cursor = pygame.Surface((248, 50))
        while out == False:
            cursor.fill(
                customgame_auxiliar_function.aux_func(selector))  # so cursor's color follow the player to be edited
            # same from above
            if show == 1:
                r.screen.blit(r.customscreen1, (0, 0))
                show = 2
            elif show == 2:
                r.screen.blit(r.customscreen2, (0, 0))
                show = 1
            for i in range(4):  # to draw "HUMAN" or "CPU" (or nothing) below each player
                if self.mode[i] == 0:  # case the current mode is "HUMAN"
                    txt = customfont.render(humano, True, customgame_auxiliar_function.aux_func(i))
                    r.screen.blit(txt, ((256 * i), 600))
                elif self.mode[i] == 1:  # case the current mode is "CPU"
                    txt = customfont.render(cpu, True, customgame_auxiliar_function.aux_func(i))
                    r.screen.blit(txt, ((256 * i), 600))
            r.screen.blit(cursor, (256 * selector, 700))
            pygame.event.pump()
            keyinput = pygame.key.get_pressed()  # get pressed keys
            if keyinput[K_ESCAPE]:
                self.selected = 0  # to return to the main menu
                out = True  # break the loop
            if keyinput[K_UP]:  # change current mode
                self.mode[selector] += 1
                if self.mode[selector] > 2:  # to allow only 3 alternatives ("HUMAN" "CPU" nothing)
                    self.mode[selector] = 0
            if keyinput[K_DOWN]:  # change current mode
                self.mode[selector] -= 1
                if self.mode[selector] < 0:  # to allow only 3 alternatives ("HUMAN" "CPU" nothing)
                    self.mode[selector] = 2
            if keyinput[K_LEFT]:  # change player to edit
                selector -= 1
                if selector < 0:  # so it won't select an invalid cursor value
                    selector = 3
            if keyinput[K_RIGHT]:  # change player to edit
                selector += 1
                if selector > 3:  # so it won't select an invalid cursor value
                    selector = 0
            if keyinput[K_RETURN]:
                g.horc = self.mode  # set the game mode
                for u in range(4):
                    if self.mode[u] == 2:  # "2" means nothing/dead
                        g.p[u] = False
                g.full = True
                out = True  # to break the loop
            pygame.display.flip()  # update screen on the monitor
            g.clock.tick(20)  # set framerate at 20fps
        save.saveconfigurations(c.udrls, self.mode)

    # instructions screen
    def controlsscreen(self):
        while self.inf == True:
            r.screen.blit(r.infoscreen, (0, 0))  # draw instructions screen
            c.menuinput()  # call special input function
            if lang:  # for the joke previously mentioned
                if self.tevira == 0:
                    r.screen.blit(r.tevira1, (15, 690))
                    self.tevira += 1
                elif self.tevira == 1:
                    r.screen.blit(r.tevira2, (15, 690))
                    self.tevira += 1
                elif self.tevira == 2:
                    r.screen.blit(r.tevira3, (15, 690))
                    self.tevira += 1
                elif self.tevira == 3:
                    r.screen.blit(r.tevira4, (15, 690))
                    self.tevira = 0
            g.clock.tick(10)  # set framerate at 10fps
            pygame.display.flip()  # update screen

    # for the many different cursors in the main screen, draw main menu then the current cursor's image
    def cursor(self):
        c.menuinput()  # call special input function
        if self.option == 0:
            r.screen.blit(r.mainmenu, (0, 0))
            r.screen.blit(r.cursor1, (690, 495))
        elif self.option == 1:
            r.screen.blit(r.mainmenu, (0, 0))
            r.screen.blit(r.cursor2, (680, 530))
        elif self.option == 2:
            r.screen.blit(r.mainmenu, (0, 0))
            r.screen.blit(r.customicon, (700, 565))
        elif self.option == 3:
            r.screen.blit(r.mainmenu, (0, 0))
            r.screen.blit(r.configicon, (700, 605))
        elif self.option == 4:
            r.screen.blit(r.mainmenu, (0, 0))
            r.screen.blit(r.info, (720, 640))
        elif self.option == 5:
            r.screen.blit(r.mainmenu, (0, 0))
            r.screen.blit(r.crediticon, (720, 685))
        elif self.option == 6:
            r.screen.blit(r.mainmenu, (0, 0))
            r.screen.blit(r.quit, (700, 710))


m = mainmenu()
if lang:
    print 'classe "menu" carregada'
else:
    print 'class "menu" loaded'
if lang:
    print 'carregando entradas de comandos'
else:
    print 'loading comands inputs'


# class responsible for most of inputs interpretation
class control:
    udrls = load.oldcontrols  # default_input#this list is for editing; before you start to wonder the name of this list it stands for up (u) down (d) right (r) left (l) shot (s); in sequence player 1, 2, 3, and 4
    joybutton = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0]]  # joypads button states
    joyvert = ['c', 'c', 'c', 'c']  # for analog joypads vertical interpreters
    joyhor = ['c', 'c', 'c', 'c']  # for analog/digital axis joypads horizontal interpreters
    njoy = pygame.joystick.get_count()  # count number of joypads plugged in the computer
    shot = [False, False, False, False]  # shot states
    AI_x = ['c', 'c', 'c', 'c']
    AI_y = ['c', 'c', 'c', 'c']

    # input interpreter of the main menu and instructions screens
    def menuinput(self):
        pygame.event.pump()
        keyinput = pygame.key.get_pressed()  # get keyboard state
        if (keyinput[K_SPACE] or keyinput[K_ESCAPE]) and m.inf == True:  # to leave the instructions screen
            m.inf = False
            m.selected = 0
            m.option = 0
        elif keyinput[K_ESCAPE] or pygame.event.peek(QUIT):  # to close Alien Conquer (ONLY FROM THE MAIN MENU)
            pygame.quit()  # clear memory from pygame's functions/drivers usage (renderizer,audio mixer,keyboard,mouse,joysticks interpreters)
            sys.exit()  # close windows (debugger and main screen)
        if keyinput[K_UP]:  # change option pointed by the cursor
            m.option -= 1
            if m.option < 0:
                m.option = 6
        if keyinput[K_DOWN]:
            m.option += 1
            if m.option > 6:
                m.option = 0
        if keyinput[K_RETURN]:  # set the current option pointed by the cursor as the choosen one
            m.selected = m.option + 1
            if m.inf == False:
                m.inf = True

    # another "all-in-one" function
    def fullinput(self):
        # set the analog interpreters to "center" so the ship won't keep moving after the analog/digital axis is released
        # the names stand for joystick player number vertical/horizontal
        self.shot = [False, False, False, False]
        self.joyhor = ['c', 'c', 'c', 'c']
        self.joyvert = ['c', 'c', 'c', 'c']
        self.AI_x = ['c', 'c', 'c', 'c']
        self.AI_y = ['c', 'c', 'c', 'c']
        pygame.event.clear()
        self.general()  # to quit current running option
        # first check if this player is not supposed to be controled by the artificial inteligence system
        # second check if there is an avalible joypad for this player
        # in last case control this player through the keyboard
        for i in range(4):
            if g.horc[i] == 1:  # AI?
                self.compcommands(i)
            elif self.njoy > i:  # joypad?
                self.joyinterpreter(i)
                self.joy(i)
            else:  # keyboard then
                self.p(i)

    # check if it is not supposed to quit what is currently running
    def general(self):
        pygame.event.pump()
        keyinput = pygame.key.get_pressed()  # get pressed keys
        if pygame.event.peek(QUIT):
            pygame.quit()
            sys.exit(0)
        if (keyinput[K_RETURN] and g.end != 5) or keyinput[
            K_ESCAPE]:  # if a game match is running and ESCAPE is pressed return to the main menu screen
            g.restart = True

    # artificial inteligence commands (the AI system doesn't control the ship, it controls an virtual joypad that controls the ship, meaning: the AI ship moves like an human controled ship)
    def compcommands(self, t):  # t is for the player to control
        aux = False  # auxiliar to deteminate if the player can shoot or not
        if i.bt:  # if the "bullet time" is activated the counter for time between each shot must reach a higher value, if the counter reach the required value the player can shoot
            if i.gotitem[t] == 2 and g.contshot[t] >= 30 - g.velogame:
                aux = True
            elif g.contshot[t] >= 30:
                aux = True
        else:
            if g.contshot[t] >= 30 - g.velogame:
                aux = True
        self.AI_x[t], self.AI_y[t] = ia.run_foo(g.monsters, g.ship[t][0], g.ship[t][1], g.trg[t], g.velogame,
                                                g.x)  # get from the AI system commands  of movement
        s = ia.shoot_foo(g.ship[t][0], g.ship[t][1], g.velogame, g.monsters, g.trg[
            t])  # bool value to know if shoud "press the shoot button" determinated by an specific part of the AI system
        if g.x[g.trg[t]] == 1:  # if the target alien is dead search for an other
            g.trg[t] = ia.aim_foo(g.spritechange, g.x, g.monsters, g.ship[t][0], g.ship[t][1], t)
        if g.p[t] == True:
            if self.AI_x[t] == 'l':  # case the AI movement retuned 'l' (left)
                r.dir[t] = 'e'  # change the ship sprite to "left sprite"
                if (i.gotitem[
                        t] == 2 and i.bt) or i.bt == False:  # if the AI player has caught the "bullet time" item or no one has it (meaning that the bullet time is off)
                    g.ship[t][0] -= g.velogame + 2  # move normaly
                else:  # else
                    g.ship[t][0] -= 2  # move slowly

            if self.AI_x[t] == 'r':
                r.dir[t] = 'd'
                if (i.gotitem[t] == 2 and i.bt) or i.bt == False:
                    g.ship[t][0] += g.velogame + 2
                else:
                    g.ship[t][0] += 2

            if self.AI_y[t] == 'u':
                if (i.gotitem[t] == 2 and i.bt) or i.bt == False:
                    g.ship[t][1] -= g.velogame + 2
                else:
                    g.ship[t][1] -= 2
                if g.ship[t][1] < 25:  # screen vertical limit (top)
                    g.ship[t][1] = 25

            if self.AI_y[t] == 'd':
                if (i.gotitem[t] == 2 and i.bt) or i.bt == False:
                    g.ship[t][1] += g.velogame + 2
                else:
                    g.ship[t][1] += 2
                if g.ship[t][1] > g.altura - 25:  # screen vertical limit (bottom)
                    g.ship[t][1] = g.altura - 25

            if aux:  # if the counter (shot waiting) return an acceptable value
                if s and i.contbeam[
                    t] == 0:  # if s is equal to True (if the AI "virtual joypad" is pressing the shot button) and if this player is not using the "laser canon" item
                    g.laser = True  # so the audio class will play laser noise
                    # change the coordenates of the "next" shot sprite to in front of the ship
                    self.shot[t] = True
                    g.shotpx[t][g.shotp[t]] = g.ship[t][0] - 11
                    g.shotpy[t][g.shotp[t]] = g.ship[t][1] - 50
                    g.contshot[t] = 0  # set the shot waiting counter back to 0
                    g.shotp[t] += 1  # move to the next shot
                    if g.shotp[
                        t] == 32:  # the limit of shots coordenates is 32 (the list goes from 0 to 31), this is to not let it go to an unexisting point of that list (and closing an cicle)
                        g.shotp[t] = 0

    # keyboard interpreter
    def p(self, playern):
        aux = False  # auxiliar for knowing if the player can shoot or not (same logic as in "compcommands" function above)
        if i.bt:
            if i.gotitem[playern] == 2 and g.contshot[playern] >= 30 - g.velogame:
                aux = True
            elif g.contshot[playern] >= 30:
                aux = True
        else:
            if g.contshot[playern] >= 30 - g.velogame:
                aux = True
        pygame.event.pump()
        keyinput = pygame.key.get_pressed()  # get pressed keys
        if g.p[playern] == True:  # check if the palyer is alive
            if keyinput[self.udrls[playern][3]]:  # LEFT
                r.dir[playern] = 'e'  # change sprite to draw
                if (i.gotitem[
                        playern] == 2 and i.bt) or i.bt == False:  # if this player 1 has the bullet time item or no one has it
                    g.ship[playern][0] -= g.velogame + 2  # (move normally)
                else:  # if someone else has it
                    g.ship[playern][0] -= 2  # move slowly

            if keyinput[self.udrls[playern][2]]:  # RIGHT
                r.dir[playern] = 'd'  # change sprite to draw
                if (i.gotitem[playern] == 2 and i.bt) or i.bt == False:
                    g.ship[playern][0] += g.velogame + 2
                else:
                    g.ship[playern][0] += 2

            if keyinput[self.udrls[playern][0]]:  # UP
                if (i.gotitem[playern] == 2 and i.bt) or i.bt == False:
                    g.ship[playern][1] -= g.velogame + 2
                else:
                    g.ship[playern][1] -= 2
                if g.ship[playern][1] < 25:
                    g.ship[playern][1] = 25

            if keyinput[self.udrls[playern][1]]:  # DOWN
                if (i.gotitem[playern] == 2 and i.bt) or i.bt == False:
                    g.ship[playern][1] += g.velogame + 2
                else:
                    g.ship[playern][1] += 2
                if g.ship[playern][1] > g.altura - 25:
                    g.ship[playern][1] = g.altura - 25

            if aux:  # if the player is allowed to shoot (see beginig of this function)
                if keyinput[self.udrls[playern][4]] and i.contbeam[
                    playern] == 0:  # if the player is pressing the shot key and isn't using the laser canon item
                    g.laser = True  # to play the laser audio
                    self.shot[playern]
                    g.shotpx[playern][g.shotp[playern]] = g.ship[playern][
                                                              0] - 11  # move laser sprite to in front of the ship
                    g.shotpy[playern][g.shotp[playern]] = g.ship[playern][1] - 50
                    g.contshot[playern] = 0  # set shot waiting counter to 0
                    g.shotp[playern] += 1  # move to the next shot
                    if g.shotp[
                        playern] == 32:  # the limit of shots coordenates is 32 (the list goes from 0 to 31), this is to not let it go to an unexisting point of that list (and closing an cicle)
                        g.shotp[playern] = 0

    def joyinterpreter(self, playern):
        if self.njoy > playern:  # check if there really is an avalible joypad for this player
            stick = pygame.joystick.Joystick(playern)
            stick.init()  # initializer pygame's joystick interpreter
            event = pygame.event.poll()
            for i in range(8):  # interpretate the first 8 buttons on an joypad
                if stick.get_button(
                        i) == False:  # if "i" the button in NOT pressed, set the buttons state list position "i" to 0
                    self.joybutton[playern][i] = 0
                if self.joybutton[playern][
                    i] == 1:  # if it is pressed set to 0 too (that way the buttons state list will reset, not allowing an button to be interpretated after being released)
                    self.joybutton[playern][i] = 0
                if stick.get_button(i) == True and g.contshot[
                    playern] >= 30 - g.velogame:  # if the button "i" is pressed AND the shot waiting counter return an acceptable value, then shoot
                    self.joybutton[playern][i] = 1
            # analog sticks interpreter
            # the analog sticks return value between -1 and 1 (0 is for center) since the center value is never precise (example: 0,000135) in the code i ask for a high intensity of it (below -0.5 and above +0.5)
            # (see pygame.org documentation about joysticks)
            if stick.get_axis(1) <= -0.5:  # axis(1) is the vertical axis of the analog stick
                self.joyvert[playern] = 'u'  # up
            elif stick.get_axis(1) >= 0.5:
                self.joyvert[playern] = 'd'  # down
            if stick.get_axis(0) <= -0.5:  # axis(1) is the horizontal axis of the analog stick
                self.joyhor[playern] = 'l'  # left
            elif stick.get_axis(0) >= 0.5:
                self.joyhor[playern] = 'r'  # right
            # hat interpreter, it returns values -1, 0 or +1 ONLY
            # "hat" is the digital directional buttons (dpad)
            joyx, joyy = stick.get_hat(0)
            if joyx > 0:  # horizontal axis
                self.joyhor[playern] = 'r'  # right
            elif joyx < 0:  # horizontal axis
                self.joyhor[playern] = 'l'  # left
            if joyy > 0:  # vertical axis
                self.joyvert[playern] = 'u'  # up
            elif joyy < 0:  # vertical axis
                self.joyvert[playern] = 'd'  # down
            stick.quit()  # shut pygame's joystick interpreter's down so that in the next time this function is called its variable will be reseted

    def joy(self, playern):
        # you know the drill (see "compcommands" above)
        aux = False
        if i.bt:
            if i.gotitem[playern] == 2 and g.contshot[playern] >= 30 - g.velogame:
                aux = True
            elif g.contshot[playern] >= 30:
                aux = True
        else:
            if g.contshot[playern] >= 30 - g.velogame:
                aux = True
        if g.p[playern] == True:  # check if it is still alive
            if self.joyhor[playern] == 'l':  # see "joyp1interpreter" above
                r.dir[playern] = 'e'  # change sprite
                # bullet time delay or not for movement
                if (i.gotitem[playern] == 2 and i.bt) or i.bt == False:
                    g.ship[playern][0] -= g.velogame + 2
                else:
                    g.ship[playern][0] -= 2

            if self.joyhor[playern] == 'r':  # see "joyp1interpreter" above
                r.dir[playern] = 'd'
                if (i.gotitem[playern] == 2 and i.bt) or i.bt == False:
                    g.ship[playern][0] += g.velogame + 2
                else:
                    g.ship[playern][0] += 2

            if self.joyvert[playern] == 'u':  # see "joyp1interpreter" above
                if (i.gotitem[playern] == 2 and i.bt) or i.bt == False:
                    g.ship[playern][1] -= g.velogame + 2
                else:
                    g.ship[playern][1] -= 2
                if g.ship[playern][1] < 25:
                    g.ship[playern][1] = 25

            if self.joyvert[playern] == 'd':  # see "joyp1interpreter" above
                if (i.gotitem[playern] == 2 and i.bt) or i.bt == False:
                    g.ship[playern][1] += g.velogame + 2
                else:
                    g.ship[playern][1] += 2
                if g.ship[playern][1] > g.altura - 25:
                    g.ship[playern][1] = g.altura - 25

            for n in range(8):  # check if in any point of the joypad buttons state list is an pressed button
                if self.joybutton[playern][n] == 1:
                    self.shot[playern] = True  # if there is it means that the player is trying to shoot
            if aux == True and self.shot[playern] == True and i.contbeam[
                playern] == 0:  # if it can shoot, want to shoot and is not using the "laser canon" item, SHOOT
                g.laser = True
                g.shotpx[playern][g.shotp[playern]] = g.ship[playern][0] - 11
                g.shotpy[playern][g.shotp[playern]] = g.ship[playern][1] - 50
                g.contshot[playern] = 0
                g.shotp[playern] += 1
                if g.shotp[playern] == 32:
                    g.shotp[playern] = 0
                # self.shot[playern] = False#reset the shoot or not state


c = control()
if lang:
    print 'entradas de comandos carregadas'
else:
    print 'comands inputs loaded'
if lang:
    print 'carregando itens'
else:
    print 'loading itens'


# class responsible for item management
# observation: this is not working 100%, so i'm working on it, so it may get confusing
class item:
    itemlist = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0]  # to know wher the item is
    itemshow = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0]  # to know where to draw it
    itemx = 0  # coordenate x of the item's position
    itemy = 0  # coordenate y of the item's position
    gotitem = [0, 0, 0, 0]  # to know who has the current item
    a = random.randint(0, 31)  # initial alien to receive an item
    caught = 0  # to know who caught the last item
    contbeam = [0, 0, 0, 0]  # timer for the laser canon
    bt = False  # if the bullet time is in effect
    contbt = 0  # timer for laser canon
    selected = random.randint(1, 2)  # choose which item the selected alien will receive
    itemsprite = 0  # similar to "contboost", is a couter to choose which item sprite to draw
    posali2positm = False  # auxiliar to determinate if the alien's position has been passed to the item's positio, it's supposed to be used only when the alien that is holding an item dies

    # function to deactivate the laser canon
    def lasercanonoff(self, i):
        a.lasercanon.stop()  # stop the audio
        # reset item stats involving players and aliens
        self.gotitem[i] = 0
        self.caught = 0
        self.contbeam[i] = 0
        for h in range(32):
            self.itemlist[h] = 0
            self.itemshow[h] = 0
        # choose new alien and item
        self.a = random.randint(0, 31)
        self.select1()

    # function to deactivate teh bullet time
    def bullettimeoff(self):
        if self.contbt == 95:  # when near to end the bullet time
            a.btoff.play()  # play "bullet time off" sound effect
        if self.contbt == 119:  # when it finishes
            pygame.mixer.music.set_volume(1.0)  # set music volume back to normal

    # another "all-in-one" function
    def fullitem(self):
        self.select1()
        self.bullettimeoff()

    # function that chooses new alien to hold an item
    def select1(self):
        self.posali2positm = False
        self.caught = 0  # means that no player is using an item
        ok = False  # auxiliar to break the loop
        while ok == False:
            if g.x[
                self.a] == 0:  # check if the selected alien is dead or alive, if it is alive just choose another type of item for the new alien that hold an item
                if self.selected == 2:
                    self.selected = 1
                    self.itemlist[self.a] = 1
                elif self.selected == 1:
                    self.selected = 2
                    self.itemlist[self.a] = 2
                ok = True
            else:  # if it is dead randomly choose an other alien to hold an item
                self.a = random.randint(0, 31)

    # function responsable for determinating beam's position, sprite and rendering it
    def beam(self):
        for u in range(4):
            if g.p[u]:
                if self.contbeam[u] < 120 and self.gotitem[u] == 1:
                    self.itemx = -50
                    self.itemy = -50
                    x = g.ship[u][0] - 32
                    y = g.ship[u][1] - 780
                    r.screen.blit(r.beam[u], (x, y))
                    self.contbeam[u] += 1
                    for j in range(32):
                        if (x >= g.monsters[0][j] - 64 and x <= g.monsters[0][j] + 34) and (
                                y >= g.monsters[1][j] - 750 and y <= g.monsters[1][j] + 20) and g.x[j] == 0 and g.p[u]:
                            g.x[j] = 1
                            if g.spritechange[j] == u:
                                g.score[u] += 10
                            else:
                                g.score[u] += 20
                            g.alien = True
                            g.contboom[j] = 0
                            if self.itemlist[j] != 0:
                                self.dropitem(j)
                            g.spritechange[j] = u
            if self.contbeam[u] >= 120:
                self.lasercanonoff(u)

    # function responsable for bullet time item management
    def bullettime(self):
        for u in range(4):
            if self.gotitem[u] == 2:
                self.bt = True
                self.contbt += 1
        if self.contbt >= 120:
            for u in range(4):
                self.gotitem[u] = 0
                self.bt = False
                self.contbt = 0
                self.itemx = -50
                self.itemy = -50
                self.caught = 0
                self.contbeam[u] = 0
                for p in range(32):
                    self.itemlist[p] = 0
                    self.itemshow[p] = 0
            self.a = random.randint(0, 31)
            self.select1()

    # function responsable for getting the position of the alien that was carrying the item to draw later the item itself
    def dropitem(self, t):  # "t" is for target, it is the index of the alien that's carrying an item
        self.posali2positm = True
        self.itemshow[t] = self.itemlist[t]  # to show the item in screen later
        self.itemx = g.monsters[0][t]  # pass the carrying's alien position to the item's position
        self.itemy = g.monsters[1][t]

    # function responsable for drawing items in the screen and animate them
    def itemfall(self, t):
        if self.itemy < 790 and self.itemshow[t] == 1:
            if self.gotitem[0] + self.gotitem[1] + self.gotitem[2] + self.gotitem[3] == 0 and self.caught == 0:
                if self.selected == 1:  # for the blue item
                    if self.itemsprite == 0:  # draw first sprite this time
                        r.screen.blit(r.item1a, (self.itemx, self.itemy))
                        self.itemsprite += 1  # to draw the other sprite next time in the function
                    elif self.itemsprite == 1:  # draw second sprite this time
                        r.screen.blit(r.item1b, (self.itemx, self.itemy))
                        self.itemsprite -= 1  # to draw the other sprite next time in the function
                elif self.selected == 2:  # for the red item
                    if self.itemsprite == 0:
                        r.screen.blit(r.item2a, (self.itemx, self.itemy))
                        self.itemsprite += 1
                    elif self.itemsprite == 1:
                        r.screen.blit(r.item2b, (self.itemx, self.itemy))
                        self.itemsprite -= 1
                self.itemy += g.velogame + 1  # move item down according to game speed
                if self.itemy > 780:  # if it falls below the screen consider it as caught to choose another alien to carry it
                    self.itemx = -50
                    self.itemy = -50
                    self.caught = 1
                    self.itemshow[t] = 0
                    self.a = random.randint(0, 31)
                    self.select1()


i = item()
if lang:
    print 'itens carregados'
else:
    print 'itens loaded'
print ''
if lang:
    print 'iniciando Alien Conquer'
else:
    print 'starting Alien Conquer'
r = render()
r.__init__()  # initializes the main window
while 1:
    g.mainloop()  # start the main loop
