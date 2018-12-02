import pymunk

from nagslang import environment
from nagslang import render
from nagslang.constants import ZORDER_LOW
from nagslang.events import AddDrawableEvent
from nagslang.game_object import (
    GameObject, SingleShapePhysicser, Result, make_body, EphemeralNote)
from nagslang.resources import resources


def get_editable_game_objects():
    classes = []
    for cls_name, cls in globals().iteritems():
        if isinstance(cls, type) and hasattr(cls, 'requires'):
            classes.append((cls_name, cls))
    return classes


class CollectibleGameObject(GameObject):
    zorder = ZORDER_LOW

    def __init__(self, space, name, shape, renderer):
        self._name = name
        self.collected = False
        shape.sensor = True
        super(CollectibleGameObject, self).__init__(
            SingleShapePhysicser(space, shape),
            renderer,
            interactible=environment.Interactible(
                environment.Action(
                    self._collect, environment.HumanFormCondition()),
                environment.Action(self._object)),
        )

    def _collect(self, protagonist):
        protagonist.add_item(self._name)
        self.physicser.remove_from_space()
        self.collected = True

    def _object(self, protagonist):
        AddDrawableEvent.post(EphemeralNote(
            "You can't get a grip on it, but you have no pockets in this form"
            " anyway.", 3))

    def update(self, dt):
        if self.collected:
            return Result(remove=[self])


class Gun(CollectibleGameObject):
    def __init__(self, space, position):
        body = make_body(None, None, position)
        self.shape = pymunk.Circle(body, 20)
        super(Gun, self).__init__(
            space, 'gun', self.shape,
            render.ImageRenderer(resources.get_image('objects', 'gun.png')),
        )

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates")]


class KeyCard(CollectibleGameObject):
    def __init__(self, space, position, name):
        body = make_body(None, None, position)
        self.shape = pymunk.Circle(body, 20)
        super(KeyCard, self).__init__(
            space, name, self.shape,
            render.ImageRenderer(
                resources.get_image('objects', '%s.png' % (name,))),
        )

    @classmethod
    def requires(cls):
        return [("name", "string"), ("position", "coordinates"),
                ("item_name", "string")]
