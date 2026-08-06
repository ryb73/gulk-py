from typing import TYPE_CHECKING, assert_never

from gulk_lib.determine_trick_winner import determine_trick_winner
from gulk_lib.events import Bid, Deal, GameEvent, NewGame, PlayCard
from gulk_lib.game_config import validate_config
from gulk_lib.game_state import GameState, HandState
from gulk_lib.scoring import score_round

if TYPE_CHECKING:
    from gulk_lib.cards import Card
    from gulk_lib.player_id import PlayerId


def apply_event(state: GameState, event: GameEvent):
    match event:
        case NewGame(config):
            assert state.config is None
            assert validate_config(config)

            state.config = config
            state.scores = {p.id: 0 for p in config.players}

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
                player_hands=player_hands,
                trump=shuffled_deck[num_cards_dealt] if deal_trump else None,
            )

        case Bid(player_id, num_tricks):
            assert state.config is not None
            assert state.hand_state is not None
            assert state.hand_state.player_bids.get(player_id) is None

            if (
                len(state.hand_state.player_bids.values())
                == len(state.config.players) - 1
            ):
                any_player_hand = next(iter(state.hand_state.player_hands.values()))
                num_cards_dealt = len(any_player_hand)
                assert (
                    sum(state.hand_state.player_bids.values()) + num_tricks
                    != num_cards_dealt
                )

            state.hand_state.player_bids[player_id] = num_tricks

        case PlayCard(player_id, card_id):
            assert state.config is not None
            assert state.hand_state is not None

            hand = state.hand_state.player_hands[player_id]
            current_trick = state.hand_state.current_trick

            card = next((c for c in hand if c.id == card_id), None)
            assert card is not None, f"card {card_id} not in {player_id}'s hand"

            hand.remove(card)
            current_trick.append((player_id, card))

            # If all players have played a card for this trick
            if len(current_trick) == len(state.config.players):
                state.hand_state.finished_tricks.append(
                    (
                        determine_trick_winner(current_trick, state.hand_state.trump),
                        current_trick,
                    )
                )
                state.hand_state.current_trick = []

                # If all players are out of cards, then the hand is over (and since all
                # players should have the same number of cards at the end of a trick,
                # we only need to check one player)
                first_player_hand = next(iter(state.hand_state.player_hands.values()))
                if len(first_player_hand) == 0:
                    for player_id, score in score_round(
                        state.hand_index, state.hand_state
                    ).items():
                        state.scores[player_id] += score

                    state.hand_index += 1
                    state.hand_state = None

        case _:
            assert_never(event)
