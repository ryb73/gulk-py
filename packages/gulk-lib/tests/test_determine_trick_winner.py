from typing import TYPE_CHECKING

from gulk_lib.cards import CardId, Joker, SuitedCard
from gulk_lib.determine_trick_winner import (
    compare_rank,
    compare_suits,
    determine_trick_winner,
)
from gulk_lib.player_id import PlayerId

if TYPE_CHECKING:
    from gulk_lib.game_state import Trick


def test_compare_suits_returns_equal_when_suits_match():
    assert compare_suits(a="♠", b="♠", trump="♥") == "Equal"


def test_compare_suits_returns_equal_when_suits_match_trump():
    assert compare_suits(a="♥", b="♥", trump="♥") == "Equal"


def test_compare_suits_returns_b_when_b_is_trump():
    assert compare_suits(a="♠", b="♥", trump="♥") == "B"


def test_compare_suits_returns_a_when_neither_is_trump():
    assert compare_suits(a="♠", b="♥", trump="♦") == "A"


def test_compare_suits_returns_a_when_a_is_trump_but_not_b():
    assert compare_suits(a="♥", b="♠", trump="♥") == "A"


def test_compare_suits_returns_a_when_there_is_no_trump():
    assert compare_suits(a="♠", b="♥", trump=None) == "A"


def test_compare_rank_returns_a_when_a_is_higher():
    assert compare_rank(a=3, b=2) == "A"


def test_compare_rank_returns_a_when_a_is_higher_face():
    assert compare_rank(a="K", b="Q") == "A"


def test_compare_rank_returns_b_when_b_is_higher():
    assert compare_rank(a=2, b=3) == "B"


def test_compare_rank_returns_b_when_b_is_higher_face():
    assert compare_rank(a="J", b="Q") == "B"


def test_compare_rank_returns_equal_when_ranks_match():
    assert compare_rank(a=5, b=5) == "Equal"


def test_compare_rank_returns_equal_when_ranks_match_face():
    assert compare_rank(a="A", b="A") == "Equal"


def test_compare_rank_treats_face_cards_as_higher_than_numbers():
    assert compare_rank(a=10, b="J") == "B"


def test_compare_rank_treats_ace_as_the_highest_rank():
    assert compare_rank(a="A", b="K") == "A"
    assert compare_rank(a=2, b="A") == "B"


def test_determine_trick_winner_lead_player_wins_against_lower_rank_of_same_suit():
    player_1, player_2 = PlayerId("1"), PlayerId("2")
    trick: Trick = [
        (player_1, SuitedCard(id=CardId(0), rank=9, suit="♠")),
        (player_2, SuitedCard(id=CardId(1), rank=3, suit="♠")),
    ]

    assert determine_trick_winner(trick, trump=None) == player_1


def test_determine_trick_winner_higher_rank_of_same_suit_wins():
    player_1, player_2 = PlayerId("1"), PlayerId("2")
    trick: Trick = [
        (player_1, SuitedCard(id=CardId(0), rank=5, suit="♠")),
        (player_2, SuitedCard(id=CardId(1), rank=9, suit="♠")),
    ]

    assert determine_trick_winner(trick, trump=None) == player_2


def test_determine_trick_winner_off_suit_card_never_wins():
    player_1, player_2 = PlayerId("1"), PlayerId("2")
    trick: Trick = [
        (player_1, SuitedCard(id=CardId(0), rank=5, suit="♠")),
        (player_2, SuitedCard(id=CardId(1), rank="A", suit="♦")),
    ]
    trump = SuitedCard(id=CardId(2), rank=2, suit="♥")

    assert determine_trick_winner(trick, trump) == player_1


def test_determine_trick_winner_multiple_same_suit_non_trump_cards_resolve_by_rank():
    player_1, player_2, player_3 = PlayerId("1"), PlayerId("2"), PlayerId("3")
    trick: Trick = [
        (player_1, SuitedCard(id=CardId(0), rank=5, suit="♠")),
        (player_2, SuitedCard(id=CardId(1), rank=9, suit="♠")),
        (player_3, SuitedCard(id=CardId(2), rank=7, suit="♠")),
    ]
    trump = SuitedCard(id=CardId(3), rank=6, suit="♥")

    assert determine_trick_winner(trick, trump) == player_2


def test_determine_trick_winner_trump_beats_higher_ranked_lead_suit():
    player_1, player_2 = PlayerId("1"), PlayerId("2")
    trick: Trick = [
        (player_1, SuitedCard(id=CardId(0), rank="A", suit="♠")),
        (player_2, SuitedCard(id=CardId(1), rank=2, suit="♥")),
    ]
    trump = SuitedCard(id=CardId(2), rank=6, suit="♥")

    assert determine_trick_winner(trick, trump) == player_2


def test_determine_trick_winner_earlier_trump_play_beats_later_trump_play_by_rank():
    player_1, player_2, player_3 = PlayerId("1"), PlayerId("2"), PlayerId("3")
    trick: Trick = [
        (player_1, SuitedCard(id=CardId(0), rank="A", suit="♠")),
        (player_2, SuitedCard(id=CardId(1), rank=9, suit="♥")),
        (player_3, SuitedCard(id=CardId(2), rank=2, suit="♥")),
    ]
    trump = SuitedCard(id=CardId(3), rank=6, suit="♥")

    assert determine_trick_winner(trick, trump) == player_2


def test_determine_trick_winner_later_trump_play_beats_earlier_trump_play_by_rank():
    player_1, player_2, player_3 = PlayerId("1"), PlayerId("2"), PlayerId("3")
    trick: Trick = [
        (player_1, SuitedCard(id=CardId(0), rank="A", suit="♠")),
        (player_2, SuitedCard(id=CardId(1), rank=2, suit="♥")),
        (player_3, SuitedCard(id=CardId(2), rank=9, suit="♥")),
    ]
    trump = SuitedCard(id=CardId(3), rank=6, suit="♥")

    assert determine_trick_winner(trick, trump) == player_3


def test_determine_trick_winner_lead_joker_wins_regardless_of_other_cards():
    player_1, player_2 = PlayerId("1"), PlayerId("2")
    trick: Trick = [
        (player_1, Joker(id=CardId(0))),
        (player_2, SuitedCard(id=CardId(1), rank="A", suit="♥")),
    ]
    trump = SuitedCard(id=CardId(2), rank=6, suit="♥")

    assert determine_trick_winner(trick, trump) == player_1


def test_determine_trick_winner_joker_played_by_a_follower_wins():
    player_1, player_2 = PlayerId("1"), PlayerId("2")
    trick: Trick = [
        (player_1, SuitedCard(id=CardId(0), rank=5, suit="♠")),
        (player_2, Joker(id=CardId(1))),
    ]

    assert determine_trick_winner(trick, trump=None) == player_2


def test_determine_trick_winner_joker_wins_immediately_ignoring_later_cards():
    player_1, player_2, player_3 = PlayerId("1"), PlayerId("2"), PlayerId("3")
    trick: Trick = [
        (player_1, SuitedCard(id=CardId(0), rank=5, suit="♠")),
        (player_2, Joker(id=CardId(1))),
        (player_3, SuitedCard(id=CardId(2), rank="A", suit="♥")),
    ]
    trump = SuitedCard(id=CardId(3), rank=6, suit="♥")

    assert determine_trick_winner(trick, trump) == player_2


def test_determine_first_joker_wins():
    player_1, player_2, player_3 = PlayerId("1"), PlayerId("2"), PlayerId("3")
    trick: Trick = [
        (player_1, SuitedCard(id=CardId(0), rank=5, suit="♠")),
        (player_2, Joker(id=CardId(1))),
        (player_3, Joker(id=CardId(2))),
    ]
    trump = SuitedCard(id=CardId(3), rank=6, suit="♥")

    assert determine_trick_winner(trick, trump) == player_2


def test_determine_trick_winner_trump_card_being_a_joker_means_no_suit_is_trump():
    player_1, player_2 = PlayerId("1"), PlayerId("2")
    trick: Trick = [
        (player_1, SuitedCard(id=CardId(0), rank=5, suit="♠")),
        (player_2, SuitedCard(id=CardId(1), rank=9, suit="♥")),
    ]
    trump = Joker(id=CardId(2))

    assert determine_trick_winner(trick, trump) == player_1
