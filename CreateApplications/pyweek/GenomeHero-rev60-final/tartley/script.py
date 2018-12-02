import gameobjects

intro = [
    #("fade", ("1234567890", 0.16, 0.15)),
    #("game", 6, 1, gameobjects.random_pair, {'time': 21}),
    ("music", "intro"),
    ("fade", ("a\nknuckledragger\ngames\nproduction", 0.16, 0.15)),
    ("main_menu", None)
]
##  ("fade", ("", 0.18, 0.15)),
about = [
    ("fade", ("we knuckledraggers hope you\nenjoyed genome hero\nthoroughly", 0.10, 0.2)),
    ("fade", ("the game was written entirely\nin the python programming\nlanguage", 0.11, 0.2)),
    ("fade", ("it utilizes the libraries\npyglet\navbin\nopengl", 0.11, 0.2)),
    ("fade", ("the music was provided by\nrotterdam ska jazz foundation\nunder the creative commons sa", 0.11, 0.15)),
    ("band_pic", None),
    ("fade", ("netherlands ska jazz huh\nthanks guys\nit really made the game", 0.11, 0.2)),
    ("fade", ("everything else\nby\ndaspork\ntactii", 0.11, 0.08)),
    ("fade", ("", 0.11, 0.2)),
    ("music", ("intro")),
]

tutorial = [
    ("fade", ("welcome to genome hero", 0.18, 0.25)),
    ("fade", ("this game is all about dna", 0.18, 0.25)),
    ("fade", ("you will be presented with\nbroken and mutated strands\nof dna", 0.12, 0.15)),
    ("fade", ("it is your job to fix them", 0.14, 0.2)),
    ("fade", ("each pair is made up of 2 nucleobases", 0.13, 0.2)),
    ("fade", ("a binds with t", 0.16, 0.3)),
    ("fade", ("c binds with g", 0.16, 0.3)),
    ("fade", ("the order does not matter", 0.16, 0.3)),
    ("fade", ("if you fail to repair the dna\nthe strand will degrade\nand start to break down", 0.11, 0.11)),
    ("fade", ("lets play a quick round with\na restriced set of basepairs\nadenine and thymine", 0.11, 0.11)),
    ("fade", ("you will only need the\na and s keys\non your keyboard", 0.18, 0.13)),
    ("fade", ("get ready", 0.18, 0.25)),
    ("game", 0, 0, gameobjects.at_pair, {'score': 1000}),
    ("fade", ("very good", 0.18, 0.25)),
    ("fade", ("now try this\nyou will need the\nd and f keys", 0.18, 0.15)),
    ("game", 0, 0, gameobjects.cg_pair, {'score': 1000}),
    ("fade", ("great job", 0.18, 0.15)),
    ("fade", ("now its time to spread\nyour wings\nn00b", 0.16, 0.11)),
    ("music", ("intro")),
] 

easy_levels = [
    ("fade", ("something easy\nyou need a streak of 30\nto progress", 0.14, 0.25)),
    ("fade", ("try to keep up", 0.18, 0.25)),
    ("game", 1, 1, gameobjects.random_pair_1, {'streak': 30}),
    ("music", "easy"),
    ("fade", ("oh you want more", 0.18, 0.25)),
    ("fade", ("this time you need a\nscore of\n100 000", 0.17, 0.25)),
    ("game", 2, 1, gameobjects.random_pair_2, {'score': 100000}),
    ("music", "fast_groove"),
    ("fade", ("lets shake it up", 0.18, 0.25)),
    ("fade", ("now you have\nto last for\n3 minutes", 0.17, 0.25)),
    ("game", 3, 1, gameobjects.random_pair_3, {'time': 180}),
    ("music", "hard"),
    ("fade", ("oh you want more\nwe have moved the\nstrand down a bit", 0.16, 0.1)),
    ("fade", ("try for another\nstreak of\n30", 0.16, 0.25)),
    ("game", 4, 2, gameobjects.random_pair_4, {'streak': 30}),
    ("music", "fast_groove"),
    ("fade", ("fine then\n1 000 000\ngood luck", 0.18, 0.25)),
    ("game", 5, 2, gameobjects.random_pair_4, {'score': 1000000}),
    ("music", "intro"),
    ("fade", ("you might want to quit now", 0.16, 0.25)),
    ("fade", ("this time\nyou need a streak of 50\nto progress", 0.16, 0.25)),
    ("game", 6, 2, gameobjects.random_pair_4, {'streak': 50}),
    ("music", "chill"),
    ("fade", ("i told you to quit\n10 000 000\ngood luck", 0.15, 0.25)),
    ("game", 7, 3, gameobjects.random_pair_5, {'score': 10000000}),
    ("music", "fast_groove"),
    ("fade", ("i told you to quit\nyou werent suppose\nto make it this far", 0.15, 0.25)),
    ("fade", (" you have to last\nfor 5 minutes\ngood times", 0.16, 0.25)),
    ("game", 8, 3, gameobjects.random_pair_5, {'time': 300}),
    ("music", "chill"),
    ("fade", ("this is the\nlast one\nits stupid.", 0.16, 0.25)),
    ("fade", ("this time\nyou need a streak of 100\nto win", 0.16, 0.25)),
    ("game", 9, 3, gameobjects.random_pair_5, {'streak': 100}),
    
    ("music", "intro"),
]


lose = [
    ("music", "intro"),
    ("fade", ("the strand was unrecoverable", 0.16, 0.3)),
    ("fade", ("you lose\ntry again\nchump", 0.18, 0.3)),
]

win = [
    ("fade", ("you win", 0.18, 0.3)),
]
