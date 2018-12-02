import pyglet


class BatchManager (object):

    def __init__(self):
        self._batch = pyglet.graphics.Batch()
        self._named_batches = {}
        self._default_batch = self._batch
        self.current_name = "default"
        
    def add(self, geometry):
        items = len(geometry.vertices)
        
        ## iter through the items
        for n in xrange(items):
            vformat, verts = geometry.vertices[n]
            cformat, colors = geometry.colors[n]
            parent = geometry.parents[n]
            group = geometry.drawgroups[n]
            prim_type = geometry.prim_types[n]
            

            numverts = len(verts)/3
            #print "Adding a prim with %d verts and %d colors" % (numverts, len(colors))
 
            ## build a vertex list from the values
            vertex_list = self._batch.add(numverts, prim_type, group,
                (vformat, verts),
                (cformat, colors),
                )

            ## set the parent vertex list for later manip
            parent.vertex_list = vertex_list
            return vertex_list

    def get_batch(self, batch=None):
        if batch==None:
            #print "<--------getting default batch", self.current_name
            return self._batch
        else:
            #print "<--------getting batch", batch
            if self._named_batches.has_key(batch):
                return self._named_batches[batch]
            else:
                new_batch = pyglet.graphics.Batch()
                self._named_batches[batch] = new_batch
                self._batch = new_batch
                return new_batch

    def set_batch(self, batch):
        if batch:
            print "---->setting batch", batch
            if self._named_batches.has_key(batch):
                 self._batch = self._named_batches[batch]
            else:
                new_batch = pyglet.graphics.Batch()
                self._named_batches[batch] = new_batch
                self._batch = new_batch
            self.current_name = batch
        else:
            print "---->setting default batch"
            self._default_batch = self._batch
            self.current_name = "default"
            
        
    def clear(self, batch):
        print "---->clearing batch", self.current_name
        if batch:
            if self._named_batches.has_key(batch):
                del self._named_batches[batch]
        if self.current_name == "default":
            self._default_batch = pyglet.graphics.Batch()
            self._batch = self._default_batch
        else:
            if self._named_batches.has_key(self.current_name):
                self._named_batches[self.current_name] = pyglet.graphics.Batch()
           


## the one true instance
batch = BatchManager()

