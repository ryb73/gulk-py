from typing import assert_never

from gulk_lib.events import GameEvent, NewGame
from gulk_lib.game_state import GameState


def apply_event(state: GameState, event: GameEvent):
    match event:
        case NewGame(config):
            assert state.config is None
            state.config = config
        case _:
            assert_never(event)
