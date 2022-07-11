import discord
import os
import logging
from settings import TOKEN, MONGODB_CONNECTION_URI, authorized_guild_id
from discord.ext import commands
from discord.ext.commands import when_mentioned_or
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)


class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=when_mentioned_or('?'),
            intents=discord.Intents.all()
        )
        self.db_client = None
        self.db = None
        self.guild_id = authorized_guild_id

    async def on_ready(self):
        self.db_client = AsyncIOMotorClient(MONGODB_CONNECTION_URI)
        self.db = self.db_client.zagadka

        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                self.load_extension(f'cogs.{filename[:-3]}')


if __name__ == '__main__':
    client = DiscordBot()
    client.run(TOKEN)
