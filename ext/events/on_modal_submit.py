import json

import disnake
from core import Client, GenerateButtons
from disnake.ext import commands


class OnModalSubmit(commands.Cog):
    def __init__(self, bot):
        self.bot: Client = bot

    @commands.Cog.listener("on_modal_submit")
    async def on_modal(self, inter: disnake.ModalInteraction):
        match inter.custom_id:
            # case "max_mafia":
            #     d = int(inter.text_values["max_mafia"].replace(" ", ""))
            #     data = json.loads(await self.bot.redis.get(str(inter.message.id)))
            #     data["config"]["max_mafia"] = d
            #     await inter.message.edit(
            #         components=GenerateButtons.generate_lobby_buttons(
            #             data["players"], data["max_players"], data["config"]
            #         )
            #     )
            #     await inter.send(f"Успешно изменено значение на: `{d}`", ephemeral=True)
            #     return await self.bot.redis.set(str(inter.message.id), json.dumps(data))
            case "max_prevoting_time":
                d = int(inter.text_values["max_prevoting_time"].replace(" ", ""))
                data = json.loads(await self.bot.redis.get(str(inter.message.id)))
                data["config"]["max_prevoting_time"] = d
                await inter.message.edit(
                    components=GenerateButtons.generate_lobby_buttons(
                        data["players"], data["max_players"], data["config"]
                    )
                )
                await inter.send(f"Успешно изменено значение на: `{d}`", ephemeral=True)
                return await self.bot.redis.set(str(inter.message.id), json.dumps(data))
            case "max_voting_time":
                d = int(inter.text_values["max_voting_time"].replace(" ", ""))
                data = json.loads(await self.bot.redis.get(str(inter.message.id)))
                data["config"]["max_voting_time"] = d
                await inter.message.edit(
                    components=GenerateButtons.generate_lobby_buttons(
                        data["players"], data["max_players"], data["config"]
                    )
                )
                await inter.send(f"Успешно изменено значение на: `{d}`", ephemeral=True)
                return await self.bot.redis.set(str(inter.message.id), json.dumps(data))


def setup(bot):
    bot.add_cog(OnModalSubmit(bot))
