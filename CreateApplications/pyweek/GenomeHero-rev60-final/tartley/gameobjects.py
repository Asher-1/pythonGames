from random import randint
combos = {  
            
            1: ('T', (None, 'A')),
            2: ('T', ('A', None)),
            3: ('A', (None, 'T')),
            4: ('A', ('T', None)),

            5: ('C', (None, 'G')),
            6: ('C', ('G', None)),
            7: ('G', (None, 'C')),
            8: ('G', ('C', None)),
            
            9: (None, ('G', 'C')),
            10:(None, ('C', 'G')),
            11:(None, ('A', 'T')),
            12:(None, ('T', 'A')),
        }


_LAST_PAIR = None
_COUNT = 0


###############################################################################
################################################################# random_pair #
###############################################################################

def random_pair(level=0, diff=0):
    global _LAST_PAIR
    global _COUNT
    if _LAST_PAIR and _COUNT < 2:
        _COUNT += 1
        if randint(1, 10) < 5+diff:
            return BasePair(_LAST_PAIR)
        elif level < 3:
            _LAST_PAIR = combos[randint(1,12)][1]
            return BasePair(_LAST_PAIR)
        elif level < 5:
            _LAST_PAIR = combos[randint(1,8)][1]
            return BasePair(_LAST_PAIR)
        elif level == 5:
            _LAST_PAIR = combos[randint(1,8)][1]
            return BasePair(_LAST_PAIR)
    else:
        _COUNT = 0
        _LAST_PAIR = combos[randint(1,12)][1]
        return BasePair(_LAST_PAIR)

def random_pair_1():
    return random_pair(1,1)

def random_pair_2():
    return random_pair(2,1)

def random_pair_3():
    return random_pair(3,1)

def random_pair_4():
    return random_pair(4,1)

def random_pair_5():
    return random_pair(5,1)

###############################################################################
########################################################### at_pair ###########
###############################################################################

def at_pair():
    num = randint(1,4)
    return BasePair(combos[num][1])

def cg_pair():
    num = randint(5,8)
    return BasePair(combos[num][1])

def custom_pair(r1, r2):
    return (r1, r2)


###############################################################################
############################################################# check_hit #######
###############################################################################

def check_hit(button, rung):
    if not rung:
        print "No Rung!!!"
        return False
    pair = rung.get_pair_data()
    
    for p in combos.values():
        if p[0] == button:
            if p[1] == pair:
                if pair[1] == None:
                    rung.game_obj.right = button
                else:
                    rung.game_obj.left = button
                rung.complete = True
                rung.update_game_obj()
                return True
            else:
                pass
    return False

if __name__ == '__main__':
    pairs = []
    for n in range(80): 
        pairs.append(random_pair())
    for p in pairs:
        print p

class BasePair (object):
    def __init__(self, _types, bonus=None):
        self.left = _types[0]
        self.right = _types[1]

    def __str__(self):
        return "(%s - %s)" % (self.left, self.right)


class Nucleobase  (object):
    def __init__(self, _type):
        self._type = _type

