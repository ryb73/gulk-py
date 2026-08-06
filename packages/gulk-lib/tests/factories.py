from gulk_lib.cards import Card, CardId
from gulk_lib.events import Bid, Deal, PlayCard
from gulk_lib.game_config import Player
from gulk_lib.player_id import PlayerId


def make_player(player_id: int) -> Player:
    return Player(PlayerId(str(player_id)), f"Player {player_id}")


def make_deal(
    shuffled_deck: list[Card],
    dealer_id: int,
    cards_per_player: int,
    *,
    deal_trump: bool,
) -> Deal:
    return Deal(shuffled_deck, PlayerId(str(dealer_id)), cards_per_player, deal_trump)


def make_bid(player_id: int, num_tricks: int) -> Bid:
    return Bid(PlayerId(str(player_id)), num_tricks)


def make_play_card(player_id: int, card_id: int) -> PlayCard:
    return PlayCard(PlayerId(str(player_id)), CardId(card_id))
