"""Hello World!"""


# 실행 queue를 하나 만들고
# 방을 만드는 동시에 dictionary로 각 id를 방, 사람으로 연결짓는다.

class Room:
    def __init__(self):
        self.state = list()


    def user_turn(self, number, data):
        self.state[number] = data

class Server:
    def __init__(self):
        self.task_queue = list()  # task list를 저장한다
        self.game_start_queue = list()  #
        self.id_to_local_info = dict()

    def queue_user_game_start(self, user_id):
        """If there's no repeated id, append new id in id list"""
        if user_id in self.game_start_queue:
            return False
        else:
            self.game_start_queue.append(user_id)
            return True

    def room_allocation(self):
        """
        If more than five people waiting, return true and
                1) make room
                2) allocate number for each id
        If not, return false
        """
        if len(self.game_start_queue) >= 5:
            new_room = Room()
            n = 0;
            for _id in self.game_start_queue[0:5]:
                self.id_to_local_info[_id] = (new_room, n)
                n += 1
            return True
        else:
            return False

    def turn_process(self, id_address, data_from_fe):
        room, player = self.id_to_local_info[id_address]
        room.user_turn(player, data_from_fe)
        # 이후 게임 로직 불러오는 함수
