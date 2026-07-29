from dataclasses import dataclass

from gulk_lib.cards import Card
from gulk_lib.game_state import GameConfig


@dataclass
class NewGame:
    game_config: GameConfig


@dataclass
class Deal:
    deck: list[Card]
    dealer_id: int
    cards_per_player: int
    trump: bool


@dataclass
class PlayCard:
    player_id: int
    card_id: int


GameEvent = NewGame | Deal | PlayCard
