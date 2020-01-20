
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
        self.id_to_room_and_number = dict()  # id를 room, number pair 로 바꾼다
        self.room_to_id = dict()
            # user_to_server와 AI_to_server

    def queue_user_game_start(self, user_id): #이거는 FE에서 game start queue 신호가 들어오면 다 넣는다
        """If there's no repeated id, append new id in id list"""
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
        """
        If more than five people waiting, return true and
                1) make room
                2) allocate number for each id
        If not, return false
        """
        if len(self.game_start_queue) >= 5:
            new_room = GR.Room()
            n = 0
            player_list = list()
            for _ in range(5):
                i_id = self.game_start_queue.pop(0)
                self.id_to_room_and_number[i_id] = (new_room, n) #이거 dictionary이다
                player_list.append(i_id)
                n += 1
            self.room_to_id[new_room] = player_list
            return True
        else:
            return False

    # turn_process는 어디서 실행시키는가? BE? GR?

    def turn_process(self, id_address, data_from_fe):
        room, player = self.id_to_room_and_number[id_address]
        room.user_turn(player, data_from_fe)
        # 이후 게임 로직 불러오는 함수

    #어찌됐든 room의 상태는 GR에서 가지고 있다

    #GR과 user는 서버에 어떻게 정보를 보낼까?

    def server_to_user(self, room_and_number, cmd):
        """Send cmd to user"""
        room, number = room_and_number
        GR.turn_process(self.room_to_id[room][number], cmd)

    def server_to_GR(self, user_id, cmd):
        """Send cmd to GR"""
        GR.turn_process(self.id_to_room_and_number[user_id], cmd)

    def user_to_server(self, cmd):
        user_id, turn, isReady = cmd
        if turn == 0 and isReady == True:
            self.queue_user_game_start(user_id)
        elif turn == 0 and isReady == False:
            self.cancel

