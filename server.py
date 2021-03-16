from typing import List, Deque, Dict
from collections import deque
import json

from protocol import Command
from queue import WaitingQueue
from room import Room


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
        self.room_dict.update({account_id: new_room for account_id in account_id_list})
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
