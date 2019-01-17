"""Model for a person"""


class NoWater(Exception):
    """There is no water to drink"""


class Person(object):
    """Model for a person"""

    eat_increase = 1
    drink_increase = 2
    hunger_decrease = 10
    thirst_decrease = 20
    max_health = 100
    max_water = 100

    def __init__(self, eats=0, drinks=0, health=0, water=0, is_infected=False,
                 thirst_decrease=20, hunger_decrease=10, eat_increase=1, drink_increase=2):
        """Initialise the person"""
        self.eats = eats
        self.drinks = drinks
        self.health = health
        self.water = water
        self.is_infected = is_infected
        self.has_eaten = False
        self.has_drunk = False
        self.thirst_decrease = thirst_decrease
        self.hunger_decrease = hunger_decrease
        self.drink_increase = drink_increase
        self.eat_increase = eat_increase

    def isInfected(self):
        """Return True if the person is infected"""
        return self.is_infected

    def hasEaten(self):
        """Return True if the person has eaten"""
        return self.has_eaten

    def hasDrunk(self):
        """Return True if the person has drunk"""
        return self.has_drunk

    def infect(self):
        """Infect the person"""
        self.is_infected = True

    def newDay(self):
        """Reset to the beginning of a day"""
        #
        # Check that we ate and drank
        if not self.hasEaten():
            self.health = max(0, self.health - self.hunger_decrease)
        if not self.hasDrunk():
            self.health = max(0, self.health - self.thirst_decrease)
        #
        self.has_drunk = False
        self.has_eaten = False

    def eatFood(self):
        """Let the person eat food"""
        self.has_eaten = True
        self.health = min(self.max_health, self.health + self.eat_increase)

    def drinkWater(self):
        """Let the person drink some water"""
        if self.water == 0:
            raise NoWater('There is no water to drink')
        #
        self.has_drunk = True
        self.water = max(0, self.water - self.drinks)
        self.health = min(self.max_health, self.health + self.drink_increase)

    def giveWater(self, amount):
        """Give an amount of water"""
        self.water = min(self.max_water, self.water + amount)

    def isDead(self):
        """Return True if the person is dead"""
        return self.health <= 0