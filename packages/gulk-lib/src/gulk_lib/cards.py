from dataclasses import dataclass
from typing import Literal

CardSuit = Literal["♠", "♥", "♦", "♣"]
CardValue = Literal[2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A", "Joker"]


@dataclass
class Card:
    value: CardValue
    suit: CardSuit
