#!/usr/bin/env python

"""Run the application.

"""

if __name__ == '__main__':

    import os, sys
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

    from gamelib import __main__
    __main__.main()
