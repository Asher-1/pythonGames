'''data.py - simple data loader/saver module'''

import os


DATA_DIR = 'data'


def filepath(filename):
    '''determine the path to a file in the data directory'''
    return os.path.join(DATA_DIR, filename)


def load(filename, mode='rb'):
    '''open a file in the data directory for reading'''
    return open(os.path.join(DATA_DIR, filename), mode)


def save(filename, mode='wb'):
    '''open a file in the data directory for writing'''
    return open(os.path.join(DATA_DIR, filename), mode)
