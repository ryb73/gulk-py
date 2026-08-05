from gulk_lib.game_config import Player
from gulk_lib.player_id import PlayerId


def make_player(player_id: int) -> Player:
    return Player(PlayerId(str(player_id)), f"Player {player_id}")
