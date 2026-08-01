import random

from gulk_lib.cards import Card


def shuffle_deck(deck: list[Card], rng: random.Random | None = None) -> list[Card]:
    """Return a shuffled copy of `deck`.

    This is the impure edge of the system: `apply_event` stays deterministic by
    consuming the shuffled deck off the `Deal` event rather than shuffling itself.

    Args:
        deck: The deck to shuffle, typically from `build_deck`.
        rng: Source of randomness. Pass a seeded `random.Random` for
            reproducible shuffles in tests.

    Returns:
        A new list holding the same cards in shuffled order.
    """
    shuffled = list(deck)
    (rng or random).shuffle(shuffled)
    return shuffled
