"""The main builder App"""

import threading

from build import *
from ui import *

import serge.engine
import serge.world
import actorsform
import builderlogic

class Builder(Build):
    """The main builder window class"""
    
    def __init__(self, engine, *args):
        """Initialise the window"""
        Build.__init__(self, *args)
        self.top_window.connect('delete-event', gtk.main_quit)
        #
        # Initialise the controls
        self.initWorlds()
        self.initSprites()
        self.initLayers()
        #
        self.engine = engine
        #self.engine.runAsync(60)
        #
        self.logic = builderlogic.BuilderLogic(self.engine)
        self.engine.attachBuilder(self.logic)
                
    ### Utility ###
    
    def doDebug(self, args):
        """Open a shell"""
        from IPython.Shell import IPythonShellEmbed  
        ipshell = IPythonShellEmbed(['-gthread'], 'Game Interactive Shell', 'Left Shell', user_ns=locals())  
        ipshell() # this call anywhere in your program will start IPython

    ### Worlds ###

    def initWorlds(self):
        """Intialise the worlds controls"""
        self.view_worlds = TView(self.widgets['view_worlds'], (str,), ('Name',), (150,), self.editWorld)
        self.view_worlds.setMultiSelect()
    
    def setWorlds(self):
        """Set the worlds that we have read in"""
        self.view_worlds.model.clear()
        for world in reversed(self.engine.getWorlds()):
            self.view_worlds.model.append((world.name,))
        if len(self.engine.getWorlds()):
            self.view_worlds.selectRow(0)
            self.changedWorld(None)

    def clickAddWorld(self, arg):
        """Add a new world"""
        name = 'World %d' % (len(self.view_worlds.model)+1)
        self.view_worlds.model.append((name,))
        world = serge.world.World(name)
        zone = serge.zone.Zone()
        zone.setSpatial(0, 0, 20000, 20000)
        zone.active = True
        world.addZone(zone)
        self.engine.addWorld(world)
        
    def clickDeleteWorld(self, arg):
        """Delete the selected worlds"""
        def removeWorld(name):
            self.engine.removeWorldNamed(name)
        self.view_worlds.deleteSelectedRows(removeWorld)
    
    def editWorld(self, path, column, new_text):
        """Rename the current world"""
        old_name = self.view_worlds.model[path][0]
        world = self.engine.getWorld(old_name)
        self.engine.removeWorld(world)
        world.name = new_text
        self.engine.addWorld(world)
        self.view_worlds.model[path][column] = new_text

    def changedWorld(self, arg):
        """The user changed the world"""
        row = self.view_worlds.getSelectedRow()
        name = self.view_worlds.model[row][0]
        self.engine.setCurrentWorldByName(name)
        if hasattr(self, 'actors'):
            self.actors.updateActorList()

    ### Sprites ###

    def initSprites(self):
        """Intialise the sprites controls"""
        # name, path, w=1, h=1, framerate=0, running=False, rectangular=True, angle=0.0, zoom=1.0
        self.view_sprites = TView(self.widgets['view_sprites'], 
                (str, str, int, int, int, int, int, float, float), 
                ('Name', 'File', 'nx', 'ny', 'Framerate', 'Running', 'Rect', 'Angle', 'Zoom'),
                (80, 150, 50, 50, 50, 50, 50, 50, 50), 
                self.editSprite,
                {1:CellRendererFile})
        self.view_sprites.setMultiSelect()
        
        
    def changedImageLocation(self, arg):
        """The image location was changed"""
        serge.visual.Register.setPath(self.widgets['entry_image_location'].get_text())
    
    def setSprites(self):
        """Set the sprites we read in"""
        for name, path, w, h, framerate, running, rectangular, angle, zoom in serge.visual.Register.getSpriteDefinitions():
            self.view_sprites.model.append((name, path, w, h, framerate, running, rectangular, angle, zoom))
        self.widgets['entry_image_location'].set_text(serge.visual.Register.base_path)
    
    def updateSprite(self, row):
        """Update the sprite referenced by the row"""
        name, path, w, h, framerate, running, rectangular, angle, zoom = self.view_sprites.model[row]
        serge.visual.Register.removeSprite(name)
        serge.visual.Register.registerSprite(name, path, w, h, framerate, running, rectangular, angle, zoom)
    
    def clickAddSprite(self, arg):
        """Add a new sprite"""
        name = 'Sprite %d' % (len(self.view_sprites.model)+1)
        self.view_sprites.model.append((name, '', 1, 1, 0, 0, 1, 0, 1))
        serge.visual.Register.registerSprite(name, '', 1, 1, 0, 0, 1, 0, 1)
        
    def clickDeleteSprite(self, arg):
        """Delete the selected sprite"""
        self.view_sprites.deleteSelectedRows()
    
    def clickSelectSpriteFile(self, arg):
        """Select the file for the current sprite"""
        #
        # Find which sprite we are editing
        try:
            row = self.view_sprites.getSelectedRow()
        except NoSelectedRow:
            return # Nothing selected so nothing to do
        #
        # Show file selection dialog to set the sprites
        fd = gtk.FileChooserDialog(title='Select sprite file', 
                action=gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK))
        fd.set_default_response(gtk.RESPONSE_OK)
        #
        # Use last default
        folder = self.widgets['entry_image_location'].get_text()
        current = self.view_sprites.model[row][1]
        fd.set_current_folder(folder)
        fd.set_current_name(current)
        #
        # Get the user's selection
        result = fd.run()
        if result == gtk.RESPONSE_OK:
            self.view_sprites.model[row][1] = os.path.relpath(fd.get_filename(), folder)
            self.updateSprite(row)
        fd.destroy()
     
    def clickSelectImageLocation(self, arg):
        """Select the path where images are stored"""
        current = self.widgets['entry_image_location'].get_text()
        #
        # Show file selection dialog to set the sprites
        fd = gtk.FileChooserDialog(title='Select sprite file', 
                action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK))
        fd.set_default_response(gtk.RESPONSE_OK)
        #
        # Use last default
        fd.set_current_folder(current)
        #
        # Get the user's selection
        result = fd.run()
        if result == gtk.RESPONSE_OK:
            self.widgets['entry_image_location'].set_text(fd.get_filename())
        fd.destroy()
        
    def editSprite(self, path, column, new_text):
        """Edited the sprite"""
        data = self.view_sprites.model[path]
        serge.visual.Register.removeSprite(data[0])
        if column in (0, 1):
            self.view_sprites.model[path][column] = new_text
            data[column] = new_text
        else:
            self.view_sprites.model[path][column] = float(new_text)
            data[column] = float(new_text)
        serge.visual.Register.registerSprite(*data)
        
    ### Layers ###
    
    def initLayers(self):
        """Intialise the layers controls"""
        self.view_layers = TView(self.widgets['view_layers'], (str, int), ('Name', 'Order'), (150, 60), self.editLayer, sortcol=1)
        self.view_layers.setMultiSelect()

    def setLayers(self):
        """Set the layers we have loaded in"""
        self.view_layers.model.clear()
        for layer in self.engine.getRenderer().getLayers():
            self.view_layers.model.append((layer.name, layer.order))
    
    def clickAddLayer(self, arg):
        """Add a new layer"""
        name = 'Layer %d' % (len(self.view_layers.model)+1)
        order = len(self.view_layers.model)+1
        self.view_layers.model.append((name, order))
        self.engine.getRenderer().addLayer(serge.render.Layer(name, order))
        
    def clickDeleteLayer(self, arg):
        """Delete the selected layers"""
        def removeLayer(name, order):
            self.engine.getRenderer().removeLayerNamed(name)
        self.view_layers.deleteSelectedRows(removeLayer)

    def editLayer(self, path, column, new_text):
        """Edited the layer"""
        old_name = self.view_layers.model[path][0]
        layer = self.engine.getRenderer().getLayer(old_name)
        if column == 0:
            self.engine.getRenderer().removeLayer(layer)
            layer.name = new_text
            self.engine.getRenderer().addLayer(layer)
            self.view_layers.model[path][column] = new_text
        else:
            layer.order = int(new_text)
            self.view_layers.model[path][column] = int(new_text)

    ### Saving and loading ###
    
    def clickSave(self, arg):
        """User wants to save everything"""
        self.engine.save('builder.dat')
    
    def clickOpen(self, arg):
        """Open a file"""
        #
        # Show file selection dialog to set the sprites
        fd = gtk.FileChooserDialog(title='Select engine file', 
                action=gtk.FILE_CHOOSER_ACTION_OPEN,
                buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OK,gtk.RESPONSE_OK))
        fd.set_default_response(gtk.RESPONSE_OK)
        #
        # Get the user's selection
        result = fd.run()
        if result == gtk.RESPONSE_OK:
            self.load(fd.get_filename())
        #
        fd.destroy()
        
    def load(self, filename):
        """Load a file"""
        self.engine.stop()
        with file(filename, 'r') as f:
            text = f.read()
        self.engine = serge.serialize.Serializable.fromString(text)
        self.logic = builderlogic.BuilderLogic(self.engine)
        self.engine.attachBuilder(self.logic)
        self.logic.engine = self.engine
        self.actors.engine = self.engine
        self.setWorlds()
        self.setLayers()
        self.setSprites()
        #self.engine.runAsync(60)
        
app = None
def main(engine=None, fps=60, argv=[]):
    global app
    engine = engine if engine else serge.engine.Engine()
    app = Builder(engine)
    app.top_window.set_title('Serge Builder')
    app.show()
    #
    act = actorsform.ActorsForm(app.engine, app)
    app.top_window.set_position(gtk.WIN_POS_CENTER)
    app.top_window.set_role('main')
    act.top_window.set_title('Serge Actors')
    act.show()
    act.top_window.set_position(gtk.WIN_POS_CENTER)
    act.top_window.set_role('actors')
    #
    app.actors = act
    #
    if len(argv)==2:
        app.load(argv[1])
    #
    gtk.gdk.threads_init()
    #
    t = threading.Thread(target=start)
    t.setDaemon(True)
    t.start()
    #
    app.engine.run(fps)
    
     
def start():   
    gtk.set_interactive(False) 
    gtk.main()

#----------------------------------------------------------------------

if __name__ == '__main__':
    main(None, sys.argv)
