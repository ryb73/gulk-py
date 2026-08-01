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


@dataclass
class HandState:
    player_hands: dict[PlayerId, list[Card]]
    tricks: dict[PlayerId, list[Card]]
    trump: Card | None


@dataclass
class GameState:
    config: GameConfig | None = None
    scores: dict[PlayerId, int] = field(default_factory=dict)
    hand_index: int = 0
    hand_state: HandState | None = None
