from dataclasses import dataclass

from gulk_lib.cards import Card, CardId
from gulk_lib.game_state import GameConfig
from gulk_lib.player_id import PlayerId


@dataclass
class NewGame:
    game_config: GameConfig


@dataclass
class Deal:
    shuffled_deck: list[Card]
    dealer_id: PlayerId
    cards_per_player: int
    deal_trump: bool


@dataclass
class Bid:
    player_id: PlayerId
    num_tricks: int


@dataclass
class PlayCard:
    player_id: PlayerId
    card_id: CardId


GameEvent = NewGame | Deal | Bid | PlayCard
