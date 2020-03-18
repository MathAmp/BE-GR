
"""Hello World!"""
import GRtmp as GR
from collections import deque

# 실행 queue를 하나 만들고
# 방을 만드는 동시에 dictionary로 각 id를 방, 사람으로 연결짓는다.


class Room:
    def __init__(self):
        self.state = list()

    def user_turn(self, number, data):
        self.state[number] = data


class Server:
    def __init__(self):
        self.task_queue = list()  # task(front에서 넘어온 일들)를 저장한다
        self.game_start_queue = deque()  # Game start를 신청한 사람들 모아둠
        self.id_to_room_and_number = dict()  # id를 room, number pair 로 바꾼다
        # room에 들어있는 id를 list로 출력. room -> id list.user_to_server와 AI_to_server
        self.room_to_ids = dict()

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
            new_room = GR.Room()
            n = 0
            player_list = list()
            for _ in range(5):
                i_id = self.game_start_queue.popleft()
                self.id_to_room_and_number[i_id] = (
                    new_room, n)  # 이거 dictionary이다
                player_list.append(i_id)
                n += 1
            self.room_to_ids[new_room] = player_list
            return True
        else:
            return False

    # turn_process는 어디서 실행시키는가? BE? GR?

    # 이후 게임 로직 불러오는 함수

    # 어찌됐든 room의 상태는 GR에서 가지고 있다

    # GR과 user는 서버에 어떻게 정보를 보낼까? 그냥 cmd로 퉁쳐 놓자

    def server_to_user(self, room_and_number, cmd):
        """Send cmd to user"""
        "게임이 시작됐다는 시그널, 대기 시그널 처리 완료(올리기, 취소하기)했다는 시그널, UI"
        room, number = room_and_number
        user_id = self.room_to_ids[room][number]
        Server.to_front_end(user_id, cmd)

    @staticmethod
    def to_front_end(user_id, cmd):
        pass

    def server_to_GR(self, user_id, cmd):
        """Send cmd to GR"""
        # 이거 내가 호출하지는 않고, user_to_server가 알아서 해줄거야. 나는 task_queue만 잘 처리하면 돼
        room, number = self.id_to_room_and_number[user_id]
        room.turn_process(number, cmd)  # 이거 리턴값을 어떻게 할까요?

    def user_to_server(self, cmd):
        "대기 시그널(올리기, 취소하기)"
        user_id, is_ready, cmd_rest = cmd
        if cmd_rest == 0 and is_ready:
            self.queue_user_game_start(user_id)
        elif cmd_rest == 0 and not is_ready:
            self.cancel_queue_user_game_start(user_id)
        else:
            self.server_to_GR(user_id, cmd_rest)

    def GR_to_server(self, cmd):
        "게임 종료 신호, AI차례인지, UI. 처음 두개가 내가 처리해야할것들"
        pass


if __name__ == '__main__':
    print("Hello World!")
    server1 = Server()
    while True:
        # 루프 만들기
