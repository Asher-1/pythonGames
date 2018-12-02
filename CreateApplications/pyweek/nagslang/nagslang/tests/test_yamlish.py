from unittest import TestCase

from nagslang.yamlish import load_s, dump_s

try:
    import yaml
except ImportError:
    yaml = None  # pyflakes:ignore

try:
    from unittest import SkipTest
except ImportError:
    from pytest import skip
    SkipTest = skip.Exception  # pyflakes:ignore


class TestParse(TestCase):
    def assertParsesAs(self, text, expected):
        self.assertEqual(load_s(text.strip()), expected)

    def test_dict_list_1(self):
        self.assertParsesAs('''
foo:
- bar
- baz
        ''', {'foo': ['bar', 'baz']})

    def test_dict_list_2(self):
        self.assertParsesAs('''
foo:
  - bar
  - baz
        ''', {'foo': ['bar', 'baz']})


class TestRoundTrip(TestCase):
    from_pyyaml = False

    def roundtrip(self, data):
        text = self.dump_s(data)
        print '\n=== Begin ===\n%s\n=== End ===' % text
        self.assertEqual(self.load_s(text), data)

    def dump_s(self, data):
        return dump_s(data)

    def load_s(self, text):
        return load_s(text)

    def test_simple_dict(self):
        self.roundtrip({'foo': 'bar'})

    def test_simple_list(self):
        self.roundtrip(['foo', 'bar'])

    def test_dict_of_dicts(self):
        self.roundtrip({'foo': {'bar': 'baz'}})

    def test_dict_tree(self):
        self.roundtrip({
            'foo': {
                'bar': {
                    'baz': 'qux'
                },
                'quux': 'corge',
            }
        })

    def test_list_of_lists(self):
        self.roundtrip(['foo', ['bar', 'baz'], 'qux'])

    def test_dict_list(self):
        self.roundtrip({
            'foo': ['bar', 'baz'],
        })

    def test_list_dict(self):
        self.roundtrip([
            {'foo': 'bar'},
            {'baz': 'qux', 'quux': 'corge'},
        ])

    def test_nested_lists(self):
        self.roundtrip({
            'foo': [['bar', 'baz', 'qux'], 'quux'],
        })

    def test_list_of_dicts(self):
        self.roundtrip({
            'foo': [
                {'bar': 'baz'},
                {'qux': 'quux'},
            ],
        })

    def test_int_dict(self):
        self.roundtrip({
            1: 'foo',
            2: 'bar',
            3: ['baz', 'qux'],
        })

    def test_dict_keys(self):
        self.roundtrip({
            True: 'true',
            False: [],
            None: {},
            0.7: -0.7,
        })

    def test_dictish_string(self):
        self.roundtrip({
            'strings': [
                'Foo: bar',
                'Baz: qux',
            ],
        })

    def test_tuples(self):
        if self.from_pyyaml:
            raise SkipTest("Can't parse PyYAML tuples")
        orig = {
            'polygons': {
                1: [
                    (0, 1),
                    (2, 3),
                ],
            },
        }
        text = self.dump_s(orig)
        result = self.load_s(text)
        self.assertEqual(orig['polygons'][1][0],
                         tuple(result['polygons'][1][0]))
        self.assertEqual(orig['polygons'][1][1],
                         tuple(result['polygons'][1][1]))

    def test_dict_tuples(self):
        if self.from_pyyaml:
            raise SkipTest("Can't parse PyYAML tuples")
        orig = {'tuple': (0, 1)}
        text = self.dump_s(orig)
        result = self.load_s(text)
        self.assertEqual(orig['tuple'],
                         tuple(result['tuple']))

    def test_quoted(self):
        # a literal true is True, but 'true' is a string
        self.roundtrip({'foo': 'true'})

    def test_literals(self):
        self.roundtrip({'foo': [True, False, None]})

    def test_numeric(self):
        self.roundtrip({'foo': [1, 2.0, -1, -2.5]})

    def test_inline(self):
        self.roundtrip([[1, 2, "hi, there' joe", '', "'"], [3, 4]])


class TestFromPyYAML(TestRoundTrip):
    from_pyyaml = True

    def dump_s(self, data):
        if yaml is None:
            raise SkipTest('yaml module unavailable')
        return yaml.dump(data, default_flow_style=False)


class TestFromPyYAMLInlineLists(TestRoundTrip):
    from_pyyaml = True

    def dump_s(self, data):
        if yaml is None:
            raise SkipTest('yaml module unavailable')
        return yaml.dump(data)


class TestToPyYAML(TestRoundTrip):
    def load_s(self, text):
        if yaml is None:
            raise SkipTest('yaml module unavailable')
        return yaml.load(text)
