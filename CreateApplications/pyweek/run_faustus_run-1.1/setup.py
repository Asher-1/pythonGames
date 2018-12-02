#!/usr/bin/env python

import copy
import glob
import os
import pyglet
import setuptools
import shutil
import subprocess
import sys


def subpackages(package):
    def _subpackages(package):
        if os.path.isfile(os.path.join(package, '__init__.py')):
            yield package.replace('/', '.')
            for x in os.listdir(package):
                subpackage = os.path.join(package, x)
                if os.path.isdir(subpackage):
                    for x in subpackages(subpackage):
                        yield x
    return list(_subpackages(package))

## Constants ##################################################################

NAME = 'Run, Faustus, Run!'

VERSION = '1.1'

PACKAGES = subpackages('gamelib') + subpackages('pyglet')


## Utility functions ##########################################################

def create_dir(*paths):
    dir_path = os.path.join(*paths)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)
    return dir_path

def glob_remove(*paths):
    glob_path = os.path.join(*paths)
    for file_path in glob.glob(glob_path):
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        elif os.path.isfile(file_path):
            os.remove(file_path)

def copy_from_sdist(name, target_path):
    base_name = '%(name)s-%(version)s-source' % metadata
    src_path = os.path.join('dist', base_name, name)
    dst_path = os.path.join(target_path, name)
    if not os.path.exists(os.path.join('dist', base_name)):
        sys.argv[1:] = ['sdist']
        sdist()
    if os.path.isdir(src_path):
        shutil.copytree(src_path, dst_path)
    elif os.path.isfile(src_path):
        shutil.copyfile(src_path, dst_path)
    return dst_path

def byte_compile(path, **kwds):
    from distutils.util import byte_compile
    path = os.path.abspath(path)
    def _walk():
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.lower().endswith('.py'):
                    yield os.path.join(root, filename)
    kwds.setdefault('prefix', os.path.split(os.sep)[0])
    byte_compile(_walk(), **kwds)


## Metadata ###################################################################

metadata = dict(

    name = 'run_faustus_run',

    version = VERSION,

    description = 'Description of the game.',

    long_description = 'Detailed description of the game.',

    author = 'Awe Thorre',

    author_email = 'awe.thorre@example.com',

    maintainer = 'Mae N. Tanner',

    maintainer_email = 'mae.n.tanner@example.com',

    url = 'http://www.example.com/my_game',

    download_url = 'http://www.example.com/my_game/download',

    classifiers = [
    ],

    platforms = [
    ],

    license = '',

)

## Pre-build ##############################################################

# copy options dictionary
options = copy.deepcopy(metadata)

# format base file name
base_name = '%(name)s-%(version)s-source' % metadata

# clean up output files
glob_remove('dist', base_name + '*')

# create staging directory
staging_path = os.path.join('dist', base_name)

## Build ##################################################################

# build options
options.update(
    # sdist options
    options = {'sdist' : dict(
        formats = ['gztar'],
        keep_temp = True,
    )},
    packages = PACKAGES,
)

# start build
setuptools.setup(**options)

## Post-build #############################################################

# move staging directory to dist directory
os.rename('%(name)s-%(version)s' % metadata, staging_path)

# clean up egg-info directory
glob_remove('%(name)s.egg-info' % metadata)

# clean up build directory
glob_remove('build')
