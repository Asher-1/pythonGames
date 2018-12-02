# setup.py
# -*- coding: utf8 -*-
# vim:fileencoding=utf8 ai ts=4 sts=4 et sw=4

"""Setuptools setup.py file for nagslang."""

from setuptools import setup, find_packages

try:
    import py2exe
    py2exe  # To make pyflakes happy.
except ImportError:
    pass

try:
    from pip.req import parse_requirements
    import os
    game_dir = os.path.dirname(__file__)
    req_file = os.path.join(game_dir, 'requirements.txt')
    install_reqs = parse_requirements(req_file)
    reqs = [str(ir.req) for ir in install_reqs]
except ImportError:
    reqs = []

# This should probably be pulled from constants.py
VERSION_STR = "0.1"

setup(
    name="nagslang",
    version=VERSION_STR,
    description="naglsang: Game for PyWeek 17",

    author=(", ".join([
        "Simon Cross",
        "David Fraser",
        "Neil Muller",
        "Adrianna Pinska",
        "Stefano Rivera",
        "David Sharpe",
        "Jeremy Thurgood",
    ])),
    author_email="ctpug@googlegroups.com",

    maintainer="Nagslang Team",
    maintainer_email="ctpug@googlegroups.com",

    url="http://ctpug.org.za/",
    download_url="https://ctpug.org.za/hg/nagslang/",

    license="MIT",

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Games/Entertainment :: Role-Playing',
        'Topic :: Games/Entertainment :: Arcade',
    ],

    platforms=[
        'Linux',
        'Mac OS X',
        'Windows',
    ],

    # Dependencies
    install_requires=reqs,

    # Files
    packages=find_packages(),
    scripts=[
        'scripts/nagslang',
    ],

    # py2exe
    windows=[{
        'script': 'scripts/nagslang',
        'icon_resources': [(0, "data/icons/werewolf-sonata.ico")],
    }],
    app=['scripts/nagslang'],
    options={
        'py2exe': {
            'skip_archive': 1,
            'dist_dir': 'dist/nagslang-%s' % VERSION_STR,
            'packages': [
                'logging', 'encodings', 'nagslang',
            ],
            'includes': [
                'pygame', 'pymunk',
            ],
            'excludes': [
                'numpy',
            ],
            'ignores': [
                # all database modules
                'pgdb', 'Sybase', 'adodbapi',
                'kinterbasdb', 'psycopg', 'psycopg2', 'pymssql',
                'sapdb', 'pysqlite2', 'sqlite', 'sqlite3',
                'MySQLdb', 'MySQLdb.connections',
                'MySQLdb.constants.CR', 'MySQLdb.constants.ER',
                # old datetime equivalents
                'DateTime', 'DateTime.ISO',
                'mx', 'mx.DateTime', 'mx.DateTime.ISO',
                # email modules
                'email.Generator', 'email.Iterators', 'email.Utils',
            ],
        },
        'py2app': {
            'app': ['run_game.py'],
            'argv_emulation': True,
            'iconfile': 'data/icons/program/icon.icns',
            'packages': [
                'logging', 'encodings', 'pygame', 'pymunk', 'nagslang', 'data',
            ],
            'excludes': ['numpy'],
        }},
    data_files=[
        # 'COPYRIGHT',
        'LICENSE.txt',
        'README.txt',
    ],
    include_package_data=True,
)
