"""Manages actors"""

from actors import *
from ui import *

import serge.engine
import serge.world
import serge.actor


class ActorsForm(Actors):
    """The main form"""
    
    def __init__(self, engine, builder, *args):
        """Initialise the window"""
        Actors.__init__(self, *args)
        #
        self.engine = engine
        self.builder = builder
        self.initActors()

        
        
    def initActors(self):
        """Initialise the actors view"""
        def getCombo(model):
            """Return the combo for sprites"""
            crc = gtk.CellRendererCombo()
            crc.set_property('model', model)
            crc.set_property('text-column', 0)
            crc.set_property('editable', True)
            crc.set_property('has_entry', False)
            return crc
        
        self.view_actors = TView(self.widgets['view_actors'], 
                (str, str, str, str, int, int), 
                ('Tag', 'Name', 'sprite', 'Layer', 'x', 'y'), 
                (150, 150, 150, 150, 60, 60), 
                self.editActor,
                special={
                            2: lambda : getCombo(self.builder.view_sprites.model), 
                            3: lambda : getCombo(self.builder.view_layers.model), 
                        })
        self.view_actors.setMultiSelect()

    def editActor(self, path, column, new_text):
        """Edit the actor in the list view"""
        row = int(path)
        world = self.engine.getCurrentWorld()
        actor = world.findActorByName(self.view_actors.model[path][1])
        world.removeActor(actor)
        data = self.view_actors.model[row]
        if column in (4, 5):
            data[column] = int(new_text)
        else:
            data[column] = new_text
        tag, name, sprite, layer, x, y = data
        new_actor = serge.actor.Actor(tag, name)
        if sprite:
            new_actor.setSpriteName(sprite)
        if layer:
            new_actor.setLayerName(layer)
        new_actor.moveTo(x, y)
        world.addActor(new_actor)
        self.view_actors.model[row] = data
        
    def clickAddActor(self, arg):
        """Add an actor"""
        name = 'A%d' % len(self.view_actors.model)
        self.view_actors.model.append(('mob', name, '', '', 0, 0))
        actor = serge.actor.Actor('mob', name)
        self.engine.getCurrentWorld().addActor(actor)
    
    def updateActorList(self):
        """Update the list of actors"""
        try:
            world = self.engine.getCurrentWorld()
        except serge.engine.NoCurrentWorld:
            return
        self.view_actors.model.clear()
        for actor in world.getActors():
            self.addActorToList(actor)
            
    def addActorToList(self, actor):
        """Add an actor to the screen"""
        self.view_actors.model.append((actor.tag, actor.name, actor.sprite, actor.layer, actor.x, actor.y))
        
