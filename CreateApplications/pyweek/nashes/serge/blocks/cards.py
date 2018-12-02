"""Simple card system"""

import random


# Error classes
class NoCard(Exception):
    """The collection was empty"""


class CardNotFound(Exception):
    """The card was not found"""


class Card(object):
    """A card for use in a card game"""

    def __init__(self, name):
        """Initialise the card"""
        self.name = name


class CardCollection(object):
    """A collection of cards"""

    def __init__(self):
        """Initialise the collection"""
        self.cards = []

    def numberOfCards(self):
        """Return the number of cards in the deck"""
        return len(self.cards)

    def addCardToTop(self, card):
        """Add a card to the top of the deck"""
        self.cards.append(card)

    def addCardsToTop(self, cards):
        """Add multiple cards to the top of the deck"""
        for card in cards:
            self.addCardToTop(card)

    def containsCard(self, card):
        """Return True if the collection contains the card"""
        return card in self.cards

    def clearCards(self):
        """Clear all the cards"""
        self.cards[:] = []

    def getCards(self):
        """Return all the cards"""
        #
        # Return a copy of the list to avoid accidentally changing the deck
        return self.cards[:]

    def shuffleCards(self):
        """Shuffle the cards"""
        random.shuffle(self.cards)

    def drawTopCard(self):
        """Draw the top card"""
        try:
            return self.cards.pop(-1)
        except IndexError:
            raise NoCard('There are no cards in the collection')

    def drawTopCards(self, number):
        """Return a number of cards from the top of the deck"""
        return [self.drawTopCard() for _ in range(number)]

    def drawSpecificCard(self, card):
        """Withdraw a specific card from the collection"""
        try:
            self.cards.remove(card)
        except ValueError:
            raise CardNotFound('Card %s was not in the collection' % card)
        else:
            return card


class Deck(CardCollection):
    """A deck of cards"""


class StandardCard(Card):
    """A standard card"""

    # Suits
    HEART = 'Heart'
    DIAMOND = 'Diamond'
    CLUB = 'Club'
    SPADE = 'Spade'

    SUITS = [HEART, DIAMOND, CLUB, SPADE]

    def __init__(self, suit, card):
        """Initialise the card"""
        super(StandardCard, self).__init__('%s-%s' % (card, suit[0]))
        self.suit = suit
        self.card = card


class StandardDeck(Deck):
    """A deck of standard cards"""

    def __init__(self):
        """Initialise the deck"""
        super(StandardDeck, self).__init__()
        #
        # Add the cards
        for suit in StandardCard.SUITS:
            for card in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
                self.addCardToTop(StandardCard(suit, card))

