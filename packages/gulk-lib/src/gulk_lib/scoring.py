from gulk_lib.game_rounds import (
    GAME_ROUNDS,
    BidScoringRule,
    ScoringRule,
    TrickScoringRule,
)
from gulk_lib.game_state import HandState, Trick
from gulk_lib.player_id import PlayerId


def calculate_hand_score_for_bid(
    scoring_rule: BidScoringRule, bid: int, tricks_taken: int
):
    if bid == tricks_taken:
        return scoring_rule.base_points + scoring_rule.points_per_trick * tricks_taken
    return 0


def get_sweeping_player(finished_tricks: list[tuple[PlayerId, Trick]]):
    result = None
    for player_id, _ in finished_tricks:
        if result is None:
            result = player_id
        elif result != player_id:
            return None
    return result


def calculate_hand_score_for_player(
    scoring_rule: ScoringRule, hand_state: HandState, player_id: PlayerId
):
    tricks_taken = sum(
        1 for trick_winner, _ in hand_state.finished_tricks if trick_winner == player_id
    )

    match scoring_rule:
        case BidScoringRule():
            return calculate_hand_score_for_bid(
                scoring_rule, hand_state.player_bids[player_id], tricks_taken
            )
        case TrickScoringRule(per_trick_score, sweep_rule):
            sweeper = get_sweeping_player(hand_state.finished_tricks)
            if sweeper == player_id:
                return sweep_rule.winner
            if sweeper is not None:
                return sweep_rule.losers
            return per_trick_score * tricks_taken


def calculate_hand_scores(scoring_rule: ScoringRule, hand_state: HandState):
    return {
        p_id: calculate_hand_score_for_player(scoring_rule, hand_state, p_id)
        for p_id in hand_state.player_hands
    }


def score_round(hand_index: int, hand_state: HandState):
    round_def = GAME_ROUNDS[hand_index]
    return calculate_hand_scores(round_def.scoring_rule, hand_state)
