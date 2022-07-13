from discord.ext import commands
from discord.utils import get
import discord


class HelperCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='echo')
    @commands.has_guild_permissions(administrator=True)
    async def echo(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name='mutelive')
    @commands.has_guild_permissions(administrator=True)
    async def mutelive(self, ctx, user: discord.Member = None):
        if not user:
            return
        mutelive_role = get(ctx.guild.roles, name='⚠︎')

        if mutelive_role in user.roles:
            return

        await user.add_roles(mutelive_role)

    @commands.command(name='unmutelive')
    @commands.has_guild_permissions(administrator=True)
    async def unmutelive(self, ctx, user: discord.Member = None):
        if not user:
            return
        mutelive_role = get(ctx.guild.roles, name='⚠︎')

        if mutelive_role not in user.roles:
            return

        await user.remove_roles(mutelive_role)


def setup(client):
    client.add_cog(HelperCommands(client))
