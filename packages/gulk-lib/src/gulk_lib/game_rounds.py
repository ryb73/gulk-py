from dataclasses import dataclass


@dataclass(frozen=True)
class BidScoringRule:
    base_points: int = 10
    points_per_trick: int = 1


@dataclass(frozen=True)
class SweepScoringRule:
    winner: int = 10
    losers: int = -10


DEFAULT_SWEEP_SCORING = SweepScoringRule()


@dataclass(frozen=True)
class TrickScoringRule:
    per_trick_score: int = -2
    sweep_scoring: SweepScoringRule = DEFAULT_SWEEP_SCORING


ScoringRule = BidScoringRule | TrickScoringRule

DEFAULT_BID_SCORING = BidScoringRule()
DEFAULT_NO_TRICK_SCORING = TrickScoringRule()


@dataclass(frozen=True)
class RoundDef:
    num_cards: int = 7
    scoring_rule: ScoringRule = DEFAULT_BID_SCORING
    deal_trump: bool = True
    bid_before_hand_seen: bool = False
    bid_before_trump_seen: bool = False
    forced_bid: int | None = None


NO_TRUMP_NO_TRICKS = RoundDef(deal_trump=False, scoring_rule=DEFAULT_NO_TRICK_SCORING)
TRUMP_NO_TRICKS = RoundDef(scoring_rule=DEFAULT_NO_TRICK_SCORING)
BID_3 = RoundDef(forced_bid=3)
HALF_BLIND = RoundDef(bid_before_trump_seen=True)
FULL_BLIND = RoundDef(bid_before_trump_seen=True, bid_before_hand_seen=True)
NO_TRUMP_TRICKS = RoundDef(deal_trump=False)

GAME_ROUNDS = [
    RoundDef(1),
    RoundDef(2),
    RoundDef(3),
    RoundDef(4),
    RoundDef(5),
    RoundDef(6),
    RoundDef(7),
    NO_TRUMP_NO_TRICKS,
    TRUMP_NO_TRICKS,
    BID_3,
    HALF_BLIND,
    FULL_BLIND,
    NO_TRUMP_TRICKS,
    RoundDef(7),
    RoundDef(6),
    RoundDef(5),
    RoundDef(4),
    RoundDef(3),
    RoundDef(2),
    RoundDef(1),
]
