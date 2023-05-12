import json

import disnake
from core import EnabledPlayerRoles, GenerateButtons, PlayerRoleEmoji
from disnake.ext import commands


class StartGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="играть", description="Запустить игру")
    async def start_game(
        self,
        inter: disnake.AppCmdInter,
        max_players: int = commands.Param(
            name="кол-во_игроков",
            description="Максимальное количество игроков для этой игры",
            min_value=5,
            max_value=15,
        ),
    ):
        data = {
            "game_admin": inter.author.id,
            "max_players": max_players,
            "players": [inter.author.id],
            "config": {
                "allowed_roles": 3,
                "multiply_healing": False,
                "multiply_harlotting": False,
                "max_prevoting_time": (max_players * 20),
                "max_voting_time": (max_players * 10),
            },
        }
        embed = disnake.Embed(
            title="Запуск игры: ожидание игроков",
            description="> **Мафия** — салонная командная психологическая пошаговая ролевая игра с детективным сюжетом, моделирующая борьбу информированных друг о друге членов организованного меньшинства с неорганизованным большинством.\n> \n> Завязка сюжета: Жители города, обессилевшие от разгула мафии, выносят решение пересажать в тюрьму всех мафиози до единого. В ответ мафия объявляет войну до полного уничтожения всех порядочных горожан.\n\n\nНажмите на кнопку **Присоединиться**, чтобы вступить в игру.",
            color=disnake.Color.yellow(),
        )
        embed.add_field(name="Присоединилось:", value=f"1/{max_players}")
        v = " ".join(
            [PlayerRoleEmoji[i.name].value for i in list(EnabledPlayerRoles(3))]
        )
        embed.add_field(name="Доступные дополнительные роли:", value=v)
        cmps = GenerateButtons.generate_lobby_buttons(
            data["players"], data["max_players"], data["config"]
        )
        await inter.send(embed=embed, components=cmps)
        msg = await inter.original_response()
        data = json.dumps(data)
        await self.bot.redis.set(str(msg.id), data)


def setup(bot):
    bot.add_cog(StartGame(bot))
