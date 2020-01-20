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
        self.game_start_queue = list()  # Game start한다
        self.id_to_local_info = dict()
            # user_to_server와 AI_to_server

    def queue_user_game_start(self, user_id): #이거는 FE에서 game start queue 신호가 들어오면 다 넣는다
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

            new_room = GR.Room()
            n = 0
            for i_id in self.game_start_queue[0:5]:
                self.id_to_local_info[i_id] = (new_room, n) #이거 dictionary이다
                self.local_info_to_id
                n += 1
            return True
        else:
            return False

    # turn_process는 어디서 실행시키는가? BE? GR?

    def turn_process(self, id_address, data_from_fe):
        room, player = self.id_to_local_info[id_address]
        room.user_turn(player, data_from_fe)
        # 이후 게임 로직 불러오는 함수

    #어찌됐든 room의 상태는 GR에서 가지고 있다

    def server_to_user(self, user_id, cmd):
        """Send cmd to user"""
        GR.turn_process(user.id, cmd)

    def server_to_GR(self, user_id, cmd):
        """Send cmd to GR"""
        GR.turn_process(user.id, cmd)

    def