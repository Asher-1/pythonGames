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
import pt_br_english
def test_pygame():
    try:
        import pygame
        del pygame
        return True
    except ImportError:
        if pt_br_english.pt_br:
            print 'Erro!'
            print ''
            print 'Biblioteca PyGame não instalada!'
            print ''
            print 'Acompanha com o jogo um atalho'
            print 'para a página da internet:'
            print '"www.pygame.org"'
            print 'Favor instalar a biblioteca PyGame para a sua versão de Linux.'
            print 'Sinto muito pelo incomodo.'
        else:
            print 'Error!'
            print ''
            print 'Library PyGame not instaled!'
            print ''
            print 'With this game follows an link'
            print 'to the internet page:'
            print '"www.pygame.org"'
            print 'Please install the PyGame library for your Linux version.'
            print 'Sorry for the inconvenience.'
        return False
