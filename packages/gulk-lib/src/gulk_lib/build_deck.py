from itertools import product

from gulk_lib.cards import RANKS, SUITS, Card, CardId, Joker, SuitedCard

DECK_BASE_SIZE = 52


def build_deck(jokers: int) -> list[Card]:
    """Build a deck in canonical (unshuffled) order.

    Each card carries an id equal to its position here. Jokers are appended
    last, so a card's id does not shift with the joker count.

    Args:
        jokers: How many jokers the game plays with.

    Returns:
        Every suited card, followed by `jokers` jokers.
    """

    deck: list[Card] = [
        SuitedCard(CardId(index), rank, suit)
        for index, (suit, rank) in enumerate(product(SUITS, RANKS))
    ]

    suited_count = len(deck)
    deck.extend(Joker(CardId(suited_count + offset)) for offset in range(jokers))
    return deck
