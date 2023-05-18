import disnake
import redis
import json
from core import Utils, CycleTimer, PlayerRole
from typing import Union
import itertools


class GameStartSelect(disnake.ui.UserSelect):
    def __init__(
        self,
        game_data: dict,
        msg: Union[disnake.Message, disnake.InteractionMessage],
        iter_move: itertools.cycle = None,
    ):
        self.msg: Union[disnake.Message, disnake.InteractionMessage] = msg
        if game_data["cycle"] == 0:
            placeholder = ""
            is_disabled = True
        elif game_data["cycle"] == 1:
            placeholder = ""
            is_disabled = True
        else:
            iter_res: CycleTimer = next(iter_move)
            if iter_res.value.increment_steps:
                game_data["cycle"] += 1
            placeholder = iter_res.value.name
            is_disabled = iter_res.value.disable_select
        self.game_data = game_data
        super().__init__(
            custom_id="select_member",
            max_values=1,
            min_values=1,
            placeholder=placeholder,
            disabled=is_disabled,
        )

    async def callback(self, inter: disnake.MessageInteraction) -> None:
        member_id = int(inter.values[0])
        if inter.author.id == member_id:
            return await inter.send("Вы не можете выбрать себя!", ephemeral=True)
        member = await inter.guild.get_or_fetch_member(member_id)
        if member.bot:
            return await inter.send("Вы не можете выбрать бота!", ephemeral=True)
        elif str(inter.author.id) not in self.game_data["players"].keys():
            return await inter.send("Вы не можете выбрать участника, который не участвует в игре!", ephemeral=True)
        member_flags = PlayerRole(self.game_data["players"].get(str(member_id), 0))
        if Utils.match_lists([PlayerRole.DEAD, PlayerRole.ARRESTED], list(member_flags)):
            return await inter.send("Вы уже не можете ", ephemeral=True)
        
        
class GameStartSelectView(disnake.ui.View):
    def __init__(self):
        super().__init__()
