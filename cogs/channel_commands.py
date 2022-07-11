import discord
from discord.ext import commands
from zagadkabot.channel_control_command import channel_command
from typing import Optional


class ChannelCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['c'])
    async def connect(self, ctx, action, user: Optional[discord.Member]):
        return await channel_command(ctx, "connect", action, user)

    @commands.command(aliases=['v'])
    async def view(self, ctx, action, user: Optional[discord.Member]):
        return await channel_command(ctx, "view", action, user)

    @commands.command(aliases=['s'])
    async def speak(self, ctx, action, user: Optional[discord.Member]):
        return await channel_command(ctx, "speak", action, user)

    @commands.command(aliases=['l'])
    async def limit(self, ctx, limit: int):
        return await channel_command(ctx, "limit", limit)

    @commands.command(aliases=['r'])
    async def reset(self, ctx, user: Optional[discord.Member]):
        return await channel_command(ctx, "reset", user)

    @commands.command()
    async def vc(self, ctx):
        id = ctx.author.voice.channel.id
        if id:
            return await ctx.send(f"<#{id}>")


def setup(client):
    client.add_cog(ChannelCommands(client))