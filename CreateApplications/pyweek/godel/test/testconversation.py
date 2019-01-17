"""Tests for the conversation system"""

import unittest
import model.conversation


class TestConversationSystem(unittest.TestCase):
    """Tests for the ConversationSystem"""

    def setUp(self):
        """Set up the tests"""
        self.c = model.conversation.ConversationSystem(
            db_file='conversation.db', recreate=True,
        )
        #
        self.d1 = {
            'person': 'bob',
            'order': 10,
            'state': 'initial',
            'displayed': False,
            'situation': 'start',
        }
        self.d2 = {
            'person': 'bob',
            'order': 20,
            'state': 'initial',
            'displayed': False,
            'situation': 'end',
        }
        self.d3 = {
            'person': 'fred',
            'order': 10,
            'state': 'final',
            'displayed': False,
            'situation': 'start',
        }
        self.d4 = {
            'person': 'fred',
            'order': 5,
            'state': 'initial',
            'displayed': False,
            'situation': 'start',
        }
        self.d5 = {
            'person': 'ant',
            'order': 5,
            'state': 'initial',
            'displayed': False,
            'situation': 'trigger',
            'provides': ['data-1'],
        }
        self.d6 = {
            'person': 'ant',
            'order': 11,
            'state': 'initial',
            'displayed': False,
            'situation': 'start',
        }
        self.d7 = {
            'person': 'ant',
            'order': 5,
            'state': 'initial',
            'displayed': False,
            'situation': 'start',
            'requires': ['data-1'],
        }
        self.d8 = {
            'person': 'ant',
            'order': 1,
            'state': 'initial',
            'displayed': False,
            'situation': 'start',
            'requires': ['data-1', 'data-2'],
        }
        self.d9 = {
            'person': 'ant',
            'order': 1,
            'state': 'initial',
            'displayed': False,
            'situation': 'end',
            'provides': ['data-1', 'data-2'],
        }
        self.d10 = {
            'person': 'billy',
            'order': 1,
            'state': 'initial',
            'displayed': False,
            'situation': 'end',
            'provides': ['data-1', 'data-2'],
            'present': ['freddy'],
        }
        self.d11 = {
            'person': 'billy',
            'order': 1,
            'state': 'initial',
            'displayed': False,
            'situation': 'end',
            'provides': ['data-1', 'data-2'],
            'present': ['freddy', 'billy'],
        }

    def tearDown(self):
        """Tear down the tests"""
        self.c.closeConnection()

    def testCanAddEntry(self):
        """testCanAddEntry: should be able to add an entry"""
        self.c.addEntry(**self.d1)
    
    def testCanGetAnEntry(self):
        """testCanGetAnEntry: should be able to get an entry"""
        guid = self.c.addEntry(
            requires=['nothing', 'something'],
            provides=['something', 'nothing'],
            **self.d1
        )
        item = self.c.getEntry(guid)
        self.assertEqual(guid, item.guid)
        self.assertEqual('bob', item.person)
        self.assertEqual(10, item.order)
        self.assertEqual('initial', item.state)
        self.assertEqual(False, item.displayed)
        self.assertEqual('start', item.situation)
        self.assertEqual(['nothing', 'something'], item.requires)
        self.assertEqual(['something', 'nothing'], item.provides)

    def testCanSetKnowledge(self):
        """testCanSetKnowledge: should be able to set knowledge"""
        self.assertEqual([], self.c.getKnowledge())
        self.c.addKnowledge(['something'])
        self.assertEqual(['something'], self.c.getKnowledge())
        self.c.addKnowledge(['nothing'])
        self.assertEqual(['something', 'nothing'], self.c.getKnowledge())

    def testAddingAlreadyKnown(self):
        """testAddingAlreadyKnown: adding knowledge we already has shouldn't re-add it"""
        self.c.addKnowledge(['something'])
        self.assertEqual(['something'], self.c.getKnowledge())
        self.c.addKnowledge(['something'])
        self.assertEqual(['something'], self.c.getKnowledge())

    def testCanTestKnowledge(self):
        """testCanTestKnowledge: should be able to test knowledge"""
        self.assertFalse(self.c.knowsAbout(['something']))
        self.c.addKnowledge(['nothing'])
        self.assertFalse(self.c.knowsAbout(['something']))
        self.c.addKnowledge(['something'])
        self.assertTrue(self.c.knowsAbout(['something']))

    def testCanTestMultipleKnowledge(self):
        """testCanTestMultipleKnowledge: should be able to test about multiple knowledges"""
        self.assertFalse(self.c.knowsAbout(['something', 'nothing']))
        self.c.addKnowledge(['something'])
        self.assertFalse(self.c.knowsAbout(['something', 'nothing']))
        self.c.addKnowledge(['nothing'])
        self.assertTrue(self.c.knowsAbout(['something', 'nothing']))

    def testCanGetByPersonSituation(self):
        """testCanGetByPersonSituation: should be able to get an entry by person and situation"""
        g1 = self.c.addEntry(**self.d1)
        g2 = self.c.addEntry(**self.d2)
        g3 = self.c.addEntry(**self.d3)
        g4 = self.c.addEntry(**self.d4)
        #
        # By situation
        self.assertEqual(g1, self.c.getNext(person='bob', situation='start').guid)
        self.assertEqual(g2, self.c.getNext(person='bob', situation='end').guid)

    def testCanGetByPersonSituationState(self):
        """testCanGetByPersonSituationState: should be able to get an entry by person and situation and state"""
        self.d3['person'] = 'bob'
        g1 = self.c.addEntry(**self.d1)
        g2 = self.c.addEntry(**self.d2)
        g3 = self.c.addEntry(**self.d3)
        g4 = self.c.addEntry(**self.d4)
        #
        # By situation
        self.assertEqual(g3, self.c.getNext(person='bob', situation='start', state='final').guid)
        self.assertEqual(g1, self.c.getNext(person='bob', situation='start', state='initial').guid)

    def testCanGetByPersonSituationOrder(self):
        """testCanGetByPersonSituationOrder: should be able to get an entry by person and situation and order"""
        g1 = self.c.addEntry(**self.d1)
        g2 = self.c.addEntry(**self.d2)
        g3 = self.c.addEntry(**self.d3)
        g4 = self.c.addEntry(**self.d4)
        #
        # By situation
        self.assertEqual(g4, self.c.getNext(person='fred', situation='start').guid)

    def testGetSituationWithNothing(self):
        """testGetSituationWithNothing: should return none when no situational data"""
        self.assertEqual(None, self.c.getNext(person='fred', situation='start'))
    
    def testCanUseNext(self):
        """testCanUseNext: should be able to use the next entry"""
        g1 = self.c.addEntry(**self.d1)
        g2 = self.c.addEntry(**self.d2)
        g3 = self.c.addEntry(**self.d3)
        g4 = self.c.addEntry(**self.d4)
        #
        self.assertEqual(g4, self.c.getNext(person='fred', situation='start').guid)
        self.c.getAndUseNext(person='fred', situation='start')        
        self.assertEqual(g3, self.c.getNext(person='fred', situation='start').guid)

    def testUsingProvidesSomething(self):
        """testUsingProvidesSomething: using something that provides facts should set that"""
        self.assertEqual([], self.c.getKnowledge())
        g5 = self.c.addEntry(**self.d5)
        #
        # Just adding should do nothing
        self.assertEqual([], self.c.getKnowledge())
        #
        # But using it should create the knowledge
        result = self.c.getAndUseNext(person='ant', situation='trigger')
        self.assertEqual(g5, result.guid)
        #
        self.assertEqual(['data-1'], self.c.getKnowledge())
    
    def testCanProvideMultipleThings(self):
        """testCanProvideMultipleThings: should be able to provide multiple data items"""
        g9 = self.c.addEntry(**self.d9)
        #
        result = self.c.getAndUseNext(person='ant', situation='end')
        self.assertEqual(g9, result.guid)
        self.assertEqual(['data-1', 'data-2'], self.c.getKnowledge())

    def testGetRespectsRequires(self):
        """testGetRespectsRequires: getting the next line should respect required knowledge"""
        g1 = self.c.addEntry(**self.d1)
        g2 = self.c.addEntry(**self.d2)
        g3 = self.c.addEntry(**self.d3)
        g4 = self.c.addEntry(**self.d4)
        g5 = self.c.addEntry(**self.d5)
        g6 = self.c.addEntry(**self.d6)
        g7 = self.c.addEntry(**self.d7)
        g8 = self.c.addEntry(**self.d8)
        #
        self.assertEqual(g6, self.c.getNext(person='ant', situation='start').guid)
        self.c.addKnowledge(['data-1'])
        self.assertEqual(g7, self.c.getNext(person='ant', situation='start').guid)
        self.c.addKnowledge(['data-2'])
        self.assertEqual(g8, self.c.getNext(person='ant', situation='start').guid)

    def testCanPersistOverTime(self):
        """testCanPersistOverTime: should be able to persist over time"""
        self.c.addKnowledge(['one', 'two'])
        self.c.closeConnection()
        #
        self.c = model.conversation.ConversationSystem(db_file='conversation.db')
        self.assertEqual(['one', 'two'], self.c.getKnowledge())

    def testCanReadFromFile(self):
        """testCanReadFromFile: should be able to read from a file"""
        self.c.loadFromFile('test.csv')
        i1 = self.c.getAndUseNext(person='a', situation='given-water')
        self.assertEqual('Thanks for the water', i1.conversation_text)
        self.assertEqual(['a'], i1.present)

        self.assertTrue(self.c.knowsAbout(['done-once']))
        self.assertFalse(self.c.knowsAbout(['done-twice']))
        #
        i2 = self.c.getAndUseNext(person='a',  situation='given-water')
        self.assertEqual('You are too kind', i2.conversation_text)
        self.assertEqual(['a', 'b', 'c'], i2.present)
        self.assertTrue(self.c.knowsAbout(['done-once']))
        self.assertTrue(self.c.knowsAbout(['done-twice']))
        #
        i3 = self.c.getAndUseNext(person='a', situation='given-water')
        self.assertEqual('Much obliged', i3.conversation_text)

    def testGetForAnyCharacter(self):
        """testGetForAnyCharacter: getting the next line can just use a character"""
        g1 = self.c.addEntry(**self.d1)
        g2 = self.c.addEntry(**self.d2)
        g3 = self.c.addEntry(**self.d3)
        g4 = self.c.addEntry(**self.d4)
        g5 = self.c.addEntry(**self.d5)
        g6 = self.c.addEntry(**self.d6)
        g7 = self.c.addEntry(**self.d7)
        g8 = self.c.addEntry(**self.d8)
        #
        self.assertEqual(g4, self.c.getAndUseNext(situation='start', state='initial').guid)
        self.assertEqual(g1, self.c.getAndUseNext(situation='start', state='initial').guid)
        self.assertEqual(g6, self.c.getAndUseNext(situation='start', state='initial').guid)

    def testCanGetWhoIsInConversation(self):
        """testCanGetWhoIsInConversation: should be able to get who is in the conversation"""
        g1 = self.c.addEntry(**self.d1)
        g10 = self.c.addEntry(**self.d10)
        #
        self.assertEqual([], self.c.getEntry(g1).present)
        self.assertEqual(['freddy'], self.c.getEntry(g10).present)

    def testCanRemoveKnowledge(self):
        """testCanRemoveKnowledge: should be able to remove knowledge"""
        self.c.addKnowledge(['one', 'two', 'three'])
        self.assertTrue(self.c.knowsAbout(['one', 'two', 'three']))
        self.c.removeKnowledge('one')
        self.assertFalse(self.c.knowsAbout(['one', 'two', 'three']))
        self.assertTrue(self.c.knowsAbout(['two', 'three']))

    def testRemovingIfAlreadyGoneIsPassThrough(self):
        """testRemovingIfAlreadyGoneIsPassThrough: should pass through when removing twice"""
        self.c.addKnowledge(['one', 'two', 'three'])
        self.c.removeKnowledge('one')
        self.c.removeKnowledge('one')
        self.assertFalse(self.c.knowsAbout(['one', 'two', 'three']))
        self.assertTrue(self.c.knowsAbout(['two', 'three']))

    def testCanConvertPresentToAliveRequires(self):
        """testCanConvertPresentToAliveRequires: should be able to convert present flag to alive"""
        g10 = self.c.addEntry(**self.d10)
        g11 = self.c.addEntry(**self.d11)
        self.c.convertPresentToRequires('{0}-alive')
        self.assertEqual(['freddy-alive'], self.c.getEntry(g10).requires)
        self.assertEqual(['freddy-alive', 'billy-alive'], self.c.getEntry(g11).requires)


if __name__ == '__main__':
    unittest.main()
