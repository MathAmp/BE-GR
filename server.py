from typing import List, Deque, Dict, AnyStr, Tuple, Union, Optional, Type
from collections import deque, namedtuple
from enum import auto, Enum, IntEnum
import json

from queue import WaitingQueue


Command = AnyStr
SendScheme = namedtuple("SendScheme", ['to', 'cmd'])
ProcessResult = namedtuple("RoomProcessResult", ['call_type', 'retval'])


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
        pass

    @staticmethod
    def is_cardstr(card_str: str) -> bool:
        pass


class Suit:

    @classmethod
    def str_to_suit(cls, suit_str: str):
        pass

    @staticmethod
    def is_suitstr(suit_str: str) -> bool:
        pass


class Play:
    pass


class FriendCall:

    def __init__(self, fctype: int, card: Optional[Card] = None):
        pass

class Perspective:
    pass


class Engine:

    def turn(self, game_id, cmd) -> int:
        pass

    def perspective(self, player_id: int) -> Perspective:
        return Perspective()

    def get_next_call(self) -> CallType:
        return CallType.FRIEND_CALL

    def get_legal_plays(self, player_id: int) -> List[Play]:
        pass

    @property
    def next_player(self):
        return int()

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


class InvalidCallTypeError(Exception):

    def __init__(self, call_type):
        super().__init__(f"Invalid call type : {call_type}")


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


class Room:

    regular_personnel = 5
    ProcessReturnType = Union[ProcessResult, ErrorCode]

    def __init__(self, account_id_list: List[int]):
        self.state = list()
        self.account_id_tuple: Tuple[int] = tuple(account_id_list)
        self.game_engine = Engine()

    def process(self, account_id: int, data: dict) -> ProcessReturnType:
        player_id = self._account_id_to_player_id(account_id)
        if player_id is not None:
            return self._process_game(player_id, data)
        else:
            return ErrorCode.NO_PLAYER_IN_ROOM

    def _process_game(self, player_id: int, data: dict) -> ProcessReturnType:
        current_call_type = self.game_engine.get_next_call()
        if current_call_type == CallType.BID:
            return self._bidding(self.game_engine, player_id, data)
        elif current_call_type == CallType.EXCHANGE:
            return self._exchange(self.game_engine, player_id, data)
        elif current_call_type == CallType.TRUMP_CHANGE:
            return self._trump_change(self.game_engine, player_id, data)
        elif current_call_type == CallType.MISS_DEAL_CHECK:
            return self._miss_deal_check(self.game_engine, player_id, data)
        elif current_call_type == CallType.FRIEND_CALL:
            return self._friend_call(self.game_engine, player_id, data)
        elif current_call_type == CallType.PLAY:
            return self._play(player_id, data)
        else:
            raise InvalidCallTypeError(current_call_type)

    @classmethod
    def _bidding(cls, engine: Engine, player_id: int, data: dict) -> ProcessReturnType:
        if cls._is_valid_data(DataKey.bid, data, int) and \
                cls._is_valid_data(DataKey.suit, data, str) and Suit.is_suitstr(data[DataKey.suit]):
            trump: Suit = Suit.str_to_suit(data[DataKey.suit])
            bid: int = data[DataKey.bid]
            return_value = engine.bidding(player_id, trump, bid)
            return ProcessResult(CallType.BID, return_value)
        else:
            return ErrorCode.INVALID_DATA

    @classmethod
    def _exchange(cls, engine: Engine, player_id: int, data: dict) -> ProcessReturnType:
        if cls._is_valid_data(DataKey.card_list, data, list) and \
                all(Card.is_cardstr(card) for card in data[DataKey.card_list]):
            card_list: List[Card] = [Card.str_to_card(card) for card in data[DataKey.card_list]]
            return_value = engine.exchange(player_id, card_list)
            return ProcessResult(CallType.EXCHANGE, return_value)
        else:
            return ErrorCode.INVALID_DATA

    @classmethod
    def _trump_change(cls, engine: Engine, player_id: int, data: dict) -> ProcessReturnType:
        if cls._is_valid_data(DataKey.suit, data, str) and Suit.is_suitstr(data[DataKey.suit]):
            trump = Suit.str_to_suit(data[DataKey.suit])
            return_value = engine.trump_change(player_id, trump)
            return ProcessResult(CallType.TRUMP_CHANGE, return_value)
        else:
            return ErrorCode.INVALID_DATA

    @classmethod
    def _miss_deal_check(cls, engine: Engine, player_id: int, data: dict) -> ProcessReturnType:
        if cls._is_valid_data(DataKey.miss_deal, data, bool):
            miss_deal = data[DataKey.miss_deal]
            return_value = engine.miss_deal_check(player_id, miss_deal)
            return ProcessResult(CallType.MISS_DEAL_CHECK, return_value)
        else:
            return ErrorCode.INVALID_DATA

    @classmethod
    def _friend_call(cls, engine: Engine, player_id: int, data: dict) -> ProcessReturnType:
        if cls._is_valid_data(DataKey.friend_call_type, data, int) and \
                cls._is_valid_data(DataKey.card, data, str) and Card.is_cardstr(data[DataKey.card]):
            friend_call_type = data[DataKey.friend_call_type]
            card = Card.str_to_card(data[DataKey.card])

            # Make friend call and execute
            friend_call = FriendCall(friend_call_type, card)
            return_value = engine.friend_call(player_id, friend_call)
            return ProcessResult(CallType.FRIEND_CALL, return_value)
        else:
            return ErrorCode.INVALID_DATA

    @classmethod
    def _play(cls, engine: Engine, player_id: int, data: dict) -> ProcessReturnType:
        if engine.next_player == player_id:
            play_list: List[Play] = engine.get_legal_plays(player_id)
            if cls._is_valid_data(DataKey.play_idx, data, int):
                play_idx = data[DataKey.play_idx]
                if 0 <= play_idx < len(play_list):
                    play = play_list[play_idx]
                    return_value = engine.play(play)
                    return ProcessResult(CallType.PLAY, return_value)
                else:
                    return ErrorCode.INDEX_OUT_OF_RANGE
            else:
                return ErrorCode.INVALID_DATA
        else:
            return ErrorCode.INVALID_PLAYER_TURN

    @staticmethod
    def _is_valid_data(key: int, data: dict, key_type: Type):
        return key in data and type(data[key]) is key_type

    @staticmethod
    def is_valid_player_id(player_id: int, total_id_cnt: int) -> bool:
        return 0 <= player_id < total_id_cnt

    def _player_id_to_account_id(self, player_id: int) -> Union[int, None]:
        if self.is_valid_player_id(player_id, len(self.account_id_tuple)):
            return self.account_id_tuple[player_id]

    def _account_id_to_player_id(self, account_id: int) -> Union[int, None]:
        if account_id in self.account_id_tuple:
            return self.account_id_tuple.index(account_id)

    def get_perspective(self, account_id: int) -> Union[Perspective, None]:
        player_id = self._account_id_to_player_id(account_id)
        if player_id:
            return self.game_engine.perspective(player_id)


class Server:

    def __init__(self):
        self.task_queue: Deque = deque()
        self.waiting_queue: WaitingQueue = WaitingQueue()
        self.room_dict: Dict[int, Room] = dict()

    @staticmethod
    def decode(cmd: Command) -> dict:
        return json.loads(cmd)

    @staticmethod
    def encode(data) -> str:
        return json.dumps(data)

    def run(self):
        pass

    def broadcast_all(self, cmd: Command) -> bool:
        return self.broadcast(list(self.room_dict.keys()), cmd)

    def broadcast(self, account_id_list: List[int], cmd: Command) -> bool:
        return all(self.send(player_id, cmd) for player_id in account_id_list)

    def send(self, account_id: int, cmd: Command) -> bool:
        return self.back_end_to_front_end(account_id, cmd)

    def enqueue_task(self) -> bool:
        cmd = self.front_end_to_back_end()
        self.task_queue.append(cmd)
        return True

    def dequeue_task(self) -> str:
        return self.task_queue.popleft()

    def enqueue_waiting(self, account_id: int) -> bool:
        if account_id not in self.room_dict:
            return self.waiting_queue.wait(account_id)
        else:
            return False

    def cancel_waiting(self, account_id: int) -> bool:
        return self.waiting_queue.cancel_wait(account_id)

    def init_room(self) -> List[Room]:
        """
        Create rooms as many as possible
        """
        init_room_list = list()
        while True:
            account_id_list = self.waiting_queue.pop_players(Room.regular_personnel)
            if account_id_list:
                init_room_list.append(self.create_room(account_id_list))
            else:
                break
        return init_room_list

    def create_room(self, account_id_list: List[int]) -> Room:
        """
        Create Single room and update id_to_room dictionary
        """
        new_room = Room(account_id_list)
        self.room_dict.update({player_id: new_room for player_id in account_id_list})
        return new_room

    @classmethod
    def front_end_to_back_end(cls) -> str:
        raise NotImplementedError

    @classmethod
    def back_end_to_front_end(cls, player_id: int, cmd: Command) -> bool:
        raise NotImplementedError


if __name__ == '__main__':
    server = Server()
    server.run()
