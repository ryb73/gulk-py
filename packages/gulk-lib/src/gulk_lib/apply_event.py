from typing import TYPE_CHECKING, assert_never

from gulk_lib.events import Deal, GameEvent, NewGame
from gulk_lib.game_state import GameState, HandState

if TYPE_CHECKING:
    from gulk_lib.cards import Card
    from gulk_lib.player_id import PlayerId


def apply_event(state: GameState, event: GameEvent):
    match event:
        case NewGame(config):
            assert state.config is None
            state.config = config
        case Deal(shuffled_deck, _, cards_per_player, deal_trump):
            assert state.config is not None
            assert cards_per_player * len(state.config.players) + (
                1 if deal_trump else 0
            ) <= len(shuffled_deck)

            # Give each player cards_per_player cards. In real life you'd deal
            # round-robin style starting with the player after the dealer, but
            # technically it doesn't matter since the deck is random anyway.
            player_hands: dict[PlayerId, list[Card]] = {
                p.id: shuffled_deck[
                    i * cards_per_player : (i * cards_per_player) + cards_per_player
                ]
                for i, p in enumerate(state.config.players)
            }

            num_cards_dealt = sum(len(hand) for hand in player_hands.values())

            state.hand_state = HandState(
                player_hands, {}, shuffled_deck[num_cards_dealt] if deal_trump else None
            )
        case _:
            assert_never(event)
