"""Handling the options"""

import logging
import optparse
import os
from model import conversation
from game import common


def read_options():
    """Read options for the game"""
    log = common.log

    parser = optparse.OptionParser()
    parser.add_option("-r", "--read-file", dest="read_file",
                      help="initialise data from csv file", action='store_true',
                      default=True)
    parser.add_option("-S", "--straight", dest="initial_state",
                      help="initialise data from csv file", type='str',
                      default=None)
    parser.add_option("-t", "--initial-time", dest="initial_time",
                      help="initialise time to start with", type='int',
                      default=0)
    parser.add_option("-d", "--initial-day", dest="initial_day",
                      help="initialise day to start with", type='int',
                      default=0)
    parser.add_option("-f", "--fast", dest="fast",
                      help="use fast mode for clock", action='store_true',
                      default=False)
    parser.add_option("-a", "--alternate", dest="alternate",
                      help="use alternate initial health properties", action='store_true',
                      default=False)
    parser.add_option("-M", "--mute-music", dest="mute_music",
                      help="mute the music", action='store_true',
                      default=False)
    parser.add_option("-l", "--log-level", dest="log_level",
                      help="logging level", type='int',
                      default=logging.ERROR)
    #
    # Read main options
    options, args = parser.parse_args()

    common.log.level = options.log_level

    if options.read_file:
        log.info('Clearing database and reading from file')
        c = conversation.ConversationSystem(recreate=True)
        c.loadFromFile(os.path.join('game', 'Refraction planning - Dialog.csv'))
        c.closeConnection()
    #
    return options
