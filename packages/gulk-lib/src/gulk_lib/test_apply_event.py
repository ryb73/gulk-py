from inline_snapshot import snapshot

from gulk_lib.apply_event import apply_event
from gulk_lib.events import NewGame
from gulk_lib.game_state import GameConfig, GameState, Player


def make_player(player_id: int):
    return Player(str(player_id), f"Player {player_id}")


def test_new_game():
    state = GameState()
    apply_event(
        state, NewGame(GameConfig([make_player(1), make_player(2), make_player(3)], 2))
    )
    assert state == snapshot(
        GameState(
            config=GameConfig(
                players=[
                    Player(id="1", name="Player 1"),
                    Player(id="2", name="Player 2"),
                    Player(id="3", name="Player 3"),
                ],
                jokers=2,
            )
        )
    )
