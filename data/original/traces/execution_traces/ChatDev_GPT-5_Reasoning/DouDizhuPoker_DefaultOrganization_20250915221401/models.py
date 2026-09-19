'''
Card and deck models for Dou Dizhu, including card representation, deck creation, and sorting utilities.
'''
import random
from typing import List
# Rank values: 3..10 -> 3..10, J=11, Q=12, K=13, A=14, 2=15, Small Joker=16, Big Joker=17
RANK_LABELS = {
    3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10',
    11: 'J', 12: 'Q', 13: 'K', 14: 'A', 15: '2', 16: 'SJ', 17: 'BJ'
}
SUITS = ['♠', '♥', '♣', '♦']  # suits are irrelevant to rules, only for unique visuals and sorting consistency
SUIT_ORDER = {s: i for i, s in enumerate(SUITS)}
class Card:
    """
    Represents a single playing card in Dou Dizhu. Suits are cosmetic; only rank matters for rules.
    Jokers use suit 'J' and ranks 16 (small) and 17 (big).
    """
    __slots__ = ("rank", "suit")
    def __init__(self, rank: int, suit: str):
        self.rank = rank
        self.suit = suit
    @property
    def is_joker(self) -> bool:
        return self.rank >= 16
    def __repr__(self) -> str:
        return f"Card({self.rank},{self.suit})"
    def display(self) -> str:
        if self.is_joker:
            return RANK_LABELS[self.rank]
        return f"{RANK_LABELS[self.rank]}{self.suit}"
    def sort_key(self):
        # High rank higher; sort ascending by rank then suit to make low cards first
        return (self.rank, SUIT_ORDER.get(self.suit, 0))
class Deck:
    """
    A standard Dou Dizhu deck with 54 cards (52 + 2 jokers).
    """
    def __init__(self):
        self.cards: List[Card] = []
        for rank in range(3, 16):  # 3..15 (2)
            for suit in SUITS:
                self.cards.append(Card(rank, suit))
        # Small Joker (16), Big Joker (17)
        self.cards.append(Card(16, 'J'))
        self.cards.append(Card(17, 'J'))
    def shuffle(self):
        random.shuffle(self.cards)
    def deal(self):
        """
        Deals cards to three players: 17 each and 3 bottom cards.
        Returns: (hands: List[List[Card]], bottom: List[Card])
        """
        self.shuffle()
        hands = [self.cards[i*17:(i+1)*17] for i in range(3)]
        bottom = self.cards[51:]
        return hands, bottom
def sort_cards(cards: List[Card]) -> List[Card]:
    """
    Returns a new list sorted by rank then suit (ascending).
    """
    return sorted(cards, key=lambda c: c.sort_key())