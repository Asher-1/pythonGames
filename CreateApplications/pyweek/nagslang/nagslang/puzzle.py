from nagslang.constants import COLLISION_TYPE_PLAYER


def get_editable_puzzlers():
    classes = []
    for cls_name, cls in globals().iteritems():
        if isinstance(cls, type) and hasattr(cls, 'requires'):
            classes.append((cls_name, cls))
    return classes


class PuzzleGlue(object):
    """Glue that holds bits of a puzzle together.
    """
    def __init__(self):
        self._components = {}

    def add_component(self, name, puzzler):
        if not isinstance(puzzler, Puzzler):
            puzzler = puzzler.puzzler
            if puzzler is None:
                # We've got a name, but no puzzler,
                # so we shouldn't actually be stuck
                # in here
                return
        self._components[name] = puzzler
        puzzler.set_glue(self)

    def get_state_of(self, name):
        return self._components[name].get_state()


class Puzzler(object):
    """Behaviour specific to a puzzle component.
    """
    def set_glue(self, glue):
        self.glue = glue

    def set_game_object(self, game_object):
        self.game_object = game_object

    def get_state(self):
        raise NotImplementedError()

    @classmethod
    def requires(cls):
        """Tell the level editor the arguments we require

           Format is a list of name: type hint tuples"""
        return [("name", "string")]


class YesPuzzler(Puzzler):
    """Yes sir, I'm always on.
    """
    def get_state(self):
        return True


class NoPuzzler(Puzzler):
    """No sir, I'm always off.
    """
    def get_state(self):
        return False


class CollidePuzzler(Puzzler):
    def __init__(self, *collision_types):
        if not collision_types:
            collision_types = (COLLISION_TYPE_PLAYER,)
        self._collision_types = collision_types

    def get_interior_colliders(self):
        space = self.game_object.get_space()
        my_shape = self.game_object.get_shape()
        shapes = [shape for shape in space.shapes
                  if shape.collision_type in self._collision_types]
        return set(shape for shape in shapes
                   if my_shape in space.point_query(shape.body.position))

    def get_colliders(self):
        space = self.game_object.get_space()
        my_shape = self.game_object.get_shape()
        shapes = set(shape for shape in space.shape_query(my_shape)
                     if shape.collision_type in self._collision_types)
        shapes.update(self.get_interior_colliders())
        return shapes

    def get_state(self):
        return bool(self.get_colliders())

    @classmethod
    def requires(cls):
        return [("name", "string"), ("collision_types", "list of ints")]


class MultiCollidePuzzler(CollidePuzzler):
    def __init__(self, min_count, *collision_types):
        self._min_count = min_count
        super(MultiCollidePuzzler, self).__init__(*collision_types)

    def get_state(self):
        return len(self.get_colliders()) >= self._min_count

    @classmethod
    def requires(cls):
        return [("name", "string"), ("min_count", "int"),
                ("collision_types", "list of ints")]


class ParentAttrPuzzler(Puzzler):
    def __init__(self, attr_name):
        self._attr_name = attr_name

    def get_state(self):
        return getattr(self.game_object, self._attr_name)

    @classmethod
    def requires(cls):
        return [("name", "string"), ("attr_name", "string")]


class StateProxyPuzzler(Puzzler):
    def __init__(self, state_source):
        self._state_source = state_source

    def get_state(self):
        return self.glue.get_state_of(self._state_source)

    @classmethod
    def requires(cls):
        return [("name", "string"), ("sources", "list of names")]


class StateLogicalAndPuzzler(Puzzler):
    def __init__(self, *state_sources):
        self._state_sources = state_sources

    def get_state(self):
        for state_source in self._state_sources:
            if not self.glue.get_state_of(state_source):
                return False
        return True

    @classmethod
    def requires(cls):
        return [("name", "string"), ("sources", "list of names")]
