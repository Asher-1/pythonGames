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
##by this point you should understand what "pt_be_english" and "lang" are
import pt_br_english
lang = pt_br_english.pt_br
if lang: print 'carregando funcoes para salvar configuracoes'
else: print 'loading configurations save functions'

##just to make sure instead of saving "32" it saves "032"
##I need an simetry of the configuracoes.dat content
def strkeyvalue(command):
    comm = str(command)
    while len(comm) < 3:
        comm = '0' + str(command)
    return comm

##the actually saving
##you'll notice it saves dinamicly to avoid repeating too much
def saveconfigurations(controls,gamemode):
    saveconfigfile = open('configuracoes.dat','w')
    ##controls
    for i in range(4):
        for u in range(5):
            saveconfigfile.write(strkeyvalue(controls[i][u]))
            if u < 4:
                saveconfigfile.write(',')
            else:
                saveconfigfile.write(' controles p' + str(i+1) + ':' + '\n')
    ##game mode
    for d in range(4):
        saveconfigfile.write(str(gamemode[d]))
        if d < 3:
            saveconfigfile.write(',')
        else:
            saveconfigfile.write('             modo de jogo:' + '\n')
    saveconfigfile.close()
if lang: print 'funcoes para salvar configuracoes carregadas'
else: print 'configurations save functions loaded'