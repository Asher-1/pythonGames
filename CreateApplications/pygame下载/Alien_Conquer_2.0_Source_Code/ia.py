# -*- coding: UTF-8 -*-
'''
This file is part of Alien Conquer.

Foobar is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Alien Conquer.  If not, see <http://www.gnu.org/licenses/>.
'''
##load language
import pt_br_english
pt_br = pt_br_english.pt_br

if pt_br: print 'carregando inteligencia artificial'
else: print 'loading artificial inteligence'

##load the evade and chase algorithyms
import evade, chase

##load the random modules for random values
import random

##function that makes the AI move
##in resume it says:
##if there is an alien close to you move away
##if there isn't move towards your target
def run_foo(m,sx,sy,trg,v,x):#(the aliens positions,the coordenate x of the AI ship,the coordenate y of the AI ship,the target alien index,the current game speed,the dead aliens list)
    for i in range(32):
        if x[i] == 0:#only consider the alien that are alive 0=alive 1=dead
            ##the evade radius (it uses the game speed to increase the radius)
            if m[0][i] in range(sx - (64+v),sx + (64+v)) and m[1][i] in range(sy - (52+v),sy + (75+v)):
                dirx,diry = evade.evade(m[0][i],m[1][i],sx,sy)
                return dirx,diry
    ##since there is no alien in the evade radius it chases the target alien
    dirx,diry = chase.chase(m[0][int(trg)],m[1][int(trg)],sx,sy)
    return dirx,diry

##the smart shot as i like to call it
##since there is a wait between each shot i prjected this function so that the ai would only shot
##when the target alien would be in range or too far
##it only holds the fire if to make don't need to wait when it get directly below it
def shoot_foo(sx,sy,v,m,trg):#(the coordenate x of the AI ship,the coordenate y of the AI ship,the current game speed,the aliens positions (since it affects the waiting to shoot),the target alien index)
    ##if the target alien is in range, shoot
    if m[0][trg] in range(sx - (15+v),sx + (37+v)) and m[1][trg] in range(sy):
        shotlaser = True
    ##if it is close but not in range, YET, and above the AI(so it actually CAN get close enough), DON'T shoot
    elif m[0][trg] in range(sx - (100+v),sx + (100+v)) and m[1][trg] in range(sy):
        shotlaser = False
    ##if the targer alien is below or too far, shoot freely
    else:
        shotlaser = True
    return shotlaser

##this is the aimming function
def aim_foo(color,dead,m,sx,sy,shipcolor):#(a list of the colors of all aliens,a list of alien that are alive or not,a list of the aliens positions,the coordenate x of the AI ship,the coordenate y of the AI ship,the color of the ship)
    aux = 0
    trg = 32
    ##just so you don't get confused:
    ##first: this loop IS suposed to break off before it is finished
    ##second:the [auxiliar((sx/32)+aux)] makes it consider the "no wall" system if the ship is at the very right and a potential terget is at the very left
    while aux < 32:#because there are 32 aliens
        ##check if the current alien is the color of the AI ship from the ship position
        ##to the right
        if color[auxiliar((sx/32)+aux)]!=shipcolor:
            ##check if it is dead
            if dead[auxiliar((sx/32)+aux)] == 0:
                ##check if it is below or above
                if (m[1][auxiliar((sx/32)+aux)]+26)<=sy:
                    ##now we're sure that that's the closest diferent color alien
                    return auxiliar((sx/32)+aux)
        ##now to the left (same drill)
        elif color[auxiliar((sx/32)-aux)]!=shipcolor:
            if dead[auxiliar((sx/32)-aux)] == 0:
                if (m[1][auxiliar((sx/32)-aux)]+26)<=sy:
                    return auxiliar((sx/32)-aux)
        aux = aux + 1
    ##if ALL alien are the same color as the ship aim to the closest one
    return sx/32

##function for selecting an random target
##this is a prototype for an weak artificial inteligence
def random_trg(dead):
    trg = random.randint(0,31)
    ##although projected to be weak, this random targetting will NOT choose an dead target
    while dead[trg] == 1:
        trg = random.randint(0,31)
    return trg

##this function was made to make the AI use "no wall" system for targetting purposes
##in a cerntain exagerated way it help the AI to visualize not the 32 aliens that YOU see
##but 96 aliens 32 on the left of the screen, 32 IN the screen and 32 on the right
def auxiliar(x):
    if x >= 32:#to the right of the screen
        return x - 32
    elif x < 0:#to the left of the screen
        return x + 32
    else:#IN the screen
        return x

##this is an old (and a bit bugged) aiming system for the AI wich will be used to make different AIs
def aim_foo2(color,m,sx,sy,shipcolor):#(an list of the color of all aliens,the aliens positions,the coordenate x of the AI ship,the coordenate y of the AI ship,the color of the ship)
    ##create an list with 32 positions
    posdist = range(32)#(position distance)
    for i in range(32):
        ##to choose only alien of diferent colors
        if color[i] != shipcolor:
        ##if it IS of an differnt color
            ##algorithym to make an subtraction return an positive number (if it should be a-b or b-a)
            if sx > m[0][i]:x = sx - m[0][i]#"x" is suposed to be the distance betwen an alien an the AI player
            elif sx < m[0][i]:x = m[0][i] - sx#"x" is suposed to be the distance betwen an alien an the AI player
            else:x = 0#"x" is suposed to be the distance betwen an alien an the AI player
        else:x = 1025#if the the alien is of the same color consider as it is too far (for targetting purposes)
        if sy < m[1][i]:x = 1025#if the AI ship is above the alien consider as it is too far (for targetting purposes)
        ##put the calculated distance in the list
        posdist[i] = x
    ##get the lowest number from the calculated distance list
    f = min(posdist)
    ##return the closest alien index
    return (f/32) - 1
if pt_br: print 'inteligencia artificial carregada'
else: print 'artificial inteligence loaded'