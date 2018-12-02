import random



BAD_MOVES = [ 'zoinks', 'doh', 'bam', 'smash', 'chump', "u mad bro", "wimp", "sucker", "troll", "you chav"]

def random_bad_move():
    n = random.randint(0, len(BAD_MOVES) - 1)
    return BAD_MOVES[n]


STREAK_TEXT = {5: "5 in a row", 10: "wow 10 strait", 20: "20 is kingly", 30: "wow 30", 40: "excellent", 50: "50 is almost good", 75: "ummmmm 75", 100: "you win the game"}

EASY_LEVELS = {0: "tutorial", 1: "deamination", 2: "depurination", 3: "heredity", 4: "rosalind", 5: "crick", 6: "resurection", 7: "watson", 8: "phage", 9: "decay", 10: ""}

MED_LEVELS = {}

HARD_LEVELS = {1: "plunge", 2: "forensics", 3: "heredity", 4: "rosalind", 5: "crick"}
