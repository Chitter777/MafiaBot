from disnake.ext import commands
from loguru import logger


class OnReady(commands.Cog, name="Готовность"):
    @commands.Cog.listener("on_ready")
    async def event_on_ready(self):
        logger.success("Бот готов к работе!")

    @commands.Cog.listener("on_connect")
    async def event_on_connect(self):
        logger.info("Успешное подключение к gateway!")


def setup(bot):
    bot.add_cog(OnReady())
