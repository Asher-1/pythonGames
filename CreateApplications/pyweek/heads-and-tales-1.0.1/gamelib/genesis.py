# random monster generation!

import random

from monster import MonsterPartMeta as MPM

names = ['Monstrosity', 'Abberation', 'Anomaly', 'Experiment', 'Travesty', 'Blasphemy',
            'Mutant', 'Monster', 'Horror', 'Creation', 'Amalgamation', 'Chimera']

def make_random_monster():
    body = random.choice(MPM.hearty_index)(None)
    body.name = random.choice(names)
    for a in body.unused_anchors():
        fill_monster_anchor(body, a)
    return body
    
def fill_monster_anchor(monster, anchor_idx):
    size = monster.anchors[anchor_idx][2]
    part_cls = random.choice(MPM.size_index[size])
    root_idx = random.choice([i for i in xrange(len(part_cls.anchors)) if part_cls.anchors[i][2] == size])
    p = monster.add_part(part_cls, anchor_idx, root_idx)
    for a in p.unused_anchors():
        if random.random() > 0.8:
            fill_monster_anchor(p, a)
