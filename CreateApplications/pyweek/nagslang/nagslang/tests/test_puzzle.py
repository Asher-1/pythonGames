from unittest import TestCase

from nagslang.constants import COLLISION_TYPE_OTHER, SWITCH_PUSHERS
from nagslang import puzzle


class FakeShape(object):
    def __init__(self, collision_type=COLLISION_TYPE_OTHER):
        self.collision_type = collision_type


class FakeSpace(object):
    def __init__(self, *shapes):
        self._shapes = shapes

    def shape_query(self, shape):
        return self._shapes


class FakeGameObject(object):
    def __init__(self, shape, space):
        self._shape = shape
        self._space = space

    def get_shape(self):
        return self._shape

    def get_space(self):
        return self._space


class FakePuzzler(puzzle.Puzzler):
    def __init__(self, fake_state):
        self.fake_state = fake_state

    def get_state(self):
        return self.fake_state


class TestPuzzles(TestCase):
    def mkpuzzler(self, gobj, cls, *args, **kw):
        puzzler = cls(*args, **kw)
        puzzler.set_game_object(gobj)
        return puzzler

    def assert_collide_state(self, expected, shapes, collision_types):
        gobj = FakeGameObject(None, FakeSpace(*shapes))
        puzzler = self.mkpuzzler(
            gobj, puzzle.CollidePuzzler, *collision_types)
        self.assertEqual(expected, puzzler.get_state())

    def test_collide_puzzler(self):
        self.assert_collide_state(False, [], [])
        self.assert_collide_state(False, [FakeShape()], SWITCH_PUSHERS)

        for collision_type in SWITCH_PUSHERS:
            self.assert_collide_state(
                True, [FakeShape(collision_type)], SWITCH_PUSHERS)
            self.assert_collide_state(
                True, [FakeShape(), FakeShape(collision_type)], SWITCH_PUSHERS)

    def test_state_proxy_puzzler(self):
        glue = puzzle.PuzzleGlue()
        puzzler = puzzle.StateProxyPuzzler('faker')
        glue.add_component('puzzler', puzzler)
        faker = FakePuzzler('foo')
        glue.add_component('faker', faker)

        self.assertEqual('foo', puzzler.get_state())
        faker.fake_state = 'bar'
        self.assertEqual('bar', puzzler.get_state())

    def test_glue_add_component(self):
        glue = puzzle.PuzzleGlue()
        puzzler = FakePuzzler('foo')
        gobj = FakeGameObject(None, None)
        gobj.puzzler = FakePuzzler('bar')

        self.assertEqual({}, glue._components)
        glue.add_component('foo', puzzler)
        self.assertEqual({'foo': puzzler}, glue._components)
        glue.add_component('bar', gobj)
        self.assertEqual(
            {'foo': puzzler, 'bar': gobj.puzzler}, glue._components)
