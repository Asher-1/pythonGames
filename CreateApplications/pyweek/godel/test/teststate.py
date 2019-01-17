"""Tests for the state system"""

import unittest
import game.statemachine


class TestStateMachine(unittest.TestCase):
    """Tests for the StateMachine"""

    def setUp(self):
        """Set up the tests"""
        self.s = TestState()

    def tearDown(self):
        """Tear down the tests"""

    def testCanExecuteSteps(self):
        """testCanExecuteSteps: should be able to execute steps"""
        self.assertEqual(0, self.s.flag)
        for i in range(4):
            self.s.update(10)
            self.assertEqual(i + 1, self.s.flag)

    def testTimeMatters(self):
        """testTimeMatters: should wait for the timer to expire"""
        self.assertEqual(0, self.s.flag)
        self.s.update(5)
        self.assertEqual(1, self.s.flag)
        self.s.update(5)
        self.assertEqual(1, self.s.flag)
        self.s.update(5)
        self.assertEqual(2, self.s.flag)

    def testCanCreateOtherGenerators(self):
        """testCanCreateOtherGenerators: should be able to create other generators"""
        self.s = Multiple()
        self.assertEqual((0, 0), (self.s.flag1, self.s.flag2))
        #
        self.s.update(5)
        self.assertEqual((1, 0), (self.s.flag1, self.s.flag2))
        self.s.update(5)
        self.assertEqual((1, 1), (self.s.flag1, self.s.flag2))
        self.s.update(5)
        self.assertEqual((2, 2), (self.s.flag1, self.s.flag2))
        self.s.update(5)
        self.assertEqual((2, 3), (self.s.flag1, self.s.flag2))
        self.s.update(5)
        self.assertEqual((3, 3), (self.s.flag1, self.s.flag2))
        self.s.update(5)
        self.assertEqual((3, 3), (self.s.flag1, self.s.flag2))
        self.s.update(5)
        self.assertEqual((4, 3), (self.s.flag1, self.s.flag2))


class TestState(game.statemachine.StateMachine):
    """A simple test"""

    initial_state = 'initial'
    flag = 0

    def initial(self):
        self.flag = 1
        yield 10
        self.flag = 2
        yield 10
        self.flag = 3
        self.nextState(self.second())

    def second(self):
        self.flag = 4
        yield 10
        self.flag = 5


class Multiple(game.statemachine.StateMachine):
    """A test with multiple generators"""

    initial_state = 'initial'
    flag1 = 0
    flag2 = 0

    def initial(self):
        self.flag1 = 1
        yield 0
        self.addGenerator(self.other())
        yield 5
        self.flag1 = 2
        yield 10
        self.flag1 = 3
        yield 10
        self.flag1 = 4

    def other(self):
        self.flag2 = 1
        yield 5
        self.flag2 = 2
        yield 5
        self.flag2 = 3

if __name__ == '__main__':
    unittest.main()
