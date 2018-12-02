from unittest import TestCase

from StringIO import StringIO

from nagslang import game_object as go
from nagslang import puzzle
from nagslang.level import Level
from nagslang.yamlish import load


class FakeSpace(object):
    def add(self, *objs):
        pass


class TestLevel(TestCase):
    def make_level(self, name, data):
        level = Level(name)
        level._get_data = lambda: data
        return level

    def roundtrip_level(self, level):
        newlevel = Level(level.name)
        f = StringIO()
        level._dump_data(f)
        f.seek(0)
        newlevel._get_data = lambda: load(f)
        return newlevel

    def test_empty_level(self):
        def do_test(level):
            level.load(FakeSpace())
            self.assertEqual((5, 10), level.get_size())
            self.assertEqual([], level.get_walls())
            self.assertEqual([], level.drawables)

        level = self.make_level('foo', {
            'size': [5, 10],
            'base_tile': 'tiles/floor.png',
            'polygons': {},
        })

        do_test(level)
        level2 = self.roundtrip_level(level)
        do_test(level2)

    def test_level_walls(self):
        def do_test(level):
            level.load(FakeSpace())
            self.assertEqual((5, 10), level.get_size())
            self.assertEqual([[(1, 1), (2, 1), (1, 2)]], level.get_walls())
            self.assertEqual([], level.drawables)

        level = self.make_level('foo', {
            'size': [5, 10],
            'base_tile': 'tiles/floor.png',
            'polygons': {
                1: [[1, 1], [2, 1], [1, 2]],
            },
        })
        do_test(level)
        level2 = self.roundtrip_level(level)
        do_test(level2)

    def test_level_game_objects(self):
        def do_test(level):
            level.load(FakeSpace())
            self.assertEqual((5, 10), level.get_size())
            self.assertEqual([], level.get_walls())
            [box, switch] = level.drawables
            self.assertTrue(isinstance(box, go.Box))
            self.assertEqual(box.shape.body.position, (3, 3))
            self.assertTrue(isinstance(switch, go.FloorSwitch))
            self.assertEqual(switch.shape.body.position, (4, 4))

            puzzle_bits = level._glue._components
            self.assertEqual(['foo', 'foo_proxy'],
                             sorted(puzzle_bits.keys()))
            self.assertTrue(
                isinstance(puzzle_bits['foo_proxy'], puzzle.StateProxyPuzzler))
            self.assertEqual('foo', puzzle_bits['foo_proxy']._state_source)
            self.assertTrue(isinstance(puzzle_bits['foo'],
                                       puzzle.CollidePuzzler))

        level = self.make_level('foo', {
            'size': [5, 10],
            'base_tile': 'tiles/floor.png',
            'polygons': {},
            'game_objects': [
                {
                    'classname': 'Box',
                    'args': [[3, 3]],
                },
                {
                    'name': 'foo',
                    'classname': 'FloorSwitch',
                    'args': [[4, 4]],
                },
                {
                    'name': 'foo_proxy',
                    'classname': 'puzzle.StateProxyPuzzler',
                    'args': ['foo'],
                },
            ],
        })

        do_test(level)
        level2 = self.roundtrip_level(level)
        do_test(level2)
