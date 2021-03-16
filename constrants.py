from enum import Enum, auto
from typing import Optional, List


class CallType(Enum):
    BID = auto()
    EXCHANGE = auto()
    TRUMP_CHANGE = auto()
    MISS_DEAL_CHECK = auto()
    FRIEND_CALL = auto()
    REDEAL = auto()
    PLAY = auto()
    GAME_OVER = auto()


class Card:

    @classmethod
    def str_to_card(cls, card_str: str):
        raise NotImplementedError

    @staticmethod
    def is_cardstr(card_str: str) -> bool:
        raise NotImplementedError


class Suit:

    @classmethod
    def str_to_suit(cls, suit_str: str):
        raise NotImplementedError

    @staticmethod
    def is_suitstr(suit_str: str) -> bool:
        raise NotImplementedError


class Play:
    pass


class FriendCall:

    def __init__(self, fctype: int, card: Optional[Card] = None):
        self.fctype = fctype
        self.card = card


class Perspective:
    pass


class Engine:

    def turn(self, game_id, cmd) -> int:
        pass

    def perspective(self, player_id: int) -> Perspective:
        raise NotImplementedError

    def get_next_call(self) -> CallType:
        raise NotImplementedError

    def get_legal_plays(self, player_id: int) -> List[Play]:
        raise NotImplementedError

    @property
    def next_player(self):
        raise NotImplementedError

    def bidding(self, bidder: int, trump: Suit, bid: int) -> int:
        """
        suit
        bid
        """
        raise NotImplementedError

    def exchange(self, player: int, discarding_cards: list) -> int:
        """
        Card List
        """
        raise NotImplementedError

    def trump_change(self, player: int, trump: Suit) -> int:
        """
        suit
        """
        raise NotImplementedError

    def miss_deal_check(self, player: int, miss_deal: bool) -> int:
        """
        miss_deal
        """
        raise NotImplementedError

    def friend_call(self, player: int, friend_call: FriendCall) -> int:
        """
        fctype
        card
        -> friend_call
        """
        raise NotImplementedError

    def play(self, play: Play) -> int:
        raise NotImplementedError
