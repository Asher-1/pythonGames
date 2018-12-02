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
import ia
def all_players_inputs_list(commands,keystate,shot,horc,joyvert,joyhor,ai_x,ai_y,number_joysticks):
    full_commands_state = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    for i in range(4):
        if horc[i] == 2:
            pass
        elif horc[i] == 1:
            if ai_y[i] == 'u':
                full_commands_state[i][0] = 1
            elif ai_y[i] == 'd':
                full_commands_state[i][1] = 1
            if ai_x[i] == 'r':
                full_commands_state[i][2] = 1
            elif ai_x[i] == 'l':
                full_commands_state[i][3] = 1
            if shot[i] == True:
                full_commands_state[i][4] = 1
        elif horc[i] == 0:
            if number_joysticks > i:
                if joyvert[i] == 'u':
                    full_commands_state[i][0] = 1
                if joyvert[i] == 'd':
                    full_commands_state[i][1] = 1
                if joyhor[i] == 'r':
                    full_commands_state[i][2] = 1
                if joyhor[i] == 'l':
                    full_commands_state[i][3] = 1
                if shot[i] == True:
                    full_commands_state[i][4] = 1
            else:
                if keystate[commands[i][0]] != 0:
                    full_commands_state[i][0] = 1
                if keystate[commands[i][1]] != 0:
                    full_commands_state[i][1] = 1
                if keystate[commands[i][2]] != 0:
                    full_commands_state[i][2] = 1
                if keystate[commands[i][3]] != 0:
                    full_commands_state[i][3] = 1
                if keystate[commands[i][4]] != 0:
                    full_commands_state[i][4] = 1
    return full_commands_state
    
def ship2ship_colision(ship,p,v,commands,trglist,deadaliens):
    for s in range(4):
        for u in range(4):
            if p[s] == False or p[u] == False:
                pass
            elif s == u:
                pass
            else:
                if ship[s][0] in range(ship[u][0]-47,ship[u][0]+47) and ship[s][1] in range(ship[u][1]-52,ship[u][1]+52):
                    if ship[s][0] in range(ship[u][0]-47,ship[u][0]):
                        if commands[s][2] == 1 and commands[u][3] == 0:
                            ship[s][0] -= (v + 2)/2
                            ship[u][0] += v + 2
                        elif commands[s][2] == 1 and commands[u][3] == 1:
                            ship[s][0] -= (v + 2)/2
                            ship[u][0] += v + 2
                            trglist[s] = ia.random_trg(deadaliens)
                            trglist[u] = ia.random_trg(deadaliens)
                        else:
                            ship[s][0] -= (v + 2)/2
                            ship[u][0] += v + 2
                    elif ship[s][0] in range(ship[u][0],ship[u][0]+47):
                        if commands[s][3] == 1 and commands[u][2] == 0:
                            ship[s][0] += (v + 2)/2
                            ship[u][0] -= v + 2
                        elif commands[s][3] == 1 and commands[u][2] == 1:
                            ship[s][0] += (v + 2)/2
                            ship[u][0] -= v + 2
                            trglist[s] = ia.random_trg(deadaliens)
                            trglist[u] = ia.random_trg(deadaliens)
                        else:
                            ship[s][0] += (v + 2)/2
                            ship[u][0] -= v + 2
                    if ship[s][1] in range(ship[u][1]-52,ship[u][1]):
                        if commands[s][1] == 1 and commands[u][0] == 0:
                            ship[s][1] -= (v + 2)/2
                            ship[u][1] += v + 2
                        elif commands[s][1] == 1 and commands[u][0] == 1:
                            ship[s][1] -= (v + 2)/2
                            ship[u][1] += v + 2
                        else:
                            ship[s][1] -= (v + 2)/2
                            ship[u][1] += v + 2
                    elif ship[s][0] in range(ship[u][0],ship[u][0]+52):
                        if commands[s][0] == 1 and commands[u][1] == 0:
                            ship[s][1] += (v + 2)/2
                            ship[u][1] -= v + 2
                        elif commands[s][0] == 1 and commands[u][1] == 1:
                            ship[s][1] += (v + 2)/2
                            ship[u][1] -= v + 2
                        else:
                            ship[s][0] += (v + 2)/2
                            ship[u][0] -= v + 2

    return ship, trglist