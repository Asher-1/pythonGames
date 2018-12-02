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
##the "os" module is for navigating through folders,
##and since the audio, background and sprite files are NOT in the same folder as the execution files
##we're definetly going to need them to access them
import os
##language choosen by the user
import pt_br_english
pt_br = pt_br_english.pt_br

if pt_br: print 'carregando imagens de fundo'
else: print 'loading background images'

##load all background images (brazilian portuguese AND english)
credit = os.path.join('Fundo', 'Creditos_pt-br')
crediteng = os.path.join('Fundo', 'Creditos_english')
setupinput = os.path.join('Fundo', 'Config')
custom1 = os.path.join('Fundo', 'customgame1')
custom2 = os.path.join('Fundo', 'customgame2')
customicon = os.path.join('Objeto', 'custom')
icon = os.path.join('Objeto', 'AC')
bk = os.path.join('Fundo', 'starfiel')
mainm = os.path.join('Fundo', 'Main')
mainmeng = os.path.join('Fundo', 'Main_english')
ciscreen = os.path.join('Fundo', 'controls')
ciscreeneng = os.path.join('Fundo', 'controlsenglish')

if pt_br:
    print 'imagens carregadas'
    print 'carregando icones'
else:
    print 'background images loaded'
    print 'loading icons'

##load sprites
ci = os.path.join('Objeto', 'Info')
booom = os.path.join('Objeto', 'boom')
m1 = os.path.join('Objeto', '1')
m2 = os.path.join('Objeto', '2')
m3 = os.path.join('Objeto', '3')
m4 = os.path.join('Objeto', '4')
csr1 = os.path.join('Objeto', '2players')
csr2 = os.path.join('Objeto', '4players')
qt = os.path.join('Objeto', 'quit')
l1 = os.path.join('Objeto', 'laser1')
l2 = os.path.join('Objeto', 'laser2')
l3 = os.path.join('Objeto', 'laser3')
l4 = os.path.join('Objeto', 'laser4')
bst1 = os.path.join('Objeto', 'boostred')
bst2 = os.path.join('Objeto', 'boostyellow')
tv1 = os.path.join('Objeto', 'tevira1')
tv2 = os.path.join('Objeto', 'tevira2')
tv3 = os.path.join('Objeto', 'tevira3')
tv4 = os.path.join('Objeto', 'tevira4')
i1a = os.path.join('Objeto', 'item11')
i1b = os.path.join('Objeto', 'item12')
i2a = os.path.join('Objeto', 'item21')
i2b = os.path.join('Objeto', 'item22')
bm1 = os.path.join('Objeto', 'beamp1')
bm2 = os.path.join('Objeto', 'beamp2')
bm3 = os.path.join('Objeto', 'beamp3')
bm4 = os.path.join('Objeto', 'beamp4')
credicon = os.path.join('Objeto', 'creditos')
config = os.path.join('Objeto', 'configuration')

if pt_br:
    print 'icones carregados'
    print 'carregando naves'
else:
    print 'icons loaded'
    print 'loading ships'
    
##load the ships sprites
sc1 = os.path.join('Naves', 'ship1_center')
sc2 = os.path.join('Naves', 'ship2_center')
sc3 = os.path.join('Naves', 'ship3_center')
sc4 = os.path.join('Naves', 'ship4_center')
se1 = os.path.join('Naves', 'ship1_esq')
se2 = os.path.join('Naves', 'ship2_esq')
se3 = os.path.join('Naves', 'ship3_esq')
se4 = os.path.join('Naves', 'ship4_esq')
sd1 = os.path.join('Naves', 'ship1_dir')
sd2 = os.path.join('Naves', 'ship2_dir')
sd3 = os.path.join('Naves', 'ship3_dir')
sd4 = os.path.join('Naves', 'ship4_dir')

if pt_br:
    print 'naves carregadas'
    print 'carregando audio'
else:
    print 'ships loaded'
    print 'loading audio'

##load all audio
lc = os.path.join('Som', 'laser canon.wav')
lsr = os.path.join('Som', 'laser.wav')
aln = os.path.join('Som', 'alien.wav')
d = os.path.join('Som', 'die.wav')
bon = os.path.join('Som', 'bton.wav')
boff = os.path.join('Som', 'btoff.wav')
menumusic = os.path.join('Som', 'menu.mp3')
gamemusic = os.path.join('Som', 'audio.mp3')

if pt_br: print 'audio carregado'
else: print 'audio loaded'
if pt_br: print 'carregando animacoes'
else: print 'loading animations'

##load the respawn animation sprites and organize them in lists
respawn1 = [os.path.join('Respawn', 'respawn11'),os.path.join('Respawn', 'respawn12'),os.path.join('Respawn', 'respawn13'),os.path.join('Respawn', 'respawn14')]
respawn2 = [os.path.join('Respawn', 'respawn21'),os.path.join('Respawn', 'respawn22'),os.path.join('Respawn', 'respawn23'),os.path.join('Respawn', 'respawn24')]
respawn3 = [os.path.join('Respawn', 'respawn31'),os.path.join('Respawn', 'respawn32'),os.path.join('Respawn', 'respawn33'),os.path.join('Respawn', 'respawn34')]
respawn4 = [os.path.join('Respawn', 'respawn41'),os.path.join('Respawn', 'respawn42'),os.path.join('Respawn', 'respawn43'),os.path.join('Respawn', 'respawn44')]

if pt_br: print 'animacoes carregadas'
else: print 'animations loaded'
if pt_br: print 'carregando configuracoes'
else: print 'loading configurations'

##OBS: the "null" variable below is just to skip the parts of file that have no importance for the software itself (open configuracoes.dat you'll get it)
lastconfigfile = open('configuracoes.dat','r')#open the file
oldcontrols = [range(5),range(5),range(5),range(5)]#just to create the commands list
##start loading
for u in range(4):#4 players
    for i in range(5):#5 commands
        oldcontrols[u][i] = int(lastconfigfile.read(3))#get the key value
        null = lastconfigfile.read(1)
    null = lastconfigfile.read(14)
lastgamemode = range(4)#create the 
for f in range(4):#4 players
    lastgamemode[f] = int(lastconfigfile.read(1))#get mode value
    null = lastconfigfile.read(1)
lastconfigfile.close()

if pt_br: print 'configuracoes carregadas'
else: print 'configurations loaded'
