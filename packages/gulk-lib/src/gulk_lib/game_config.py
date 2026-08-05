from dataclasses import dataclass

from gulk_lib.player_id import PlayerId


@dataclass
class Player:
    id: PlayerId
    name: str


@dataclass
class GameConfig:
    players: list[Player]
    jokers: int
