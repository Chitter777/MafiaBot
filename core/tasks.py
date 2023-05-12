import asyncio
import json

from core import AllVoted, TimerType, Utils


class Tasks:
    @staticmethod
    async def game_loop_task(client, key: str, ttype: TimerType, vtype: TimerType):
        sec = json.loads(await client.redis.get(key))["config"][vtype.value]
        try:
            await Utils.vote_timer(
                redis_con=client.redis, sec=sec, msg_id=key, vtype=ttype
            )
        except asyncio.TimeoutError:
            return "Время истекло"
        except AllVoted:
            "Все проголосовали"
