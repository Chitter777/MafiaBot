import redis.asyncio as redis
from disnake.ext import commands
from loguru import logger


class Client(commands.InteractionBot):
    def __init__(self, *args, **kwargs):
        self.redis: redis.Redis = redis.Redis(decode_responses=True)
        super().__init__(*args, **kwargs)
