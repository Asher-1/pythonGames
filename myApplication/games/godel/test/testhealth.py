"""Tests for the health and water model"""

import unittest
import model.food
import model.water
import model.person


class TestPerson(unittest.TestCase):
    """Tests for the Person"""

    def setUp(self):
        """Set up the tests"""
        self.p1 = model.person.Person(
            eats=1,
            drinks=2,
            health=20,
            water=10,
            is_infected=False,
        )

    def tearDown(self):
        """Tear down the tests"""

    def testProperties(self):
        """testProperties: should have properties"""
        self.assertFalse(self.p1.hasEaten())
        self.assertFalse(self.p1.hasDrunk())

    def testNewDay(self):
        """testNewDay: new day should reset settings"""
        self.p1.newDay()
        self.assertFalse(self.p1.hasEaten())
        self.assertFalse(self.p1.hasDrunk())
        #
        self.p1.eatFood()
        self.p1.drinkWater()
        #
        self.assertTrue(self.p1.hasEaten())
        self.assertTrue(self.p1.hasDrunk())
        #
        self.assertEqual(8, self.p1.water)

    def testCannotDrinkIfNoWater(self):
        """testCannotDrinkIfNoWater: should not be able to drink if don't have water"""
        self.p1.water = 0
        self.assertRaises(model.person.NoWater, self.p1.drinkWater)

    def testCanBeInfected(self):
        """testCanBeInfected: should be able to be infected"""
        self.assertFalse(self.p1.isInfected())
        self.p1.infect()
        self.assertTrue(self.p1.isInfected())


class TestFood(unittest.TestCase):
    """Tests for the Food"""

    def setUp(self):
        """Set up the tests"""
        self.f = model.food.FoodReserve(100)
        self.p = [
            model.person.Person(eats=1),
            model.person.Person(eats=2),
            model.person.Person(eats=3),
        ]

    def tearDown(self):
        """Tear down the tests"""

    def testFindFoodAdds(self):
        """testFindFoodAdds: finding food should add food"""
        self.f.findFood(10)
        self.assertEqual(110, self.f.amount)
        self.f.findFood(-20)
        self.assertEqual(90, self.f.amount)

    def testShouldNotGoBelowZero(self):
        """testShouldNotGoBelowZero: should not go below zero"""
        self.f.findFood(-110)
        self.assertEqual(0, self.f.amount)

    def testCanCheckIfEmpty(self):
        """testCanCheckIfEmpty: should be able to check if the food is empty"""
        self.f.findFood(-110)
        self.assertTrue(self.f.isEmpty())

    def testPeopleEatingFoodShouldReduce(self):
        """testPeopleEatingFoodShouldReduce: people eating food should decrease amount"""
        for p in self.p:
            self.assertFalse(p.hasEaten())
        #
        self.f.eatFood(self.p)
        self.assertEqual(94, self.f.amount)
        #
        for p in self.p:
            self.assertTrue(p.hasEaten())

    def testShouldNotEatBelowZero(self):
        """testShouldNotEatBelowZero: should not eat below zero"""
        self.f.findFood(-95)
        self.assertEqual(5, self.f.amount)
        self.f.eatFood(self.p)
        self.assertEqual(0, self.f.amount)
        self.assertTrue(self.f.isEmpty())


class TestWater(unittest.TestCase):
    """Tests for the Water"""

    def setUp(self):
        """Set up the tests"""
        self.w = model.water.WaterReserve(100)
        self.p = [
            model.person.Person(drinks=1, water=20),
            model.person.Person(drinks=2, water=30),
            model.person.Person(drinks=3, water=5),
        ]

    def tearDown(self):
        """Tear down the tests"""

    def testFindWaterAdds(self):
        """testFindWaterAdds: finding water should add food"""
        self.w.findWater(10)
        self.assertEqual(110, self.w.amount)
        self.w.findWater(-20)
        self.assertEqual(90, self.w.amount)

    def testShouldNotGoBelowZero(self):
        """testShouldNotGoBelowZero: should not go below zero"""
        self.w.findWater(-110)
        self.assertEqual(0, self.w.amount)

    def testCanCheckIfEmpty(self):
        """testCanCheckIfEmpty: should be able to check if the water is empty"""
        self.w.findWater(-110)
        self.assertTrue(self.w.isEmpty())

    def testPeopleDrinkingWaterShouldReduce(self):
        """testPeopleDrinkingFoodShouldReduce: people drinking water should decrease amount"""
        self.w.drinkWater(self.p)
        self.assertEqual(19, self.p[0].water)
        self.assertEqual(28, self.p[1].water)
        self.assertEqual(2, self.p[2].water)

    def testShouldNotDrinkBelowZero(self):
        """testShouldNotDrinkBelowZero: should not eat below zero"""
        self.w.drinkWater(self.p)
        self.w.drinkWater(self.p)
        self.assertEqual(18, self.p[0].water)
        self.assertEqual(26, self.p[1].water)
        self.assertEqual(0, self.p[2].water)


class TestHealth(unittest.TestCase):
    """Tests for the Health"""

    def setUp(self):
        """Set up the tests"""
        self.p1 = model.person.Person(
            eats=1,
            drinks=2,
            health=20,
            water=10,
            is_infected=False,
        )
        self.p1.eat_increase = 2
        self.p1.drink_increase = 3
        self.p1.hunger_decrease = 10
        self.p1.thirst_decrease = 20

    def tearDown(self):
        """Tear down the tests"""

    def testCheckEatingAndDrinking(self):
        """testCheckEating: eating and drinking should gain health"""
        self.p1.eatFood()
        self.p1.drinkWater()
        self.assertEqual(20 + 2 + 3, self.p1.health)

    def testNotEatingAndDrinking(self):
        """testNotEatingAndDrinking: not eating and drinking should lose health"""
        self.p1.health = 100
        self.assertEqual(100, self.p1.health)
        self.p1.newDay()
        self.assertEqual(70, self.p1.health)

    def testShouldNotGoPastMax(self):
        """testShouldNotGoPastMax: should not go past max health"""
        self.p1.max_health = 22
        self.p1.eatFood()
        self.p1.drinkWater()
        self.assertEqual(22, self.p1.health)


if __name__ == '__main__':
    unittest.main()
