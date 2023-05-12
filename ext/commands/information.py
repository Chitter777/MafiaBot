import json

import disnake
from core import PlayerRoleEmoji, PlayerRoleName
from disnake.ext import commands


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        f = open("./files/jsons/role_descriptions.json", encoding="utf-8")
        self.role_descr = json.load(f)
        f.close()

    @commands.slash_command(name="информация")
    async def info(self, inter):
        ...

    @info.sub_command(name="роли", description="Узнать информацию об игровых ролях")
    async def start_game(
        self,
        inter,
        role=commands.Param(
            name="роль",
            description="Укажите название игровой роли, о которой Вы хотите узнать",
            choices=[
                PlayerRoleName[rname].value for rname in PlayerRoleName.__members__
            ],
        ),
    ):
        n = PlayerRoleName.get_key(role)
        embed = disnake.Embed(
            title=PlayerRoleEmoji[n].value + " " + role,
            description=self.role_descr[n],
            colour=disnake.Color.blue(),
        )
        await inter.send(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Information(bot))
