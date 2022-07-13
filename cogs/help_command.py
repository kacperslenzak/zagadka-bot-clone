from discord.ext import commands
from zagadkabot.embed import HelpEmbed


class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        channel = self.get_destination()
        em = HelpEmbed(self.context)
        em.create()
        return await self.context.reply(embed=em)

    async def send_command_help(self, command):
        channel = self.get_destination()
        em = HelpEmbed(self.context)
        em.create()
        return await self.context.reply(embed=em)


class HelpCommandCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        help_command = CustomHelpCommand()
        help_command.cog = self
        client.help_command = help_command


def setup(client):
    client.add_cog(HelpCommandCog(client))