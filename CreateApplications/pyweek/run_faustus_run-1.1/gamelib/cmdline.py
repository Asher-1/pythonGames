"""gamelib.cmdline -- command line parser

"""

import argparse
import contextlib

from gamelib.constants import *

__all__ = ['Parser', 'option', 'parse', 'mutex']


## Parser ####################################################################

class Parser(object):
    """Wrapper for argparse providing decorator based argument definition.

    ::Methods::

        `Parser.option(*, **)`
            Decorate a function to be called when a command line argument is
            matched. For example::

                @parser.option('-f', '--foo'):
                def foo(value):
                    'help string printed with -h or --help'
                    config.foo = int(value)

        `Parser.mutex()`
            Create a context for mutually exclusive options. For example::

                with parser.mutex():
                    @parser.option('-1')
                    def m1(): config.m = 1
                    @parser.option('-2')
                    def m2(): config.m = 2

        `Parser.parse()`
            Parse the command line and call the matched functions.

    """

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.group = self.parser
        self.functions = {}

    def option(self, *args, **kwds):

        # Ignore debug options without DEBUG set.
        if kwds.pop('debug', False) and not DEBUG:
            return lambda function: None

        def decorator(function):

            # Store the function.
            self.functions[function.__name__] = function

            # Argument properties for parameters and switches.
            kwds.update({
                'help' : function.__doc__,
                'dest' : function.__name__,})

            # Argument properties for parameters only.
            varnames = function.func_code.co_varnames
            if varnames:
                kwds.update({
                    'action' : 'store',
                    'nargs' : len(varnames),
                    'metavar' : varnames[0].upper(),})

            # Argument properties for switches only.
            else:
                kwds.update({
                    'action' : 'store_const',
                    'const' : True,
                    'default' : False,})

            # Add the argument to the parser.
            self.group.add_argument(*args, **kwds)

        return decorator

    def parse(self):
        args = self.parser.parse_args()
        for name, function in self.functions.items():
            value = getattr(args, name)
            # Argument is a switch.
            if value is True:
                function()
            # Argument is a single-valued parameter.
            elif isinstance(value, str):
                function(value)
            # Argument is a multi-valued parameter.
            elif isinstance(value, list):
                function(*value)

    @contextlib.contextmanager
    def mutex(self):
        assert self.group is self.parser, "recursive mutex command line group"
        self.group = self.parser.add_mutually_exclusive_group()
        yield
        self.group = self.parser


## Global API ################################################################

_parser = Parser()
option = _parser.option
parse = _parser.parse
mutex = _parser.mutex
