from inline_snapshot import snapshot

from gulk_lib.game_rounds import (
    GAME_ROUNDS,
    NO_TRUMP_NO_TRICKS,
    BidScoringRule,
    TrickScoringRule,
)
from gulk_lib.game_state import HandState, Trick
from gulk_lib.player_id import PlayerId
from gulk_lib.scoring import (
    calculate_hand_score_for_bid,
    calculate_hand_score_for_player,
    calculate_hand_scores,
    get_sweeping_player,
    score_round,
)


def test_calculate_hand_score_for_bid_awards_points_when_bid_is_met():
    rule = BidScoringRule()
    assert calculate_hand_score_for_bid(rule, bid=3, tricks_taken=3) == 13


def test_calculate_hand_score_for_bid_awards_nothing_when_bid_is_missed_low():
    rule = BidScoringRule()
    assert calculate_hand_score_for_bid(rule, bid=3, tricks_taken=2) == 0


def test_calculate_hand_score_for_bid_awards_nothing_when_bid_is_missed_high():
    rule = BidScoringRule()
    assert calculate_hand_score_for_bid(rule, bid=3, tricks_taken=4) == 0


def test_calculate_hand_score_for_bid_uses_the_given_rules_values():
    rule = BidScoringRule(base_points=5, points_per_trick=2)
    assert calculate_hand_score_for_bid(rule, bid=2, tricks_taken=2) == 9


def test_get_sweeping_player_returns_the_winner_of_a_single_trick():
    player_1 = PlayerId("1")
    assert get_sweeping_player([(player_1, [])]) == player_1


def test_get_sweeping_player_returns_the_player_who_won_every_trick():
    player_1 = PlayerId("1")
    finished_tricks: list[tuple[PlayerId, Trick]] = [
        (player_1, []),
        (player_1, []),
        (player_1, []),
    ]
    assert get_sweeping_player(finished_tricks) == player_1


def test_get_sweeping_player_returns_none_when_tricks_are_split():
    player_1, player_2 = PlayerId("1"), PlayerId("2")
    finished_tricks: list[tuple[PlayerId, Trick]] = [(player_1, []), (player_2, [])]
    assert get_sweeping_player(finished_tricks) is None


def test_calculate_hand_score_for_player_with_bid_rule_uses_that_players_own_bid():
    player_1, player_2 = PlayerId("1"), PlayerId("2")
    rule = BidScoringRule()
    hand_state = HandState(
        player_bids={player_1: 2, player_2: 0},
        finished_tricks=[
            (player_1, []),
            (player_2, []),
            (player_2, []),
            (player_1, []),
        ],
    )

    player_1_actual = calculate_hand_score_for_player(rule, hand_state, player_1)
    assert player_1_actual == 12
    player_2_actual = calculate_hand_score_for_player(rule, hand_state, player_2)
    assert player_2_actual == 0


def test_calculate_hand_score_for_player_with_trick_rule_and_no_sweep():
    player_1, player_2 = PlayerId("1"), PlayerId("2")
    rule = TrickScoringRule()
    hand_state = HandState(
        finished_tricks=[(player_1, []), (player_2, []), (player_2, [])]
    )

    player_1_actual = calculate_hand_score_for_player(rule, hand_state, player_1)
    assert player_1_actual == -2

    player_2_actual = calculate_hand_score_for_player(rule, hand_state, player_2)
    assert player_2_actual == -4


def test_calculate_hand_score_for_player_with_trick_rule_respects_sweep():
    player_1, player_2 = PlayerId("1"), PlayerId("2")
    rule = TrickScoringRule()
    hand_state = HandState(finished_tricks=[(player_1, []), (player_1, [])])

    player_1_actual = calculate_hand_score_for_player(rule, hand_state, player_1)
    assert player_1_actual == 10

    player_2_actual = calculate_hand_score_for_player(rule, hand_state, player_2)
    assert player_2_actual == -10


def test_calculate_hand_scores_covers_every_player_even_those_with_no_tricks():
    player_1, player_2, player_3 = PlayerId("1"), PlayerId("2"), PlayerId("3")
    rule = BidScoringRule()
    hand_state = HandState(
        player_bids={player_1: 2, player_2: 0, player_3: 0},
        player_hands={player_1: [], player_2: [], player_3: []},
        finished_tricks=[(player_1, []), (player_1, []), (player_2, [])],
    )

    assert calculate_hand_scores(rule, hand_state) == snapshot(
        {"1": 12, "2": 0, "3": 10}
    )


def test_score_round_uses_the_bid_scoring_rule_for_a_bid_round():
    player_1, player_2, player_3 = PlayerId("1"), PlayerId("2"), PlayerId("3")
    hand_state = HandState(
        player_bids={player_1: 3, player_2: 2, player_3: 3},
        player_hands={player_1: [], player_2: [], player_3: []},
        finished_tricks=[
            (player_1, []),
            (player_1, []),
            (player_2, []),
            (player_3, []),
            (player_3, []),
            (player_2, []),
            (player_1, []),
        ],
    )

    assert score_round(6, hand_state) == snapshot({"1": 13, "2": 12, "3": 0})


def test_score_round_uses_the_trick_scoring_rule_for_a_no_trick_round():
    player_1, player_2, player_3 = PlayerId("1"), PlayerId("2"), PlayerId("3")
    hand_index = GAME_ROUNDS.index(NO_TRUMP_NO_TRICKS)
    hand_state = HandState(
        player_hands={player_1: [], player_2: [], player_3: []},
        finished_tricks=[
            (player_1, []),
            (player_1, []),
            (player_2, []),
            (player_2, []),
            (player_2, []),
            (player_2, []),
            (player_2, []),
        ],
    )

    assert score_round(hand_index, hand_state) == snapshot({"1": -4, "2": -10, "3": 0})
