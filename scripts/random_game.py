"""Generate a full 20-round Gulk game with random-but-legal player decisions.

Useful for fuzzing/stress-testing gulk-lib's event reducer, trick-winner logic,
and scoring across an entire game rather than the handful of events most tests
hand-write. Run with `uv run python scripts/random_game.py`.
"""

import argparse
import random
from typing import assert_never

from gulk_lib.apply_event import apply_event
from gulk_lib.build_deck import build_deck
from gulk_lib.cards import Card, Joker, SuitedCard
from gulk_lib.events import Bid, Deal, GameEvent, NewGame, PlayCard
from gulk_lib.game_config import GameConfig, Player, validate_config
from gulk_lib.game_rounds import GAME_ROUNDS
from gulk_lib.game_state import GameState, Trick
from gulk_lib.player_id import PlayerId
from gulk_lib.shuffle_deck import shuffle_deck


def format_event_for_paste(event: GameEvent, jokers: int) -> str:
    """Render `event` as a call to a `tests.factories` helper (`make_deal`,
    `make_bid`, `make_play_card`) or, for `NewGame`, to `make_player` inline
    inside a literal `GameConfig` -- text meant to be pasted straight into a
    test, not a `repr()` of the event object itself.

    Player/card ids print as bare integers (e.g. `make_bid(player_id=2, ...)`)
    since `PlayerId`/`CardId` are just `str`/`int` `NewType`s under the hood
    -- interpolating them directly already yields the right literal text, and
    the helpers re-wrap them, avoiding the type errors from pasting a raw
    `PlayerId`-typed value where a plain literal was written by hand.
    """
    match event:
        case NewGame(game_config):
            players = ", ".join(f"make_player({p.id})" for p in game_config.players)
            return f"NewGame(GameConfig([{players}], jokers={game_config.jokers}))"
        case Deal(_, dealer_id, cards_per_player, deal_trump):
            return (
                f"make_deal(shuffle_deck(build_deck({jokers}), rng), "
                f"dealer_id={dealer_id}, cards_per_player={cards_per_player}, "
                f"deal_trump={deal_trump})"
            )
        case Bid(player_id, num_tricks):
            return f"make_bid(player_id={player_id}, num_tricks={num_tricks})"
        case PlayCard(player_id, card_id):
            return f"make_play_card(player_id={player_id}, card_id={card_id})"
        case _:
            assert_never(event)


def legal_cards(hand: list[Card], current_trick: Trick) -> list[Card]:
    """Cards from `hand` that are legal to play into `current_trick`.

    Follows suit when possible, matching the convention `determine_trick_winner`
    already assumes: a led Joker has no suit, so it imposes no follow-suit
    constraint on the rest of the trick.
    """
    # TODO(ryan): `not <non_boolean>` shouldn't be allowed – can I get a linter for this?
    if not current_trick:
        return hand

    _, lead_card = current_trick[0]
    if isinstance(lead_card, Joker):
        return hand

    same_suit = [
        card
        for card in hand
        if isinstance(card, SuitedCard) and card.suit == lead_card.suit
    ]
    return same_suit or hand


def _random_bid(rng: random.Random, cards_dealt: int, forbidden: int | None) -> int:
    """A bid in `[0, cards_dealt]`, peaked around the middle rather than uniform.

    `forbidden`, when given, is the one value that would trip the "screw the
    dealer" assertion in `apply_event` (bids summing exactly to `cards_dealt`
    on the last bid of a hand); nudged away from by one instead of resampled,
    since `cards_dealt >= 1` for every round in `GAME_ROUNDS` guarantees a
    neighbor stays in range.
    """
    bid = round(rng.triangular(0, cards_dealt, cards_dealt / 2))
    if bid != forbidden:
        return bid
    return bid + 1 if bid < cards_dealt else bid - 1


def generate_random_game(
    config: GameConfig, deck_rng: random.Random, decision_rng: random.Random
) -> list[GameEvent]:
    """Build a full flat `GameEvent` sequence for one game.

    Applies each event to a local `GameState` as it's generated, since later
    choices (which cards remain in a hand, what's already been bid, who's
    leading a trick) depend on the state produced by earlier ones.

    Deck shuffling and bid/card-play randomization draw from separate `Random`
    instances so that replaying just the `shuffle_deck` calls (as printed by
    `format_event_for_paste` for `--output events`) reproduces the same deals
    -- sharing one `Random` for both would desync after the first hand, since
    the pasted-back bids/plays are fixed literals that no longer consume from
    it between shuffles.
    """
    events: list[GameEvent] = [NewGame(config)]
    state = GameState()
    apply_event(state, events[0])

    player_ids = [p.id for p in config.players]
    num_players = len(player_ids)
    dealer_index = 0

    for round_def in GAME_ROUNDS:
        cards_dealt = round_def.num_cards
        dealer_id = player_ids[dealer_index]

        deal_event = Deal(
            shuffle_deck(build_deck(config.jokers), deck_rng),
            dealer_id,
            cards_dealt,
            round_def.deal_trump,
        )
        events.append(deal_event)
        apply_event(state, deal_event)
        assert state.hand_state is not None

        bid_order = [
            player_ids[(dealer_index + 1 + i) % num_players] for i in range(num_players)
        ]
        for i, player_id in enumerate(bid_order):
            forbidden = (
                cards_dealt - sum(state.hand_state.player_bids.values())
                if i == num_players - 1
                else None
            )
            if round_def.forced_bid is not None and round_def.forced_bid != forbidden:
                num_tricks = round_def.forced_bid
            else:
                num_tricks = _random_bid(decision_rng, cards_dealt, forbidden)

            bid_event = Bid(player_id, num_tricks)
            events.append(bid_event)
            apply_event(state, bid_event)

        leader_index = (dealer_index + 1) % num_players
        for _ in range(cards_dealt):
            trick_order = [
                player_ids[(leader_index + i) % num_players] for i in range(num_players)
            ]
            for player_id in trick_order:
                assert state.hand_state is not None
                hand = state.hand_state.player_hands[player_id]
                card = decision_rng.choice(
                    legal_cards(hand, state.hand_state.current_trick)
                )
                play_event = PlayCard(player_id, card.id)
                events.append(play_event)
                apply_event(state, play_event)

            if state.hand_state is not None:
                winner_id, _ = state.hand_state.finished_tricks[-1]
                leader_index = player_ids.index(winner_id)

        dealer_index = (dealer_index + 1) % num_players

    return events


def _make_players(count: int) -> list[Player]:
    return [Player(PlayerId(str(n)), f"Player {n}") for n in range(1, count + 1)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--players", type=int, default=4, help="Number of players.")
    parser.add_argument(
        "--jokers", type=int, default=0, help="Number of jokers in the deck."
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed, for a reproducible game."
    )
    parser.add_argument(
        "--output",
        choices=["summary", "events"],
        default="summary",
        help=(
            "Print a human-readable summary (default), or a paste-able events "
            "list built from tests.factories helpers."
        ),
    )
    args = parser.parse_args()

    config = GameConfig(_make_players(args.players), args.jokers)
    if not validate_config(config):
        msg = f"Deck too small for {args.players} players with {args.jokers} jokers."
        raise SystemExit(msg)

    # Resolved (rather than left as None) so a derived seed can be printed
    # below for --output events. Deck shuffling gets its own Random, seeded
    # independently from the one driving bid/card-play decisions -- see
    # generate_random_game's docstring for why they can't share one.
    seed = args.seed if args.seed is not None else random.randrange(2**32)
    seed_rng = random.Random(seed)
    deck_seed = seed_rng.randrange(2**32)
    decision_seed = seed_rng.randrange(2**32)
    events = generate_random_game(
        config, random.Random(deck_seed), random.Random(decision_seed)
    )

    if args.output == "events":
        print(f"rng = random.Random({deck_seed})")
        print("[")
        for event in events:
            print(f"    {format_event_for_paste(event, config.jokers)},")
        print("]")
        return

    final_state = GameState()
    for event in events:
        apply_event(final_state, event)

    print(f"Generated {len(events)} events across {len(GAME_ROUNDS)} hands.")
    print(f"Final hand_index: {final_state.hand_index}")
    print("Final scores:")
    for player in config.players:
        print(f"  {player.name}: {final_state.scores[player.id]}")


if __name__ == "__main__":
    main()
