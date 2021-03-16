from typing import Union, List, Tuple, Type

from protocol import ProcessResult, ErrorCode, DataKey
from constrants import CallType, Card, Suit, Play, FriendCall, Perspective, Engine


class InvalidCallTypeError(Exception):

    def __init__(self, call_type):
        super().__init__(f"Invalid call type : {call_type}")


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
    def _is_valid_player_id(player_id: int, total_id_cnt: int) -> bool:
        return 0 <= player_id < total_id_cnt

    def _player_id_to_account_id(self, player_id: int) -> Union[int, None]:
        if self._is_valid_player_id(player_id, len(self.account_id_tuple)):
            return self.account_id_tuple[player_id]

    def _account_id_to_player_id(self, account_id: int) -> Union[int, None]:
        if account_id in self.account_id_tuple:
            return self.account_id_tuple.index(account_id)

    def get_perspective(self, account_id: int) -> Union[Perspective, None]:
        player_id = self._account_id_to_player_id(account_id)
        if player_id:
            return self.game_engine.perspective(player_id)
