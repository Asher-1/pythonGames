'''grid.py - glorified dictionary'''


class CellBlocked(Exception):
    pass


class Grid(object):
    
    def __init__(self):
        self.cells = {}

    def __getitem__(self, key):
        if key in self.cells:
            return self.cells[key]
        else:
            return self.default

    def __setitem__(self, key, value):
        self.cells[key] = value
        return True

    def __delitem__(self, key):
        if key in self.cells:
            del self.cells[key]

    def __iter__(self):
        return self.cells.iteritems()

    def fill(self, pos, dim, cell):
        for i in xrange(pos[0], dim[0]):
            for j in xrange(pos[1], dim[1]):
                self.cells[i, j] = cell
        return self

    def size(self):
        top = [0, 0]
        bottom = [1, 1]
        for x, y in self.cells:
            top[0] = min(top[0], x)
            top[1] = min(top[1], y)
            bottom[0] = max(bottom[0], x+1)
            bottom[1] = max(bottom[1], y+1)

        pos = (top[0], top[1])
        dim = (bottom[0]-top[0], bottom[1]-top[1])

        return pos, dim


class PlatformGrid(Grid):
    default = (False, False)
    
    def __init__(self, w, h):
        Grid.__init__(self)
        self.w = w
        self.h = h
        self.reset_reachability()
        self.locked = False
        self.calculate_reachability()
        self.dirty = True
 
    def __setitem__(self, key, value):
        self.dirty = True
        Grid.__setitem__(self, key, value)
        if not self.locked:
            self.calculate_reachability()

    def __delitem__(self, key):
        Grid.__delitem__(self, key)
        if not self.locked:
            self.calculate_reachability()

    def mark_clean(self):
        self.dirty = False

    def lock(self): # call this to make big updates to the grid all at once
        self.locked = True
        
    def unlock(self):
        self.locked = False # locks are not reentrant!
        self.calculate_reachability()

    def add_platform(self, pos=(0, 0), len=0):
        for i in xrange(pos[0], pos[0]+len):
            cell = self[i, pos[1]]
            self[i, pos[1]] = (True, cell[1])

    def add_ladder(self, pos=(0, 0), len=0):
        for j in xrange(pos[1], pos[1]+len):
            cell = self[pos[0], j]
            self[pos[0], j] = (cell[0], True)

    def cell_has_floor(self, pos):
        if self[pos[0],pos[1]-1][0]: return True # platform in cell below
        if pos[1] <= 0: return True # bottom of screen
        return False

    def cell_has_ladder(self, pos):
        return self[pos][1]

    def cell_supported(self, pos):
        return self.cell_has_floor(pos) or self[pos][1] # ladder in cell

    def connected_cells(self, pos):
        cx, cy = pos
        on_platform = self.cell_has_floor(pos)
        on_ladder = self[pos][1] # this cell is ladder
        res = set()
        if on_platform:
            if self.cell_has_floor((cx-1,cy)) and cx > 0: res.add((cx-1,cy))
            if self.cell_has_floor((cx+1,cy)) and cx < self.w: res.add((cx+1,cy))
            if self[cx,cy-1][1]: res.add((cx,cy-1)) # can climb down onto ladder
        if on_ladder:
            if self[cx,cy-1][1]: res.add((cx,cy-1))
            if self[cx,cy+1][1]: res.add((cx,cy+1))
            if self.cell_has_floor((cx,cy+1)): res.add((cx,cy+1)) # can climb up onto platform
        return res
        
    def reset_reachability(self):
        self.colours = Grid()
        self.colours.default = None
        
    def calculate_reachability(self):
        self.reset_reachability()
        colour = 1
        for x in xrange(self.w):
            for y in xrange(self.h):
                if self.cell_supported((x,y)) and self.colours[(x,y)] is None:
                    done = set()
                    todo = set([(x,y)])
                    while len(todo):
                        cell = todo.pop()
                        self.colours[cell] = colour
                        done.add(cell)
                        todo.update(self.connected_cells(cell) - done)
                    colour += 1
        
    def reachable(self, pos1, pos2):
        return self.colours[pos1] is not None and self.colours[pos1] == self.colours[pos2]
    
    def platform_dict(self):
        plats = dict()
        platstart = None
        for v in xrange(self.h):
            for u in xrange(self.w):
                if self[u,v][0]:
                    if not platstart:
                        platstart = (u,v)
                        plats[platstart] = 1
                    else:
                        plats[platstart] += 1
                else:
                    platstart = None
            platstart = None 
        return plats


class MachineGrid(Grid):
    default = None

    def add_part(self, part):
        x, y = part.pos
        for i, j in part.region:
            if self[x+i, y+j]: raise CellBlocked
        for i, j in part.region:
            self[x+i, y+j] = part

    def remove_part(self, part):
        x, y = part.pos
        for i, j in part.region:
            self[x+i, y+j] = None
