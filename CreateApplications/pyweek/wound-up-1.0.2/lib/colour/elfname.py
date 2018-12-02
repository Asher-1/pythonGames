'''elfname.py - elf name generation'''

from random import choice, random, randint



start_nicknames = [ "Mad Dog", "Crazy-Eye", "Fancypants", "Honest", "Crumbly", "Questionable", "Festering", "Untouchable", "Immortal", "Ballsy", "Killer", "Evil", "Blazing", "Acid", "Really Mad", "Bloody", "Barking", "Terrible", "Gimpy", "Lame", "Gutless", "Shivering", "Ugly", "Snotty" ]

male_firstnames = [ "abraham", "addlebert", "agamemnon", "amos", "arthur", "augustus", "bartholomew", "basil", "bobby", "buggy", "buster", "cletus", "cornelius", "crispin", "danbury", "darius", "dilbert", "draco", "elphis", "eugene", "franklin", "frankenstein", "franky", "frederic", "gordon", "grant", "isaac", "jacob", "jeremy", "jimmy", "lincoln", "morris", "norbert", "norris", "osbert", "oscar", "osric", "phineas", "quentin", "reginald", "roosevelt", "rutherford", "stanley", "terrence", "theodore", "titus", "trevor", "tycho", "tyson", "ulysses", "victor", "wimbledon", "winstable", "winston", "xavier", "xeno", "xerxes", "zachariah", "zebedee", "zebulon" ]

female_firstnames = [ "amelia", "angelina", "autumn", "bertha", "beyonce", "celeste", "cordelia", "daphne", "dorothy", "esmerelda", "elspeth", "fanny", "fiona", "gertrude", "hetty", "hortense", "ida", "iris", "jemima", "kensington", "kirsty", "laetitia", "lucrezia", "magdalena", "minnie", "moira", "nora", "noreen", "octavia", "pearl", "peggy", "quincy", "rebecca", "rhiannon", "sharona", "tabitha", "ursula", "verity", "viola", "wanda", "xanthe", "xena", "yvette", "yvonne", "zsa-zsa", "fenella", "anthea", "melissa", "edwina", "fleur", "bathsheba", "mutya", "ophelia", "deanara", "shandy", "dolly", "persephone", "portia", "polly", "molly", "kerry", "sherry", "sandy", "mandy", "candy", "chardonnay", "kelis", "macy", "rihanna", "geraldine", "milly", "poppy", "prudence", "marla", "carla", "darla", "fifi", "marilyn", "ginger", "mavis", "eve", "cosette"]

middle_nicknames = [ "The Elfmeister", "Crusher", "The King", "Is-He-An-Elf?", "Stalker", "The Terror", "Eight Pints", "Wizard", "Hacker", "Chopper", "Tycoon", "Tranquility", "The Eagle", "Commodore", "Amigo", "Typhoid Mary", "Fatty", "Slippers", "Bignose", "Scarface" , "Tiger Boy", "Princess Parasolia", "Captain Cardboard", "Doctor Strangesmell"]

full_surname_prefixes = [ "de", "du", "van", "von" ]

surname_prefixes = [ "Mac", "Mc" ] 

dbl_surname_starts = [ "bag", "big", "bog", "bug", "bum", "cob", "cod", "cog", "cop", "dog", "dor", "gad", "gum", "ham", "hum", "nog", "nor", "plat", "pod", "pot", "ser", "sor", "swar", "swor", "tad", "tod", "tog", "trap", "wad" ]
nondbl_surname_starts = [ "elf", "spoon", "thumb", "sword", "tink", "feather", "rock", "dust" ]
surname_starts = dbl_surname_starts + nondbl_surname_starts

dbl_surname_middles = [ "ing", "i", "les" ]
nondbl_surname_middles = [ "", "s" ]
surname_middles = dbl_surname_middles + nondbl_surname_middles

surname_suffixes = [ "bottom", "bury", "field", "worth", "ton", "land", "son", "smith", "wright", "cliffe" ]

fullname_suffixes = [ "III", "Jr.", "Sr.", "Esq.", "II", "IX", "the Conqueror" ]

def random_name(female=False):
    name = []
    
    # optional leading nickname
    if random() < 0.2:
        name.append('"'+choice(start_nicknames)+'"')
    # firstname
    if female:
        name.append(choice(female_firstnames).capitalize())
    else:
        name.append(choice(male_firstnames).capitalize())
    # optional middle nickname
    if random() < 0.2:
        name.append('"'+choice(middle_nicknames)+'"')
    # optional word before surname
    if random() < 0.1:
        name.append(choice(full_surname_prefixes))
    # surname (optionally double barrelled)
    name.append(random_surname())
    if random() < 0.2:
        name[-1] += "-"
        name[-1] += random_surname()
    # optional suffix to fullname
    if random() < 0.1:
        name.append(choice(fullname_suffixes))

    return " ".join(name)


def random_surname():
    name = []

    if random() < 0.1:
        prefix = choice(surname_prefixes)
    else:
        prefix = ""

    name.append(choice(surname_starts))
    name.append(choice(surname_middles))
    name.append(choice(surname_suffixes))

    # Fix a consonant error
    if name[0] in dbl_surname_starts and name[1] in dbl_surname_middles:
        name[0] += name[0][-1]
    
    return prefix + "".join(name).capitalize()


if __name__ == "__main__":
    for i in xrange(5):
        print random_name()
    for i in xrange(5):
        print random_name(female=True)
