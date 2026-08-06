from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass
from pprint import pformat

from gulk_lib.apply_event import apply_event
from gulk_lib.events import GameEvent
from gulk_lib.game_state import GameState


@dataclass
class Step:
    event: GameEvent
    state: GameState


def apply_events(state: GameState, events: Sequence[GameEvent]) -> list[Step]:
    """Apply `events` to `state` in sequence, recording a snapshot of the
    resulting state after each one.

    `apply_event` mutates `state` in place and returns nothing, so each
    snapshot is a deep copy taken right after applying its event -- otherwise
    every recorded step would just alias the same, final, mutated state.
    """
    history: list[Step] = []
    for event in events:
        apply_event(state, event)
        history.append(Step(event, deepcopy(state)))
    return history


def format_history(history: list[Step]) -> str:
    return "\n\n".join(
        f"{pformat(step.event)}\n->\n{pformat(step.state)}" for step in history
    )
