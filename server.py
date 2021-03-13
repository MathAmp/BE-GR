from typing import List, Deque, Dict, AnyStr, Tuple, Union
from collections import deque, namedtuple
from enum import auto, Enum
import json

from queue import WaitingQueue


Command = AnyStr
SendScheme = namedtuple("SendScheme", ['to', 'cmd'])
RoomProcessResult = namedtuple("RoomProcessResult", ['call_type', 'retval'])


class CallType(Enum):
    BID = auto()
    EXCHANGE = auto()
    TRUMP_CHANGE = auto()
    MISS_DEAL_CHECK = auto()
    FRIEND_CALL = auto()
    REDEAL = auto()
    PLAY = auto()
    GAME_OVER = auto()


class Perspective:
    pass


class Engine:

    def turn(self, game_id, cmd) -> int:
        pass

    def perspective(self, player_id: int) -> Perspective:
        return Perspective()

    def get_next_call(self) -> CallType:
        return CallType.FRIEND_CALL

    def bidding(self, bidder: int, trump: int, bid: int) -> int:
        """
        suit
        bid
        """
        raise NotImplementedError

    def exchange(self, discarding_cards: list) -> int:
        """
        Card List
        """
        raise NotImplementedError

    def trump_change(self, trump: int) -> int:
        """
        suit
        """
        raise NotImplementedError

    def miss_deal_check(self, player: int, miss_deal: bool) -> int:
        """
        miss_deal
        """
        raise NotImplementedError

    def friend_call(self, friend_call: int) -> int:
        """
        fctype
        card
        -> friend_call
        """
        raise NotImplementedError

    def play(self, play: int) -> int:
        raise NotImplementedError


class Room:

    regular_personnel = 5

    def __init__(self, account_id_list: List[int]):
        self.state = list()
        self.account_id_tuple: Tuple[int] = tuple(account_id_list)
        self.game_engine = Engine()

    def process(self, account_id: int, data: dict) -> Union[RoomProcessResult, None]:
        player_id = self._account_id_to_player_id(account_id)
        if player_id is not None:
            return self._process_game(player_id, data)

    def _process_game(self, player_id: int, data: dict) -> Union[RoomProcessResult, None]:
        current_call_type = self.game_engine.get_next_call()
        if current_call_type == CallType.BID:
            self._bidding(self.game_engine, player_id, data)
        elif current_call_type == CallType.EXCHANGE:
            self._exchange(self.game_engine, data)
        elif current_call_type == CallType.TRUMP_CHANGE:
            self._trump_change(self.game_engine, data)
        elif current_call_type == CallType.MISS_DEAL_CHECK:
            self._miss_deal_check(self.game_engine, data)
        elif current_call_type == CallType.FRIEND_CALL:
            self._friend_call(self.game_engine, data)
        elif current_call_type == CallType.PLAY:
            self._play(self.game_engine, data)
        else:
            return None

    @staticmethod
    def _bidding(engine: Engine, player_id: int, data: dict) -> Union[RoomProcessResult, None]:
        if 'suit' in data and 'bid' in data:
            return_value = engine.bidding(player_id, )
            return RoomProcessResult(CallType.BID, return_value)

    @staticmethod
    def _exchange(engine: Engine, data: dict) -> RoomProcessResult:
        if 'card_list' in data:
            card_list = []
            return_value = engine.exchange()
            pass

    @staticmethod
    def _trump_change(engine: Engine, data: dict) -> RoomProcessResult:
        pass

    @staticmethod
    def _miss_deal_check(engine: Engine, data: dict) -> RoomProcessResult:
        pass

    @staticmethod
    def _friend_call(engine: Engine, data: dict) -> RoomProcessResult:
        raise NotImplementedError

    @staticmethod
    def _play(engine: Engine, data: dict) -> Union[RoomProcessResult, None]:
        raise NotImplementedError

    def _player_id_to_account_id(self, player_id: int) -> Union[int, None]:
        if 0 <= player_id <= len(self.account_id_tuple):
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
    def front_end_to_back_end(cls):
        raise NotImplementedError

    @classmethod
    def back_end_to_front_end(cls, player_id: int, cmd: Command):
        raise NotImplementedError


if __name__ == '__main__':
    server = Server()
    server.run()
