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
##this module returns the direction to chase for the artificial inteligence system
##not much to explain here, it basicly move toward the alien
def chase(mx,my,sx,sy):#(coordenate x of the alien to chase,coordenate y of the alien to chase,coordenate x of the ship,coordenate y of the ship)
    dx = 'c'
    dy = 'c'
    if mx > sx:
        dx = 'r'
    elif mx < sx:
        dx = 'l'
    if my > sy:
        dy = 'd'
    elif my < sy:
        dy = 'u'
    return dx,dy