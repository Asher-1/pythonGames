"""Implementation of a hexagonal grid"""

import math
import serge.actor
import serge.common
import serge.input
import serge.events
import serge.blocks.layout
import serge.blocks.visualblocks


class OutOfRange(Exception): """The cell was out of range of the grid"""


# Events
E_CELL_LEFT_CLICK = 'cell-left-click'
E_CELL_RIGHT_CLICK = 'cell-right-click'


class HexagonalGrid(serge.common.Loggable):
    """A hexagonal grid

    The grid is referenced by an x, y pair with 0, 0 being the top left.

    """

    _odd_x_neighbour_offsets = [
        (-1, 0), (0, -1), (1, 0), (-1, 1), (0, 1), (1, 1),
    ]
    _even_x_neighbour_offsets = [
        (-1, -1), (0, -1), (1, -1), (-1, 0), (0, 1), (1, 0),
    ]
    _offset_ordinals = [
        'nw', 'n', 'ne', 'sw', 's', 'se',
    ]
    _offset_reversed = {
        'nw': 'se', 'n': 's', 'ne': 'sw', 'sw': 'ne', 's': 'n', 'se': 'nw',
    }
    _points_offsets = [
        (-0.5, -1.0), (0.5, -1.0),
        (1.0, 0.0), (0.5, 1.0),
        (-0.5, 1.0), (-1.0, 0.0),
    ]

    def __init__(self, width, height, hexagon_size=1):
        """Initialise the grid"""
        self.width = width
        self.height = height
        self.hexagon_size = hexagon_size
        self.half_size = math.sqrt(3.0 / 4.0) * self.hexagon_size
        #
        self.grid = []
        self.cell_centers = []
        self.clearGrid()

    def clearGrid(self):
        """Clear the grid"""
        #
        # Initialise the grid
        for y in range(self.height + 1):
            self.grid.append([])
            for x in range(self.width + 1):
                self.grid[-1].append(None)
                px, py = self.getCellLocation(x, y)
                self.cell_centers.append(((px, py), (x, y)))

    def setCell(self, x, y, cell):
        """Set the cell contents"""
        if not self.cellIsInGrid(x, y):
            raise OutOfRange('Cell %s, %s is out of range of the grid' % (x, y))
        #
        self.grid[y][x] = cell

    def getCell(self, x, y):
        """Return the cell contents"""
        if not self.cellIsInGrid(x, y):
            raise OutOfRange('Cell %s, %s is out of range of the grid' % (x, y))
        #
        return self.grid[y][x]

    def cellIsInGrid(self, x, y):
        """Return True if the cell is in the grid"""
        return 0 <= x < self.width and 0 <= y < self.height

    def _getOffsetsForCell(self, x, y):
        """Return the neighbour offsets appropriate for a cell"""
        return self._even_x_neighbour_offsets if x % 2 == 0 else self._odd_x_neighbour_offsets

    def _getOffsetsDictionary(self, x, y):
        """Return a dictionary of offsets for a cell"""
        return dict(zip(self._offset_ordinals, self._getOffsetsForCell(x, y)))

    def getNeighbourLocations(self, x, y):
        """Return the neighbouring cells of a cell"""
        if not self.cellIsInGrid(x, y):
            raise OutOfRange('Cell %s, %s is out of range of the grid' % (x, y))
        #
        # Choose the right offsets
        offsets = self._getOffsetsForCell(x, y)
        #
        neighbours = [(x + dx, y + dy) for dx, dy in offsets if self.cellIsInGrid(x + dx, y + dy)]
        return neighbours

    def getNeighbours(self, x, y):
        """Return the neighbour cells of the specified location"""
        return [self.getCell(cx, cy) for cx, cy in self.getNeighbourLocations(x, y)]

    def getNeighbourLocationsWithin(self, x, y, distance):
        """Return all the neighbour cell locations within a certain distance of the point"""
        if not self.cellIsInGrid(x, y):
            raise OutOfRange('Cell %s, %s is out of range of the grid' % (x, y))
        #
        # Go through all locations and find those within the distance range
        matching_locations = []
        for cx, cy in self.iterLocations():
            cell_distance = self.getCellDistance((x, y), (cx, cy))
            if 1 <= cell_distance <= distance:
                matching_locations.append((cx, cy))
        #
        return matching_locations

    def getNeighbourCellsWithin(self, x, y, distance):
        """Return all the neighbour cells within a certain distance of the point"""
        return [self.getCell(cx, cy) for cx, cy in self.getNeighbourLocationsWithin(x, y, distance)]

    def getRelativeCellCoords(self, x, y, direction):
        """Return the coordinates of the cell at a certain direction from this"""
        dx, dy = self._getOffsetsDictionary(x, y)[direction]
        cx, cy = x + dx, y + dy
        #
        if not self.cellIsInGrid(cx, cy):
            raise OutOfRange('Cell %s, %s would be out of range of the grid' % (x, y))
        else:
            return cx, cy

    def getRelativeCell(self, x, y, direction):
        """Return the cell at a relative offset to this one"""
        return self.getCell(*self.getRelativeCellCoords(x, y, direction))

    def getCellDirection(self, (x, y), (cx, cy)):
        """Get the direction of one cell from another"""
        offsets = self._getOffsetsDictionary(x, y)
        reverse_offsets = {}
        for direction, (dx, dy) in offsets.iteritems():
            reverse_offsets[x + dx, y + dy] = self._offset_reversed[direction]
        try:
            return reverse_offsets[cx, cy]
        except KeyError:
            raise OutOfRange('Cannot find direction of cell %s, %s from %s, %s' % (
                x, y, cx, cy
            ))

    def getCellLocation(self, x, y):
        """Return the location of cell center based on the top left being 0, 0"""
        vertical_offset = self.half_size if x % 2 == 0 else 2 * self.half_size
        #
        return (
            self.hexagon_size + self.hexagon_size * x * 1.5,
            vertical_offset + self.half_size * y * 2.0
        )

    def getCellDistance(self, (x1, y1), (x2, y2)):
        """Return the distance between two cells"""
        if x1 > x2:
            return self.getCellDistance((x2, y2), (x1, y1))
        #
        dx = x2 - x1
        dy = y2 - y1
        x_odd = 1 if x1 % 2 == 1 else 0
        x_even = 1 if not x_odd else 0
        #
        if dx == 0:
            return abs(dy)
        elif dy == 0:
            return abs(dx)
        elif dy >= 0:
            return abs(dx) + abs(dy) - min(abs(dy), (abs(dx) + x_odd) // 2)
        else:
            return abs(dx) + abs(dy) - min(abs(dy), (abs(dx) + x_even) // 2)

    def getCellCoordsContaining(self, px, py):
        """Return the coordinates of a cell containing the point"""
        dist, (x, y) = self._getClosestCenter(px, py)
        if dist <= self.hexagon_size:
            return x, y
        else:
            raise OutOfRange('%s, %s is not in closest cell (%s, %s: dist=%s)' % (
                px, py, x, y, dist
            ))

    def getCellContaining(self, x, y):
        """Return the cell containing the point"""
        return self.getCell(*self.getCellCoordsContaining(x, y))

    def _getClosestCenter(self, px, py):
        """Return the closest cell center"""
        distances = []
        for (tx, ty), (x, y) in self.cell_centers:
            distance = math.sqrt((px - tx) ** 2 + (py - ty) ** 2)
            distances.append((distance, (x, y)))
        distances.sort()
        return distances[0]

    def getCellPoints(self, x, y):
        """Return the points for the given cell"""
        px, py = self.getCellLocation(x, y)
        points = []
        for dx, dy in self._points_offsets:
            points.append((
                px + dx * self.hexagon_size,
                py + dy * self.half_size
            ))
        #
        return points

    def iterLocations(self):
        """Iterate through the locations"""
        for x in range(self.width):
            for y in range(self.height):
                yield (x, y)

    def iterCells(self):
        """Iterate through the cells"""
        for x, y in self.iterLocations():
            yield self.getCell(x, y)


class HexGridCell(serge.actor.Actor):
    """A grid cell on the screen"""

    def __init__(self, tag, name, location, grid, colour, stroke_colour=None, stroke_width=0):
        """Initialise the grid cell"""
        super(HexGridCell, self).__init__(tag, name)
        #
        self.grid = grid
        self.location = location
        self.colour = colour
        self.stroke_colour = stroke_colour
        self.stroke_width = stroke_width
        #
        self.visual = serge.blocks.visualblocks.Polygon(
            points=self.grid.getCellPoints(0, 0),
            colour=self.colour,
            stroke_colour=self.stroke_colour,
            stroke_width=self.stroke_width
        )

class HexGridDisplay(serge.blocks.layout.BaseGrid):
    """Displays and manages a hexagonal grid on the screen"""

    def __init__(self, tag, name='', size=(1, 1), width=None,
                 height=None, background_colour=None, background_layer=None,
                 hexagon_size=1, cell_colour=(255, 255, 255), stroke_colour=(255, 255, 255),
                 stroke_width=1, cell_cls=HexGridCell):
        """Initialise the grid"""
        #
        self.hexagon_size = hexagon_size
        self.cell_colour = cell_colour
        self.stroke_width = stroke_width
        self.stroke_colour = stroke_colour
        self.cell_cls = cell_cls
        self._mouse_over_cell = None
        self._mouse_down = False
        self._right_mouse_down = False
        #
        super(HexGridDisplay, self).__init__(
            tag, name, size, width,
            height, background_colour, background_layer)

    def setGrid(self, size):
        """Set the new grid"""
        self._overlay_grid = HexagonalGrid(size[0], size[1], self.hexagon_size)
        #
        for x, y in self._overlay_grid.iterLocations():
            cell = self.cell_cls(
                'grid-cell', 'cell-%s-%s' % (x, y),
                (x, y),
                self._overlay_grid,
                self.cell_colour,
                self.stroke_colour,
                self.stroke_width
            )
            cell.moveTo(*self._overlay_grid.getCellLocation(x, y))
            self.addChild(cell)
            self._overlay_grid.setCell(x, y, cell)

    def _redoLocations(self):
        """Reloate items in case we have moved"""
        for x, y in self._overlay_grid.iterLocations():
            cell = self._overlay_grid.getCell(x, y)
            px, py = self._overlay_grid.getCellLocation(x, y)
            cell.moveTo(self.x + px, self.y + py)

    def addedToWorld(self, world):
        """Added to the world"""
        super(HexGridDisplay, self).addedToWorld(world)
        #
        self.mouse = world.getEngine().getMouse()

    def updateActor(self, interval, world):
        """Update the display"""
        super(HexGridDisplay, self).updateActor(interval, world)
        #
        # Check if the mouse is over a cell
        px, py = self.mouse.getScreenPos()
        try:
            cell = self._overlay_grid.getCellContaining(px - self.x, py - self.y)
        except OutOfRange:
            cell = None

        #
        if self._mouse_over_cell != cell:
            if self._mouse_over_cell is not None:
                self.processEvent((serge.events.E_MOUSE_LEAVE, self._mouse_over_cell))
                self._mouse_over_cell = None
            if cell is not None:
                self._mouse_over_cell = cell
                self.processEvent((serge.events.E_MOUSE_ENTER, cell))
        elif self._mouse_over_cell is not None:
            self.processEvent((serge.events.E_MOUSE_OVER, self._mouse_over_cell))
        #
        if self.mouse.isDown(serge.input.M_LEFT):
            self._mouse_down = True
        if self.mouse.isUp(serge.input.M_LEFT):
            if self._mouse_down and self._mouse_over_cell:
                self.processEvent((E_CELL_LEFT_CLICK, self._mouse_over_cell))
            self._mouse_down = False
        if self.mouse.isDown(serge.input.M_RIGHT) and self._mouse_over_cell:
            self._right_mouse_down = True
        if self.mouse.isUp(serge.input.M_RIGHT):
            if self._right_mouse_down and self._mouse_over_cell:
                self.processEvent((E_CELL_RIGHT_CLICK, self._mouse_over_cell))
            self._right_mouse_down = False

    def getNeighbourCells(self, cell):
        """Get the neighbours of a cell"""
        return self._overlay_grid.getNeighbours(*cell.location)

    def getNeighbourCellsWithin(self, x, y, distance):
        """Return the neighbour cells in a certain distance"""
        return self._overlay_grid.getNeighbourCellsWithin(x, y, distance)

    def getCell(self, x, y):
        """Return the cell"""
        return self._overlay_grid.getCell(x, y)

    def iterLocations(self):
        """Iterate through the cell locations"""
        for cx, cy in self._overlay_grid.iterLocations():
            yield cx, cy

    def getGrid(self):
        """Return the underlying grid"""
        return self._overlay_grid

    def getCellDistance(self, loc1, loc2):
        """Return the distance between two cells"""
        return self._overlay_grid.getCellDistance(loc1, loc2)