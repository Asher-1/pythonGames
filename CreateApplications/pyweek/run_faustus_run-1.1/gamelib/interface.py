from __future__ import division

import inspect
import math
import textwrap
import weakref

import pyglet
from pyglet.gl import *

__metapod_debug__ = False


## Constants ##################################################################

LEFT = pyglet.window.key.LEFT
DOWN = pyglet.window.key.DOWN
RIGHT = pyglet.window.key.RIGHT
UP = pyglet.window.key.UP


## Utility Functions ##########################################################

def _get_class_name(obj):
    if not isinstance(obj, type): obj = type(obj)
    return "%s.%s" % (inspect.getmodule(obj).__name__, obj.__name__)

def _point_test(x, y, c=(1.0, 0.0, 0.0, 1.0)):
    glPointSize(1.0)
    pyglet.graphics.draw(1, GL_POINTS, ('v2f', (x, y)), ('c4f', c))

def _rect_test(x, y, w, h, c=(1.0, 0.0, 0.0, 1.0)):
    glLineWidth(1.0)
    pyglet.graphics.draw(4, GL_LINE_LOOP, ('v2f', (x, y, x + w, y, x + w,
        y + h, x, y + h)), ('c4f', c * 4))


## CACHING PROPERTIES & ATTRIBUTE DESCRIPTORS #################################

class _DependentTracker(object):
    """Mixin for objects tracking dependent caching properties on panels.

    """

    _computing = []

    def _register_dependent(self, obj):
        """Register the top caching property computation as a dependent.

        :Parameters:
            `obj` : object
                The object which should be depended on.

        """
        if self._computing:
            top = self._computing[-1]
            if self not in obj._dependents:
                obj._dependents[self] = set()
            obj._dependents[self].add(top)

    def _clear_dependents(self, obj):
        """Clear and remove all dependent caching properties.

        :Parameters:
            `obj` : object
                The object whose dependents should be cleared.

        """
        if self in obj._dependents:
            dependents = obj._dependents[self]
            while len(dependents) > 0:
                prop, dobj = dependents.pop()
                prop.__delete__(dobj())

    def __repr__(self):
        return "<%s : %s>" % (_get_class_name(self), self._name)


class Attribute(_DependentTracker):
    """Panel attribute descriptors.

    """

    def __init__(self, default, dynamic=False, dtype=None):
        """Create an Attribute object.

        :Parameters:
            `default` : object
                The default value of the attribute.
            `dynamic` : boolean
                If set then dependents will not be managed.
            `dtype` : type
                If set the stored value will be coerced.

        """
        super(Attribute, self).__init__()
        self._dtype = dtype or (lambda v: v)
        self._default = self._process(default)
        self._name = None

        if dynamic:
            self._register_dependent = lambda obj: None
            self._clear_dependents = lambda obj: None

        self._unmanaged = type(self) is Attribute and \
                          dtype is None and \
                          dynamic

    def __get__(self, obj, cls):
        """Retrieve the value from the panel attribute dictionary.

        """
        if obj is None:
            return self
        self._register_dependent(obj)
        attrs = obj._panel_attrs
        try:
            return attrs[self._name]
        except KeyError:
            value = self._default
            attrs[self._name] = value
            return self._default

    def __set__(self, obj, value):
        """Set the value in the panel attribute dictionary removing dependent
        caching properties if necessary.

        """
        value = self._process(value)
        attrs = obj._panel_attrs
        if attrs.get(self._name, self._default) != value:
            attrs[self._name] = value
            self._clear_dependents(obj)

    def __delete__(self, obj):
        """Reset the value in the panel attribute dictionary to the default
        removing dependent caching properties if necessary.

        """
        self.__set__(obj, self._default)

    def _process(self, value):
        """Process the value into the stored form.

        :Parameters:
            `value` : object
                The object being set.

        """
        if value is None:
            return value
        return self._dtype(value)


class Directional(Attribute):
    """Attribute accepting values in four directions.

    """

    def _process(self, value):
        """Process the value into the stored form.

        :Parameters:
            `value` : object
                The object being set.

        """
        if value is None:
            return value
        try:
            value = map(self._dtype, value)
        except TypeError:
            return (self._dtype(value),) * 4
        if len(value) == 2:
            return tuple(value * 2)
        elif len(value) == 4:
            return tuple(value)
        raise ValueError


class Tracking(Attribute):
    """Attribute which follows the value of another attribute.

    """

    def __init__(self, tracked, **kwds):
        """Create a Tracking object.

        :Parameters:
            `tracked` : str
                The name of the attribute to track.

        """
        super(Tracking, self).__init__(None, **kwds)
        self._tracked = tracked

    def __get__(self, obj, cls):
        """Retrieve the value from the panel attribute dictionary.

        """
        if obj is None:
            return self
        self._register_dependent(obj)
        attrs = obj._panel_attrs
        if attrs.get(self._name) is not None:
            return attrs[self._name]
        return getattr(obj, self._tracked)


class Ratio(Attribute):
    """Attribute accepting values as a ratio of two numbers.

    """

    def _process(self, value):
        """Process the value into the stored form.

        :Parameters:
            `value` : object
                The object being set.

        """
        if value is None:
            return value
        try:
            value = map(self._dtype, value)
        except TypeError:
            value = map(self._dtype, (value, 1.0))
        if len(value) == 2:
            return tuple(value)
        raise ValueError


class Cached(_DependentTracker):
    """Caching property objects.

    """

    def __init__(self, function):
        """Create a Cached object.

        :Parameters:
            `function` : function
                The wrapped method.

        """
        super(Cached, self).__init__()
        self._name = function.func_name
        self._function = function

    def __get__(self, obj, cls=None):
        """Optionally compute and then return the cached value.

        """
        if obj is None:
            return self
        self._register_dependent(obj)
        cache = obj._panel_cache
        try:
            return cache[self._name]
        except KeyError:
            dobj = weakref.ref(obj)
            Cached._computing.append((self, dobj))
            try:
                cache[self._name] = self._function(obj)
            finally:
                Cached._computing.pop()
            return cache[self._name]

    def __set__(self, obj, value):
        """Override the cached value.

        """
        if self._name not in obj._panel_cache or \
            obj._panel_cache[self._name] != value:
                obj._panel_cache[self._name] = value
                self._clear_dependents(obj)

    def __delete__(self, obj):
        """Remove the cached value, forcing recomputation.

        """
        if obj is None:
            return
        try:
            del obj._panel_cache[self._name]
            self._clear_dependents(obj)
        except KeyError:
            pass



## PANEL BASE CLASS (AND METACLASS) ###########################################

class Panel(object):
    """Base class for interface objects.

    """

    ## Keyword Attributes
    #####################

    # Dynamic offset.
    xoffset = Attribute(0, dynamic=True, dtype=int)
    yoffset = Attribute(0, dynamic=True, dtype=int)

    # Scroll offset.
    scroll_xoffset = Attribute(0, dynamic=True, dtype=int)
    scroll_yoffset = Attribute(0, dynamic=True, dtype=int)

    # Alignment offset.
    layout_xoffset = Attribute(0, dtype=int)
    layout_yoffset = Attribute(0, dtype=int)

    # Dimensions.
    width = Attribute(None) # rel: layout.width
    height = Attribute(None) # rel: layout.height
    aspect = Ratio(None)

    # Alignment dimensions.
    layout_width = Attribute(None) # rel: absolute
    layout_height = Attribute(None) # rel: absolute

    # Alignment.
    halign = Attribute("center") # rel: parent.width
    valign = Attribute("center") # rel: parent.height
    anchor_x = Tracking("halign") # rel: content.width
    anchor_y = Tracking("valign") # rel: content.height

    # Directional padding.
    margin = Directional(0.0) # rel: layout.height
    padding = Directional(0.0) # rel: layout.height

    # Scrolling.
    scroll_sensitivity = Attribute(0.2) # rel: view.height
    scroll_horizontal = Attribute(True)
    scroll_vertical = Attribute(True)

    # Frame.
    frame_width = Attribute(0.02) # rel: layout.height
    frame_texture = Attribute(None)
    frame_color = Attribute(None)

    # Background.
    background_texture = Attribute(None)
    background_color = Attribute(None)
    background_tiles = Attribute(None)

    # Scissor test.
    scissor = Attribute(False)

    order = Attribute(0)
    outside = Attribute(False)

    ## Class Attributes
    ###################

    # Child superclass restriction.
    child_class = None

    # Layout flag.
    is_layout = False

    ## Metaclass
    ############

    class PanelMeta(type):
        """Metaclass for interface objects.

        """

        def __init__(self, name, bases, dict):
            """Create a PanelMeta object.

            """
            super(self.PanelMeta, self).__init__(name, bases, dict)

            # Start from blank name trees.
            self._keyword_names = self._cached_names = frozenset()

            # Collate the name trees from base classes.
            for base in bases:
                self._keyword_names |= getattr(base, "_keyword_names", set())
                self._cached_names |= getattr(base, "_cached_names", set())

            # Process attribute objects and cached objects.
            for name, value in dict.items():
                if isinstance(value, Attribute):
                    self._keyword_names |= frozenset([name])
                    value._name = name
                if isinstance(value, Cached):
                    self._cached_names |= frozenset([name])

            # Check all names against the class.
            for name in set(self._keyword_names):
                if not isinstance(getattr(self, name), Attribute):
                    self._keyword_names -= frozenset([name])
            for name in set(self._cached_names):
                if not isinstance(getattr(self, name), Cached):
                    self._cached_names -= frozenset([name])

    __metaclass__ = PanelMeta

    ## Constructor
    ##############

    def __init__(self, **kwds):
        """Create a Panel object.

        """
        super(Panel, self).__init__()

        #: Root of this panel tree.
        self._root = self
        #: Parent of this panel.
        self._parent = None
        #: List of children of this panel.
        self._children = []
        #: Whether to render this panel.
        self._visible = True

        # Create a blank panel state.
        self._panel_attrs = {}
        self._panel_cache = {}
        self._dependents = {}

        # Check if we should init now.
        self._delayed_init = kwds.pop('_delayed_init', False)

        # Populate the panel state.
        self._load_keyword_attributes(**kwds)

        # Call the subclass init hook.
        if not self._delayed_init:
            self.init_panel()

    def _load_keyword_attributes(self, **kwds):
        for name, value in kwds.items():
            if name not in self._keyword_names:
                raise TypeError, "%s got an unexpected keyword argument %r" % \
                        (_get_class_name(self), name)
            setattr(self, name, value)

    def _clear_cached_attributes(self):
        for node in self.descendants:
            for name in self._cached_names:
                delattr(self, name)

    def __repr__(self):
        return "<%s : %s>" % (_get_class_name(self), hex(id(self)))

    ## Extension API
    ################

    def init_panel(self):
        """Prepare panel resources.

        """

    def compute_content_size(self):
        """Compute the size of the panel content.

        """

    def draw_content(self):
        """Render the panel content.

        """

    ## Properties
    #############

    def _get_root(self):
        return self._root

    root = property(_get_root, doc=textwrap.dedent("""\
        The root of the panel's tree.

        """))

    def _get_parent(self):
        return self._parent

    def _set_parent(self, parent):
        for child in self.descendants:
            assert child is not parent, "cannot create loops"
        if self.parent is not None:
            self.parent.remove(self)
        parent.add(self)

    parent = property(_get_parent, _set_parent, doc=textwrap.dedent("""\
        The parent of the panel.

        """))

    def _get_children(self):
        return tuple(self._children)

    children = property(_get_children, doc=textwrap.dedent("""\
        The children of the panel.

        """))

    def _get_visible(self):
        return self._visible

    def _set_visible(self, visible):
        self._visible = visible

    visible = property(_get_visible, _set_visible, doc=textwrap.dedent("""\
        The visibility flag to shortcut drawing and signal handling.

        """))

    ## Child Handling
    #################

    @property
    def descendants(self):
        """Iterator over this and descendant nodes.

        """
        yield self
        for child in list(self._children):
            for node in child.descendants:
                yield node

    def add(self, child=None, **kwds):
        """Add a node as a child of this one.

        :Parameters:
            `child` : Panel
                The panel to add as a child.

        """
        # Ensure we have an instance.
        if child is None:
            child = self.child_class
        if isinstance(child, type):
            child = child(_delayed_init=True)

        # Ensure we have an instance of the appropriate type.
        if not isinstance(child, self.child_class):
            raise TypeError, "children of %s must inherit from %s" % \
                    (_get_class_name(self),
                     _get_class_name(self.child_class))
        child._load_keyword_attributes(**kwds)

        # Make sure the child is valid.
        assert child._parent is None, "node cannot have multiple parents"

        # Incorporate child into the tree.
        child._parent = self
        for node in child.descendants:
            node._root = self._root
        self._children.append(child)

        # Process any delayed init.
        if child._delayed_init:
            child._delayed_init = False
            child.init_panel()

        # Clear all cached data for the subtree.
        self._clear_cached_attributes()

        # Return the new child object.
        return child

    def remove(self, child):
        """Remove a child node from this one.

        :Parameters:
            `child` : Panel
                The child panel to remove.

        """
        self._children.remove(child)
        self._clear_cached_attributes()

    def destroy(self):
        """Remove the panel from its parent.

        """
        self._parent.remove(self)

    ## Dimension Handling
    #####################

    _symbol_factors = { "right"  :  1.0,  "top"    :  1.0,
                        "center" :  0.5,  "middle" :  0.5,
                        "left"   :  0.0,  "bottom" :  0.0, }

    _sym = lambda s,x: s._symbol_factors.get(x, x)
    _mgn = lambda s,i,x: s.margin[i] - sum(s.margin[i::2]) * s._sym(x)
    _pad = lambda s,i,x: s.padding[i] - sum(s.padding[i::2]) * s._sym(x)

    # The 'maximum view' is simply the largest the view can be. It provides
    # a default for the content size as well as providing upper bounds for
    # the computed view size.

    @Cached
    def max_view_size(self):
        """The maximum size of the visible panel content.

        """
        # Parent dimensions.
        lwidth, lheight = self.layout_size

        # Margin & padding dimensions.
        hpad = lheight * (sum(self.margin[0::2]) + sum(self.padding[0::2]))
        vpad = lheight * (sum(self.margin[1::2]) + sum(self.padding[1::2]))

        # "Inner" dimensions.
        iwidth = max(0.0, lwidth - hpad)
        iheight = max(0.0, lheight - vpad)

        # Aspect scaling.
        if self.aspect is not None:
            aspectx, aspecty = self.aspect
            if aspectx * iheight < aspecty * iwidth:
                iwidth = iheight * aspectx / aspecty
            elif aspectx * iheight >= aspecty * iwidth:
                iheight = iwidth * aspecty / aspectx

        # 0) Sensible default.
        width, height = iwidth, iheight

        if self.width is not None:
            if self.height is not None:
                # 1) Have width and height.
                width = min(iwidth, lwidth * self.width - hpad)
                height = min(iheight, lheight * self.height - vpad)
            elif self.aspect is not None:
                # 2) Have width and aspect, no height.
                width = min(iwidth, lwidth * self.width - hpad)
                height = width * aspecty / aspectx
            else:
                # 3) Have width sans height and aspect.
                width = min(iwidth, lwidth * self.width - hpad)
                height = iheight

        elif self.height is not None:
            if self.aspect is not None:
                # 4) Have height and aspect, no width.
                height = min(iheight, lheight * self.height - vpad)
                width = height * aspectx / aspecty
            else:
                # 5) Have height sans width and aspect.
                width = iwidth
                height = min(iheight, lheight * self.height - vpad)

        return width, height

    # The 'content' is a subregion of the parent's content and is defined by
    # every (renderable) subclass. It is the exact size of the renderable
    # content, the offset is determined automatically.

    @Cached
    def content_size(self):
        """The size of the panel content.

        """
        return self.compute_content_size() or self.max_view_size

    @Cached
    def parent_size(self):
        """The size of the parent panel's content.

        """
        if self.parent is not None:
            return self.parent.content_size
        return (0.0, 0.0)

    @Cached
    def layout_size(self):
        """The panel's layout dimensions used in relative measurements.

        """
        if self.parent.is_layout:
            return self.parent.layout_size
        return self.parent_size

    @Cached
    def content_offset(self):
        """The static (cached) offset from the parent's content corner.

        """
        # Symbol resolvers.
        sym, mgn, pad = self._sym, self._mgn, self._pad

        # Base dimensions.
        cwidth, cheight = self.content_size
        pcwidth, pcheight = self.parent_size

        # Alignment dimensions.
        if self.layout_width is not None:
            pcwidth = self.layout_width
        if self.layout_height is not None:
            pcheight = self.layout_height

        # Alignment offset.
        offset_x = pcwidth * sym(self.halign)
        offset_y = pcheight * sym(self.valign)

        # Layout offset.
        offset_x += self.layout_xoffset
        offset_y += self.layout_yoffset

        # Anchor offset.
        offset_x -= cwidth * sym(self.anchor_x)
        offset_y -= cheight * sym(self.anchor_y)

        # Margin offset.
        offset_x += pcheight * (mgn(0, self.halign) + pad(0, self.halign))
        offset_y += pcheight * (mgn(1, self.valign) + pad(1, self.valign))

        return offset_x, offset_y

    @Cached
    def cumulative_offset(self):
        """The cumulative static offset from the window's content corner.

        """
        if self.parent is not None:
            ox, oy = self.parent.cumulative_offset
            px, py = self.content_offset
            return ox + px, oy + py
        return self.content_offset

    @property
    def dynamic_offset(self):
        """The dynamic (uncached) offset from the parent's content corner.

        """
        return self.xoffset + self.scroll_xoffset, \
               self.yoffset + self.scroll_yoffset

    # The 'view' is a subregion of the parent's view and a subregion of the
    # window. It is the size of the rendered content and as such is never any
    # larger than the content.

    @Cached
    def view_size(self):
        """The size of the visible panel content.

        """
        cwidth, cheight = self.content_size
        mvwidth, mvheight = self.max_view_size
        return min(cwidth, mvwidth), min(cheight, mvheight)

    # The 'frame' is a region enclosing the view defined by the padding. It is
    # used to render backgrounds and outlines and for scissoring.

    @Cached
    def frame_size(self):
        """The size of the panel frame.

        """
        lwidth, lheight = self.layout_size
        vwidth, vheight = self.view_size
        hpad = lheight * sum(self.padding[0::2])
        vpad = lheight * sum(self.padding[1::2])
        return vwidth + hpad, vheight + vpad

    @Cached
    def frame_offset(self):
        """The offset to the frame's corner.

        """
        # Symbol resolver.
        sym = self._sym

        # Base dimensions.
        cwidth, cheight = self.content_size
        vwidth, vheight = self.view_size
        lwidth, lheight = self.layout_size

        # Content offset.
        offset_x = sym(self.anchor_x) * (cwidth - vwidth)
        offset_y = sym(self.anchor_y) * (cheight - vheight)

        # Padding offset.
        offset_x -= lheight * self.padding[0]
        offset_y -= lheight * self.padding[1]

        return offset_x, offset_y

    ## Signal Handling
    ##################

    def convert_coordinates(self, x, y):
        """Convert the coordinates from parent relative coordinates.

        :Parameters:
            `x`, `y` : float
                The coordinates to convert.

        """
        static_x, static_y = self.content_offset
        dynamic_x, dynamic_y = self.dynamic_offset
        return x - (static_x + dynamic_x), y - (static_y + dynamic_y)

    def convert_window_coordinates(self, x, y):
        """Convert the coordinates from window relative coordinates.

        :Parameters:
            `x`, `y` : float
                The coordinates to convert.

        """
        panel = self
        while panel is not None:
            static_x, static_y = panel.content_offset
            dynamic_x, dynamic_y = panel.dynamic_offset
            x -= (static_x + dynamic_x)
            y -= (static_y + dynamic_y)
            panel = panel.parent
        return x, y

    def convert_root_coordinates(self, x, y):
        panel = self
        while panel.parent is not None:
            static_x, static_y = panel.content_offset
            dynamic_x, dynamic_y = panel.dynamic_offset
            x -= (static_x + dynamic_x)
            y -= (static_y + dynamic_y)
            panel =panel.parent
        return x, y

    def contains_coordinates(self, x, y):
        """Determine whether some coordinates are in the panel.

        :Parameters:
            `x`, `y` : float
                The coordinates to test.

        """
        frame_x, frame_y = self.frame_offset
        frame_x -= self.scroll_xoffset
        frame_y -= self.scroll_yoffset
        frame_w, frame_h = self.frame_size
        return frame_x <= x < frame_x + frame_w and \
               frame_y <= y < frame_y + frame_h

    def contains_window_coordinates(self, x, y):
        """Determine whether some window relative coordinates are in the panel.

        :Parameters:
            `x`, `y` : float
                The coordinates to test.

        """
        x, y = self.convert_window_coordinates(x, y)
        return self.contains_coordinates(x, y)

    def set_handler(self, name, func, *args):
        """Create a signal handler for the given signal.

        Additional arguments are passed to the function.

        :Parameters:
            `name` : str
                The name of the signal
            `func` : function
                The function to call.

        """
        setattr(self, name, lambda *a: func(*args) or True)
        return self

    def process_signal(self, name, *args):
        """Recurse a signal down the panel tree.

        Additional arguments are passed to the signal handler.

        :Parameters:
            `name` : str
                The name of the signal.

        """
        if self._visible:
            for child in reversed(list(self.children)):
                result = child.process_signal(name, *args)
                if result is not None:
                    return result
            if hasattr(self, name):
                if __metapod_debug__:
                    self.report_signal(name, *args)
                return getattr(self, name)(*args)

    def process_mouse_signal(self, name, x, y, *args):
        """Recurse a mouse signal down the panel tree.

        Additional arguments are passed to the signal handler.

        :Parameters:
            `name` : str
                The name of the signal.
            `x`, `y` : float
                The coordinates of the signal.

        """
        if self._visible:
            x, y = self.convert_coordinates(x, y)
            for child in reversed(list(self.children)):
                result = child.process_mouse_signal(name, x, y, *args)
                if result is not None:
                    return result
            if hasattr(self, name):
                if __metapod_debug__:
                    self.report_signal(name, x, y, *args)
                return getattr(self, name)(x, y, *args)

    def process_contained_signal(self, name, x, y, *args):
        """Recurse a mouse signal through panels which contain it.

        Additional arguments are passed to the signal handler.

        :Parameters:
            `name` : str
                The name of the signal.
            `x`, `y` : float
                The coordinates of the signal.
        """
        if self._visible:
            x, y = self.convert_coordinates(x, y)
            for child in reversed(list(self.children)):
                result = child.process_contained_signal(name, x, y, *args)
                if result is not None:
                    return result
            if hasattr(self, name) and self.contains_coordinates(x, y):
                if __metapod_debug__:
                    self.report_signal(name, x, y, *args)
                return getattr(self, name)(x, y, *args)

    def report_signal(self, name, *args):
        """Print the given signal and arguments to standard output.

        :Parameters:
            `name` : str
                The name of the signal.

        """
        formats = { float: "%.1f", long: "%.1f", int: "%.1f",
                    unicode: "%r", str: "%r" }
        subs = [formats.get(type(arg), "%r") for arg in args]
        print "%r -- %s(%s)" % (self, name, ", ".join(subs)) % args

    def get_directional_panel(self, child, direction, wrap=False):
        """Return the panel in a given direction for the given child.

        :Parameters:
            `child` : Panel
                The child panel used as a reference point.
            `direction` : int
                The orthogonal direction in which to look (0 = left, 1 = down,
                2 = right, 3 = up).
            `wrap` : bool
                Whether to wrap between the left and right and the top and
                bottom.

        """
        idx = self._children.index(child)
        if direction in (LEFT, UP):
            idx -= 1
        elif direction in (DOWN, RIGHT):
            idx += 1
        if wrap:
            return idx % len(self._children)
        else:
            return max(0, min(len(self._children) - 1, idx))

    ## Scrolling
    ############

    @Cached
    def scroll_bounds(self):
        cwidth, cheight = self.content_size
        vwidth, vheight = self.view_size
        scroll_xmin = (vwidth - cwidth) * (1 - self._sym(self.halign))
        scroll_xmax = (cwidth - vwidth) * self._sym(self.halign)
        scroll_ymin = 0#(vheight - cheight) * (1 - self._sym(self.valign))
        scroll_ymax = (cheight - vheight)# * self._sym(self.valign)
        return scroll_xmin, scroll_xmax, scroll_ymin, scroll_ymax

    def scroll_by(self, steps_x, steps_y):
        scroll_xmin, scroll_xmax, scroll_ymin, scroll_ymax = self.scroll_bounds
        vwidth, vheight = self.view_size
        if steps_x != 0 and self.scroll_horizontal:
            xoffset = self.scroll_xoffset
            xoffset += steps_x * self.scroll_sensitivity * vheight
            self.scroll_xoffset = max(scroll_xmin, min(scroll_xmax, xoffset))
        if steps_y != 0 and self.scroll_vertical:
            yoffset = self.scroll_yoffset
            yoffset -= steps_y * self.scroll_sensitivity * vheight
            self.scroll_yoffset = max(scroll_ymin, min(scroll_ymax, yoffset))

    def scroll_relative(self, relative_x=None, relative_y=None):
        scroll_xmin, scroll_xmax, scroll_ymin, scroll_ymax = self.scroll_bounds
        if relative_x is not None and self.scroll_horizontal:
            xoffset = relative_x * (scroll_xmax - scroll_xmin)
            self.scroll_xoffset = scroll_xmin + xoffset
        if relative_y is not None and self.scroll_vertical:
            yoffset = relative_y * (scroll_ymax - scroll_ymin)
            self.scroll_yoffset = scroll_ymin + yoffset

    def scroll_child(self, child):
        scroll_xmin, scroll_xmax, scroll_ymin, scroll_ymax = self.scroll_bounds
        cwidth, cheight = self.content_size
        vwidth, vheight = self.view_size
        offsetx, offsety = child.content_offset
        chwidth, chheight = child.content_size
        if self.scroll_horizontal:
            scroll_xmax = cwidth - offsetx - chwidth + scroll_xmin
            scroll_xmin = cwidth - offsetx - vwidth + scroll_xmin
            if self.scroll_xoffset < scroll_xmin:
                self.scroll_xoffset = scroll_xmin
            elif self.scroll_xoffset > scroll_xmax:
                self.scroll_xoffset = scroll_xmax
        if self.scroll_vertical:
            scroll_ymax = cheight - offsety - chheight + scroll_ymin
            scroll_ymin = cheight - offsety - vheight + scroll_ymin
            if self.scroll_yoffset < scroll_ymin:
                self.scroll_yoffset = scroll_ymin
            elif self.scroll_yoffset > scroll_ymax:
                self.scroll_yoffset = scroll_ymax

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.scroll_by(scroll_x, scroll_y)

    ## Rendering
    ############

    @property
    def scissor_offset(self):
        """The dynamic offset of the panel's scissor box.

        """
        if self.parent is not None:
            parent_x, parent_y = self.parent.scissor_offset
            dynamic_x, dynamic_y = self.dynamic_offset
            return parent_x + dynamic_x - self.scroll_xoffset, \
                   parent_y + dynamic_y - self.scroll_yoffset
        return self.dynamic_offset

    @Cached
    def scissor_shape(self):
        """The shape of the scissor rectangle.

        """
        ox, oy = self.cumulative_offset
        fx, fy = self.frame_offset
        fw, fh = self.frame_size
        scx = int(math.floor(ox+fx))
        scy = int(math.floor(oy+fy))
        scw = int(math.floor(ox+fx+fw)) - scx
        sch = int(math.floor(oy+fy+fh)) - scy
        while self.parent is not None:
            if self.parent.scissor:
                pscx, pscy, pscw, psch = self.parent.scissor_shape
                scw = min(scx + scw, pscx + pscw)
                sch = min(scy + sch, pscy + psch)
                scx = max(scx, pscx)
                scy = max(scy, pscy)
                scw = scw - scx
                sch = sch - scy
                break
            else:
                self = self.parent
        return scx, scy, scw, sch

    @Cached
    def frame_vlist(self):
        """The vertex list used to render the frame texture.

        """
        # Frame dimensions.
        fw, fh = self.frame_size
        t = self.frame_width * self.root.content_size[1] / 2

        # Cell processing order.
        frame_cells = [(0, 0), (1, 0), (2, 0), (2, 1),
                       (2, 2), (1, 2), (0, 2), (0, 1)]
        cell_offsets = [(0, 0), (1, 0), (1, 1), (0, 1)]

        # Texture dimensions.
        if self.frame_texture is not None:
            tx, ty = self.frame_texture.tex_coords[:2]
            tw = self.frame_texture.tex_coords[6] - tx
            th = self.frame_texture.tex_coords[7] - ty
        elif self.frame_color is not None:
            tx = ty = tw = th = 0.0

        # Utility mappings.
        txmap = {0: tx,   1: tx+tw/2,   2: tx+tw/2,   3: tx+tw}
        tymap = {0: ty,   1: ty+th/2,   2: ty+th/2,   3: ty+th}
        vxmap = {0: -t,   1:       t,   2:    fw-t,   3:  fw+t}
        vymap = {0: -t,   1:       t,   2:    fh-t,   3:  fh+t}

        # Create data arrays.
        cdata, tdata, vdata = [255] * 128, [], []
        for cx, cy in frame_cells:
            for ox, oy in cell_offsets:
                # Extend data arrays.
                tdata.extend([txmap[cx+ox], tymap[cy+oy]])
                vdata.extend([vxmap[cx+ox], vymap[cy+oy]])
        if self.frame_color is not None:
            cdata = [int(255 * x) for x in self.frame_color] * 32


        # Create and return vertex list.
        if self.frame_texture is not None:
            return pyglet.graphics.vertex_list(32, ('c4B', cdata),
                                                   ('t2f', tdata),
                                                   ('v2f', vdata),)
        elif self.frame_color is not None:
            return pyglet.graphics.vertex_list(32, ('c4B', cdata),
                                                   ('v2f', vdata),)

    @Cached
    def background_vlist(self):
        """The vertex list used to render the background texture.

        """
        fw, fh = self.frame_size
        cdata, tdata, vdata = [255] * 16, [], []

        # Texture dimensions.
        if self.background_texture is not None:
            tx, ty = self.background_texture.tex_coords[:2]
            tw = self.background_texture.tex_coords[6] - tx
            th = self.background_texture.tex_coords[7] - ty
        elif self.background_color is not None:
            tx = ty = tw = th = 0.0

        # Color data.
        if self.background_color is not None:
            cdata = [int(255 * x) for x in self.background_color] * 4

        if self.background_tiles is not None:
            th = self.background_tiles
            tw = th * fw / fh

        tdata = [tx, ty, tx + tw, ty, tx + tw, ty + th, tx, ty + th]
        vdata = [0, 0, fw, 0, fw, fh, 0, fh]

        # Create and return vertex list.
        if self.background_texture is not None:
            return pyglet.graphics.vertex_list(4, ('c4B', cdata),
                                                  ('t2f', tdata),
                                                  ('v2f', vdata),)
        else:
            return pyglet.graphics.vertex_list(4, ('c4B', cdata),
                                                  ('v2f', vdata),)

    def draw_frame(self):
        """Render the panel frame.

        """
        texture = self.frame_texture
        if texture is not None:
            glPushAttrib(GL_TEXTURE_BIT)
            glEnable(texture.target)
            glBindTexture(texture.target, texture.id)
        self.frame_vlist.draw(GL_QUADS)
        if texture is not None:
            glPopAttrib()

    def draw_background(self):
        """Render the panel background.

        """
        texture = self.background_texture
        if texture is not None:
            glPushAttrib(GL_TEXTURE_BIT)
            glEnable(texture.target)
            glBindTexture(texture.target, texture.id)
        self.background_vlist.draw(GL_QUADS)
        if texture is not None:
            glPopAttrib()

    def draw(self):
        """Render the panel and child panels.

        """
        # Shortcut if disabled.
        if not self._visible:
            return

        # Offset to content corner.
        glPushMatrix()
        ox, oy = self.content_offset
        dx, dy = self.dynamic_offset
        glTranslatef(ox + dx, oy + dy, 0.0)

        # Flag to track scissor.
        _have_set_scissor = False

        # Clean computations.
        width, height = self.content_size

        # Render the background.
        if (self.background_texture is not None) or \
           (self.background_color is not None):
            glPushMatrix()
            fx, fy = self.frame_offset
            fx -= self.scroll_xoffset
            fy -= self.scroll_yoffset
            glTranslatef(fx, fy, 0.0)
            self.draw_background()
            glPopMatrix()

        # Set scissor state.
        if self.scissor:
            _have_set_scissor = True
            glPushAttrib(GL_SCISSOR_BIT)
            scx, scy, scw, sch = self.scissor_shape
            ox, oy = self.scissor_offset
            glScissor(scx + ox, scy + oy, scw, sch)
            glEnable(GL_SCISSOR_TEST)

        # Render the content.
        self.draw_content()

        # Render the children.
        children = list(self.children)
        children.sort(key=lambda c: c.order)
        for child in children:
                child.draw()

        # Unset scissor state.
        if _have_set_scissor:
            glPopAttrib()

        # Render the frame.
        if (self.frame_texture is not None) or \
           (self.frame_color is not None):
            glPushMatrix()
            fx, fy = self.frame_offset
            fx -= self.scroll_xoffset
            fy -= self.scroll_yoffset
            glTranslatef(fx, fy, 0.0)
            self.draw_frame()
            glPopMatrix()

        # Render debug rectangles.
        if __metapod_debug__:
            if Panel._debug_focus_panel is self:
                cw, ch = self.content_size
                fx, fy = self.frame_offset
                fx -= self.scroll_xoffset
                fy -= self.scroll_yoffset
                fw, fh = self.frame_size
                _rect_test(0, 0, cw, ch, (1, 0, 0, 1))
                _rect_test(fx, fy, fw, fh, (0, 1, 0, 1))

        glPopMatrix()

    ## Debug
    ########

    if __metapod_debug__:
        _debug_focus_panel = None
        def debug_focus(self, x, y):
            Panel._debug_focus_panel = self
            return True

Panel.child_class = Panel


## LAYOUT PANEL IMPLEMENTATIONS ###############################################

class Horizontal(Panel):
    """Layout children horizontally.

    """

    is_layout = True

    spacing = Attribute(0.0) # rel: layout.height

    def get_directional_panel(self, child, direction, wrap=False):
        idx = self._children.index(child)
        if direction == LEFT:
            idx -= 1
        elif direction == RIGHT:
            idx += 1
        if wrap:
            return idx % len(self._children)
        else:
            return max(0, min(len(self._children) - 1, idx))

    def compute_content_size(self):
        lwidth, lheight = self.layout_size
        spacing = self.spacing * lheight
        current_width = max_height = 0.0
        for child in self.children:
            child.halign = "left"
            child.anchor_x = None
            child.layout_xoffset = current_width
            cwidth, cheight = child.content_size
            current_width += cwidth + spacing
            max_height = max(max_height, cheight)
        return max(0.0, current_width - spacing), max_height


class Vertical(Panel):
    """Layout children vertically.

    """

    is_layout = True

    spacing = Attribute(0.0) # rel: layout.height

    def get_directional_panel(self, child, direction, wrap=False):
        idx = self._children.index(child)
        if direction == UP:
            idx -= 1
        elif direction == DOWN:
            idx += 1
        if wrap:
            return idx % len(self._children)
        else:
            return max(0, min(len(self._children) - 1, idx))

    def compute_content_size(self):
        lwidth, lheight = self.layout_size
        spacing = self.spacing * lheight
        current_height = max_width = 0.0
        for child in reversed(self.children):
            child.valign = "bottom"
            child.anchor_y = None
            child.layout_yoffset = current_height
            cwidth, cheight = child.content_size
            current_height += cheight + spacing
            max_width = max(max_width, cwidth)
        return max_width, max(0.0, current_height - spacing)


class Grid(Panel):
    """Layout children in a fixed width grid.

    """

    is_layout = True

    spacing = Attribute(0.0) # rel: layout.height
    grid_width = Attribute(5, dtype=int)

    def get_directional_panel(self, child, direction, wrap=False):
        idx = self._children.index(child)
        row, col = divmod(idx, self.grid_width)
        numrows = -(len(self._children) // -self.grid_width)
        if direction == LEFT:
            col -= 1
        elif direction == RIGHT:
            col += 1
        elif direction == UP:
            row -= 1
        elif direction == DOWN:
            row += 1
        if wrap:
            row = row % numrows
            col = col % self.grid_width
        else:
            row = max(0, min(numrows - 1, row))
            col = max(0, min(self.grid_width - 1, col))
        idx = row * self.grid_width + col
        return max(0, min(len(self._children) - 1, idx))

    def compute_content_size(self):
        rows = [0.0] * -(len(self.children) // -self.grid_width)
        cols = [0.0] * self.grid_width
        for idx, child in enumerate(self.children):
            child.anchor_x = child.anchor_y = None
            cwidth, cheight = child.content_size
            row, col = divmod(idx, self.grid_width)
            row = len(rows) - row - 1
            rows[row] = max(cheight, rows[row])
            cols[col] = max(cwidth, cols[col])
        lwidth, lheight = self.layout_size
        spacing = self.spacing * lheight
        for idx, child in enumerate(self.children):
            row, col = divmod(idx, self.grid_width)
            row = len(rows) - row - 1
            child.layout_width = cols[col]
            child.layout_height = rows[row]
            child.layout_xoffset = sum(cols[:col]) + spacing * col
            child.layout_yoffset = sum(rows[:row]) + spacing * row
        return sum(cols) + spacing * (len(cols) - 1), \
               sum(rows) + spacing * (len(rows) - 1)



## CONTENT PANEL IMPLEMENTATIONS ##############################################

class Root(Panel):
    """Panel for attaching a window.

    """

    window = Attribute(None)

    @Cached
    def parent_size(self):
        if self.window is None:
            return (0.0, 0.0)
        return self.window.get_size()

    @Cached
    def layout_size(self):
        if self.window is None:
            return (0.0, 0.0)
        return self.window.get_size()

    def draw(self):
        if self.layout_size != self.window.get_size():
            self._clear_cached_attributes()
        super(Root, self).draw()


class Color(Panel):
    """Panel containing a block of color.

    """

    color = Attribute((0.4, 0.4, 0.8, 0.5))

    def draw_content(self):
        width, height = self.content_size
        cattr = 'c%dB' % len(self.color)
        cdata = [int(255 * x) for x in self.color] * 4
        vdata = [0.0, 0.0, width, 0.0, width, height, 0.0, height]
        pyglet.graphics.draw(4, GL_QUADS, ('v2f', vdata), (cattr, cdata))


class Text(Panel):
    """Panel containing some text.

    """

    font_name = Attribute(None)
    font_size = Attribute(0.08) # rel: root.height
    color = Attribute((1.0, 1.0, 1.0, 1.0))
    italic = Attribute(False)
    bold = Attribute(False)
    align = Attribute("center")
    text = Attribute(u"")

    def init_panel(self):
        self.document = d = pyglet.text.document.UnformattedDocument()
        self.layout = pyglet.text.layout.IncrementalTextLayout(d, 0, 0)

    def compute_content_size(self):
        self.layout.begin_update()
        self.layout.content_width = 0 # Do not remove this line... seriously!
        rcwidth, rcheight = self.root.content_size
        mvwidth, mvheight = self.max_view_size
        self.document.set_style(0, 0, {
            "font_name" : self.font_name,
            "font_size" : int(self.font_size * rcheight),
            "color" : [int(255 * x) for x in self.color],
            "italic" : self.italic,
            "bold" : self.bold,
            "align" : self.align})
        self.document.text = self.text
        self.layout.x = self.layout.y = 0
        self.layout.width = mvwidth
        self.layout.height = mvheight
        self.layout.content_valign = "bottom"
        self.layout.multiline = True
        self.layout.end_update()
        return self.layout.content_width, \
               self.layout.content_height

    def draw_content(self):
        glPushMatrix()
        blank_width = self.layout.width - self.layout.content_width
        offset = -self._symbol_factors[self.align] * blank_width
        glTranslatef(offset, 0.0, 0.0)
        self.layout.draw()
        glPopMatrix()


class Image(Panel):
    """Panel containing an image.

    """

    image = Attribute(None)
    fade = Attribute(1.0)
    color = Attribute(None)
    scale = Attribute(1.0)
    constrain = Attribute(True, dtype=bool)
    grey = False

    def compute_content_size(self):
        width, height = self.max_view_size
        if self.image:
            if self.constrain:
                iwidth = self.image.width
                iheight = self.image.height
                iaspect = iwidth / iheight
                if width < height * iaspect:
                    height = width / iaspect
                elif width >= height * iaspect:
                    width = height * iaspect
        return width, height

    def draw_content(self):
        if self.image:
            cwidth, cheight = self.content_size
            scale_x = cwidth / self.image.width
            scale_y = cheight / self.image.height
            glPushAttrib(GL_ALL_ATTRIB_BITS)
            if self.color:
                glColor3f(*self.color)
            else:
                glColor4f(1, 1, 1, self.fade)
            glPushMatrix()
            glScalef(scale_x, scale_y, 1.0)
            glTranslatef(self.image.width/2, self.image.height/2,0)
            glScalef(self.scale, self.scale, 1.0)
            glTranslatef(-self.image.width/2, -self.image.height/2,0)
            self.image.blit(0, 0)
            glPopMatrix()
            glPopAttrib()


class Camera(Panel):
    """Panel containing a world view under a camera transform.

    """

    world_height = Attribute(480.0, dynamic=True)
    world_angle = Attribute(90.0, dynamic=True)
    draw_world = Attribute((lambda: None), dynamic=True)

    camera_anchor_x = Attribute("center", dynamic=True)
    camera_anchor_y = Attribute("center", dynamic=True)
    camera_xoffset = Attribute(0.0, dynamic=True)
    camera_yoffset = Attribute(0.0, dynamic=True)
    camera_zoom = Attribute(1.0, dynamic=True)
    camera_angle = Attribute(0.0, dynamic=True)

    def transform_coordinates(self, x, y):
        cwidth, cheight = self.content_size
        anchor_x = cwidth * self._sym(self.camera_anchor_x)
        anchor_y = cheight * self._sym(self.camera_anchor_y)
        scale = cheight * self.camera_zoom / self.world_height
        angle = math.radians(-self.camera_angle + self.world_angle)
        cos, sin = math.cos(angle), math.sin(angle)
        xoffset = -self.camera_xoffset
        yoffset = -self.camera_yoffset
        x = (x - anchor_x) / scale
        y = (y - anchor_y) / scale
        return x * +cos + y * +sin - xoffset, \
               x * -sin + y * +cos - yoffset

    def transform_window_coordinates(self, x, y):
        x, y = self.convert_window_coordinates(x, y)
        return self.transform_coordinates(x, y)

    def transform_root_coordinates(self, x, y):
        x, y = self.convert_root_coordinates(x, y)
        return self.transform_coordinates(x, y)

    def draw_content(self):
        cwidth, cheight = self.content_size
        anchor_x = cwidth * self._sym(self.camera_anchor_x)
        anchor_y = cheight * self._sym(self.camera_anchor_y)
        scale = cheight * self.camera_zoom / self.world_height
        angle = -self.camera_angle + self.world_angle
        cos, sin = math.cos(angle), math.sin(angle)
        xoffset = -self.camera_xoffset
        yoffset = -self.camera_yoffset
        glPushMatrix()
        glTranslatef(anchor_x, anchor_y, 0.0)
        glScalef(scale, scale, 1.0)
        glRotatef(angle, 0.0, 0.0, 1.0)
        glTranslatef(xoffset, yoffset, 0.0)
        self.draw_world()
        glPopMatrix()


class MenuItem(Panel):

    callback = Attribute(None)

    def focus(self):
        pass

    def unfocus(self):
        pass

    def select(self):
        pass

    def unselect(self):
        pass

    def activate(self):
        if self.callback is None:
            self.parent.change_selected(self)
        else:
            try:
                function = self.callback[0]
                args = self.callback[1:]
                function(*args)
            except TypeError:
                self.callback()


class Menu(Panel):

    item_options = Attribute({})

    child_class = MenuItem

    def init_panel(self):
        super(Menu, self).init_panel()
        self._focused = None
        self._selected = []

    def add(self, child=None, **kwds):
        kwds = dict(self.item_options, **kwds)
        return super(Menu, self).add(child, **kwds)

    def change_focused(self, child):
        if self._focused is not None:
            self._focused.unfocus()
            self._focused = None
        if child is not None:
            self._focused = child
            self._focused.focus()

    def change_selected(self, child):
        if child in self._selected:
            if child.unselect() is not False:
                self._selected.remove(child)
        elif child.select() is not False:
            self._selected.append(child)
        self.change_focused(self._focused)

    #def on_key_press(self, symbol, modifiers):
    #    if self._focused is None:
    #        self.change_focused(self.children[0])
    #    elif symbol in (LEFT, DOWN, RIGHT, UP):
    #        idx = self.get_directional_panel(self._focused, symbol, False)
    #        self.change_focused(self._children[idx])

    def on_mouse_motion(self, x, y, dx, dy):
        for child in self.children:
            cx, cy = child.convert_coordinates(x, y)
            if child.contains_coordinates(cx, cy):
                self.change_focused(child)
                break
        else:
            self.change_focused(None)

    def on_mouse_release(self, x, y, button, modifiers):
        for child in self.children:
            cx, cy = child.convert_coordinates(x, y)
            if child.contains_coordinates(cx, cy):
                child.activate()
                break


## DEFAULT PANEL EVENT HANDLER ################################################

class Handler(object):
    """Panel event-signal conversion object.

    """

    ## Constructor
    ##############

    def __init__(self, root=None):
        """Create a Handler object.

        :Parameters:
            `root` : interface.panel.Panel
                The panel at the root of the panel tree.

        """
        self.root = root

    ## Event handlers
    #################

    @staticmethod
    def report_event():

        # Frame introspection.
        event_frame = sys._getframe().f_back
        event_name = event_frame.f_code.co_name
        event_varnames = event_frame.f_code.co_varnames
        event_vars = event_frame.f_locals

        # Alternative 'repr' functions.
        from pyglet.window import key, mouse
        reprs = { "modifiers" : key.modifiers_string,
                  "motion"    : key.motion_string,
                  "symbol"    : key.symbol_string,
                  "button"    : mouse.buttons_string,
                  "buttons"   : mouse.buttons_string, }

        # Construct argument lists.
        arguments = []
        for name in event_varnames[1:]:
            value = reprs.get(name, repr)(event_vars[name])
            arguments.append("%s=%s" % (name, value))

        # Print event.
        print "%s(%s)" % (event_name, ", ".join(arguments))

    def on_key_press(self, symbol, modifiers):
        """Process the 'on_key_press' event.

        """
        if self.root.process_signal("on_key_press", symbol, modifiers):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def on_key_release(self, symbol, modifiers):
        """Process the 'on_key_release' event.

        """
        if self.root.process_signal("on_key_release", symbol, modifiers):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Process the 'on_mouse_drag' event.

        """
        if self.root.process_mouse_signal("on_mouse_drag", x, y, dx, dy,
                buttons, modifiers):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def on_mouse_enter(self, x, y):
        """Process the 'on_mouse_enter' event.

        """
        return pyglet.event.EVENT_UNHANDLED

    def on_mouse_leave(self, x, y):
        """Process the 'on_mouse_leave' event.

        """
        return pyglet.event.EVENT_UNHANDLED

    def on_mouse_motion(self, x, y, dx, dy):
        """Process the 'on_mouse_motion' event.

        """
        if __metapod_debug__:
            self.root.process_contained_signal("debug_focus", x, y)
        if self.root.process_mouse_signal("on_mouse_motion", x, y, dx, dy):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def on_mouse_press(self, x, y, button, modifiers):
        """Process the 'on_mouse_press' event.

        """
        if self.root.process_contained_signal("on_mouse_press", x, y, button,
                modifiers):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def on_mouse_release(self, x, y, button, modifiers):
        """Process the 'on_mouse_release' event.

        """
        if self.root.process_contained_signal("on_mouse_release", x, y, button,
                modifiers):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Process the 'on_mouse_scroll' event.

        """
        if self.root.process_contained_signal("on_mouse_scroll", x, y, scroll_x,
                scroll_y):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def on_text(self, text):
        """Process the 'on_text' event.

        """
        if self.root.process_signal("on_text", text):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def on_text_motion(self, motion):
        """Process the 'on_text_motion' event.

        """
        if self.root.process_signal("on_text_motion", motion):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED

    def on_text_motion_select(self, motion):
        """Process the 'on_text_motion_select' event.

        """
        if self.root.process_signal("on_text_motion_select", motion):
            return pyglet.event.EVENT_HANDLED
        return pyglet.event.EVENT_UNHANDLED


if __name__ == "__main__":

    import __main__ as interface

    import pyglet
    from pyglet.gl import *

    class MyMenuItem(interface.MenuItem, interface.Text):

        focus_color = interface.Attribute((1, 1, 0, 1))
        unfocus_color = interface.Attribute((1, 1, 1, 1))

        def focus(self):
            self.color = self.focus_color
            self.parent.scroll_child(self)

        def unfocus(self):
            self.color = self.unfocus_color

        def select(self):
            self.focus_color = (1, 0, 0, 1)
            self.unfocus_color = (1, 0, 1, 1)

        def unselect(self):
            self.focus_color = (1, 1, 0, 1)
            self.unfocus_color = (1, 1, 1, 1)

    class MyMenu(interface.Menu, interface.Vertical):

        child_class = MyMenuItem

    class Test(object):

        def __init__(self, width, height):

            self.window = pyglet.window.Window(width, height)

            # Create the root panel.
            self.root = interface.Root(
                    aspect = (16, 9),
                    background_color = (0.4, 0.4, 1.0, 0.5),
                    scissor = True,
                    window = self.window,
                    )

            # Create the menu panel.
            self.menu = self.root.add(MyMenu,
                    halign = 0.3,
                    item_options = dict(
                        font_size = 0.08,
                        font_name = "Gill Sans",
                        text = u"<default>",
                        ),
                    )

            # Populate the menu panel.
            self.menu.add(MyMenuItem, text="Item 1")
            self.menu.add(MyMenuItem, text="Item 2")
            self.menu.add(MyMenuItem, text="Item 3")
            self.menu.add(MyMenuItem, text="Item 4")
            self.menu.add(MyMenuItem, text="Item 5")
            self.menu.add(MyMenuItem, text="Item 6")
            self.menu.add(MyMenuItem, text="Item 7")
            self.menu.add(MyMenuItem, text="Item 8")
            self.menu.add(MyMenuItem, text="Item 9")
            self.menu.add(MyMenuItem, text="Item 10")
            self.menu.add(MyMenuItem, text="Item 11")
            self.menu.add(MyMenuItem, text="Item 12")
            self.menu.add(MyMenuItem, text="Item 13")
            self.menu.add(MyMenuItem, text="Item 14")
            self.menu.add(MyMenuItem, text="Item 15")

            self.handler = interface.Handler(self.root)
            self.window.push_handlers(self.handler)
            self.window.push_handlers(self)

            pyglet.clock.schedule(self.update)
            self.fps = pyglet.clock.ClockDisplay()

        def update(self, dt):
            pass

        def on_draw(self):
            self.window.clear()
            self.root.draw()
            self.fps.draw()

    test = Test(640, 480)
    pyglet.app.run()
