"""Logic for handling the builder functions relating to the pygame screen"""

import pygame

import serge.common
import serge.input
import serge.visual
import serge.render

class Drag():
    def __init__(self, pos):
        """Dragging operation"""
        self.initial_pos = pos

class BuilderLogic(serge.common.Loggable):
    """Logic about the builder process in pygame"""
    
    def __init__(self, engine):
        """Initialise the BuilderLogic"""
        self.addLogger()
        self.log.info('Created builder')
        self.engine = engine
        self.stats = engine.getStats()
        self.drag = None
        self.zoom = 1.0
        self.createVisuals()
        
    def createVisuals(self):
        """Create our visual elements"""
        self.mode = serge.visual.Text('Builder mode', (0, 255, 0))
        self.coords = serge.visual.Text('(0, 0)', (0, 255, 0))
        self.framerate = serge.visual.Text('Rate: ', (0, 255, 0))
        self.engine.getRenderer().addLayer(serge.render.Layer('builder', 100))
        
    def updateBuilder(self, interval):
        """Update the builder"""
        if self.keyboard.isDown(pygame.K_F9):
            self.log.debug('Left shift')
        #
        self.handleStatus()    
        self.handleLeftMouseDown()
        self.handleMouseWheel()
                
    def handleStatus(self):
        """Update our status"""
        x, y = self.mouse.getScreenPos()
        self.coords.setText('(%d, %d)' % (x, y))
                
    def handleLeftMouseDown(self):
        """Handle that the left mouse button is down"""
        #
        # Mouse left down
        if self.mouse.isDown(serge.input.M_LEFT):
            if not self.drag:
                self.drag = Drag(self.mouse.getScreenPos())
            else:
                self.camera.move(*((self.drag.initial_pos - self.mouse.getScreenPos())))
                self.drag.initial_pos = self.mouse.getScreenPos()
        elif self.drag:
            self.drag = None
            
    def handleMouseWheel(self):
        """Handle the mouse wheel being used"""
        #
        # Check if the mouse wheel is being used
        factor = None
        if self.mouse.isDown(serge.input.M_WHEEL_UP):
            factor = 1.1
        elif self.mouse.isDown(serge.input.M_WHEEL_DOWN):
            factor = 0.9
        #
        if factor:
            self.zoom *= factor
            x, y = self.mouse.getScreenPos()
            self.log.info('Zooming to %s, %s, %s' % (self.zoom, x, y))
            self.world.setZoom(self.zoom*factor, x, y)
            self.camera.setZoom(self.zoom*factor, x, y)

    def renderTo(self, renderer, interval):
        """Update the builder display"""
        self.mode.renderTo(interval, renderer.getLayer('builder').getSurface(), (20, 20))
        self.coords.renderTo(interval, renderer.getLayer('builder').getSurface(), (150, 20))
        self.framerate.setText('Rate: %5.2f (%5.2f)' % (self.stats.current_frame_rate, self.stats.average_frame_rate))
        self.framerate.renderTo(interval, renderer.getLayer('builder').getSurface(), (20, 35))
          
    @property
    def world(self):
        return self.engine.getCurrentWorld()
    
    @property
    def mouse(self):
        return self.engine.getMouse()
    
    @property
    def keyboard(self):
        return self.engine.getKeyboard()
    
    @property
    def camera(self):
        return self.engine.getRenderer().getCamera()
