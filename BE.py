from typing import List, Deque, Dict
from collections import deque

import GRtmp as GR
from queue import WaitingQueue


# 실행 queue를 하나 만들고
# 방을 만드는 동시에 dictionary로 각 id를 방, 사람으로 연결짓는다.


class Player:

    def __init__(self, player_id: int):
        self.player_id: int = player_id


class Room:

    regular_personnel = 5

    def __init__(self, player_id_list: List[int]):
        self.state = list()
        self.player_id_list: List[int] = player_id_list
        self.player_sequence_dict = dict()

    def user_turn(self, number, data):
        self.state[number] = data


class MyServer:

    def __init__(self):
        self.task_queue: Deque = deque()
        self.waiting_queue: WaitingQueue = WaitingQueue()
        self.room_dict: Dict[int, Room] = dict()

    def enqueue_task(self) -> bool:
        cmd = self.front_end_to_back_end()
        self.task_queue.append(cmd)
        return True

    def enqueue_waiting(self, player_id: int) -> bool:
        if player_id not in self.room_dict:
            return self.waiting_queue.wait(player_id)
        else:
            return False

    def cancel_waiting(self, player_id: int) -> bool:
        return self.waiting_queue.cancel_wait(player_id)

    def init_room(self) -> List[Room]:
        """
        Create rooms as many as possible
        """
        init_room_list = list()
        while True:
            player_id_list = self.waiting_queue.pop_players(Room.regular_personnel)
            if player_id_list:
                init_room_list.append(self.create_room(player_id_list))
            else:
                break
        return init_room_list

    def create_room(self, player_id_list: List[int]) -> Room:
        """
        Create Single room
        """
        new_room = Room(player_id_list)
        self.room_dict.update({player_id: new_room for player_id in player_id_list})
        return new_room

    @classmethod
    def front_end_to_back_end(cls):
        raise NotImplementedError

    @classmethod
    def back_end_to_front_end(cls):
        raise NotImplementedError


class Server:

    def __init__(self):
        self.task_queue = list()  # task(front에서 넘어온 일들)를 저장한다
        self.game_start_queue: Deque = deque()  # Game start를 신청한 사람들 모아둠
        self.id_to_room_and_number = dict()  # id를 room, number pair 로 바꾼다
        # room에 들어있는 id를 list로 출력. room -> id list.user_to_server와 AI_to_server
        self.room_to_ids = dict()
        self.room_to_user_num = dict()

    def task_queue_maker(self):
        # ! Loop 만들기
        cmd = Server.from_front_end()
        self.task_queue.append(cmd)

    # 이거는 FE에서 game start queue 신호가 들어오면 다 넣는다
    def queue_user_game_start(self, user_id):
        """If id is not repeated, append new id in id list"""
        if user_id in self.game_start_queue:
            return False
        else:
            self.game_start_queue.append(user_id)
            return True

    def cancel_queue_user_game_start(self, user_id):
        if user_id in self.game_start_queue:
            self.game_start_queue.remove(user_id)
            return True
        else:
            return False

    def room_allocation(self):
        """If more than five people waiting, return true and
                1) make room
                2) allocate number for each id
        If not, return false
        """
        while len(self.game_start_queue) >= 5:
            self.room_generate(5)
            return True
        else:
            return False

    def room_generate(self, user_num):
        new_room = GR.Room()
        player_list = list()
        for n in range(user_num):
            i_id = self.game_start_queue.popleft()
            self.id_to_room_and_number[i_id] = (new_room, n)
            player_list.append(i_id)
        self.room_to_ids[new_room] = player_list
        self.room_to_user_num[new_room] = user_num

    # turn_process는 어디서 실행시키는가? BE? GR?

    # 이후 게임 로직 불러오는 함수

    # 어찌됐든 room의 상태는 GR에서 가지고 있다

    # GR과 user는 서버에 어떻게 정보를 보낼까? 그냥 cmd로 퉁쳐 놓자

    def server_to_user(self, room_and_number, cmd):
        """Send cmd to user"""
        "게임이 시작됐다는 시그널, 대기 시그널 처리 완료(올리기, 취소하기)했다는 시그널, UI"
        room, number = room_and_number
        for ids in self.room_to_ids[room]:
            Server.to_front_end(ids, cmd)

    @staticmethod
    def to_front_end(user_id, cmd):
        raise NotImplementedError

    @staticmethod
    def from_front_end():
        raise NotImplementedError

    def server_to_GR(self, user_id, cmd):
        """Send cmd to GR"""
        # 이거 내가 호출하지는 않고, user_to_server가 알아서 해줄거야. 나는 task_queue만 잘 처리하면 돼
        room, number = self.id_to_room_and_number[user_id]
        is_game_over, ui_info = room.turn_process(number, cmd)
        # 이거 리턴값을 어떻게 할까요?

        # ret_value는 게임종료, AI차례, UI 차례대로.

        if is_game_over:
            for player in self.room_to_ids[room]:
                self.server_to_user((room, player), "GameOver")
            return

        player_index = self.room_to_ids[room].index(user_id)
        if player_index >= self.room_to_user_num[room]:
            # ! AI call
            raise NotImplementedError

        self.server_to_user((room, player), ui_info)

    def user_to_server(self, cmd):
        "대기 시그널(올리기, 취소하기)"
        user_id, is_ready, cmd_rest = cmd
        if cmd_rest == 0 and is_ready:
            self.queue_user_game_start(user_id)
        elif cmd_rest == 0 and not is_ready:
            self.cancel_queue_user_game_start(user_id)
        else:
            self.server_to_GR(user_id, cmd_rest)

    def one_task_processing(self, cmd):
        self.user_to_server(cmd)


if __name__ == '__main__':
    print("Hello World!")
    server1 = Server()
    while True:
        # 루프 만들기
        server1.task_queue_maker()
        for task in server1.task_queue:
            server1.one_task_processing(task)
        server1.room_allocation()
