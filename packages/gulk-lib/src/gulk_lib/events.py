from dataclasses import dataclass

from gulk_lib.game_state import GameConfig


@dataclass
class NewGame:
    game_config: GameConfig


@dataclass
class Shuffle:
    seed: int


@dataclass
class Deal:
    dealer_id: int
    cards_per_player: int
    trump: bool


@dataclass
class PlayCard:
    player_id: int
    card_id: int


GameEvent = NewGame | Shuffle | Deal | PlayCard
