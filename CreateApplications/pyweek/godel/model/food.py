"""Models a reserve of food"""


class FoodReserve(object):
    """Model for a reserve of food"""

    def __init__(self, amount):
        """Initialise the reserve"""
        self.amount = amount

    def findFood(self, found):
        """Add the amount of food to the reserve"""
        self.amount = max(0, self.amount + found)

    def isEmpty(self):
        """Return True if the reserve is empty"""
        return self.amount <= 0

    def eatFood(self, people):
        """Let the people eat food"""
        for person in people:
            amount_to_eat = person.eats
            self.amount = max(0, self.amount - amount_to_eat)
            person.eatFood()