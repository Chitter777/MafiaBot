import json

import disnake
from core import Client, EnabledPlayerRoles, GenerateButtons, PlayerRoleEmoji
from disnake.ext import commands
from loguru import logger


class OnDropdown(commands.Cog):
    def __init__(self, bot):
        self.bot: Client = bot

    @staticmethod
    def __is_bool(data) -> str:
        if isinstance(data, bool):
            if data:
                return "да"
            else:
                return "нет"

    @commands.Cog.listener("on_dropdown")
    @logger.catch(reraise=True)
    async def on_drpdwn(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "sets":
            data = json.loads(await self.bot.redis.get(str(inter.message.id)))
            if data is None:
                return await inter.send(
                    "Упс, данные потеряны. Возможно, игроки собирались слишком долго",
                    ephemeral=True,
                )
            elif data["game_admin"] != inter.author.id:
                return await inter.send("✋ Вы не создатель этой игры!", ephemeral=True)
            match inter.values[0]:
                case "allowed_roles":
                    cmpnts = GenerateButtons.generate_role_select(
                        data["config"]["allowed_roles"], inter.message.id
                    )
                    embed = disnake.Embed(
                        description="TEST", colour=disnake.Color.blurple()
                    )
                    await inter.send(embed=embed, components=cmpnts, ephemeral=True)
                case "max_mafia":
                    return await inter.response.send_modal(
                        title="Изменить максимальное количество мафии",
                        components=[
                            disnake.ui.TextInput(
                                label="Максимальное количество мафии в игре",
                                custom_id="max_mafia",
                                style=disnake.TextInputStyle.short,
                                placeholder="Введите количество мафии",
                                value=str(data["config"]["max_mafia"]),
                                max_length=1,
                                min_length=1,
                            )
                        ],
                        custom_id="max_mafia",
                    )
                case "multiply_healing":
                    data["config"]["multiply_healing"] = not data["config"][
                        "multiply_healing"
                    ]
                    d = data["config"]["multiply_healing"]
                    cmpnts = GenerateButtons.generate_lobby_buttons(
                        members=data["players"],
                        max_members=data["max_players"],
                        config=data["config"],
                    )
                    await inter.message.edit(components=cmpnts)
                    await inter.send(
                        f"Успешно изменено значение на `{OnDropdown.__is_bool(d)}`",
                        ephemeral=True,
                    )
                    return await self.bot.redis.set(
                        str(inter.message.id), json.dumps(data)
                    )
                case "multiply_harlotting":
                    data["config"]["multiply_harlotting"] = not data["config"][
                        "multiply_harlotting"
                    ]
                    d = data["config"]["multiply_harlotting"]
                    cmpnts = GenerateButtons.generate_lobby_buttons(
                        members=data["players"],
                        max_members=data["max_players"],
                        config=data["config"],
                    )
                    await inter.message.edit(components=cmpnts)
                    await inter.send(
                        f"Успешно изменено значение на `{OnDropdown.__is_bool(d)}`",
                        ephemeral=True,
                    )
                    return await self.bot.redis.set(
                        str(inter.message.id), json.dumps(data)
                    )
                case "max_prevoting_time":
                    return await inter.response.send_modal(
                        title="Изменить максимальное время для обсуждения",
                        components=[
                            disnake.ui.TextInput(
                                label="Максимальное время обсуждения",
                                custom_id="max_prevoting_time",
                                style=disnake.TextInputStyle.long,
                                placeholder="Введите время в секундах. Допускаются только цифры с основанием 10",
                                value=str(data["config"]["max_prevoting_time"]),
                                max_length=4,
                                min_length=1,
                            )
                        ],
                        custom_id="max_prevoting_time",
                    )
                case "max_voting_time":
                    return await inter.response.send_modal(
                        title="Изменить максимальное время для голосования",
                        components=[
                            disnake.ui.TextInput(
                                label="Максимальное время голосования",
                                custom_id="max_voting_time",
                                style=disnake.TextInputStyle.long,
                                placeholder="Введите время в секундах. Допускаются только цифры с основанием 10",
                                value=str(data["config"]["max_voting_time"]),
                                max_length=4,
                                min_length=1,
                            )
                        ],
                        custom_id="max_voting_time",
                    )
                case _:
                    logger.critical("Вот тут собака зарыта!")
        elif inter.component.custom_id.startswith("change_allowed_roles__"):
            msg_id = int(
                inter.component.custom_id.replace("change_allowed_roles__", "")
            )
            data = json.loads(await self.bot.redis.get(str(msg_id)))
            if data is None:
                return await inter.send(
                    "Упс, данные потеряны. Возможно, игроки собирались слишком долго",
                    ephemeral=True,
                )
            elif data["game_admin"] == inter.author.id:
                await inter.response.defer()
                allowed_roles = 0
                vals = inter.values if inter.values is not None else []
                for choice in vals:
                    c = EnabledPlayerRoles.__getattr__(choice.upper())
                    allowed_roles = allowed_roles + c
                data["config"].update({"allowed_roles": allowed_roles})
                cmpns = GenerateButtons.generate_role_select(
                    data["config"]["allowed_roles"], msg_id
                )
                v = " ".join(
                    [
                        PlayerRoleEmoji.__getattr__(i.name).value
                        for i in list(
                            EnabledPlayerRoles(data["config"]["allowed_roles"])
                        )
                    ]
                )
                msg: disnake.Message = await inter.channel.fetch_message(msg_id)
                embed = msg.embeds[0]
                embed.remove_field(1)
                embed.add_field(name="Доступные дополнительные роли:", value=v)
                await msg.edit(embed=embed)
                await inter.edit_original_response(components=cmpns)
                await self.bot.redis.set(str(msg_id), json.dumps(data))
                return await inter.send(
                    "Вы успешно добавили игровые роли в настройки игровой сессии",
                    ephemeral=True,
                )
        elif inter.component.custom_id.startswith("_choice"):
            pass
        else:
            logger.critical(inter.component.custom_id)


def setup(bot):
    bot.add_cog(OnDropdown(bot))
