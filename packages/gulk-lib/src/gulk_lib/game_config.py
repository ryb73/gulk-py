from dataclasses import dataclass

from gulk_lib.build_deck import build_deck
from gulk_lib.game_rounds import GAME_ROUNDS
from gulk_lib.player_id import PlayerId


@dataclass
class Player:
    id: PlayerId
    name: str


@dataclass
class GameConfig:
    players: list[Player]
    jokers: int


def validate_config(config: GameConfig):
    num_players = len(config.players)
    max_cards_dealt = max(
        r.num_cards * num_players + (1 if r.deal_trump else 0) for r in GAME_ROUNDS
    )
    return max_cards_dealt <= len(build_deck(config.jokers))
