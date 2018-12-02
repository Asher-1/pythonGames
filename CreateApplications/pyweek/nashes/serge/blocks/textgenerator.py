# coding: utf-8
"""Implements a class to help with randomized text generation"""

import random
import re
import fnmatch
import operator


class NameNotFound(Exception): """An expansion for the name was not found"""
class NoOccurrence(Exception): """There was no occurrence of a fact"""
class InvalidTime(Exception): """The time specified was invalid"""


class TextGenerator(object):
    """Generate text from forms
    
    A form gives the possible values for something, for example the
    form for colour might give [red, green, blue].
    
    You can then convert sentences like 'the @colour@ book'
    
    Conversion can be hierarchical like:
        objects are [book, table, @{colour}@ cat]
        
    Sentence 'the @{object}@' would give a "book" or a "red cat".
    
    When looking up examples from text or files the form should be:
    
        type: example1
        type: example2
        
    Or
    
        type {
            example1
            example2
        }
    """
    
    def __init__(self):
        """Initialise the generator"""
        self.forms = {}
        
    def addExample(self, name, conversion):
        """Add a new form"""
        try:
            the_form = self.forms[name]
        except KeyError:
            the_form = set()
            self.forms[name] = the_form
        #
        the_form.add(conversion)

    def addExampleFromText(self, text):
        """Add an example from text - the name is ':' separated from the conversion"""
        parts = [i.strip() for i in text.strip().split(':', 1)]
        if len(parts) != 2:
            raise ValueError('Need ":" separated name and then conversion. Got [%s]' % (parts,))
        self.addExample(*parts)
    
    def addExamplesFromText(self, text):
        """Add a number of examples from text"""
        in_multiline = None
        for idx, full_line in enumerate(text.splitlines()):
            line = full_line.strip()
            if line and not line.startswith('#'):
                if line.endswith('{'):
                    # Multiple lines follow - store the name
                    parts = line.split(' ')
                    if len(parts) != 2:
                        raise ValueError('Need "<name> {" for multi-line (line %d:"%s")' % (idx, full_line))
                    in_multiline = parts[0].strip()
                elif line.endswith('}'):
                    # Multiple lines end
                    in_multiline = None
                else:
                    if not in_multiline:
                        self.addExampleFromText(line)
                    else:
                        self.addExample(in_multiline, line)
    
    def addExamplesFromFile(self, filename):
        """Add multiple examples from a file"""
        text = file(filename, 'r').read()
        self.addExamplesFromText(text)
                
    def getRandomFormCompletion(self, name, properties=None):
        """Return the comletion of a form randomly"""
        properties = {} if properties is None else properties
        try:
            results = self.forms[name]
        except KeyError:
            # No name found
            raise NameNotFound('The expansion @%s@ was not defined' % name)
        else:
            result = random.choice(list(results))
            if name not in properties:
                properties[name] = result
            return result
        
    def getRandomSentence(self, text, properties=None):
        """Return a random sentence from the text"""
        if properties is None:
            properties = {}
        match = re.match('(.*)@{(.+?)}@(.*)', text, re.DOTALL+re.M)
        if match:
            name = match.groups()[1]
            try:
                notfound = False
                replacement = properties[name]
            except KeyError:
                replacement = self.getRandomFormCompletion(name, properties)
            #
            result = self.getRandomSentence(
                match.groups()[0] + 
                replacement + 
                match.groups()[2], properties)
            return result
        else:
            return text

import random

# from http://www.geocities.com/anvrill/names/cc_goth.html
PLACES = ['Adara', 'Adena', 'Adrianne', 'Alarice', 'Alvita', 'Amara', 'Ambika', 'Antonia', 'Araceli', 'Balandria', 'Basha',
'Beryl', 'Bryn', 'Callia', 'Caryssa', 'Cassandra', 'Casondrah', 'Chatha', 'Ciara', 'Cynara', 'Cytheria', 'Dabria', 'Darcei',
'Deandra', 'Deirdre', 'Delores', 'Desdomna', 'Devi', 'Dominique', 'Drucilla', 'Duvessa', 'Ebony', 'Fantine', 'Fuscienne',
'Gabi', 'Gallia', 'Hanna', 'Hedda', 'Jerica', 'Jetta', 'Joby', 'Kacila', 'Kagami', 'Kala', 'Kallie', 'Keelia', 'Kerry',
'Kerry-Ann', 'Kimberly', 'Killian', 'Kory', 'Lilith', 'Lucretia', 'Lysha', 'Mercedes', 'Mia', 'Maura', 'Perdita', 'Quella',
'Riona', 'Safiya', 'Salina', 'Severin', 'Sidonia', 'Sirena', 'Solita', 'Tempest', 'Thea', 'Treva', 'Trista', 'Vala', 'Winta']


###############################################################################
# Markov Name model
# A random name generator, by Peter Corbett
# http://www.pick.ucam.org/~ptc24/mchain.html
# This script is hereby entered into the public domain
###############################################################################

class Mdict:
    def __init__(self):
        self.d = {}
    def __getitem__(self, key):
        if key in self.d:
            return self.d[key]
        else:
            raise KeyError(key)
    def add_key(self, prefix, suffix):
        if prefix in self.d:
            self.d[prefix].append(suffix)
        else:
            self.d[prefix] = [suffix]
    def get_suffix(self,prefix):
        l = self[prefix]
        return random.choice(l)


class MarkovNameGenerator(object):
    """
    A name from a Markov chain
    """
    def __init__(self, names, chainlen=2):
        """
        Building the dictionary
        """
        self.mcd = Mdict()
        oldnames = []
        self.chainlen = chainlen

        for l in names:
            l = l.strip()
            oldnames.append(l)
            s = " " * chainlen + l
            for n in range(0,len(l)):
                self.mcd.add_key(s[n:n+chainlen], s[n+chainlen])
            self.mcd.add_key(s[len(l):len(l)+chainlen], "\n")

    def getName(self, max_length=9):
        """
        New name from the Markov chain
        """
        prefix = " " * self.chainlen
        name = ""
        suffix = ""
        while True:
            suffix = self.mcd.get_suffix(prefix)
            if suffix == "\n" or len(name) > max_length:
                break
            else:
                name = name + suffix
                prefix = prefix[1:] + suffix
        return name.capitalize()

EUROPE = [
    "Moscow",
    "LONDON",
    "St Petersburg",
    "BERLIN",
    "MADRID",
    "ROMA",
    "KIEV",
    "PARIS",
    "Bucharest",
    "BUDAPEST",
    "Hamburg",
    "MINSK",
    "Warsaw",
    "Belgrade",
    "Vienna",
    "Kharkov",
    "Barcelona",
    "Novosibirsk",
    "Nizhny Novgorod",
    "Milan",
    "Ekaterinoburg",
    "Munich",
    "Prague",
    "Samara",
    "Omsk",
    "SOFIA",
    "Dnepropetrovsk",
    "Kazan",
    "Ufa",
    "Chelyabinsk",
    "Donetsk",
    "Naples",
    "Birmingham",
    "Perm",
    "Rostov-na-Donu",
    "Odessa",
    "Volgograd",
    "Cologne",
    "Turin",
    "Voronezh",
    "Krasnoyarsk",
    "Saratov",
    "ZAGREB",
    "Zaporozhye",
    "Lódz",
    "Marseille",
    "RIGA",
    "Lvov",
    "Athens",
    "Salonika",
    "STOCKHOLM",
    "Kraków",
    "Valencia",
    "AMSTERDAM",
    "Leeds",
    "Tolyatti",
    "Kryvy Rig",
    "Sevilla",
    "Palermo",
    "Ulyanovsk",
    "KISHINEV",
    "Genova",
    "Izhevsk",
    "Frankfurt am Main",
    "Krasnodar",
    "Breslau",
    "Glasgow",
    "Yaroslave",
    "Khabarovsk",
    "Vladivostok",
    "Zaragoza",
    "Essen",
    "Rotterdam",
    "Irkutsk",
    "Dortmund",
    "Stuttgart",
    "Barnaul",
    "VILNIUS",
    "Poznan",
    "Düsseldorf",
    "Novokuznetsk",
    "Lisbon",
    "HELSINKI",
    "Málaga",
    "Bremen",
    "Sheffield",
    "SARAJEVO",
    "Penza",
    "Ryazan",
    "Orenburg",
    "Naberezhnye Tchelny",
    "Duisburg",
    "Lipetsk",
    "Hannover",
    "Mykolaiv",
    "Tula",
    "OSLO",
    "Tyumen",
    "Copenhagen",
    "Kemerovo",
    "Moscow",
    "LONDON",
    "St Petersburg",
    "BERLIN",
    "MADRID",
    "ROMA",
    "KIEV",
    "PARIS",
    "Bucharest",
    "BUDAPEST",
    "Hamburg",
    "MINSK",
    "Warsaw",
    "Belgrade",
    "Vienna",
    "Kharkov",
    "Barcelona",
    "Novosibirsk",
    "Nizhny Novgorod",
    "Milan",
    "Ekaterinoburg",
    "Munich",
    "Prague",
    "Samara",
    "Omsk",
    "SOFIA",
    "Dnepropetrovsk",
    "Kazan",
    "Ufa",
    "Chelyabinsk",
    "Donetsk",
    "Naples",
    "Birmingham",
    "Perm",
    "Rostov-na-Donu",
    "Odessa",
    "Volgograd",
    "Cologne",
    "Turin",
    "Voronezh",
    "Krasnoyarsk",
    "Saratov",
    "ZAGREB",
    "Zaporozhye",
    "Lódz",
    "Marseille",
    "RIGA",
    "Lvov",
    "Athens",
    "Salonika",
    "STOCKHOLM",
    "Kraków",
    "Valencia",
    "AMSTERDAM",
    "Leeds",
    "Tolyatti",
    "Kryvy Rig",
    "Sevilla",
    "Palermo",
    "Ulyanovsk",
    "KISHINEV",
    "Genova",
    "Izhevsk",
    "Frankfurt am Main",
    "Krasnodar",
    "Breslau",
    "Glasgow",
    "Yaroslave",
    "Khabarovsk",
    "Vladivostok",
    "Zaragoza",
    "Essen",
    "Rotterdam",
    "Irkutsk",
    "Dortmund",
    "Stuttgart",
    "Barnaul",
    "VILNIUS",
    "Poznan",
    "Düsseldorf",
    "Novokuznetsk",
    "Lisbon",
    "HELSINKI",
    "Málaga",
    "Bremen",
    "Sheffield",
    "SARAJEVO",
    "Penza",
    "Ryazan",
    "Orenburg",
    "Naberezhnye Tchelny",
    "Duisburg",
    "Lipetsk",
    "Hannover",
    "Mykolaiv",
    "Tula",
    "OSLO",
    "Tyumen",
    "Copenhagen",
    "Kemerovo",
]


class FactDatabase(object):
    """Stores facts about the world"""

    def __init__(self):
        """Initialise the database"""
        self.db = {}
        self.current_time = 0

    def addFact(self, fact_id, *params):
        """Add a fact to the database"""
        self.db.setdefault(fact_id, []).append((self.current_time, ) + params)

    def getTime(self):
        """Return the current time"""
        return self.current_time

    def setTime(self, time):
        """Set the current time"""
        if time < self.current_time:
            raise InvalidTime('Tried to set time (%s) before current time (%s)' % (time, self.current_time))
        self.current_time = time

    def _getMatchingFacts(self, fact_id):
        """Return a list of the facts matching the id"""
        if '*' not in fact_id:
            return [fact_id]
        else:
            return fnmatch.filter(self.db.keys(), fact_id)

    def hasOccurred(self, fact_id):
        """Return True if the fact has occurred"""
        ids = self._getMatchingFacts(fact_id)
        if not ids:
            return False
        #
        for this_id in ids:
            if this_id in self.db:
                return True
        else:
            return False

    def getOccurrenceFrequency(self, fact_id):
        """Return the frequency with which a fact as occurred"""
        if self.current_time == 0:
            return 0
        return float(self.getNumberOfOccurrences(fact_id)) / self.current_time

    def getNumberOfOccurrences(self, fact_id):
        """Return the number of times a fact has occurred"""
        total = 0
        for this_id in self._getMatchingFacts(fact_id):
            try:
                total += len(self.db[this_id])
            except KeyError:
                pass
        return total

    def getLastOccurrenceTime(self, fact_id):
        """Return the last time a fact occurred"""
        return self.getLastOccurrence(fact_id)[0]

    def getLastOccurrence(self, fact_id):
        """Return the last instance of an event"""
        results = []
        for this_id in self._getMatchingFacts(fact_id):
            try:
                results.append(self.db[this_id][-1])
            except KeyError:
                pass
        if not results:
            raise NoOccurrence('No occurrences of fact %s' % fact_id)
        else:
            results.sort()
            return results[-1]

    def getLastFactParameters(self, fact_id):
        """Return the parameters for the last time the fact occurred"""
        return self.getLastOccurrence(fact_id)[1:]

    def getFactInstances(self, fact_id):
        """Return all instances of a certain fact"""
        result = []
        for this_id in self._getMatchingFacts(fact_id):
            result.extend(self.db.get(this_id, []))
        result.sort()
        return result


class RuleSystem(object):
    """Implements a rule checking system"""

    def __init__(self, db):
        """Initialise the rule system"""
        self.db = db
        self.rules = []

    def addRule(self, rule, priority=None):
        """Add a rule to the system"""
        if priority is None:
            priority = -len(self.rules)
        self.rules.append((priority, rule))
        self.rules.sort()

    def getBestMatchingRule(self):
        """Return the best rule matching the current world"""
        for _, rule in reversed(self.rules):
            if rule.isMatched(self.db):
                return rule
        else:
            return None

    def FactOccurred(self, fact_id):
        """Return a checker for a fact"""
        return lambda db: db.hasOccurred(fact_id)

    def FactNotOccurred(self, fact_id):
        """Return a checker for a fact not occurring"""
        return lambda db: not db.hasOccurred(fact_id)

    def FactOccurredNumberOfTimes(self, fact_id, number):
        """Return a checker for a fact occurring a number of times"""
        return lambda db: db.getNumberOfOccurrences(fact_id) >= number

    def FactNotOccurredNumberOfTimes(self, fact_id, number):
        """Return a checker for a fact not occurring a number of times"""
        return lambda db: db.getNumberOfOccurrences(fact_id) < number

    def FactOccurredExactNumberOfTimes(self, fact_id, number):
        """Return a checker for a fact occurring a number of times"""
        return lambda db: db.getNumberOfOccurrences(fact_id) == number

    def FactNotOccurredExactNumberOfTimes(self, fact_id, number):
        """Return a checker for a fact not occurring a number of times"""
        return lambda db: db.getNumberOfOccurrences(fact_id) != number

    def FactOccurredFrequency(self, fact_id, frequency):
        """Return a checker for a fact occurring at least the given frequency"""
        return lambda db: db.getOccurrenceFrequency(fact_id) >= frequency

    def FactNotOccurredFrequency(self, fact_id, frequency):
        """Return a checker for a fact occurring at most the given frequency"""
        return lambda db: db.getOccurrenceFrequency(fact_id) < frequency

    def FactRecentlyOccurred(self, fact_id, interval):
        """Return a checker for a fact occurring in the last time interval"""
        def checker(db):
            try:
                return db.getTime() - db.getLastOccurrenceTime(fact_id) <= interval
            except NoOccurrence:
                return False
        return checker

    def FactNotRecentlyOccurred(self, fact_id, interval):
        """Return a checker for a fact not occurring in the last time interval"""
        def checker(db):
            try:
                return db.getTime() - db.getLastOccurrenceTime(fact_id) > interval
            except NoOccurrence:
                return False
        return checker


class Rule(object):
    """Implements a rule"""

    def __init__(self, rule_id, clauses):
        """Initialise the rule"""
        self.rule_id = rule_id
        self.clauses = clauses

    def isMatched(self, db):
        """Return True if the rule is matched"""
        for clause in self.clauses:
            if not clause(db):
                return False
        else:
            return True

    def fireRule(self, db):
        """Call this when the rule should fire

        Override this method to give particular rule behaviours

        """


class RechargingRule(Rule):
    """A rule that must recharge once it fires"""

    def __init__(self, rule_id, clauses, recharge_time):
        """Initialise the rule"""
        super(RechargingRule, self).__init__(rule_id, clauses)
        #
        self.recharge_time = recharge_time
        self._last_fire_time = None

    def fireRule(self, db):
        """Fire the rule"""
        self._last_fire_time = db.getTime()

    def isMatched(self, db):
        """Return True if we are matched - must match and not be charging"""
        if self._last_fire_time is not None and db.getTime() - self._last_fire_time < self.recharge_time:
            return False
        else:
            return super(RechargingRule, self).isMatched(db)


if __name__ == '__main__':
    t = TextGenerator()
    t.addExample('colour', 'red')
    t.addExample('colour', 'green')
    t.addExample('colour', 'blue')
    t.addExample('object', '@thing@')
    t.addExample('object', 'a @colour@ @thing@')
    t.addExample('object', 'a @colour@ @thing@')    
    t.addExample('thing', 'cat')
    t.addExample('thing', 'dog')
    t.addExample('thing', 'book')
    t.addExample('size', 'small')
    t.addExample('size', 'tiny')
    t.addExample('size', 'large')
    t.addExample('thing', '@size@ @thing@')
    
    for i in range(10):
        print t.getRandomSentence('@object@')

    n = TextGenerator()
    n.addExamplesFromText(
    """
     colour:  red
    colour:  blue
    colour:  green 
    colour:  yellow
    colour:  purple 
    colour:  black 
    colour:  fuscia 
    #
    jewel:   diamond
    jewel:   ruby
    jewel:   emerald
    jewel:   saphire    
    #
    size: small
    size: tiny
    size: large
    size: giant
    #
    time-span: everlasting
    time-span: temporary
    time-span: nighttime
    time-span: daytime
    time-span: lifelong
    time-span: eternal
    #
    effect: wellness
    effect: charm
    effect: charisma
    effect: intellect
    #
    jewel-item:  @colour@ @jewel@
    jewel-item:  @jewel@
    #
    jewel-description: The @size@ @jewel-item@ of @property@
    jewel-description: The @jewel-item@ of @property@
    short-jewel-description: @jewel-item@
    #
    property: @time-span@ @effect@
    property: @effect@
    #
    reason: was @verb@ by @name@ in @time@
    verb: lost
    verb: placed
    verb: discarded
    verb: mislaid
    verb: recorded
    #
    name: @first-name@ @last-name@
    name: @first-name@ @last-name@ @post-name@
    first-name: Bob
    first-name: Fred
    first-name: Jim
    first-name: Bill
    first-name: Marvin
    first-name: Jill
    first-name: Alice
    first-name: Sheila
    first-name: Lemon
    last-name: Smith
    last-name: Jones
    last-name: Crimson
    last-name: Little
    last-name: Jenson
    last-name: Williams
    post-name: Junior
    post-name: Senior
    post-name: I
    post-name: II
    #
    time: 1900's
    time: 1800's
    time: 1950's
    time: 1960's
    time: 1970's
    time: 1980's
    time: 1990's
    #
    description: @jewel-description@ @reason@
    #
    """
    )              
    
    for i in range(20):
        print n.getRandomSentence('@description@')

