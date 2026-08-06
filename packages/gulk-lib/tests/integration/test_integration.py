from inline_snapshot import external

from gulk_lib.events import NewGame
from gulk_lib.game_config import GameConfig
from gulk_lib.game_state import GameState
from tests.factories import make_player
from tests.integration.history import apply_events, format_history


def test_new_game():
    player_1, player_2 = make_player(1), make_player(2)

    events = [NewGame(GameConfig([player_1, player_2], jokers=0))]

    state = GameState()
    history = apply_events(state, events)

    assert format_history(history) == external("uuid:new_game.txt")


# TODO(ryan): full 20-round game event sequence  # noqa: FIX002
