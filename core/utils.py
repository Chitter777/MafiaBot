import asyncio
import json

import redis
from core import AllVoted, TimerType


class Between:
    """
    Нахождение числа в заданном промежутке чисел
    """

    def __init__(self, n1: int, n2: int):
        self.n1 = n1
        self.n2 = n2

    def __contains__(self, item: int) -> bool:
        if self.n1 <= item <= self.n2:
            return True
        else:
            return False


class Utils:
    @staticmethod
    def calc_mafia(pl_len: int) -> int:
        """
        Вычисление нужного количества мафии для игры, согласно количеству игроков
        :param pl_len:
        :return:
        """
        if pl_len in Between(3, 5):
            max_mafia = 1
        elif pl_len in Between(6, 9):
            max_mafia = 2
        elif pl_len in Between(10, 14):
            max_mafia = 3
        else:
            max_mafia = round(pl_len / 3)
        return max_mafia

    @staticmethod
    async def vote_timer(
        sec: int, msg_id: str, redis_con: redis.Redis, vtype: TimerType
    ):
        async with asyncio.timeout(sec):
            for i in range(sec):
                match vtype:
                    case TimerType.VOTE:
                        data = json.loads(await redis_con.get(msg_id))
                        if len(data["voted"]) == data["required_votes_count"]:
                            raise AllVoted("Все проголосовали")
                    case TimerType.WAITING:
                        pass
                await asyncio.sleep(1)
