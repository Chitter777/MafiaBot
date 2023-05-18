import asyncio
import codecs
import json
import random
from typing import List

import disnake
from core import (
    Client,
    EnabledPlayerRoles,
    GenerateButtons,
    PlayerRole,
    PlayerRoleEmoji,
    PlayerRoleName,
    Utils,
    CycleTimer,
)
import ext.views as views
from disnake.ext import commands
from loguru import logger


class OnBttClick(commands.Cog):
    def __init__(self, bot):
        self.bot: Client = bot
        with codecs.open(
            "./files/jsons/cycle_description.json", "r", encoding="utf_8_sig"
        ) as f:
            self.cycle = json.loads(f.read())

    @staticmethod
    def get_key(d, value):
        for k, v in d.items():
            if v == value:
                return k
        return None

    @commands.Cog.listener("on_button_click")
    @logger.catch(reraise=True)
    async def on_btt_click(self, inter: disnake.MessageInteraction):
        icci = inter.component.custom_id
        if icci == "join_to_game":
            data: dict = json.loads(await self.bot.redis.get(str(inter.message.id)))
            if inter.author.id == data["game_admin"]:
                embed = disnake.Embed(
                    title="Завершение игры: предупреждение об отмене",
                    description="Вы уверены, что хотите отменить игру? Для отмены нажмите **Отменить игру**. В противном случае просто скройте это сообщение",
                    color=disnake.Color.red(),
                )
                return await inter.send(
                    embed=embed,
                    components=[
                        disnake.ui.Button(
                            label="Отменить игру",
                            style=disnake.ButtonStyle.red,
                            custom_id=f"cancel_game__{inter.message.id}",
                        )
                    ],
                    ephemeral=True,
                )
            elif inter.author.id in data.get("players", []):
                return await inter.send(
                    "Вы действительно хотите покинуть игру?",
                    ephemeral=True,
                    components=[
                        disnake.ui.Button(
                            label="Да",
                            emoji="✔️",
                            custom_id=f"leave_{inter.message.id}",
                            style=disnake.ButtonStyle.red,
                        )
                    ],
                )
            elif len(data.get("players", [])) < data["max_players"]:
                data["players"].append(inter.author.id)
                embed = inter.message.embeds[0]
                embed.remove_field(0)
                embed.insert_field_at(
                    0,
                    "Присоединилось:",
                    f"{len(data['players'])}/{data['max_players']}",
                )
                cmpnts = GenerateButtons.generate_lobby_buttons(
                    data["players"], data["max_players"], data["config"]
                )
                await inter.message.edit(embed=embed, components=cmpnts)
                await self.bot.redis.set(str(inter.message.id), json.dumps(data))
                await inter.send("Вы успешно присоединились к игре", ephemeral=True)
            elif len(data.get("players", [])) >= data["max_players"]:
                return await inter.send(
                    "🛑 В этой игре уже достаточно человек!", ephemeral=True
                )
        elif icci.startswith("leave_"):
            msg_id = int(inter.component.custom_id.replace("leave_", ""))
            await inter.response.defer()
            data = json.loads(await self.bot.redis.get(str(msg_id)))
            data["players"].remove(inter.author.id)
            msg = await inter.channel.fetch_message(msg_id)
            embed = msg.embeds[0]
            embed.remove_field(0)
            embed.insert_field_at(
                0, "Присоединилось:", f"{len(data['players'])}/{data['max_players']}"
            )
            cmpnts = GenerateButtons.generate_lobby_buttons(
                data["players"], data["max_players"], data["config"]["allowed_roles"]
            )
            await msg.edit(embed=embed, components=cmpnts)
            await inter.edit_original_response(
                "🚪 Вы успешно покинули игру", embeds=[], components=[]
            )
            await self.bot.redis.set(str(msg_id), json.dumps(data))
        elif icci.startswith("cancel_game__"):
            await inter.response.defer()
            msg_id = icci.replace("cancel_game__", "")
            data = json.loads(await self.bot.redis.get(msg_id))
            if data["game_admin"] == inter.author.id:
                msg = await inter.channel.fetch_message(int(msg_id))
                embed = disnake.Embed(
                    title="Запуск игры: игра отменена",
                    description="Игра была отменена создателем",
                    color=disnake.Color.dark_gray(),
                )
                await msg.edit(embed=embed, components=[])
                await inter.edit_original_response(
                    "Вы успешно отменили игру", embeds=[], components=[]
                )
                await self.bot.redis.delete(msg_id)
                return await msg.delete(delay=10)
        elif icci == "start_game":
            data: dict = json.loads(await self.bot.redis.get(str(inter.message.id)))
            if inter.author.id == data["game_admin"]:
                await inter.message.edit(
                    components=[
                        disnake.ui.Button(label="Создание ", disabled=True, emoji="⌛")
                    ]
                )
                playerlist: list = data["players"].copy()
                epl = EnabledPlayerRoles(data["config"]["allowed_roles"])
                data["cycle"] = 0
                data["isEnd"] = False
                max_mafia = Utils.calc_mafia(len(playerlist))
                players = {}
                o = {
                    inter.guild.default_role: disnake.PermissionOverwrite(
                        read_messages=False, send_messages=False
                    ),
                    inter.guild.me: disnake.PermissionOverwrite(
                        read_messages=True, send_messages=True, manage_channels=True
                    ),
                }
                mafia: List[disnake.Member] = []
                if EnabledPlayerRoles.SENIOR in epl:
                    p = playerlist.pop(random.randint(0, len(playerlist) - 1))
                    logger.debug(p)
                    players.update({p: PlayerRole.SENIOR.value})
                    o.update(
                        {
                            inter.guild.get_member(p): disnake.PermissionOverwrite(
                                read_messages=True, send_messages=True
                            )
                        }
                    )
                    max_mafia -= 1
                    mafia.append(inter.guild.get_member(p))
                for i in range(0, max_mafia):
                    p = playerlist.pop(random.randint(0, len(playerlist) - 1))
                    member = await inter.guild.get_or_fetch_member(p)
                    players.update({p: PlayerRole.MAFIA.value})
                    o.update(
                        {
                            member: disnake.PermissionOverwrite(
                                read_messages=True, send_messages=True
                            )
                        }
                    )
                    mafia.append(member)
                epl_list = list(EnabledPlayerRoles.__members__.keys())
                epl_list.remove(str(EnabledPlayerRoles.SENIOR.name))
                for epl_name in epl_list:
                    if EnabledPlayerRoles[epl_name] in epl:
                        players.update(
                            {
                                playerlist.pop(
                                    random.randint(0, len(playerlist) - 1)
                                ): PlayerRole[epl_name].value
                            }
                        )
                for member in playerlist:
                    players.update({member: PlayerRole.INNOCENT.value})
                del playerlist
                data["players"]: dict = players

                role = await inter.guild.create_role(
                    name="MAFIA-1337",
                    reason=f"Создание роли для доступа в канал({inter.author} | {inter.author.id})",
                )
                game_category = await inter.guild.create_category(
                    name="Мафия", reason="Игра в мафию"
                )
                perms = {
                    inter.guild.default_role: disnake.PermissionOverwrite(
                        read_messages=False, send_messages=False
                    ),
                    role: disnake.PermissionOverwrite(
                        read_messages=True, send_messages=False
                    ),
                }
                for member in players.keys():
                    member = await inter.guild.get_or_fetch_member(int(member))
                    await member.add_roles(
                        role, reason="Выдача роли доступа для игры в мафию"
                    )
                vote_channel = await game_category.create_text_channel(
                    name="голосование", resaon="", overwrites=perms
                )
                perms.update(
                    {
                        role: disnake.PermissionOverwrite(
                            read_messages=True, send_messages=True
                        )
                    }
                )
                square_channel = await game_category.create_text_channel(
                    name="площадь",
                    reason=f"Создание главной комнаты игры",
                    overwrites=perms,
                )
                mafia_channel = await game_category.create_text_channel(
                    name="мафия",
                    overwrites=o,
                    reason="Создание приватного канала для мафиози",
                )
                mafia_lore = self.cycle["start_mafia"].format(
                    self.cycle["start_mafia_with_senior"]
                    if EnabledPlayerRoles.SENIOR in epl
                    else ""
                )
                if EnabledPlayerRoles.MANIAC in epl:
                    mafia_lore += self.cycle["start_mafia_with_maniac"]
                embed = disnake.Embed(
                    title="Ночь 0", description=mafia_lore, colour=disnake.Color.red()
                )
                if EnabledPlayerRoles.MANIAC in epl:
                    embed.add_field(
                        name="Маньяк:",
                        value="<@"
                        + str(OnBttClick.get_key(players, PlayerRole.MANIAC.value))
                        + ">",
                    )
                await mafia_channel.send(
                    " ".join(
                        [
                            member.mention if member is not None else "None"
                            for member in mafia
                        ]
                    ),
                    embed=embed,
                )
                embed = disnake.Embed(
                    title="Ночь 0",
                    description=self.cycle["start_all"],
                    colour=disnake.Color.dark_blue(),
                )
                await vote_channel.send(
                    content=role.mention,
                    embed=embed,
                    components=[
                        disnake.ui.Button(
                            label="Узнать роль",
                            custom_id="check_role",
                            style=disnake.ButtonStyle.blurple,
                            emoji="🎭",
                        )
                    ],
                )
                data["game_channels"] = {
                    "category": game_category.id,
                    "vote": vote_channel.id,
                    "square": square_channel.id,
                    "mafia": mafia_channel.id,
                }
                data["game_role"] = role.id
                data["isEnd"] = False
                data.pop("max_players")
                await self.bot.redis.delete(str(inter.message.id))
                await self.bot.redis.set(str(game_category.id), json.dumps(data))

                msg = await vote_channel.send(
                    content="Подождите, идёт генерация выбора"
                )
                view = views.VoteSelectView(
                    redis_con=self.bot.redis,
                    timeout=15,
                )
                view.set_msg_view()
            else:
                return await inter.send("✋ Вы не создатель этой игры!", ephemeral=True)
        elif icci == "check_role":
            data: dict = json.loads(
                await self.bot.redis.get(str(inter.message.channel.category_id))
            )
            playerflag: PlayerRole = PlayerRole(data["players"][str(inter.author.id)])
            if PlayerRole.DEAD in playerflag:
                pl_rolename = PlayerRoleName.DEAD.value
                pl_emoji = PlayerRoleEmoji.DEAD.value
            elif PlayerRole.ARRESTED in playerflag:
                pl_rolename = PlayerRoleName.ARRESTED.value
                pl_emoji = PlayerRoleEmoji.ARRESTED.value
            else:
                pl_rolename = PlayerRoleName[str(playerflag.name)].value
                pl_emoji = PlayerRoleEmoji[str(playerflag.name)].value
            pl_response = "Ваша роль - " + pl_emoji + " " + pl_rolename
            await inter.send(pl_response, ephemeral=True)
        else:
            logger.critical(icci)


def setup(bot):
    bot.add_cog(OnBttClick(bot))
