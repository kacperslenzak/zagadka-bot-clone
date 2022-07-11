import discord
import asyncio
from discord.ext import commands


class SetupManager(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def create_roles(self, ctx):
        roles = ('♳', '♴', '♵', '♶', '♷', '♸', '♹', '⚀', '⚁', '⚂', '⚃', '🟡', '$1', '$2', '$4', '$8', '$16', '$32', '$64', '$128', '♽', '✉︎', '✤' '✆', '♼', '✪', '🔴', '🟢', '🔵', '☢︎', '⌀', '⚠︎')
        check_role = discord.utils.find(lambda r: r.name == roles[0], ctx.guild.roles)
        if check_role:
            return

        check_role_1 = discord.utils.find(lambda r: r.name == '1', ctx.guild.roles)
        check_role_128 = discord.utils.find(lambda r: r.name == '128', ctx.guild.roles)
        if check_role_1 and check_role_128:
            return

        for role in roles:
            await ctx.guild.create_role(name=role)

        for role in range(1, 128):
            await ctx.guild.create_role(name=str(role))

        return


def setup(client):
    client.add_cog(SetupManager(client))