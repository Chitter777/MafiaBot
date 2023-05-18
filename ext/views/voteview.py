import json

import disnake
import redis

from core import Utils, CycleTimer
from typing import Union
import itertools


class VoteSelect(disnake.ui.StringSelect):
    def __init__(self, redis_con: redis.Redis):
        super().__init__(custom_id="")
        self.redis_con: redis.Redis = redis_con

    async def callback(self, inter: disnake.MessageInteraction) -> None:
        await Utils.calc_game(
            self.bot.redis,
        )


class VoteSelectView(disnake.ui.View):
    def __init__(
        self,
        redis_con: redis.Redis,
        timeout: float,
        cycle_data: CycleTimer,
    ):
        super().__init__(timeout=timeout)
        self.redis_con: redis.Redis = redis_con
        self.message: Union[disnake.Message, disnake.InteractionMessage, None] = None
        self.cycle: Union[CycleTimer, itertools.cycle]

    def set_msg_view(self, msg: Union[disnake.Message, disnake.InteractionMessage]):
        self.message = msg
        self.add_item(VoteSelect(redis_con=self.redis_con))
        return self.message

    async def on_timeout(self) -> None:
        data = json.loads(
            await self.redis_con.get(str(self.message.channel.category_id))
        )
        vsw = VoteSelectView(
            redis_con=self.redis_con,
            timeout=120,
        )

        vsw.message = await self.message.edit(view=vsw)
