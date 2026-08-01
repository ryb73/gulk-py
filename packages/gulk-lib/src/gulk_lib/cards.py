from dataclasses import dataclass
from typing import Literal, NewType

CardId = NewType("CardId", int)

CardSuit = Literal["♠", "♥", "♦", "♣"]
Rank = Literal[2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]

# The Literal types above declare which suits and ranks exist; these tuples exist
# only to enumerate them when building a deck. Their order is arbitrary and
# carries no ranking meaning -- game-specific ordering belongs in game logic.
# They are tuples rather than sets so that deck construction, and therefore any
# seeded shuffle, is reproducible across processes (set iteration order varies
# under hash randomization).
SUITS: tuple[CardSuit, ...] = ("♠", "♥", "♦", "♣")
RANKS: tuple[Rank, ...] = (2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A")


@dataclass(frozen=True)
class SuitedCard:
    id: CardId
    rank: Rank
    suit: CardSuit


@dataclass(frozen=True)
class Joker:
    id: CardId


Card = SuitedCard | Joker
