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
##load selected language
import pt_br_english
pt_br = pt_br_english

if pt_br: print 'carregando funcoes auxiliares'
else: print 'loading auxiliar functions'

##this function is only to return the RGB for each player
##it is used to define the color of TrueTypeFonts and to decide the color of certain surfaces
def aux_func(x):
    if x == 0:
        return (255,0,0)
    elif x == 1:
        return (0,0,255)
    elif x == 2:
        return (255,255,0)
    elif x == 3:
        return (0,255,0)

##this function is to translate the key names on the keyboard
##pygame can return the name of a key as a string but only in english so i use it to return a name in brazilian portuguese using a database
##this function is only called if the language selected is pt-br (if pt_br_english.pt_br is True)
def aux_name(x):
    if x == 'right':
        return 'direita'
    elif x == 'left':
        return 'esquerda'
    elif x == 'up':
        return 'cima'
    elif x == 'down':
        return 'baixo'
    elif x == 'left ctrl':
        return 'ctrl da esquerda'
    elif x == 'right ctrl':
        return 'ctrl da direita'
    elif x == 'left shift':
        return 'shift da esquerda'
    elif x == 'right shift':
        return 'shift da direita'
    elif x == 'left meta':
        return 'meta da esquerda'
    elif x == 'right meta':
        return 'meta da direita'
    elif x == 'left alt':
        return 'alt da esquerda'
    elif x == 'right alt':
        return 'alt da direita'
    elif x == 'space':
        return 'espaco'
    elif x[0] == '[':
        return 'NUM ' + str(int(x[1]))
    else:
        return x
if pt_br: print 'funcoes auxiliares carregadas'
else: print 'audio loaded'
