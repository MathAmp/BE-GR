from typing import List
from collections import deque


class WaitingQueue(deque):

    def __init__(self):
        super().__init__()

    def is_able_to_start(self, num: int) -> bool:
        return len(self) >= num

    def wait(self, account_id: int) -> bool:
        if account_id not in self:
            self.append(account_id)
            return True
        else:
            return False

    def pop_players(self, num: int) -> List[int]:
        if self.is_able_to_start(num):
            return [self.popleft() for _ in range(num)]
        else:
            return list()

    def cancel_wait(self, player_id: int) -> bool:
        try:
            self.remove(player_id)
            return True
        except ValueError:
            return False
