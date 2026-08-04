from typing import TYPE_CHECKING, Literal

from gulk_lib.cards import Card, CardSuit, Joker, Rank, SuitedCard
from gulk_lib.game_state import Trick

if TYPE_CHECKING:
    from gulk_lib.player_id import PlayerId

SuitComparison = Literal["A", "B", "Equal"]


def compare_suits(a: CardSuit, b: CardSuit, trump: CardSuit | None) -> SuitComparison:
    if a == b:
        return "Equal"
    if b == trump:
        return "B"
    return "A"


ranks_in_order = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]


def compare_rank(a: Rank, b: Rank):
    if a == b:
        return "Equal"

    for rank in ranks_in_order:
        if rank == a:
            return "B"
        if rank == b:
            return "A"

    msg = f"Neither card found in ranks_in_order: a={a}; b={b}"
    raise ValueError(msg)


def determine_trick_winner(current_trick: Trick, trump: Card | None):
    trick_iter = iter(current_trick)
    lead_player_id, lead_card = next(trick_iter)

    if isinstance(lead_card, Joker):
        return lead_player_id

    trump_suit = trump.suit if isinstance(trump, SuitedCard) else None

    winning_play: tuple[PlayerId, SuitedCard] = (lead_player_id, lead_card)
    for challenger_id, challenger_card in trick_iter:
        if isinstance(challenger_card, Joker):
            return challenger_id

        suit_comparison = compare_suits(
            a=winning_play[1].suit, b=challenger_card.suit, trump=trump_suit
        )
        match suit_comparison:
            case "A":
                continue
            case "B":
                winning_play = (challenger_id, challenger_card)
            case "Equal":
                if compare_rank(a=winning_play[1].rank, b=challenger_card.rank) == "B":
                    winning_play = (challenger_id, challenger_card)

    return winning_play[0]
