from typing import Any, List, Union

import disnake
from core import ChoiceType, EnabledPlayerRoles, PlayerRole, PlayerRoleName
from loguru import logger


class GenerateButtons:
    ROLES = {
        PlayerRoleName.DETECTIVE: ["детектива", "🔎"],
        PlayerRoleName.MEDIC: ["медика", "🩺"],
        PlayerRoleName.HARLOT: ["путану", "👠"],
        PlayerRoleName.MANIAC: ["маньяка", "🔪"],
        PlayerRoleName.SENIOR: ["Дона мафии", "🚬"],
    }
    SETS_NAME = {
        "allowed_roles": {
            "label": "Активные роли",
            "descr": "Настроить наличие активных ролей игры",
            "emoji": "👥",
        },
        # "max_mafia": {
        #     "label": "Максимальное количество мафиози в игре",
        #     "descr": "Значение: {0}",
        #     "emoji": "🎩",
        # },
        "multiply_healing": {
            "label": "Доктор может лечить одного игрока подряд",
            "descr": "Значение: {0}",
            "emoji": "❤️‍🩹",
        },
        "multiply_harlotting": {
            "label": "Путана может заглядывать к одному игроку подряд",
            "descr": "Значение: {0}",
            "emoji": "👠",
        },
        "max_prevoting_time": {
            "label": "Максимальное время для обсуждения",
            "descr": "Значение: {0}",
            "emoji": "⏳",
        },
        "max_voting_time": {
            "label": "Максимальное время для голосования",
            "descr": "Значение: {0}",
            "emoji": "⌛",
        },
    }

    @staticmethod
    @logger.catch
    def generate_lobby_buttons(members: List[int], max_members: int, config: dict):
        def __is_bool(data) -> Union[Any, str]:
            if isinstance(data, bool):
                if data:
                    return "да"
                else:
                    return "нет"
            else:
                return data

        components = []
        select = []
        lmembs = len(members)

        if lmembs >= max_members:
            btt_name = "Мест нет!"
            btt_emj = "📛"
            btt_style = disnake.ButtonStyle.gray
        else:
            btt_name = "Присоединиться"
            btt_emj = "➕"
            btt_style = disnake.ButtonStyle.blurple
        components.append(
            disnake.ui.Button(
                label=btt_name,
                emoji=btt_emj,
                style=btt_style,
                custom_id="join_to_game",
                row=0,
            )
        )

        if lmembs >= 4:
            dis = False
        else:
            dis = True
        components.append(
            disnake.ui.Button(
                label="Начать игру",
                emoji="▶️",
                style=disnake.ButtonStyle.green,
                custom_id="start_game",
                disabled=dis,
                row=0,
            ),
        )

        for k, v in GenerateButtons.SETS_NAME.items():
            select.append(
                disnake.SelectOption(
                    label=v["label"],
                    description=v["descr"].format(__is_bool(config[k])),
                    value=k,
                    emoji=v["emoji"],
                )
            )

        components.append(
            disnake.ui.StringSelect(
                placeholder="Настроить игру",
                options=select,
                row=1,
                custom_id="sets",
                min_values=1,
                max_values=1,
            )
        )
        return components

    @staticmethod
    def generate_role_select(roles: int, msg_id: int):
        epl = EnabledPlayerRoles(roles)
        select = []
        plchldr = "Включить {0} в игру"
        for PLN in EnabledPlayerRoles.__members__:
            if EnabledPlayerRoles[PLN] in epl:
                default = True
            else:
                default = False
            select.append(
                disnake.SelectOption(
                    label=PlayerRoleName[PLN].value,
                    description=plchldr.format(
                        GenerateButtons.ROLES[PlayerRoleName[PLN]][0]
                    ),
                    value=PLN.lower(),
                    emoji=GenerateButtons.ROLES[PlayerRoleName[PLN]][1],
                    default=default,
                )
            )
        cmpnts = [
            disnake.ui.StringSelect(
                custom_id="change_allowed_roles__" + str(msg_id),
                placeholder="Выберите роли, доступные к отыгровке в этой игре",
                min_values=0,
                max_values=len(select),
                options=select,
            )
        ]
        return cmpnts

    @staticmethod
    async def generate_member_choice(
        inter: disnake.MessageInteraction, members: dict, choice_type: ChoiceType
    ):
        choices = []
        placeholder = ""
        choice_id = ""
        ex_roles = [PlayerRole.DEAD, PlayerRole.ARRESTED]
        match ChoiceType(choice_type.value):
            case ChoiceType.HARLOT_CHOSE:
                placeholder = "Путана выбирает участника, к которому пойдёт сейчас"
                choice_id = "harlot_choice"
                choices = await GenerateButtons.__generate_members(
                    inter, members, ex_roles
                )
            case ChoiceType.MAFIA_KILL:
                placeholder = "Мафия должна сделать свой выбор"
                choice_id = "mafia_choice"
                choices = await GenerateButtons.__generate_members(
                    inter,
                    members,
                    ex_roles
                    + [
                        PlayerRole.MAFIA,
                        PlayerRole.SENIOR,
                    ],
                )
            case ChoiceType.MANIAC_KILL:
                placeholder = "Маньяк делает свой выбор"
                choice_id = "maniac_choice"
                choices = await GenerateButtons.__generate_members(
                    inter, members, ex_roles
                )
            case ChoiceType.DETECTIVE_CHECK:
                choice_id = "detective_choice"
                placeholder = "Детектив проверяет игрока на причастность к мафии"
                choices = await GenerateButtons.__generate_members(
                    inter, members, ex_roles
                )
            case ChoiceType.MEDIC_CHOSE:
                choice_id = "medic_choice"
                placeholder = "Медик приходит на помощь к кому-то (или к себе)"
                choices = await GenerateButtons.__generate_members(
                    inter, members, ex_roles
                )
            case ChoiceType.SENIOR_CHECK:
                choice_id = "medic_choice"
                placeholder = "Медик приходит на помощь к кому-то (или к себе)"
                choices = await GenerateButtons.__generate_members(
                    inter,
                    members,
                    ex_roles
                    + [
                        PlayerRole.MAFIA,
                        PlayerRole.SENIOR,
                    ],
                )

        s = disnake.ui.StringSelect(
            placeholder=placeholder,
            custom_id=choice_id,
            options=choices,
            min_values=1,
            max_values=1,
        )
        return s

    @staticmethod
    async def __generate_members(
        inter: disnake.Interaction, member_list: dict, ex_player_roles: list
    ) -> list:
        choices = []
        for member in member_list:
            mflags = PlayerRole(member["flags"])
            if not all(pflag in mflags for pflag in ex_player_roles):
                choices.append(
                    disnake.SelectOption(
                        label=(
                            await inter.guild.get_or_fetch_member(int(member))
                        ).display_name
                    )
                )
        return choices
