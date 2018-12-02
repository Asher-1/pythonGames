import random

rc = random.choice

ingredients = ["meat", "fish", "potato", "cabbage", "egg", "turnip",
               "carrot", "veal", "chilli", "lettuce", "milk", "sausage",
               "ham", "tofu", "cheese", "seafood", "fruit", "cream"]

dishes = ["pies", "sandwiches", "omelettes", "tacos", "stew", "pizza", "ravioli", "salsa", "jam", "tagine", "casserole", "sorbet", "confit", "trifle"]

levels = ["awesome", "legendary", "great", "good", "mediocre", "passable",
          "competent", "bad", "terrible", "dire", "lucky", "irritatingly good", "hardcore", "magnificent", "rubbish"]

sports = ["hockey", "chess", "tiddlywinks", "football", "baseball",
          "basketball", "darts", "polo", "rugby", "cricket", "ludo", "Twister(tm)", "elephant polo"]

slackings = ["lazing about", "loafing around", "sleeping", "daydreaming",
             "wasting time", "slacking off", "sunbathing", "taking baths", "spitting tobacco"]

colours = ["red", "orange", "yellow", "green", "blue", "purple", "indigo",
           "violet", "lavender", "white", "black", "brown", "mauve"]

opinions = ["likes", "loves", "hates", "detests", "loathes",
            "gets a kick out of", "dreads", "is ambivalent about",
            "enjoys", "dreams of"]

smells = ["fresh-cut grass", "sweat", "room freshener", "pine", "lavender",
          "chocolate", "curry", "mint", "clean linen", "blood", "vomit",
          "napalm", "metal", "roses", "cordite", "carpet", "wee"]

frequencies = ["often", "frequently", "occasionally", "sometimes"]

groups = ["strangers", "family members", "hoboes", "small children", "dogs",
          "cats", "people in the street", "politicians"]

gestures = ["spits", "waves", "whistles", "throws stones", "rants", "winks",
            "smiles", "grins", "screams"]

times = ["in the morning", "while sleepy", "during lunch", "after work",
         "on public holidays", "at inappropriate times"]

food_acts = ["making", "eating", "selling"]

get_food = lambda: random.choice(ingredients) + " " + random.choice(dishes)

get_sport = lambda: random.choice(sports)

get_food_act = lambda: random.choice(food_acts) + " " + get_food()

get_play_sport = lambda: "playing " + get_sport()

get_slack = lambda: random.choice(slackings)

get_wear_colour = lambda: "wearing " + random.choice(colours)

activity_eps = [get_food_act, get_play_sport, get_slack, get_wear_colour]

get_optional_frequency_prefix = lambda: ["", (random.choice(frequencies) + " ")][random.random() < 0.5]

get_optional_time_suffix = lambda: ["", " " + random.choice(times)][random.random() < 0.3]

get_activity = lambda: random.choice(activity_eps)()

get_smell_opinion = lambda: random.choice(opinions) + " the smell of " + random.choice(smells) + get_optional_time_suffix() + "."
get_smell = lambda: random.choice(frequencies) + " smells of " + random.choice(smells) + get_optional_time_suffix() + "."

get_act_opinion = lambda: random.choice(opinions) + " " + get_activity() + get_optional_time_suffix() + "."

get_act_skill = lambda: random.choice(levels) + " at " + get_activity() + get_optional_time_suffix() + "."

get_does_act = lambda: random.choice(frequencies) + " found " + get_activity() + get_optional_time_suffix() + "."

get_does_gesture = lambda: get_optional_frequency_prefix() + rc(gestures) + " at " + rc(groups) + "."

get_turns_colour = lambda: rc(frequencies) + " turns " + rc(colours) + get_optional_time_suffix() + "."

sentence_entrypoints = [get_act_opinion, get_act_opinion, get_act_skill, get_act_skill, get_smell_opinion,
                        get_smell_opinion, get_turns_colour, get_does_act, get_does_act, get_does_gesture,
                        get_does_gesture]

def random_bio(s=2):
    bits = sentence_entrypoints[:]
    random.shuffle(bits)
    bits = bits[:s]
    bits = map(lambda x: x().capitalize(), bits)
    return " ".join(bits)

if __name__ == "__main__":
    for n in xrange(5):
        print random_bio()
