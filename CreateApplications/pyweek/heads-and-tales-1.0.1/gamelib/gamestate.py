import collections
import os
import pickle
import pyglet
import random
import data

from gamelib import app
from gamelib import monster
from gamelib import team
from gamelib.constants import *


def get_game():
    if not hasattr(app, 'current_game'):
        app.current_game = Game()
    return app.current_game
app.game = get_game

def new_game():
    del app.current_game


class Game(pyglet.event.EventDispatcher):

    # world map travel
    current_map_name = 'tower1'
    current_world_node = 'centre'
    if DEBUG:
        current_map_name = 'act2'
        current_world_node = 'outsidetower'
    dest_world_node = None
    world_map_distance = 0
    travel_distance = None
    had_encounter = False

    def __init__(self):
        self.options = {}
        self.inventory = collections.defaultdict(int)
        self.team = team.Team([data.monsters.improvedgoat])
        self.closed_links = set()
        self.plotflags = {}
        self.load()

    def invparts(self, index=monster.MonsterPartMeta.all_index):
        if DEBUG:
            for part in index:
                yield part, 1000
        else:
            for part in index:
                if self.inventory[part]:
                    yield part, self.inventory[part]

    ## Saving/Loading #########################################################

    def save_path(self, name='save'):
        path = pyglet.resource.get_settings_path(APP_NAME)
        if not os.path.exists(path): os.makedirs(path)
        return os.path.join(path, '%s.sav' % name)

    def save(self, name='save'):
        path = self.save_path(name)
        # Serialise monsters
        monsters = []
        for m in self.team.monsters:
            if m is None: monsters.append(m)
            else: monsters.append(m.serialise())
        # Save data.
        data = (self.current_map_name,
                self.current_world_node,
                monsters,
                self.closed_links,
                self.plotflags,
                dict(self.inventory),
                self.options,
                )
        pickle.dump(data, open(path, 'w'))

    def load(self, name='save'):
        path = self.save_path(name)
        if os.path.exists(path):
            # Load data.
            try:
                (self.current_map_name,
                 self.current_world_node,
                 monsters,
                 self.closed_links,
                 self.plotflags,
                 self.inventory,
                 self.options,
                 ) = pickle.load(open(path, 'r'))
            except ValueError:
                if DEBUG:
                    raise Exception("Something went wrong on load. Save format changed?")
                else:
                    raise
            # Deserialise monsters.
            for i, m in enumerate(monsters):
                if m is None: self.team[i] = m
                else: self.team[i] = monster.MonsterPart.deserialise(m)
            # Fix inventory
            self.inventory = collections.defaultdict(lambda: 0, self.inventory)

    def get_plot_flag(self, name):
        return self.plotflags.get(name, False)
        
    def set_plot_flag(self, name, value):
        self.plotflags[name] = value

    def teleport(self, node):
        self.current_world_node = node
        self.dest_world_node = None

    def reset_inventory(self):
        self.inventory = collections.defaultdict(int)

    @property
    def travelling(self):
        return self.dest_world_node is not None

    def start_travel(self, node, distance):
        self.dest_world_node = node
        self.world_map_distance = 0.0
        self.travel_distance = distance

    def travel(self):
        self.world_map_distance += SPEED
        if self.world_map_distance >= self.travel_distance:
            self.current_world_node = self.dest_world_node
            self.dest_world_node = None
            self.travel_distance = None
            self.had_encounter = False
        else:
            if not self.had_encounter and random.random() < 0.005: # parameterise
                self.had_encounter = True # only one per journey
                return "fight a bear" # return info about the encounter
            else:
                return None

    def close_link(self, mapname, start, end):
        if start > end:
            start, end = end, start
        self.closed_links.add((mapname, start, end))
        self.dispatch_event('on_close_link', mapname, start, end)

    def open_link(self, mapname, start, end):
        if start > end:
            start, end = end, start
        self.closed_links.remove((mapname, start, end))
        self.dispatch_event('on_open_link', mapname, start, end)

    def link_closed(self, mapname, start, end):
        if start > end:
            start, end = end, start
        return (mapname, start, end) in self.closed_links

Game.register_event_type('on_close_link')
Game.register_event_type('on_open_link')
