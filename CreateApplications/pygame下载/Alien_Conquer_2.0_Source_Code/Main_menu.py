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
##load the language module
import pt_br_english

##the first menu of the game still in the debugger screen
print 'Seja Bem Vindo a Alien Conquer 2.0'
print 'Welcome to Alien Conquer 2.0'
print 'copyright (C) 2008 Taiua Pires'
print ''
print 'escolha um idioma - choose a language'
print '"P" para portugues brasileiro'
print '"E" for english'
BorE = False
while not BorE:
    ##get an input
    choice = 'E'

    ##check if the user have choosen an availible option
    if choice == 'P' or choice == 'p' or choice == 'E' or choice == 'e':
        BorE = True
    else:
        print 'favor pressionar "P" para portugues brasileiro'
        print 'please press "E" for english'
if choice == 'P' or choice == 'p':
    pass
elif choice == 'E' or choice == 'e':
    ##change the bool pt_br to "False" so that all the other Alien Conquer modules will use english language
    pt_br_english.pt_br = False
import Pygame_teste

if Pygame_teste.test_pygame() == True:
    import Alien_Conquer
else:
    pass
