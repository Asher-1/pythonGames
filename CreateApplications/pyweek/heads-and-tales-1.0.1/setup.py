import os
import pyglet
import setuptools
import shutil
import sys


## constants ##################################################################

PACKAGES = ["gamelib", "pyglet"]


## utility functions ##########################################################

def clean_dir(*paths):
    dir_path = os.path.join(*paths)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)
    return dir_path


## metadata ###################################################################

options = dict(

    name = 'heads-and-tales',

    version = '1.0.1',

    description = 'An monster building RPG.',

    long_description = '',

    author = 'Super Effective',

    author_email = 'heads-and-tales@supereffective.org',

    maintainer = '',

    maintainer_email = '',

    url = 'http://www.supereffective.org/pages/Heads-And-Tales',

    download_url = 'http://www.supereffective.org/pages/Heads-And-Tales',

    classifiers = [
    ],

    platforms = [
    ],

    license = 'BSD',

)


## general config #############################################################

options.update(

    packages = setuptools.find_packages(),

    data_files = [
    ],

    entry_points = {
        'console_scripts' : [
            'mygame = gamelib.__main__:main',
        ],
    },

)


## sdist ######################################################################

if 'sdist' in sys.argv:

    base = '%s-%s' % (options['name'], options['version'])
    staging_path = clean_dir('dist', base)
    shutil.rmtree(staging_path)

    # sdist build options
    options.update(

        options = {
            'sdist' : dict(
            ),
        },

    )

    # start build
    setuptools.setup(**options)

    # clean up
    shutil.rmtree('heads_and_tales.egg-info')


## py2exe #####################################################################

elif 'py2exe' in sys.argv:

    import py2exe

    # create staging directory
    base = '%s-%s-win32' % (options['name'], options['version'])
    staging_path = clean_dir('dist', base)

    # package avbin in top level
    avbin_path = pyglet.lib.loader.find_library('avbin')
    options['data_files'].append(('', [avbin_path]))

    # prepare icon resources
    icons = [(1, os.path.join('gamelib', 'data', 'misc', 'icon.ico'))]

    # py2exe build options
    options.update(

        options = {
            'py2exe' : dict(
                bundle_files = 1,
                dist_dir = staging_path,
                optimize = 2,
                packages = PACKAGES,
            ),
        },

        # build targets
        windows = [
            dict(
                icon_resources = icons,
                script = 'run_game.py',
            ),
        ],

    )

    # start build
    setuptools.setup(**options)


## py2app #####################################################################

elif 'py2app' in sys.argv:

    # create staging directory
    base = '%s-%s-osx' % (options['name'], options['version'])
    staging_path = clean_dir('dist', base)

    # prepare icon resource
    icon = os.path.join('gamelib', 'data', 'misc', 'icon.icns')

    # py2app build options
    options.update(

        options = {
            'py2app' : dict(
                argv_emulation = True,
                iconfile = icon,
                optimize = 2,
                frameworks = ['libavbin.dylib'],
                packages = PACKAGES,
            ),
        },

        # build targets
        app = ['run_game.py'],

    )

    # start build
    setuptools.setup(**options)


## default ####################################################################

else:

    # start build
    setuptools.setup(**options)
