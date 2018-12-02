'''
Created on 12.09.2011

'''

import data 

from math2d import Vector2
from math2d import interpolate_rotation

from pyglet import graphics
from pyglet import gl

from renderables import debugRenderGroup
from renderables import BaseRenderable
from random import Random

class Path(BaseRenderable):
    
    _Count = 0
    _Start = None
    _End = None
    
    _VisualizeEditMode = False
    
    editHighlight = None
    editBasePoint = None
    
    def __init__(self):
        BaseRenderable.__init__(self, renderCallback=False)
    
    def __getstate__(self):
        state = BaseRenderable.__getstate__(self)
        state.add_data(self, "_Start", self._Start)
        return state
    
    def __setstate__(self, state):
        BaseRenderable.__setstate__(self, state)
        self._Start = state.get_data(self, "_Start")
        
        self._Count = 0
        self._End = None
        wp = self._Start
        while wp:
            self._Count += 1
            self._End = wp
            wp = wp.get_neighbour(True)
        
    def _get_add_base(self):
        if self.editBasePoint: return self.editBasePoint
        return self._End
    
    def _set_add_base(self, waypoint):
        if waypoint == self._End:
            self.editBasePoint = None
        else:
            self.editBasePoint = waypoint
    
    def add_waypoint(self, waypoint):
        waypoint.set_next(None)
        waypoint.set_previous(None)
        
        if self._Start == None:
            self._Start = waypoint
            self._End = waypoint
        else:
            editbase = self._get_add_base()
            isEnd = editbase == self._End
            isStart = not isEnd and editbase == self._Start
            if isStart:
                editbase.set_previous(waypoint)
                self._Start = waypoint
            else:
                oldNext = editbase.get_neighbour(True)
                editbase.set_next(waypoint)
                waypoint.set_next(oldNext)
                if isEnd: self._End = waypoint
        
        self._Count += 1
                
        self._set_add_base(waypoint)
        
    def remove_waypoint(self, waypoint):
        if not self.contains_waypoint(waypoint): return
        
        previousWp = waypoint.get_neighbour(False)
        nextWp = waypoint.get_neighbour(True)
        
        if waypoint == self._Start: self._Start = nextWp
        if waypoint == self._End: self._End = previousWp
        
        if nextWp : nextWp.set_previous(previousWp)
        if previousWp: previousWp.set_next(nextWp)
        self._Count -= 1 
     
    def contains_waypoint(self, waypoint):
        walk = self._Start
        while walk:
            if walk == waypoint: return True
            walk = walk.get_neighbour(True)
        return False
            
    def get_start(self):
        return self._Start
    
    def get_end(self):
        return self._End 

    def visualize(self, editMode = False):
        self._VisualizeEditMode = editMode
        self._set_rendercallback(True)
            
    def render(self, gameTime, deltaTime):
        BaseRenderable.render(self, gameTime, deltaTime)

        pointCount = self._Count
        points = [0.0] * pointCount * 2
        
        i = 0
        w = self._Start
        while w:
            points[i] = w.get_position().x
            points[i+1] = w.get_position().y
            i += 2
            w = w.get_neighbour(True)

        if self._VisualizeEditMode:
            debugRenderGroup.set_state_recursive()
                    
            if self._get_add_base():
                point = self._get_add_base().get_position()
                gl.glColor3f(0.0, 0.0, 0.0)
                gl.glPointSize(12)
                graphics.draw(1, gl.GL_POINTS, ('v2f', (point.x, point.y)))
                
            if self.editHighlight:
                point = self.editHighlight.get_position()
                gl.glColor3f(0.0, 1.0, 1.0)
                gl.glPointSize(10)
                graphics.draw(1, gl.GL_POINTS, ('v2f', (point.x, point.y)))
                
            if pointCount > 0:
                start = self._Start.get_position()
                gl.glColor3f(1.0, 0.0, 0.0)
                gl.glPointSize(8)
                graphics.draw(1, gl.GL_POINTS, ('v2f', (start.x, start.y)))
                
            if pointCount > 1:
                end = self._End.get_position()
                gl.glColor3f(0.0, 1.0, 0.0)
                gl.glPointSize(8)
                graphics.draw(1, gl.GL_POINTS, ('v2f', (end.x, end.y)))
            
            debugRenderGroup.unset_state_recursive()
        
        debugRenderGroup.set_state_recursive()
        if not self._VisualizeEditMode:
            gl.glPointSize(3)
            gl.glLineWidth(1)
            gl.glColor3f(0.4, 0.0, 0.0)
        graphics.draw(pointCount, gl.GL_LINE_STRIP, ('v2f', points))
        graphics.draw(pointCount, gl.GL_POINTS, ('v2f', points))
        debugRenderGroup.unset_state_recursive()
        
        self._set_rendercallback(False)
    
    
class Waypoint:
    
    _next = None
    _previous = None
    _position = Vector2()
    
    _nextDist = 0.0
    _nextDir = Vector2()
    _nextVec = Vector2()
    
    def __init__(self, position):
        self._position = position
    
    def __getstate__(self):
        state = data.SaveData()
        state.add_data(self, "_next", self._next)
        state.add_data(self, "_previous", self._previous)
        state.add_data(self, "_position", self._position)
        return state
    
    def __setstate__(self, state):
        self._next = state.get_data(self, "_next")
        self._previous = state.get_data(self, "_previous")
        self._position = state.get_data(self, "_position")
        self._update_cache()
    
    def _update_cache(self):
        self._nextDir = Vector2()
        self._nextDist = 0.0
        self._nextVec = Vector2()
        if self._next:
            self._nextVec = (self._next._position - self._position)
            self._nextDist = self._nextVec.get_length()
            self._nextDir = self._nextVec * (1.0 / self._nextDist)  
    
    def set_next(self, waypoint):
        if self._next == waypoint:
            return        
        oldNext = self._next 
        self._next = waypoint
        if oldNext and oldNext.get_neighbour(False) == self: 
            oldNext.set_previous(None)
        if waypoint: waypoint.set_previous(self)
        self._update_cache()
        
    def set_previous(self, waypoint):
        if self._previous == waypoint:
            return
        oldPrevious = self._previous
        self._previous = waypoint
        if oldPrevious and oldPrevious.get_neighbour(True) == self:
            oldPrevious.set_next(None)
        if waypoint: waypoint.set_next(self)
    
    def get_neighbour(self, forward):
        if forward:
            return self._next
        else:
            return self._previous
    
    def get_position(self):
        return self._position
    
    def set_position(self, position):
        self._position = position
    
    def get_dir_next(self):
        return self._nextDir
    
    def get_dist_next(self):
        return self._nextDist
    
    def get_position_between(self, normalized):
        return self._position + self._nextVec * normalized
    
    
class Walker:
    
    _From = None
    _To = None
    _ToDist = 0.0
    _ToRotation = 0.0
    _CurrentDist = 0.0
    
    _Speed = 1.0
    _RotationSpeed = None
    _Rotation = 0.0
    _Variation = 0.0
    _Forward = True
    _Stopped = True
    
    _VariationOffset = Vector2(0.0, 0.0)
    
    frameMove = 0.0
    
    def __init__(self, startPoint, forward, speed, variation):
        self._From = startPoint
        self._CurrentDist = 0.0
        self._Forward = forward
        self._Speed = speed
        self._Variation = variation
        self._RotationSpeed = self._Speed * 2.7778
        
        # TODO: start at Variation Offset 0,0 and update every frame
        self._update_variation(0, 0)
        self.start()
    
    def set_speed(self, speed):
        self._Speed = speed
        
    def _update_variation(self, gameTime, deltaTime):
        # temporary implementation; some work required
        rnd = Random()
        
        variation = 2.0 * self._Variation
        self._VariationOffset = Vector2(rnd.random() * variation - self._Variation, rnd.random() * variation - self._Variation)
                
    def _set_to(self, to):
        self._To = to
        if to != None:
            self._ToDist = self._From.get_dist_next()
            self._ToRotation = self._From.get_dir_next().to_rotation()
        else:
            self._ToDist = 0.0
        
    def stop(self):
        self._Stopped = True
        
    def start(self):
        if self._From == None:
            return
        if self._To == None:
            self._set_to(self._From.get_neighbour(self._Forward))
            self._Rotation = self._ToRotation
        self._Stopped = False
        
    def turn(self):
        if self._To != None:
            self._From = self._To
        
        newDist = self._ToDist - self._CurrentDist
        self._Forward = not self._Forward        
        self._set_to(self._From.get_neighbour(self._Forward))
        self._CurrentDist = newDist
        
    def update(self, gameTime, deltaTime):
        if self._Stopped:
            return
        
        self.frameMove = self._Speed * deltaTime 
        deltaDist = self.frameMove
        while deltaDist > 0.0 and not self.has_reached_target():
            distanceToDo = self._ToDist - self._CurrentDist
            self._CurrentDist += deltaDist
            deltaDist -= distanceToDo
            if deltaDist >= 0.0:
                self._move_next()
        
        rotationDelta, _ = interpolate_rotation(self._Rotation, self._ToRotation, self._RotationSpeed, deltaTime)
        self._Rotation += rotationDelta          
    
    def _move_next(self):
        self._From = self._To
        self._set_to(self._From.get_neighbour(self._Forward))
        self._CurrentDist = 0.0
    
    def get_visual_position(self):
        if self.has_reached_target():
            return self._From.get_position()
        
        return self._From.get_position() + self._From.get_dir_next() * self._CurrentDist + self._VariationOffset
    
    def get_position(self):
        if self.has_reached_target():
            return self._From.get_position()
        
        return self._From.get_position() + self._From.get_dir_next() * self._CurrentDist
    
    def get_rotation(self):
        return self._Rotation
    
    def has_reached_target(self):
        return self._From.get_neighbour(self._Forward) == None