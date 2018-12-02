'''path.py - implementation of pathfinding for elves'''

import math
import heapq

def find_path_i(grid, endpos, currentpath, ignore):
    routes = grid.connected_cells(currentpath[-1]) - ignore
    if not routes: return None
    if endpos in routes: return currentpath+[endpos]
    for r in routes:
        ignore.update([r])
        res = find_path_i(grid, endpos, currentpath+[r], ignore)
        if res is not None: return res

def find_path(grid, startpos, endpos):
    return find_path_i(grid, endpos, [startpos], set([startpos]))
    
def path_heuristic(path, endpos):
    dx = abs(path[-1][0] - endpos[0])
    dy = abs(path[-1][1] - endpos[1])
    return len(path) + dx + dy

def find_best_path(grid, startpos, endpos):
    if not grid.reachable(startpos, endpos):
        return None
    initialpath = [startpos]
    solutions = [(path_heuristic(initialpath, endpos), initialpath)]
    ignore = set()
    while solutions != []:
        nothing, route = heapq.heappop(solutions)
        lastcell = route[-1]
        if not lastcell in ignore:
            if lastcell == endpos:
                return route
            ignore.add(lastcell)
            newcells = grid.connected_cells(route[-1]) - ignore
            for c in newcells:
                newpath = route + [c]
                heapq.heappush(solutions, (path_heuristic(newpath, endpos), newpath))
    return None
