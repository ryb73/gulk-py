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
    player_bids: dict[PlayerId, int]
    player_hands: dict[PlayerId, list[Card]]
    current_trick: Trick
    finished_tricks: list[tuple[PlayerId, Trick]]
    trump: Card | None


@dataclass
class GameState:
    config: GameConfig | None = None
    scores: dict[PlayerId, int] = field(default_factory=dict)
    hand_index: int = 0
    hand_state: HandState | None = None
