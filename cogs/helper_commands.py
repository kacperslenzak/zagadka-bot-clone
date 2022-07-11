from discord.ext import commands


class HelperCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='echo')
    @commands.has_guild_permissions(administrator=True)
    async def echo(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

def setup(client):
    client.add_cog(HelperCommands(client))