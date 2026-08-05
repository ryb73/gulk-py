from dataclasses import dataclass, field

from gulk_lib.cards import Card
from gulk_lib.player_id import PlayerId


@dataclass
class Player:
    id: PlayerId
    name: str


@dataclass
class GameConfig:
    players: list[Player]
    jokers: int


Trick = list[tuple[PlayerId, Card]]


@dataclass
class HandState:
    player_bids: dict[PlayerId, int] = field(default_factory=dict)
    """Number of tricks each player bid they will take this hand. Populated as
    Bid events are applied; a player absent from this dict hasn't bid yet."""
    player_hands: dict[PlayerId, list[Card]] = field(default_factory=dict)
    """Cards each player currently holds, i.e. dealt minus those already played."""
    current_trick: Trick = field(default_factory=list)
    """Cards played so far in the trick that's in progress, in play order."""
    finished_tricks: list[tuple[PlayerId, Trick]] = field(default_factory=list)
    """Completed tricks for the hand, each paired with the id of the player who won
    it."""
    trump: Card | None = None
    """The trump card for this hand, or None if the round is played without trump."""


@dataclass
class GameState:
    config: GameConfig | None = None
    scores: dict[PlayerId, int] = field(default_factory=dict)
    hand_index: int = 0
    hand_state: HandState | None = None
