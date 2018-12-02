"""Useful helper classes for the builder UI"""

import gtk

class NoSelectedRow(Exception): """There was no row selected"""

class CellRendererFile(gtk.CellRendererText):
    def __init__(self):
        gtk.CellRendererText.__init__(self)
        self.props.editable = True

    def do_start_editing(self, event, widget, path, background_area, cell_area, flags):
        print 'I am here!'
        self.emit('edited', path, "TODO: Dialog output")


class TView():
    """A set of handlers for tree views"""
    
    def __init__(self, widget, cols, names, widths, callback, special=None, sortcol=0):
        """Initialise"""
        #
        # Special is a dictionary of types to use for rendering
        if special is None:
            special = {}
        #
        self.widget = widget
        self.columns = []
        #
        # Create the model
        self.model = m = gtk.ListStore(*cols)
        widget.set_model(m)
        widget.set_property('headers-clickable' ,True)
        self.callback = callback
        #
        # Create the columns
        for idx, (col, name, width) in enumerate(zip(cols, names, widths)):
            i = gtk.TreeViewColumn(name)
            i.set_clickable(True)
            i.set_sort_column_id(idx)
            i.set_sort_indicator(False)
            r = special.get(idx, gtk.CellRendererText)()
            r.set_property('editable', True)
            r.connect('edited', self.cellTextEdit, idx)
            i.pack_start(r)
            i.add_attribute(r, 'text', idx)
            i.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            i.set_fixed_width(width)
            widget.append_column(i)
            self.columns.append((i, r))
        #
        self.model.set_sort_column_id(0, gtk.SORT_ASCENDING)
        
    def sort(self, model, iter1, iter2, data):
        """Return sorting of two rows"""
        return cmp(model[iter1][0], model[iter2][1])

    def getSelectedRow(self):
        """Return the selected row for a widget"""
        try:
            return self.widget.get_selection().get_selected_rows()[1][0][0]
        except IndexError:
            raise NoSelectedRow
                    
    def getSelectedRows(self):
        """Return the selected rows for a widget"""
        return [item[0] for item in self.widget.get_selection().get_selected_rows()[1]]

    def setMultiSelect(self):
        """Set this to be multiple select"""
        self.widget.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

    def removeRow(self, row):
        """Remove one of our rows"""
        i = self.model.get_iter(row)
        self.model.remove(i)

    def deleteSelectedRows(self, callback=None):
        """Delete the selected rows calling the callback for each row deleted"""
        for row in reversed(self.getSelectedRows()):
            if callback:
                callback(*self.model[row])
            self.removeRow(row)

    def cellTextEdit(self, cell, path, new_text, column):
        """Text was edited"""
        self.callback(path, column, new_text)

    def selectRow(self, row):
        """Select the given row"""
        self.widget.get_selection().select_path(row)
        
        
