from pprint import pformat

from inline_snapshot import external

from gulk_lib.apply_event import apply_event
from gulk_lib.events import NewGame
from gulk_lib.game_config import GameConfig
from gulk_lib.game_state import GameState
from tests.factories import make_player


def test_new_game():
    player_1, player_2 = make_player(1), make_player(2)
    events = [NewGame(GameConfig([player_1, player_2], jokers=0))]

    state = GameState()
    for event in events:
        apply_event(state, event)

    assert pformat(state) == external("uuid:new_game.txt")
