from collections import namedtuple
from enum import Enum, auto, IntEnum
from typing import AnyStr

Command = AnyStr
SendScheme = namedtuple("SendScheme", ['to', 'cmd'])
ProcessResult = namedtuple("RoomProcessResult", ['call_type', 'retval'])


class ErrorCode(Enum):

    NO_PLAYER_IN_ROOM = auto()
    INVALID_DATA = auto()
    INDEX_OUT_OF_RANGE = auto()
    INVALID_PLAYER_TURN = auto()


class DataKey(IntEnum):
    bid = 0
    suit = auto()
    card = auto()
    card_list = auto()
    miss_deal = auto()
    friend_call_type = auto()
    play_idx = auto()
