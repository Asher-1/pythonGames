"""A reserve of water"""


class WaterReserve(object):
    """Model for a reserve of Water"""

    def __init__(self, amount):
        """Initialise the reserve"""
        self.amount = amount

    def findWater(self, found):
        """Add the amount of Water to the reserve"""
        self.amount = max(0, self.amount + found)

    def useWater(self, used):
        """Remove the amount of Water to the reserve"""
        self.amount = max(0, self.amount - used)

    def isEmpty(self):
        """Return True if the reserve is empty"""
        return self.amount <= 0

    def drinkWater(self, people):
        """Let the people drink water"""
        for person in people:
            amount_to_drink = person.drinks
            self.amount = max(0, self.amount - amount_to_drink)
            person.drinkWater()