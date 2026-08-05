import pytest
from inline_snapshot import snapshot

from gulk_lib.apply_event import apply_event
from gulk_lib.build_deck import build_deck
from gulk_lib.cards import CardId, Joker, SuitedCard
from gulk_lib.events import Bid, Deal, NewGame, PlayCard
from gulk_lib.game_config import Player
from gulk_lib.game_state import GameConfig, GameState, HandState
from gulk_lib.player_id import PlayerId
from tests.factories import make_player


def test_new_game():
    state = GameState()
    apply_event(
        state, NewGame(GameConfig([make_player(1), make_player(2), make_player(3)], 2))
    )
    assert state == snapshot(
        GameState(
            config=GameConfig(
                players=[
                    Player(id=PlayerId("1"), name="Player 1"),
                    Player(id=PlayerId("2"), name="Player 2"),
                    Player(id=PlayerId("3"), name="Player 3"),
                ],
                jokers=2,
            ),
            scores={PlayerId("1"): 0, PlayerId("2"): 0, PlayerId("3"): 0},
        )
    )


def test_deal_gives_each_player_a_hand_and_leaves_trump_unset():
    player_1, player_2, player_3 = make_player(1), make_player(2), make_player(3)
    deck = build_deck(jokers=0)
    state = GameState(config=GameConfig([player_1, player_2, player_3], jokers=0))

    apply_event(state, Deal(deck, player_1.id, cards_per_player=5, deal_trump=False))

    assert state.hand_state == snapshot(
        HandState(
            player_bids={},
            player_hands={
                PlayerId("1"): [
                    SuitedCard(id=CardId(0), rank=2, suit="♠"),
                    SuitedCard(id=CardId(1), rank=3, suit="♠"),
                    SuitedCard(id=CardId(2), rank=4, suit="♠"),
                    SuitedCard(id=CardId(3), rank=5, suit="♠"),
                    SuitedCard(id=CardId(4), rank=6, suit="♠"),
                ],
                PlayerId("2"): [
                    SuitedCard(id=CardId(5), rank=7, suit="♠"),
                    SuitedCard(id=CardId(6), rank=8, suit="♠"),
                    SuitedCard(id=CardId(7), rank=9, suit="♠"),
                    SuitedCard(id=CardId(8), rank=10, suit="♠"),
                    SuitedCard(id=CardId(9), rank="J", suit="♠"),
                ],
                PlayerId("3"): [
                    SuitedCard(id=CardId(10), rank="Q", suit="♠"),
                    SuitedCard(id=CardId(11), rank="K", suit="♠"),
                    SuitedCard(id=CardId(12), rank="A", suit="♠"),
                    SuitedCard(id=CardId(13), rank=2, suit="♥"),
                    SuitedCard(id=CardId(14), rank=3, suit="♥"),
                ],
            },
            current_trick=[],
            finished_tricks=[],
            trump=None,
        )
    )


def test_deal_sets_trump_to_the_card_after_the_last_hand():
    player_1, player_2 = make_player(1), make_player(2)
    deck = build_deck(jokers=0)[:5]
    state = GameState(config=GameConfig([player_1, player_2], jokers=0))

    apply_event(state, Deal(deck, player_1.id, cards_per_player=2, deal_trump=True))

    assert state.hand_state == snapshot(
        HandState(
            player_bids={},
            player_hands={
                PlayerId("1"): [
                    SuitedCard(id=CardId(0), rank=2, suit="♠"),
                    SuitedCard(id=CardId(1), rank=3, suit="♠"),
                ],
                PlayerId("2"): [
                    SuitedCard(id=CardId(2), rank=4, suit="♠"),
                    SuitedCard(id=CardId(3), rank=5, suit="♠"),
                ],
            },
            current_trick=[],
            finished_tricks=[],
            trump=SuitedCard(id=CardId(4), rank=6, suit="♠"),
        )
    )


def test_deal_supports_the_max_players_and_cards_per_player_the_game_allows():
    # GAME_ROUNDS never deals more than 7 cards per player, so 7 players is the most
    # that can be dealt a full round (49 cards) plus a trump card (50) from a single
    # 52-card deck.
    players = [make_player(n) for n in range(1, 8)]
    deck = build_deck(jokers=0)
    state = GameState(config=GameConfig(players, jokers=0))

    apply_event(state, Deal(deck, players[0].id, cards_per_player=7, deal_trump=True))

    assert state == snapshot(
        GameState(
            config=GameConfig(
                players=[
                    Player(id=PlayerId("1"), name="Player 1"),
                    Player(id=PlayerId("2"), name="Player 2"),
                    Player(id=PlayerId("3"), name="Player 3"),
                    Player(id=PlayerId("4"), name="Player 4"),
                    Player(id=PlayerId("5"), name="Player 5"),
                    Player(id=PlayerId("6"), name="Player 6"),
                    Player(id=PlayerId("7"), name="Player 7"),
                ],
                jokers=0,
            ),
            hand_state=HandState(
                player_hands={
                    PlayerId("1"): [
                        SuitedCard(id=CardId(0), rank=2, suit="♠"),
                        SuitedCard(id=CardId(1), rank=3, suit="♠"),
                        SuitedCard(id=CardId(2), rank=4, suit="♠"),
                        SuitedCard(id=CardId(3), rank=5, suit="♠"),
                        SuitedCard(id=CardId(4), rank=6, suit="♠"),
                        SuitedCard(id=CardId(5), rank=7, suit="♠"),
                        SuitedCard(id=CardId(6), rank=8, suit="♠"),
                    ],
                    PlayerId("2"): [
                        SuitedCard(id=CardId(7), rank=9, suit="♠"),
                        SuitedCard(id=CardId(8), rank=10, suit="♠"),
                        SuitedCard(id=CardId(9), rank="J", suit="♠"),
                        SuitedCard(id=CardId(10), rank="Q", suit="♠"),
                        SuitedCard(id=CardId(11), rank="K", suit="♠"),
                        SuitedCard(id=CardId(12), rank="A", suit="♠"),
                        SuitedCard(id=CardId(13), rank=2, suit="♥"),
                    ],
                    PlayerId("3"): [
                        SuitedCard(id=CardId(14), rank=3, suit="♥"),
                        SuitedCard(id=CardId(15), rank=4, suit="♥"),
                        SuitedCard(id=CardId(16), rank=5, suit="♥"),
                        SuitedCard(id=CardId(17), rank=6, suit="♥"),
                        SuitedCard(id=CardId(18), rank=7, suit="♥"),
                        SuitedCard(id=CardId(19), rank=8, suit="♥"),
                        SuitedCard(id=CardId(20), rank=9, suit="♥"),
                    ],
                    PlayerId("4"): [
                        SuitedCard(id=CardId(21), rank=10, suit="♥"),
                        SuitedCard(id=CardId(22), rank="J", suit="♥"),
                        SuitedCard(id=CardId(23), rank="Q", suit="♥"),
                        SuitedCard(id=CardId(24), rank="K", suit="♥"),
                        SuitedCard(id=CardId(25), rank="A", suit="♥"),
                        SuitedCard(id=CardId(26), rank=2, suit="♦"),
                        SuitedCard(id=CardId(27), rank=3, suit="♦"),
                    ],
                    PlayerId("5"): [
                        SuitedCard(id=CardId(28), rank=4, suit="♦"),
                        SuitedCard(id=CardId(29), rank=5, suit="♦"),
                        SuitedCard(id=CardId(30), rank=6, suit="♦"),
                        SuitedCard(id=CardId(31), rank=7, suit="♦"),
                        SuitedCard(id=CardId(32), rank=8, suit="♦"),
                        SuitedCard(id=CardId(33), rank=9, suit="♦"),
                        SuitedCard(id=CardId(34), rank=10, suit="♦"),
                    ],
                    PlayerId("6"): [
                        SuitedCard(id=CardId(35), rank="J", suit="♦"),
                        SuitedCard(id=CardId(36), rank="Q", suit="♦"),
                        SuitedCard(id=CardId(37), rank="K", suit="♦"),
                        SuitedCard(id=CardId(38), rank="A", suit="♦"),
                        SuitedCard(id=CardId(39), rank=2, suit="♣"),
                        SuitedCard(id=CardId(40), rank=3, suit="♣"),
                        SuitedCard(id=CardId(41), rank=4, suit="♣"),
                    ],
                    PlayerId("7"): [
                        SuitedCard(id=CardId(42), rank=5, suit="♣"),
                        SuitedCard(id=CardId(43), rank=6, suit="♣"),
                        SuitedCard(id=CardId(44), rank=7, suit="♣"),
                        SuitedCard(id=CardId(45), rank=8, suit="♣"),
                        SuitedCard(id=CardId(46), rank=9, suit="♣"),
                        SuitedCard(id=CardId(47), rank=10, suit="♣"),
                        SuitedCard(id=CardId(48), rank="J", suit="♣"),
                    ],
                },
                trump=SuitedCard(id=CardId(49), rank="Q", suit="♣"),
            ),
        )
    )


def test_deal_requires_config_to_already_be_set():
    state = GameState()
    deck = build_deck(jokers=0)

    with pytest.raises(AssertionError):
        apply_event(
            state, Deal(deck, make_player(1).id, cards_per_player=5, deal_trump=False)
        )


def test_deal_requires_enough_cards_for_every_hand_plus_trump():
    player_1, player_2, player_3 = make_player(1), make_player(2), make_player(3)
    deck = build_deck(jokers=0)[:15]
    state = GameState(config=GameConfig([player_1, player_2, player_3], jokers=0))

    with pytest.raises(AssertionError):
        apply_event(state, Deal(deck, player_1.id, cards_per_player=5, deal_trump=True))


def test_bid_records_a_player_bid():
    player_1, player_2 = make_player(1), make_player(2)
    state = GameState(
        config=GameConfig([player_1, player_2], jokers=0),
        hand_state=HandState(
            player_bids={},
            player_hands={player_1.id: [], player_2.id: []},
            current_trick=[],
            finished_tricks=[],
            trump=None,
        ),
    )

    apply_event(state, Bid(player_1.id, 3))

    assert state.hand_state == snapshot(
        HandState(
            player_bids={PlayerId("1"): 3},
            player_hands={PlayerId("1"): [], PlayerId("2"): []},
            current_trick=[],
            finished_tricks=[],
            trump=None,
        )
    )


def test_bid_records_bids_from_multiple_players_independently():
    player_1, player_2 = make_player(1), make_player(2)
    state = GameState(
        config=GameConfig([player_1, player_2], jokers=0),
        hand_state=HandState(
            player_bids={player_1.id: 3},
            player_hands={player_1.id: [], player_2.id: []},
            current_trick=[],
            finished_tricks=[],
            trump=None,
        ),
    )

    apply_event(state, Bid(player_2.id, 0))

    assert state.hand_state == snapshot(
        HandState(
            player_bids={PlayerId("1"): 3, PlayerId("2"): 0},
            player_hands={PlayerId("1"): [], PlayerId("2"): []},
            current_trick=[],
            finished_tricks=[],
            trump=None,
        )
    )


def test_bid_requires_config_to_already_be_set():
    player_1 = make_player(1)
    state = GameState()

    with pytest.raises(AssertionError):
        apply_event(state, Bid(player_1.id, 3))


def test_bid_requires_hand_state_to_already_be_set():
    player_1 = make_player(1)
    state = GameState(config=GameConfig([player_1], jokers=0))

    with pytest.raises(AssertionError):
        apply_event(state, Bid(player_1.id, 3))


def test_bid_raises_if_player_already_bid():
    player_1 = make_player(1)
    state = GameState(
        config=GameConfig([player_1], jokers=0),
        hand_state=HandState(
            player_bids={player_1.id: 3},
            player_hands={player_1.id: []},
            current_trick=[],
            finished_tricks=[],
            trump=None,
        ),
    )

    with pytest.raises(AssertionError):
        apply_event(state, Bid(player_1.id, 5))


def test_play_card_moves_card_from_hand_to_current_trick():
    player_1, player_2 = make_player(1), make_player(2)
    deck = build_deck(0)
    player1_hand = [deck.pop(), deck.pop()]
    state = GameState(
        config=GameConfig([player_1, player_2], jokers=0),
        hand_state=HandState(
            player_bids={},
            player_hands={
                player_1.id: player1_hand,
                player_2.id: [deck.pop(), deck.pop()],
            },
            current_trick=[],
            finished_tricks=[],
            trump=None,
        ),
    )

    apply_event(state, PlayCard(player_1.id, player1_hand[0].id))

    assert state.hand_state == snapshot(
        HandState(
            player_bids={},
            player_hands={
                PlayerId("1"): [SuitedCard(id=CardId(50), rank="K", suit="♣")],
                PlayerId("2"): [
                    SuitedCard(id=CardId(49), rank="Q", suit="♣"),
                    SuitedCard(id=CardId(48), rank="J", suit="♣"),
                ],
            },
            current_trick=[
                (PlayerId("1"), SuitedCard(id=CardId(51), rank="A", suit="♣"))
            ],
            finished_tricks=[],
            trump=None,
        )
    )


def test_play_card_appends_to_existing_current_trick():
    player_1, player_2, player_3 = make_player(1), make_player(2), make_player(3)
    deck = build_deck(0)
    player2_hand = [deck.pop(), deck.pop()]
    state = GameState(
        config=GameConfig([player_1, player_2, player_3], jokers=0),
        hand_state=HandState(
            player_bids={},
            player_hands={
                player_1.id: [deck.pop()],
                player_2.id: player2_hand,
                player_3.id: [deck.pop(), deck.pop()],
            },
            current_trick=[(player_1.id, deck.pop())],
            finished_tricks=[],
            trump=None,
        ),
    )

    apply_event(state, PlayCard(player_2.id, player2_hand[0].id))

    assert state.hand_state == snapshot(
        HandState(
            player_bids={},
            player_hands={
                PlayerId("1"): [SuitedCard(id=CardId(49), rank="Q", suit="♣")],
                PlayerId("2"): [SuitedCard(id=CardId(50), rank="K", suit="♣")],
                PlayerId("3"): [
                    SuitedCard(id=CardId(48), rank="J", suit="♣"),
                    SuitedCard(id=CardId(47), rank=10, suit="♣"),
                ],
            },
            current_trick=[
                (PlayerId("1"), SuitedCard(id=CardId(46), rank=9, suit="♣")),
                (PlayerId("2"), SuitedCard(id=CardId(51), rank="A", suit="♣")),
            ],
            finished_tricks=[],
            trump=None,
        )
    )


def test_play_card_finishes_trick():
    player_1, player_2 = make_player(1), make_player(2)
    deck = build_deck(0)
    player2_hand = [deck.pop(), deck.pop()]
    state = GameState(
        config=GameConfig([player_1, player_2], jokers=0),
        hand_state=HandState(
            player_bids={},
            player_hands={player_1.id: [deck.pop()], player_2.id: player2_hand},
            current_trick=[(player_1.id, deck.pop())],
            finished_tricks=[],
            trump=None,
        ),
    )

    apply_event(state, PlayCard(player_2.id, player2_hand[0].id))

    assert state.hand_state == snapshot(
        HandState(
            player_bids={},
            player_hands={
                PlayerId("1"): [SuitedCard(id=CardId(49), rank="Q", suit="♣")],
                PlayerId("2"): [SuitedCard(id=CardId(50), rank="K", suit="♣")],
            },
            current_trick=[],
            finished_tricks=[
                (
                    PlayerId("2"),
                    [
                        (PlayerId("1"), SuitedCard(id=CardId(48), rank="J", suit="♣")),
                        (PlayerId("2"), SuitedCard(id=CardId(51), rank="A", suit="♣")),
                    ],
                )
            ],
            trump=None,
        )
    )


def test_play_card_requires_config_to_already_be_set():
    player_1 = make_player(1)
    card = SuitedCard(id=CardId(0), rank=2, suit="♠")
    state = GameState()

    with pytest.raises(AssertionError):
        apply_event(state, PlayCard(player_1.id, card.id))


def test_play_card_requires_hand_state_to_already_be_set():
    player_1 = make_player(1)
    state = GameState(config=GameConfig([player_1], jokers=0))

    with pytest.raises(AssertionError):
        apply_event(state, PlayCard(player_1.id, CardId(0)))


def test_play_card_raises_if_card_not_in_hand():
    player_1, player_2 = make_player(1), make_player(2)
    card1, card2 = Joker(CardId(1)), Joker(CardId(2))
    state = GameState(
        config=GameConfig([player_1], jokers=0),
        hand_state=HandState(
            player_bids={},
            player_hands={player_1.id: [card1], player_2.id: [card2]},
            current_trick=[],
            finished_tricks=[],
            trump=None,
        ),
    )

    with pytest.raises(AssertionError):
        apply_event(state, PlayCard(player_1.id, card2.id))


def test_play_card_finishes_hand_scores_it_and_advances_hand_index():
    player_1, player_2 = make_player(1), make_player(2)
    deck = build_deck(0)
    player2_card = deck.pop()
    lead_card = deck.pop()
    state = GameState(
        config=GameConfig([player_1, player_2], jokers=0),
        scores={player_1.id: 5, player_2.id: 5},
        hand_index=0,
        hand_state=HandState(
            player_bids={player_1.id: 1, player_2.id: 1},
            player_hands={player_1.id: [], player_2.id: [player2_card]},
            current_trick=[(player_1.id, lead_card)],
            finished_tricks=[],
            trump=None,
        ),
    )

    apply_event(state, PlayCard(player_2.id, player2_card.id))

    assert state == snapshot(
        GameState(
            config=GameConfig(
                players=[
                    Player(id=PlayerId("1"), name="Player 1"),
                    Player(id=PlayerId("2"), name="Player 2"),
                ],
                jokers=0,
            ),
            scores={PlayerId("1"): 5, PlayerId("2"): 16},
            hand_index=1,
        )
    )
