'''
Serializer and dumper for a simple, YAMLish format (actually a YAML subset).
The top level object is a dict or list.
lists and dicts can contain:
 * lists, dicts,
 * single line strings,
 * ints, floats,
 * True, False, and None
dict keys can only be scalar.
'''

import re


def dump(data, file_object):
    file_object.write(dump_s(data))


def dump_s(data):
    return Dumper().dump(data)


def load(file_object):
    yaml = file_object.read()
    return load_s(yaml)


def load_s(yaml):
    return Parser().parse(yaml.strip())


class Dumper(object):
    def dump(self, data):
        return '\n'.join(self._dump_block(data)) + '\n'

    def _dump_block(self, data, indent=0):
        for type_ in (list, tuple, dict):
            if isinstance(data, type_):
                f = getattr(self, '_dump_%s_block' % type_.__name__)
                return f(data, indent)
        raise NotImplementedError()

    def _dump_inline(self, data):
        if data is True or data is False or data is None:
            return self._dump_literal(data)
        for type_ in (list, tuple, dict, basestring, int, float):
            if isinstance(data, type_):
                f = getattr(self, '_dump_%s' % type_.__name__)
                return f(data)
        raise NotImplementedError('Type: %s' % type(data))

    def _dump_list_block(self, data, indent):
        output = []
        for item in data:
            if self._inlineable(item):
                output.append('%s- %s' % (' ' * indent,
                                          self._dump_inline(item)))
            else:
                dumped = self._dump_block(item, indent + 2)
                dumped[0] = '%s- %s' % (' ' * indent, dumped[0][indent + 2:])
                output += dumped
        return output

    _dump_tuple_block = _dump_list_block

    def _dump_dict_block(self, data, indent):
        output = []
        for k, v in sorted(data.iteritems()):
            output.append('%s%s:' % (' ' * indent, self._dump_inline(k)))
            if self._inlineable(v):
                output[-1] += ' ' + self._dump_inline(v)
            elif isinstance(v, dict):
                output += self._dump_block(v, indent + 2)
            elif isinstance(v, (list, tuple)):
                output += self._dump_block(v, indent)
            else:
                raise NotImplementedError("Cannot dump %r", data)
        return output

    def _inlineable(self, data):
        if isinstance(data, (list, tuple)):
            return all(not isinstance(item, (list, dict, tuple))
                       for item in data)
        elif isinstance(data, dict):
            return all(not isinstance(item, (list, dict, tuple))
                       for item in data.itervalues())
        else:
            return True

    def _dump_list(self, data):
        return '[%s]' % ', '.join(self._dump_inline(item) for item in data)

    _dump_tuple = _dump_list

    def _dump_dict(self, data):
        return '{%s}' % ', '.join(
            '%s: %s' % (self._dump_inline(key), self._dump_inline(value))
            for key, value in data.iteritems())

    def _dump_basestring(self, data):
        if data in ('true', 'false', 'null'):
            return "'%s'" % data
        if "'" in data or ':' in data or data.startswith('['):
            return "'%s'" % data.replace("'", "''")
        if data == '':
            return "''"
        return data

    def _dump_int(self, data):
        return str(data)

    def _dump_float(self, data):
        return str(data)

    def _dump_literal(self, data):
        return {
            True: 'true',
            False: 'false',
            None: 'null',
        }[data]


class Parser(object):
    _spaces_re = re.compile(r'^(\s*)(.*)')
    _list_re = re.compile(r'^(-\s+)(.*)')
    _dict_re = re.compile(r"^((?![{['])[^-:]+):\s?(.*)")
    _inline_list_re = re.compile(r"^([^',]+|(?:'')+|'.+?[^'](?:'')*')"
                                 r"(?:, (.*))?$")

    def __init__(self):
        # Stack of (indent level, container object)
        self._stack = []
        # When a dict's value is a nested block, remember the key
        self._parent_key = None

    @property
    def _indent(self):
        return self._stack[-1][0]

    @property
    def _container(self):
        return self._stack[-1][1]

    @property
    def _in_list(self):
        return isinstance(self._container, list)

    @property
    def _in_dict(self):
        return isinstance(self._container, dict)

    def _push(self, container, indent=None):
        in_list = self._in_list
        assert in_list or self._parent_key

        if indent is None:
            indent = self._indent
        self._stack.append((indent, container()))
        if in_list:
            self._stack[-2][1].append(self._container)
        else:
            self._stack[-2][1][self._parent_key] = self._container
            self._parent_key = None

    def parse(self, yaml):
        if yaml.startswith(('[', '{')):
            return self._parse_value(yaml)

        if yaml.startswith('-'):
            self._stack.append((0, []))
        else:
            self._stack.append((0, {}))

        for line in yaml.splitlines():
            spaces, line = self._spaces_re.match(line).groups()

            while len(spaces) < self._indent:
                self._stack.pop()

            lm = self._list_re.match(line)
            dm = self._dict_re.match(line)
            if len(spaces) == self._indent:
                if lm and self._in_dict:
                    # Starting a list in a dict
                    self._push(list)
                elif dm and self._in_list:
                    # Left an embedded list
                    self._stack.pop()

            if len(spaces) > self._indent:
                assert self._parent_key
                if dm:
                    # Nested dict
                    self._push(dict, len(spaces))
                elif lm:
                    # Over-indented list in a dict
                    self._push(list, len(spaces))

            indent = self._indent
            while lm and lm.group(2).startswith('- '):
                # Nested lists
                prefix, line = lm.groups()
                indent += len(prefix)
                self._push(list, indent)
                lm = self._list_re.match(line)
            del indent

            if lm:
                prefix, line = lm.groups()
                dm = self._dict_re.match(line)
                if dm:
                    self._push(dict, self._indent + len(prefix))
                else:
                    assert self._in_list
                    self._container.append(self._parse_value(line))

            if dm:
                key, value = dm.groups()
                key = self._parse_value(key)
                assert self._in_dict
                if value:
                    value = self._parse_value(value)
                    self._container[key] = value
                else:
                    self._parent_key = key

        return self._stack[0][1]

    def _parse_value(self, value):
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1].replace("''", "'")
        if value.startswith('[') and value.endswith(']'):
            value = value[1:-1]
            output = []
            while value:
                m = self._inline_list_re.match(value)
                assert m, value
                output.append(self._parse_value(m.group(1)))
                value = m.group(2)
            return output
        if value.startswith('{') and value.endswith('}'):
            value = value[1:-1]
            output = {}
            while value:
                key, value = value.split(': ', 1)
                m = self._inline_list_re.match(value)
                assert m
                output[key] = self._parse_value(m.group(1))
                value = m.group(2)
            return output
        if value.startswith('!!'):
            raise NotImplementedError()
        if value == 'true':
            return True
        if value == 'false':
            return False
        if value == 'null':
            return None
        for type_ in (int, float):
            try:
                return type_(value)
            except ValueError:
                pass
        return value
