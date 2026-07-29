from dataclasses import dataclass, field


@dataclass
class Player:
    id: str
    name: str


@dataclass
class GameConfig:
    players: list[Player]
    jokers: int


@dataclass
class GameState:
    config: GameConfig | None = None
    scores: dict[str, int] = field(default_factory=dict)
    hand: int = 0
